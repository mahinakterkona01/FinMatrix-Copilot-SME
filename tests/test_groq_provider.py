import sys
from types import SimpleNamespace
from src import llm_client

def test_groq_provider_uses_chat_completions(monkeypatch):
    monkeypatch.setenv("FINMATRIX_LLM_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_API_KEY", "test-key-only")
    monkeypatch.delenv("FINMATRIX_ENABLE_OPENAI", raising=False)

    captured = {}
    class FakeClient:
        def __init__(self, **kwargs):
            captured["client"] = kwargs
            self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))
        def create(self, **kwargs):
            captured["request"] = kwargs
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content="Test response"))]
            )

    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(OpenAI=FakeClient))
    assert llm_client.is_enabled()
    assert llm_client._generate_text("system", "question", 50, 5) == "Test response"
    assert captured["client"]["base_url"] == "https://api.groq.com/openai/v1"
    assert captured["request"]["model"] == "openai/gpt-oss-20b"
