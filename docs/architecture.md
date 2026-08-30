# SwitchAI Technical Architecture Specification

## Overview

SwitchAI creates a provider-independent AI workspace with a unified shared memory system across Anthropic, Google Gemini, and OpenAI.

```
                  +--------------------------------+
                  |         SHARED MEMORY          |
                  | Goals • Facts • Decisions      |
                  | Constraints • Summary          |
                  +---------------+----------------+
                                  |
                        [ ContextPackage ]
                                  |
       +--------------------------+--------------------------+
       |                          |                          |
+------v-------+           +------v-------+           +------v-------+
|  Anthropic   |           |    Gemini    |           |    OpenAI    |
|   Adapter    |           |   Adapter    |           |   Adapter    |
+--------------+           +--------------+           +--------------+
```

## Security & Credential Isolation

- **Zero Client-Side Key Storage:** Raw provider API keys are never saved in `localStorage`, cookies, or JavaScript state.
- **Server-Side Encryption:** Provider credentials are encrypted at rest using 32-byte Fernet symmetric encryption (`ENCRYPTION_KEY`).
- **Response Sanitization:** Provider credentials are stripped from API response payloads (`api_key` and `encrypted_api_key` are omitted).
- **Environment Isolation:** Secrets loaded strictly from environment variables (`.env`).

## Provider Adapter Abstraction (`ProviderAdapter`)

All AI model interactions pass through abstract `ProviderAdapter` interfaces:
- `validate_credentials(api_key: str) -> bool`
- `list_models() -> List[str]`
- `generate(context_package: ContextPackage, api_key: str, model: str) -> ProviderResponse`
- `stream(context_package: ContextPackage, api_key: str, model: str) -> AsyncGenerator`
- `normalize_error(error: Exception) -> NormalizedError`
- `get_health(api_key: str) -> ProviderHealth`

## Context Package & Context Passport

When a request is initiated or a provider switch occurs:
1. `build_context_package()` retrieves pinned memories and keyword-matched facts.
2. `build_context_passport()` formats goals, facts, decisions, constraints, and open questions into a visual structure.
3. The target adapter formats `ContextPackage` into model-specific system prompts.

## Resilient Automatic Fallback & Circuit Breaker

- **Circuit Breaker:** Tracks provider failure rates in `CIRCUIT_BREAKER_FAILURES` with a 30-second cooldown period.
- **Error Normalization:** Standardizes errors into `RATE_LIMIT`, `TIMEOUT`, `SERVICE_UNAVAILABLE`, `AUTHENTICATION_ERROR`, `BAD_REQUEST`, `CONTEXT_TOO_LARGE`, or `UNKNOWN`.
- **Fallback Chain:** Automatically reroutes retryable errors (`RATE_LIMIT`, `TIMEOUT`, `SERVICE_UNAVAILABLE`) to secondary healthy providers while retaining thread state.

## Tech Stack
- **Backend:** Python 3.8+, FastAPI, SQLAlchemy, Pydantic v2, SQLite, Pytest
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS (Dark Theme), Lucide Icons
- **Harness:** Built exclusively with **LatentCode**
- **Skills:** `api-integration`, `frontend-ui-dark-ts`, `api-rate-limiting-helper`
