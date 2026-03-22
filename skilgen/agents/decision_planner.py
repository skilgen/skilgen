from __future__ import annotations

from pathlib import Path

from skilgen.deep_agents_core import run_deep_json
from skilgen.core.freshness import compute_freshness_report, load_freshness_state
from skilgen.core.models import AgentDecision, RequirementsContext, RunMemory
from skilgen.core.run_memory import load_current_run_memory
from skilgen.external_skills import external_skill_policy, ranked_external_skills


def build_agent_decision_native(
    project_root: Path,
    requirements: RequirementsContext,
    domain_graph,
    skill_tree,
    current_run_memory: RunMemory | None,
) -> AgentDecision:
    freshness = compute_freshness_report(project_root, requirements, domain_graph, load_freshness_state(project_root))
    top_level_skill_paths = [
        node.path
        for node in skill_tree
        if node.parent_skill is None and (not freshness.impacted_domains or node.domain in freshness.impacted_domains)
    ]
    if not top_level_skill_paths:
        top_level_skill_paths = [node.path for node in skill_tree if node.parent_skill is None]
    ranked_external = ranked_external_skills(project_root).get("skills", [])
    memory_to_load = [".skilgen/memory/current_run.json", ".skilgen/state/freshness.json", ".skilgen/external-skills/lock.json"]
    preferred_external: list[str] = []
    if current_run_memory is not None:
        memory_to_load.append(f".skilgen/memory/runs/{current_run_memory.run_id}.json")
    for entry in ranked_external[:3]:
        preferred_external.append(str(entry.get("slug", "")))
        normalized = entry.get("lock_metadata", {}).get("normalized", {}) if isinstance(entry.get("lock_metadata"), dict) else {}
        summary_path = normalized.get("summary_path")
        index_path = normalized.get("index_path")
        if isinstance(summary_path, str):
            try:
                relative = Path(summary_path).resolve().relative_to(project_root).as_posix()
            except ValueError:
                relative = summary_path
            memory_to_load.append(relative)
            if relative not in top_level_skill_paths:
                top_level_skill_paths.append(relative)
        if isinstance(index_path, str):
            try:
                relative_index = Path(index_path).resolve().relative_to(project_root).as_posix()
            except ValueError:
                relative_index = index_path
            memory_to_load.append(relative_index)
    should_refresh = freshness.reason != "no_source_changes"
    reason = (
        "Source changes were detected and the impacted domains should be refreshed before the next coding task."
        if should_refresh
        else "No source changes were detected, so agents can reuse the current skill tree and run memory."
    )
    next_actions = []
    if should_refresh:
        next_actions.append("Refresh the impacted top-level skills before starting implementation work.")
    next_actions.append("Load AGENTS.md and the prioritized parent skills first.")
    if ranked_external:
        next_actions.append(
            f"Load the top ranked external skill packs first: {', '.join(slug for slug in preferred_external if slug) or 'external summaries'}."
        )
        next_actions.append("Use each external pack's normalized index and summary before loading lower-ranked imports.")
    if current_run_memory is not None and current_run_memory.recent_events:
        next_actions.append("Use the latest run memory to continue from the most recent execution context.")
    return AgentDecision(
        should_refresh=should_refresh,
        reason=reason,
        prioritized_domains=freshness.impacted_domains or freshness.top_level_domains,
        prioritized_skill_paths=top_level_skill_paths,
        memory_to_load=memory_to_load,
        next_actions=next_actions,
    )


def build_agent_decision(
    project_root: Path,
    requirements: RequirementsContext,
    domain_graph,
    skill_tree,
) -> AgentDecision:
    root = project_root.resolve()
    current_run_memory = load_current_run_memory(root)
    native = build_agent_decision_native(root, requirements, domain_graph, skill_tree, current_run_memory)
    freshness = compute_freshness_report(root, requirements, domain_graph, load_freshness_state(root))
    policy = external_skill_policy(root)
    ranked = ranked_external_skills(root)
    payload = run_deep_json(
        "agent decision planning",
        (
            "Decide whether Skilgen should refresh skills now, which domains and skills an agent should prioritize, "
            "and which memory files an agent should load first. Return JSON with keys should_refresh, reason, "
            "prioritized_domains, prioritized_skill_paths, memory_to_load, next_actions. Optimize for agent usefulness: "
            "favor the smallest refresh that preserves correctness, choose skills that match the currently impacted "
            "domains, rank trusted external skill packs when they fit the repo, and keep memory recommendations focused on the files most likely to help the next coding step.\n\n"
            f"Project root: {root}\n"
            f"Freshness JSON: {freshness.__dict__}\n"
            f"External skills policy JSON: {policy}\n"
            f"Ranked external skills JSON: {ranked}\n"
            f"Current run memory: {current_run_memory.__dict__ if current_run_memory is not None else None}\n"
            f"Skill tree JSON: {[node.__dict__ for node in skill_tree]}\n"
            f"Native decision JSON: {native.__dict__}\n"
        ),
        lambda: native.__dict__,
        project_root=root,
    )
    return AgentDecision(
        should_refresh=bool(payload.get("should_refresh", native.should_refresh)),
        reason=str(payload.get("reason", native.reason)),
        prioritized_domains=[str(item) for item in payload.get("prioritized_domains", native.prioritized_domains)],
        prioritized_skill_paths=[str(item) for item in payload.get("prioritized_skill_paths", native.prioritized_skill_paths)],
        memory_to_load=[str(item) for item in payload.get("memory_to_load", native.memory_to_load)],
        next_actions=[str(item) for item in payload.get("next_actions", native.next_actions)],
    )
