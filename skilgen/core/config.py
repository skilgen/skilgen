from __future__ import annotations

from pathlib import Path

from skilgen.core.models import SkilgenConfig


DEFAULT_CONFIG = SkilgenConfig(
    include_paths=["."],
    exclude_paths=[".git", "__pycache__", ".venv", "node_modules", ".skilgen"],
    domains_override=[],
    skill_depth=2,
    update_trigger="auto",
    langsmith_project=None,
    model_provider="openai",
    model="gpt-4.1-mini",
    api_key_env="OPENAI_API_KEY",
    model_temperature=None,
    model_max_tokens=None,
    model_retry_attempts=3,
    model_retry_base_delay_seconds=1.0,
    auto_install_external_skills=True,
    external_skills_allowed_trust_levels=["official", "spec", "community", "curated"],
    external_skills_allowlist=[],
    external_skills_denylist=[],
    external_skills_auto_activate=True,
    external_skills_policy_mode="permissive",
    auto_activate_mcp_connectors=True,
    mcp_connectors_require_official_source=True,
    mcp_connectors_require_oauth=True,
    mcp_connector_allowlist=[],
    mcp_connector_denylist=[],
    enterprise_skill_paths=[],
    enterprise_skill_git_urls=[],
)


PROVIDER_DEFAULTS: dict[str, tuple[str, str]] = {
    "openai": ("gpt-4.1-mini", "OPENAI_API_KEY"),
    "anthropic": ("claude-sonnet-4-5", "ANTHROPIC_API_KEY"),
    "gemini": ("gemini-2.5-pro", "GOOGLE_API_KEY"),
    "google": ("gemini-2.5-pro", "GOOGLE_API_KEY"),
    "google_genai": ("gemini-2.5-pro", "GOOGLE_API_KEY"),
    "huggingface": ("meta-llama/Llama-3.1-70B-Instruct", "HUGGINGFACEHUB_API_TOKEN"),
    "hugging_face": ("meta-llama/Llama-3.1-70B-Instruct", "HUGGINGFACEHUB_API_TOKEN"),
    "hf": ("meta-llama/Llama-3.1-70B-Instruct", "HUGGINGFACEHUB_API_TOKEN"),
}


def _parse_scalar(raw: str) -> str | int | float | bool | None:
    value = raw.strip()
    if value in {"", "null", "None"}:
        return None
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    if value.isdigit():
        return int(value)
    try:
        if "." in value:
            return float(value)
    except ValueError:
        pass
    if value.startswith(("'", '"')) and value.endswith(("'", '"')):
        return value[1:-1]
    return value


def load_config(project_root: Path) -> SkilgenConfig:
    path = project_root / "skilgen.yml"
    if not path.exists():
        return DEFAULT_CONFIG

    data: dict[str, object] = {
        "include_paths": [],
        "exclude_paths": [],
        "domains_override": [],
        "skill_depth": DEFAULT_CONFIG.skill_depth,
        "update_trigger": DEFAULT_CONFIG.update_trigger,
        "langsmith_project": DEFAULT_CONFIG.langsmith_project,
        "model_provider": DEFAULT_CONFIG.model_provider,
        "model": DEFAULT_CONFIG.model,
        "api_key_env": DEFAULT_CONFIG.api_key_env,
        "model_temperature": DEFAULT_CONFIG.model_temperature,
        "model_max_tokens": DEFAULT_CONFIG.model_max_tokens,
        "model_retry_attempts": DEFAULT_CONFIG.model_retry_attempts,
        "model_retry_base_delay_seconds": DEFAULT_CONFIG.model_retry_base_delay_seconds,
        "auto_install_external_skills": DEFAULT_CONFIG.auto_install_external_skills,
        "external_skills_allowed_trust_levels": list(DEFAULT_CONFIG.external_skills_allowed_trust_levels),
        "external_skills_allowlist": list(DEFAULT_CONFIG.external_skills_allowlist),
        "external_skills_denylist": list(DEFAULT_CONFIG.external_skills_denylist),
        "external_skills_auto_activate": DEFAULT_CONFIG.external_skills_auto_activate,
        "external_skills_policy_mode": DEFAULT_CONFIG.external_skills_policy_mode,
        "auto_activate_mcp_connectors": DEFAULT_CONFIG.auto_activate_mcp_connectors,
        "mcp_connectors_require_official_source": DEFAULT_CONFIG.mcp_connectors_require_official_source,
        "mcp_connectors_require_oauth": DEFAULT_CONFIG.mcp_connectors_require_oauth,
        "mcp_connector_allowlist": list(DEFAULT_CONFIG.mcp_connector_allowlist),
        "mcp_connector_denylist": list(DEFAULT_CONFIG.mcp_connector_denylist),
        "enterprise_skill_paths": list(DEFAULT_CONFIG.enterprise_skill_paths),
        "enterprise_skill_git_urls": list(DEFAULT_CONFIG.enterprise_skill_git_urls),
    }
    current_list: str | None = None

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- "):
            if current_list is None:
                continue
            items = data.setdefault(current_list, [])
            if isinstance(items, list):
                items.append(stripped[2:].strip())
            continue
        if ":" not in stripped:
            continue
        key, raw = stripped.split(":", 1)
        key = key.strip()
        raw = raw.strip()
        if raw == "":
            current_list = key
            data.setdefault(key, [])
            continue
        current_list = None
        data[key] = _parse_scalar(raw)

    return SkilgenConfig(
        include_paths=list(data.get("include_paths", [])),
        exclude_paths=list(data.get("exclude_paths", [])),
        domains_override=list(data.get("domains_override", [])),
        skill_depth=int(data.get("skill_depth", DEFAULT_CONFIG.skill_depth)),
        update_trigger=str(data.get("update_trigger", DEFAULT_CONFIG.update_trigger)),
        langsmith_project=data.get("langsmith_project") if isinstance(data.get("langsmith_project"), str) or data.get("langsmith_project") is None else None,
        model_provider=data.get("model_provider") if isinstance(data.get("model_provider"), str) or data.get("model_provider") is None else None,
        model=data.get("model") if isinstance(data.get("model"), str) or data.get("model") is None else None,
        api_key_env=data.get("api_key_env") if isinstance(data.get("api_key_env"), str) or data.get("api_key_env") is None else None,
        model_temperature=float(data.get("model_temperature")) if isinstance(data.get("model_temperature"), (float, int)) else None,
        model_max_tokens=int(data.get("model_max_tokens")) if isinstance(data.get("model_max_tokens"), int) else None,
        model_retry_attempts=int(data.get("model_retry_attempts", DEFAULT_CONFIG.model_retry_attempts)),
        model_retry_base_delay_seconds=float(data.get("model_retry_base_delay_seconds", DEFAULT_CONFIG.model_retry_base_delay_seconds)),
        auto_install_external_skills=bool(data.get("auto_install_external_skills", DEFAULT_CONFIG.auto_install_external_skills)),
        external_skills_allowed_trust_levels=list(data.get("external_skills_allowed_trust_levels", DEFAULT_CONFIG.external_skills_allowed_trust_levels)),
        external_skills_allowlist=list(data.get("external_skills_allowlist", DEFAULT_CONFIG.external_skills_allowlist)),
        external_skills_denylist=list(data.get("external_skills_denylist", DEFAULT_CONFIG.external_skills_denylist)),
        external_skills_auto_activate=bool(data.get("external_skills_auto_activate", DEFAULT_CONFIG.external_skills_auto_activate)),
        external_skills_policy_mode=str(data.get("external_skills_policy_mode", DEFAULT_CONFIG.external_skills_policy_mode)),
        auto_activate_mcp_connectors=bool(data.get("auto_activate_mcp_connectors", DEFAULT_CONFIG.auto_activate_mcp_connectors)),
        mcp_connectors_require_official_source=bool(
            data.get("mcp_connectors_require_official_source", DEFAULT_CONFIG.mcp_connectors_require_official_source)
        ),
        mcp_connectors_require_oauth=bool(data.get("mcp_connectors_require_oauth", DEFAULT_CONFIG.mcp_connectors_require_oauth)),
        mcp_connector_allowlist=list(data.get("mcp_connector_allowlist", DEFAULT_CONFIG.mcp_connector_allowlist)),
        mcp_connector_denylist=list(data.get("mcp_connector_denylist", DEFAULT_CONFIG.mcp_connector_denylist)),
        enterprise_skill_paths=list(data.get("enterprise_skill_paths", DEFAULT_CONFIG.enterprise_skill_paths)),
        enterprise_skill_git_urls=list(data.get("enterprise_skill_git_urls", DEFAULT_CONFIG.enterprise_skill_git_urls)),
    )


def render_default_config(provider: str | None = None) -> str:
    provider_key = provider.strip().lower() if provider else None
    model = ""
    api_key_env = ""
    if provider_key in PROVIDER_DEFAULTS:
        model, api_key_env = PROVIDER_DEFAULTS[provider_key]

    provider_comment = (
        "# Set these to your preferred provider. For example:\n"
        "# openai / gpt-4.1-mini / OPENAI_API_KEY\n"
        "# anthropic / claude-sonnet-4-5 / ANTHROPIC_API_KEY\n"
        "# gemini / gemini-2.5-pro / GOOGLE_API_KEY\n"
        "# huggingface / meta-llama/Llama-3.1-70B-Instruct / HUGGINGFACEHUB_API_TOKEN\n"
    )

    return f"""# Skilgen configuration
include_paths:
  - .
exclude_paths:
  - .git
  - __pycache__
  - .venv
  - node_modules
  - .skilgen
domains_override:
skill_depth: 2
update_trigger: auto
langsmith_project:
{provider_comment}model_provider: {provider_key or ""}
model: {model}
api_key_env: {api_key_env}
model_temperature:
model_max_tokens:
model_retry_attempts: 3
model_retry_base_delay_seconds: 1.0
auto_install_external_skills: true
external_skills_allowed_trust_levels:
  - official
  - spec
  - community
  - curated
external_skills_allowlist:
external_skills_denylist:
external_skills_auto_activate: true
external_skills_policy_mode: permissive
auto_activate_mcp_connectors: true
mcp_connectors_require_official_source: true
mcp_connectors_require_oauth: true
mcp_connector_allowlist:
mcp_connector_denylist:
enterprise_skill_paths:
enterprise_skill_git_urls:
"""
