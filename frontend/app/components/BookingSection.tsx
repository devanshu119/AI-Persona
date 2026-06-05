"use client";

interface BookingSectionProps {
  calcomUsername?: string;
}

export default function BookingSection({
  calcomUsername = "devanshu",
}: BookingSectionProps) {
  return (
    <div className="booking-card">
      <div style={{ padding: "28px 28px 0" }}>
        <div className="section-label">📅 Schedule a Meeting</div>
        <p style={{ color: "var(--text-secondary)", fontSize: "14px", marginTop: "8px" }}>
          Book a 30-minute call directly on Devanshu&apos;s calendar. Real availability, instant confirmation.
        </p>
      </div>
      <iframe
        src={`https://cal.com/${calcomUsername}?embed=true&theme=dark`}
        className="booking-embed"
        title="Book a meeting with Devanshu"
        id="calcom-booking-embed"
        loading="lazy"
        style={{ minHeight: "650px" }}
      />
    </div>
  );
}
