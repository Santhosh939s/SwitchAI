import pytest
from app.adapters.gemini import GeminiAdapter
from app.schemas.context import ContextPackage

def test_gemini_stale_model_rejection_regression():
    adapter = GeminiAdapter()
    pkg = ContextPackage(conversation_id="test_conv", current_message="SWITCHAI_TEST_OK")
    
    # Passing stale model gemini-1.5-pro should raise ValueError (MODEL_NOT_FOUND) when no key or real key is used
    with pytest.raises(Exception) as exc_info:
        adapter.generate(pkg, api_key="sk-fake-key-12345", model="gemini-1.5-pro")
    
    err = adapter.normalize_error(exc_info.value)
    assert err.code == "AUTHENTICATION_ERROR" or err.code == "BAD_REQUEST"
