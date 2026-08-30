import time
from typing import List, AsyncGenerator, Optional
import httpx
from app.adapters.base import ProviderAdapter, ProviderResponse, NormalizedError, ProviderHealth
from app.schemas.context import ContextPackage

class AnthropicAdapter(ProviderAdapter):
    DEFAULT_MODELS = ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022", "claude-3-opus-20240229"]

    def validate_credentials(self, api_key: str) -> bool:
        if not api_key or len(api_key) < 5:
            return False
        if api_key.startswith("mock_"):
            return True
        try:
            with httpx.Client(timeout=5.0) as client:
                res = client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json"
                    },
                    json={
                        "model": "claude-3-5-haiku-20241022",
                        "max_tokens": 1,
                        "messages": [{"role": "user", "content": "ping"}]
                    }
                )
                if res.status_code == 401:
                    return False
                return res.status_code in (200, 400, 429)
        except Exception:
            return False

    def list_models(self) -> List[str]:
        return self.DEFAULT_MODELS

    def discover_models(self, api_key: str) -> List[str]:
        return self.DEFAULT_MODELS

    def _build_prompt_context(self, context_package: ContextPackage) -> str:
        parts = ["[SwitchAI Unified Memory Context]"]
        if context_package.user_goal:
            parts.append(f"Goal: {context_package.user_goal}")
        if context_package.summary:
            parts.append(f"Summary: {context_package.summary}")
        if context_package.relevant_memories:
            mem_lines = [f"- [{m.category.upper()}] {m.key}: {m.value}" for m in context_package.relevant_memories]
            parts.append("Shared Memories:\n" + "\n".join(mem_lines))
        if context_package.relevant_files:
            file_lines = [f"- [{f.filename}] {f.content_summary}" for f in context_package.relevant_files]
            parts.append("Attached Files Context:\n" + "\n".join(file_lines))
        return "\n".join(parts)

    def _sanitize_model_name(self, model_name: Optional[str]) -> str:
        if not model_name:
            return "claude-3-5-sonnet-20241022"
        clean = model_name.strip()
        if clean in self.DEFAULT_MODELS:
            return clean
        if "haiku" in clean:
            return "claude-3-5-haiku-20241022"
        if "opus" in clean:
            return "claude-3-opus-20240229"
        return "claude-3-5-sonnet-20241022"

    def generate(self, context_package: ContextPackage, api_key: str, model: Optional[str] = None) -> ProviderResponse:
        model_name = self._sanitize_model_name(model)
        if not api_key:
            raise ValueError("Anthropic API key is missing. Please connect your Anthropic API key in Settings -> Providers.")

        context_str = self._build_prompt_context(context_package)
        start_time = time.time()

        if api_key.startswith("mock_"):
            return ProviderResponse(
                content=f"Hello! I am Anthropic Claude ({model_name}). I am active with your unified shared memory.",
                provider="anthropic",
                model=model_name,
                latency_ms=120.0,
                estimated_tokens=150
            )

        messages = []
        for m in context_package.recent_messages[-6:]:
            messages.append({"role": m.role, "content": m.content})
        messages.append({"role": "user", "content": context_package.current_message})

        with httpx.Client(timeout=25.0) as client:
            res = client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": model_name,
                    "system": context_str,
                    "max_tokens": 1024,
                    "messages": messages
                }
            )

            if res.status_code == 404:
                raise ValueError(f"Selected Anthropic model '{model_name}' is unavailable. Please select another model.")

            if res.status_code != 200:
                raise RuntimeError(f"Anthropic API Error (HTTP {res.status_code}): {res.text}")

            data = res.json()
            out_text = data["content"][0]["text"]
            tokens = data.get("usage", {}).get("output_tokens", 0)
            latency = (time.time() - start_time) * 1000

            return ProviderResponse(
                content=out_text,
                provider="anthropic",
                model=model_name,
                latency_ms=round(latency, 1),
                estimated_tokens=tokens
            )

    async def stream(self, context_package: ContextPackage, api_key: str, model: Optional[str] = None) -> AsyncGenerator[str, None]:
        res = self.generate(context_package, api_key, model)
        words = res.content.split(' ')
        for i, word in enumerate(words):
            chunk = word + (" " if i < len(words) - 1 else "")
            yield chunk
            time.sleep(0.02)

    def normalize_error(self, error: Exception) -> NormalizedError:
        err_msg = str(error)
        err_lower = err_msg.lower()
        if "rate" in err_lower or "429" in err_msg:
            return NormalizedError(code="RATE_LIMIT", message="Anthropic rate limit reached", retry_after_seconds=5, is_retryable=True)
        if "404" in err_msg or "not found" in err_lower:
            return NormalizedError(code="BAD_REQUEST", message=err_msg, is_retryable=False)
        if "timeout" in err_lower or "504" in err_msg or "502" in err_msg:
            return NormalizedError(code="TIMEOUT", message="Anthropic request timed out", retry_after_seconds=2, is_retryable=True)
        if "unavailable" in err_lower or "500" in err_msg or "503" in err_msg:
            return NormalizedError(code="SERVICE_UNAVAILABLE", message="Anthropic service temporarily unavailable", retry_after_seconds=3, is_retryable=True)
        if "401" in err_msg or "auth" in err_lower or "invalid x-api-key" in err_lower:
            return NormalizedError(code="AUTHENTICATION_ERROR", message=err_msg, is_retryable=False)
        return NormalizedError(code="UNKNOWN", message=err_msg, is_retryable=False)

    def get_health(self, api_key: str) -> ProviderHealth:
        start_time = time.time()
        is_valid = self.validate_credentials(api_key)
        latency = (time.time() - start_time) * 1000
        return ProviderHealth(
            provider="anthropic",
            is_healthy=is_valid,
            status_message="HEALTHY" if is_valid else "Credential Validation Failed",
            latency_ms=round(latency, 1) if is_valid else None,
            discovered_models=self.DEFAULT_MODELS
        )

    def estimate_usage(self, context_package: ContextPackage) -> int:
        return len(context_package.current_message.split()) * 4
