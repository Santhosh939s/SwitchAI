import time
from typing import List, AsyncGenerator, Optional
import httpx
from app.adapters.base import ProviderAdapter, ProviderResponse, NormalizedError, ProviderHealth
from app.schemas.context import ContextPackage

class GeminiAdapter(ProviderAdapter):
    DEFAULT_MODELS = ["gemini-3.6-flash", "gemini-3.5-flash-lite", "gemini-flash-latest"]

    def validate_credentials(self, api_key: str) -> bool:
        if not api_key or len(api_key) < 10:
            return False
        if api_key.startswith("mock_"):
            return True
        try:
            with httpx.Client(timeout=5.0) as client:
                res = client.get(
                    f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
                )
                if res.status_code in (400, 401, 403):
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
                res = client.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}")
                if res.status_code == 200:
                    data = res.json()
                    discovered = []
                    excluded_keywords = [
                        "-tts", "-transcribe", "-image", "computer-use",
                        "deep-research", "lyria", "nano-banana", "-customtools"
                    ]
                    for m in data.get("models", []):
                        name = m.get("name", "").replace("models/", "")
                        methods = m.get("supportedGenerationMethods", [])
                        
                        # Filter out non-chat / specialty models
                        if any(k in name for k in excluded_keywords):
                            continue

                        # Keep only models matching -flash or -pro that support generateContent
                        if "generateContent" in methods and ("-flash" in name or "-pro" in name or "latest" in name):
                            discovered.append(name)

                    if discovered:
                        sorted_models = sorted(discovered)
                        priority_order = ["gemini-3.6-flash", "gemini-3.5-flash-lite", "gemini-flash-latest", "gemini-1.5-flash"]
                        top_models = [m for m in priority_order if m in sorted_models]
                        other_models = [m for m in sorted_models if m not in top_models]
                        return top_models + other_models
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
        web_results = context_package.metadata.get("web_results", [])
        if web_results:
            web_lines = [f"- [{r.get('title')}]({r.get('url')}): {r.get('snippet')}" for r in web_results]
            parts.append("Live Web Search Results:\n" + "\n".join(web_lines))
        parts.append("\n[System Instruction: Be concise, clear, and token-efficient. Provide direct answers without unnecessary fluff or huge walls of text unless the user explicitly asks to 'explain in detail' or 'explain briefly'.]")
        return "\n".join(parts)

    def _sanitize_model_name(self, model_name: Optional[str]) -> str:
        if not model_name:
            return "gemini-3.6-flash"
        clean = model_name.replace("models/", "").strip()
        if clean.startswith("gemini-") or clean.startswith("gemma-"):
            return clean
        if "pro" in clean:
            return "gemini-3.6-flash"
        return "gemini-3.6-flash"

    def generate(self, context_package: ContextPackage, api_key: str, model: Optional[str] = None) -> ProviderResponse:
        model_name = self._sanitize_model_name(model or "gemini-3.6-flash")

        if not api_key:
            raise ValueError("Gemini API key is missing. Please connect your Gemini API key in Settings -> Providers.")

        context_str = self._build_prompt_context(context_package)
        start_time = time.time()

        if api_key.startswith("mock_"):
            return ProviderResponse(
                content=f"Hello! I am Google Gemini ({model_name}). I am active with your unified shared memory.",
                provider="gemini",
                model=model_name,
                latency_ms=95.0,
                estimated_tokens=140
            )

        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        contents = []

        if context_str:
            contents.append({"role": "user", "parts": [{"text": f"System Context Instructions: {context_str}"}]})
            contents.append({"role": "model", "parts": [{"text": "Understood. I will follow these shared memory instructions."}]})

        for m in context_package.recent_messages[-6:]:
            role = "user" if m.role == "user" else "model"
            contents.append({"role": role, "parts": [{"text": m.content}]})

        contents.append({"role": "user", "parts": [{"text": context_package.current_message}]})

        with httpx.Client(timeout=25.0) as client:
            res = client.post(
                endpoint,
                headers={"Content-Type": "application/json"},
                json={"contents": contents}
            )

            if res.status_code == 404:
                raise ValueError(f"Selected Gemini model '{model_name}' is unavailable or not supported for v1beta API. Please select another model.")

            if res.status_code != 200:
                raise RuntimeError(f"Gemini API Error (HTTP {res.status_code}): {res.text}")

            data = res.json()
            try:
                out_text = data["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError):
                out_text = "Received response from Gemini without text output."

            tokens = data.get("usageMetadata", {}).get("totalTokenCount", 0)
            latency = (time.time() - start_time) * 1000

            return ProviderResponse(
                content=out_text,
                provider="gemini",
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
        if "quota" in err_lower or "429" in err_msg or "resource_exhausted" in err_lower:
            return NormalizedError(code="RATE_LIMIT", message="Gemini quota exceeded or rate limited", retry_after_seconds=10, is_retryable=True)
        if "404" in err_msg or "unavailable" in err_lower or "not found" in err_lower:
            return NormalizedError(code="BAD_REQUEST", message=err_msg, is_retryable=False)
        if "timeout" in err_lower or "504" in err_msg or "502" in err_msg:
            return NormalizedError(code="TIMEOUT", message="Gemini request timed out", retry_after_seconds=2, is_retryable=True)
        if "500" in err_msg or "503" in err_msg:
            return NormalizedError(code="SERVICE_UNAVAILABLE", message="Gemini service temporarily unavailable", retry_after_seconds=3, is_retryable=True)
        if "key" in err_lower or "400" in err_msg or "403" in err_msg or "401" in err_msg:
            return NormalizedError(code="AUTHENTICATION_ERROR", message=err_msg, is_retryable=False)
        return NormalizedError(code="UNKNOWN", message=err_msg, is_retryable=False)

    def get_health(self, api_key: str) -> ProviderHealth:
        start_time = time.time()
        is_valid = self.validate_credentials(api_key)
        if not is_valid:
            return ProviderHealth(provider="gemini", is_healthy=False, status_message="Credential Validation Failed", discovered_models=self.DEFAULT_MODELS)

        discovered = self.discover_models(api_key)
        latency = (time.time() - start_time) * 1000
        return ProviderHealth(
            provider="gemini",
            is_healthy=True,
            status_message=f"HEALTHY ({len(discovered)} models discovered)",
            latency_ms=round(latency, 1),
            discovered_models=discovered
        )

    def estimate_usage(self, context_package: ContextPackage) -> int:
        return len(context_package.current_message.split()) * 4
