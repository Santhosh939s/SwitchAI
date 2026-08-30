# SwitchAI — "One memory. Many AI models."

> **BuildSprint 2026 Project by LatentForce**  
> Built exclusively using **LatentCode** AI coding harness and enhanced with SkillPatch agent skills.

SwitchAI decouples AI conversation state and memory from model providers. The user maintains **ONE** shared memory system across Anthropic Claude, Google Gemini, and OpenAI GPT.

---

## Key Features

1. **Model-Independent Shared Memory:** Durable goals, facts, decisions, and constraints belong to SwitchAI rather than any provider.
2. **Context Passport:** Visual representation of transferred goals, facts, decisions, and conversation summary when switching providers.
3. **Resilient Automatic Fallback:** Bounded exponential backoff, rate limit (429) detection, circuit breaker cooldowns, and automatic rerouting without losing thread state.
4. **Smart Task Auto-Routing:** Request classifier (`coding`, `reasoning`, `long_context`, `summarization`, `fast_response`) with user strategy priority options (`quality`, `speed`, `cost`, `balanced`).
5. **Secure Provider Connections:** Credentials encrypted at rest via 32-byte Fernet symmetric keys; zero client-side key storage.
6. **Internal Telemetry Dashboard:** Performance telemetry tracking requests, latency, token estimates, and fallback counts.

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
$env:PYTHONPATH="backend"
python -m uvicorn app.main:app --reload --port 8000
```

Run test suite:
```bash
$env:PYTHONPATH="backend"
python -m pytest backend/tests
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

1. **Landing Page:** Open `http://localhost:5173` → Click "Start Chatting".
2. **Signup / Login:** Create a new SwitchAI account at `/signup`.
3. **Connect Providers:** Navigate to `/settings/providers` → Connect Anthropic, Gemini, or OpenAI keys (or test with mock keys).
4. **Start Chat:** Navigate to `/chat` → Type: *"I am building a college food delivery app using FastAPI, PostgreSQL, and React."*
5. **Shared Memory Inspection:** Click "🧠 Shared Memory" → Verify extracted goals, tech stack facts, and architectural decisions.
6. **Switch Provider:** Change provider header selector to **Claude (Anthropic)** or **Gemini (Google)** → View the **Context Passport** sidebar and transfer notification banner.
7. **Simulate Fallback:** Provider rate limits or timeouts automatically trigger fallback to secondary healthy providers while preserving thread state.
8. **Telemetry:** Visit `/usage` to view tracked requests, average latency, and fallback counts.
