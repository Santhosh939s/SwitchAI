import time
from typing import List, AsyncGenerator, Optional
import httpx
from app.adapters.base import ProviderAdapter, ProviderResponse, NormalizedError, ProviderHealth
from app.schemas.context import ContextPackage

class CohereAdapter(ProviderAdapter):
    DEFAULT_MODELS = ["command-r-plus", "command-r"]

    def validate_credentials(self, api_key: str) -> bool:
        if not api_key or len(api_key) < 5:
            return False
        if api_key.startswith("mock_"):
            return True
        try:
            with httpx.Client(timeout=5.0) as client:
                res = client.get(
                    "https://api.cohere.com/v1/models",
                    headers={"Authorization": f"Bearer {api_key}"}
                )
                if res.status_code == 401:
                    return False
                return res.status_code == 200
        except Exception:
            return False

    def list_models(self) -> List[str]:
        return self.DEFAULT_MODELS

    def discover_models(self, api_key: str) -> List[str]:
        if not api_key:
            return self.DEFAULT_MODELS
        try:
            with httpx.Client(timeout=8.0) as client:
                res = client.get("https://api.cohere.com/v1/models", headers={"Authorization": f"Bearer {api_key}"})
                if res.status_code == 200:
                    data = res.json()
                    discovered = [m["name"] for m in data.get("models", []) if "command" in m.get("name", "")]
                    if discovered:
                        return sorted(discovered)
        except Exception:
            pass
        return self.DEFAULT_MODELS

    def _build_prompt_context(self, context_package: ContextPackage) -> str:
        parts = ["[SwitchAI Unified Shared Memory Context]"]
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
            return "command-r-plus"
        clean = model_name.strip()
        if clean in self.DEFAULT_MODELS:
            return clean
        if "plus" in clean:
            return "command-r-plus"
        return "command-r"

    def generate(self, context_package: ContextPackage, api_key: str, model: Optional[str] = None) -> ProviderResponse:
        model_name = self._sanitize_model_name(model)
        if not api_key:
            raise ValueError("Cohere API key is missing. Please connect your Cohere API key in Settings -> Providers.")

        context_str = self._build_prompt_context(context_package)
        start_time = time.time()

        if api_key.startswith("mock_"):
            return ProviderResponse(
                content=f"Hello! I am Cohere Command ({model_name}). I am active with your unified shared memory.",
                provider="cohere",
                model=model_name,
                latency_ms=110.0,
                estimated_tokens=140
            )

        prompt_str = f"{context_str}\n\nUser Question: {context_package.current_message}"

        with httpx.Client(timeout=25.0) as client:
            res = client.post(
                "https://api.cohere.com/v1/chat",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model_name,
                    "message": prompt_str
                }
            )

            if res.status_code == 404:
                raise ValueError(f"Selected Cohere model '{model_name}' is unavailable. Please select another model.")

            if res.status_code != 200:
                raise RuntimeError(f"Cohere API Error (HTTP {res.status_code}): {res.text}")

            data = res.json()
            out_text = data.get("text", "")
            tokens = data.get("meta", {}).get("tokens", {}).get("output_tokens", 0)
            latency = (time.time() - start_time) * 1000

            return ProviderResponse(
                content=out_text,
                provider="cohere",
                model=model_name,
                latency_ms=round(latency, 1),
                estimated_tokens=tokens
            )

    async def stream(self, context_package: ContextPackage, api_key: str, model: Optional[str] = None) -> AsyncGenerator[str, None]:
        yield "[Cohere Stream] Command stream ready."

    def normalize_error(self, error: Exception) -> NormalizedError:
        err_msg = str(error)
        err_lower = err_msg.lower()
        if "rate" in err_lower or "429" in err_msg:
            return NormalizedError(code="RATE_LIMIT", message="Cohere rate limit reached", retry_after_seconds=5, is_retryable=True)
        if "404" in err_msg or "not found" in err_lower:
            return NormalizedError(code="BAD_REQUEST", message=err_msg, is_retryable=False)
        if "401" in err_msg or "auth" in err_lower:
            return NormalizedError(code="AUTHENTICATION_ERROR", message=err_msg, is_retryable=False)
        return NormalizedError(code="UNKNOWN", message=err_msg, is_retryable=False)

    def get_health(self, api_key: str) -> ProviderHealth:
        start_time = time.time()
        is_valid = self.validate_credentials(api_key)
        if not is_valid:
            return ProviderHealth(provider="cohere", is_healthy=False, status_message="Credential Validation Failed", discovered_models=self.DEFAULT_MODELS)

        discovered = self.discover_models(api_key)
        latency = (time.time() - start_time) * 1000
        return ProviderHealth(
            provider="cohere",
            is_healthy=True,
            status_message=f"HEALTHY ({len(discovered)} models discovered)",
            latency_ms=round(latency, 1),
            discovered_models=discovered
        )

    def estimate_usage(self, context_package: ContextPackage) -> int:
        return len(context_package.current_message.split()) * 4
