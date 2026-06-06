import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || "https://ai-persona-cr8c.onrender.com";

// Extend Vercel function timeout to 60s to handle Render cold-start (~30-50s)
export const maxDuration = 60;

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();

    // 55s timeout — gives Render time to cold-start before Vercel cuts the function
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 55_000);

    let backendResponse: Response;
    try {
      backendResponse = await fetch(`${BACKEND_URL}/rag-query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...body, stream: true }),
        signal: controller.signal,
      });
    } finally {
      clearTimeout(timeoutId);
    }

    if (!backendResponse.ok) {
      return NextResponse.json(
        { error: "Backend error", status: backendResponse.status },
        { status: backendResponse.status }
      );
    }

    // Pass through the streaming response
    return new NextResponse(backendResponse.body, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
        "Access-Control-Allow-Origin": "*",
      },
    });
  } catch (error) {
    console.error("Chat API error:", error);
    const isTimeout = error instanceof Error && error.name === "AbortError";
    return NextResponse.json(
      { error: isTimeout ? "Backend is waking up, please try again in a moment" : "Internal server error" },
      { status: 503 }
    );
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
