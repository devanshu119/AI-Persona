"""
Cal.com API wrapper for availability checking and meeting booking.
Uses Cal.com API v2 (v1 was decommissioned).
"""
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import httpx

CALCOM_BASE_URL = "https://api.cal.com/v2"


def _get_headers() -> dict:
    api_key = os.environ["CALCOM_API_KEY"]
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "cal-api-version": "2024-09-04",
    }


async def get_availability(
    days_ahead: int = 7,
    timezone_str: str = "Asia/Kolkata",
) -> dict:
    """
    Fetch available time slots from Cal.com for the next N days.
    Uses Cal.com v2 public /slots/available endpoint (no auth needed).
    """
    event_type_id = os.environ.get("CALCOM_EVENT_TYPE_ID", "5912502")
    username = os.environ.get("CALCOM_USERNAME", "devanshu09")
    event_slug = os.environ.get("CALCOM_EVENT_SLUG", "30min")
    booking_url = f"https://cal.com/{username}/{event_slug}"

    now = datetime.now(timezone.utc)
    start_time = now.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    end_time = (now + timedelta(days=days_ahead)).strftime("%Y-%m-%dT%H:%M:%S.000Z")

    url = f"{CALCOM_BASE_URL}/slots/available"
    params = {
        "eventTypeId": event_type_id,
        "startTime": start_time,
        "endTime": end_time,
        "timeZone": timezone_str,
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Public endpoint — no auth header required
            resp = await client.get(url, params=params)

        if resp.status_code != 200:
            return {
                "available": True,
                "message": f"Calendar available Mon–Fri 9am–5pm IST. Book at {booking_url}",
                "slots": [],
                "booking_url": booking_url,
            }

        data = resp.json()
        slots_raw = data.get("data", {}).get("slots", {})

        formatted_slots = []
        for date_str, slot_list in slots_raw.items():
            for slot in slot_list[:3]:  # Max 3 per day
                slot_time_str = slot.get("time", "") if isinstance(slot, dict) else slot
                try:
                    slot_time = datetime.fromisoformat(slot_time_str)
                    formatted_slots.append({
                        "date": date_str,
                        "time_utc": slot_time_str,
                        "time_readable": slot_time.strftime("%A, %B %d at %I:%M %p IST"),
                    })
                except Exception:
                    pass
            if len(formatted_slots) >= 6:
                break

        return {
            "available": len(formatted_slots) > 0,
            "slots": formatted_slots[:6],
            "booking_url": booking_url,
            "message": (
                f"Found {len(formatted_slots)} available slots in the next {days_ahead} days."
                if formatted_slots
                else f"No open slots this week. Book at {booking_url}"
            ),
        }

    except Exception as e:
        return {
            "available": True,
            "message": f"Calendar available Mon–Fri 9am–5pm IST. Book at {booking_url}",
            "slots": [],
            "booking_url": booking_url,
        }


async def create_booking(
    name: str,
    email: str,
    start_time: str,
    timezone_str: str = "Asia/Kolkata",
    notes: Optional[str] = None,
) -> dict:
    """
    Create a booking on Cal.com using v2 API.
    start_time should be ISO 8601 format (e.g., "2025-06-15T14:00:00.000Z")
    """
    event_type_id = os.environ.get("CALCOM_EVENT_TYPE_ID", "")
    username = os.environ.get("CALCOM_USERNAME", "devanshu09")

    try:
        start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
    except ValueError:
        return {
            "success": False,
            "message": "Invalid start time format. Please provide ISO 8601 format.",
        }

    url = f"{CALCOM_BASE_URL}/bookings"
    payload = {
        "eventTypeId": int(event_type_id) if event_type_id else 0,
        "start": start_time,
        "timeZone": timezone_str,
        "attendee": {
            "name": name,
            "email": email,
            "timeZone": timezone_str,
        },
        "metadata": {"source": "ai-persona"},
    }

    if notes:
        payload["bookingFieldsResponses"] = {"notes": notes}

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, headers=_get_headers(), json=payload)

        if resp.status_code in (200, 201):
            booking_data = resp.json().get("data", resp.json())
            return {
                "success": True,
                "booking_id": booking_data.get("uid", ""),
                "meeting_url": booking_data.get("videoCallData", {}).get("url", ""),
                "start_time": start_time,
                "name": name,
                "email": email,
                "message": (
                    f"Meeting confirmed! A confirmation email will be sent to {email}. "
                    f"Scheduled for {start_dt.strftime('%A, %B %d at %I:%M %p UTC')}."
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
                "raw_error": resp.text[:300],
            }

    except Exception as e:
        return {
            "success": False,
            "message": f"Booking error: {str(e)}. Please book at https://cal.com/{username}",
        }
