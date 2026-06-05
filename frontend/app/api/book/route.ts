import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || "https://ai-persona-cr8c.onrender.com";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { name, email, start_time, timezone, notes } = body;

    if (!name || !email || !start_time) {
      return NextResponse.json(
        { error: "name, email, and start_time are required" },
        { status: 400 }
      );
    }

    const backendResponse = await fetch(`${BACKEND_URL}/book`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, start_time, timezone, notes }),
    });

    const data = await backendResponse.json();

    if (!backendResponse.ok) {
      return NextResponse.json({ error: data.detail || "Booking failed" }, { status: 422 });
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error("Booking API error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
