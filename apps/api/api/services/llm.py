from __future__ import annotations

import re
from typing import Any

import httpx

from packages.db.llm_key import decrypt_key


class LLMNotConfiguredError(Exception):
    pass


class LLMCallError(Exception):
    pass


def _provider_settings(org_settings: dict[str, Any] | None) -> tuple[str, str, str, str | None]:
    settings = org_settings or {}
    provider = str(settings.get("llm_provider") or "").lower()
    model = str(settings.get("llm_model") or "")
    encrypted_key = settings.get("llm_api_key_enc")
    base_url = settings.get("llm_base_url")

    if not encrypted_key and settings.get("anthropic_api_key_encrypted"):
        provider = provider or "anthropic"
        encrypted_key = settings.get("anthropic_api_key_encrypted")

    if not provider or not encrypted_key:
        raise LLMNotConfiguredError("Configure an AI model in Settings to use this feature")

    try:
        api_key = decrypt_key(str(encrypted_key))
    except Exception as exc:
        raise LLMNotConfiguredError("Stored LLM API key could not be decrypted") from exc

    if not api_key:
        raise LLMNotConfiguredError("Configure an AI model in Settings to use this feature")
    return provider, model, api_key, str(base_url).rstrip("/") if base_url else None


def _snippet(response: httpx.Response) -> str:
    text = response.text.replace("\n", " ").strip()
    return text[:500]


def _openai_max_tokens_param(model: str, max_tokens: int) -> dict[str, int]:
    """
    Newer OpenAI reasoning models use max_completion_tokens instead of max_tokens.
    Keep custom/OpenAI-compatible defaults backward-compatible unless the model ID
    clearly belongs to the newer OpenAI family.
    """
    model_lower = (model or "").lower()
    if re.match(r"^o\d", model_lower):
        return {"max_completion_tokens": max_tokens}
    if re.match(r"^gpt-(4\.5|[5-9])", model_lower):
        return {"max_completion_tokens": max_tokens}
    return {"max_tokens": max_tokens}


def _build_openai_messages(model: str, system_prompt: str, user_prompt: str) -> list[dict[str, str]]:
    model_lower = (model or "").lower()
    if re.match(r"^o\d", model_lower):
        return [{"role": "user", "content": f"{system_prompt}\n\n{user_prompt}"}]
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


async def _post_json(url: str, *, headers: dict[str, str], json: dict[str, Any], params: dict[str, str] | None = None) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, headers=headers, json=json, params=params)
    if response.status_code < 200 or response.status_code >= 300:
        raise LLMCallError(f"Provider returned {response.status_code}: {_snippet(response)}")
    try:
        payload = response.json()
    except ValueError as exc:
        raise LLMCallError("Provider returned invalid JSON") from exc
    if not isinstance(payload, dict):
        raise LLMCallError("Provider returned an unexpected response")
    return payload


async def call_llm(
    org_settings: dict[str, Any] | None,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 1024,
) -> str:
    provider, model, api_key, base_url = _provider_settings(org_settings)

    if provider == "anthropic":
        payload = await _post_json(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={
                "model": model or "claude-sonnet-4-5",
                "max_tokens": max_tokens,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_prompt}],
            },
        )
        content = payload.get("content")
        if isinstance(content, list) and content and isinstance(content[0], dict):
            text = content[0].get("text")
            if isinstance(text, str) and text.strip():
                return text.strip()

    if provider in {"openai", "custom"}:
        if provider == "custom":
            if not base_url:
                raise LLMNotConfiguredError("Custom LLM base URL is missing")
            url = f"{base_url}/chat/completions"
        else:
            url = f"{base_url}/chat/completions" if base_url else "https://api.openai.com/v1/chat/completions"
        payload = await _post_json(
            url,
            headers={"Authorization": f"Bearer {api_key}", "content-type": "application/json"},
            json={
                "model": model or "gpt-4o-mini",
                **_openai_max_tokens_param(model or "gpt-4o-mini", max_tokens),
                "messages": _build_openai_messages(model or "gpt-4o-mini", system_prompt, user_prompt),
            },
        )
        choices = payload.get("choices")
        if isinstance(choices, list) and choices and isinstance(choices[0], dict):
            message = choices[0].get("message")
            if isinstance(message, dict) and isinstance(message.get("content"), str):
                return str(message["content"]).strip()

    if provider == "gemini":
        gemini_model = model or "gemini-2.0-flash"
        payload = await _post_json(
            f"https://generativelanguage.googleapis.com/v1beta/models/{gemini_model}:generateContent",
            headers={"content-type": "application/json"},
            params={"key": api_key},
            json={
                "contents": [{"parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}]}],
                "generationConfig": {"maxOutputTokens": max_tokens},
            },
        )
        candidates = payload.get("candidates")
        if isinstance(candidates, list) and candidates and isinstance(candidates[0], dict):
            content = candidates[0].get("content")
            parts = content.get("parts") if isinstance(content, dict) else None
            if isinstance(parts, list) and parts and isinstance(parts[0], dict):
                text = parts[0].get("text")
                if isinstance(text, str) and text.strip():
                    return text.strip()

    if provider not in {"anthropic", "openai", "gemini", "custom"}:
        raise LLMNotConfiguredError(f"Unsupported LLM provider: {provider}")
    raise LLMCallError("Provider returned an empty text response")
