from __future__ import annotations

import asyncio

import pytest

from apps.api.api.services.llm import LLMNotConfiguredError, _build_openai_messages, _openai_max_tokens_param, call_llm
from packages.db.llm_key import decrypt_key, encrypt_key, key_hint


def test_save_openai_config() -> None:
    encrypted = encrypt_key("sk-test-openai")
    assert decrypt_key(encrypted) == "sk-test-openai"
    assert key_hint("sk-test-openai") == "...enai"


def test_save_anthropic_config() -> None:
    encrypted = encrypt_key("sk-ant-test")
    assert decrypt_key(encrypted) == "sk-ant-test"


def test_save_gemini_config() -> None:
    encrypted = encrypt_key("AIza-test")
    assert decrypt_key(encrypted) == "AIza-test"


def test_save_custom_config() -> None:
    encrypted = encrypt_key("custom-key")
    assert decrypt_key(encrypted) == "custom-key"


def test_call_llm_not_configured() -> None:
    with pytest.raises(LLMNotConfiguredError):
        asyncio.run(call_llm({}, "system", "user"))


def test_openai_max_tokens_o1() -> None:
    params = _openai_max_tokens_param("o1", 1024)
    assert params == {"max_completion_tokens": 1024}


def test_openai_max_tokens_o3_mini() -> None:
    params = _openai_max_tokens_param("o3-mini", 1024)
    assert params == {"max_completion_tokens": 1024}


def test_openai_max_tokens_gpt4o() -> None:
    params = _openai_max_tokens_param("gpt-4o", 1024)
    assert params == {"max_tokens": 1024}


def test_openai_max_tokens_gpt5() -> None:
    params = _openai_max_tokens_param("gpt-5", 1024)
    assert params == {"max_completion_tokens": 1024}


def test_build_messages_o_series_no_system_role() -> None:
    msgs = _build_openai_messages("o1-mini", "system text", "user text")
    assert all(message["role"] != "system" for message in msgs)
    assert "system text" in msgs[0]["content"]


def test_build_messages_gpt4_has_system_role() -> None:
    msgs = _build_openai_messages("gpt-4o", "system text", "user text")
    assert msgs[0]["role"] == "system"


class FakeResponse:
    status_code = 200
    text = "{}"

    def __init__(self, payload):
        self.payload = payload

    def json(self):
        return self.payload


class FakeClient:
    calls: list[str] = []

    def __init__(self, timeout: float):
        self.timeout = timeout

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    async def post(self, url, **kwargs):
        self.calls.append(str(url))
        if "anthropic" in str(url):
            return FakeResponse({"content": [{"text": "OK"}]})
        if "googleapis" in str(url):
            return FakeResponse({"candidates": [{"content": {"parts": [{"text": "OK"}]}}]})
        return FakeResponse({"choices": [{"message": {"content": "OK"}}]})


def _settings(provider: str, base_url: str | None = None) -> dict[str, str]:
    settings = {"llm_provider": provider, "llm_model": "model", "llm_api_key_enc": encrypt_key("key")}
    if base_url:
        settings["llm_base_url"] = base_url
    return settings


def test_call_llm_routes_anthropic(monkeypatch) -> None:
    FakeClient.calls = []
    monkeypatch.setattr("apps.api.api.services.llm.httpx.AsyncClient", FakeClient)
    assert asyncio.run(call_llm(_settings("anthropic"), "system", "user")) == "OK"
    assert "https://api.anthropic.com/v1/messages" in FakeClient.calls


def test_call_llm_routes_openai(monkeypatch) -> None:
    FakeClient.calls = []
    monkeypatch.setattr("apps.api.api.services.llm.httpx.AsyncClient", FakeClient)
    assert asyncio.run(call_llm(_settings("openai"), "system", "user")) == "OK"
    assert "https://api.openai.com/v1/chat/completions" in FakeClient.calls


def test_call_llm_routes_gemini(monkeypatch) -> None:
    FakeClient.calls = []
    monkeypatch.setattr("apps.api.api.services.llm.httpx.AsyncClient", FakeClient)
    assert asyncio.run(call_llm(_settings("gemini"), "system", "user")) == "OK"
    assert FakeClient.calls[0].startswith("https://generativelanguage.googleapis.com")


def test_call_llm_routes_custom(monkeypatch) -> None:
    FakeClient.calls = []
    monkeypatch.setattr("apps.api.api.services.llm.httpx.AsyncClient", FakeClient)
    assert asyncio.run(call_llm(_settings("custom", "https://llm.example/v1"), "system", "user")) == "OK"
    assert FakeClient.calls == ["https://llm.example/v1/chat/completions"]
