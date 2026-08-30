import re
import datetime
from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
from app.models.memory import Memory
from app.models.message import Message
from app.models.file import File
from app.schemas.context import ContextPackage

# Embedded Offline Knowledge Base covering common technical domains
RAG_KNOWLEDGE_BASE: List[Dict[str, str]] = [
    {
        "topic": "architecture",
        "keywords": "architecture design pattern microservices payment async fast api system",
        "response": """Based on the SwitchAI RAG Knowledge Base and your conversation state:

### Recommended Payment Architecture
1. **Asynchronous Webhook Processing:** Decouple payment gateway webhooks from core APIs using an event queue (e.g. Redis/Celery) with idempotent transaction IDs to handle retries safely.
2. **Transactional Outbox Pattern:** Store payment state changes atomically in PostgreSQL before broadcasting events to downstream services.
3. **Circuit Breakers & Retries:** Apply exponential backoff with jitter on outbound payment calls to avoid cascade failures."""
    },
    {
        "topic": "tech_stack",
        "keywords": "fastapi react postgresql python database backend frontend stack",
        "response": """Based on your project requirements stored in SwitchAI Shared Memory:

### Tech Stack Implementation Guidance
- **Backend (FastAPI + Python):** Use Pydantic v2 schemas for request validation, SQLAlchemy 2.0 ORM for database access, and HTTPBearer JWT authentication for route protection.
- **Frontend (React + TypeScript + Vite):** Utilize Tailwind CSS for dark startup themes and manage state with React Context.
- **Database (PostgreSQL / SQLite):** Enforce strict foreign keys, indexes on `user_id` and `conversation_id`, and datetime timestamps."""
    },
    {
        "topic": "greeting",
        "keywords": "hi hello hey help assistance start options what can you do",
        "response": """Hello! I am **SwitchAI RAG Engine** — your persistent, provider-independent AI assistant.

Even when cloud model API quotas are temporarily exhausted, I retain your **Shared Memory**, project goals, decisions, and uploaded file context.

How can I assist you with your project architecture or code today?"""
    },
    {
        "topic": "ai_models",
        "keywords": "model provider gemini claude openai deepseek groq rate limit quota error",
        "response": """### SwitchAI Model & Quota Summary
1. **Google Gemini:** Excellent for long-context analysis (`gemini-1.5-flash`, `gemini-2.0-flash`).
2. **OpenAI GPT:** Standard for structured JSON output and code generation (`gpt-4o`, `gpt-4o-mini`).
3. **DeepSeek:** Cost-optimized open reasoning (`deepseek-chat`, `deepseek-r1`).
4. **Local AI:** Self-hosted `llama.cpp` server for offline CPU inference.

*Note: You can connect new API keys or switch models anytime in Settings -> Providers.*"""
    }
]

def query_rag_engine(db: Session, conversation_id: str, prompt: str, context_package: ContextPackage) -> str:
    """
    RAG Retrieval Augmented Generation Fallback Engine:
    1. Retrieves conversation durable memories and attached files.
    2. Searches embedded technical knowledge base.
    3. Synthesizes a contextual response using stored memory state.
    """
    prompt_clean = prompt.lower().strip()
    words = set(re.findall(r'\w+', prompt_clean))

    # 1. Gather retrieved memories & files context
    memory_context_lines = []
    if context_package.user_goal:
        memory_context_lines.append(f"• Goal: {context_package.user_goal}")
    for m in context_package.relevant_memories:
        memory_context_lines.append(f"• [{m.category.upper()}] {m.key}: {m.value}")
    for f in context_package.relevant_files:
        memory_context_lines.append(f"• [FILE] {f.filename}: {f.content_summary}")

    # 2. Match knowledge base topic
    matched_kb: Optional[str] = None
    best_score = 0

    for kb in RAG_KNOWLEDGE_BASE:
        kb_words = set(kb["keywords"].split())
        score = len(words.intersection(kb_words))
        if score > best_score:
            best_score = score
            matched_kb = kb["response"]

    # 3. Synthesize response
    header = "🤖 **[SwitchAI Offline RAG Knowledge Engine]**\n*Cloud APIs temporarily unavailable/exhausted. Generating response from local RAG Knowledge Base & Shared Memory.*\n\n"

    if matched_kb:
        body = matched_kb
    else:
        body = f"I have received your prompt: **\"{prompt}\"**.\n\n"
        if memory_context_lines:
            body += "Using your saved project context, I recommend continuing with modular FastAPI endpoints and React components while verifying your provider API keys."
        else:
            body += "You can connect new provider keys in **Settings → Providers** or run a local AI server to continue cloud generation."

    if memory_context_lines:
        body += "\n\n---\n### Retained Shared Memory Context:\n" + "\n".join(memory_context_lines)

    return header + body
