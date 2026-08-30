import time
from typing import List, AsyncGenerator, Optional
import httpx
from app.core.config import settings
from app.adapters.base import ProviderAdapter, ProviderResponse, NormalizedError, ProviderHealth
from app.schemas.context import ContextPackage

class LocalAdapter(ProviderAdapter):
    def validate_credentials(self, api_key: str) -> bool:
        base_url = settings.LOCAL_AI_BASE_URL.rstrip('/')
        try:
            with httpx.Client(timeout=1.0) as client:
                res = client.get(f"{base_url}/models")
                return res.status_code == 200
        except Exception:
            return False

    def list_models(self) -> List[str]:
        preferred = settings.LOCAL_AI_MODEL or "Qwen2.5-1.5B-Instruct-Q4_K_M"
        return [preferred]

    def discover_models(self, api_key: str) -> List[str]:
        base_url = settings.LOCAL_AI_BASE_URL.rstrip('/')
        try:
            with httpx.Client(timeout=1.0) as client:
                res = client.get(f"{base_url}/models")
                if res.status_code == 200:
                    data = res.json()
                    models_data = data.get("data", [])
                    discovered = [m.get("id") for m in models_data if m.get("id")]
                    if discovered:
                        preferred = settings.LOCAL_AI_MODEL
                        if preferred and preferred in discovered:
                            return [preferred] + [m for m in discovered if m != preferred]
                        return discovered
        except Exception:
            pass
        return self.list_models()

    def _build_prompt_context(self, context_package: ContextPackage) -> str:
        parts = ["[SwitchAI Unified Shared Memory Context (Local AI Inference)]"]
        if context_package.user_goal:
            parts.append(f"Goal: {context_package.user_goal}")
        if context_package.summary:
            parts.append(f"Summary: {context_package.summary}")
        if context_package.relevant_memories:
            mem_lines = [f"- [{m.category.upper()}] {m.key}: {m.value}" for m in context_package.relevant_memories]
            parts.append("Shared Memories:\n" + "\n".join(mem_lines))
        return "\n".join(parts)

    def generate(self, context_package: ContextPackage, api_key: str, model: Optional[str] = None) -> ProviderResponse:
        base_url = settings.LOCAL_AI_BASE_URL.rstrip('/')
        discovered = self.discover_models(api_key)
        
        # Use requested model if available in discovered, otherwise first discovered, or fallback
        if model and model in discovered:
            model_name = model
        elif discovered:
            model_name = discovered[0]
        else:
            model_name = settings.LOCAL_AI_MODEL or "Qwen2.5-1.5B-Instruct-Q4_K_M"

        context_str = self._build_prompt_context(context_package)
        start_time = time.time()

        messages = [{"role": "system", "content": context_str}]
        for m in context_package.recent_messages[-6:]:
            messages.append({"role": m.role, "content": m.content})
        messages.append({"role": "user", "content": context_package.current_message})

        try:
            with httpx.Client(timeout=30.0) as client:
                res = client.post(
                    f"{base_url}/chat/completions",
                    headers={"Content-Type": "application/json"},
                    json={
                        "model": model_name,
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 1024
                    }
                )

                if res.status_code == 404:
                    raise ValueError(f"Selected Local AI model '{model_name}' is not found on endpoint {base_url}.")

                if res.status_code != 200:
                    raise RuntimeError(f"Local AI Server Error (HTTP {res.status_code}): {res.text}")

                data = res.json()
                out_text = data["choices"][0]["message"]["content"]
                tokens = data.get("usage", {}).get("total_tokens", 0)
                latency = (time.time() - start_time) * 1000

                return ProviderResponse(
                    content=out_text,
                    provider="local",
                    model=model_name,
                    latency_ms=round(latency, 1),
                    estimated_tokens=tokens
                )
        except (httpx.ConnectError, httpx.ConnectTimeout) as e:
            raise RuntimeError(f"Local AI is offline. Start the local model server at {base_url}.")
        except Exception as e:
            raise e

    async def stream(self, context_package: ContextPackage, api_key: str, model: Optional[str] = None) -> AsyncGenerator[str, None]:
        yield "[Local AI Stream] Active."

    def normalize_error(self, error: Exception) -> NormalizedError:
        err_msg = str(error)
        err_lower = err_msg.lower()
        if "offline" in err_lower or "connect" in err_lower:
            return NormalizedError(code="SERVICE_UNAVAILABLE", message="Local AI is offline. Start the local model server.", retry_after_seconds=2, is_retryable=True)
        if "timeout" in err_lower or "504" in err_msg:
            return NormalizedError(code="TIMEOUT", message="Local AI inference request timed out.", retry_after_seconds=2, is_retryable=True)
        if "404" in err_msg or "not found" in err_lower:
            return NormalizedError(code="BAD_REQUEST", message=err_msg, is_retryable=False)
        return NormalizedError(code="UNKNOWN", message=err_msg, is_retryable=False)

    def get_health(self, api_key: str) -> ProviderHealth:
        base_url = settings.LOCAL_AI_BASE_URL.rstrip('/')
        start_time = time.time()
        try:
            with httpx.Client(timeout=1.0) as client:
                res = client.get(f"{base_url}/models")
                latency = (time.time() - start_time) * 1000
                if res.status_code == 200:
                    discovered = self.discover_models(api_key)
                    return ProviderHealth(
                        provider="local",
                        is_healthy=True,
                        status_message=f"HEALTHY (Server running at {base_url})",
                        latency_ms=round(latency, 1),
                        discovered_models=discovered
                    )
        except Exception:
            pass

        return ProviderHealth(
            provider="local",
            is_healthy=False,
            status_message=f"NOT_RUNNING (Local AI is offline at {base_url})",
            discovered_models=self.list_models()
        )

    def estimate_usage(self, context_package: ContextPackage) -> int:
        return len(context_package.current_message.split()) * 4
