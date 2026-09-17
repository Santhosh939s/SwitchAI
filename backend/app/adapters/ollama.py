import json
import httpx
from typing import List, AsyncGenerator, Optional
import time

from app.adapters.base import ProviderAdapter, ProviderResponse, NormalizedError, ProviderHealth
from app.schemas.context import ContextPackage

class OllamaAdapter(ProviderAdapter):
    
    def validate_credentials(self, api_key: str) -> bool:
        # For Ollama, the api_key field stores the base URL (e.g., http://localhost:11434)
        base_url = api_key.strip().rstrip("/")
        if not base_url:
            return False
            
        try:
            with httpx.Client(timeout=5.0) as client:
                res = client.get(f"{base_url}/api/version")
                return res.status_code == 200
        except Exception:
            return False

    def list_models(self) -> List[str]:
        # Fallback list if discovery fails
        return ["llama3", "mistral", "phi3"]

    def discover_models(self, api_key: str) -> List[str]:
        base_url = api_key.strip().rstrip("/")
        try:
            with httpx.Client(timeout=5.0) as client:
                res = client.get(f"{base_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    models = [m.get("name") for m in data.get("models", [])]
                    return sorted(models)
                return self.list_models()
        except Exception:
            return self.list_models()

    def generate(self, context_package: ContextPackage, api_key: str, model: Optional[str] = None) -> ProviderResponse:
        base_url = api_key.strip().rstrip("/")
        selected_model = model or "llama3"
        
        messages = []
        if context_package.system_instruction:
            messages.append({"role": "system", "content": context_package.system_instruction})
            
        # Append memories to context
        if context_package.memories:
            mem_text = "\n".join([f"- {m.category.upper()}: {m.value}" for m in context_package.memories])
            messages.append({"role": "system", "content": f"User Shared Context:\n{mem_text}"})
            
        if context_package.web_search_context:
            messages.append({"role": "system", "content": f"Live Web Search Facts:\n{context_package.web_search_context}"})
            
        for msg in context_package.recent_messages:
            messages.append({"role": msg.role, "content": msg.content})

        start_time = time.time()
        
        try:
            with httpx.Client(timeout=60.0) as client:
                payload = {
                    "model": selected_model,
                    "messages": messages,
                    "stream": False
                }
                res = client.post(f"{base_url}/api/chat", json=payload)
                res.raise_for_status()
                data = res.json()
                
                content = data.get("message", {}).get("content", "")
                eval_count = data.get("eval_count", 0)
                prompt_eval_count = data.get("prompt_eval_count", 0)
                total_tokens = eval_count + prompt_eval_count
                latency_ms = (time.time() - start_time) * 1000
                
                return ProviderResponse(
                    content=content,
                    provider="ollama",
                    model=selected_model,
                    latency_ms=latency_ms,
                    estimated_tokens=total_tokens,
                    raw_response=data
                )
        except Exception as e:
            raise Exception(f"Ollama error: {str(e)}")

    def stream(self, context_package: ContextPackage, api_key: str, model: Optional[str] = None) -> AsyncGenerator[str, None]:
        # Streaming implementation for Ollama API
        base_url = api_key.strip().rstrip("/")
        selected_model = model or "llama3"
        
        messages = []
        if context_package.system_instruction:
            messages.append({"role": "system", "content": context_package.system_instruction})
            
        if context_package.memories:
            mem_text = "\n".join([f"- {m.category.upper()}: {m.value}" for m in context_package.memories])
            messages.append({"role": "system", "content": f"User Shared Context:\n{mem_text}"})
            
        if context_package.web_search_context:
            messages.append({"role": "system", "content": f"Live Web Search Facts:\n{context_package.web_search_context}"})
            
        for msg in context_package.recent_messages:
            messages.append({"role": msg.role, "content": msg.content})

        async def _stream():
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    payload = {
                        "model": selected_model,
                        "messages": messages,
                        "stream": True
                    }
                    async with client.stream("POST", f"{base_url}/api/chat", json=payload) as response:
                        response.raise_for_status()
                        async for chunk in response.aiter_lines():
                            if chunk:
                                try:
                                    data = json.loads(chunk)
                                    msg = data.get("message", {})
                                    content = msg.get("content", "")
                                    if content:
                                        yield content
                                except json.JSONDecodeError:
                                    continue
            except Exception as e:
                yield f"\n[Ollama Connection Error: {str(e)}]"
                
        return _stream()

    def normalize_error(self, error: Exception) -> NormalizedError:
        msg = str(error).lower()
        if "timeout" in msg:
            return NormalizedError(code="TIMEOUT", message="Ollama request timed out.", is_retryable=True)
        if "connection" in msg or "connect" in msg:
            return NormalizedError(code="SERVICE_UNAVAILABLE", message="Could not connect to Ollama server.", is_retryable=True)
        return NormalizedError(code="UNKNOWN", message=f"Ollama error: {str(error)}", is_retryable=False)

    def get_health(self, api_key: str) -> ProviderHealth:
        start_time = time.time()
        try:
            base_url = api_key.strip().rstrip("/")
            with httpx.Client(timeout=5.0) as client:
                res = client.get(f"{base_url}/api/version")
                res.raise_for_status()
                
            # Try to get models
            models = self.discover_models(api_key)
            
            latency = (time.time() - start_time) * 1000
            return ProviderHealth(
                provider="ollama",
                is_healthy=True,
                status_message="Ollama is reachable.",
                latency_ms=latency,
                discovered_models=models
            )
        except Exception as e:
            return ProviderHealth(
                provider="ollama",
                is_healthy=False,
                status_message=f"Connection failed: {str(e)}",
                latency_ms=None,
                discovered_models=[]
            )

    def estimate_usage(self, context_package: ContextPackage) -> int:
        count = 0
        if context_package.system_instruction:
            count += len(context_package.system_instruction.split())
        for msg in context_package.recent_messages:
            count += len(msg.content.split())
        if context_package.current_message:
            count += len(context_package.current_message.split())
        # rough estimate: 1.3 tokens per word
        return int(count * 1.3)

