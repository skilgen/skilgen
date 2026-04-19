from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from skilgen.agents.architecture_planner import _evidence_graph_payload, _sanitize_architecture_payload
from skilgen.core.models import (
    ArchitectureBlueprint,
    ArchitectureDomain,
    DependencyRiskGraph,
    DependencyRiskNode,
    DomainGraph,
    DomainGraphNode,
    EvidenceGraph,
    EvidenceItem,
    RuntimeSignalArtifact,
    RuntimeSignals,
    SkillMaterializationPlan,
    SymbolRelationship,
)


class ArchitecturePlannerTests(unittest.TestCase):
    def test_sanitize_architecture_payload_drops_unknown_domains_and_invalid_paths(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            valid_path = root / "src" / "billing.py"
            valid_path.parent.mkdir(parents=True)
            valid_path.write_text("def run():\n    return True\n", encoding="utf-8")
            domain_graph = DomainGraph(
                nodes=[
                    DomainGraphNode(
                        name="billing",
                        summary="Billing workflows",
                        confidence=0.9,
                        key_files=["src/billing.py"],
                        key_patterns=["payments"],
                        parent_domain=None,
                        child_domains=[],
                        related_domains=["shared"],
                        skill_path="skills/billing/SKILL.md",
                    ),
                    DomainGraphNode(
                        name="shared",
                        summary="Shared infrastructure",
                        confidence=0.8,
                        key_files=["src/shared.py"],
                        key_patterns=["utils"],
                        parent_domain=None,
                        child_domains=[],
                        related_domains=["billing"],
                        skill_path="skills/shared/SKILL.md",
                    ),
                ],
                recommendations=["Keep boundaries grounded in evidence."],
            )
            native = ArchitectureBlueprint(
                headline="Native blueprint",
                system_summary="Native system summary",
                domains=[
                    ArchitectureDomain(
                        name="billing",
                        summary="Billing workflows",
                        confidence=0.9,
                        responsibilities=["Owns invoice flows"],
                        evidence_paths=["src/billing.py"],
                        related_domains=["shared"],
                        recommended_skill_path="skills/billing/SKILL.md",
                    ),
                    ArchitectureDomain(
                        name="shared",
                        summary="Shared infrastructure",
                        confidence=0.8,
                        responsibilities=["Hosts shared services"],
                        evidence_paths=["src/shared.py"],
                        related_domains=["billing"],
                        recommended_skill_path="skills/shared/SKILL.md",
                    ),
                ],
                hotspots=["low confidence"],
                recommendations=["Review boundaries"],
                materialization_plan=[
                    SkillMaterializationPlan(
                        domain="billing",
                        parent_skill_path="skills/billing/SKILL.md",
                        child_skill_paths=["skills/billing/api/SKILL.md"],
                        cross_links=["skills/shared/SKILL.md"],
                        decision="split",
                        rationale="Native rationale",
                    ),
                    SkillMaterializationPlan(
                        domain="shared",
                        parent_skill_path="skills/shared/SKILL.md",
                        child_skill_paths=[],
                        cross_links=["skills/billing/SKILL.md"],
                        decision="keep",
                        rationale="Shared rationale",
                    ),
                ],
            )

            payload = {
                "headline": "Proposed blueprint",
                "domains": [
                    {
                        "name": "billing",
                        "summary": "Updated billing summary",
                        "responsibilities": ["Owns invoices"],
                        "evidence_paths": ["src/billing.py", "../secrets.env"],
                        "related_domains": ["shared", "unknown"],
                        "recommended_skill_path": "skills/other/SKILL.md",
                    },
                    {
                        "name": "rogue",
                        "summary": "Should be ignored",
                        "evidence_paths": ["etc/passwd"],
                    },
                ],
                "materialization_plan": [
                    {
                        "domain": "billing",
                        "decision": "explode",
                        "child_skill_paths": ["skills/billing/api/SKILL.md", "skills/rogue/SKILL.md"],
                        "cross_links": ["skills/shared/SKILL.md", "skills/rogue/SKILL.md"],
                        "rationale": "Custom rationale",
                    }
                ],
            }

            sanitized = _sanitize_architecture_payload(root, domain_graph, native, payload)

            self.assertEqual([domain.name for domain in sanitized.domains], ["billing", "shared"])
            self.assertEqual(sanitized.domains[0].summary, "Updated billing summary")
            self.assertEqual(sanitized.domains[0].evidence_paths, ["src/billing.py"])
            self.assertEqual(sanitized.domains[0].related_domains, ["shared"])
            self.assertEqual(sanitized.domains[0].recommended_skill_path, "skills/billing/SKILL.md")
            self.assertEqual(sanitized.materialization_plan[0].decision, "split")
            self.assertEqual(sanitized.materialization_plan[0].child_skill_paths, ["skills/billing/api/SKILL.md"])
            self.assertEqual(sanitized.materialization_plan[0].cross_links, ["skills/shared/SKILL.md"])

    def test_sanitize_architecture_payload_falls_back_to_native_for_empty_input(self) -> None:
        domain_graph = DomainGraph(
            nodes=[
                DomainGraphNode(
                    name="backend",
                    summary="Backend services",
                    confidence=0.8,
                    key_files=["api/server.py"],
                    key_patterns=["http"],
                    parent_domain=None,
                    child_domains=[],
                    related_domains=[],
                    skill_path="skills/backend/SKILL.md",
                )
            ],
            recommendations=[],
        )
        native = ArchitectureBlueprint(
            headline="Native headline",
            system_summary="Native summary",
            domains=[
                ArchitectureDomain(
                    name="backend",
                    summary="Backend services",
                    confidence=0.8,
                    responsibilities=["Serve requests"],
                    evidence_paths=["api/server.py"],
                    related_domains=[],
                    recommended_skill_path="skills/backend/SKILL.md",
                )
            ],
            hotspots=["watch timeouts"],
            recommendations=["Keep it simple"],
            materialization_plan=[
                SkillMaterializationPlan(
                    domain="backend",
                    parent_skill_path="skills/backend/SKILL.md",
                    child_skill_paths=[],
                    cross_links=[],
                    decision="keep",
                    rationale="Native rationale",
                )
            ],
        )

        sanitized = _sanitize_architecture_payload(Path.cwd(), domain_graph, native, {})
        self.assertEqual(sanitized, native)

    def test_evidence_graph_payload_redacts_config_snippets_and_secret_markers(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "skilgen.yml").write_text("model_redaction_mode: balanced\n", encoding="utf-8")
            evidence_graph = EvidenceGraph(
                language_inventory={"python": 1},
                dominant_languages=["python"],
                import_graph={"src/app.py": ["os"]},
                items=[
                    EvidenceItem(
                        path="config/.env",
                        kind="config",
                        language=None,
                        tags=["config"],
                        snippet=["API_KEY=secret-value", "TOKEN=demo"],
                    ),
                    EvidenceItem(
                        path="src/app.py",
                        kind="code",
                        language="python",
                        tags=["backend"],
                        snippet=["api_key = 'secret-value'", "token = 'demo-token'"],
                    ),
                ],
                recommendations=["Review config boundaries."],
                symbol_relationships=[
                    SymbolRelationship(
                        source_path="src/app.py",
                        source_symbol="BillingService",
                        relationship="extends",
                        target_symbol="BaseService",
                        target_path="src/base.py",
                        confidence=0.95,
                    )
                ],
                runtime_signals=RuntimeSignals(
                    artifacts=[
                        RuntimeSignalArtifact(
                            path="reports/coverage.xml",
                            kind="coverage",
                            format="coverage-xml",
                            signal_count=1,
                            related_paths=["src/app.py"],
                            summary="Coverage data for 1 files",
                        )
                    ],
                    coverage_by_path={"src/app.py": 0.5},
                ),
                dependency_risk_graph=DependencyRiskGraph(
                    nodes=[
                        DependencyRiskNode(
                            id="src/app.py",
                            kind="source-file",
                            risk_score=0.3,
                            signals=["fanout:high"],
                            dependencies=["src/base.py"],
                        )
                    ]
                ),
            )

            payload = _evidence_graph_payload(root, evidence_graph)

            self.assertEqual(payload["items"][0]["snippet"], [])
            self.assertTrue(payload["items"][1]["snippet"])
            self.assertIn("[redacted]", " ".join(payload["items"][1]["snippet"]))
            self.assertEqual(payload["symbol_relationships"][0]["relationship"], "extends")
            self.assertEqual(payload["runtime_signals"]["artifacts"][0]["kind"], "coverage")
            self.assertEqual(payload["dependency_risk_graph"]["nodes"][0]["id"], "src/app.py")


if __name__ == "__main__":
    unittest.main()
