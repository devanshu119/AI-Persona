# AI Persona

> **Live System**: Voice Agent + RAG Chat Interface + Real Calendar Booking  


---

## 🔗 Live Links

| Component | Link |
|-----------|------|
| 📞 Voice Agent (Phone) | **+1 (540) 893-1058** |
| 💬 Chat Interface | [ai-persona-ebon.vercel.app](https://ai-persona-ebon.vercel.app) |
| 📅 Direct Booking | [cal.com/devanshu09/30min](https://cal.com/devanshu09/30min) |
| 🐙 GitHub | [github.com/devanshu119/AI-Persona](https://github.com/devanshu119/AI-Persona) |

---

## Architecture

```
                         ┌──────────────────────────────────────┐
                         │         SHARED RAG LAYER             │
                         │   Resume PDF + GitHub Repos          │
                         │   → Cohere embed-english-v3.0        │
                         │   → Pinecone (namespace: resume/     │
                         │               github)                │
                         └──────────┬───────────────┬──────────┘
                                    │               │
          ┌─────────────────────────▼──┐   ┌────────▼──────────────────┐
          │    PART A: VOICE AGENT     │   │  PART B: CHAT INTERFACE   │
          │    Vapi.ai Platform        │   │  Next.js 15 (Vercel)      │
          │                           │   │  + FastAPI (Render)        │
          │  📞 +1 (540) 893-1058     │   │  💬 ai-persona-ebon.vercel │
          │  LLM: Groq llama-3.1-8b   │   │                           │
          │  Voice: ElevenLabs        │   │  Streaming SSE responses  │
          │  STT: Deepgram Nova-2     │   │  Markdown rendering       │
          │                           │   │  Cal.com embed            │
          │  Tools (function calls):  │   │                           │
          │  ├─ get_persona_context() │   │  Direct Render API calls: │
          │  ├─ check_availability()  │   │  ├─ POST /rag-query       │
          │  └─ book_meeting()        │   │  └─ GET  /availability    │
          └────────────┬──────────────┘   └──────────┬──────────────┘
                       │                             │
                       └──────────────┬──────────────┘
                                      │
                      ┌───────────────▼───────────────┐
                      │    FastAPI Backend (Render)    │
                      │    ai-persona-cr8c.onrender.com│
                      │                               │
                      │  POST /rag-query (streaming)  │
                      │  POST /vapi-rag (tool webhook)│
                      │  GET  /availability           │
                      │  POST /book                   │
                      │  GET  /health                 │
                      │                               │
                      │  LangChain RetrievalQA Chain  │
                      │  Groq llama-3.1-8b-instant    │
                      │  Cal.com API v2               │
                      └───────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------| 
| Voice Platform | **Vapi.ai** | Phone number, STT, TTS, tool calling, barge-in |
| Voice LLM | **Groq llama-3.1-8b-instant** | Ultra-low latency (<1.8s first response) |
| Chat LLM | **Groq llama-3.1-8b-instant** | RAG-grounded chat responses |
| Embeddings | **Cohere embed-english-v3.0** | 1024-dim, high-quality retrieval |
| Vector DB | **Pinecone** (free serverless) | Multi-namespace semantic search |
| RAG Framework | **LangChain** | Document loaders, retrieval chain |
| Voice TTS | **ElevenLabs** (via Vapi) | Natural, low-latency voice |
| Voice STT | **Deepgram Nova-2** (via Vapi) | ~4% WER, fast transcription |
| Chat Frontend | **Next.js 15** | App Router, streaming, Vercel deploy |
| Backend | **FastAPI** (Python 3.11) | Async API, SSE streaming |
| Calendar | **Cal.com** (v2 API) | Open-source, API-first booking |
| Backend Host | **Render.com** (free) | Persistent Python container |
| Frontend Host | **Vercel** (free) | Edge CDN, instant deploy |

---

## Setup Instructions

### Prerequisites

You need accounts on:
- [Groq](https://console.groq.com) — for llama-3.1-8b-instant LLM
- [Cohere](https://dashboard.cohere.com) — for embeddings
- [Pinecone](https://app.pinecone.io) — for vector storage (free tier)
- [Vapi.ai](https://dashboard.vapi.ai) — for voice agent (free trial)
- [Cal.com](https://cal.com) — for calendar booking (free)
- [Render.com](https://render.com) — for backend hosting (free)
- [Vercel](https://vercel.com) — for frontend hosting (free)

---

### Step 1: Clone and Configure Backend

```bash
git clone https://github.com/devanshu119/AI-Persona.git
cd AI-Persona/backend
cp .env.example .env
```

Edit `.env` with your API keys:
```env
GROQ_API_KEY=gsk_...
COHERE_API_KEY=...
PINECONE_API_KEY=...
PINECONE_INDEX_NAME=devanshu-persona
CALCOM_API_KEY=cal_live_...
CALCOM_EVENT_TYPE_ID=5912502
CALCOM_EVENT_SLUG=30min
CALCOM_USERNAME=devanshu09
GITHUB_TOKEN=ghp_...
GITHUB_USERNAME=devanshu119
FRONTEND_URL=https://your-app.vercel.app
```

**Getting Cal.com credentials:**
1. Sign up at cal.com, create a free event type ("30-min meeting")
2. Go to Settings → API Keys → Generate key
3. Find your Event Type ID from the URL: `cal.com/event-types/**12345**`

---

### Step 2: Ingest Data into Pinecone

```bash
cd backend
pip install -r requirements.txt

# Run the one-time ingestion (fetches resume + GitHub repos)
python ingest/run_ingestion.py

# Optional: pass your resume PDF
python ingest/run_ingestion.py --resume path/to/resume.pdf
```

Expected output:
```
✓ Resume: 18 chunks ingested
✓ GitHub: 64 chunks ingested
Total: 82 chunks in Pinecone
```

---

### Step 3: Deploy Backend to Render

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo, point to `backend/` directory
4. Render detects `Dockerfile` automatically
5. Add environment variables from `.env` in Render dashboard
6. Deploy → Copy your Render URL (e.g., `https://ai-persona-cr8c.onrender.com`)

Test the deployment:
```bash
curl https://your-backend.onrender.com/health
# → {"status":"ok","service":"devanshu-ai-persona","version":"1.0.0"}
```

---

### Step 4: Deploy Frontend to Vercel

```bash
cd frontend
cp .env.example .env.local
# Edit .env.local with your Render backend URL
```

```env
BACKEND_URL=https://your-backend.onrender.com
NEXT_PUBLIC_BACKEND_URL=https://your-backend.onrender.com
NEXT_PUBLIC_CALCOM_USERNAME=devanshu09
```

```bash
npx vercel --prod
```

Or connect via Vercel dashboard → Import from GitHub → set env vars.

---

### Step 5: Set Up Vapi Voice Agent

```bash
cd vapi
cp .env.example .env
# Add VAPI_API_KEY and BACKEND_URL (Render URL)

pip install httpx python-dotenv
python setup_assistant.py
```

This will:
1. Create the assistant with all 3 tools configured
2. Auto-assign to your first phone number (if available)
3. Save the assistant ID to `vapi/vapi_config.json`

**Get a phone number:**
1. Go to [dashboard.vapi.ai/phone-numbers](https://dashboard.vapi.ai/phone-numbers)
2. Create a free US number
3. Assign the assistant (from `vapi_config.json` ID)

---

### Step 6: Run Evaluations

```bash
cd evals
pip install -r requirements.txt

# Run RAGAS chat evaluation against live backend
python chat_evals.py --backend https://your-backend.onrender.com --output results.json

# Generate the 1-page PDF report
python report_generator.py --results results.json --output report.pdf
```

---

## Cost Breakdown

| Resource | Tier | Cost |
|----------|------|------|
| Render.com backend | Free | $0/month |
| Vercel frontend | Free | $0/month |
| Pinecone vector DB | Free (100K vectors) | $0/month |
| Cal.com | Free | $0/month |
| Vapi.ai | Pay-per-use | ~$0.05–0.15/min |
| Groq (llama-3.1-8b) | Free tier | $0 (rate-limited) |
| Cohere (embeddings) | Free trial | $0 |

**Per call estimate**: ~$0.08 (5-min call × Vapi per-minute rate)  
**Per chat session estimate**: ~$0.001 (3 queries × Groq free tier)  
**One-time ingestion cost**: ~$0.002 (Cohere embedding calls)  

---

## Project Structure

```
AI-Persona/
├── backend/
│   ├── main.py                  # FastAPI app (all endpoints)
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── render.yaml
│   ├── .env.example
│   ├── rag/
│   │   ├── chain.py             # LangChain RAG chain (Groq + Cohere)
│   │   ├── persona_prompt.py    # System prompts
│   │   └── pinecone_client.py   # Vector store client
│   ├── calcom/
│   │   └── calcom.py            # Cal.com API v2 wrapper
│   └── ingest/
│       ├── resume_loader.py     # Resume PDF → Pinecone
│       ├── github_loader.py     # GitHub repos → Pinecone
│       └── run_ingestion.py     # Orchestration script
├── frontend/
│   ├── app/
│   │   ├── page.tsx             # Landing page
│   │   ├── layout.tsx           # Root layout
│   │   ├── globals.css          # Design system
│   │   └── components/
│   │       ├── ChatWidget.tsx   # Streaming SSE chat UI
│   │       └── BookingSection.tsx
│   ├── package.json
│   ├── next.config.mjs
│   └── .env.example
├── vapi/
│   ├── setup_assistant.py       # Creates Vapi assistant via API
│   ├── vapi_config.json         # Assistant ID + backend URL
│   └── .env.example
├── evals/
│   ├── golden_qa.json           # 20 ground-truth Q&A pairs
│   ├── chat_evals.py            # Evaluation runner
│   ├── report_generator.py      # PDF report generation
│   ├── results.json             # (generated after eval run)
│   └── report.html              # (generated eval report)
└── README.md
```

---

## Hard Requirements Checklist

- [x] **Voice < 2s first response** — Vapi + Deepgram Nova-2 + Groq llama-3.1-8b ≈ 1.8s p50
- [x] **Real calendar booking** — Cal.com API v2, real availability check, confirmed bookings
- [x] **RAG grounded** — No hardcoded answers; all responses from Pinecone retrieval (resume + GitHub)
- [x] **Barge-in handling** — Vapi built-in interruption support
- [x] **Public GitHub repo** — This repo, with README + architecture + cost breakdown
- [x] **Eval report** — `evals/report.html` with all required metrics
- [x] **Live at submission** — Voice (`+1 540-893-1058`) + chat (Vercel URL) both live

---

