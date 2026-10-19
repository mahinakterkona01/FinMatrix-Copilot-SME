import sys
import pytest
import requests
from types import SimpleNamespace

from src import llm_client


def test_llm_disabled_by_default(monkeypatch):
    monkeypatch.delenv("FINMATRIX_ENABLE_OPENAI", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert llm_client.is_enabled() is False
    assert llm_client.rewrite_answer("hello", "existing answer") is None


def test_llm_requires_api_key_even_when_enabled(monkeypatch):
    monkeypatch.setenv("FINMATRIX_ENABLE_OPENAI", "true")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert llm_client.is_enabled() is False
    assert llm_client.rewrite_answer("hello", "existing answer") is None


def test_llm_requires_explicit_opt_in(monkeypatch):
    monkeypatch.setenv("FINMATRIX_ENABLE_OPENAI", "false")
    monkeypatch.setenv("OPENAI_API_KEY", "test-placeholder-not-a-real-key")
    assert llm_client.is_enabled() is False
    assert llm_client.rewrite_answer("hello", "existing answer") is None


def test_llm_enabled_only_with_flag_and_key(monkeypatch):
    monkeypatch.setenv("FINMATRIX_ENABLE_OPENAI", "true")
    monkeypatch.setenv("OPENAI_API_KEY", "test-placeholder-not-a-real-key")
    assert llm_client.is_enabled() is True


def install_fake_openai(monkeypatch, create_response):
    captured = {}

    class FakeOpenAI:
        def __init__(self, **kwargs):
            captured["client_kwargs"] = kwargs
            self.responses = SimpleNamespace(create=create_response)

    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(OpenAI=FakeOpenAI))
    return captured


def test_rewrite_answer_returns_mocked_output_and_disables_storage(monkeypatch):
    monkeypatch.setenv("FINMATRIX_ENABLE_OPENAI", "true")
    monkeypatch.setenv("OPENAI_API_KEY", "test-placeholder-not-a-real-key")
    monkeypatch.setenv("OPENAI_MODEL", "mock-model")

    captured = {}

    def fake_create(**kwargs):
        captured["request"] = kwargs
        return SimpleNamespace(output_text="Clear rewritten answer.")

    client_capture = install_fake_openai(monkeypatch, fake_create)
    result = llm_client.rewrite_answer("Explain cash flow", "Existing answer.")

    assert result == "Clear rewritten answer."
    assert captured["request"]["store"] is False
    assert captured["request"]["model"] == "mock-model"
    assert captured["request"]["max_output_tokens"] == 350
    assert "Existing answer." in captured["request"]["input"]
    assert client_capture["client_kwargs"]["timeout"] == 20.0
    assert client_capture["client_kwargs"]["max_retries"] == 0


def test_rewrite_answer_returns_none_on_api_error(monkeypatch):
    monkeypatch.setenv("FINMATRIX_ENABLE_OPENAI", "true")
    monkeypatch.setenv("OPENAI_API_KEY", "test-placeholder-not-a-real-key")

    def fake_create(**kwargs):
        raise RuntimeError("Simulated API failure")

    install_fake_openai(monkeypatch, fake_create)
    assert llm_client.rewrite_answer("question", "authoritative answer") is None


def test_rewrite_answer_returns_none_for_empty_output(monkeypatch):
    monkeypatch.setenv("FINMATRIX_ENABLE_OPENAI", "true")
    monkeypatch.setenv("OPENAI_API_KEY", "test-placeholder-not-a-real-key")

    install_fake_openai(
        monkeypatch,
        lambda **kwargs: SimpleNamespace(output_text="  "),
    )
    assert llm_client.rewrite_answer("question", "authoritative answer") is None



def test_safe_rewrite_accepts_preserved_financial_content():
    original = (
        "Cash inflow is BDT 12,500. Warning: this is an estimate. "
        "Intent: forecast. Confidence: medium"
    )
    rewritten = (
        "Estimated cash inflow is BDT 12,500. Warning: this is an estimate. "
        "Intent: forecast. Confidence: medium"
    )
    assert llm_client.is_safe_rewrite(original, rewritten) is True


def test_safe_rewrite_rejects_changed_numbers():
    assert llm_client.is_safe_rewrite(
        "Expected inflow: BDT 12,500",
        "Expected inflow: BDT 15,200",
    ) is False


def test_safe_rewrite_rejects_removed_currency_code():
    assert llm_client.is_safe_rewrite(
        "Expected inflow: BDT 12,500",
        "Expected inflow: 12,500",
    ) is False


def test_safe_rewrite_rejects_removed_warning():
    assert llm_client.is_safe_rewrite(
        "Warning: this estimate is uncertain.",
        "This estimate is available.",
    ) is False


def test_safe_rewrite_rejects_removed_metadata():
    assert llm_client.is_safe_rewrite(
        "Forecast result. Intent: forecast. Confidence: medium",
        "Forecast result.",
    ) is False



def test_rewrite_answer_rejects_changed_financial_amount(monkeypatch):
    monkeypatch.setenv("FINMATRIX_ENABLE_OPENAI", "true")
    monkeypatch.setenv("OPENAI_API_KEY", "test-placeholder-not-a-real-key")

    install_fake_openai(
        monkeypatch,
        lambda **kwargs: SimpleNamespace(
            output_text="Expected inflow: BDT 15,200"
        ),
    )

    result = llm_client.rewrite_answer(
        "Explain inflow",
        "Expected inflow: BDT 12,500",
    )
    assert result is None


def test_rewrite_answer_rejects_removed_warning(monkeypatch):
    monkeypatch.setenv("FINMATRIX_ENABLE_OPENAI", "true")
    monkeypatch.setenv("OPENAI_API_KEY", "test-placeholder-not-a-real-key")

    install_fake_openai(
        monkeypatch,
        lambda **kwargs: SimpleNamespace(
            output_text="This estimate is available."
        ),
    )

    result = llm_client.rewrite_answer(
        "Explain forecast",
        "Warning: this estimate is uncertain.",
    )
    assert result is None

def test_safe_rewrite_accepts_preserved_currency_symbols():
    symbols = ["$"] + [chr(code) for code in (0x20AC, 0x00A3, 0x00A5, 0x20B9, 0x09F3)]
    for symbol in symbols:
        original = f"Cash balance: {symbol}12,500"
        rewritten = f"Cash balance is {symbol}12,500"
        assert llm_client.is_safe_rewrite(original, rewritten) is True


def test_safe_rewrite_rejects_changed_currency_symbols():
    pairs = [
        ("$", chr(0x20AC)),
        (chr(0x09F3), "$"),
        (chr(0x00A3), chr(0x00A5)),
        (chr(0x20B9), chr(0x20AC)),
    ]
    for original_symbol, rewritten_symbol in pairs:
        original = f"Cash balance: {original_symbol}12,500"
        rewritten = f"Cash balance: {rewritten_symbol}12,500"
        assert llm_client.is_safe_rewrite(original, rewritten) is False


def test_safe_rewrite_rejects_added_or_removed_currency_symbols():
    assert llm_client.is_safe_rewrite(
        "Cash balance: 12,500",
        "Cash balance: $12,500",
    ) is False
    assert llm_client.is_safe_rewrite(
        "Cash balance: " + chr(0x20AC) + "12,500",
        "Cash balance: 12,500",
    ) is False



@pytest.fixture(autouse=True)
def _isolate_llm_provider_for_existing_tests(monkeypatch):
    """Isolate legacy OpenAI tests from the local .env provider choice."""
    monkeypatch.setenv("FINMATRIX_LLM_PROVIDER", "openai")


def _configure_ollama_for_test(monkeypatch):
    monkeypatch.setenv("FINMATRIX_LLM_PROVIDER", "ollama")
    monkeypatch.setenv("FINMATRIX_ENABLE_OLLAMA", "true")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.2:3b")


def test_ollama_answer_query_uses_local_chat_api(monkeypatch):
    _configure_ollama_for_test(monkeypatch)
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "message": {
                    "role": "assistant",
                    "content": "SME cash flow tracks money entering and leaving a business."
                }
            }

    def fake_post(url, **kwargs):
        captured["url"] = url
        captured.update(kwargs)
        return FakeResponse()

    monkeypatch.setattr(requests, "post", fake_post)

    answer = llm_client.answer_query("Explain SME cash flow.")

    assert answer
    assert "cash flow" in answer.lower()
    assert captured["url"] == "http://127.0.0.1:11434/api/chat"
    assert captured["json"]["model"] == "llama3.2:3b"
    assert captured["json"]["stream"] is False
    assert captured["json"]["messages"]


def test_ollama_rewrite_preserves_financial_safeguards(monkeypatch):
    _configure_ollama_for_test(monkeypatch)
    original = (
        "Estimated net cash flow is BDT 12,500. "
        "Warning: this is an estimate, not a guaranteed outcome."
    )

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "message": {
                    "role": "assistant",
                    "content": (
                        "Estimated net cash flow is BDT 12,500. "
                        "Warning: this remains an estimate, not a guaranteed outcome."
                    )
                }
            }

    def fake_post(url, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(requests, "post", fake_post)

    rewritten = llm_client.rewrite_answer(
        "Explain this result clearly.", original
    )

    assert rewritten is not None
    assert llm_client.is_safe_rewrite(original, rewritten)


def test_ollama_connection_failure_returns_fallback(monkeypatch):
    _configure_ollama_for_test(monkeypatch)

    def fake_post(url, **kwargs):
        raise requests.ConnectionError("mocked local service outage")

    monkeypatch.setattr(requests, "post", fake_post)

    assert llm_client.answer_query("Explain SME cash flow.") is None
    assert llm_client.rewrite_answer(
        "Explain this result.",
        "The original deterministic answer is BDT 12,500."
    ) is None


def test_ollama_rewrite_rejects_changed_financial_amount(monkeypatch):
    _configure_ollama_for_test(monkeypatch)

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "message": {
                    "role": "assistant",
                    "content": "Estimated net cash flow is BDT 15,200."
                }
            }

    monkeypatch.setattr(
        requests,
        "post",
        lambda url, **kwargs: FakeResponse(),
    )

    original = "Estimated net cash flow is BDT 12,500."
    assert llm_client.rewrite_answer(
        "Explain this result.", original
    ) is None
