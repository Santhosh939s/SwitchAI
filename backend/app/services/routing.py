from typing import Dict, List, Tuple, Optional
from sqlalchemy.orm import Session
from app.services.providers import get_user_provider_connections, SUPPORTED_PROVIDERS, get_adapter
from app.services.fallback import is_circuit_open
from app.schemas.routing import RoutingPreviewResponse

TASK_CATEGORIES = [
    "general", "coding", "reasoning", "long_context",
    "summarization", "creative", "transformation", "fast_response"
]

def classify_prompt_task(prompt: str) -> str:
    text = prompt.lower().strip()
    words = text.split()

    if "summarize" in text or "summary" in text or "tldr" in text:
        return "summarization"
    if len(words) > 300 or "long document" in text or "page" in text or "report" in text or "analyze this long" in text or "pdf" in text:
        return "long_context"
    if "def " in text or "class " in text or "function" in text or "code" in text or "bug" in text or "api" in text or "sql" in text or "git" in text:
        return "coding"
    if "why" in text or "prove" in text or "explain architectural" in text or "logic" in text or "math" in text or "compare" in text:
        return "reasoning"
    if "write a story" in text or "poem" in text or "creative" in text:
        return "creative"
    if "convert" in text or "format" in text or "json to" in text or "translate" in text:
        return "transformation"
    if len(words) < 8 or "quick" in text or "fast" in text:
        return "fast_response"

    return "general"

def route_request(db: Session, user_id: str, prompt: str, priority: str = "balanced") -> RoutingPreviewResponse:
    task_cat = classify_prompt_task(prompt)
    conns = get_user_provider_connections(db, user_id)

    # Filter connected candidate providers for user_id
    connected = [
        p for p in SUPPORTED_PROVIDERS 
        if p in conns and conns[p].status in ("CREDENTIALS_SAVED", "HEALTHY") and not is_circuit_open(p)
    ]

    # Fallback to supported providers if no user keys are connected yet (e.g. preview mode)
    if not connected:
        connected = [p for p in SUPPORTED_PROVIDERS if not is_circuit_open(p)]
    if not connected:
        connected = SUPPORTED_PROVIDERS

    p_priority = (priority or "balanced").lower()

    selected_provider = connected[0]
    rationale = ""

    if task_cat == "long_context" and "gemini" in connected:
        selected_provider = "gemini"
        rationale = "Selected Gemini because this request requires long-context analysis."
    elif task_cat == "coding" and "deepseek" in connected:
        selected_provider = "deepseek"
        rationale = "Selected DeepSeek for specialized code generation & reasoning."
    elif task_cat == "coding" and "openai" in connected and p_priority in ("quality", "balanced"):
        selected_provider = "openai"
        rationale = "Selected OpenAI GPT for structured coding & API specification task."
    elif task_cat == "reasoning" and "deepseek" in connected:
        selected_provider = "deepseek"
        rationale = "Selected DeepSeek R1 for deep mathematical & logical reasoning."
    elif task_cat == "reasoning" and "anthropic" in connected:
        selected_provider = "anthropic"
        rationale = "Selected Claude because this request requires deep critique and multi-step reasoning."
    elif p_priority == "speed" and "groq" in connected:
        selected_provider = "groq"
        rationale = "Selected Groq Llama 3 for ultra-low-latency fast response execution."
    elif p_priority == "speed" and "gemini" in connected:
        selected_provider = "gemini"
        rationale = "Selected Gemini for high-throughput fast response optimization."
    else:
        rationale = f"Selected {selected_provider.upper()} based on connected provider health & task category '{task_cat}'."

    adapter = get_adapter(selected_provider)
    conn = conns.get(selected_provider)
    if conn and conn.default_model:
        selected_model = conn.default_model
    else:
        models = adapter.list_models()
        selected_model = models[0] if models else "default"

    return RoutingPreviewResponse(
        task_category=task_cat,
        selected_provider=selected_provider,
        selected_model=selected_model,
        rationale=rationale,
        priority=p_priority,
        available_providers=connected
    )
