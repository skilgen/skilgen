"""Parse Terraform HCL directories into infrastructure evidence summaries."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

try:  # pragma: no cover - optional dependency
    import hcl2
except ImportError:  # pragma: no cover - optional dependency
    hcl2 = None


RESOURCE_CATEGORIES = {
    "aws_": "cloud_infrastructure",
    "kubernetes_": "k8s_infrastructure",
    "google_": "gcp",
    "azurerm_": "azure",
}
TAGGABLE_RESOURCE_PREFIXES = ("aws_", "azurerm_", "google_")
NON_TAGGABLE_RESOURCE_TYPES = {
    "aws_iam_policy_attachment",
    "aws_iam_role_policy_attachment",
    "google_project_iam_binding",
    "google_project_iam_member",
    "google_project_iam_policy",
}
ARN_PATTERN = re.compile(r"arn:aws:[A-Za-z0-9_:/=${}.*+-]+")
AWS_ACCOUNT_PATTERN = re.compile(r"(?<!\d)\d{12}(?!\d)")
AWS_REGION_PATTERN = re.compile(
    r"\b(?:us|eu|ap|sa|ca|me|af)-(?:gov-)?(?:central|north|south|east|west|northeast|northwest|southeast|southwest)-\d\b"
)
RESOURCE_BLOCK_RE = re.compile(r'(?ms)^\s*resource\s+"([^"]+)"\s+"([^"]+)"\s*\{')
LABELED_BLOCK_RE = re.compile(r'(?ms)^\s*(provider|variable|output|module)\s+"([^"]+)"\s*\{')
BACKEND_BLOCK_RE = re.compile(r'(?ms)^\s*backend\s+"([^"]+)"\s*\{')
DATA_REMOTE_STATE_RE = re.compile(r'(?ms)^\s*data\s+"terraform_remote_state"\s+"([^"]+)"\s*\{')
ASSIGNMENT_RE = re.compile(r'^\s*([A-Za-z_][A-Za-z0-9_-]*)\s*=\s*(.+?)\s*$', re.MULTILINE)


class TerraformParserError(ValueError):
    """Raised when a Terraform directory cannot be parsed."""


@dataclass(frozen=True)
class TerraformResource:
    """A Terraform resource declaration with its inferred ownership category."""

    type: str
    name: str
    category: str
    file: str


@dataclass(frozen=True)
class TerraformParseResult:
    """Terraform directory summary suitable for skill-generation evidence."""

    root: str
    files: list[str]
    parser_backend: str
    resource_counts: dict[str, int]
    resource_counts_by_category: dict[str, int]
    resources: list[TerraformResource] = field(default_factory=list)
    providers: dict[str, dict[str, object]] = field(default_factory=dict)
    variables: dict[str, dict[str, object]] = field(default_factory=dict)
    outputs: dict[str, dict[str, object]] = field(default_factory=dict)
    modules: dict[str, dict[str, object]] = field(default_factory=dict)
    backend_config: dict[str, dict[str, object]] = field(default_factory=dict)
    patterns: list[str] = field(default_factory=list)
    anti_patterns: list[str] = field(default_factory=list)


def parse_terraform_directory(path: str | Path) -> TerraformParseResult:
    """Parse all ``*.tf`` files under ``path`` and summarize infrastructure evidence."""

    root = Path(path).resolve()
    if not root.exists():
        raise TerraformParserError(f"Terraform parser expected an existing path: {root}")
    if not root.is_dir():
        raise TerraformParserError(f"Terraform parser expected a directory, got file: {root}")

    files = sorted(candidate for candidate in root.rglob("*.tf") if candidate.is_file())
    resources: list[TerraformResource] = []
    providers: dict[str, dict[str, object]] = {}
    variables: dict[str, dict[str, object]] = {}
    outputs: dict[str, dict[str, object]] = {}
    modules: dict[str, dict[str, object]] = {}
    backend_config: dict[str, dict[str, object]] = {}
    patterns: set[str] = set()
    anti_patterns: set[str] = set()
    backend = "python-hcl2" if hcl2 is not None else "regex-fallback"
    terraform_required_version = False
    provider_version_constraints: set[str] = set()

    for file_path in files:
        text = _read_text(file_path)
        if not text.strip():
            continue
        payload = _load_hcl(file_path, text)
        relative = file_path.relative_to(root).as_posix()

        for resource_type, name, body in _iter_resources(payload, text):
            category = _resource_category(resource_type)
            resources.append(TerraformResource(type=resource_type, name=name, category=category, file=relative))
            if _requires_tags(resource_type) and not _has_key(body, "tags"):
                anti_patterns.add(f"resource_without_tags:{resource_type}.{name}")

        for provider_name, body in _iter_named_blocks(payload, "provider", text):
            providers[provider_name] = _public_mapping(body)
            if _has_key(body, "default_tags") or _has_key(body, "tags"):
                patterns.add("provider_default_tags")

        for variable_name, body in _iter_named_blocks(payload, "variable", text):
            variable_mapping = _public_mapping(body)
            description = _scalar(variable_mapping.get("description"))
            variables[variable_name] = {
                "description": description,
                "has_validation": _has_key(body, "validation"),
                "type": _type_label(variable_mapping.get("type")),
            }
            if description:
                patterns.add("variable_descriptions")
            else:
                anti_patterns.add(f"variable_without_description:{variable_name}")
            if _has_key(body, "validation"):
                patterns.add("variable_validation")

        for output_name, body in _iter_named_blocks(payload, "output", text):
            output_mapping = _public_mapping(body)
            description = _scalar(output_mapping.get("description"))
            outputs[output_name] = {"description": description}
            if not description:
                anti_patterns.add(f"output_without_description:{output_name}")

        for module_name, body in _iter_named_blocks(payload, "module", text):
            modules[module_name] = _public_mapping(body)
            if not _has_key(body, "version"):
                anti_patterns.add(f"module_missing_version:{module_name}")

        for backend_name, body in _iter_backends(payload, text):
            backend_config[backend_name] = _public_mapping(body)
            patterns.add("remote_state_backend")

        if _has_remote_state_data(payload, text):
            patterns.add("remote_state_data_source")

        if _has_any_tags(payload, text):
            patterns.add("resource_tags")

        if _terraform_required_version(payload, text):
            terraform_required_version = True
        provider_version_constraints.update(_required_provider_versions(payload, text))
        anti_patterns.update(_hardcoded_value_findings(relative, text))

    if files and not terraform_required_version:
        anti_patterns.add("missing_terraform_required_version")
    for provider_name in sorted(providers):
        if provider_name not in provider_version_constraints:
            anti_patterns.add(f"provider_missing_version_constraint:{provider_name}")

    resource_counts = Counter(resource.type for resource in resources)
    category_counts = Counter(resource.category for resource in resources)
    return TerraformParseResult(
        root=root.as_posix(),
        files=[path.relative_to(root).as_posix() for path in files],
        parser_backend=backend,
        resource_counts=dict(sorted(resource_counts.items())),
        resource_counts_by_category=dict(sorted(category_counts.items())),
        resources=resources,
        providers=dict(sorted(providers.items())),
        variables=dict(sorted(variables.items())),
        outputs=dict(sorted(outputs.items())),
        modules=dict(sorted(modules.items())),
        backend_config=dict(sorted(backend_config.items())),
        patterns=sorted(patterns),
        anti_patterns=sorted(anti_patterns),
    )


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise TerraformParserError(f"Terraform parser could not read {path}: {exc}") from exc


def _load_hcl(path: Path, text: str) -> dict[str, object]:
    if hcl2 is None:
        _validate_balanced_braces(path, text)
        return {}
    try:
        with path.open("r", encoding="utf-8") as handle:
            loaded = hcl2.load(handle)
    except Exception as exc:  # pragma: no cover - exercised only when python-hcl2 is installed
        raise TerraformParserError(f"Terraform parser failed to parse {path}: {exc}") from exc
    if not isinstance(loaded, dict):
        raise TerraformParserError(f"Terraform parser expected object payload in {path}")
    return loaded


def _validate_balanced_braces(path: Path, text: str) -> None:
    depth = 0
    for char in _strip_strings(text):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        if depth < 0:
            raise TerraformParserError(f"Terraform parser found an unmatched closing brace in {path}")
    if depth:
        raise TerraformParserError(f"Terraform parser found {depth} unmatched opening brace(s) in {path}")


def _strip_strings(text: str) -> str:
    return re.sub(r'"(?:\\.|[^"\\])*"', '""', text)


def _resource_category(resource_type: str) -> str:
    for prefix, category in RESOURCE_CATEGORIES.items():
        if resource_type.startswith(prefix):
            return category
    return "infrastructure"


def _requires_tags(resource_type: str) -> bool:
    return resource_type.startswith(TAGGABLE_RESOURCE_PREFIXES) and resource_type not in NON_TAGGABLE_RESOURCE_TYPES


def _iter_resources(payload: dict[str, object], text: str) -> list[tuple[str, str, dict[str, object] | str]]:
    resources: list[tuple[str, str, dict[str, object] | str]] = []
    for entry in _as_list(payload.get("resource")):
        if not isinstance(entry, dict):
            continue
        for resource_type, named_blocks in entry.items():
            if not isinstance(named_blocks, dict):
                continue
            for name, body in named_blocks.items():
                resources.append((str(resource_type), str(name), body if isinstance(body, dict) else {}))
    if resources:
        return resources
    return [(rtype, name, _extract_block_body(text, match.end() - 1)) for match in RESOURCE_BLOCK_RE.finditer(text) for rtype, name in [match.groups()]]


def _iter_named_blocks(
    payload: dict[str, object], kind: str, text: str
) -> list[tuple[str, dict[str, object] | str]]:
    entries: list[tuple[str, dict[str, object] | str]] = []
    for entry in _as_list(payload.get(kind)):
        if not isinstance(entry, dict):
            continue
        for name, body in entry.items():
            entries.append((str(name), body if isinstance(body, dict) else {}))
    if entries:
        return entries
    return [
        (name, _extract_block_body(text, match.end() - 1))
        for match in LABELED_BLOCK_RE.finditer(text)
        for block_kind, name in [match.groups()]
        if block_kind == kind
    ]


def _iter_backends(payload: dict[str, object], text: str) -> list[tuple[str, dict[str, object] | str]]:
    entries: list[tuple[str, dict[str, object] | str]] = []
    for terraform in _as_list(payload.get("terraform")):
        if not isinstance(terraform, dict):
            continue
        for backend_entry in _as_list(terraform.get("backend")):
            if isinstance(backend_entry, dict):
                for name, body in backend_entry.items():
                    entries.append((str(name), body if isinstance(body, dict) else {}))
    if entries:
        return entries
    return [(name, _extract_block_body(text, match.end() - 1)) for match in BACKEND_BLOCK_RE.finditer(text) for name in [match.group(1)]]


def _as_list(value: object) -> list[object]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _extract_block_body(text: str, open_brace_index: int) -> str:
    depth = 0
    for index in range(open_brace_index, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[open_brace_index + 1 : index]
    return text[open_brace_index + 1 :]


def _has_key(body: object, key: str) -> bool:
    if isinstance(body, dict):
        return key in body
    if isinstance(body, str):
        return re.search(rf"(?m)^\s*{re.escape(key)}\s*(=|\{{)", body) is not None
    return False


def _scalar(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return str(value)


def _type_label(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "list"
    return type(value).__name__


def _public_mapping(body: object) -> dict[str, object]:
    if isinstance(body, dict):
        return {str(key): _redacted_value(value) for key, value in sorted(body.items(), key=lambda item: str(item[0]))}
    if isinstance(body, str):
        return _parse_hcl_mapping(body)
    return {}


def _parse_hcl_mapping(text: str) -> dict[str, object]:
    result: dict[str, object] = {}
    index = 0
    length = len(text)
    while index < length:
        index = _skip_hcl_whitespace(text, index)
        if index >= length:
            break
        key_match = re.match(r"[A-Za-z_][A-Za-z0-9_-]*", text[index:])
        if not key_match:
            index = _advance_to_next_line(text, index)
            continue
        key = key_match.group(0)
        index += len(key)
        index = _skip_hcl_whitespace(text, index)
        if index < length and text[index] == "=":
            index += 1
            index = _skip_hcl_whitespace(text, index)
            if index < length and text[index] == "{":
                block_end = _matching_brace_index(text, index)
                result[key] = _redacted_value(_parse_hcl_mapping(text[index + 1 : block_end]))
                index = block_end + 1
                continue
            value, index = _read_hcl_scalar(text, index)
            result[key] = _redacted_value(value)
            continue
        if index < length and text[index] == "{":
            block_end = _matching_brace_index(text, index)
            result[key] = _redacted_value(_parse_hcl_mapping(text[index + 1 : block_end]))
            index = block_end + 1
            continue
        index = _advance_to_next_line(text, index)
    return result


def _skip_hcl_whitespace(text: str, index: int) -> int:
    length = len(text)
    while index < length:
        if text.startswith("//", index) or text[index] == "#":
            index = _advance_to_next_line(text, index)
            continue
        if text[index].isspace():
            index += 1
            continue
        break
    return index


def _advance_to_next_line(text: str, index: int) -> int:
    newline = text.find("\n", index)
    return len(text) if newline == -1 else newline + 1


def _matching_brace_index(text: str, open_index: int) -> int:
    depth = 0
    index = open_index
    in_string = False
    escaped = False
    while index < len(text):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
        else:
            if char == '"':
                in_string = True
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return index
        index += 1
    return len(text) - 1


def _read_hcl_scalar(text: str, index: int) -> tuple[str, int]:
    if index >= len(text):
        return "", index
    if text[index] == '"':
        index += 1
        chars: list[str] = []
        escaped = False
        while index < len(text):
            char = text[index]
            if escaped:
                chars.append(char)
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                index += 1
                break
            else:
                chars.append(char)
            index += 1
        return "".join(chars), index

    line_end = text.find("\n", index)
    if line_end == -1:
        line_end = len(text)
    value = text[index:line_end].strip()
    if "#" in value:
        value = value.split("#", 1)[0].strip()
    if "//" in value:
        value = value.split("//", 1)[0].strip()
    return value.rstrip(","), line_end + 1 if line_end < len(text) else line_end


def _redacted_value(value: object) -> object:
    if isinstance(value, dict):
        return {str(key): _redacted_value(nested) for key, nested in value.items()}
    if isinstance(value, list):
        return [_redacted_value(item) for item in value]
    if isinstance(value, str) and _looks_sensitive(value):
        return "[redacted]"
    return value


def _looks_sensitive(value: str) -> bool:
    lowered = value.lower()
    return any(token in lowered for token in ("secret", "password", "token", "private_key", "access_key"))


def _has_remote_state_data(payload: dict[str, object], text: str) -> bool:
    if DATA_REMOTE_STATE_RE.search(text):
        return True
    for data_entry in _as_list(payload.get("data")):
        if isinstance(data_entry, dict) and "terraform_remote_state" in data_entry:
            return True
    return False


def _has_any_tags(payload: dict[str, object], text: str) -> bool:
    if re.search(r"(?m)^\s*(tags|default_tags)\s*(=|\{)", text):
        return True
    return _contains_key(payload, {"tags", "default_tags"})


def _contains_key(value: object, keys: set[str]) -> bool:
    if isinstance(value, dict):
        return any(str(key) in keys or _contains_key(nested, keys) for key, nested in value.items())
    if isinstance(value, list):
        return any(_contains_key(item, keys) for item in value)
    return False


def _terraform_required_version(payload: dict[str, object], text: str) -> bool:
    if re.search(r"(?m)^\s*required_version\s*=", text):
        return True
    for terraform in _as_list(payload.get("terraform")):
        if isinstance(terraform, dict) and "required_version" in terraform:
            return True
    return False


def _required_provider_versions(payload: dict[str, object], text: str) -> set[str]:
    providers: set[str] = set()
    for terraform in _as_list(payload.get("terraform")):
        if not isinstance(terraform, dict):
            continue
        for required in _as_list(terraform.get("required_providers")):
            if not isinstance(required, dict):
                continue
            for name, body in required.items():
                if isinstance(body, dict) and body.get("version"):
                    providers.add(str(name))
    if providers:
        return providers
    required_match = re.search(r"(?ms)required_providers\s*\{", text)
    if not required_match:
        return providers
    body = _extract_block_body(text, required_match.end() - 1)
    for provider_match in re.finditer(r"(?ms)([A-Za-z0-9_-]+)\s*=\s*\{", body):
        provider_body = _extract_block_body(body, provider_match.end() - 1)
        if re.search(r"(?m)^\s*version\s*=", provider_body):
            providers.add(provider_match.group(1))
    return providers


def _hardcoded_value_findings(relative: str, text: str) -> set[str]:
    findings: set[str] = set()
    if ARN_PATTERN.search(text):
        findings.add(f"hardcoded_arn:{relative}")
    if AWS_ACCOUNT_PATTERN.search(text):
        findings.add(f"hardcoded_aws_account_id:{relative}")
    if AWS_REGION_PATTERN.search(text):
        findings.add(f"hardcoded_region:{relative}")
    return findings
