# SwitchAI — "One memory. Many AI models."

> **BuildSprint 2026 Project by LatentForce**  
> Built exclusively using **LatentCode** AI coding harness and enhanced with SkillPatch agent skills.

SwitchAI decouples AI conversation state and memory from model providers. The user maintains **ONE** shared memory system across 7 Cloud AI Providers (Google Gemini, OpenAI GPT, Anthropic Claude, DeepSeek, Groq LPU, Mistral AI, Cohere).

---

## Key Architectural Features

1. **Model-Independent Shared Memory:** Durable goals, facts, decisions, and constraints belong to SwitchAI rather than any single provider.
2. **Context Passport:** Visual representation of transferred goals, facts, decisions, and conversation summary when switching providers mid-thread with 0 context loss.
3. **User Profile & Account Management:**
   - Bottom-left sidebar user badge displaying profile avatar and name.
   - Interactive Profile Settings Modal allowing users to update their Display Name and Email Address persisted in SQLite via `PATCH /api/auth/profile`.
4. **Strict Sign-Up / Sign-In Account Verification:**
   - Account creation occurs strictly via Sign-Up (`/register`).
   - Sign-In (`/login`) verifies account existence first, returning clear feedback (*"No account found with this email address. Please sign up first"* or *"Incorrect password"*).
5. **RAG-First Execution & Control (`🧠 RAG` Toggle):**
   - **RAG-First Lookup (ON):** Checks local 28-domain grounded knowledge base and shared memory first. If matched, returns answers instantly with **0 cloud token cost**.
   - **Direct Cloud AI (OFF):** Bypasses local pre-lookup, sending requests directly to Cloud AI model APIs.
6. **100% Free Live Web Search (`🌐 Web` Toggle):**
   - Keyless DuckDuckGo search integration with custom User-Agent Wikipedia REST API fallback.
   - Live web search facts are automatically extracted and permanently saved into SQLite shared memory (`memories` table).
7. **Concise Token-Efficient System Prompts:**
   - Enforces strict system instructions across Gemini, OpenAI, and Anthropic adapters: *"Be concise, clear, and token-efficient. Provide direct answers without unnecessary fluff."*
8. **28-Domain Grounded RAG Knowledge Base:**
   - Embedded knowledge base covering Science, Tech, AI/ML, CS, Programming, Math, Physics, Chemistry, Biology, Medicine, History, Geography, India, Civics, Economics, Business, Finance, Environment, Space, Engineering, Literature, Language, Culture, Sports, Everyday Life, and General Knowledge with acronym expansion (`ml` $\rightarrow$ `machine learning`, `ai` $\rightarrow$ `artificial intelligence`, `db` $\rightarrow$ `database`).
9. **Strict Connected Provider Isolation & Dynamic Model Discovery:**
   - Chat dropdowns show **ONLY** connected providers with valid keys.
   - Dynamic `/models` discovery filters out non-chat specialty models (`-tts`, `-transcribe`, `computer-use`, `deep-research`).
10. **Resilient Circuit Breaker & Fallback:**
    - Bounded exponential backoff, rate limit (429) detection, circuit breaker cooldowns, and automatic rerouting across connected providers or the offline RAG engine.
11. **Smart Task Auto-Routing:**
    - Request classifier (`coding`, `reasoning`, `long_context`, `summarization`, `fast_response`) with user strategy priorities (`quality`, `speed`, `cost`, `balanced`).
12. **File Context Uploads:**
    - Support for attaching `.txt`, `.md`, `.json`, `.csv` document summaries directly to the `ContextPackage`.
13. **LatentForce Cyber-Flame Theme Aesthetic:**
    - LatentForce Flame Orange `#EE5622` theme, dark obsidian background grid texture (`#0A0A0B`), glassmorphic cards, interactive model-switching simulator, and accordion FAQ.
14. **Secure Provider Connections:**
    - Credentials encrypted at rest via 32-byte Fernet symmetric keys; zero client-side key storage.
15. **Internal Telemetry Dashboard:**
    - Performance telemetry tracking requests, latency, token estimates, and fallback counts.

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
3. **Connect Providers:** Navigate to `/settings/providers` → Connect Gemini, OpenAI, DeepSeek, or Anthropic keys.
4. **Start Chat:** Navigate to `/chat` → Type: *"I am building a college food delivery app using FastAPI, PostgreSQL, and React."*
5. **Shared Memory Inspection:** Click "🧠 Shared Memory" → Verify extracted goals, tech stack facts, and architectural decisions.
6. **User Profile Settings:** Click your avatar badge in the bottom-left sidebar → Update your display name and email address.
7. **RAG-First Lookup (`🧠 RAG` Toggle):** Ask *"What is Machine Learning?"* → Observe instant 0-token response from RAG Knowledge Base. Toggle RAG Off for direct Cloud AI generation.
8. **Live Web Search (`🌐 Web` Toggle):** Click `🌐 Web` on the chat bar → Type: *"What is the latest news on AI?"* → Observe live web search results retrieved and saved into shared memory.
9. **Switch Provider:** Change provider header selector to **Gemini (Google)**, **GPT (OpenAI)**, or **DeepSeek** → View the **Context Passport** sidebar and transfer notification banner.
10. **Simulate Fallback / RAG Engine:** If cloud provider rate limits or quota errors occur, SwitchAI automatically falls back to secondary healthy providers or the offline **RAG Knowledge Engine**.
11. **Telemetry:** Visit `/usage` to view tracked requests, average latency, and fallback counts.
