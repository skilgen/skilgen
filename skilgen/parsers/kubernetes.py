"""Parse Kubernetes YAML manifests without exposing secret values."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


WORKLOAD_KINDS = {"Deployment", "StatefulSet", "DaemonSet", "ReplicaSet", "Job", "CronJob", "Pod"}
RBAC_KINDS = {"Role", "ClusterRole", "RoleBinding", "ClusterRoleBinding", "ServiceAccount"}
SENSITIVE_KEY_TOKENS = ("password", "passwd", "secret", "token", "api_key", "apikey", "private_key")


class KubernetesParserError(ValueError):
    """Raised when Kubernetes manifests cannot be parsed."""


@dataclass(frozen=True)
class KubernetesObjectSummary:
    """A Kubernetes object summary with metadata and safe details only."""

    kind: str
    name: str
    namespace: str | None
    file: str
    details: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class KubernetesManifestParseResult:
    """Kubernetes manifest evidence extracted from YAML documents."""

    root: str
    files: list[str]
    counts_by_kind: dict[str, int]
    objects: list[KubernetesObjectSummary] = field(default_factory=list)
    deployments: list[KubernetesObjectSummary] = field(default_factory=list)
    services: list[KubernetesObjectSummary] = field(default_factory=list)
    configmaps: list[KubernetesObjectSummary] = field(default_factory=list)
    secrets: list[KubernetesObjectSummary] = field(default_factory=list)
    ingress: list[KubernetesObjectSummary] = field(default_factory=list)
    rbac: list[KubernetesObjectSummary] = field(default_factory=list)
    patterns: list[str] = field(default_factory=list)
    anti_patterns: list[str] = field(default_factory=list)


def parse_kubernetes_manifests(path: str | Path) -> KubernetesManifestParseResult:
    """Parse Kubernetes manifest files from a file or directory."""

    root = Path(path).resolve()
    if not root.exists():
        raise KubernetesParserError(f"Kubernetes parser expected an existing path: {root}")

    files = _manifest_files(root)
    objects: list[KubernetesObjectSummary] = []
    patterns: set[str] = set()
    anti_patterns: set[str] = set()

    for file_path in files:
        documents = _load_yaml_documents(file_path)
        relative = file_path.relative_to(root if root.is_dir() else root.parent).as_posix()
        for document in documents:
            if not isinstance(document, dict):
                continue
            summary = _summarize_object(document, relative)
            if summary is None:
                continue
            objects.append(summary)
            _collect_patterns(document, summary, patterns, anti_patterns)

    counts = Counter(obj.kind for obj in objects)
    return KubernetesManifestParseResult(
        root=root.as_posix(),
        files=[path.relative_to(root if root.is_dir() else root.parent).as_posix() for path in files],
        counts_by_kind=dict(sorted(counts.items())),
        objects=objects,
        deployments=[obj for obj in objects if obj.kind == "Deployment"],
        services=[obj for obj in objects if obj.kind == "Service"],
        configmaps=[obj for obj in objects if obj.kind == "ConfigMap"],
        secrets=[obj for obj in objects if obj.kind == "Secret"],
        ingress=[obj for obj in objects if obj.kind == "Ingress"],
        rbac=[obj for obj in objects if obj.kind in RBAC_KINDS],
        patterns=sorted(patterns),
        anti_patterns=sorted(anti_patterns),
    )


def _manifest_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root] if root.suffix.lower() in {".yaml", ".yml"} else []
    candidate_roots = _candidate_manifest_roots(root)
    files: set[Path] = set()
    for candidate_root in candidate_roots:
        files.update(
            path
            for path in candidate_root.rglob("*")
            if path.is_file()
            and path.suffix.lower() in {".yaml", ".yml"}
            and not _is_within_helm_chart(path)
            and _looks_like_kubernetes_manifest(path)
        )
    return sorted(files)


def _candidate_manifest_roots(root: Path) -> list[Path]:
    named_roots = sorted(
        {
            path
            for path in root.rglob("*")
            if path.is_dir() and path.name.lower() in {"k8s", "kubernetes", "manifests", "deploy", "deployment"}
        }
    )
    if named_roots:
        return named_roots
    return [root]


def _is_within_helm_chart(path: Path) -> bool:
    for parent in [path.parent, *path.parents]:
        if (parent / "Chart.yaml").is_file():
            return True
    return False


def _looks_like_kubernetes_manifest(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return False
    return "apiVersion:" in text and "kind:" in text


def _load_yaml_documents(path: Path) -> list[object]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise KubernetesParserError(f"Kubernetes parser could not read {path}: {exc}") from exc
    if not text.strip():
        return []
    try:
        return list(yaml.safe_load_all(text))
    except yaml.YAMLError as exc:
        raise KubernetesParserError(f"Kubernetes parser failed to parse {path}: {exc}") from exc


def _summarize_object(document: dict[str, Any], relative: str) -> KubernetesObjectSummary | None:
    kind = str(document.get("kind") or "").strip()
    if not kind:
        return None
    metadata = document.get("metadata")
    metadata = metadata if isinstance(metadata, dict) else {}
    name = str(metadata.get("name") or "<unnamed>")
    namespace = metadata.get("namespace")
    details: dict[str, object] = {"apiVersion": document.get("apiVersion")}
    if kind in WORKLOAD_KINDS:
        details.update(_workload_details(document))
    elif kind == "Service":
        spec = document.get("spec") if isinstance(document.get("spec"), dict) else {}
        details["type"] = spec.get("type", "ClusterIP")
        details["ports"] = [_safe_port(port) for port in spec.get("ports", []) if isinstance(port, dict)]
    elif kind == "ConfigMap":
        details["keys"] = sorted(_data_keys(document))
    elif kind == "Secret":
        details["type"] = document.get("type")
        details["keys"] = sorted(_data_keys(document))
    elif kind == "Ingress":
        spec = document.get("spec") if isinstance(document.get("spec"), dict) else {}
        details["hosts"] = sorted(_ingress_hosts(spec))
    elif kind in RBAC_KINDS:
        details["rbac_kind"] = kind
    return KubernetesObjectSummary(
        kind=kind,
        name=name,
        namespace=str(namespace) if namespace else None,
        file=relative,
        details=details,
    )


def _safe_port(port: dict[str, Any]) -> dict[str, object]:
    return {key: value for key, value in port.items() if key in {"name", "port", "targetPort", "protocol"}}


def _data_keys(document: dict[str, Any]) -> set[str]:
    keys: set[str] = set()
    for field in ("data", "binaryData", "stringData"):
        value = document.get(field)
        if isinstance(value, dict):
            keys.update(str(key) for key in value)
    return keys


def _ingress_hosts(spec: dict[str, Any]) -> set[str]:
    hosts: set[str] = set()
    for rule in spec.get("rules", []):
        if isinstance(rule, dict) and rule.get("host"):
            hosts.add(str(rule["host"]))
    return hosts


def _workload_details(document: dict[str, Any]) -> dict[str, object]:
    containers = _containers(document)
    return {
        "containers": [
            {
                "name": str(container.get("name") or "<unnamed>"),
                "image": str(container.get("image") or ""),
            }
            for container in containers
        ],
        "container_count": len(containers),
    }


def _collect_patterns(
    document: dict[str, Any],
    summary: KubernetesObjectSummary,
    patterns: set[str],
    anti_patterns: set[str],
) -> None:
    if summary.kind in WORKLOAD_KINDS:
        containers = _containers(document)
        if containers and all(_has_resource_limits(container) for container in containers):
            patterns.add("resource_limits")
        for container in containers:
            container_name = str(container.get("name") or "<unnamed>")
            if not _has_resource_limits(container):
                anti_patterns.add(f"missing_resource_limits:{summary.kind}/{summary.name}:{container_name}")
            image = str(container.get("image") or "")
            if _uses_latest_image(image):
                anti_patterns.add(f"latest_image_tag:{summary.kind}/{summary.name}:{container_name}")
            if _has_probe(container):
                patterns.add("health_probes")
            if _is_privileged(container):
                anti_patterns.add(f"privileged_container:{summary.kind}/{summary.name}:{container_name}")
        if _runs_non_root(document):
            patterns.add("non_root_containers")
    if summary.kind == "ConfigMap":
        for key in summary.details.get("keys", []):
            if _looks_sensitive_key(str(key)):
                anti_patterns.add(f"configmap_secret_key:{summary.name}:{key}")


def _containers(document: dict[str, Any]) -> list[dict[str, Any]]:
    pod_spec = _pod_spec(document)
    containers: list[dict[str, Any]] = []
    for field in ("initContainers", "containers"):
        value = pod_spec.get(field)
        if isinstance(value, list):
            containers.extend(item for item in value if isinstance(item, dict))
    return containers


def _pod_spec(document: dict[str, Any]) -> dict[str, Any]:
    kind = document.get("kind")
    spec = document.get("spec") if isinstance(document.get("spec"), dict) else {}
    if kind == "Pod":
        return spec
    if kind == "CronJob":
        template = (
            spec.get("jobTemplate", {})
            .get("spec", {})
            .get("template", {})
            if isinstance(spec.get("jobTemplate"), dict)
            else {}
        )
        return template.get("spec", {}) if isinstance(template, dict) and isinstance(template.get("spec"), dict) else {}
    template = spec.get("template") if isinstance(spec.get("template"), dict) else {}
    return template.get("spec", {}) if isinstance(template.get("spec"), dict) else {}


def _has_resource_limits(container: dict[str, Any]) -> bool:
    resources = container.get("resources") if isinstance(container.get("resources"), dict) else {}
    limits = resources.get("limits") if isinstance(resources.get("limits"), dict) else {}
    return bool(limits.get("cpu") and limits.get("memory"))


def _uses_latest_image(image: str) -> bool:
    if not image:
        return False
    image_without_digest = image.split("@", 1)[0]
    last_segment = image_without_digest.rsplit("/", 1)[-1]
    return ":" not in last_segment or last_segment.endswith(":latest")


def _has_probe(container: dict[str, Any]) -> bool:
    return bool(container.get("livenessProbe") or container.get("readinessProbe") or container.get("startupProbe"))


def _is_privileged(container: dict[str, Any]) -> bool:
    security_context = container.get("securityContext")
    return isinstance(security_context, dict) and security_context.get("privileged") is True


def _runs_non_root(document: dict[str, Any]) -> bool:
    pod_security = _pod_spec(document).get("securityContext")
    if isinstance(pod_security, dict) and (pod_security.get("runAsNonRoot") is True or _nonzero_user(pod_security)):
        return True
    return any(_container_runs_non_root(container) for container in _containers(document))


def _container_runs_non_root(container: dict[str, Any]) -> bool:
    security_context = container.get("securityContext")
    return isinstance(security_context, dict) and (
        security_context.get("runAsNonRoot") is True or _nonzero_user(security_context)
    )


def _nonzero_user(security_context: dict[str, Any]) -> bool:
    run_as_user = security_context.get("runAsUser")
    return isinstance(run_as_user, int) and run_as_user > 0


def _looks_sensitive_key(key: str) -> bool:
    lowered = key.lower()
    return any(token in lowered for token in SENSITIVE_KEY_TOKENS)
