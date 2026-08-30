from abc import ABC, abstractmethod
from typing import List, AsyncGenerator, Dict, Any, Optional
from pydantic import BaseModel
from app.schemas.context import ContextPackage

class ProviderResponse(BaseModel):
    content: str
    provider: str
    model: str
    latency_ms: float
    estimated_tokens: int
    raw_response: Optional[Dict[str, Any]] = None

class NormalizedError(BaseModel):
    code: str  # AUTHENTICATION_ERROR, RATE_LIMIT, TIMEOUT, SERVICE_UNAVAILABLE, BAD_REQUEST, CONTEXT_TOO_LARGE, UNKNOWN
    message: str
    retry_after_seconds: Optional[int] = None
    is_retryable: bool

class ProviderHealth(BaseModel):
    provider: str
    is_healthy: bool
    status_message: str
    latency_ms: Optional[float] = None
    discovered_models: List[str] = []

class ProviderAdapter(ABC):
    @abstractmethod
    def validate_credentials(self, api_key: str) -> bool:
        pass

    @abstractmethod
    def list_models(self) -> List[str]:
        pass

    @abstractmethod
    def discover_models(self, api_key: str) -> List[str]:
        pass

    @abstractmethod
    def generate(self, context_package: ContextPackage, api_key: str, model: Optional[str] = None) -> ProviderResponse:
        pass

    @abstractmethod
    def stream(self, context_package: ContextPackage, api_key: str, model: Optional[str] = None) -> AsyncGenerator[str, None]:
        pass

    @abstractmethod
    def normalize_error(self, error: Exception) -> NormalizedError:
        pass

    @abstractmethod
    def get_health(self, api_key: str) -> ProviderHealth:
        pass

    @abstractmethod
    def estimate_usage(self, context_package: ContextPackage) -> int:
        pass
