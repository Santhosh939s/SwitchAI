# SwitchAI — "One memory. Many AI models."
## Comprehensive Master Project Specification & Technical Architecture

---

## 1. Executive Summary

| Attribute | Details |
| :--- | :--- |
| **Project Name** | **SwitchAI** |
| **Core Tagline** | *"One memory. Many AI models."* |
| **Harness / Framework** | Built with **LatentCode** AI Coding Harness & SkillPatch Agent Skills |
| **Repository** | [GitHub: Santhosh939s/Switch-AI-LatentForce](https://github.com/Santhosh939s/Switch-AI-LatentForce) |
| **Backend Stack** | Python 3.8+, FastAPI, SQLAlchemy ORM, SQLite, Pydantic v2, Pytest, Fernet Encryption |
| **Frontend Stack** | React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons, Framer Motion |
| **Theme / Aesthetic** | **LatentForce Cyber-Flame** (Flame Orange `#EE5622`, Obsidian `#0A0A0B`, Glassmorphism) |
| **Supported Models** | Google Gemini, OpenAI GPT, Anthropic Claude, DeepSeek, Groq LPU, Mistral AI, Cohere, Local Ollama + Local Offline RAG |

SwitchAI is an intelligent, provider-agnostic conversational intelligence platform designed to eliminate model lock-in. It decouples conversation memory, durable facts, user goals, and architectural decisions from individual AI providers, enabling frictionless switching mid-thread across 8 major AI providers (7 Cloud LLMs + Local Ollama) and an embedded offline RAG engine with zero context loss.

---

## 2. Problem Statement & Industry Bottlenecks

Modern generative AI workflows suffer from severe architectural fragmentation and provider lock-in:

1. **Siloed Provider Context & Memory Lock-In:**
   - Conversation context in ChatGPT, Claude.ai, or Gemini is trapped within that specific vendor's silo.
   - Migrating a long-running problem solving session from GPT-4o to Claude 3.5 Sonnet requires manually restating requirements, leading to prompt fatigue and loss of implicit constraints.

2. **Catastrophic Context Loss During Provider Outages / Rate Limits (429):**
   - When a provider experiences rate limits (HTTP 429), quota depletion, or service degradation (503), workflows halt immediately without intelligent automated fallback to an alternative model with intact context.

3. **High Token Costs for Repetitive Grounded Knowledge:**
   - Routine queries (e.g., standard definitions, computer science concepts, algorithm explanations) consume expensive cloud tokens when they could be served instantly by a local grounded knowledge engine for $0.

4. **Inconsistent System Instructions & Token Bloat:**
   - Different model APIs require disparate system prompt structures, often resulting in token-heavy fluff and divergent formatting.

5. **Security Risks with Raw API Key Storage:**
   - Many web apps store raw provider API keys in browser `localStorage`, creating vulnerabilities to XSS attacks and credential leakage.

---

## 3. The SwitchAI Solution: Architectural Philosophy

SwitchAI establishes a **Universal Memory Layer** that sits between the client and AI model providers.

```
                      +------------------------------------------+
                      |               USER CLIENT                |
                      |   React 18 + TS + Cyber-Flame UI         |
                      +--------------------+---------------------+
                                           |  HTTPS / REST / SSE
                                           v
                      +------------------------------------------+
                      |         SWITCHAI CORE BACKEND            |
                      |           (FastAPI Gateway)              |
                      +--------------------+---------------------+
                                           |
                +--------------------------+--------------------------+
                |                                                     |
                v                                                     v
+-------------------------------+                     +-------------------------------+
|     SHARED MEMORY ENGINE      |                     |    SMART ROUTER & FALLBACK    |
| • Goals        • Decisions    |                     | • Task Classifier (Coding/RAG)|
| • Facts        • Constraints  |                     | • Priority Strategy (Speed/$) |
| • Preferences  • Summaries    |                     | • Circuit Breaker (30s Reset) |
+---------------+---------------+                     +---------------+---------------+
                |                                                     |
                +--------------------------+--------------------------+
                                           |
                                   [ ContextPackage ]
                                           |
     +-------------+-------------+---------+---------+-------------+-------------+
     |             |             |                   |             |             |
     v             v             v                   v             v             v
+---------+   +---------+   +---------+         +---------+   +---------+   +---------+
| Gemini  |   | OpenAI  |   | Claude  |   ...   | DeepSeek|   | Groq    |   | 28-Dom  |
| Adapter |   | Adapter |   | Adapter |         | Adapter |   | Adapter |   | RAG Eng |
+---------+   +---------+   +---------+         +---------+   +---------+   +---------+
```

### Core Value Pillars:
* **One Shared Memory:** Durable memory items (`goal`, `fact`, `decision`, `constraint`, `preference`) belong to the user thread, not the AI provider.
* **Context Passport:** A visual and computational data payload transferred across models when switching providers mid-thread.
* **RAG-First Execution (`🧠 RAG` Toggle):** Directs incoming prompts to an offline 28-domain grounded knowledge engine with acronym expansion before reaching external APIs.
* **Free Live Web Search (`🌐 Web` Toggle):** Integrated keyless DuckDuckGo search with Wikipedia REST API fallback, auto-extracting facts into SQLite memory.
* **Zero Client-Side Keys:** All credentials encrypted at rest using 32-byte Fernet symmetric encryption.

---

## 4. Key Subsystems & Technical Details

### 4.1. Universal Memory & Context Passport Engine

Memory in SwitchAI is categorized into deterministic semantic types:

| Category | Description | Example |
| :--- | :--- | :--- |
| `goal` | Core objective of the user's workflow | *"Build an AI-powered triage platform with FastAPI & React"* |
| `fact` | Permanent project facts, libraries, tech stack details | *"PostgreSQL with asyncpg used for database storage"* |
| `decision` | Architectural and engineering choices finalized | *"Decided to use Fernet symmetric encryption for credential storage"* |
| `constraint` | Hard boundaries or negative constraints | *"Do not use Tailwind v4; strictly use Tailwind v3.4"* |
| `preference` | Style or response formatting preferences | *"Enforce concise, token-efficient system responses"* |
| `task_state` | Current execution status of active task items | *"Auth endpoints completed; currently building fallback router"* |

#### The `ContextPackage` Payload Structure:
```json
{
  "conversation_id": "conv_89f1a23c",
  "system_instruction": "Be concise, clear, and token-efficient. Provide direct answers without unnecessary fluff.",
  "memories": [
    {"category": "goal", "key": "target_app", "value": "SwitchAI platform"},
    {"category": "fact", "key": "backend_framework", "value": "FastAPI + SQLAlchemy"}
  ],
  "recent_messages": [
    {"role": "user", "content": "How do we handle rate limits?"},
    {"role": "assistant", "content": "Using exponential backoff and circuit breaker fallback."}
  ],
  "file_contexts": [],
  "web_search_context": ""
}
```

#### Context Passport:
When a provider switch is triggered (e.g., from DeepSeek to Gemini 1.5 Flash), the backend constructs a `ContextPassportResponse` containing extracted goals, key facts, decisions, and conversation summaries. The frontend displays this as a transfer notification banner and sidebar passport preview with 0 context loss.

---

### 4.2. Supported Multi-Model Providers & Adapter Abstraction

All model interactions conform to the unified abstract class `ProviderAdapter`:

```python
class ProviderAdapter(ABC):
    @abstractmethod
    def validate_credentials(self, api_key: str) -> bool: ...
    @abstractmethod
    def list_models(self) -> List[str]: ...
    @abstractmethod
    def generate(self, context: ContextPackage, api_key: str, model: str) -> ProviderResponse: ...
    @abstractmethod
    def stream(self, context: ContextPackage, api_key: str, model: str) -> AsyncGenerator: ...
    @abstractmethod
    def normalize_error(self, error: Exception) -> NormalizedError: ...
    @abstractmethod
    def get_health(self, api_key: str) -> ProviderHealth: ...
```

#### Adapter Implementations:
1. **Google Gemini (`gemini.py`):** Supports `gemini-1.5-flash`, `gemini-1.5-pro`, `gemini-2.0-flash`. Formats `ContextPackage` into Gemini contents and system instructions.
2. **OpenAI GPT (`openai.py`):** Supports `gpt-4o`, `gpt-4o-mini`, `o1-mini`. Formats context into OpenAI standard ChatCompletion JSON messages.
3. **Anthropic Claude (`anthropic.py`):** Supports `claude-3-5-sonnet-latest`, `claude-3-5-haiku-latest`. Injects top-level system strings and message objects.
4. **DeepSeek (`deepseek.py`):** Supports `deepseek-chat`, `deepseek-reasoner` via standard OpenAI-compatible API schemas.
5. **Groq LPU (`groq.py`):** Supports `llama-3.3-70b-versatile`, `llama-3.1-8b-instant`, `mixtral-8x7b-32768` for sub-second responses.
6. **Mistral AI (`mistral.py`):** Supports `mistral-large-latest`, `mistral-small-latest`, `codestral-latest`.
7. **Cohere (`cohere.py`):** Supports `command-r-plus`, `command-r`.
8. **Offline Grounded RAG (`rag.py`):** Local knowledge engine requiring 0 external credentials and 0 cloud token spend.

#### Dynamic Model Discovery & Connected Provider Isolation:
- Dropdown menus strictly filter providers to **ONLY** those with verified connected API keys in the database.
- Dynamic `/models` endpoint automatically filters out specialty non-chat models (`-tts`, `-transcribe`, `-audio`, `computer-use`, `deep-research`).

---

### 4.3. 28-Domain Grounded Offline RAG Engine

The embedded RAG system provides instant, deterministic domain knowledge at zero token cost.

#### Features:
- **Acronym Expansion:** Expands shorthand queries prior to retrieval:
  - `ml` $\rightarrow$ `machine learning`
  - `ai` $\rightarrow$ `artificial intelligence`
  - `db` $\rightarrow$ `database`
  - `dl` $\rightarrow$ `deep learning`
  - `nlp` $\rightarrow$ `natural language processing`
- **28 Supported Knowledge Domains:**
  1. Science & Technology
  2. Artificial Intelligence & Machine Learning
  3. Computer Science & Data Structures
  4. Software Engineering & Programming Languages (Python, JS/TS, Go, Rust, C++)
  5. Mathematics & Statistics
  6. Physics (Classical & Quantum)
  7. Chemistry & Material Science
  8. Biology & Genetics
  9. Medicine & Healthcare
  10. World History & Ancient Civilizations
  11. Geography & World Cultures
  12. Indian History, Constitution & Geography
  13. Civics, Governance & International Law
  14. Economics & Monetary Policy
  15. Business, Startups & Venture Capital
  16. Personal Finance & Investment
  17. Environmental Science & Sustainability
  18. Astronomy & Space Exploration
  19. Mechanical, Civil & Electrical Engineering
  20. Literature, Philosophy & Arts
  21. Linguistics & Natural Languages
  22. World Cultures & Traditions
  23. Sports, Olympics & Athletics
  24. Everyday Life, Health & Productivity
  25. General Knowledge & Trivia
  26. Cybersecurity & Cryptography
  27. Cloud Computing & DevOps
  28. System Design & Microservices Architecture

---

### 4.4. 100% Free Live Web Search Integration

SwitchAI includes built-in live internet search capabilities without requiring paid third-party search API keys:

1. **Primary Provider:** Keyless DuckDuckGo Instant Answer / HTML Search (`search_web_ddg()`).
2. **Fallback Provider:** Wikipedia REST API (`search_wikipedia()`) with custom `User-Agent` headers (`SwitchAI-Bot/1.0`) if DuckDuckGo returns rate limits (HTTP 202/429).
3. **Auto-Memory Persistence:** Relevant extracted web facts are immediately stored in the SQLite `memories` table for long-term thread recall.

---

### 4.5. Smart Auto-Routing & Resilient Circuit Breakers

#### Task Classification:
Incoming user prompts are analyzed and classified into:
* `coding` (def, class, function, code, bug, sql, git)
* `reasoning` (why, prove, logic, math, compare)
* `long_context` (>300 words, document, report, analyze)
* `summarization` (summarize, tldr, overview)
* `creative` (story, poem, script)
* `transformation` (convert, format, json to, translate)
* `fast_response` (<8 words, quick, ping)
* `general`

#### Routing Strategies:
* **Quality First:** Routes coding to DeepSeek / GPT-4o, reasoning to Claude 3.5 Sonnet / o1.
* **Speed First:** Routes to Groq LPU (Llama 3.3 70B / 8B).
* **Cost First:** Routes to RAG engine or lightweight models (Gemini 1.5 Flash, GPT-4o-mini).
* **Balanced:** Dynamically matches model tier to classified task complexity.

#### Resilient Circuit Breaker:
- **Error Normalization:** Standardizes cloud exceptions into `RATE_LIMIT` (429), `TIMEOUT` (408/504), `SERVICE_UNAVAILABLE` (503), `AUTHENTICATION_ERROR` (401), or `CONTEXT_TOO_LARGE` (400).
- **Circuit State Machine:** Failed providers enter a 30-second cooldown period during which subsequent requests are automatically routed to the next healthy provider in the fallback chain.

---

### 4.6. Security & Credential Isolation

- **Fernet Symmetric Encryption:** All user API keys are encrypted at rest using a 32-byte cryptographic key (`ENCRYPTION_KEY`).
- **Response Sanitization:** Backend API responses never include raw or encrypted keys in JSON payloads.
- **Zero Client-Side Storage:** Keys are never stored in `localStorage` or `sessionStorage`.

---

### 4.7. Authentication & Profile Management

- **Strict Sign-Up (`/register`):** Account creation is strictly isolated to Sign-Up.
- **Verification on Sign-In (`/login`):** Validates email existence first:
  - Missing account: *"No account found with this email address. Please sign up first."*
  - Invalid password: *"Incorrect password. Please verify your credentials."*
- **User Profile Management (`PATCH /api/auth/profile`):** Bottom-left sidebar avatar badge with interactive modal allowing updates to Display Name and Email Address.
- **Database Schema Auto-Migration (`init_db.py`):** Automatically migrates SQLite database files on boot (`ALTER TABLE users ADD COLUMN name VARCHAR`) preventing 500 errors on legacy databases.

---

## 5. Database Schema & ORM Models

```
 +--------------------------------------------------------------------------------+
 |                                  DATABASE SCHEMA                               |
 +--------------------------------------------------------------------------------+

      +-------------------+                  +------------------------+
      |      users        |                  |  provider_credentials  |
      +-------------------+                  +------------------------+
      | id (PK, String)   |<----+            | id (PK, String)        |
      | email (String, UQ)|     |            | user_id (FK -> users)  |
      | hashed_password   |     |            | provider (String)      |
      | name (String)     |     |            | encrypted_api_key      |
      | created_at (Date) |     |            | is_active (Boolean)    |
      +-------------------+     |            | last_validated_at      |
                |               |            +------------------------+
                | 1:N           |
                v               | 1:N
      +-------------------+     |            +------------------------+
      |   conversations   |     +----------->|       usage_logs       |
      +-------------------+                  +------------------------+
      | id (PK, String)   |<----+            | id (PK, String)        |
      | user_id (FK)      |     |            | user_id (FK -> users)  |
      | title (String)    |     |            | conversation_id (FK)   |
      | current_provider  |     |            | provider (String)      |
      | current_model     |     |            | model (String)         |
      | created_at (Date) |     |            | prompt_tokens (Int)    |
      | updated_at (Date) |     |            | completion_tokens (Int)|
      +-------------------+     |            | latency_ms (Float)     |
        |               |       |            | is_fallback (Boolean)  |
        | 1:N           | 1:N   |            | created_at (Date)      |
        v               v       |            +------------------------+
  +-----------+   +-----------+ |
  | messages  |   | memories  | |
  +-----------+   +-----------+ |
  | id (PK)   |   | id (PK)   | |
  | conv_id   |   | conv_id   | |
  | role      |   | category  | |
  | content   |   | key       | |
  | provider  |   | value     | |
  | model     |   | is_pinned | |
  | tokens    |   | created_at| |
  | created_at|   +-----------+ |
  +-----------+                 |
                                | 1:N
                        +----------------+
                        |     files      |
                        +----------------+
                        | id (PK, String)|
                        | conv_id (FK)   |
                        | filename (Str) |
                        | content_summary|
                        | file_size (Int)|
                        | created_at     |
                        +----------------+
```

---

## 6. Complete REST API Reference

### Authentication (`/api/auth`)
- `POST /api/auth/register` — Create new user account (`email`, `password`, `name`).
- `POST /api/auth/login` — Authenticate and receive JWT access token.
- `GET /api/auth/me` — Retrieve current authenticated user profile.
- `PATCH /api/auth/profile` — Update user display name and email address.

### Conversations & Chat (`/api/conversations`)
- `GET /api/conversations` — List all conversations for authenticated user.
- `POST /api/conversations` — Create new conversation thread.
- `GET /api/conversations/{id}` — Retrieve conversation details with message history.
- `POST /api/conversations/{id}/messages` — Send message and generate AI response. Supports query parameters:
  - `rag_only=true|false` (Toggle grounded RAG execution)
  - `web_search=true|false` (Toggle live web search)
- `POST /api/conversations/{id}/switch-provider` — Switch active model provider mid-thread and generate Context Passport.
- `GET /api/conversations/{id}/passport` — Retrieve current visual Context Passport.
- `DELETE /api/conversations/{id}` — Delete conversation thread and associated memory.

### Shared Memory (`/api/memory`)
- `GET /api/memory/{conversation_id}` — List all structured memory items for thread.
- `POST /api/memory/{conversation_id}` — Manually add memory item (`category`, `key`, `value`, `is_pinned`).
- `PATCH /api/memory/{memory_id}` — Edit existing memory item.
- `DELETE /api/memory/{memory_id}` — Remove memory item.

### Provider Management (`/api/providers`)
- `GET /api/providers` — List all 8 providers with connection status and model lists.
- `POST /api/providers/{provider}/connect` — Save and encrypt provider API key.
- `DELETE /api/providers/{provider}/disconnect` — Disconnect provider and remove stored key.
- `GET /api/providers/{provider}/models` — Discover available chat models for provider.

### Smart Routing & Telemetry (`/api/routing`, `/api/usage`, `/api/health`)
- `POST /api/routing/preview` — Preview recommended model provider based on prompt analysis.
- `GET /api/usage/summary` — Retrieve aggregated telemetry: total requests, average latency, tokens, fallbacks.
- `GET /api/health` — Gateway health and status check.

---

## 7. Frontend Design System & UI Components

### LatentForce Cyber-Flame Design System:
* **Color Palette:**
  * Flame Orange Accent: `#EE5622` / `rgb(238, 86, 34)`
  * Flame Amber Secondary: `#F27A4B`
  * Dark Obsidian Background: `#0A0A0B` / `#111114`
  * Surface Card Slate: `#18181B` with `border-white/10`
* **Glassmorphism:** `backdrop-blur-md bg-zinc-900/70 border border-zinc-800/80`
* **Typography:** Modern clean sans-serif typography hierarchy.

### Key UI Pages & Components:
1. **Landing Page (`LandingPage.tsx`):**
   - Hero banner with animated badge and value proposition.
   - Interactive Live Model-Switching Simulator.
   - Architecture walkthrough with interactive cards.
   - Responsive FAQ Accordion.
2. **Chat Workspace (`ChatPage.tsx`):**
   - Provider Header Selector (strictly displays connected providers).
   - `🧠 RAG` and `🌐 Web` direct action toggles on chat input bar.
   - Context Passport sidebar drawer and transfer notification banners.
   - Bottom-left sidebar user profile avatar badge with interactive edit modal.
3. **Shared Memory Inspector (`MemoryPage.tsx`):**
   - Categorized badges for Goals, Facts, Decisions, Constraints, and Task States.
   - Pin, edit, and delete controls for user-curated memory.
4. **Provider Settings Hub (`ProvidersPage.tsx`):**
   - Connection cards for all 7 cloud providers + local RAG engine.
   - Encryption badge and dynamic model discovery list.
5. **Usage & Telemetry Dashboard (`UsagePage.tsx`):**
   - Performance metrics, token estimates, latency breakdowns, and fallback counters.

---

## 8. Installation, Setup & Verification

### Prerequisites
* Python 3.8 or higher
* Node.js 18 or higher & npm
* SQLite3

### 1. Environment Setup
```bash
# Clone the repository
git clone https://github.com/Santhosh939s/Switch-AI-LatentForce.git
cd Switch-AI-LatentForce

# Create environment configuration
cp .env.example .env
```

`.env` configuration keys:
```ini
JWT_SECRET=supersecret_switchai_jwt_key_2026_latentforce
ENCRYPTION_KEY=32_byte_base64_fernet_key_here
DATABASE_URL=sqlite:///./switchai.db
```

### 2. Backend (FastAPI) Setup
```bash
cd backend
python -m pip install -r requirements.txt

# Run test suite (19 test cases)
pytest

# Start backend development server
python -m uvicorn app.main:app --reload --port 8000
```

### 3. Frontend (React + Vite) Setup
```bash
cd ../frontend
npm install

# Run frontend test/build
npm run build

# Start frontend development server
npm run dev
```

The application will be accessible at: `http://localhost:5173`.

---

## 9. First-Run Evaluation & Demo Workflow

1. **Sign Up:** Open `http://localhost:5173/signup` $\rightarrow$ Create an account (`Full Name`, `Email`, `Password`).
2. **Connect Providers:** Navigate to `Settings` $\rightarrow$ Connect Gemini, OpenAI, DeepSeek, or Anthropic API keys.
3. **Ask Grounded RAG Query (0-Token Cost):**
   - In Chat, keep `🧠 RAG` ON.
   - Prompt: *"What is Machine Learning?"* or *"Explain quantum mechanics."*
   - Verify instant response generated with **0 cloud token spend**.
4. **Extract Live Web Information:**
   - Click `🌐 Web` toggle ON.
   - Prompt: *"What are the latest updates in AI research?"*
   - Verify DuckDuckGo/Wikipedia results retrieved and auto-saved to Shared Memory.
5. **Establish Shared Thread Context:**
   - Prompt: *"I am building a smart agriculture IoT monitoring system with FastAPI, ESP32 microcontrollers, and React."*
6. **Inspect Shared Memory:**
   - Click `🧠 Shared Memory` in the navigation bar.
   - Verify automatically extracted goals, tech stack facts, and architecture decisions.
7. **Switch Provider Mid-Thread:**
   - In the model header dropdown, switch from **Gemini** to **GPT (OpenAI)** or **DeepSeek**.
   - Observe the **Context Passport** transfer banner displaying transferred goals and constraints.
   - Follow-up prompt: *"What database should I use for this IoT project?"*
   - Notice the new model immediately understands the full project context without needing re-explanation.
8. **Update User Profile:**
   - Click the user avatar in the bottom-left sidebar $\rightarrow$ Update display name $\rightarrow$ Verify instant persistence.

---

## 10. Summary Matrix

| Capability | SwitchAI Implementation |
| :--- | :--- |
| **Provider Independence** | Decoupled memory layer shared across 7 Cloud LLMs + Local RAG |
| **Context Migration** | Context Package & Context Passport with 0 context loss |
| **RAG Grounding** | Embedded 28-domain knowledge engine with acronym expansion |
| **Live Internet Access** | Keyless DuckDuckGo search with Wikipedia REST API fallback |
| **Resilience & Uptime** | Bounded exponential backoff + 30s circuit breaker failover |
| **Credential Security** | 32-byte Fernet symmetric encryption; zero client-side key storage |
| **Account Isolation** | Strict Sign-Up creation + verified Sign-In with friendly error messages |
| **Visual Aesthetics** | LatentForce Cyber-Flame theme (`#EE5622`, dark obsidian, glassmorphism) |

---
*SwitchAI — Built by LatentForce for BuildSprint 2026.*
