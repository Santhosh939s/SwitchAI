import time
from typing import List, AsyncGenerator, Optional
from app.adapters.base import ProviderAdapter, ProviderResponse, NormalizedError, ProviderHealth
from app.schemas.context import ContextPackage

class RagAdapter(ProviderAdapter):
    def validate_credentials(self, api_key: str) -> bool:
        return True

    def list_models(self) -> List[str]:
        return ["local-knowledge-base"]

    def discover_models(self, api_key: str) -> List[str]:
        return self.list_models()

    def generate(self, context_package: ContextPackage, api_key: str, model: Optional[str] = None) -> ProviderResponse:
        from app.services.rag import query_rag_engine
        # Generate response using local RAG engine
        res_text = query_rag_engine(None, context_package.conversation_id, context_package.current_message, context_package)
        return ProviderResponse(
            content=res_text,
            provider="rag_engine",
            model="local-knowledge-base",
            latency_ms=15.0,
            estimated_tokens=120
        )

    async def stream(self, context_package: ContextPackage, api_key: str, model: Optional[str] = None) -> AsyncGenerator[str, None]:
        yield "[RAG Engine Stream] Active."

    def normalize_error(self, error: Exception) -> NormalizedError:
        return NormalizedError(code="UNKNOWN", message=str(error), is_retryable=False)

    def get_health(self, api_key: str) -> ProviderHealth:
        return ProviderHealth(provider="rag_engine", is_healthy=True, status_message="HEALTHY", discovered_models=self.list_models())

    def estimate_usage(self, context_package: ContextPackage) -> int:
        return len(context_package.current_message.split()) * 4
