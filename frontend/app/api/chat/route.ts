import { NextRequest, NextResponse } from "next/server";

// Edge Runtime: true streaming support, no buffering, no 10s function timeout
export const runtime = "edge";

const BACKEND_URL = process.env.BACKEND_URL || "https://ai-persona-cr8c.onrender.com";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();

    const backendResponse = await fetch(`${BACKEND_URL}/rag-query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...body, stream: true }),
    });

    if (!backendResponse.ok) {
      return NextResponse.json(
        { error: "Backend error", status: backendResponse.status },
        { status: backendResponse.status }
      );
    }

    // Pass through the streaming response — Edge Runtime streams this properly
    return new NextResponse(backendResponse.body, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
      },
    });
  } catch (error) {
    console.error("Chat API error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}

export async function OPTIONS() {
  return new NextResponse(null, {
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    },
  });
}
