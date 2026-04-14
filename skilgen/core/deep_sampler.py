from __future__ import annotations

from pathlib import Path
from typing import Any

from skilgen.core.config import load_config
from skilgen.core.models import CorpusSettings, SkilgenConfig


def select_deep_read_targets(
    index_payload: dict[str, Any],
    *,
    project_root: str | Path | None = None,
    config: SkilgenConfig | None = None,
    total_budget: int | None = None,
) -> list[str]:
    corpus = _corpus_settings(project_root, config)
    entries = [entry for entry in index_payload.get("entries", []) if isinstance(entry, dict) and isinstance(entry.get("path"), str)]
    if not entries:
        return []

    entry_by_path = {entry["path"]: entry for entry in entries}
    clusters = {
        cluster_id: [path for path in paths if path in entry_by_path]
        for cluster_id, paths in index_payload.get("clusters", {}).items()
        if isinstance(cluster_id, str) and isinstance(paths, list)
    }
    target_budget = max(1, total_budget if total_budget is not None else corpus.budget)

    source_entries = sorted(_entries_by_category(entries, "source"), key=_sort_key)
    config_entries = sorted(_entries_by_category(entries, "config"), key=_sort_key)
    doc_entries = sorted(
        [entry for entry in entries if entry.get("category") in {"documentation", "enterprise_document"}],
        key=_sort_key,
    )

    hub_candidates = [entry["path"] for entry in source_entries]
    hub_selected = hub_candidates[: min(corpus.hub_budget, len(hub_candidates))]

    while True:
        covered_clusters = {
            entry_by_path[path].get("cluster_id")
            for path in hub_selected
            if path in entry_by_path and entry_by_path[path].get("cluster_id") is not None
        }
        mandatory_clusters = _cluster_representatives(
            clusters,
            entry_by_path,
            covered_clusters=covered_clusters,
            min_cluster_size=corpus.min_cluster_size,
        )
        reserved = min(corpus.config_budget, len(config_entries)) + min(corpus.doc_budget, len(doc_entries)) + len(mandatory_clusters)
        max_hubs = min(corpus.hub_budget, max(0, target_budget - reserved))
        if len(hub_selected) <= max_hubs:
            break
        hub_selected = hub_candidates[:max_hubs]

    covered_clusters = {
        entry_by_path[path].get("cluster_id")
        for path in hub_selected
        if path in entry_by_path and entry_by_path[path].get("cluster_id") is not None
    }
    mandatory_clusters = _cluster_representatives(
        clusters,
        entry_by_path,
        covered_clusters=covered_clusters,
        min_cluster_size=corpus.min_cluster_size,
    )
    optional_clusters = _cluster_representatives(
        clusters,
        entry_by_path,
        covered_clusters=covered_clusters,
        min_cluster_size=1,
        exclude_paths=set(mandatory_clusters),
    )

    selected: list[str] = []
    selected.extend(hub_selected)
    selected.extend(mandatory_clusters)

    optional_cluster_limit = max(0, corpus.cluster_budget - len(mandatory_clusters))
    for path in optional_clusters[:optional_cluster_limit]:
        if len(selected) >= target_budget:
            break
        selected.append(path)

    for entry in config_entries[: corpus.config_budget]:
        if len(selected) >= target_budget:
            break
        selected.append(entry["path"])
    for entry in doc_entries[: corpus.doc_budget]:
        if len(selected) >= target_budget:
            break
        selected.append(entry["path"])

    if len(selected) < target_budget:
        for entry in sorted(entries, key=_sort_key):
            path = entry["path"]
            if path in selected:
                continue
            selected.append(path)
            if len(selected) >= target_budget:
                break

    deduped: list[str] = []
    seen: set[str] = set()
    for path in selected:
        if path in seen:
            continue
        seen.add(path)
        deduped.append(path)
        if len(deduped) >= target_budget:
            break
    return deduped


def _entries_by_category(entries: list[dict[str, Any]], category: str) -> list[dict[str, Any]]:
    return [entry for entry in entries if entry.get("category") == category]


def _sort_key(entry: dict[str, Any]) -> tuple[float, str]:
    return (-float(entry.get("importance_score", 0.0) or 0.0), str(entry["path"]))


def _cluster_representatives(
    clusters: dict[str, list[str]],
    entry_by_path: dict[str, dict[str, Any]],
    *,
    covered_clusters: set[object],
    min_cluster_size: int,
    exclude_paths: set[str] | None = None,
) -> list[str]:
    excluded = exclude_paths or set()
    candidates: list[tuple[int, float, str]] = []
    for cluster_id, paths in clusters.items():
        if cluster_id in covered_clusters or len(paths) < min_cluster_size:
            continue
        ranked = sorted(
            [entry_by_path[path] for path in paths if path in entry_by_path and path not in excluded],
            key=_sort_key,
        )
        if not ranked:
            continue
        top = ranked[0]
        candidates.append((len(paths), float(top.get("importance_score", 0.0) or 0.0), top["path"]))
    candidates.sort(key=lambda item: (-item[0], -item[1], item[2]))
    return [path for _size, _score, path in candidates]


def _corpus_settings(project_root: str | Path | None, config: SkilgenConfig | None) -> CorpusSettings:
    if config is not None:
        return config.corpus
    if project_root is not None:
        return load_config(Path(project_root).resolve()).corpus
    return CorpusSettings()
