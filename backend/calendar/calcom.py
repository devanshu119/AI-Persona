"""
Cal.com API wrapper for availability checking and meeting booking.
"""
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import httpx

CALCOM_BASE_URL = "https://api.cal.com/v1"


def _get_headers() -> dict:
    api_key = os.environ["CALCOM_API_KEY"]
    return {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}


async def get_availability(
    days_ahead: int = 7,
    timezone_str: str = "Asia/Kolkata",
) -> dict:
    """
    Fetch available time slots from Cal.com for the next N days.
    Returns a structured dict with available slots.
    """
    event_type_id = os.environ.get("CALCOM_EVENT_TYPE_ID", "")
    username = os.environ.get("CALCOM_USERNAME", "devanshu")

    now = datetime.now(timezone.utc)
    date_from = now.strftime("%Y-%m-%d")
    date_to = (now + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

    url = f"{CALCOM_BASE_URL}/slots"
    params = {
        "eventTypeId": event_type_id,
        "startTime": f"{date_from}T00:00:00.000Z",
        "endTime": f"{date_to}T23:59:59.000Z",
        "timeZone": timezone_str,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url, headers=_get_headers(), params=params)

    if resp.status_code != 200:
        # Fallback: return generic availability message
        return {
            "available": False,
            "message": "Could not fetch real-time availability. Please visit https://cal.com/devanshu to book directly.",
            "slots": [],
            "booking_url": f"https://cal.com/{username}",
        }

    data = resp.json()
    slots_raw = data.get("slots", {})

    # Format slots for easy reading
    formatted_slots = []
    for date_str, slot_list in slots_raw.items():
        for slot in slot_list[:3]:  # Max 3 per day
            slot_time = datetime.fromisoformat(slot["time"].replace("Z", "+00:00"))
            formatted_slots.append(
                {
                    "date": date_str,
                    "time_utc": slot["time"],
                    "time_readable": slot_time.strftime("%A, %B %d at %I:%M %p UTC"),
                }
            )
        if len(formatted_slots) >= 6:
            break

    return {
        "available": len(formatted_slots) > 0,
        "slots": formatted_slots[:6],
        "booking_url": f"https://cal.com/{username}",
        "message": (
            f"Found {len(formatted_slots)} available slots in the next {days_ahead} days."
            if formatted_slots
            else "No available slots found. Please check back later or visit the booking link."
        ),
    }


async def create_booking(
    name: str,
    email: str,
    start_time: str,
    timezone_str: str = "Asia/Kolkata",
    notes: Optional[str] = None,
) -> dict:
    """
    Create a booking on Cal.com.
    start_time should be ISO 8601 format (e.g., "2025-06-15T14:00:00.000Z")
    """
    event_type_id = os.environ.get("CALCOM_EVENT_TYPE_ID", "")
    username = os.environ.get("CALCOM_USERNAME", "devanshu")

    # Parse and compute end time (assume 30-min meetings)
    try:
        start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        end_dt = start_dt + timedelta(minutes=30)
        end_time = end_dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    except ValueError:
        return {
            "success": False,
            "message": "Invalid start time format. Please provide ISO 8601 format.",
        }

    url = f"{CALCOM_BASE_URL}/bookings"
    payload = {
        "eventTypeId": int(event_type_id) if event_type_id else 0,
        "start": start_time,
        "end": end_time,
        "timeZone": timezone_str,
        "responses": {
            "name": name,
            "email": email,
            "notes": notes or f"Booked via AI persona — interview scheduling for Scaler AI Engineer role",
        },
        "metadata": {"source": "ai-persona"},
        "language": "en",
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(url, headers=_get_headers(), json=payload)

    if resp.status_code in (200, 201):
        booking_data = resp.json()
        return {
            "success": True,
            "booking_id": booking_data.get("uid", ""),
            "meeting_url": booking_data.get("videoCallData", {}).get("url", ""),
            "start_time": start_time,
            "name": name,
            "email": email,
            "message": (
                f"Meeting confirmed! A confirmation email will be sent to {email}. "
                f"Meeting scheduled for {start_dt.strftime('%A, %B %d at %I:%M %p UTC')}."
            ),
            "booking_url": f"https://cal.com/{username}",
        }
    else:
        return {
            "success": False,
            "message": (
                f"Booking failed (status {resp.status_code}). "
                f"Please book directly at https://cal.com/{username}"
            ),
            "raw_error": resp.text[:200],
        }
