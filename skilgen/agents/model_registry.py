from __future__ import annotations

import os

from skilgen.core.models import ModelSettings, SkilgenConfig


DEFAULT_KEY_ENV = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GOOGLE_API_KEY",
    "google": "GOOGLE_API_KEY",
    "google_genai": "GOOGLE_API_KEY",
    "huggingface": "HUGGINGFACEHUB_API_TOKEN",
    "hugging_face": "HUGGINGFACEHUB_API_TOKEN",
    "hf": "HUGGINGFACEHUB_API_TOKEN",
    "groq": "GROQ_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
}

SUPPORTED_PROVIDERS = tuple(sorted({"openai", "anthropic", "google_genai", "huggingface", "groq", "openrouter"}))


def normalize_provider(provider: str | None) -> str:
    raw = (provider or "openai").strip().lower()
    aliases = {
        "openai": "openai",
        "anthropic": "anthropic",
        "gemini": "google_genai",
        "google": "google_genai",
        "google_genai": "google_genai",
        "huggingface": "huggingface",
        "hugging_face": "huggingface",
        "hf": "huggingface",
    }
    return aliases.get(raw, raw)


def resolve_model_settings(config: SkilgenConfig) -> ModelSettings:
    provider = normalize_provider(config.model_provider)
    api_key_env = config.api_key_env or DEFAULT_KEY_ENV.get(provider, "MODEL_API_KEY")
    return ModelSettings(
        provider=provider,
        model=config.model,
        api_key_env=api_key_env,
        api_key_present=bool(os.getenv(api_key_env)),
        temperature=config.model_temperature,
        max_tokens=config.model_max_tokens,
        retry_attempts=config.model_retry_attempts,
        retry_base_delay_seconds=config.model_retry_base_delay_seconds,
    )


def provider_supported(provider: str | None) -> bool:
    return normalize_provider(provider) in SUPPORTED_PROVIDERS
