"""
FastAPI backend for Devanshu's AI Persona system.
Serves both the chat interface (Part B) and Vapi voice agent tool calls (Part A).

Endpoints:
  POST /rag-query       — Chat RAG query with streaming
  POST /vapi-rag        — Vapi tool-call webhook (returns JSON for voice agent)
  GET  /availability    — Check Cal.com calendar availability
  POST /book            — Create a Cal.com booking
  GET  /health          — Health check
"""
import os
import json
import asyncio
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv

load_dotenv()

# Validate required env vars at startup
_REQUIRED_ENV = ["GROQ_API_KEY", "COHERE_API_KEY", "PINECONE_API_KEY", "PINECONE_INDEX_NAME"]
_missing = [k for k in _REQUIRED_ENV if not os.environ.get(k)]
if _missing:
    raise RuntimeError(f"Missing required environment variables: {_missing}")

from rag.chain import get_rag_context_for_vapi, stream_rag_response
from calcom.calcom import get_availability, create_booking

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Devanshu AI Persona API",
    description="RAG-grounded AI persona backend for voice and chat interfaces",
    version="1.0.0",
)

FRONTEND_URL = os.environ.get("FRONTEND_URL", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------
class ChatRequest(BaseModel):
    query: str
    stream: bool = True


class BookingRequest(BaseModel):
    name: str
    email: str
    start_time: str  # ISO 8601
    timezone: str = "Asia/Kolkata"
    notes: Optional[str] = None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "devanshu-ai-persona",
        "version": "1.0.0",
    }


@app.post("/rag-query")
async def rag_query(req: ChatRequest):
    """
    Main RAG endpoint for the chat interface.
    Supports streaming (SSE) and non-streaming responses.
    """
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    if req.stream:
        async def event_generator():
            try:
                async for token in stream_rag_response(req.query):
                    yield f"data: {json.dumps({'token': token})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )
    else:
        # Non-streaming fallback
        try:
            result = get_rag_context_for_vapi(req.query)
            return {"answer": result["answer"], "sources": result["sources"]}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@app.post("/vapi-rag")
async def vapi_rag_tool(request: Request):
    """
    Vapi tool-call webhook endpoint.
    Called by Vapi when the voice agent invokes the 'get_persona_context' tool.
    
    Vapi sends:
    {
      "message": {
        "type": "tool-calls",
        "toolCalls": [{"function": {"name": "get_persona_context", "arguments": {"query": "..."}}}]
      }
    }
    
    Must return:
    {
      "results": [{"toolCallId": "...", "result": "answer text"}]
    }
    """
    try:
        body = await request.json()
        message = body.get("message", {})
        tool_calls = message.get("toolCalls", [])

        results = []
        for call in tool_calls:
            call_id = call.get("id", "")
            func = call.get("function", {})
            func_name = func.get("name", "")
            arguments = func.get("arguments", {})

            if func_name == "get_persona_context":
                query = arguments.get("query", "")
                rag_result = get_rag_context_for_vapi(query)
                result_text = rag_result["answer"]

            elif func_name == "check_availability":
                days = int(arguments.get("days_ahead", 7))
                avail = await get_availability(days_ahead=days)
                if avail["slots"]:
                    slot_list = "\n".join(
                        f"- {s['time_readable']}" for s in avail["slots"][:4]
                    )
                    result_text = f"Available slots:\n{slot_list}\n\nBook at: {avail['booking_url']}"
                else:
                    result_text = avail["message"]

            elif func_name == "book_meeting":
                name = arguments.get("name", "")
                email = arguments.get("email", "")
                start_time = arguments.get("start_time", "")
                booking = await create_booking(name=name, email=email, start_time=start_time)
                result_text = booking["message"]

            else:
                result_text = f"Unknown function: {func_name}"

            results.append({"toolCallId": call_id, "result": result_text})

        return {"results": results}

    except Exception as e:
        return JSONResponse(
            status_code=200,  # Vapi expects 200 even on errors
            content={"results": [{"toolCallId": "", "result": f"Error: {str(e)}"}]},
        )


@app.get("/availability")
async def check_availability(days_ahead: int = 7, timezone: str = "Asia/Kolkata"):
    """Check Cal.com calendar availability."""
    result = await get_availability(days_ahead=days_ahead, timezone_str=timezone)
    return result


@app.post("/book")
async def book_meeting(req: BookingRequest):
    """Create a Cal.com booking."""
    if not all([req.name, req.email, req.start_time]):
        raise HTTPException(
            status_code=400, detail="name, email, and start_time are required"
        )
    result = await create_booking(
        name=req.name,
        email=req.email,
        start_time=req.start_time,
        timezone_str=req.timezone,
        notes=req.notes,
    )
    if not result["success"]:
        raise HTTPException(status_code=422, detail=result["message"])
    return result


# ---------------------------------------------------------------------------
# Init (called once on startup in production)
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def startup_event():
    """Warm up the RAG chain on startup to reduce cold-start latency."""
    print("Warming up RAG chain...")
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: get_rag_context_for_vapi("Who is Devanshu?")
        )
        print("RAG chain warmed up successfully")
    except Exception as e:
        print(f"Warmup failed (non-fatal): {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
