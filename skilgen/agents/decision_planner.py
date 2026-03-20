from __future__ import annotations

from pathlib import Path

from skilgen.deep_agents_core import run_deep_json
from skilgen.core.freshness import compute_freshness_report, load_freshness_state
from skilgen.core.models import AgentDecision, RequirementsContext, RunMemory
from skilgen.core.project_memory import load_project_memory
from skilgen.core.run_memory import load_current_run_memory


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
    memory_to_load = [".skilgen/memory/project_memory.json", ".skilgen/memory/current_run.json", ".skilgen/state/freshness.json"]
    project_memory = load_project_memory(project_root)
    if project_memory is not None and project_memory.memory_files:
        memory_to_load = list(dict.fromkeys([*project_memory.memory_files, *memory_to_load]))
    if current_run_memory is not None:
        memory_to_load.append(f".skilgen/memory/runs/{current_run_memory.run_id}.json")
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
    payload = run_deep_json(
        "agent decision planning",
        (
            "Decide whether Skilgen should refresh skills now, which domains and skills an agent should prioritize, "
            "and which memory files an agent should load first. Return JSON with keys should_refresh, reason, "
            "prioritized_domains, prioritized_skill_paths, memory_to_load, next_actions. Optimize for agent usefulness: "
            "favor the smallest refresh that preserves correctness, choose skills that match the currently impacted "
            "domains, and keep memory recommendations focused on the files most likely to help the next coding step.\n\n"
            f"Project root: {root}\n"
            f"Freshness JSON: {freshness.__dict__}\n"
            f"Current run memory: {current_run_memory.__dict__ if current_run_memory is not None else None}\n"
            f"Skill tree JSON: {[node.__dict__ for node in skill_tree]}\n"
            f"Native decision JSON: {native.__dict__}\n"
        ),
        lambda: native.__dict__,
    )
    return AgentDecision(
        should_refresh=bool(payload.get("should_refresh", native.should_refresh)),
        reason=str(payload.get("reason", native.reason)),
        prioritized_domains=[str(item) for item in payload.get("prioritized_domains", native.prioritized_domains)],
        prioritized_skill_paths=[str(item) for item in payload.get("prioritized_skill_paths", native.prioritized_skill_paths)],
        memory_to_load=[str(item) for item in payload.get("memory_to_load", native.memory_to_load)],
        next_actions=[str(item) for item in payload.get("next_actions", native.next_actions)],
    )
