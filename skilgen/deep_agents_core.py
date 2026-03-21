from __future__ import annotations

import asyncio
import json
import os
import time
from typing import Callable

from pathlib import Path

from skilgen.agents.model_registry import provider_supported, resolve_model_settings
from skilgen.core.config import DEFAULT_CONFIG, load_config

try:
    from deepagents import create_deep_agent
    from langchain.chat_models import init_chat_model
except ImportError:  # pragma: no cover
    create_deep_agent = None
    init_chat_model = None


def runtime_label(enabled: bool) -> str:
    return "model_backed" if enabled else "local_fallback"


def _provider_docs_url(provider: str | None) -> str:
    mapping = {
        "openai": "https://platform.openai.com/docs",
        "anthropic": "https://docs.anthropic.com",
        "google_genai": "https://ai.google.dev/gemini-api/docs",
        "huggingface": "https://huggingface.co/docs",
        "groq": "https://console.groq.com/docs",
        "openrouter": "https://openrouter.ai/docs",
    }
    return mapping.get(provider or "openai", "https://platform.openai.com/docs")


def _provider_env_hint(provider: str | None, api_key_env: str | None) -> str:
    label = provider or "model provider"
    env_name = api_key_env or "MODEL_API_KEY"
    return f"Export `{env_name}` with valid {label} credentials before running model-backed commands."


def _classify_model_error(exc: Exception, provider: str | None, api_key_env: str | None) -> dict[str, object]:
    text = str(exc).lower()
    retryable = False
    category = "unknown_error"
    message = (
        f"Skilgen could not complete the model-backed request with provider `{provider or 'openai'}`. "
        f"See {_provider_docs_url(provider)} for provider setup and troubleshooting."
    )
    recommendations = [
        _provider_env_hint(provider, api_key_env),
        f"Confirm the configured model name is available for `{provider or 'openai'}`.",
    ]

    if any(marker in text for marker in ["missing api key", "api key", "unauthorized", "invalid api key", "authentication"]):
        category = "authentication_error"
        message = (
            f"Skilgen could not authenticate with provider `{provider or 'openai'}`. "
            f"Check `{api_key_env or 'MODEL_API_KEY'}` and verify that the credential is valid."
        )
        recommendations = [
            _provider_env_hint(provider, api_key_env),
            f"Verify the account or project behind `{provider or 'openai'}` still has access to the configured model.",
        ]
    elif any(marker in text for marker in ["rate limit", "429", "too many requests", "insufficient_quota", "quota"]):
        category = "rate_limit_error"
        retryable = True
        message = (
            f"Skilgen hit a temporary limit from provider `{provider or 'openai'}` while running a model-backed task."
        )
        recommendations = [
            "Retry in a few moments or lower the number of repeated model-backed runs.",
            f"Check your {provider or 'provider'} quota, billing, and usage limits.",
        ]
    elif any(marker in text for marker in ["timeout", "timed out", "temporarily unavailable", "connection reset", "connection error", "overloaded", "service unavailable", "502", "503", "504", "500"]):
        category = "transient_provider_error"
        retryable = True
        message = (
            f"Skilgen encountered a temporary provider or network failure while calling `{provider or 'openai'}`."
        )
        recommendations = [
            "Retry the command shortly. Skilgen will automatically retry transient failures, but the provider may still be unavailable.",
            f"Check {_provider_docs_url(provider)} for provider status or incident updates.",
        ]
    elif any(marker in text for marker in ["model not found", "unknown model", "unsupported model", "not found"]):
        category = "model_configuration_error"
        message = (
            f"Skilgen could not find or use the configured model for provider `{provider or 'openai'}`."
        )
        recommendations = [
            "Update `model` in `skilgen.yml` to a provider-supported model identifier.",
            f"Confirm the model is enabled for your `{provider or 'openai'}` account.",
        ]

    return {
        "category": category,
        "retryable": retryable,
        "message": message,
        "recommendations": recommendations,
        "provider": provider or "openai",
        "api_key_env": api_key_env or "MODEL_API_KEY",
    }


def _resolved_settings(project_root: str | Path = "."):
    return resolve_model_settings(load_config(Path(project_root).resolve()))


def deep_agents_unavailable_reason(project_root: str | Path = ".") -> str | None:
    settings = _resolved_settings(project_root)
    if not provider_supported(settings.provider):
        return (
            f"Unsupported model provider: {settings.provider}. "
            "Supported providers are openai, anthropic, google_genai/gemini, huggingface, groq, and openrouter."
        )
    if create_deep_agent is None:
        return (
            "Deep Agents dependencies are not installed in this Python environment. "
            "Use Python 3.11+ for Deep Agents support, or reinstall after upgrading Python."
        )
    if settings.provider != "huggingface" and init_chat_model is None:
        return (
            "Chat model initialization is unavailable in this Python environment. "
            "Reinstall Skilgen with the required LangChain provider packages."
        )
    key_env = settings.api_key_env or "OPENAI_API_KEY"
    if not os.getenv(key_env):
        return f"Missing model credential environment variable: {key_env}"
    return None


def _close_model(model: object) -> None:
    close = getattr(model, "close", None)
    if not callable(close):
        return
    try:
        result = close()
        if asyncio.iscoroutine(result):
            asyncio.run(result)
    except Exception:
        pass


def _model_name(project_root: str | Path = ".") -> str:
    settings = _resolved_settings(project_root)
    provider = settings.provider or "openai"
    model = settings.model or DEFAULT_CONFIG.model or os.getenv("SKILGEN_MODEL", "gpt-4.1-mini")
    return f"{provider}:{model}"


def deep_agents_available(project_root: str | Path = ".") -> bool:
    return deep_agents_unavailable_reason(project_root) is None


def current_runtime_mode(project_root: str | Path = ".") -> str:
    return runtime_label(deep_agents_available(project_root))


def runtime_diagnostics(project_root: str | Path = ".") -> dict[str, object]:
    root = Path(project_root).resolve()
    config = load_config(root)
    settings = resolve_model_settings(config)
    reason = deep_agents_unavailable_reason(root)
    enabled = reason is None
    recommendations: list[str] = []
    if not provider_supported(settings.provider):
        recommendations.append("Set `model_provider` in skilgen.yml to a supported provider.")
    if not settings.model:
        recommendations.append("Set `model` in skilgen.yml so Skilgen knows which model to use.")
    if settings.api_key_env and not os.getenv(settings.api_key_env):
        recommendations.append(_provider_env_hint(settings.provider, settings.api_key_env))
    if reason and "dependencies are not installed" in reason:
        recommendations.append("Reinstall Skilgen in Python 3.11+ so model-backed dependencies are available.")
    if not recommendations:
        recommendations.append("Runtime configuration looks ready for model-backed execution.")
    return {
        "project_root": str(root),
        "runtime": runtime_label(enabled),
        "model_backed_available": enabled,
        "provider": settings.provider,
        "model": settings.model,
        "api_key_env": settings.api_key_env,
        "api_key_present": settings.api_key_present,
        "temperature": settings.temperature,
        "max_tokens": settings.max_tokens,
        "retry_attempts": settings.retry_attempts,
        "retry_base_delay_seconds": settings.retry_base_delay_seconds,
        "reason": reason,
        "recommendations": recommendations,
    }


def _build_chat_model(project_root: str | Path = "."):
    if init_chat_model is None:
        raise RuntimeError("Chat model initialization is unavailable")
    settings = _resolved_settings(project_root)
    if settings.provider == "huggingface":
        kwargs: dict[str, object] = {
            "base_url": "https://router.huggingface.co/v1",
            "api_key": os.getenv(settings.api_key_env or "HUGGINGFACEHUB_API_TOKEN"),
            "use_responses_api": False,
        }
        if settings.temperature is not None:
            kwargs["temperature"] = settings.temperature
        if settings.max_tokens is not None:
            kwargs["max_tokens"] = settings.max_tokens
        model = settings.model or DEFAULT_CONFIG.model or "meta-llama/Llama-3.1-70B-Instruct"
        return init_chat_model(f"openai:{model}", **kwargs)
    model_name = _model_name(project_root)
    kwargs: dict[str, object] = {}
    if settings.temperature is not None:
        kwargs["temperature"] = settings.temperature
    if settings.max_tokens is not None:
        kwargs["max_tokens"] = settings.max_tokens
    return init_chat_model(model_name, **kwargs)


def _extract_json(text: str) -> dict[str, object]:
    stripped = text.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        return json.loads(stripped)
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start >= 0 and end > start:
        return json.loads(stripped[start : end + 1])
    raise ValueError("No JSON object found in Deep Agents response")


def _is_transient_error(exc: Exception, provider: str | None = None, api_key_env: str | None = None) -> bool:
    return bool(_classify_model_error(exc, provider, api_key_env)["retryable"])


def _invoke_with_retry(
    fn: Callable[[], object],
    *,
    attempts: int = 3,
    delay_seconds: float = 1.0,
    provider: str | None = None,
    api_key_env: str | None = None,
) -> object:
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            return fn()
        except Exception as exc:  # pragma: no cover - exercised in integration paths
            last_error = exc
            if attempt == attempts - 1 or not _is_transient_error(exc, provider, api_key_env):
                raise
            time.sleep(delay_seconds * (attempt + 1))
    if last_error is not None:
        raise last_error
    raise RuntimeError("Model-backed invocation failed without an exception")


def _normalize_json_with_model(task: str, raw_text: str, project_root: str | Path = ".") -> dict[str, object]:
    if init_chat_model is None:
        raise RuntimeError("Chat model is unavailable for JSON normalization")
    settings = _resolved_settings(project_root)
    model = _build_chat_model(project_root)
    try:
        response = _invoke_with_retry(
            lambda: model.invoke(
                [
                    (
                        "system",
                        (
                            "You normalize agent outputs into strict JSON for Skilgen. "
                            "Return exactly one valid JSON object, with no markdown fences, commentary, or prose. "
                            "If the source text is partially structured, preserve all useful fields and discard filler."
                        ),
                    ),
                    (
                        "user",
                        (
                            f"Task: {task}\n\n"
                            "Normalize the following agent output into one valid JSON object matching the requested schema.\n\n"
                            f"{raw_text}"
                        ),
                    ),
                ]
            ),
            attempts=settings.retry_attempts,
            delay_seconds=settings.retry_base_delay_seconds,
            provider=settings.provider,
            api_key_env=settings.api_key_env,
        )
        return _extract_json(_message_text(response))
    finally:
        _close_model(model)


def _message_text(message: object) -> str:
    if isinstance(message, dict):
        content = message.get("content", "")
    else:
        content = getattr(message, "content", "")
    if isinstance(content, list):
        return "".join(part.get("text", "") if isinstance(part, dict) else str(part) for part in content).strip()
    return str(content).strip()


def run_deep_json(
    task: str,
    prompt: str,
    fallback: Callable[[], dict[str, object]],
    *,
    project_root: str | Path = ".",
) -> dict[str, object]:
    required = os.getenv("SKILGEN_DEEPAGENTS_REQUIRED") == "1"
    root = Path(project_root).resolve()
    if not deep_agents_available(root):
        if required:
            raise RuntimeError(deep_agents_unavailable_reason(root) or "Deep Agents runtime is required but unavailable")
        return fallback()

    settings = _resolved_settings(root)
    model = _build_chat_model(root)
    agent = create_deep_agent(
        model=model,
        system_prompt=(
            "You are Skilgen's internal reasoning engine for requirements interpretation, planning, "
            "feature modeling, and skill guidance synthesis.\n"
            "Your job is to extract complete, implementation-relevant information from the provided "
            "requirements and code context without inventing unsupported details.\n"
            "Prioritize:\n"
            "1. completeness over brevity,\n"
            "2. grounded details from the provided input,\n"
            "3. stable output formatting,\n"
            "4. direct support for downstream automation.\n"
            "Output contract:\n"
            "- Return exactly one valid JSON object.\n"
            "- Do not wrap JSON in markdown fences.\n"
            "- Do not add explanation before or after the JSON.\n"
            "- Prefer short, concrete strings over vague summaries.\n"
            "- Include only fields supported by the requested shape."
        ),
    )
    try:
        result = _invoke_with_retry(
            lambda: agent.invoke({"messages": [{"role": "user", "content": f"Task: {task}\n\n{prompt}"}]}),
            attempts=settings.retry_attempts,
            delay_seconds=settings.retry_base_delay_seconds,
            provider=settings.provider,
            api_key_env=settings.api_key_env,
        )
        messages = result.get("messages", []) if isinstance(result, dict) else []
        if not messages:
            if required:
                raise RuntimeError("Deep Agents returned no messages")
            return fallback()
        collected = []
        for message in reversed(messages):
            text = _message_text(message)
            if not text:
                continue
            collected.append(text)
            try:
                return _extract_json(text)
            except Exception:
                continue
        normalized_source = "\n\n".join(reversed(collected))
        if normalized_source:
            return _normalize_json_with_model(task, normalized_source, root)
        raise ValueError("No usable agent text found for JSON normalization")
    except Exception as exc:
        if required:
            error = _classify_model_error(exc, settings.provider, settings.api_key_env)
            raise RuntimeError(
                f"{error['message']} Task=`{task}` Provider={_model_name(root)} "
                f"Category={error['category']} Recommendations={' | '.join(error['recommendations'])}"
            ) from exc
        return fallback()
    finally:
        _close_model(model)


def run_deep_text(
    task: str,
    prompt: str,
    fallback: Callable[[], str],
    *,
    project_root: str | Path = ".",
) -> str:
    required = os.getenv("SKILGEN_DEEPAGENTS_REQUIRED") == "1"
    root = Path(project_root).resolve()
    if not deep_agents_available(root):
        if required:
            raise RuntimeError(deep_agents_unavailable_reason(root) or "Deep Agents runtime is required but unavailable")
        return fallback()

    settings = _resolved_settings(root)
    model = _build_chat_model(root)
    agent = create_deep_agent(
        model=model,
        system_prompt=(
            "You are Skilgen's internal content synthesis engine.\n"
            "Write polished, structured project artifacts for Skilgen using the supplied requirements, "
            "code evidence, and plan context.\n"
            "Prioritize clarity, completeness, reuse guidance, and traceability to evidence.\n"
            "Output contract:\n"
            "- Return only the requested markdown text.\n"
            "- Do not add preambles like 'Here is the markdown'.\n"
            "- Preserve requested headings, tables, references, and file-oriented structure.\n"
            "- Prefer actionable guidance over abstract commentary."
        ),
    )
    try:
        result = _invoke_with_retry(
            lambda: agent.invoke({"messages": [{"role": "user", "content": f"Task: {task}\n\n{prompt}"}]}),
            attempts=settings.retry_attempts,
            delay_seconds=settings.retry_base_delay_seconds,
            provider=settings.provider,
            api_key_env=settings.api_key_env,
        )
        messages = result.get("messages", []) if isinstance(result, dict) else []
        if not messages:
            if required:
                raise RuntimeError("Deep Agents returned no messages")
            return fallback()
        return _message_text(messages[-1])
    except Exception as exc:
        if required:
            error = _classify_model_error(exc, settings.provider, settings.api_key_env)
            raise RuntimeError(
                f"{error['message']} Task=`{task}` Provider={_model_name(root)} "
                f"Category={error['category']} Recommendations={' | '.join(error['recommendations'])}"
            ) from exc
        return fallback()
    finally:
        _close_model(model)
