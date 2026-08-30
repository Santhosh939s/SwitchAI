# SwitchAI — "One memory. Many AI models."

> **BuildSprint 2026 Project by LatentForce**  
> Built exclusively using **LatentCode** AI coding harness and enhanced with SkillPatch agent skills.

SwitchAI decouples AI conversation state and memory from model providers. The user maintains **ONE** shared memory system across 7 Cloud AI Providers (Google Gemini, OpenAI GPT, Anthropic Claude, DeepSeek, Groq LPU, Mistral AI, Cohere) and self-hosted **Local AI** (llama.cpp / Qwen2.5).

---

## Key Features

1. **Model-Independent Shared Memory:** Durable goals, facts, decisions, and constraints belong to SwitchAI rather than any single provider.
2. **Context Passport:** Visual representation of transferred goals, facts, decisions, and conversation summary when switching providers mid-thread.
3. **100% Free Live Web Search:** Keyless DuckDuckGo web search integration (`🌐 Web Search` toggle) that automatically extracts web facts and permanently stores them in SQLite shared memory.
4. **Offline RAG Knowledge Engine:** Learns from past chat history, shared memories, and file attachments to generate contextual responses when cloud API quotas are exhausted.
5. **Self-Hosted Local AI Provider:** Native support for local OpenAI-compatible inference servers (e.g. `llama.cpp` on `http://127.0.0.1:8080/v1` with Qwen2.5-1.5B) for 100% offline CPU execution.
6. **Resilient Automatic Fallback:** Bounded exponential backoff, rate limit (429) detection, circuit breaker cooldowns, and automatic rerouting without losing thread state.
7. **Smart Task Auto-Routing:** Request classifier (`coding`, `reasoning`, `long_context`, `summarization`, `fast_response`) with user strategy priority options (`quality`, `speed`, `cost`, `balanced`).
8. **File Context Uploads:** Support for attaching `.txt`, `.md`, `.json`, `.csv` document summaries directly to the `ContextPackage`.
9. **Secure Provider Connections:** Credentials encrypted at rest via 32-byte Fernet symmetric keys; zero client-side key storage.
10. **Internal Telemetry Dashboard:** Performance telemetry tracking requests, latency, token estimates, and fallback counts.

---

## Installed SkillPatch Skills

SwitchAI integrates three verified SkillPatch skills:
1. `api-integration`: Provider Adapter interface, retries, backoff, correlation tracking, and health validation.
2. `frontend-ui-dark-ts`: Dark theme design system, glassmorphism tokens, Tailwind CSS styling, and Framer Motion animations.
3. `api-rate-limiting-helper`: Rate-limiting header classification, circuit breakers, 429 response normalization, and fallback execution.

---

## Getting Started

### Environment Setup
Create a `.env` file from `.env.example`:
```bash
cp .env.example .env
```

### Backend (Python FastAPI)
```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

Run test suite:
```bash
pytest
```

### Frontend (React + TypeScript + Vite + Tailwind CSS)
```bash
cd frontend
npm install
npm run dev
```

Build production bundle:
```bash
npm run build
```

---

## First-Run Demo Flow

1. **Landing Page:** Open `http://localhost:5173` → Click "Start chatting".
2. **Signup / Login:** Create a new SwitchAI account at `/signup`.
3. **Connect Providers:** Navigate to `/settings/providers` → Connect Gemini, OpenAI, DeepSeek, or Anthropic keys (or test with mock keys / Local AI).
4. **Start Chat:** Navigate to `/chat` → Type: *"I am building a college food delivery app using FastAPI, PostgreSQL, and React."*
5. **Shared Memory Inspection:** Click "🧠 Shared Memory" → Verify extracted goals, tech stack facts, and architectural decisions.
6. **Live Web Search:** Click `🌐 Web Search` on the chat bar → Type: *"What is the latest news on FastAPI?"* → Observe web search facts saved into shared memory.
7. **Switch Provider:** Change provider header selector to **Gemini (Google)**, **GPT (OpenAI)**, or **DeepSeek** → View the **Context Passport** sidebar and transfer notification banner.
8. **Simulate Fallback / RAG Engine:** If cloud provider rate limits or quota errors occur, SwitchAI automatically falls back to secondary healthy providers or the offline **RAG Knowledge Engine**.
9. **Telemetry:** Visit `/usage` to view tracked requests, average latency, and fallback counts.
