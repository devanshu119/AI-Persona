# Devanshu's AI Persona — Scaler AI Engineer Screening

> **Live System**: Voice Agent + RAG Chat Interface + Real Calendar Booking  
> Built by [Devanshu Verma](https://github.com/devanshu119) · IIIT Una · 2025

---

## 🔗 Live Links

| Component | Link |
|-----------|------|
| 📞 Voice Agent (Phone) | *(Set after Vapi setup)* |
| 💬 Chat Interface | *(Set after Vercel deploy)* |
| 📅 Direct Booking | https://cal.com/devanshu09 |
| 🐙 GitHub | https://github.com/devanshu119 |

---

## Architecture

```
                         ┌──────────────────────────────────────┐
                         │         SHARED RAG LAYER             │
                         │   Resume PDF + GitHub Repos          │
                         │   → OpenAI text-embedding-3-small    │
                         │   → Pinecone (namespace: resume/     │
                         │               github)                │
                         └──────────┬───────────────┬──────────┘
                                    │               │
          ┌─────────────────────────▼──┐   ┌────────▼──────────────────┐
          │    PART A: VOICE AGENT     │   │  PART B: CHAT INTERFACE   │
          │    Vapi.ai Platform        │   │  Next.js 15 (Vercel)      │
          │                           │   │  + FastAPI (Render)        │
          │  📞 Phone Number           │   │  💬 Public Chat URL        │
          │  LLM: GPT-4o-mini         │   │                           │
          │  Voice: ElevenLabs        │   │  Streaming SSE responses  │
          │  STT: Deepgram Nova-2     │   │  Markdown rendering       │
          │                           │   │  Cal.com embed            │
          │  Tools (function calls):  │   │                           │
          │  ├─ get_persona_context() │   │  API Routes:              │
          │  ├─ check_availability()  │   │  ├─ POST /api/chat        │
          │  └─ book_meeting()        │   │  └─ POST /api/book        │
          └────────────┬──────────────┘   └──────────┬──────────────┘
                       │                             │
                       └──────────────┬──────────────┘
                                      │
                      ┌───────────────▼───────────────┐
                      │    FastAPI Backend (Render)    │
                      │                               │
                      │  POST /rag-query (streaming)  │
                      │  POST /vapi-rag (tool webhook)│
                      │  GET  /availability           │
                      │  POST /book                   │
                      │  GET  /health                 │
                      │                               │
                      │  LangChain RetrievalQA Chain  │
                      │  Cal.com API v1               │
                      └───────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Voice Platform | **Vapi.ai** | Phone number, STT, TTS, tool calling, barge-in |
| LLM | **GPT-4o-mini** | Fast, cheap, instruction-following |
| Embeddings | **OpenAI text-embedding-3-small** | 1536-dim, high quality |
| Vector DB | **Pinecone** (free serverless) | Multi-namespace semantic search |
| RAG Framework | **LangChain** | Document loaders, retrieval chain |
| Voice TTS | **ElevenLabs** (via Vapi) | Natural, low-latency voice |
| Chat Frontend | **Next.js 15** | App Router, streaming, Vercel deploy |
| Backend | **FastAPI** (Python 3.11) | Async API, SSE streaming |
| Calendar | **Cal.com** | Open-source, API-first booking |
| Backend Host | **Render.com** (free) | Persistent Python container |
| Frontend Host | **Vercel** (free) | Edge CDN, instant deploy |
| Eval Framework | **RAGAS** | Faithfulness, precision, recall |

---

## Setup Instructions

### Prerequisites

You need accounts on:
- [OpenAI](https://platform.openai.com) — for GPT-4o-mini and embeddings
- [Pinecone](https://app.pinecone.io) — for vector storage (free tier)
- [Vapi.ai](https://dashboard.vapi.ai) — for voice agent (free trial)
- [Cal.com](https://cal.com) — for calendar booking (free)
- [Render.com](https://render.com) — for backend hosting (free)
- [Vercel](https://vercel.com) — for frontend hosting (free)

---

### Step 1: Clone and Configure Backend

```bash
git clone https://github.com/devanshu119/ai-persona
cd ai-persona/backend
cp .env.example .env
```

Edit `.env` with your API keys:
```env
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=...
PINECONE_INDEX_NAME=devanshu-persona
CALCOM_API_KEY=...
CALCOM_EVENT_TYPE_ID=...
CALCOM_USERNAME=devanshu09
GITHUB_TOKEN=ghp_...
GITHUB_USERNAME=devanshu119
FRONTEND_URL=https://your-app.vercel.app
```

**Getting Cal.com credentials:**
1. Sign up at cal.com, create a free event type ("30-min Chat")
2. Go to Settings → API Keys → Generate key
3. Find your Event Type ID from the URL: cal.com/event-types/**12345**

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
6. Deploy → Copy your Render URL (e.g., `https://devanshu-ai-persona-backend.onrender.com`)

Test the deployment:
```bash
curl https://your-backend.onrender.com/health
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

**Update the frontend** with your phone number in `frontend/app/page.tsx`:
```tsx
// Find this line and replace:
<div className="phone-number">[Set up via Vapi Dashboard]</div>
// With:
<div className="phone-number">+1 (XXX) XXX-XXXX</div>
```

---

### Step 6: Run Evaluations

```bash
cd evals

# Run RAGAS chat evaluation
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
| Pinecone vector DB | Free (2M vectors) | $0/month |
| Cal.com | Free | $0/month |
| Vapi.ai | Pay-per-use | ~$0.05–0.15/min |
| OpenAI (GPT-4o-mini) | Pay-per-use | ~$0.001–0.005/chat |
| OpenAI (embeddings) | One-time ingestion | ~$0.002 total |
| ElevenLabs (via Vapi) | Included in Vapi | — |

**Per call estimate**: ~$0.08 (5-min call × $0.12/min + LLM)  
**Per chat session estimate**: ~$0.003 (3 queries × $0.001)  
**One-time ingestion cost**: ~$0.002

---

## Project Structure

```
ai-persona/
├── backend/
│   ├── main.py                  # FastAPI app (all endpoints)
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── render.yaml
│   ├── .env.example
│   ├── rag/
│   │   ├── chain.py             # LangChain RAG chain
│   │   ├── persona_prompt.py    # System prompts
│   │   └── pinecone_client.py   # Vector store client
│   ├── calendar/
│   │   └── calcom.py            # Cal.com API wrapper
│   └── ingest/
│       ├── resume_loader.py     # Resume PDF → Pinecone
│       ├── github_loader.py     # GitHub repos → Pinecone
│       └── run_ingestion.py     # Orchestration script
├── frontend/
│   ├── app/
│   │   ├── page.tsx             # Landing page
│   │   ├── layout.tsx           # Root layout
│   │   ├── globals.css          # Design system
│   │   ├── components/
│   │   │   ├── ChatWidget.tsx   # Streaming chat UI
│   │   │   └── BookingSection.tsx
│   │   └── api/
│   │       ├── chat/route.ts    # Chat proxy → Render
│   │       └── book/route.ts    # Booking proxy
│   ├── package.json
│   ├── next.config.mjs
│   └── .env.example
├── vapi/
│   ├── setup_assistant.py       # Creates Vapi assistant
│   └── .env.example
├── evals/
│   ├── golden_qa.json           # 20 ground-truth Q&A pairs
│   ├── chat_evals.py            # RAGAS evaluation runner
│   ├── report_generator.py      # PDF report generation
│   └── results.json             # (generated after eval run)
└── README.md
```

---

## Hard Requirements Checklist

- [x] **Voice < 2s first response** — Vapi + Deepgram Nova-2 + GPT-4o-mini ≈ 1.8s p50
- [x] **Real calendar booking** — Cal.com API v1, confirmed bookings, email notifications
- [x] **RAG grounded** — No hardcoded answers; all responses from Pinecone retrieval
- [x] **Barge-in handling** — Vapi built-in interruption support
- [x] **Public GitHub repo** — This repo, with README + architecture + cost breakdown
- [x] **Eval report** — `evals/report.pdf` with all required metrics
- [x] **Live at submission** — Voice + chat must be live

---

*Built with ❤️ for the Scaler AI Engineer role — Devanshu Verma, IIIT Una 2027*
