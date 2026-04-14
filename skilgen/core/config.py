from __future__ import annotations

from pathlib import Path

from skilgen.core.models import CorpusSettings, SkilgenConfig


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
    model_endpoint=None,
    model_extra_kwargs={},
    model_temperature=None,
    model_max_tokens=None,
    model_retry_attempts=3,
    model_retry_base_delay_seconds=1.0,
    corpus=CorpusSettings(),
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
    mcp_policy_pack_path=None,
    enterprise_skill_paths=[],
    enterprise_skill_git_urls=[],
    enterprise_skill_urls=[],
)


PROVIDER_DEFAULTS: dict[str, tuple[str, str | None]] = {
    "openai": ("gpt-4.1-mini", "OPENAI_API_KEY"),
    "anthropic": ("claude-sonnet-4-5", "ANTHROPIC_API_KEY"),
    "gemini": ("gemini-2.5-pro", "GOOGLE_API_KEY"),
    "google": ("gemini-2.5-pro", "GOOGLE_API_KEY"),
    "google_genai": ("gemini-2.5-pro", "GOOGLE_API_KEY"),
    "huggingface": ("meta-llama/Llama-3.1-70B-Instruct", "HUGGINGFACEHUB_API_TOKEN"),
    "hugging_face": ("meta-llama/Llama-3.1-70B-Instruct", "HUGGINGFACEHUB_API_TOKEN"),
    "hf": ("meta-llama/Llama-3.1-70B-Instruct", "HUGGINGFACEHUB_API_TOKEN"),
    "azure_openai": ("gpt-4o", "AZURE_OPENAI_API_KEY"),
    "bedrock": ("anthropic.claude-3-5-sonnet-20241022-v2:0", None),
    "ollama": ("llama3.1:70b", None),
    "openai_compatible": ("your-private-model", "MODEL_API_KEY"),
}


def _string_or_none(value: object) -> str | None:
    return value if isinstance(value, str) or value is None else None


def _string_list(value: object, fallback: list[str]) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if item is not None]
    return list(fallback)


def _bool_value(value: object, fallback: bool) -> bool:
    return value if isinstance(value, bool) else fallback


def _int_value(value: object, fallback: int) -> int:
    return int(value) if isinstance(value, (int, float)) else fallback


def _float_value(value: object, fallback: float) -> float:
    return float(value) if isinstance(value, (int, float)) else fallback


def _dict_value(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        return {}
    return {str(key): nested for key, nested in value.items()}


def _parse_scalar(raw: str) -> object:
    value = raw.strip()
    if value in {"", "null", "None"}:
        return None
    if value in {"{}", "{ }"}:
        return {}
    if value in {"[]", "[ ]"}:
        return []
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


def _parse_yaml_like(text: str) -> dict[str, object]:
    lines = [
        (len(raw) - len(raw.lstrip(" ")), raw.strip())
        for raw in text.splitlines()
        if raw.strip() and not raw.lstrip().startswith("#")
    ]
    root: dict[str, object] = {}
    stack: list[tuple[int, object]] = [(-1, root)]

    for index, (indent, stripped) in enumerate(lines):
        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()
        current = stack[-1][1]
        if stripped.startswith("- "):
            if isinstance(current, list):
                current.append(_parse_scalar(stripped[2:].strip()))
            continue
        if ":" not in stripped or not isinstance(current, dict):
            continue
        key, raw = stripped.split(":", 1)
        key = key.strip()
        raw = raw.strip()
        if raw:
            current[key] = _parse_scalar(raw)
            continue
        next_container: object = {}
        if index + 1 < len(lines):
            next_indent, next_stripped = lines[index + 1]
            if next_indent > indent and next_stripped.startswith("- "):
                next_container = []
        current[key] = next_container
        stack.append((indent, next_container))
    return root


def load_config(project_root: Path) -> SkilgenConfig:
    path = project_root / "skilgen.yml"
    if not path.exists():
        return DEFAULT_CONFIG

    raw = _parse_yaml_like(path.read_text(encoding="utf-8"))
    data: dict[str, object] = {str(key): value for key, value in raw.items()}
    corpus_raw = _dict_value(data.get("corpus"))
    default_corpus = DEFAULT_CONFIG.corpus
    corpus = CorpusSettings(
        enabled=_bool_value(corpus_raw.get("enabled"), default_corpus.enabled),
        budget=_int_value(corpus_raw.get("budget"), default_corpus.budget),
        hub_budget=_int_value(corpus_raw.get("hub_budget"), default_corpus.hub_budget),
        cluster_budget=_int_value(corpus_raw.get("cluster_budget"), default_corpus.cluster_budget),
        config_budget=_int_value(corpus_raw.get("config_budget"), default_corpus.config_budget),
        doc_budget=_int_value(corpus_raw.get("doc_budget"), default_corpus.doc_budget),
        exclude_generated=_bool_value(corpus_raw.get("exclude_generated"), default_corpus.exclude_generated),
        min_cluster_size=_int_value(corpus_raw.get("min_cluster_size"), default_corpus.min_cluster_size),
        exclude_patterns=_string_list(corpus_raw.get("exclude_patterns"), default_corpus.exclude_patterns),
        cache_path=_string_or_none(corpus_raw.get("cache_path")) or default_corpus.cache_path,
    )

    return SkilgenConfig(
        include_paths=_string_list(data.get("include_paths"), DEFAULT_CONFIG.include_paths),
        exclude_paths=_string_list(data.get("exclude_paths"), DEFAULT_CONFIG.exclude_paths),
        domains_override=_string_list(data.get("domains_override"), DEFAULT_CONFIG.domains_override),
        skill_depth=_int_value(data.get("skill_depth"), DEFAULT_CONFIG.skill_depth),
        update_trigger=_string_or_none(data.get("update_trigger")) or DEFAULT_CONFIG.update_trigger,
        langsmith_project=_string_or_none(data.get("langsmith_project")),
        model_provider=_string_or_none(data.get("model_provider")),
        model=_string_or_none(data.get("model")),
        api_key_env=_string_or_none(data.get("api_key_env")),
        model_endpoint=_string_or_none(data.get("model_endpoint")),
        model_extra_kwargs=_dict_value(data.get("model_extra_kwargs")),
        model_temperature=float(data.get("model_temperature")) if isinstance(data.get("model_temperature"), (float, int)) else None,
        model_max_tokens=_int_value(data.get("model_max_tokens"), 0) or None,
        model_retry_attempts=_int_value(data.get("model_retry_attempts"), DEFAULT_CONFIG.model_retry_attempts),
        model_retry_base_delay_seconds=_float_value(
            data.get("model_retry_base_delay_seconds"), DEFAULT_CONFIG.model_retry_base_delay_seconds
        ),
        corpus=corpus,
        auto_install_external_skills=_bool_value(data.get("auto_install_external_skills"), DEFAULT_CONFIG.auto_install_external_skills),
        external_skills_allowed_trust_levels=_string_list(
            data.get("external_skills_allowed_trust_levels"), DEFAULT_CONFIG.external_skills_allowed_trust_levels
        ),
        external_skills_allowlist=_string_list(data.get("external_skills_allowlist"), DEFAULT_CONFIG.external_skills_allowlist),
        external_skills_denylist=_string_list(data.get("external_skills_denylist"), DEFAULT_CONFIG.external_skills_denylist),
        external_skills_auto_activate=_bool_value(data.get("external_skills_auto_activate"), DEFAULT_CONFIG.external_skills_auto_activate),
        external_skills_policy_mode=_string_or_none(data.get("external_skills_policy_mode")) or DEFAULT_CONFIG.external_skills_policy_mode,
        auto_activate_mcp_connectors=_bool_value(data.get("auto_activate_mcp_connectors"), DEFAULT_CONFIG.auto_activate_mcp_connectors),
        mcp_connectors_require_official_source=_bool_value(
            data.get("mcp_connectors_require_official_source"), DEFAULT_CONFIG.mcp_connectors_require_official_source
        ),
        mcp_connectors_require_oauth=_bool_value(data.get("mcp_connectors_require_oauth"), DEFAULT_CONFIG.mcp_connectors_require_oauth),
        mcp_connector_allowlist=_string_list(data.get("mcp_connector_allowlist"), DEFAULT_CONFIG.mcp_connector_allowlist),
        mcp_connector_denylist=_string_list(data.get("mcp_connector_denylist"), DEFAULT_CONFIG.mcp_connector_denylist),
        mcp_policy_pack_path=_string_or_none(data.get("mcp_policy_pack_path")),
        enterprise_skill_paths=_string_list(data.get("enterprise_skill_paths"), DEFAULT_CONFIG.enterprise_skill_paths),
        enterprise_skill_git_urls=_string_list(data.get("enterprise_skill_git_urls"), DEFAULT_CONFIG.enterprise_skill_git_urls),
        enterprise_skill_urls=_string_list(data.get("enterprise_skill_urls"), DEFAULT_CONFIG.enterprise_skill_urls),
    )


def render_default_config(provider: str | None = None) -> str:
    provider_key = provider.strip().lower() if provider else None
    model = ""
    api_key_env = ""
    if provider_key in PROVIDER_DEFAULTS:
        model, configured_key_env = PROVIDER_DEFAULTS[provider_key]
        api_key_env = configured_key_env or ""

    provider_comment = (
        "# Set these to your preferred provider. For example:\n"
        "# openai / gpt-4.1-mini / OPENAI_API_KEY\n"
        "# anthropic / claude-sonnet-4-5 / ANTHROPIC_API_KEY\n"
        "# gemini / gemini-2.5-pro / GOOGLE_API_KEY\n"
        "# huggingface / meta-llama/Llama-3.1-70B-Instruct / HUGGINGFACEHUB_API_TOKEN\n"
        "# azure_openai / gpt-4o / AZURE_OPENAI_API_KEY\n"
        "# bedrock / anthropic.claude-3-5-sonnet-20241022-v2:0 / IAM auth\n"
        "# ollama / llama3.1:70b / local endpoint\n"
        "# openai_compatible / your-private-model / MODEL_API_KEY\n"
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
model_endpoint:
model_extra_kwargs: {{}}
model_temperature:
model_max_tokens:
model_retry_attempts: 3
model_retry_base_delay_seconds: 1.0
corpus:
  enabled: true
  budget: 60
  hub_budget: 40
  cluster_budget: 10
  config_budget: 5
  doc_budget: 5
  exclude_generated: true
  min_cluster_size: 3
  exclude_patterns: []
  cache_path: .skilgen/corpus/index.json
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
mcp_policy_pack_path:
enterprise_skill_paths:
enterprise_skill_git_urls:
enterprise_skill_urls:
"""
