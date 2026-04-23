# Analysis

```json
{
  "framework_fingerprint": {
    "frontend": {
      "name": "nextjs",
      "confidence": 0.99,
      "evidence": [
        "next.config",
        "app/",
        "pages/"
      ]
    },
    "backend": {
      "name": "fastapi",
      "confidence": 0.99,
      "evidence": [
        "fastapi",
        "main.py",
        "pyproject.toml"
      ]
    },
    "test_framework": {
      "name": "unittest",
      "confidence": 0.8500000000000001,
      "evidence": [
        "test_",
        "unittest"
      ]
    },
    "build_tool": {
      "name": "setuptools",
      "confidence": 0.65,
      "evidence": [
        "pyproject.toml"
      ]
    }
  },
  "signals": {
    "backend_routes": [
      "skilgen/api/__init__.py",
      "skilgen/api/jobs.py",
      "skilgen/api/server.py",
      "skilgen/api/service.py"
    ],
    "frontend_routes": [],
    "components": [],
    "services": [
      "skilgen/api/service.py"
    ],
    "tests": [
      "tests/__init__.py",
      "tests/oidc_test_utils.py",
      "tests/test_analytics.py",
      "tests/test_api_smoke.py",
      "tests/test_architecture_cli.py",
      "tests/test_architecture_planner.py",
      "tests/test_audit.py",
      "tests/test_auth_claim_mapping.py",
      "tests/test_auth_tokens.py",
      "tests/test_autoupdate.py",
      "tests/test_cli.py",
      "tests/test_codebase_signals.py",
      "tests/test_config.py",
      "tests/test_context.py",
      "tests/test_corpus_cli.py",
      "tests/test_corpus_index.py",
      "tests/test_dashboard_cli.py",
      "tests/test_decision_planner.py",
      "tests/test_delivery.py",
      "tests/test_dependency_risk.py",
      "tests/test_dependency_risk_graph_workstream.py",
      "tests/test_diff.py",
      "tests/test_document_ingestion.py",
      "tests/test_domain_graph_planner.py",
      "tests/test_enterprise_document_formats.py",
      "tests/test_enterprise_policy_cli.py",
      "tests/test_feature_extractor.py",
      "tests/test_framework_fingerprint.py",
      "tests/test_identity_policy_store.py",
      "tests/test_jobs.py",
      "tests/test_model_registry.py",
      "tests/test_org_settings.py",
      "tests/test_overview_data.py",
      "tests/test_packaging.py",
      "tests/test_plan_cli.py",
      "tests/test_pr_comment.py",
      "tests/test_pr_comment_dedup.py",
      "tests/test_rate_limit_store.py",
      "tests/test_registry_api.py",
      "tests/test_registry_cli.py",
      "tests/test_registry_dashboard.py",
      "tests/test_relationship_mapper.py",
      "tests/test_repos_screen.py",
      "tests/test_requirements.py",
      "tests/test_requirements_parser.py",
      "tests/test_roadmap_planner.py",
      "tests/test_roadmap_skills.py",
      "tests/test_run_memory.py",
      "tests/test_runtime_hardening.py",
      "tests/test_runtime_signals.py",
      "tests/test_score.py",
      "tests/test_score_quality_system.py",
      "tests/test_sdk.py",
      "tests/test_skill_detail.py",
      "tests/test_skill_usage_analytics.py",
      "tests/test_skillayer_api_infra.py",
      "tests/test_source_graphs.py",
      "tests/test_stripe_portal.py",
      "tests/test_stripe_webhook.py",
      "tests/test_upgrade_flow.py",
      "tests/test_validate_cli.py",
      "tests/test_vercel_api_deploy.py",
      "tests/test_vercel_dashboard_deploy.py",
      "tests/test_workspace_graph.py"
    ],
    "data_models": [],
    "persistence_layers": [],
    "background_jobs": [
      "skilgen/api/jobs.py",
      "tests/test_jobs.py"
    ],
    "auth_files": [
      "skilgen/core/auth_tokens.py",
      "tests/test_auth_claim_mapping.py",
      "tests/test_auth_tokens.py"
    ],
    "state_files": [],
    "design_system_files": [],
    "legacy_programs": [],
    "copybooks": [],
    "language_inventory": {
      "python": 128
    }
  },
  "repo_archetype": "skilgen-platform",
  "workspace_graph": {
    "tool": "turbo",
    "packages": [
      {
        "id": "apps-dashboard",
        "name": "skillayer-dashboard",
        "root_path": "apps/dashboard",
        "package_type": null,
        "manifest_paths": [
          "apps/dashboard/package.json"
        ],
        "config_evidence": [
          "apps/dashboard/package.json",
          "turbo.json"
        ]
      },
      {
        "id": "apps-web",
        "name": "skillayer-web",
        "root_path": "apps/web",
        "package_type": "app",
        "manifest_paths": [
          "apps/web/package.json"
        ],
        "config_evidence": [
          "apps/web/package.json",
          "turbo.json"
        ]
      },
      {
        "id": "packages-config",
        "name": "@skillayer/config",
        "root_path": "packages/config",
        "package_type": "library",
        "manifest_paths": [
          "packages/config/package.json"
        ],
        "config_evidence": [
          "packages/config/package.json",
          "turbo.json"
        ]
      },
      {
        "id": "packages-db",
        "name": "@skillayer/db",
        "root_path": "packages/db",
        "package_type": "library",
        "manifest_paths": [
          "packages/db/package.json"
        ],
        "config_evidence": [
          "packages/db/package.json",
          "turbo.json"
        ]
      },
      {
        "id": "packages-types",
        "name": "@skillayer/types",
        "root_path": "packages/types",
        "package_type": "library",
        "manifest_paths": [
          "packages/types/package.json"
        ],
        "config_evidence": [
          "packages/types/package.json",
          "turbo.json"
        ]
      },
      {
        "id": "packages-ui",
        "name": "@skillayer/ui",
        "root_path": "packages/ui",
        "package_type": "library",
        "manifest_paths": [
          "packages/ui/package.json"
        ],
        "config_evidence": [
          "packages/ui/package.json",
          "turbo.json"
        ]
      }
    ],
    "dependencies": [
      {
        "source": "apps-dashboard",
        "target": "packages-config",
        "evidence": [
          "apps/dashboard/package.json:@skillayer/config"
        ]
      },
      {
        "source": "apps-dashboard",
        "target": "packages-types",
        "evidence": [
          "apps/dashboard/package.json:@skillayer/types"
        ]
      },
      {
        "source": "apps-dashboard",
        "target": "packages-ui",
        "evidence": [
          "apps/dashboard/package.json:@skillayer/ui"
        ]
      },
      {
        "source": "apps-web",
        "target": "packages-config",
        "evidence": [
          "apps/web/package.json:@skillayer/config"
        ]
      },
      {
        "source": "apps-web",
        "target": "packages-types",
        "evidence": [
          "apps/web/package.json:@skillayer/types"
        ]
      },
      {
        "source": "apps-web",
        "target": "packages-ui",
        "evidence": [
          "apps/web/package.json:@skillayer/ui"
        ]
      },
      {
        "source": "packages-types",
        "target": "packages-config",
        "evidence": [
          "packages/types/package.json:@skillayer/config"
        ]
      },
      {
        "source": "packages-ui",
        "target": "packages-config",
        "evidence": [
          "packages/ui/package.json:@skillayer/config"
        ]
      }
    ],
    "entrypoints": [
      "apps-dashboard",
      "apps-web"
    ],
    "confidence": 0.92,
    "detection_evidence": [
      "turbo.json"
    ]
  },
  "domain_graph": {
    "nodes": [
      {
        "name": "platform",
        "summary": "Tooling and runtime domain covering Skilgen's internal engine, CLI, planners, generators, and maintenance scripts.",
        "confidence": 0.9,
        "key_files": [
          "skilgen/__init__.py",
          "skilgen/autoupdate.py",
          "skilgen/agents/__init__.py",
          "skilgen/agents/architecture_planner.py",
          "skilgen/cli/__init__.py",
          "skilgen/cli/main.py",
          "skilgen/core/__init__.py",
          "skilgen/core/analytics.py"
        ],
        "key_patterns": [
          "tooling platform",
          "generation engine",
          "repo-local operating surface"
        ],
        "parent_domain": null,
        "child_domains": [
          "platform-runtime",
          "platform-agents",
          "platform-cli",
          "platform-core",
          "platform-generators",
          "platform-scripts"
        ],
        "related_domains": [
          "requirements",
          "backend",
          "roadmap",
          "frontend"
        ],
        "skill_path": "skills/platform/SKILL.md"
      },
      {
        "name": "platform-runtime",
        "summary": "Runtime orchestration guidance for package-level entrypoints, delivery orchestration, and repo-wide integration surfaces.",
        "confidence": 0.84,
        "key_files": [
          "skilgen/__init__.py",
          "skilgen/autoupdate.py",
          "skilgen/deep_agents_core.py",
          "skilgen/deep_agents_runtime.py",
          "skilgen/delivery.py",
          "setup.py"
        ],
        "key_patterns": [
          "runtime orchestration",
          "repo-wide coordination",
          "package entrypoints"
        ],
        "parent_domain": "platform",
        "child_domains": [],
        "related_domains": [
          "requirements",
          "roadmap",
          "backend"
        ],
        "skill_path": "skills/platform/runtime/SKILL.md"
      },
      {
        "name": "platform-agents",
        "summary": "Planner and inference guidance for domain graphing, architecture synthesis, and decision intelligence.",
        "confidence": 0.84,
        "key_files": [
          "skilgen/agents/__init__.py",
          "skilgen/agents/architecture_planner.py",
          "skilgen/agents/codebase_signals.py",
          "skilgen/agents/decision_planner.py",
          "skilgen/agents/domain_graph_planner.py",
          "skilgen/agents/evidence_graph.py"
        ],
        "key_patterns": [
          "domain inference",
          "architecture synthesis",
          "agent planning logic"
        ],
        "parent_domain": "platform",
        "child_domains": [],
        "related_domains": [
          "requirements",
          "roadmap",
          "backend"
        ],
        "skill_path": "skills/platform/agents/SKILL.md"
      },
      {
        "name": "platform-cli",
        "summary": "Operator-facing CLI guidance for command surfaces, progress reporting, and repo-local execution flows.",
        "confidence": 0.84,
        "key_files": [
          "skilgen/cli/__init__.py",
          "skilgen/cli/main.py"
        ],
        "key_patterns": [
          "command surfaces",
          "operator UX",
          "progress orchestration"
        ],
        "parent_domain": "platform",
        "child_domains": [],
        "related_domains": [
          "requirements",
          "roadmap",
          "backend"
        ],
        "skill_path": "skills/platform/cli/SKILL.md"
      },
      {
        "name": "platform-core",
        "summary": "Shared core guidance for scoring, freshness, diffing, context loading, and validation primitives.",
        "confidence": 0.84,
        "key_files": [
          "skilgen/core/__init__.py",
          "skilgen/core/analytics.py",
          "skilgen/core/audit.py",
          "skilgen/core/auth_tokens.py",
          "skilgen/core/config.py",
          "skilgen/core/context.py"
        ],
        "key_patterns": [
          "shared models",
          "freshness and scoring",
          "validation primitives"
        ],
        "parent_domain": "platform",
        "child_domains": [],
        "related_domains": [
          "requirements",
          "roadmap",
          "backend"
        ],
        "skill_path": "skills/platform/core/SKILL.md"
      },
      {
        "name": "platform-generators",
        "summary": "Artifact materialization guidance for docs, skills, dashboards, and output rendering flows.",
        "confidence": 0.84,
        "key_files": [
          "skilgen/generators/__init__.py",
          "skilgen/generators/package.py",
          "skilgen/generators/skills.py"
        ],
        "key_patterns": [
          "artifact rendering",
          "materialization flow",
          "repo-local outputs"
        ],
        "parent_domain": "platform",
        "child_domains": [],
        "related_domains": [
          "requirements",
          "roadmap",
          "backend"
        ],
        "skill_path": "skills/platform/generators/SKILL.md"
      },
      {
        "name": "platform-scripts",
        "summary": "Maintenance automation guidance for release helpers and repo scripts that support the generation pipeline.",
        "confidence": 0.84,
        "key_files": [
          "scripts/bump_version.py",
          "scripts/deploy_api.py",
          "scripts/deploy_dashboard.py",
          "scripts/run_requirements_pipeline.py"
        ],
        "key_patterns": [
          "maintenance automation",
          "release helpers",
          "pipeline scripts"
        ],
        "parent_domain": "platform",
        "child_domains": [],
        "related_domains": [
          "requirements",
          "roadmap",
          "backend"
        ],
        "skill_path": "skills/platform/scripts/SKILL.md"
      },
      {
        "name": "roadmap",
        "summary": "Delivery sequencing domain that keeps phases, next steps, and implementation order explicit for agents.",
        "confidence": 0.84,
        "key_files": [
          "skills/roadmap/SKILL.md",
          "REPORT.md"
        ],
        "key_patterns": [
          "phase-based delivery",
          "sequenced implementation planning",
          "traceable next steps"
        ],
        "parent_domain": null,
        "child_domains": [
          "roadmap-phase-0",
          "roadmap-phase-1",
          "roadmap-phase-2",
          "roadmap-phase-3"
        ],
        "related_domains": [
          "requirements",
          "backend",
          "frontend"
        ],
        "skill_path": "skills/roadmap/SKILL.md"
      },
      {
        "name": "roadmap-phase-0",
        "summary": "Roadmap phase node for phase-0 planning and sequencing guidance.",
        "confidence": 0.72,
        "key_files": [
          "skills/roadmap/SKILL.md"
        ],
        "key_patterns": [
          "phase sequencing",
          "delivery planning"
        ],
        "parent_domain": "roadmap",
        "child_domains": [],
        "related_domains": [
          "requirements"
        ],
        "skill_path": "skills/roadmap/phase-0/SKILL.md"
      },
      {
        "name": "roadmap-phase-1",
        "summary": "Roadmap phase node for phase-1 planning and sequencing guidance.",
        "confidence": 0.72,
        "key_files": [
          "skills/roadmap/SKILL.md"
        ],
        "key_patterns": [
          "phase sequencing",
          "delivery planning"
        ],
        "parent_domain": "roadmap",
        "child_domains": [],
        "related_domains": [
          "requirements"
        ],
        "skill_path": "skills/roadmap/phase-1/SKILL.md"
      },
      {
        "name": "roadmap-phase-2",
        "summary": "Roadmap phase node for phase-2 planning and sequencing guidance.",
        "confidence": 0.72,
        "key_files": [
          "skills/roadmap/SKILL.md"
        ],
        "key_patterns": [
          "phase sequencing",
          "delivery planning"
        ],
        "parent_domain": "roadmap",
        "child_domains": [],
        "related_domains": [
          "requirements"
        ],
        "skill_path": "skills/roadmap/phase-2/SKILL.md"
      },
      {
        "name": "roadmap-phase-3",
        "summary": "Roadmap phase node for phase-3 planning and sequencing guidance.",
        "confidence": 0.72,
        "key_files": [
          "skills/roadmap/SKILL.md"
        ],
        "key_patterns": [
          "phase sequencing",
          "delivery planning"
        ],
        "parent_domain": "roadmap",
        "child_domains": [],
        "related_domains": [
          "requirements"
        ],
        "skill_path": "skills/roadmap/phase-3/SKILL.md"
      }
    ],
    "recommendations": [
      "Repo archetype detected as `skilgen-platform`; keep generated skills aligned to that repo shape before applying generic labels.",
      "Use the inferred domain graph to decide which parent and child skills need regeneration.",
      "Refresh AGENTS.md whenever parent skill entry points or core domain relationships change.",
      "Detected `turbo` workspace metadata with 6 packages and 8 internal package edges; keep package domains distinct from file import analysis.",
      "Keep endpoint and flow validation coupled to the inferred domains when code changes.",
      "Re-run planning when new requirements materially change the inferred domain topology."
    ]
  },
  "detected_domains": [
    {
      "name": "platform",
      "confidence": 0.9,
      "key_files": [
        "skilgen/__init__.py",
        "skilgen/autoupdate.py",
        "skilgen/agents/__init__.py",
        "skilgen/agents/architecture_planner.py",
        "skilgen/cli/__init__.py",
        "skilgen/cli/main.py",
        "skilgen/core/__init__.py",
        "skilgen/core/analytics.py"
      ],
      "key_patterns": [
        "tooling platform",
        "generation engine",
        "repo-local operating surface"
      ],
      "sub_domains": [
        "platform-runtime",
        "platform-agents",
        "platform-cli",
        "platform-core",
        "platform-generators",
        "platform-scripts"
      ]
    },
    {
      "name": "platform-runtime",
      "confidence": 0.84,
      "key_files": [
        "skilgen/__init__.py",
        "skilgen/autoupdate.py",
        "skilgen/deep_agents_core.py",
        "skilgen/deep_agents_runtime.py",
        "skilgen/delivery.py",
        "setup.py"
      ],
      "key_patterns": [
        "runtime orchestration",
        "repo-wide coordination",
        "package entrypoints"
      ],
      "sub_domains": []
    },
    {
      "name": "platform-agents",
      "confidence": 0.84,
      "key_files": [
        "skilgen/agents/__init__.py",
        "skilgen/agents/architecture_planner.py",
        "skilgen/agents/codebase_signals.py",
        "skilgen/agents/decision_planner.py",
        "skilgen/agents/domain_graph_planner.py",
        "skilgen/agents/evidence_graph.py"
      ],
      "key_patterns": [
        "domain inference",
        "architecture synthesis",
        "agent planning logic"
      ],
      "sub_domains": []
    },
    {
      "name": "platform-cli",
      "confidence": 0.84,
      "key_files": [
        "skilgen/cli/__init__.py",
        "skilgen/cli/main.py"
      ],
      "key_patterns": [
        "command surfaces",
        "operator UX",
        "progress orchestration"
      ],
      "sub_domains": []
    },
    {
      "name": "platform-core",
      "confidence": 0.84,
      "key_files": [
        "skilgen/core/__init__.py",
        "skilgen/core/analytics.py",
        "skilgen/core/audit.py",
        "skilgen/core/auth_tokens.py",
        "skilgen/core/config.py",
        "skilgen/core/context.py"
      ],
      "key_patterns": [
        "shared models",
        "freshness and scoring",
        "validation primitives"
      ],
      "sub_domains": []
    },
    {
      "name": "platform-generators",
      "confidence": 0.84,
      "key_files": [
        "skilgen/generators/__init__.py",
        "skilgen/generators/package.py",
        "skilgen/generators/skills.py"
      ],
      "key_patterns": [
        "artifact rendering",
        "materialization flow",
        "repo-local outputs"
      ],
      "sub_domains": []
    },
    {
      "name": "platform-scripts",
      "confidence": 0.84,
      "key_files": [
        "scripts/bump_version.py",
        "scripts/deploy_api.py",
        "scripts/deploy_dashboard.py",
        "scripts/run_requirements_pipeline.py"
      ],
      "key_patterns": [
        "maintenance automation",
        "release helpers",
        "pipeline scripts"
      ],
      "sub_domains": []
    },
    {
      "name": "roadmap",
      "confidence": 0.84,
      "key_files": [
        "skills/roadmap/SKILL.md",
        "REPORT.md"
      ],
      "key_patterns": [
        "phase-based delivery",
        "sequenced implementation planning",
        "traceable next steps"
      ],
      "sub_domains": [
        "roadmap-phase-0",
        "roadmap-phase-1",
        "roadmap-phase-2",
        "roadmap-phase-3"
      ]
    },
    {
      "name": "roadmap-phase-0",
      "confidence": 0.72,
      "key_files": [
        "skills/roadmap/SKILL.md"
      ],
      "key_patterns": [
        "phase sequencing",
        "delivery planning"
      ],
      "sub_domains": []
    },
    {
      "name": "roadmap-phase-1",
      "confidence": 0.72,
      "key_files": [
        "skills/roadmap/SKILL.md"
      ],
      "key_patterns": [
        "phase sequencing",
        "delivery planning"
      ],
      "sub_domains": []
    },
    {
      "name": "roadmap-phase-2",
      "confidence": 0.72,
      "key_files": [
        "skills/roadmap/SKILL.md"
      ],
      "key_patterns": [
        "phase sequencing",
        "delivery planning"
      ],
      "sub_domains": []
    },
    {
      "name": "roadmap-phase-3",
      "confidence": 0.72,
      "key_files": [
        "skills/roadmap/SKILL.md"
      ],
      "key_patterns": [
        "phase sequencing",
        "delivery planning"
      ],
      "sub_domains": []
    }
  ],
  "skill_tree": [
    {
      "path": "skills/platform/SKILL.md",
      "domain": "platform",
      "parent_skill": null,
      "child_skills": [
        "skills/platform/runtime/SKILL.md",
        "skills/platform/agents/SKILL.md",
        "skills/platform/cli/SKILL.md",
        "skills/platform/core/SKILL.md",
        "skills/platform/generators/SKILL.md",
        "skills/platform/scripts/SKILL.md"
      ],
      "cross_references": [
        "skills/roadmap/SKILL.md"
      ]
    },
    {
      "path": "skills/platform/runtime/SKILL.md",
      "domain": "platform-runtime",
      "parent_skill": "skills/platform/SKILL.md",
      "child_skills": [],
      "cross_references": [
        "skills/roadmap/SKILL.md"
      ]
    },
    {
      "path": "skills/platform/agents/SKILL.md",
      "domain": "platform-agents",
      "parent_skill": "skills/platform/SKILL.md",
      "child_skills": [],
      "cross_references": [
        "skills/roadmap/SKILL.md"
      ]
    },
    {
      "path": "skills/platform/cli/SKILL.md",
      "domain": "platform-cli",
      "parent_skill": "skills/platform/SKILL.md",
      "child_skills": [],
      "cross_references": [
        "skills/roadmap/SKILL.md"
      ]
    },
    {
      "path": "skills/platform/core/SKILL.md",
      "domain": "platform-core",
      "parent_skill": "skills/platform/SKILL.md",
      "child_skills": [],
      "cross_references": [
        "skills/roadmap/SKILL.md"
      ]
    },
    {
      "path": "skills/platform/generators/SKILL.md",
      "domain": "platform-generators",
      "parent_skill": "skills/platform/SKILL.md",
      "child_skills": [],
      "cross_references": [
        "skills/roadmap/SKILL.md"
      ]
    },
    {
      "path": "skills/platform/scripts/SKILL.md",
      "domain": "platform-scripts",
      "parent_skill": "skills/platform/SKILL.md",
      "child_skills": [],
      "cross_references": [
        "skills/roadmap/SKILL.md"
      ]
    },
    {
      "path": "skills/roadmap/SKILL.md",
      "domain": "roadmap",
      "parent_skill": null,
      "child_skills": [
        "skills/roadmap/phase-0/SKILL.md",
        "skills/roadmap/phase-1/SKILL.md",
        "skills/roadmap/phase-2/SKILL.md",
        "skills/roadmap/phase-3/SKILL.md"
      ],
      "cross_references": []
    },
    {
      "path": "skills/roadmap/phase-0/SKILL.md",
      "domain": "roadmap-phase-0",
      "parent_skill": "skills/roadmap/SKILL.md",
      "child_skills": [],
      "cross_references": []
    },
    {
      "path": "skills/roadmap/phase-1/SKILL.md",
      "domain": "roadmap-phase-1",
      "parent_skill": "skills/roadmap/SKILL.md",
      "child_skills": [],
      "cross_references": []
    },
    {
      "path": "skills/roadmap/phase-2/SKILL.md",
      "domain": "roadmap-phase-2",
      "parent_skill": "skills/roadmap/SKILL.md",
      "child_skills": [],
      "cross_references": []
    },
    {
      "path": "skills/roadmap/phase-3/SKILL.md",
      "domain": "roadmap-phase-3",
      "parent_skill": "skills/roadmap/SKILL.md",
      "child_skills": [],
      "cross_references": []
    }
  ],
  "import_graph": {
    "scripts/bump_version.py": [
      "__future__",
      "argparse",
      "pathlib",
      "re"
    ],
    "scripts/deploy_api.py": [
      "__future__",
      "argparse",
      "collections.abc",
      "contextlib",
      "json",
      "pathlib",
      "shutil",
      "subprocess"
    ],
    "scripts/deploy_dashboard.py": [
      "__future__",
      "argparse",
      "collections.abc",
      "contextlib",
      "json",
      "pathlib",
      "subprocess"
    ],
    "scripts/run_requirements_pipeline.py": [
      "__future__",
      "argparse",
      "json",
      "pathlib",
      "skilgen/delivery.py",
      "sys"
    ],
    "setup.py": [
      "setuptools"
    ],
    "skilgen/__init__.py": [
      "skilgen/agents/__init__.py",
      "skilgen/autoupdate.py",
      "skilgen/delivery.py",
      "skilgen/sdk.py"
    ],
    "skilgen/agents/__init__.py": [
      "skilgen/agents/architecture_planner.py",
      "skilgen/agents/codebase_signals.py",
      "skilgen/agents/decision_planner.py",
      "skilgen/agents/domain_graph_planner.py",
      "skilgen/agents/evidence_graph.py",
      "skilgen/agents/feature_extractor.py",
      "skilgen/agents/framework_fingerprint.py",
      "skilgen/agents/language_parsers.py",
      "skilgen/agents/model_registry.py",
      "skilgen/agents/relationship_mapper.py",
      "skilgen/agents/requirements_parser.py",
      "skilgen/agents/roadmap_planner.py",
      "skilgen/agents/source_graphs.py",
      "skilgen/agents/workspace_graph.py"
    ],
    "skilgen/agents/architecture_planner.py": [
      "__future__",
      "dataclasses",
      "pathlib",
      "skilgen/agents/domain_graph_planner.py",
      "skilgen/agents/evidence_graph.py",
      "skilgen/core/config.py",
      "skilgen/core/models.py",
      "skilgen/deep_agents_core.py"
    ],
    "skilgen/agents/codebase_signals.py": [
      "__future__",
      "ast",
      "functools",
      "pathlib",
      "re",
      "skilgen/core/config.py",
      "skilgen/core/corpus_index.py",
      "skilgen/core/deep_sampler.py",
      "skilgen/core/document_ingestion.py",
      "skilgen/core/models.py"
    ],
    "skilgen/agents/decision_planner.py": [
      "__future__",
      "pathlib",
      "skilgen/core/freshness.py",
      "skilgen/core/models.py",
      "skilgen/core/run_memory.py",
      "skilgen/deep_agents_core.py",
      "skilgen/enterprise_skills.py",
      "skilgen/external_skills.py"
    ],
    "skilgen/agents/domain_graph_planner.py": [
      "__future__",
      "pathlib",
      "skilgen/agents/codebase_signals.py",
      "skilgen/agents/requirements_parser.py",
      "skilgen/agents/workspace_graph.py",
      "skilgen/core/models.py",
      "skilgen/deep_agents_core.py"
    ],
    "skilgen/agents/evidence_graph.py": [
      "__future__",
      "pathlib",
      "skilgen/agents/codebase_signals.py",
      "skilgen/agents/relationship_mapper.py",
      "skilgen/agents/source_graphs.py",
      "skilgen/agents/workspace_graph.py",
      "skilgen/core/dependency_risk.py",
      "skilgen/core/models.py",
      "skilgen/core/runtime_signals.py"
    ],
    "skilgen/agents/feature_extractor.py": [
      "__future__",
      "pathlib",
      "skilgen/agents/codebase_signals.py",
      "skilgen/agents/requirements_parser.py",
      "skilgen/core/models.py",
      "skilgen/deep_agents_core.py"
    ],
    "skilgen/agents/framework_fingerprint.py": [
      "__future__",
      "pathlib",
      "skilgen/core/models.py"
    ],
    "skilgen/agents/language_parsers.py": [
      "__future__",
      "ast",
      "dataclasses",
      "pathlib",
      "re",
      "tree_sitter_language_pack"
    ],
    "skilgen/agents/model_registry.py": [
      "__future__",
      "os",
      "skilgen/core/models.py"
    ],
    "skilgen/agents/relationship_mapper.py": [
      "__future__",
      "ast",
      "pathlib",
      "re",
      "skilgen/agents/codebase_signals.py",
      "warnings"
    ],
    "skilgen/agents/requirements_parser.py": [
      "__future__",
      "pathlib",
      "skilgen/agents/codebase_signals.py",
      "skilgen/core/models.py",
      "skilgen/core/requirements.py",
      "skilgen/deep_agents_core.py"
    ],
    "skilgen/agents/roadmap_planner.py": [
      "__future__",
      "pathlib",
      "skilgen/agents/model_registry.py",
      "skilgen/core/models.py",
      "skilgen/deep_agents_core.py"
    ],
    "skilgen/agents/source_graphs.py": [
      "__future__",
      "ast",
      "functools",
      "pathlib",
      "re",
      "skilgen/agents/codebase_signals.py",
      "skilgen/agents/language_parsers.py",
      "skilgen/agents/relationship_mapper.py",
      "skilgen/core/models.py"
    ],
    "skilgen/agents/workspace_graph.py": [
      "__future__",
      "json",
      "pathlib",
      "re",
      "skilgen/core/models.py",
      "yaml"
    ],
    "skilgen/api/__init__.py": [
      "skilgen/api/server.py"
    ],
    "skilgen/api/jobs.py": [
      "__future__",
      "concurrent.futures",
      "contextlib",
      "dataclasses",
      "datetime",
      "json",
      "pathlib",
      "skilgen/core/audit.py",
      "sqlite3",
      "threading",
      "typing",
      "uuid"
    ],
    "skilgen/api/server.py": [
      "__future__",
      "concurrent.futures",
      "dataclasses",
      "hashlib",
      "hmac",
      "http.server",
      "ipaddress",
      "json",
      "logging",
      "os",
      "pathlib",
      "skilgen/api/service.py",
      "skilgen/core/audit.py",
      "skilgen/core/auth_tokens.py",
      "skilgen/core/identity_policy_store.py",
      "skilgen/core/rate_limit_store.py",
      "skilgen/core/runtime_data.py",
      "socket",
      "threading",
      "time",
      "urllib.parse",
      "uuid"
    ],
    "skilgen/api/service.py": [
      "__future__",
      "pathlib",
      "skilgen/agents/decision_planner.py",
      "skilgen/api/jobs.py",
      "skilgen/autoupdate.py",
      "skilgen/core/analytics.py",
      "skilgen/core/context.py",
      "skilgen/core/diff.py",
      "skilgen/core/freshness.py",
      "skilgen/core/identity_policy_store.py",
      "skilgen/core/requirements.py",
      "skilgen/core/run_memory.py",
      "skilgen/core/score.py",
      "skilgen/deep_agents_core.py",
      "skilgen/deep_agents_runtime.py",
      "skilgen/delivery.py",
      "skilgen/enterprise_skills.py",
      "skilgen/external_skills.py",
      "typing"
    ],
    "skilgen/autoupdate.py": [
      "__future__",
      "datetime",
      "json",
      "os",
      "pathlib",
      "signal",
      "skilgen/agents/codebase_signals.py",
      "skilgen/core/config.py",
      "skilgen/core/generated_outputs.py",
      "skilgen/core/repo_state.py",
      "skilgen/delivery.py",
      "subprocess",
      "sys",
      "time"
    ],
    "skilgen/cli/__init__.py": [],
    "skilgen/cli/main.py": [
      "__future__",
      "argparse",
      "dataclasses",
      "json",
      "pathlib",
      "skilgen/__init__.py",
      "skilgen/agents/__init__.py",
      "skilgen/agents/requirements_parser.py",
      "skilgen/api/server.py",
      "skilgen/api/service.py",
      "skilgen/autoupdate.py",
      "skilgen/core/analytics.py",
      "skilgen/core/config.py",
      "skilgen/core/corpus_index.py",
      "skilgen/core/dependency_risk.py",
      "skilgen/core/enterprise_policy.py",
      "skilgen/core/evals.py",
      "skilgen/core/runtime_data.py",
      "skilgen/core/score.py",
      "skilgen/deep_agents_core.py",
      "skilgen/delivery.py",
      "skilgen/enterprise_skills.py",
      "skilgen/external_skills.py",
      "skilgen/registry_client.py",
      "sys",
      "threading",
      "time"
    ],
    "skilgen/core/__init__.py": [],
    "skilgen/core/analytics.py": [
      "__future__",
      "collections",
      "datetime",
      "json",
      "os",
      "pathlib",
      "re",
      "skilgen/external_skills.py"
    ],
    "skilgen/core/audit.py": [
      "__future__",
      "contextlib",
      "datetime",
      "fcntl",
      "json",
      "os",
      "pathlib",
      "threading",
      "typing"
    ],
    "skilgen/core/auth_tokens.py": [
      "__future__",
      "base64",
      "cryptography.exceptions",
      "cryptography.hazmat.primitives",
      "cryptography.hazmat.primitives.asymmetric",
      "hashlib",
      "hmac",
      "ipaddress",
      "json",
      "pathlib",
      "socket",
      "threading",
      "time",
      "typing",
      "urllib.parse",
      "urllib.request"
    ],
    "skilgen/core/config.py": [
      "__future__",
      "pathlib",
      "skilgen/core/models.py"
    ],
    "skilgen/core/context.py": [
      "__future__",
      "pathlib",
      "skilgen/agents/codebase_signals.py",
      "skilgen/agents/domain_graph_planner.py",
      "skilgen/agents/framework_fingerprint.py",
      "skilgen/agents/workspace_graph.py",
      "skilgen/core/models.py"
    ],
    "skilgen/core/corpus_index.py": [
      "__future__",
      "collections",
      "fnmatch",
      "hashlib",
      "json",
      "pathlib",
      "re",
      "skilgen/agents/codebase_signals.py",
      "skilgen/agents/language_parsers.py",
      "skilgen/core/config.py",
      "skilgen/core/document_ingestion.py",
      "skilgen/core/models.py",
      "typing"
    ],
    "skilgen/core/deep_sampler.py": [
      "__future__",
      "pathlib",
      "skilgen/core/config.py",
      "skilgen/core/models.py",
      "typing"
    ],
    "skilgen/core/dependency_risk.py": [
      "__future__",
      "json",
      "pathlib",
      "re",
      "skilgen/agents/relationship_mapper.py",
      "skilgen/agents/workspace_graph.py",
      "skilgen/core/models.py",
      "tomllib"
    ],
    "skilgen/core/diff.py": [
      "__future__",
      "pathlib",
      "skilgen/core/context.py",
      "skilgen/core/freshness.py",
      "skilgen/core/repo_state.py",
      "skilgen/core/requirements.py",
      "skilgen/core/score.py"
    ],
    "skilgen/core/document_ingestion.py": [
      "__future__",
      "bs4",
      "csv",
      "html",
      "json",
      "openpyxl",
      "pathlib",
      "pptx",
      "pypdf",
      "re",
      "tomllib",
      "xml.etree.ElementTree",
      "yaml",
      "zipfile"
    ],
    "skilgen/core/enterprise_policy.py": [
      "__future__",
      "dataclasses",
      "datetime",
      "pathlib",
      "skilgen/core/dependency_risk.py",
      "skilgen/core/score.py",
      "skilgen/enterprise_skills.py",
      "skilgen/external_skills.py",
      "typing",
      "yaml"
    ],
    "skilgen/core/evals.py": [
      "__future__",
      "json",
      "pathlib"
    ],
    "skilgen/core/freshness.py": [
      "__future__",
      "dataclasses",
      "hashlib",
      "json",
      "pathlib",
      "skilgen/core/generated_outputs.py",
      "skilgen/core/models.py"
    ],
    "skilgen/core/generated_outputs.py": [
      "__future__",
      "pathlib"
    ],
    "skilgen/core/identity_policy_store.py": [
      "__future__",
      "contextlib",
      "datetime",
      "json",
      "os",
      "pathlib",
      "sqlite3",
      "typing"
    ],
    "skilgen/core/models.py": [
      "__future__",
      "dataclasses",
      "pathlib"
    ],
    "skilgen/core/project_memory.py": [
      "__future__",
      "dataclasses",
      "json",
      "pathlib",
      "skilgen/core/models.py"
    ],
    "skilgen/core/rate_limit_store.py": [
      "__future__",
      "math",
      "os",
      "pathlib",
      "sqlite3"
    ],
    "skilgen/core/repo_state.py": [
      "__future__",
      "pathlib",
      "re",
      "shutil",
      "skilgen/agents/language_parsers.py",
      "subprocess"
    ],
    "skilgen/core/requirements.py": [
      "__future__",
      "hashlib",
      "json",
      "pathlib",
      "skilgen/agents/codebase_signals.py",
      "skilgen/core/document_ingestion.py",
      "skilgen/core/models.py"
    ],
    "skilgen/core/run_memory.py": [
      "__future__",
      "dataclasses",
      "json",
      "pathlib",
      "skilgen/core/models.py",
      "uuid"
    ],
    "skilgen/core/runtime_data.py": [
      "__future__",
      "pathlib",
      "shutil",
      "skilgen/core/config.py",
      "time"
    ],
    "skilgen/core/runtime_signals.py": [
      "__future__",
      "json",
      "pathlib",
      "re",
      "skilgen/core/models.py",
      "xml.etree"
    ],
    "skilgen/core/score.py": [
      "__future__",
      "datetime",
      "html",
      "json",
      "pathlib",
      "re",
      "skilgen/agents/codebase_signals.py",
      "skilgen/core/context.py",
      "skilgen/core/freshness.py",
      "skilgen/core/requirements.py",
      "skilgen/core/validation.py",
      "subprocess",
      "threading",
      "urllib.parse"
    ],
    "skilgen/core/validation.py": [
      "__future__",
      "pathlib",
      "skilgen/agents/codebase_signals.py",
      "skilgen/deep_agents_core.py"
    ],
    "skilgen/deep_agents_core.py": [
      "__future__",
      "asyncio",
      "deepagents",
      "json",
      "langchain.chat_models",
      "os",
      "pathlib",
      "queue",
      "skilgen/agents/model_registry.py",
      "skilgen/core/config.py",
      "threading",
      "time",
      "typing"
    ],
    "skilgen/deep_agents_runtime.py": [
      "__future__",
      "dataclasses",
      "deepagents",
      "json",
      "langchain.chat_models",
      "langchain_core.tools",
      "os",
      "pathlib",
      "skilgen/agents/codebase_signals.py",
      "skilgen/agents/decision_planner.py",
      "skilgen/agents/domain_graph_planner.py",
      "skilgen/agents/evidence_graph.py",
      "skilgen/agents/feature_extractor.py",
      "skilgen/agents/framework_fingerprint.py",
      "skilgen/agents/model_registry.py",
      "skilgen/agents/relationship_mapper.py",
      "skilgen/agents/requirements_parser.py",
      "skilgen/agents/roadmap_planner.py",
      "skilgen/agents/workspace_graph.py",
      "skilgen/autoupdate.py",
      "skilgen/core/analytics.py",
      "skilgen/core/config.py",
      "skilgen/core/context.py",
      "skilgen/core/corpus_index.py",
      "skilgen/core/diff.py",
      "skilgen/core/freshness.py",
      "skilgen/core/requirements.py",
      "skilgen/core/score.py",
      "skilgen/core/validation.py",
      "skilgen/deep_agents_core.py",
      "skilgen/enterprise_skills.py",
      "skilgen/external_skills.py",
      "skilgen/generators/package.py",
      "skilgen/generators/skills.py",
      "typing"
    ],
    "skilgen/delivery.py": [
      "__future__",
      "dataclasses",
      "pathlib",
      "skilgen/agents/__init__.py",
      "skilgen/agents/codebase_signals.py",
      "skilgen/agents/source_graphs.py",
      "skilgen/core/analytics.py",
      "skilgen/core/audit.py",
      "skilgen/core/config.py",
      "skilgen/core/context.py",
      "skilgen/core/corpus_index.py",
      "skilgen/core/freshness.py",
      "skilgen/core/generated_outputs.py",
      "skilgen/core/models.py",
      "skilgen/core/repo_state.py",
      "skilgen/core/requirements.py",
      "skilgen/core/run_memory.py",
      "skilgen/core/runtime_data.py",
      "skilgen/core/score.py",
      "skilgen/deep_agents_core.py",
      "skilgen/enterprise_skills.py",
      "skilgen/external_skills.py",
      "skilgen/generators/package.py",
      "skilgen/generators/skills.py",
      "time",
      "typing"
    ],
    "skilgen/enterprise_skills.py": [
      "__future__",
      "dataclasses",
      "datetime",
      "json",
      "os",
      "pathlib",
      "re",
      "shutil",
      "skilgen/core/config.py",
      "skilgen/core/document_ingestion.py",
      "subprocess",
      "urllib.parse",
      "urllib.request"
    ],
    "skilgen/external_skills.py": [
      "__future__",
      "dataclasses",
      "datetime",
      "json",
      "os",
      "pathlib",
      "re",
      "shutil",
      "skilgen/core/config.py",
      "subprocess"
    ],
    "skilgen/generators/__init__.py": [],
    "skilgen/generators/package.py": [
      "__future__",
      "dataclasses",
      "datetime",
      "html",
      "json",
      "pathlib",
      "re",
      "skilgen/agents/__init__.py",
      "skilgen/agents/feature_extractor.py",
      "skilgen/agents/requirements_parser.py",
      "skilgen/core/config.py",
      "skilgen/core/context.py",
      "skilgen/core/models.py",
      "skilgen/deep_agents_core.py",
      "skilgen/deep_agents_runtime.py",
      "skilgen/enterprise_skills.py",
      "skilgen/external_skills.py",
      "sys",
      "typing"
    ],
    "skilgen/generators/skills.py": [
      "__future__",
      "datetime",
      "os",
      "pathlib",
      "skilgen/agents/architecture_planner.py",
      "skilgen/agents/codebase_signals.py",
      "skilgen/agents/requirements_parser.py",
      "skilgen/agents/roadmap_planner.py",
      "skilgen/core/config.py",
      "skilgen/core/context.py",
      "skilgen/core/dependency_risk.py",
      "skilgen/core/models.py",
      "skilgen/deep_agents_core.py",
      "typing"
    ],
    "skilgen/registry_client.py": [
      "__future__",
      "json",
      "os",
      "pathlib",
      "typing",
      "urllib.error",
      "urllib.request"
    ],
    "skilgen/sdk.py": [
      "__future__",
      "pathlib",
      "skilgen/api/service.py",
      "skilgen/autoupdate.py",
      "skilgen/core/config.py",
      "skilgen/core/evals.py",
      "skilgen/delivery.py",
      "skilgen/enterprise_skills.py",
      "skilgen/external_skills.py"
    ],
    "tests/__init__.py": [],
    "tests/oidc_test_utils.py": [
      "__future__",
      "base64",
      "cryptography.hazmat.primitives",
      "cryptography.hazmat.primitives.asymmetric",
      "http.server",
      "json",
      "pathlib",
      "threading",
      "time",
      "typing"
    ],
    "tests/test_analytics.py": [
      "pathlib",
      "skilgen/core/analytics.py",
      "skilgen/generators/package.py",
      "tempfile",
      "unittest"
    ],
    "tests/test_api_smoke.py": [
      "__future__",
      "io",
      "json",
      "logging",
      "os",
      "pathlib",
      "skilgen/api/server.py",
      "skilgen/core/auth_tokens.py",
      "subprocess",
      "tempfile",
      "tests/oidc_test_utils.py",
      "threading",
      "time",
      "unittest",
      "urllib.error",
      "urllib.parse",
      "urllib.request"
    ],
    "tests/test_architecture_cli.py": [
      "json",
      "pathlib",
      "subprocess",
      "sys",
      "tempfile",
      "unittest"
    ],
    "tests/test_architecture_planner.py": [
      "pathlib",
      "skilgen/agents/architecture_planner.py",
      "skilgen/core/models.py",
      "tempfile",
      "unittest"
    ],
    "tests/test_audit.py": [
      "__future__",
      "os",
      "pathlib",
      "skilgen/core/audit.py",
      "tempfile",
      "unittest",
      "unittest.mock"
    ],
    "tests/test_auth_claim_mapping.py": [
      "__future__",
      "json",
      "os",
      "pathlib",
      "skilgen/api/server.py",
      "tempfile",
      "unittest"
    ],
    "tests/test_auth_tokens.py": [
      "__future__",
      "pathlib",
      "skilgen/core/auth_tokens.py",
      "tempfile",
      "tests/oidc_test_utils.py",
      "time",
      "unittest"
    ],
    "tests/test_autoupdate.py": [
      "pathlib",
      "skilgen/autoupdate.py",
      "tempfile",
      "unittest"
    ],
    "tests/test_cli.py": [
      "json",
      "pathlib",
      "subprocess",
      "sys",
      "tempfile",
      "unittest"
    ],
    "tests/test_codebase_signals.py": [
      "pathlib",
      "skilgen/agents/codebase_signals.py",
      "tempfile",
      "unittest"
    ],
    "tests/test_config.py": [
      "pathlib",
      "skilgen/core/config.py",
      "tempfile",
      "unittest"
    ],
    "tests/test_context.py": [
      "pathlib",
      "skilgen/core/context.py",
      "skilgen/core/requirements.py",
      "tempfile",
      "unittest"
    ],
    "tests/test_corpus_cli.py": [
      "json",
      "pathlib",
      "subprocess",
      "sys",
      "tempfile",
      "unittest"
    ],
    "tests/test_corpus_index.py": [
      "pathlib",
      "skilgen/agents/codebase_signals.py",
      "skilgen/core/corpus_index.py",
      "skilgen/core/deep_sampler.py",
      "tempfile",
      "unittest"
    ],
    "tests/test_dashboard_cli.py": [
      "contextlib",
      "datetime",
      "io",
      "json",
      "pathlib",
      "skilgen/autoupdate.py",
      "skilgen/cli/main.py",
      "skilgen/core/requirements.py",
      "skilgen/generators/package.py",
      "subprocess",
      "sys",
      "tempfile",
      "unittest",
      "unittest.mock"
    ],
    "tests/test_decision_planner.py": [
      "pathlib",
      "skilgen/agents/decision_planner.py",
      "skilgen/core/context.py",
      "skilgen/core/requirements.py",
      "skilgen/external_skills.py",
      "subprocess",
      "tempfile",
      "unittest"
    ],
    "tests/test_delivery.py": [
      "pathlib",
      "skilgen/core/models.py",
      "skilgen/core/score.py",
      "skilgen/delivery.py",
      "tempfile",
      "unittest",
      "unittest.mock"
    ],
    "tests/test_dependency_risk.py": [
      "json",
      "pathlib",
      "skilgen/core/dependency_risk.py",
      "tempfile",
      "unittest"
    ],
    "tests/test_dependency_risk_graph_workstream.py": [
      "__future__",
      "apps/api/api/routes/repos.py",
      "datetime",
      "json",
      "pathlib",
      "skilgen/core/dependency_risk.py",
      "tempfile",
      "types"
    ],
    "tests/test_diff.py": [
      "json",
      "pathlib",
      "skilgen/core/context.py",
      "skilgen/core/diff.py",
      "skilgen/core/freshness.py",
      "skilgen/core/requirements.py",
      "subprocess",
      "sys",
      "tempfile",
      "unittest"
    ],
    "tests/test_document_ingestion.py": [
      "__future__",
      "openpyxl",
      "pathlib",
      "pptx",
      "skilgen/core/document_ingestion.py",
      "skilgen/core/requirements.py",
      "tempfile",
      "unittest",
      "zipfile"
    ],
    "tests/test_domain_graph_planner.py": [
      "pathlib",
      "skilgen/agents/domain_graph_planner.py",
      "skilgen/core/requirements.py",
      "tempfile",
      "unittest",
      "unittest.mock"
    ],
    "tests/test_enterprise_document_formats.py": [
      "__future__",
      "pathlib",
      "skilgen/core/document_ingestion.py",
      "skilgen/enterprise_skills.py",
      "tempfile",
      "unittest"
    ],
    "tests/test_enterprise_policy_cli.py": [
      "__future__",
      "datetime",
      "json",
      "pathlib",
      "subprocess",
      "sys",
      "tempfile"
    ],
    "tests/test_feature_extractor.py": [
      "pathlib",
      "skilgen/agents/feature_extractor.py",
      "tempfile",
      "unittest"
    ],
    "tests/test_framework_fingerprint.py": [
      "pathlib",
      "skilgen/agents/framework_fingerprint.py",
      "tempfile",
      "unittest"
    ],
    "tests/test_identity_policy_store.py": [
      "__future__",
      "os",
      "pathlib",
      "skilgen/core/identity_policy_store.py",
      "tempfile",
      "unittest"
    ],
    "tests/test_jobs.py": [
      "contextlib",
      "pathlib",
      "skilgen/api/jobs.py",
      "skilgen/api/service.py",
      "sqlite3",
      "tempfile",
      "time",
      "unittest"
    ],
    "tests/test_model_registry.py": [
      "os",
      "skilgen/agents/model_registry.py",
      "skilgen/core/models.py",
      "unittest"
    ],
    "tests/test_org_settings.py": [
      "__future__",
      "apps/api/api/analysis.py",
      "apps/api/api/auth.py",
      "apps/api/api/routes/orgs.py",
      "asyncio",
      "datetime",
      "fastapi",
      "fastapi.testclient",
      "packages/db/database.py",
      "pathlib",
      "sqlalchemy.exc",
      "types",
      "typing"
    ],
    "tests/test_overview_data.py": [
      "__future__",
      "packages/db/schemas.py",
      "pathlib"
    ],
    "tests/test_packaging.py": [
      "os",
      "pathlib",
      "shutil",
      "subprocess",
      "sys",
      "tempfile",
      "time",
      "unittest"
    ],
    "tests/test_plan_cli.py": [
      "json",
      "pathlib",
      "subprocess",
      "sys",
      "tempfile",
      "unittest"
    ],
    "tests/test_pr_comment.py": [
      "__future__",
      "apps/api/api/pr_comment.py",
      "unittest"
    ],
    "tests/test_pr_comment_dedup.py": [
      "__future__",
      "apps/api/api/pr_comment.py",
      "httpx",
      "pytest",
      "typing"
    ],
    "tests/test_rate_limit_store.py": [
      "__future__",
      "pathlib",
      "skilgen/core/rate_limit_store.py",
      "tempfile",
      "unittest"
    ],
    "tests/test_registry_api.py": [
      "__future__",
      "apps/api/api/auth.py",
      "apps/api/api/routes/registry.py",
      "datetime",
      "fastapi",
      "fastapi.testclient",
      "packages/db/database.py",
      "types",
      "typing"
    ],
    "tests/test_registry_cli.py": [
      "__future__",
      "http.server",
      "json",
      "os",
      "pathlib",
      "subprocess",
      "sys",
      "tempfile",
      "threading",
      "typing",
      "unittest"
    ],
    "tests/test_registry_dashboard.py": [
      "__future__",
      "pathlib"
    ],
    "tests/test_relationship_mapper.py": [
      "pathlib",
      "skilgen/agents/relationship_mapper.py",
      "tempfile",
      "unittest"
    ],
    "tests/test_repos_screen.py": [
      "__future__",
      "pathlib"
    ],
    "tests/test_requirements.py": [
      "json",
      "pathlib",
      "skilgen/core/requirements.py",
      "tempfile",
      "unittest"
    ],
    "tests/test_requirements_parser.py": [
      "pathlib",
      "skilgen/agents/requirements_parser.py",
      "tempfile",
      "unittest"
    ],
    "tests/test_roadmap_planner.py": [
      "skilgen/agents/roadmap_planner.py",
      "skilgen/core/models.py",
      "unittest"
    ],
    "tests/test_roadmap_skills.py": [
      "pathlib",
      "skilgen/core/requirements.py",
      "skilgen/generators/skills.py",
      "tempfile",
      "unittest"
    ],
    "tests/test_run_memory.py": [
      "pathlib",
      "skilgen/core/models.py",
      "skilgen/core/run_memory.py",
      "tempfile",
      "unittest"
    ],
    "tests/test_runtime_hardening.py": [
      "os",
      "pathlib",
      "skilgen/deep_agents_core.py",
      "tempfile",
      "time",
      "types",
      "unittest",
      "unittest.mock"
    ],
    "tests/test_runtime_signals.py": [
      "json",
      "pathlib",
      "skilgen/core/runtime_signals.py",
      "tempfile",
      "unittest"
    ],
    "tests/test_score.py": [
      "pathlib",
      "skilgen/core/repo_state.py",
      "skilgen/core/score.py",
      "subprocess",
      "tempfile",
      "threading",
      "unittest",
      "unittest.mock"
    ],
    "tests/test_score_quality_system.py": [
      "__future__",
      "apps/api/api/routes/orgs.py",
      "apps/api/api/routes/repos.py",
      "datetime",
      "fastapi",
      "fastapi.testclient",
      "json",
      "packages/db/database.py",
      "pathlib",
      "pytest",
      "skilgen/core/score.py",
      "subprocess",
      "sys",
      "tempfile",
      "types",
      "typing"
    ],
    "tests/test_sdk.py": [
      "json",
      "pathlib",
      "skilgen/external_skills.py",
      "skilgen/sdk.py",
      "subprocess",
      "tempfile",
      "time",
      "unittest",
      "unittest.mock"
    ],
    "tests/test_skill_detail.py": [
      "__future__",
      "apps/api/api/routes/skills.py",
      "asyncio",
      "pathlib",
      "types"
    ],
    "tests/test_skill_usage_analytics.py": [
      "__future__",
      "apps/api/api/routes/admin.py",
      "apps/api/api/routes/orgs.py",
      "apps/api/api/routes/skills.py",
      "asyncio",
      "datetime",
      "fastapi",
      "fastapi.testclient",
      "packages/db/config.py",
      "packages/db/database.py",
      "pathlib",
      "types",
      "typing"
    ],
    "tests/test_skillayer_api_infra.py": [
      "__future__",
      "apps/api/api/auth.py",
      "apps/api/api/index.py",
      "apps/api/api/routes/metrics.py",
      "apps/api/api/routes/webhook.py",
      "datetime",
      "fastapi",
      "fastapi.testclient",
      "hashlib",
      "hmac",
      "packages/db/config.py",
      "packages/db/models/Base.py",
      "packages/db/models/Org.py",
      "packages/db/models/Repo.py",
      "pytest"
    ],
    "tests/test_source_graphs.py": [
      "pathlib",
      "skilgen/agents/language_parsers.py",
      "skilgen/agents/source_graphs.py",
      "tempfile",
      "unittest"
    ],
    "tests/test_stripe_portal.py": [
      "__future__",
      "apps/api/api/auth.py",
      "apps/api/api/routes/stripe.py",
      "fastapi",
      "fastapi.testclient",
      "packages/db/database.py",
      "pytest",
      "types",
      "typing"
    ],
    "tests/test_stripe_webhook.py": [
      "__future__",
      "apps/api/api/auth.py",
      "apps/api/api/routes/stripe.py",
      "fastapi",
      "fastapi.testclient",
      "json",
      "packages/db/database.py",
      "packages/db/models/Org.py",
      "pytest",
      "types",
      "typing"
    ],
    "tests/test_upgrade_flow.py": [
      "pathlib",
      "unittest"
    ],
    "tests/test_validate_cli.py": [
      "json",
      "subprocess",
      "sys",
      "unittest"
    ],
    "tests/test_vercel_api_deploy.py": [
      "__future__",
      "json",
      "pathlib",
      "scripts/deploy_api.py"
    ],
    "tests/test_vercel_dashboard_deploy.py": [
      "__future__",
      "json",
      "pathlib",
      "scripts/deploy_dashboard.py"
    ],
    "tests/test_workspace_graph.py": [
      "pathlib",
      "skilgen/agents/workspace_graph.py",
      "tempfile",
      "unittest"
    ]
  },
  "evidence_graph": {
    "language_inventory": {
      "python": 128
    },
    "dominant_languages": [
      "python"
    ],
    "import_graph": {
      "scripts/bump_version.py": [
        "__future__",
        "argparse",
        "pathlib",
        "re"
      ],
      "scripts/deploy_api.py": [
        "__future__",
        "argparse",
        "collections.abc",
        "contextlib",
        "json",
        "pathlib",
        "shutil",
        "subprocess"
      ],
      "scripts/deploy_dashboard.py": [
        "__future__",
        "argparse",
        "collections.abc",
        "contextlib",
        "json",
        "pathlib",
        "subprocess"
      ],
      "scripts/run_requirements_pipeline.py": [
        "__future__",
        "argparse",
        "json",
        "pathlib",
        "skilgen/delivery.py",
        "sys"
      ],
      "setup.py": [
        "setuptools"
      ],
      "skilgen/__init__.py": [
        "skilgen/agents/__init__.py",
        "skilgen/autoupdate.py",
        "skilgen/delivery.py",
        "skilgen/sdk.py"
      ],
      "skilgen/agents/__init__.py": [
        "skilgen/agents/architecture_planner.py",
        "skilgen/agents/codebase_signals.py",
        "skilgen/agents/decision_planner.py",
        "skilgen/agents/domain_graph_planner.py",
        "skilgen/agents/evidence_graph.py",
        "skilgen/agents/feature_extractor.py",
        "skilgen/agents/framework_fingerprint.py",
        "skilgen/agents/language_parsers.py",
        "skilgen/agents/model_registry.py",
        "skilgen/agents/relationship_mapper.py",
        "skilgen/agents/requirements_parser.py",
        "skilgen/agents/roadmap_planner.py",
        "skilgen/agents/source_graphs.py",
        "skilgen/agents/workspace_graph.py"
      ],
      "skilgen/agents/architecture_planner.py": [
        "__future__",
        "dataclasses",
        "pathlib",
        "skilgen/agents/domain_graph_planner.py",
        "skilgen/agents/evidence_graph.py",
        "skilgen/core/config.py",
        "skilgen/core/models.py",
        "skilgen/deep_agents_core.py"
      ],
      "skilgen/agents/codebase_signals.py": [
        "__future__",
        "ast",
        "functools",
        "pathlib",
        "re",
        "skilgen/core/config.py",
        "skilgen/core/corpus_index.py",
        "skilgen/core/deep_sampler.py",
        "skilgen/core/document_ingestion.py",
        "skilgen/core/models.py"
      ],
      "skilgen/agents/decision_planner.py": [
        "__future__",
        "pathlib",
        "skilgen/core/freshness.py",
        "skilgen/core/models.py",
        "skilgen/core/run_memory.py",
        "skilgen/deep_agents_core.py",
        "skilgen/enterprise_skills.py",
        "skilgen/external_skills.py"
      ],
      "skilgen/agents/domain_graph_planner.py": [
        "__future__",
        "pathlib",
        "skilgen/agents/codebase_signals.py",
        "skilgen/agents/requirements_parser.py",
        "skilgen/agents/workspace_graph.py",
        "skilgen/core/models.py",
        "skilgen/deep_agents_core.py"
      ],
      "skilgen/agents/evidence_graph.py": [
        "__future__",
        "pathlib",
        "skilgen/agents/codebase_signals.py",
        "skilgen/agents/relationship_mapper.py",
        "skilgen/agents/source_graphs.py",
        "skilgen/agents/workspace_graph.py",
        "skilgen/core/dependency_risk.py",
        "skilgen/core/models.py",
        "skilgen/core/runtime_signals.py"
      ],
      "skilgen/agents/feature_extractor.py": [
        "__future__",
        "pathlib",
        "skilgen/agents/codebase_signals.py",
        "skilgen/agents/requirements_parser.py",
        "skilgen/core/models.py",
        "skilgen/deep_agents_core.py"
      ],
      "skilgen/agents/framework_fingerprint.py": [
        "__future__",
        "pathlib",
        "skilgen/core/models.py"
      ],
      "skilgen/agents/language_parsers.py": [
        "__future__",
        "ast",
        "dataclasses",
        "pathlib",
        "re",
        "tree_sitter_language_pack"
      ],
      "skilgen/agents/model_registry.py": [
        "__future__",
        "os",
        "skilgen/core/models.py"
      ],
      "skilgen/agents/relationship_mapper.py": [
        "__future__",
        "ast",
        "pathlib",
        "re",
        "skilgen/agents/codebase_signals.py",
        "warnings"
      ],
      "skilgen/agents/requirements_parser.py": [
        "__future__",
        "pathlib",
        "skilgen/agents/codebase_signals.py",
        "skilgen/core/models.py",
        "skilgen/core/requirements.py",
        "skilgen/deep_agents_core.py"
      ],
      "skilgen/agents/roadmap_planner.py": [
        "__future__",
        "pathlib",
        "skilgen/agents/model_registry.py",
        "skilgen/core/models.py",
        "skilgen/deep_agents_core.py"
      ],
      "skilgen/agents/source_graphs.py": [
        "__future__",
        "ast",
        "functools",
        "pathlib",
        "re",
        "skilgen/agents/codebase_signals.py",
        "skilgen/agents/language_parsers.py",
        "skilgen/agents/relationship_mapper.py",
        "skilgen/core/models.py"
      ],
      "skilgen/agents/workspace_graph.py": [
        "__future__",
        "json",
        "pathlib",
        "re",
        "skilgen/core/models.py",
        "yaml"
      ],
      "skilgen/api/__init__.py": [
        "skilgen/api/server.py"
      ],
      "skilgen/api/jobs.py": [
        "__future__",
        "concurrent.futures",
        "contextlib",
        "dataclasses",
        "datetime",
        "json",
        "pathlib",
        "skilgen/core/audit.py",
        "sqlite3",
        "threading",
        "typing",
        "uuid"
      ],
      "skilgen/api/server.py": [
        "__future__",
        "concurrent.futures",
        "dataclasses",
        "hashlib",
        "hmac",
        "http.server",
        "ipaddress",
        "json",
        "logging",
        "os",
        "pathlib",
        "skilgen/api/service.py",
        "skilgen/core/audit.py",
        "skilgen/core/auth_tokens.py",
        "skilgen/core/identity_policy_store.py",
        "skilgen/core/rate_limit_store.py",
        "skilgen/core/runtime_data.py",
        "socket",
        "threading",
        "time",
        "urllib.parse",
        "uuid"
      ],
      "skilgen/api/service.py": [
        "__future__",
        "pathlib",
        "skilgen/agents/decision_planner.py",
        "skilgen/api/jobs.py",
        "skilgen/autoupdate.py",
        "skilgen/core/analytics.py",
        "skilgen/core/context.py",
        "skilgen/core/diff.py",
        "skilgen/core/freshness.py",
        "skilgen/core/identity_policy_store.py",
        "skilgen/core/requirements.py",
        "skilgen/core/run_memory.py",
        "skilgen/core/score.py",
        "skilgen/deep_agents_core.py",
        "skilgen/deep_agents_runtime.py",
        "skilgen/delivery.py",
        "skilgen/enterprise_skills.py",
        "skilgen/external_skills.py",
        "typing"
      ],
      "skilgen/autoupdate.py": [
        "__future__",
        "datetime",
        "json",
        "os",
        "pathlib",
        "signal",
        "skilgen/agents/codebase_signals.py",
        "skilgen/core/config.py",
        "skilgen/core/generated_outputs.py",
        "skilgen/core/repo_state.py",
        "skilgen/delivery.py",
        "subprocess",
        "sys",
        "time"
      ],
      "skilgen/cli/__init__.py": [],
      "skilgen/cli/main.py": [
        "__future__",
        "argparse",
        "dataclasses",
        "json",
        "pathlib",
        "skilgen/__init__.py",
        "skilgen/agents/__init__.py",
        "skilgen/agents/requirements_parser.py",
        "skilgen/api/server.py",
        "skilgen/api/service.py",
        "skilgen/autoupdate.py",
        "skilgen/core/analytics.py",
        "skilgen/core/config.py",
        "skilgen/core/corpus_index.py",
        "skilgen/core/dependency_risk.py",
        "skilgen/core/enterprise_policy.py",
        "skilgen/core/evals.py",
        "skilgen/core/runtime_data.py",
        "skilgen/core/score.py",
        "skilgen/deep_agents_core.py",
        "skilgen/delivery.py",
        "skilgen/enterprise_skills.py",
        "skilgen/external_skills.py",
        "skilgen/registry_client.py",
        "sys",
        "threading",
        "time"
      ],
      "skilgen/core/__init__.py": [],
      "skilgen/core/analytics.py": [
        "__future__",
        "collections",
        "datetime",
        "json",
        "os",
        "pathlib",
        "re",
        "skilgen/external_skills.py"
      ],
      "skilgen/core/audit.py": [
        "__future__",
        "contextlib",
        "datetime",
        "fcntl",
        "json",
        "os",
        "pathlib",
        "threading",
        "typing"
      ],
      "skilgen/core/auth_tokens.py": [
        "__future__",
        "base64",
        "cryptography.exceptions",
        "cryptography.hazmat.primitives",
        "cryptography.hazmat.primitives.asymmetric",
        "hashlib",
        "hmac",
        "ipaddress",
        "json",
        "pathlib",
        "socket",
        "threading",
        "time",
        "typing",
        "urllib.parse",
        "urllib.request"
      ],
      "skilgen/core/config.py": [
        "__future__",
        "pathlib",
        "skilgen/core/models.py"
      ],
      "skilgen/core/context.py": [
        "__future__",
        "pathlib",
        "skilgen/agents/codebase_signals.py",
        "skilgen/agents/domain_graph_planner.py",
        "skilgen/agents/framework_fingerprint.py",
        "skilgen/agents/workspace_graph.py",
        "skilgen/core/models.py"
      ],
      "skilgen/core/corpus_index.py": [
        "__future__",
        "collections",
        "fnmatch",
        "hashlib",
        "json",
        "pathlib",
        "re",
        "skilgen/agents/codebase_signals.py",
        "skilgen/agents/language_parsers.py",
        "skilgen/core/config.py",
        "skilgen/core/document_ingestion.py",
        "skilgen/core/models.py",
        "typing"
      ],
      "skilgen/core/deep_sampler.py": [
        "__future__",
        "pathlib",
        "skilgen/core/config.py",
        "skilgen/core/models.py",
        "typing"
      ],
      "skilgen/core/dependency_risk.py": [
        "__future__",
        "json",
        "pathlib",
        "re",
        "skilgen/agents/relationship_mapper.py",
        "skilgen/agents/workspace_graph.py",
        "skilgen/core/models.py",
        "tomllib"
      ],
      "skilgen/core/diff.py": [
        "__future__",
        "pathlib",
        "skilgen/core/context.py",
        "skilgen/core/freshness.py",
        "skilgen/core/repo_state.py",
        "skilgen/core/requirements.py",
        "skilgen/core/score.py"
      ],
      "skilgen/core/document_ingestion.py": [
        "__future__",
        "bs4",
        "csv",
        "html",
        "json",
        "openpyxl",
        "pathlib",
        "pptx",
        "pypdf",
        "re",
        "tomllib",
        "xml.etree.ElementTree",
        "yaml",
        "zipfile"
      ],
      "skilgen/core/enterprise_policy.py": [
        "__future__",
        "dataclasses",
        "datetime",
        "pathlib",
        "skilgen/core/dependency_risk.py",
        "skilgen/core/score.py",
        "skilgen/enterprise_skills.py",
        "skilgen/external_skills.py",
        "typing",
        "yaml"
      ],
      "skilgen/core/evals.py": [
        "__future__",
        "json",
        "pathlib"
      ],
      "skilgen/core/freshness.py": [
        "__future__",
        "dataclasses",
        "hashlib",
        "json",
        "pathlib",
        "skilgen/core/generated_outputs.py",
        "skilgen/core/models.py"
      ],
      "skilgen/core/generated_outputs.py": [
        "__future__",
        "pathlib"
      ],
      "skilgen/core/identity_policy_store.py": [
        "__future__",
        "contextlib",
        "datetime",
        "json",
        "os",
        "pathlib",
        "sqlite3",
        "typing"
      ],
      "skilgen/core/models.py": [
        "__future__",
        "dataclasses",
        "pathlib"
      ],
      "skilgen/core/project_memory.py": [
        "__future__",
        "dataclasses",
        "json",
        "pathlib",
        "skilgen/core/models.py"
      ],
      "skilgen/core/rate_limit_store.py": [
        "__future__",
        "math",
        "os",
        "pathlib",
        "sqlite3"
      ],
      "skilgen/core/repo_state.py": [
        "__future__",
        "pathlib",
        "re",
        "shutil",
        "skilgen/agents/language_parsers.py",
        "subprocess"
      ],
      "skilgen/core/requirements.py": [
        "__future__",
        "hashlib",
        "json",
        "pathlib",
        "skilgen/agents/codebase_signals.py",
        "skilgen/core/document_ingestion.py",
        "skilgen/core/models.py"
      ],
      "skilgen/core/run_memory.py": [
        "__future__",
        "dataclasses",
        "json",
        "pathlib",
        "skilgen/core/models.py",
        "uuid"
      ],
      "skilgen/core/runtime_data.py": [
        "__future__",
        "pathlib",
        "shutil",
        "skilgen/core/config.py",
        "time"
      ],
      "skilgen/core/runtime_signals.py": [
        "__future__",
        "json",
        "pathlib",
        "re",
        "skilgen/core/models.py",
        "xml.etree"
      ],
      "skilgen/core/score.py": [
        "__future__",
        "datetime",
        "html",
        "json",
        "pathlib",
        "re",
        "skilgen/agents/codebase_signals.py",
        "skilgen/core/context.py",
        "skilgen/core/freshness.py",
        "skilgen/core/requirements.py",
        "skilgen/core/validation.py",
        "subprocess",
        "threading",
        "urllib.parse"
      ],
      "skilgen/core/validation.py": [
        "__future__",
        "pathlib",
        "skilgen/agents/codebase_signals.py",
        "skilgen/deep_agents_core.py"
      ],
      "skilgen/deep_agents_core.py": [
        "__future__",
        "asyncio",
        "deepagents",
        "json",
        "langchain.chat_models",
        "os",
        "pathlib",
        "queue",
        "skilgen/agents/model_registry.py",
        "skilgen/core/config.py",
        "threading",
        "time",
        "typing"
      ],
      "skilgen/deep_agents_runtime.py": [
        "__future__",
        "dataclasses",
        "deepagents",
        "json",
        "langchain.chat_models",
        "langchain_core.tools",
        "os",
        "pathlib",
        "skilgen/agents/codebase_signals.py",
        "skilgen/agents/decision_planner.py",
        "skilgen/agents/domain_graph_planner.py",
        "skilgen/agents/evidence_graph.py",
        "skilgen/agents/feature_extractor.py",
        "skilgen/agents/framework_fingerprint.py",
        "skilgen/agents/model_registry.py",
        "skilgen/agents/relationship_mapper.py",
        "skilgen/agents/requirements_parser.py",
        "skilgen/agents/roadmap_planner.py",
        "skilgen/agents/workspace_graph.py",
        "skilgen/autoupdate.py",
        "skilgen/core/analytics.py",
        "skilgen/core/config.py",
        "skilgen/core/context.py",
        "skilgen/core/corpus_index.py",
        "skilgen/core/diff.py",
        "skilgen/core/freshness.py",
        "skilgen/core/requirements.py",
        "skilgen/core/score.py",
        "skilgen/core/validation.py",
        "skilgen/deep_agents_core.py",
        "skilgen/enterprise_skills.py",
        "skilgen/external_skills.py",
        "skilgen/generators/package.py",
        "skilgen/generators/skills.py",
        "typing"
      ],
      "skilgen/delivery.py": [
        "__future__",
        "dataclasses",
        "pathlib",
        "skilgen/agents/__init__.py",
        "skilgen/agents/codebase_signals.py",
        "skilgen/agents/source_graphs.py",
        "skilgen/core/analytics.py",
        "skilgen/core/audit.py",
        "skilgen/core/config.py",
        "skilgen/core/context.py",
        "skilgen/core/corpus_index.py",
        "skilgen/core/freshness.py",
        "skilgen/core/generated_outputs.py",
        "skilgen/core/models.py",
        "skilgen/core/repo_state.py",
        "skilgen/core/requirements.py",
        "skilgen/core/run_memory.py",
        "skilgen/core/runtime_data.py",
        "skilgen/core/score.py",
        "skilgen/deep_agents_core.py",
        "skilgen/enterprise_skills.py",
        "skilgen/external_skills.py",
        "skilgen/generators/package.py",
        "skilgen/generators/skills.py",
        "time",
        "typing"
      ],
      "skilgen/enterprise_skills.py": [
        "__future__",
        "dataclasses",
        "datetime",
        "json",
        "os",
        "pathlib",
        "re",
        "shutil",
        "skilgen/core/config.py",
        "skilgen/core/document_ingestion.py",
        "subprocess",
        "urllib.parse",
        "urllib.request"
      ],
      "skilgen/external_skills.py": [
        "__future__",
        "dataclasses",
        "datetime",
        "json",
        "os",
        "pathlib",
        "re",
        "shutil",
        "skilgen/core/config.py",
        "subprocess"
      ],
      "skilgen/generators/__init__.py": [],
      "skilgen/generators/package.py": [
        "__future__",
        "dataclasses",
        "datetime",
        "html",
        "json",
        "pathlib",
        "re",
        "skilgen/agents/__init__.py",
        "skilgen/agents/feature_extractor.py",
        "skilgen/agents/requirements_parser.py",
        "skilgen/core/config.py",
        "skilgen/core/context.py",
        "skilgen/core/models.py",
        "skilgen/deep_agents_core.py",
        "skilgen/deep_agents_runtime.py",
        "skilgen/enterprise_skills.py",
        "skilgen/external_skills.py",
        "sys",
        "typing"
      ],
      "skilgen/generators/skills.py": [
        "__future__",
        "datetime",
        "os",
        "pathlib",
        "skilgen/agents/architecture_planner.py",
        "skilgen/agents/codebase_signals.py",
        "skilgen/agents/requirements_parser.py",
        "skilgen/agents/roadmap_planner.py",
        "skilgen/core/config.py",
        "skilgen/core/context.py",
        "skilgen/core/dependency_risk.py",
        "skilgen/core/models.py",
        "skilgen/deep_agents_core.py",
        "typing"
      ],
      "skilgen/registry_client.py": [
        "__future__",
        "json",
        "os",
        "pathlib",
        "typing",
        "urllib.error",
        "urllib.request"
      ],
      "skilgen/sdk.py": [
        "__future__",
        "pathlib",
        "skilgen/api/service.py",
        "skilgen/autoupdate.py",
        "skilgen/core/config.py",
        "skilgen/core/evals.py",
        "skilgen/delivery.py",
        "skilgen/enterprise_skills.py",
        "skilgen/external_skills.py"
      ],
      "tests/__init__.py": [],
      "tests/oidc_test_utils.py": [
        "__future__",
        "base64",
        "cryptography.hazmat.primitives",
        "cryptography.hazmat.primitives.asymmetric",
        "http.server",
        "json",
        "pathlib",
        "threading",
        "time",
        "typing"
      ],
      "tests/test_analytics.py": [
        "pathlib",
        "skilgen/core/analytics.py",
        "skilgen/generators/package.py",
        "tempfile",
        "unittest"
      ],
      "tests/test_api_smoke.py": [
        "__future__",
        "io",
        "json",
        "logging",
        "os",
        "pathlib",
        "skilgen/api/server.py",
        "skilgen/core/auth_tokens.py",
        "subprocess",
        "tempfile",
        "tests/oidc_test_utils.py",
        "threading",
        "time",
        "unittest",
        "urllib.error",
        "urllib.parse",
        "urllib.request"
      ],
      "tests/test_architecture_cli.py": [
        "json",
        "pathlib",
        "subprocess",
        "sys",
        "tempfile",
        "unittest"
      ],
      "tests/test_architecture_planner.py": [
        "pathlib",
        "skilgen/agents/architecture_planner.py",
        "skilgen/core/models.py",
        "tempfile",
        "unittest"
      ],
      "tests/test_audit.py": [
        "__future__",
        "os",
        "pathlib",
        "skilgen/core/audit.py",
        "tempfile",
        "unittest",
        "unittest.mock"
      ],
      "tests/test_auth_claim_mapping.py": [
        "__future__",
        "json",
        "os",
        "pathlib",
        "skilgen/api/server.py",
        "tempfile",
        "unittest"
      ],
      "tests/test_auth_tokens.py": [
        "__future__",
        "pathlib",
        "skilgen/core/auth_tokens.py",
        "tempfile",
        "tests/oidc_test_utils.py",
        "time",
        "unittest"
      ],
      "tests/test_autoupdate.py": [
        "pathlib",
        "skilgen/autoupdate.py",
        "tempfile",
        "unittest"
      ],
      "tests/test_cli.py": [
        "json",
        "pathlib",
        "subprocess",
        "sys",
        "tempfile",
        "unittest"
      ],
      "tests/test_codebase_signals.py": [
        "pathlib",
        "skilgen/agents/codebase_signals.py",
        "tempfile",
        "unittest"
      ],
      "tests/test_config.py": [
        "pathlib",
        "skilgen/core/config.py",
        "tempfile",
        "unittest"
      ],
      "tests/test_context.py": [
        "pathlib",
        "skilgen/core/context.py",
        "skilgen/core/requirements.py",
        "tempfile",
        "unittest"
      ],
      "tests/test_corpus_cli.py": [
        "json",
        "pathlib",
        "subprocess",
        "sys",
        "tempfile",
        "unittest"
      ],
      "tests/test_corpus_index.py": [
        "pathlib",
        "skilgen/agents/codebase_signals.py",
        "skilgen/core/corpus_index.py",
        "skilgen/core/deep_sampler.py",
        "tempfile",
        "unittest"
      ],
      "tests/test_dashboard_cli.py": [
        "contextlib",
        "datetime",
        "io",
        "json",
        "pathlib",
        "skilgen/autoupdate.py",
        "skilgen/cli/main.py",
        "skilgen/core/requirements.py",
        "skilgen/generators/package.py",
        "subprocess",
        "sys",
        "tempfile",
        "unittest",
        "unittest.mock"
      ],
      "tests/test_decision_planner.py": [
        "pathlib",
        "skilgen/agents/decision_planner.py",
        "skilgen/core/context.py",
        "skilgen/core/requirements.py",
        "skilgen/external_skills.py",
        "subprocess",
        "tempfile",
        "unittest"
      ],
      "tests/test_delivery.py": [
        "pathlib",
        "skilgen/core/models.py",
        "skilgen/core/score.py",
        "skilgen/delivery.py",
        "tempfile",
        "unittest",
        "unittest.mock"
      ],
      "tests/test_dependency_risk.py": [
        "json",
        "pathlib",
        "skilgen/core/dependency_risk.py",
        "tempfile",
        "unittest"
      ],
      "tests/test_dependency_risk_graph_workstream.py": [
        "__future__",
        "apps/api/api/routes/repos.py",
        "datetime",
        "json",
        "pathlib",
        "skilgen/core/dependency_risk.py",
        "tempfile",
        "types"
      ],
      "tests/test_diff.py": [
        "json",
        "pathlib",
        "skilgen/core/context.py",
        "skilgen/core/diff.py",
        "skilgen/core/freshness.py",
        "skilgen/core/requirements.py",
        "subprocess",
        "sys",
        "tempfile",
        "unittest"
      ],
      "tests/test_document_ingestion.py": [
        "__future__",
        "openpyxl",
        "pathlib",
        "pptx",
        "skilgen/core/document_ingestion.py",
        "skilgen/core/requirements.py",
        "tempfile",
        "unittest",
        "zipfile"
      ],
      "tests/test_domain_graph_planner.py": [
        "pathlib",
        "skilgen/agents/domain_graph_planner.py",
        "skilgen/core/requirements.py",
        "tempfile",
        "unittest",
        "unittest.mock"
      ],
      "tests/test_enterprise_document_formats.py": [
        "__future__",
        "pathlib",
        "skilgen/core/document_ingestion.py",
        "skilgen/enterprise_skills.py",
        "tempfile",
        "unittest"
      ],
      "tests/test_enterprise_policy_cli.py": [
        "__future__",
        "datetime",
        "json",
        "pathlib",
        "subprocess",
        "sys",
        "tempfile"
      ],
      "tests/test_feature_extractor.py": [
        "pathlib",
        "skilgen/agents/feature_extractor.py",
        "tempfile",
        "unittest"
      ],
      "tests/test_framework_fingerprint.py": [
        "pathlib",
        "skilgen/agents/framework_fingerprint.py",
        "tempfile",
        "unittest"
      ],
      "tests/test_identity_policy_store.py": [
        "__future__",
        "os",
        "pathlib",
        "skilgen/core/identity_policy_store.py",
        "tempfile",
        "unittest"
      ],
      "tests/test_jobs.py": [
        "contextlib",
        "pathlib",
        "skilgen/api/jobs.py",
        "skilgen/api/service.py",
        "sqlite3",
        "tempfile",
        "time",
        "unittest"
      ],
      "tests/test_model_registry.py": [
        "os",
        "skilgen/agents/model_registry.py",
        "skilgen/core/models.py",
        "unittest"
      ],
      "tests/test_org_settings.py": [
        "__future__",
        "apps/api/api/analysis.py",
        "apps/api/api/auth.py",
        "apps/api/api/routes/orgs.py",
        "asyncio",
        "datetime",
        "fastapi",
        "fastapi.testclient",
        "packages/db/database.py",
        "pathlib",
        "sqlalchemy.exc",
        "types",
        "typing"
      ],
      "tests/test_overview_data.py": [
        "__future__",
        "packages/db/schemas.py",
        "pathlib"
      ],
      "tests/test_packaging.py": [
        "os",
        "pathlib",
        "shutil",
        "subprocess",
        "sys",
        "tempfile",
        "time",
        "unittest"
      ],
      "tests/test_plan_cli.py": [
        "json",
        "pathlib",
        "subprocess",
        "sys",
        "tempfile",
        "unittest"
      ],
      "tests/test_pr_comment.py": [
        "__future__",
        "apps/api/api/pr_comment.py",
        "unittest"
      ],
      "tests/test_pr_comment_dedup.py": [
        "__future__",
        "apps/api/api/pr_comment.py",
        "httpx",
        "pytest",
        "typing"
      ],
      "tests/test_rate_limit_store.py": [
        "__future__",
        "pathlib",
        "skilgen/core/rate_limit_store.py",
        "tempfile",
        "unittest"
      ],
      "tests/test_registry_api.py": [
        "__future__",
        "apps/api/api/auth.py",
        "apps/api/api/routes/registry.py",
        "datetime",
        "fastapi",
        "fastapi.testclient",
        "packages/db/database.py",
        "types",
        "typing"
      ],
      "tests/test_registry_cli.py": [
        "__future__",
        "http.server",
        "json",
        "os",
        "pathlib",
        "subprocess",
        "sys",
        "tempfile",
        "threading",
        "typing",
        "unittest"
      ],
      "tests/test_registry_dashboard.py": [
        "__future__",
        "pathlib"
      ],
      "tests/test_relationship_mapper.py": [
        "pathlib",
        "skilgen/agents/relationship_mapper.py",
        "tempfile",
        "unittest"
      ],
      "tests/test_repos_screen.py": [
        "__future__",
        "pathlib"
      ],
      "tests/test_requirements.py": [
        "json",
        "pathlib",
        "skilgen/core/requirements.py",
        "tempfile",
        "unittest"
      ],
      "tests/test_requirements_parser.py": [
        "pathlib",
        "skilgen/agents/requirements_parser.py",
        "tempfile",
        "unittest"
      ],
      "tests/test_roadmap_planner.py": [
        "skilgen/agents/roadmap_planner.py",
        "skilgen/core/models.py",
        "unittest"
      ],
      "tests/test_roadmap_skills.py": [
        "pathlib",
        "skilgen/core/requirements.py",
        "skilgen/generators/skills.py",
        "tempfile",
        "unittest"
      ],
      "tests/test_run_memory.py": [
        "pathlib",
        "skilgen/core/models.py",
        "skilgen/core/run_memory.py",
        "tempfile",
        "unittest"
      ],
      "tests/test_runtime_hardening.py": [
        "os",
        "pathlib",
        "skilgen/deep_agents_core.py",
        "tempfile",
        "time",
        "types",
        "unittest",
        "unittest.mock"
      ],
      "tests/test_runtime_signals.py": [
        "json",
        "pathlib",
        "skilgen/core/runtime_signals.py",
        "tempfile",
        "unittest"
      ],
      "tests/test_score.py": [
        "pathlib",
        "skilgen/core/repo_state.py",
        "skilgen/core/score.py",
        "subprocess",
        "tempfile",
        "threading",
        "unittest",
        "unittest.mock"
      ],
      "tests/test_score_quality_system.py": [
        "__future__",
        "apps/api/api/routes/orgs.py",
        "apps/api/api/routes/repos.py",
        "datetime",
        "fastapi",
        "fastapi.testclient",
        "json",
        "packages/db/database.py",
        "pathlib",
        "pytest",
        "skilgen/core/score.py",
        "subprocess",
        "sys",
        "tempfile",
        "types",
        "typing"
      ],
      "tests/test_sdk.py": [
        "json",
        "pathlib",
        "skilgen/external_skills.py",
        "skilgen/sdk.py",
        "subprocess",
        "tempfile",
        "time",
        "unittest",
        "unittest.mock"
      ],
      "tests/test_skill_detail.py": [
        "__future__",
        "apps/api/api/routes/skills.py",
        "asyncio",
        "pathlib",
        "types"
      ],
      "tests/test_skill_usage_analytics.py": [
        "__future__",
        "apps/api/api/routes/admin.py",
        "apps/api/api/routes/orgs.py",
        "apps/api/api/routes/skills.py",
        "asyncio",
        "datetime",
        "fastapi",
        "fastapi.testclient",
        "packages/db/config.py",
        "packages/db/database.py",
        "pathlib",
        "types",
        "typing"
      ],
      "tests/test_skillayer_api_infra.py": [
        "__future__",
        "apps/api/api/auth.py",
        "apps/api/api/index.py",
        "apps/api/api/routes/metrics.py",
        "apps/api/api/routes/webhook.py",
        "datetime",
        "fastapi",
        "fastapi.testclient",
        "hashlib",
        "hmac",
        "packages/db/config.py",
        "packages/db/models/Base.py",
        "packages/db/models/Org.py",
        "packages/db/models/Repo.py",
        "pytest"
      ],
      "tests/test_source_graphs.py": [
        "pathlib",
        "skilgen/agents/language_parsers.py",
        "skilgen/agents/source_graphs.py",
        "tempfile",
        "unittest"
      ],
      "tests/test_stripe_portal.py": [
        "__future__",
        "apps/api/api/auth.py",
        "apps/api/api/routes/stripe.py",
        "fastapi",
        "fastapi.testclient",
        "packages/db/database.py",
        "pytest",
        "types",
        "typing"
      ],
      "tests/test_stripe_webhook.py": [
        "__future__",
        "apps/api/api/auth.py",
        "apps/api/api/routes/stripe.py",
        "fastapi",
        "fastapi.testclient",
        "json",
        "packages/db/database.py",
        "packages/db/models/Org.py",
        "pytest",
        "types",
        "typing"
      ],
      "tests/test_upgrade_flow.py": [
        "pathlib",
        "unittest"
      ],
      "tests/test_validate_cli.py": [
        "json",
        "subprocess",
        "sys",
        "unittest"
      ],
      "tests/test_vercel_api_deploy.py": [
        "__future__",
        "json",
        "pathlib",
        "scripts/deploy_api.py"
      ],
      "tests/test_vercel_dashboard_deploy.py": [
        "__future__",
        "json",
        "pathlib",
        "scripts/deploy_dashboard.py"
      ],
      "tests/test_workspace_graph.py": [
        "pathlib",
        "skilgen/agents/workspace_graph.py",
        "tempfile",
        "unittest"
      ]
    },
    "items": [
      {
        "path": "CODEBASE_ONLY",
        "kind": "requirements",
        "language": null,
        "tags": [
          "requirements"
        ],
        "snippet": [
          "Codebase-only mode: no requirements file supplied.",
          "Detected backend-oriented structure from routes, services, or server files.",
          "Detected frontend-oriented structure from routes, pages, or component files.",
          "Scanned 543 files from the project root.",
          "Observed: .env.example",
          "Observed: .env.local",
          "Observed: .github/CODEOWNERS",
          "Observed: .github/ISSUE_TEMPLATE/bug_report.yml"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/langgraph/typing.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "from typing_extensions import TypeVar",
          "from langgraph._internal._typing import StateLike",
          "__all__ = (",
          "\"StateT\",",
          "\"StateT_co\",",
          "\"StateT_contra\",",
          "\"InputT\",",
          "\"OutputT\",",
          "\"ContextT\",",
          ")",
          "StateT = TypeVar(\"StateT\", bound=StateLike)"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/typing_extensions.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "import abc",
          "import builtins",
          "import collections",
          "import collections.abc",
          "import contextlib",
          "import enum",
          "import functools",
          "import inspect",
          "import io",
          "import keyword",
          "import operator",
          "import sys"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/openai/_models.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "import os",
          "import inspect",
          "import weakref",
          "from typing import (",
          "IO,",
          "TYPE_CHECKING,",
          "Any,",
          "Type,",
          "Tuple,",
          "Union,",
          "Generic,"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/_pytest/logging.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "# mypy: allow-untyped-defs",
          "\"\"\"Access and control log capturing.\"\"\"",
          "from __future__ import annotations",
          "from collections.abc import Generator",
          "from collections.abc import Mapping",
          "from collections.abc import Set as AbstractSet",
          "from contextlib import contextmanager",
          "from contextlib import nullcontext",
          "from datetime import datetime",
          "from datetime import timedelta",
          "from datetime import timezone",
          "import io"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/anyio/functools.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "__all__ = (",
          "\"AsyncCacheInfo\",",
          "\"AsyncCacheParameters\",",
          "\"AsyncLRUCacheWrapper\",",
          "\"cache\",",
          "\"lru_cache\",",
          "\"reduce\",",
          ")",
          "import functools",
          "import sys",
          "from collections import OrderedDict"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/openpyxl/utils/datetime.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "# Copyright (c) 2010-2024 openpyxl",
          "\"\"\"Manage Excel date weirdness.\"\"\"",
          "# Python stdlib imports",
          "import datetime",
          "from math import isnan",
          "import re",
          "MAC_EPOCH = datetime.datetime(1904, 1, 1)",
          "WINDOWS_EPOCH = datetime.datetime(1899, 12, 30)",
          "CALENDAR_WINDOWS_1900 = 2415018.5   # Julian date of WINDOWS_EPOCH",
          "CALENDAR_MAC_1904 = 2416480.5       # Julian date of MAC_EPOCH",
          "CALENDAR_WINDOWS_1900 = WINDOWS_EPOCH",
          "CALENDAR_MAC_1904 = MAC_EPOCH"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/_pytest/pathlib.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "import atexit",
          "from collections.abc import Callable",
          "from collections.abc import Iterable",
          "from collections.abc import Iterator",
          "import contextlib",
          "from enum import Enum",
          "from errno import EBADF",
          "from errno import ELOOP",
          "from errno import ENOENT",
          "from errno import ENOTDIR",
          "import fnmatch"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/_pytest/warnings.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "# mypy: allow-untyped-defs",
          "from __future__ import annotations",
          "from collections.abc import Generator",
          "from contextlib import contextmanager",
          "from contextlib import ExitStack",
          "import sys",
          "from typing import Literal",
          "import warnings",
          "from _pytest.config import apply_warning_filters",
          "from _pytest.config import Config",
          "from _pytest.config import parse_warning_filter",
          "from _pytest.main import Session"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/anthropic/_models.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "import os",
          "import inspect",
          "import weakref",
          "from typing import (",
          "IO,",
          "TYPE_CHECKING,",
          "Any,",
          "Type,",
          "Union,",
          "Generic,",
          "TypeVar,"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/celery/utils/collections.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "\"\"\"Custom maps, sets, sequences, and other data structures.\"\"\"",
          "import time",
          "from collections import OrderedDict as _OrderedDict",
          "from collections import deque",
          "from collections.abc import Callable, Mapping, MutableMapping, MutableSet, Sequence",
          "from heapq import heapify, heappop, heappush",
          "from itertools import chain, count",
          "from queue import Empty",
          "from typing import Any, Dict, Iterable, List  # noqa",
          "from .functional import first, uniq",
          "from .text import match_case",
          "try:"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/fsspec/json.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "import json",
          "from collections.abc import Callable, Mapping, Sequence",
          "from contextlib import suppress",
          "from pathlib import PurePath",
          "from typing import Any, ClassVar",
          "from .registry import _import_class, get_filesystem_class",
          "from .spec import AbstractFileSystem",
          "class FilesystemJSONEncoder(json.JSONEncoder):",
          "include_password: ClassVar[bool] = True",
          "def default(self, o: Any) -> Any:",
          "if isinstance(o, AbstractFileSystem):",
          "return o.to_dict(include_password=self.include_password)"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/huggingface_hub/dataclasses.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "import collections.abc",
          "import inspect",
          "import types",
          "from collections.abc import Callable",
          "from dataclasses import _MISSING_TYPE, MISSING, Field, field, fields, make_dataclass",
          "from functools import lru_cache, wraps",
          "from typing import (",
          "Annotated,",
          "Any,",
          "ForwardRef,",
          "Literal,",
          "Type,"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/celery/utils/time.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "\"\"\"Utilities related to dates, times, intervals, and timezones.\"\"\"",
          "from __future__ import annotations",
          "import logging",
          "import numbers",
          "import os",
          "import random",
          "import sys",
          "import time as _time",
          "from calendar import monthrange",
          "from datetime import date, datetime, timedelta",
          "from datetime import timezone as datetime_timezone",
          "from datetime import tzinfo"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/alembic/autogenerate/compare/types.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "import logging",
          "from typing import Any",
          "from typing import Optional",
          "from typing import TYPE_CHECKING",
          "from typing import Union",
          "from sqlalchemy import types as sqltypes",
          "from ...util import DispatchPriority",
          "from ...util import PriorityDispatchResult",
          "if TYPE_CHECKING:",
          "from sqlalchemy.sql.elements import quoted_name",
          "from sqlalchemy.sql.schema import Column"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/pip/_internal/commands/inspect.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "import logging",
          "from optparse import Values",
          "from typing import Any",
          "from pip._vendor.packaging.markers import default_environment",
          "from pip._vendor.rich import print_json",
          "from pip import __version__",
          "from pip._internal.cli import cmdoptions",
          "from pip._internal.cli.base_command import Command",
          "from pip._internal.cli.status_codes import SUCCESS",
          "from pip._internal.metadata import BaseDistribution, get_environment",
          "from pip._internal.utils.compat import stdlib_pkgs",
          "from pip._internal.utils.urls import path_to_url"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/langchain_core/output_parsers/pydantic.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "\"\"\"Output parsers using Pydantic.\"\"\"",
          "import json",
          "from typing import Annotated, Generic, Literal, overload",
          "import pydantic",
          "from pydantic import SkipValidation",
          "from typing_extensions import override",
          "from langchain_core.exceptions import OutputParserException",
          "from langchain_core.output_parsers import JsonOutputParser",
          "from langchain_core.outputs import Generation",
          "from langchain_core.utils.pydantic import (",
          "PydanticBaseModel,",
          "TBaseModel,"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/openpyxl/compat/abc.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "# Copyright (c) 2010-2024 openpyxl",
          "try:",
          "from abc import ABC",
          "except ImportError:",
          "from abc import ABCMeta",
          "ABC = ABCMeta('ABC', (object, ), {})"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/filelock/asyncio.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "\"\"\"An asyncio-based implementation of the file lock.\"\"\"",
          "from __future__ import annotations",
          "import asyncio",
          "import contextlib",
          "import logging",
          "import os",
          "import time",
          "from dataclasses import dataclass",
          "from inspect import iscoroutinefunction",
          "from threading import local",
          "from typing import TYPE_CHECKING, Any, NoReturn, TypeVar",
          "from ._api import _UNSET_FILE_MODE, BaseFileLock, FileLockContext, FileLockMeta"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/tqdm/contrib/itertools.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "\"\"\"",
          "Thin wrappers around `itertools`.",
          "\"\"\"",
          "import itertools",
          "from ..auto import tqdm as tqdm_auto",
          "__author__ = {\"github.com/\": [\"casperdcl\"]}",
          "__all__ = ['product']",
          "def product(*iterables, **tqdm_kwargs):",
          "\"\"\"",
          "Equivalent of `itertools.product`.",
          "Parameters",
          "tqdm_class  : [default: tqdm.auto.tqdm]."
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/celery/contrib/pytest.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "\"\"\"Fixtures and testing utilities for :pypi:`pytest <pytest>`.\"\"\"",
          "import os",
          "from contextlib import contextmanager",
          "from typing import TYPE_CHECKING, Any, Mapping, Sequence, Union  # noqa",
          "import pytest",
          "if TYPE_CHECKING:",
          "from celery import Celery",
          "from ..worker import WorkController",
          "else:",
          "Celery = WorkController = object",
          "NO_WORKER = os.environ.get('NO_WORKER')",
          "def pytest_configure(config):"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/openai/_utils/__init__.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from ._logs import SensitiveHeadersFilter as SensitiveHeadersFilter",
          "from ._path import path_template as path_template",
          "from ._sync import asyncify as asyncify",
          "from ._proxy import LazyProxy as LazyProxy",
          "from ._utils import (",
          "flatten as flatten,",
          "is_dict as is_dict,",
          "is_list as is_list,",
          "is_given as is_given,",
          "is_tuple as is_tuple,",
          "json_safe as json_safe,",
          "lru_cache as lru_cache,"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/anthropic/_utils/__init__.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from ._path import path_template as path_template",
          "from ._sync import asyncify as asyncify",
          "from ._proxy import LazyProxy as LazyProxy",
          "from ._utils import (",
          "flatten as flatten,",
          "is_dict as is_dict,",
          "is_list as is_list,",
          "is_given as is_given,",
          "is_tuple as is_tuple,",
          "json_safe as json_safe,",
          "lru_cache as lru_cache,",
          "is_mapping as is_mapping,"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/openai/_types.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "from os import PathLike",
          "from typing import (",
          "IO,",
          "TYPE_CHECKING,",
          "Any,",
          "Dict,",
          "List,",
          "Type,",
          "Tuple,",
          "Union,",
          "Mapping,"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/redis/_parsers/socket.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "import errno",
          "import io",
          "import socket",
          "from io import SEEK_END",
          "from typing import Optional, Union",
          "from ..exceptions import ConnectionError, TimeoutError",
          "from ..utils import SSL_AVAILABLE",
          "NONBLOCKING_EXCEPTION_ERROR_NUMBERS = {BlockingIOError: errno.EWOULDBLOCK}",
          "if SSL_AVAILABLE:",
          "import ssl",
          "if hasattr(ssl, \"SSLWantReadError\"):",
          "NONBLOCKING_EXCEPTION_ERROR_NUMBERS[ssl.SSLWantReadError] = 2"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/fsspec/tests/abstract/copy.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from hashlib import md5",
          "from itertools import product",
          "import pytest",
          "from fsspec.tests.abstract.common import GLOB_EDGE_CASES_TESTS",
          "class AbstractCopyTests:",
          "def test_copy_file_to_existing_directory(",
          "self,",
          "fs,",
          "fs_join,",
          "fs_bulk_operations_scenario_0,",
          "fs_target,",
          "supports_empty_directories,"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/sqlalchemy/util/typing.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "# util/typing.py",
          "# Copyright (C) 2022-2026 the SQLAlchemy authors and contributors",
          "# <see AUTHORS file>",
          "from __future__ import annotations",
          "import builtins",
          "from collections import deque",
          "import collections.abc as collections_abc",
          "import re",
          "import sys",
          "import typing",
          "from typing import Any",
          "from typing import Callable"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/pip/_internal/utils/subprocess.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "import logging",
          "import os",
          "import shlex",
          "import subprocess",
          "from collections.abc import Iterable, Mapping",
          "from typing import Any, Callable, Literal, Union",
          "from pip._vendor.rich.markup import escape",
          "from pip._internal.cli.spinners import SpinnerInterface, open_spinner",
          "from pip._internal.exceptions import InstallationSubprocessError",
          "from pip._internal.utils.logging import VERBOSE, subprocess_logger",
          "from pip._internal.utils.misc import HiddenText"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/kombu/utils/uuid.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "\"\"\"UUID utilities.\"\"\"",
          "from __future__ import annotations",
          "from typing import Callable",
          "from uuid import UUID, uuid4",
          "def uuid(_uuid: Callable[[], UUID] = uuid4) -> str:",
          "\"\"\"Generate unique id in UUID4 format.",
          "See Also",
          "For now this is provided by :func:`uuid.uuid4`.",
          "\"\"\"",
          "return str(_uuid())"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/_pytest/unittest.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "# mypy: allow-untyped-defs",
          "\"\"\"Discover and run std-library \"unittest\" style tests.\"\"\"",
          "from __future__ import annotations",
          "from collections.abc import Callable",
          "from collections.abc import Generator",
          "from collections.abc import Iterable",
          "from collections.abc import Iterator",
          "from enum import auto",
          "from enum import Enum",
          "import inspect",
          "import sys",
          "import traceback"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/google/genai/_interactions/_models.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "# Copyright 2025 Google LLC",
          "#",
          "# Licensed under the Apache License, Version 2.0 (the \"License\");",
          "from __future__ import annotations",
          "import os",
          "import inspect",
          "import weakref",
          "from typing import (",
          "IO,",
          "TYPE_CHECKING,",
          "Any,",
          "Type,"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/pygments/lexers/math.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "\"\"\"",
          "pygments.lexers.math",
          "~~~~~~~~~~~~~~~~~~~~",
          "Just export lexers that were contained in this module.",
          ":copyright: Copyright 2006-present by the Pygments team, see AUTHORS.",
          ":license: BSD, see LICENSE for details.",
          "\"\"\"",
          "from pygments.lexers.python import NumPyLexer",
          "from pygments.lexers.matlab import MatlabLexer, MatlabSessionLexer, \\",
          "OctaveLexer, ScilabLexer",
          "from pygments.lexers.julia import JuliaLexer, JuliaConsoleLexer",
          "from pygments.lexers.r import RConsoleLexer, SLexer, RdLexer"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/sqlalchemy/sql/__init__.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "# sql/__init__.py",
          "# Copyright (C) 2005-2026 the SQLAlchemy authors and contributors",
          "# <see AUTHORS file>",
          "from typing import Any",
          "from typing import TYPE_CHECKING",
          "from ._typing import ColumnExpressionArgument as ColumnExpressionArgument",
          "from ._typing import NotNullable as NotNullable",
          "from ._typing import Nullable as Nullable",
          "from .base import Executable as Executable",
          "from .compiler import COLLECT_CARTESIAN_PRODUCTS as COLLECT_CARTESIAN_PRODUCTS",
          "from .compiler import FROM_LINTING as FROM_LINTING",
          "from .compiler import NO_LINTING as NO_LINTING"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/sqlalchemy/sql/elements.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "# sql/elements.py",
          "# Copyright (C) 2005-2026 the SQLAlchemy authors and contributors",
          "# <see AUTHORS file>",
          "\"\"\"Core SQL expression elements, including :class:`_expression.ClauseElement`,",
          ":class:`_expression.ColumnElement`, and derived classes.",
          "\"\"\"",
          "from __future__ import annotations",
          "from decimal import Decimal",
          "from enum import Enum",
          "import itertools",
          "import operator",
          "import re"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/requests_toolbelt/adapters/ssl.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "# -*- coding: utf-8 -*-",
          "\"\"\"",
          "requests_toolbelt.ssl_adapter",
          "=============================",
          "This file contains an implementation of the SSLAdapter originally demonstrated",
          "in this blog post:",
          "https://lukasa.co.uk/2013/01/Choosing_SSL_Version_In_Requests/",
          "\"\"\"",
          "import requests",
          "from requests.adapters import HTTPAdapter",
          "from .._compat import poolmanager",
          "class SSLAdapter(HTTPAdapter):"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/anthropic/_types.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "from os import PathLike",
          "from typing import (",
          "IO,",
          "TYPE_CHECKING,",
          "Any,",
          "Dict,",
          "List,",
          "Type,",
          "Tuple,",
          "Union,",
          "Mapping,"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/openai/_compat.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "from typing import TYPE_CHECKING, Any, Union, Generic, TypeVar, Callable, cast, overload",
          "from datetime import date, datetime",
          "from typing_extensions import Self, Literal, TypedDict",
          "import pydantic",
          "from pydantic.fields import FieldInfo",
          "from ._types import IncEx, StrBytesIntFloat",
          "_T = TypeVar(\"_T\")",
          "_ModelT = TypeVar(\"_ModelT\", bound=pydantic.BaseModel)",
          "PYDANTIC_V1 = pydantic.VERSION.startswith(\"1.\")",
          "if TYPE_CHECKING:",
          "def parse_date(value: date | StrBytesIntFloat) -> date:  # noqa: ARG001"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/sqlalchemy/engine/interfaces.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "# engine/interfaces.py",
          "# Copyright (C) 2005-2026 the SQLAlchemy authors and contributors",
          "# <see AUTHORS file>",
          "\"\"\"Define core interfaces used by the engine system.\"\"\"",
          "from __future__ import annotations",
          "from enum import Enum",
          "from typing import Any",
          "from typing import Awaitable",
          "from typing import Callable",
          "from typing import ClassVar",
          "from typing import Collection",
          "from typing import Dict"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/sqlalchemy/sql/_typing.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "# sql/_typing.py",
          "# Copyright (C) 2022-2026 the SQLAlchemy authors and contributors",
          "# <see AUTHORS file>",
          "from __future__ import annotations",
          "import operator",
          "from typing import Any",
          "from typing import Callable",
          "from typing import Dict",
          "from typing import Generic",
          "from typing import Iterable",
          "from typing import Mapping",
          "from typing import NoReturn"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/openai/_base_client.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "import sys",
          "import json",
          "import time",
          "import uuid",
          "import email",
          "import asyncio",
          "import inspect",
          "import logging",
          "import platform",
          "import warnings",
          "import email.utils"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/sqlalchemy/sql/base.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "# sql/base.py",
          "# Copyright (C) 2005-2026 the SQLAlchemy authors and contributors",
          "# <see AUTHORS file>",
          "\"\"\"Foundational utilities common to many sql modules.\"\"\"",
          "from __future__ import annotations",
          "import collections",
          "from enum import Enum",
          "import itertools",
          "from itertools import zip_longest",
          "import operator",
          "import re",
          "from typing import Any"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/openpyxl/chartsheet/chartsheet.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "# Copyright (c) 2010-2024 openpyxl",
          "from openpyxl.descriptors import Typed, Set, Alias",
          "from openpyxl.descriptors.excel import ExtensionList",
          "from openpyxl.descriptors.serialisable import Serialisable",
          "from openpyxl.drawing.spreadsheet_drawing import (",
          "AbsoluteAnchor,",
          "SpreadsheetDrawing,",
          ")",
          "from openpyxl.worksheet.page import (",
          "PageMargins,",
          "PrintPageSetup",
          ")"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/openpyxl/comments/comments.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "# Copyright (c) 2010-2024 openpyxl",
          "class Comment:",
          "_parent = None",
          "def __init__(self, text, author, height=79, width=144):",
          "self.content = text",
          "self.author = author",
          "self.height = height",
          "self.width = width",
          "@property",
          "def parent(self):",
          "return self._parent",
          "def __eq__(self, other):"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/openpyxl/formula/tokenizer.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "\"\"\"",
          "This module contains a tokenizer for Excel formulae.",
          "The tokenizer is based on the Javascript tokenizer found at",
          "http://ewbi.blogs.com/develops/2004/12/excel_formula_p.html written by Eric",
          "Bachtal",
          "\"\"\"",
          "import re",
          "class TokenizerError(Exception):",
          "\"\"\"Base class for all Tokenizer errors.\"\"\"",
          "class Tokenizer:",
          "\"\"\"",
          "A tokenizer for Excel worksheet formulae."
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/shellingham/_core.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "SHELL_NAMES = (",
          "{\"sh\", \"bash\", \"dash\", \"ash\"}  # Bourne.",
          "| {\"csh\", \"tcsh\"}  # C.",
          "| {\"ksh\", \"zsh\", \"fish\"}  # Common alternatives.",
          "| {\"cmd\", \"powershell\", \"pwsh\"}  # Microsoft.",
          "| {\"elvish\", \"xonsh\", \"nu\"}  # More exotic.",
          ")",
          "class ShellDetectionFailure(EnvironmentError):",
          "pass"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/openpyxl/chartsheet/custom.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "# Copyright (c) 2010-2024 openpyxl",
          "from openpyxl.worksheet.header_footer import HeaderFooter",
          "from openpyxl.descriptors import (",
          "Bool,",
          "Integer,",
          "Set,",
          "Typed,",
          "Sequence",
          ")",
          "from openpyxl.descriptors.excel import Guid",
          "from openpyxl.descriptors.serialisable import Serialisable",
          "from openpyxl.worksheet.page import ("
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/openpyxl/comments/comment_sheet.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "# Copyright (c) 2010-2024 openpyxl",
          "## Incomplete!",
          "from openpyxl.descriptors.serialisable import Serialisable",
          "from openpyxl.descriptors import (",
          "Typed,",
          "Integer,",
          "Set,",
          "String,",
          "Bool,",
          ")",
          "from openpyxl.descriptors.excel import Guid, ExtensionList",
          "from openpyxl.descriptors.sequence import NestedSequence"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/openpyxl/formula/__init__.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "# Copyright (c) 2010-2024 openpyxl",
          "from .tokenizer import Tokenizer"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/shellingham/__init__.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "import importlib",
          "import os",
          "from ._core import ShellDetectionFailure",
          "__version__ = \"1.5.4\"",
          "def detect_shell(pid=None, max_depth=10):",
          "name = os.name",
          "try:",
          "impl = importlib.import_module(\".{}\".format(name), __name__)",
          "except ImportError:",
          "message = \"Shell detection not implemented for {0!r}\".format(name)",
          "raise RuntimeError(message)",
          "try:"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/_pytest/_version.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "# file generated by vcs-versioning",
          "# don't change, don't track in version control",
          "from __future__ import annotations",
          "__all__ = [",
          "\"__version__\",",
          "\"__version_tuple__\",",
          "\"version\",",
          "\"version_tuple\",",
          "\"__commit_id__\",",
          "\"commit_id\",",
          "]",
          "version: str"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/annotated_doc/main.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "class Doc:",
          "\"\"\"Define the documentation of a type annotation using `Annotated`, to be",
          "used in class attributes, function and method parameters, return values,",
          "and variables.",
          "The value should be a positional-only string literal to allow static tools",
          "like editors and documentation generators to use it.",
          "This complements docstrings.",
          "The string value passed is available in the attribute `documentation`.",
          "Example:",
          "```Python",
          "from typing import Annotated",
          "from annotated_doc import Doc"
        ],
        "related_imports": []
      },
      {
        "path": "infra/docker/docker-compose.prod.yml",
        "kind": "source",
        "language": "config",
        "tags": [
          "config"
        ],
        "snippet": [
          "version: 3.9",
          "services.api.build.context: ../..",
          "services.api.build.dockerfile: apps/api/Dockerfile",
          "services.api.restart: unless-stopped",
          "services.api.ports[0]: 8000:8000",
          "services.api.environment.DEPLOYMENT_MODE: selfhosted",
          "services.api.env_file[0]: ../../.env",
          "services.api.depends_on.postgres.condition: service_healthy",
          "services.api.depends_on.redis.condition: service_started",
          "services.worker.build.context: ../..",
          "services.worker.build.dockerfile: apps/worker/Dockerfile",
          "services.worker.restart: unless-stopped"
        ],
        "related_imports": []
      },
      {
        "path": "infra/docker/docker-compose.yml",
        "kind": "source",
        "language": "config",
        "tags": [
          "config"
        ],
        "snippet": [
          "version: 3.9",
          "services.api.build.context: ../..",
          "services.api.build.dockerfile: apps/api/Dockerfile",
          "services.api.ports[0]: 8000:8000",
          "services.api.environment.DATABASE_URL: postgresql+asyncpg://skillayer:skillayer@postgres:5432/skillayer",
          "services.api.environment.REDIS_URL: redis://redis:6379/0",
          "services.api.environment.DEPLOYMENT_MODE: development",
          "services.api.env_file[0]: ../../.env",
          "services.api.depends_on.postgres.condition: service_healthy",
          "services.api.depends_on.redis.condition: service_started",
          "services.api.volumes[0]: ../../skilgen:/app/skilgen",
          "services.api.volumes[1]: ../../apps/api:/app/apps/api"
        ],
        "related_imports": []
      },
      {
        "path": ".env.example",
        "kind": "source",
        "language": "config",
        "tags": [
          "config"
        ],
        "snippet": [
          "# -- Database --------------------------",
          "DATABASE_URL=postgresql+asyncpg://user:pass@host/db",
          "# -- GitHub App ------------------------",
          "GITHUB_APP_ID=",
          "GITHUB_APP_PRIVATE_KEY=",
          "GITHUB_WEBHOOK_SECRET=",
          "WORKOS_API_KEY=",
          "WORKOS_CLIENT_ID=",
          "WORKOS_REDIRECT_URI=https://app.skillayer.com/callback",
          "NEXT_PUBLIC_WORKOS_REDIRECT_URI=https://app.skillayer.com/callback",
          "WORKOS_COOKIE_PASSWORD=",
          "OIDC_ISSUER_URL=https://your-company.okta.com"
        ],
        "related_imports": []
      },
      {
        "path": ".turbo/cache/05d96156f2209614-manifest.json",
        "kind": "source",
        "language": "config",
        "tags": [
          "config"
        ],
        "snippet": [
          "files.apps/dashboard/.next/standalone/node_modules/next/dist/server/normalizers/request/rsc.js.size: 490",
          "files.apps/dashboard/.next/standalone/node_modules/next/dist/server/normalizers/request/rsc.js.mtime_nanos: 1776748264929361542",
          "files.apps/dashboard/.next/standalone/node_modules/next/dist/server/normalizers/request/rsc.js.mode: 420",
          "files.apps/dashboard/.next/standalone/node_modules/next/dist/server/normalizers/request/rsc.js.is_dir: False",
          "files.apps/dashboard/.next/standalone/node_modules/caniuse-lite/data/features/es6.js.size: 2136",
          "files.apps/dashboard/.next/standalone/node_modules/caniuse-lite/data/features/es6.js.mtime_nanos: 1776748264759674948",
          "files.apps/dashboard/.next/standalone/node_modules/caniuse-lite/data/features/es6.js.mode: 420",
          "files.apps/dashboard/.next/standalone/node_modules/caniuse-lite/data/features/es6.js.is_dir: False",
          "files.apps/dashboard/.next/standalone/node_modules/next/dist/build/webpack/loaders/css-loader/src/plugins/postcss-import-parser.js.size: 8872",
          "files.apps/dashboard/.next/standalone/node_modules/next/dist/build/webpack/loaders/css-loader/src/plugins/postcss-import-parser.js.mtime_nanos: 1776748264814243199",
          "files.apps/dashboard/.next/standalone/node_modules/next/dist/build/webpack/loaders/css-loader/src/plugins/postcss-import-parser.js.mode: 420",
          "files.apps/dashboard/.next/standalone/node_modules/next/dist/build/webpack/loaders/css-loader/src/plugins/postcss-import-parser.js.is_dir: False"
        ],
        "related_imports": []
      },
      {
        "path": ".turbo/cache/2eabdbab3a2e656b-manifest.json",
        "kind": "source",
        "language": "config",
        "tags": [
          "config"
        ],
        "snippet": [
          "files.apps/dashboard/.next/standalone/node_modules/react-dom/cjs/react-dom-server.browser.production.js.size: 220700",
          "files.apps/dashboard/.next/standalone/node_modules/react-dom/cjs/react-dom-server.browser.production.js.mtime_nanos: 1776660761225244944",
          "files.apps/dashboard/.next/standalone/node_modules/react-dom/cjs/react-dom-server.browser.production.js.mode: 420",
          "files.apps/dashboard/.next/standalone/node_modules/react-dom/cjs/react-dom-server.browser.production.js.is_dir: False",
          "files.apps/dashboard/.next/server/app/_not-found.meta.size: 207",
          "files.apps/dashboard/.next/server/app/_not-found.meta.mtime_nanos: 1776660749978533172",
          "files.apps/dashboard/.next/server/app/_not-found.meta.mode: 420",
          "files.apps/dashboard/.next/server/app/_not-found.meta.is_dir: False",
          "files.apps/dashboard/.next/standalone/node_modules/next/dist/server/lib/router-utils/instrumentation-globals.external.js.size: 3602",
          "files.apps/dashboard/.next/standalone/node_modules/next/dist/server/lib/router-utils/instrumentation-globals.external.js.mtime_nanos: 1776660761222293598",
          "files.apps/dashboard/.next/standalone/node_modules/next/dist/server/lib/router-utils/instrumentation-globals.external.js.mode: 420",
          "files.apps/dashboard/.next/standalone/node_modules/next/dist/server/lib/router-utils/instrumentation-globals.external.js.is_dir: False"
        ],
        "related_imports": []
      },
      {
        "path": "docs/examples/librechat-skill-tree/ARCHITECTURE.md",
        "kind": "source",
        "language": "documentation",
        "tags": [
          "documentation"
        ],
        "snippet": [
          "# Architecture",
          "## Evidence-backed architecture blueprint for the codebase",
          "Skilgen identified 6 top-level architecture domains from 41 evidence items and 26 domain graph nodes. Parser backends in use: python-ast, regex. Source comprehension currently trac",
          "```mermaid",
          "graph TD",
          "api[\"api\"]",
          "api --> roadmap[\"roadmap\"]",
          "api -. evidence .-> api_api_app_clients_baseclient_js[\"api/app/clients/BaseClient.js\"]",
          "api -. evidence .-> api_api_app_clients_ollamaclient_js[\"api/app/clients/OllamaClient.js\"]",
          "api -. evidence .-> api_api_app_clients_textstream_js[\"api/app/clients/TextStream.js\"]",
          "client[\"client\"]",
          "client --> roadmap[\"roadmap\"]"
        ],
        "related_imports": []
      },
      {
        "path": "docs/examples/claude-agent-sdk-python-dashboard.html",
        "kind": "source",
        "language": "enterprise_document",
        "tags": [
          "enterprise_document"
        ],
        "snippet": [
          "Skilgen Dashboard \u00b7 claude-agent-sdk-python",
          "\u00a9 Skilgen",
          "Agent Intelligence Surface",
          "Repository \u00b7 claude-agent-sdk-python",
          "Skilgen Operating System",
          "All your skill intelligence \u2014 alive, connected, and visible on a single surface. A living dashboard and repo map.",
          "claude-agent-sdk-python",
          "is translated into one operating surface for coding agents: architecture, evidence, dependencies, skill flows, score, freshness, analytics, auto-update, and capability context toge",
          "All skills current",
          "Auto-update on",
          "Git-aware new untracked files",
          "Evidence"
        ],
        "related_imports": []
      },
      {
        "path": "docs/examples/claude-code-dashboard.html",
        "kind": "source",
        "language": "enterprise_document",
        "tags": [
          "enterprise_document"
        ],
        "snippet": [
          "Skilgen Dashboard \u00b7 claude-code",
          "Skilgen",
          "Agent Intelligence Surface",
          "The Pulse",
          "The Weaver",
          "The Nexus",
          "The Foundry",
          "hub",
          "ops",
          "\u00a9 Skilgen",
          "Skilgen OS",
          "Repository \u00b7 claude-code"
        ],
        "related_imports": []
      },
      {
        "path": "docs/examples/langchain-dashboard.html",
        "kind": "source",
        "language": "enterprise_document",
        "tags": [
          "enterprise_document"
        ],
        "snippet": [
          "Skilgen Dashboard \u00b7 langchain",
          "\u00a9 Skilgen",
          "Agent Intelligence Surface",
          "Repository \u00b7 langchain",
          "Skilgen Operating System",
          "All your skill intelligence \u2014 alive, connected, and visible on a single surface. Not a dashboard. A living map.",
          "langchain",
          "is translated into one operating surface for coding agents: architecture, evidence, dependencies, skill flows, score, freshness, analytics, auto-update, and capability context toge",
          "15 stale skills",
          "Auto-update on",
          "Git-aware new untracked files",
          "Evidence"
        ],
        "related_imports": []
      },
      {
        "path": "docs/examples/librechat-dashboard.html",
        "kind": "source",
        "language": "enterprise_document",
        "tags": [
          "enterprise_document"
        ],
        "snippet": [
          "Skilgen Dashboard \u00b7 librechat-dashboard-clean-0414",
          "\u00a9 Skilgen",
          "Agent Intelligence Surface",
          "Repository \u00b7 librechat-dashboard-clean-0414",
          "Skilgen Operating System",
          "All your skill intelligence \u2014 alive, connected, and visible on a single surface. A living dashboard and repo map.",
          "librechat-dashboard-clean-0414",
          "is translated into one operating surface for coding agents: architecture, evidence, dependencies, skill flows, score, freshness, analytics, auto-update, and capability context toge",
          "All skills current",
          "Auto-update on",
          "Git-aware manual edit",
          "Evidence"
        ],
        "related_imports": []
      },
      {
        "path": "scripts/bump_version.py",
        "kind": "structure",
        "language": "python",
        "tags": [
          "structural-evidence"
        ],
        "snippet": [
          "from __future__ import annotations",
          "imports argparse",
          "imports re",
          "from pathlib import Path",
          "function replace_version",
          "function main"
        ],
        "related_imports": [
          "__future__",
          "argparse",
          "pathlib",
          "re"
        ]
      },
      {
        "path": "scripts/deploy_api.py",
        "kind": "structure",
        "language": "python",
        "tags": [
          "structural-evidence"
        ],
        "snippet": [
          "from __future__ import annotations",
          "imports argparse",
          "imports json",
          "imports shutil",
          "imports subprocess",
          "from collections.abc import Iterator",
          "from contextlib import contextmanager",
          "from pathlib import Path",
          "function load_project_link",
          "function deploy_command"
        ],
        "related_imports": [
          "__future__",
          "argparse",
          "collections.abc",
          "contextlib",
          "json",
          "pathlib",
          "shutil",
          "subprocess"
        ]
      },
      {
        "path": "scripts/deploy_dashboard.py",
        "kind": "structure",
        "language": "python",
        "tags": [
          "structural-evidence"
        ],
        "snippet": [
          "from __future__ import annotations",
          "imports argparse",
          "imports json",
          "imports subprocess",
          "from collections.abc import Iterator",
          "from contextlib import contextmanager",
          "from pathlib import Path",
          "function load_project_link",
          "function deploy_command",
          "function dashboard_project_link"
        ],
        "related_imports": [
          "__future__",
          "argparse",
          "collections.abc",
          "contextlib",
          "json",
          "pathlib",
          "subprocess"
        ]
      },
      {
        "path": "scripts/run_requirements_pipeline.py",
        "kind": "structure",
        "language": "python",
        "tags": [
          "structural-evidence"
        ],
        "snippet": [
          "from __future__ import annotations",
          "imports argparse",
          "imports json",
          "from pathlib import Path",
          "imports sys",
          "from skilgen.delivery import run_delivery",
          "function main"
        ],
        "related_imports": [
          "__future__",
          "argparse",
          "json",
          "pathlib",
          "skilgen/delivery.py",
          "sys"
        ]
      },
      {
        "path": "setup.py",
        "kind": "structure",
        "language": "python",
        "tags": [
          "structural-evidence"
        ],
        "snippet": [
          "from setuptools import setup"
        ],
        "related_imports": [
          "setuptools"
        ]
      },
      {
        "path": "skilgen/__init__.py",
        "kind": "structure",
        "language": "python",
        "tags": [
          "structural-evidence"
        ],
        "snippet": [
          "from skilgen.agents import fingerprint_project",
          "from skilgen.autoupdate import auto_update_status, ensure_auto_update_worker, stop_auto_update_worker",
          "from skilgen.delivery import run_delivery",
          "from skilgen.sdk import activate_project_mcp_connector, activate_skill_source, analyze_project, architecture_project"
        ],
        "related_imports": [
          "skilgen/agents/__init__.py",
          "skilgen/autoupdate.py",
          "skilgen/delivery.py",
          "skilgen/sdk.py"
        ]
      },
      {
        "path": "skilgen/agents/__init__.py",
        "kind": "structure",
        "language": "python",
        "tags": [
          "structural-evidence"
        ],
        "snippet": [
          "from skilgen.agents.codebase_signals import analyze_codebase, collect_code_evidence, collect_structural_evidence",
          "from skilgen.agents.architecture_planner import build_architecture_blueprint",
          "from skilgen.agents.evidence_graph import build_evidence_graph",
          "from skilgen.agents.language_parsers import parse_language_evidence",
          "from skilgen.agents.decision_planner import build_agent_decision",
          "from skilgen.agents.domain_graph_planner import build_domain_graph",
          "from skilgen.agents.feature_extractor import extract_features",
          "from skilgen.agents.framework_fingerprint import fingerprint_project",
          "from skilgen.agents.model_registry import resolve_model_settings",
          "from skilgen.agents.relationship_mapper import build_import_graph"
        ],
        "related_imports": [
          "skilgen/agents/architecture_planner.py",
          "skilgen/agents/codebase_signals.py",
          "skilgen/agents/decision_planner.py",
          "skilgen/agents/domain_graph_planner.py",
          "skilgen/agents/evidence_graph.py",
          "skilgen/agents/feature_extractor.py",
          "skilgen/agents/framework_fingerprint.py",
          "skilgen/agents/language_parsers.py",
          "skilgen/agents/model_registry.py",
          "skilgen/agents/relationship_mapper.py",
          "skilgen/agents/requirements_parser.py",
          "skilgen/agents/roadmap_planner.py",
          "skilgen/agents/source_graphs.py",
          "skilgen/agents/workspace_graph.py"
        ]
      },
      {
        "path": "skilgen/agents/architecture_planner.py",
        "kind": "structure",
        "language": "python",
        "tags": [
          "structural-evidence"
        ],
        "snippet": [
          "from __future__ import annotations",
          "from dataclasses import asdict",
          "from pathlib import Path",
          "from skilgen.agents.domain_graph_planner import build_domain_graph",
          "from skilgen.agents.evidence_graph import build_evidence_graph",
          "from skilgen.core.config import load_config",
          "from skilgen.deep_agents_core import run_deep_json",
          "from skilgen.core.models import ArchitectureBlueprint, ArchitectureDomain, DomainGraph, DomainGraphNode",
          "function _redact_snippet_lines",
          "function _evidence_graph_payload"
        ],
        "related_imports": [
          "__future__",
          "dataclasses",
          "pathlib",
          "skilgen/agents/domain_graph_planner.py",
          "skilgen/agents/evidence_graph.py",
          "skilgen/core/config.py",
          "skilgen/core/models.py",
          "skilgen/deep_agents_core.py"
        ]
      },
      {
        "path": "skilgen/agents/codebase_signals.py",
        "kind": "structure",
        "language": "python",
        "tags": [
          "structural-evidence"
        ],
        "snippet": [
          "from __future__ import annotations",
          "imports ast",
          "from functools import lru_cache",
          "imports re",
          "from pathlib import Path",
          "from skilgen.core.config import load_config",
          "from skilgen.core.corpus_index import load_corpus_index",
          "from skilgen.core.deep_sampler import select_deep_read_targets",
          "from skilgen.core.document_ingestion import extract_document_text",
          "from skilgen.core.models import CodebaseSignals"
        ],
        "related_imports": [
          "__future__",
          "ast",
          "functools",
          "pathlib",
          "re",
          "skilgen/core/config.py",
          "skilgen/core/corpus_index.py",
          "skilgen/core/deep_sampler.py",
          "skilgen/core/document_ingestion.py",
          "skilgen/core/models.py"
        ]
      },
      {
        "path": "skilgen/agents/decision_planner.py",
        "kind": "structure",
        "language": "python",
        "tags": [
          "structural-evidence"
        ],
        "snippet": [
          "from __future__ import annotations",
          "from pathlib import Path",
          "from skilgen.deep_agents_core import run_deep_json",
          "from skilgen.core.freshness import compute_freshness_report, load_freshness_state",
          "from skilgen.core.models import AgentDecision, RequirementsContext, RunMemory",
          "from skilgen.core.run_memory import load_current_run_memory",
          "from skilgen.enterprise_skills import active_enterprise_skills, active_mcp_connectors",
          "from skilgen.external_skills import external_skill_policy, ranked_external_skills",
          "function build_agent_decision_native",
          "function build_agent_decision"
        ],
        "related_imports": [
          "__future__",
          "pathlib",
          "skilgen/core/freshness.py",
          "skilgen/core/models.py",
          "skilgen/core/run_memory.py",
          "skilgen/deep_agents_core.py",
          "skilgen/enterprise_skills.py",
          "skilgen/external_skills.py"
        ]
      },
      {
        "path": "skilgen/agents/domain_graph_planner.py",
        "kind": "structure",
        "language": "python",
        "tags": [
          "structural-evidence"
        ],
        "snippet": [
          "from __future__ import annotations",
          "from pathlib import Path",
          "from skilgen.agents.codebase_signals import analyze_codebase, collect_code_evidence, collect_structural_evidence, is_internal_skillayer_monorepo",
          "from skilgen.agents.requirements_parser import parse_project_intent_native",
          "from skilgen.agents.workspace_graph import build_workspace_graph",
          "from skilgen.deep_agents_core import run_deep_json",
          "from skilgen.core.models import CodebaseSignals, DomainGraph, DomainGraphNode, RequirementsContext",
          "function _node",
          "function _top_file",
          "function _python_package_root"
        ],
        "related_imports": [
          "__future__",
          "pathlib",
          "skilgen/agents/codebase_signals.py",
          "skilgen/agents/requirements_parser.py",
          "skilgen/agents/workspace_graph.py",
          "skilgen/core/models.py",
          "skilgen/deep_agents_core.py"
        ]
      },
      {
        "path": "skilgen/agents/evidence_graph.py",
        "kind": "structure",
        "language": "python",
        "tags": [
          "structural-evidence"
        ],
        "snippet": [
          "from __future__ import annotations",
          "from pathlib import Path",
          "from skilgen.agents.codebase_signals import analyze_codebase, collect_code_evidence, collect_structural_evidence",
          "from skilgen.agents.relationship_mapper import build_import_graph",
          "from skilgen.agents.source_graphs import build_call_graph, build_config_runtime_graph, build_parser_summary, build_symbol_graph",
          "from skilgen.agents.workspace_graph import build_workspace_graph",
          "from skilgen.core.dependency_risk import build_dependency_risk_graph",
          "from skilgen.core.models import EvidenceGraph, EvidenceItem, RequirementsContext, RuntimeSignals",
          "from skilgen.core.runtime_signals import collect_runtime_signals",
          "function _text_preview"
        ],
        "related_imports": [
          "__future__",
          "pathlib",
          "skilgen/agents/codebase_signals.py",
          "skilgen/agents/relationship_mapper.py",
          "skilgen/agents/source_graphs.py",
          "skilgen/agents/workspace_graph.py",
          "skilgen/core/dependency_risk.py",
          "skilgen/core/models.py",
          "skilgen/core/runtime_signals.py"
        ]
      },
      {
        "path": "skilgen/agents/feature_extractor.py",
        "kind": "structure",
        "language": "python",
        "tags": [
          "structural-evidence"
        ],
        "snippet": [
          "from __future__ import annotations",
          "from pathlib import Path",
          "from skilgen.agents.codebase_signals import analyze_codebase",
          "from skilgen.agents.requirements_parser import parse_project_intent, parse_project_intent_native",
          "from skilgen.deep_agents_core import run_deep_json",
          "from skilgen.core.models import FeatureRecord",
          "function extract_features_native",
          "function extract_features"
        ],
        "related_imports": [
          "__future__",
          "pathlib",
          "skilgen/agents/codebase_signals.py",
          "skilgen/agents/requirements_parser.py",
          "skilgen/core/models.py",
          "skilgen/deep_agents_core.py"
        ]
      },
      {
        "path": "skilgen/agents/framework_fingerprint.py",
        "kind": "structure",
        "language": "python",
        "tags": [
          "structural-evidence"
        ],
        "snippet": [
          "from __future__ import annotations",
          "from pathlib import Path",
          "from skilgen.core.models import FrameworkFingerprint, FrameworkMatch",
          "function _gather_files",
          "function _match",
          "function fingerprint_project"
        ],
        "related_imports": [
          "__future__",
          "pathlib",
          "skilgen/core/models.py"
        ]
      },
      {
        "path": "skilgen/agents/language_parsers.py",
        "kind": "structure",
        "language": "python",
        "tags": [
          "structural-evidence"
        ],
        "snippet": [
          "from __future__ import annotations",
          "imports ast",
          "imports re",
          "from dataclasses import dataclass, field",
          "from pathlib import Path",
          "class ParsedSymbolRelationship",
          "class ParsedLanguageEvidence",
          "function _safe_text",
          "function _tree_sitter_parse",
          "function _node_name"
        ],
        "related_imports": [
          "__future__",
          "ast",
          "dataclasses",
          "pathlib",
          "re",
          "tree_sitter_language_pack"
        ]
      },
      {
        "path": "skilgen/agents/model_registry.py",
        "kind": "structure",
        "language": "python",
        "tags": [
          "structural-evidence"
        ],
        "snippet": [
          "from __future__ import annotations",
          "imports os",
          "from skilgen.core.models import ModelSettings, SkilgenConfig",
          "function normalize_provider",
          "function resolve_model_settings",
          "function provider_supported"
        ],
        "related_imports": [
          "__future__",
          "os",
          "skilgen/core/models.py"
        ]
      },
      {
        "path": ".pytest_cache/README.md",
        "kind": "documentation",
        "language": null,
        "tags": [
          "docs"
        ],
        "snippet": [
          "# pytest cache directory #",
          "This directory contains data from the pytest's cache plugin,",
          "which provides the `--lf` and `--ff` options, as well as the `cache` fixture.",
          "**Do not** commit this to version control.",
          "See [the docs](https://docs.pytest.org/en/stable/how-to/cache.html) for more information."
        ],
        "related_imports": []
      },
      {
        "path": ".venv/lib/python3.13/site-packages/langsmith/cli/README.md",
        "kind": "documentation",
        "language": null,
        "tags": [
          "docs"
        ],
        "snippet": [
          "# DOCKER-COMPOSE MOVED",
          "All documentation for `docker-compose` has been moved to the [helm repository](https://github.com/langchain-ai/helm/tree/main/charts/langsmith)."
        ],
        "related_imports": []
      },
      {
        "path": ".venv/lib/python3.13/site-packages/langsmith/sandbox/README.md",
        "kind": "documentation",
        "language": null,
        "tags": [
          "docs"
        ],
        "snippet": [
          "# LangSmith Sandbox",
          "Sandboxed code execution for LangSmith. Run untrusted code safely in isolated containers.",
          "> \u26a0\ufe0f **Warning**: This module is experimental. Features and APIs may change, and breaking changes are expected as we iterate.",
          "## Quick Start",
          "```python",
          "from langsmith.sandbox import SandboxClient",
          "# Client uses LANGSMITH_ENDPOINT and LANGSMITH_API_KEY from environment",
          "client = SandboxClient()"
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/langsmith/cli/README.md",
        "kind": "documentation",
        "language": null,
        "tags": [
          "docs"
        ],
        "snippet": [
          "# DOCKER-COMPOSE MOVED",
          "All documentation for `docker-compose` has been moved to the [helm repository](https://github.com/langchain-ai/helm/tree/main/charts/langsmith)."
        ],
        "related_imports": []
      },
      {
        "path": ".venv-api/lib/python3.13/site-packages/langsmith/sandbox/README.md",
        "kind": "documentation",
        "language": null,
        "tags": [
          "docs"
        ],
        "snippet": [
          "# LangSmith Sandbox",
          "Sandboxed code execution for LangSmith. Run untrusted code safely in isolated containers.",
          "> \u26a0\ufe0f **Warning**: This module is experimental. Features and APIs may change, and breaking changes are expected as we iterate.",
          "## Quick Start",
          "```python",
          "from langsmith.sandbox import SandboxClient",
          "# Client uses LANGSMITH_ENDPOINT and LANGSMITH_API_KEY from environment",
          "client = SandboxClient()"
        ],
        "related_imports": []
      },
      {
        "path": "AGENTS.md",
        "kind": "documentation",
        "language": null,
        "tags": [
          "docs"
        ],
        "snippet": [
          "# Skilgen Agent Contract",
          "## Project Overview",
          "This repository was generated or refreshed by Skilgen to help coding agents work from project-specific context instead of generic prompts.",
          "The current input mode was: `codebase only`.",
          "## How To Work In This Repo",
          "1. Open `skills/MANIFEST.md` first.",
          "2. Open the most specific inferred child skill before changing code.",
          "3. Use `FEATURES.md`, `REPORT.md`, and `TRACEABILITY.md` to understand intent, current shape, and evidence."
        ],
        "related_imports": []
      },
      {
        "path": "apps/api/Dockerfile",
        "kind": "config",
        "language": null,
        "tags": [
          "config"
        ],
        "snippet": [
          "FROM python:3.12-slim",
          "WORKDIR /app",
          "RUN apt-get update && apt-get install -y \\",
          "git curl build-essential \\",
          "&& rm -rf /var/lib/apt/lists/*",
          "COPY pyproject.toml setup.py ./",
          "COPY skilgen/ ./skilgen/",
          "COPY packages/db/ ./packages/db/"
        ],
        "related_imports": []
      },
      {
        "path": "apps/dashboard/.next/package.json",
        "kind": "config",
        "language": null,
        "tags": [
          "config"
        ],
        "snippet": [
          "{\"type\": \"commonjs\"}"
        ],
        "related_imports": []
      },
      {
        "path": "apps/dashboard/.next/standalone/apps/dashboard/.next/package.json",
        "kind": "config",
        "language": null,
        "tags": [
          "config"
        ],
        "snippet": [
          "{\"type\": \"commonjs\"}"
        ],
        "related_imports": []
      },
      {
        "path": "apps/dashboard/.next/standalone/apps/dashboard/package.json",
        "kind": "config",
        "language": null,
        "tags": [
          "config"
        ],
        "snippet": [
          "{",
          "\"name\": \"skillayer-dashboard\",",
          "\"private\": true,",
          "\"type\": \"module\",",
          "\"scripts\": {",
          "\"build\": \"next build\",",
          "\"dev\": \"next dev\",",
          "\"lint\": \"eslint .\","
        ],
        "related_imports": []
      },
      {
        "path": "apps/dashboard/.next/standalone/node_modules/@img/colour/package.json",
        "kind": "config",
        "language": null,
        "tags": [
          "config"
        ],
        "snippet": [
          "{",
          "\"name\": \"@img/colour\",",
          "\"version\": \"1.1.0\",",
          "\"description\": \"The ESM-only 'color' package made compatible for use with CommonJS runtimes\",",
          "\"license\": \"MIT\",",
          "\"main\": \"index.cjs\",",
          "\"types\": \"index.d.ts\",",
          "\"exports\": {"
        ],
        "related_imports": []
      },
      {
        "path": "apps/dashboard/.next/standalone/node_modules/@img/sharp-darwin-arm64/package.json",
        "kind": "config",
        "language": null,
        "tags": [
          "config"
        ],
        "snippet": [
          "{",
          "\"name\": \"@img/sharp-darwin-arm64\",",
          "\"version\": \"0.34.5\",",
          "\"description\": \"Prebuilt sharp for use with macOS 64-bit ARM\",",
          "\"author\": \"Lovell Fuller <npm@lovell.info>\",",
          "\"homepage\": \"https://sharp.pixelplumbing.com\",",
          "\"repository\": {",
          "\"type\": \"git\","
        ],
        "related_imports": []
      },
      {
        "path": ".vercel/output/diagnostics/cli_traces.json",
        "kind": "runtime",
        "language": null,
        "tags": [
          "runtime",
          "traces",
          "json"
        ],
        "snippet": [
          "0 spans across 0 services"
        ],
        "related_imports": []
      },
      {
        "path": "apps/web/.vercel/output/diagnostics/cli_traces.json",
        "kind": "runtime",
        "language": null,
        "tags": [
          "runtime",
          "traces",
          "json"
        ],
        "snippet": [
          "0 spans across 0 services"
        ],
        "related_imports": []
      }
    ],
    "recommendations": [
      "Use high-signal source evidence to define domain boundaries before generating skills.",
      "Prefer domains that are supported by both code evidence and requirements intent.",
      "Optimize skill synthesis around the dominant languages: python.",
      "Use structural evidence such as functions, classes, divisions, and sections to refine skill boundaries.",
      "Use the symbol graph to align skill boundaries with real modules, classes, and callable surfaces.",
      "Parser backends in use: empty, python-ast, regex.",
      "Keep skill guidance grounded in both implementation evidence and the nearest mapped tests.",
      "Model package boundaries from the `turbo` workspace graph separately from file-level import edges.",
      "Use cross-file symbol relationships to keep inheritance and interface seams aligned with the skill tree.",
      "Thread runtime artifacts such as coverage, test results, SARIF, and traces into skill guidance when they exist.",
      "Break internal dependency cycles before materializing fine-grained skills around those files or packages.",
      "High fan-out dependency hotspots surfaced in: scripts/deploy_api.py, skilgen/agents/__init__.py, skilgen/agents/architecture_planner.py, skilgen/agents/codebase_signals.py, skilgen/agents/decision_planner.py."
    ],
    "parser_summary": {
      "scripts/bump_version.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 2,
        "call_count": 13,
        "import_count": 4,
        "relationship_count": 0
      },
      "scripts/deploy_api.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 6,
        "call_count": 29,
        "import_count": 8,
        "relationship_count": 0
      },
      "scripts/deploy_dashboard.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 6,
        "call_count": 29,
        "import_count": 7,
        "relationship_count": 0
      },
      "scripts/run_requirements_pipeline.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 1,
        "call_count": 11,
        "import_count": 6,
        "relationship_count": 0
      },
      "setup.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 0,
        "call_count": 1,
        "import_count": 1,
        "relationship_count": 0
      },
      "skilgen/__init__.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 0,
        "call_count": 0,
        "import_count": 4,
        "relationship_count": 0
      },
      "skilgen/agents/__init__.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 0,
        "call_count": 0,
        "import_count": 14,
        "relationship_count": 0
      },
      "skilgen/agents/architecture_planner.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 5,
        "call_count": 30,
        "import_count": 8,
        "relationship_count": 0
      },
      "skilgen/agents/codebase_signals.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 30,
        "call_count": 30,
        "import_count": 10,
        "relationship_count": 0
      },
      "skilgen/agents/decision_planner.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 2,
        "call_count": 20,
        "import_count": 8,
        "relationship_count": 0
      },
      "skilgen/agents/domain_graph_planner.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 20,
        "call_count": 30,
        "import_count": 7,
        "relationship_count": 0
      },
      "skilgen/agents/evidence_graph.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 5,
        "call_count": 30,
        "import_count": 9,
        "relationship_count": 0
      },
      "skilgen/agents/feature_extractor.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 2,
        "call_count": 10,
        "import_count": 6,
        "relationship_count": 0
      },
      "skilgen/agents/framework_fingerprint.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 3,
        "call_count": 14,
        "import_count": 3,
        "relationship_count": 0
      },
      "skilgen/agents/language_parsers.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 10,
        "call_count": 30,
        "import_count": 6,
        "relationship_count": 0
      },
      "skilgen/agents/model_registry.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 3,
        "call_count": 10,
        "import_count": 3,
        "relationship_count": 0
      },
      "skilgen/agents/relationship_mapper.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 5,
        "call_count": 30,
        "import_count": 6,
        "relationship_count": 0
      },
      "skilgen/agents/requirements_parser.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 4,
        "call_count": 14,
        "import_count": 6,
        "relationship_count": 0
      },
      "skilgen/agents/roadmap_planner.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 2,
        "call_count": 10,
        "import_count": 5,
        "relationship_count": 0
      },
      "skilgen/agents/source_graphs.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 17,
        "call_count": 30,
        "import_count": 9,
        "relationship_count": 0
      },
      "skilgen/agents/workspace_graph.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 24,
        "call_count": 30,
        "import_count": 6,
        "relationship_count": 0
      },
      "skilgen/api/__init__.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 0,
        "call_count": 0,
        "import_count": 1,
        "relationship_count": 0
      },
      "skilgen/api/jobs.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 19,
        "call_count": 30,
        "import_count": 12,
        "relationship_count": 1
      },
      "skilgen/api/server.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 30,
        "call_count": 30,
        "import_count": 20,
        "relationship_count": 3
      },
      "skilgen/api/service.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 30,
        "call_count": 30,
        "import_count": 19,
        "relationship_count": 0
      },
      "skilgen/autoupdate.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 13,
        "call_count": 30,
        "import_count": 14,
        "relationship_count": 0
      },
      "skilgen/cli/__init__.py": {
        "language": "python",
        "backend": "empty",
        "symbol_count": 0,
        "call_count": 0,
        "import_count": 0,
        "relationship_count": 0
      },
      "skilgen/cli/main.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 15,
        "call_count": 30,
        "import_count": 20,
        "relationship_count": 0
      },
      "skilgen/core/__init__.py": {
        "language": "python",
        "backend": "empty",
        "symbol_count": 0,
        "call_count": 0,
        "import_count": 0,
        "relationship_count": 0
      },
      "skilgen/core/analytics.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 9,
        "call_count": 30,
        "import_count": 8,
        "relationship_count": 0
      },
      "skilgen/core/audit.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 5,
        "call_count": 20,
        "import_count": 9,
        "relationship_count": 0
      },
      "skilgen/core/auth_tokens.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 20,
        "call_count": 30,
        "import_count": 16,
        "relationship_count": 1
      },
      "skilgen/core/config.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 10,
        "call_count": 30,
        "import_count": 3,
        "relationship_count": 0
      },
      "skilgen/core/context.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 5,
        "call_count": 30,
        "import_count": 7,
        "relationship_count": 0
      },
      "skilgen/core/corpus_index.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 24,
        "call_count": 30,
        "import_count": 13,
        "relationship_count": 0
      },
      "skilgen/core/deep_sampler.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 5,
        "call_count": 21,
        "import_count": 5,
        "relationship_count": 0
      },
      "skilgen/core/dependency_risk.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 22,
        "call_count": 30,
        "import_count": 8,
        "relationship_count": 0
      },
      "skilgen/core/diff.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 3,
        "call_count": 17,
        "import_count": 7,
        "relationship_count": 0
      },
      "skilgen/core/document_ingestion.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 15,
        "call_count": 30,
        "import_count": 14,
        "relationship_count": 0
      },
      "skilgen/core/enterprise_policy.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 21,
        "call_count": 30,
        "import_count": 10,
        "relationship_count": 0
      },
      "skilgen/core/evals.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 2,
        "call_count": 12,
        "import_count": 3,
        "relationship_count": 0
      },
      "skilgen/core/freshness.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 13,
        "call_count": 30,
        "import_count": 7,
        "relationship_count": 0
      },
      "skilgen/core/generated_outputs.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 1,
        "call_count": 3,
        "import_count": 2,
        "relationship_count": 0
      },
      "skilgen/core/identity_policy_store.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 10,
        "call_count": 30,
        "import_count": 8,
        "relationship_count": 0
      },
      "skilgen/core/models.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 30,
        "call_count": 3,
        "import_count": 3,
        "relationship_count": 0
      },
      "skilgen/core/project_memory.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 5,
        "call_count": 16,
        "import_count": 5,
        "relationship_count": 0
      },
      "skilgen/core/rate_limit_store.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 4,
        "call_count": 17,
        "import_count": 5,
        "relationship_count": 0
      },
      "skilgen/core/repo_state.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 9,
        "call_count": 30,
        "import_count": 6,
        "relationship_count": 0
      },
      "skilgen/core/requirements.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 9,
        "call_count": 30,
        "import_count": 7,
        "relationship_count": 0
      },
      "skilgen/core/run_memory.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 10,
        "call_count": 28,
        "import_count": 6,
        "relationship_count": 0
      },
      "skilgen/core/runtime_data.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 3,
        "call_count": 20,
        "import_count": 5,
        "relationship_count": 0
      },
      "skilgen/core/runtime_signals.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 12,
        "call_count": 30,
        "import_count": 6,
        "relationship_count": 0
      },
      "skilgen/core/score.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 30,
        "call_count": 30,
        "import_count": 14,
        "relationship_count": 0
      },
      "skilgen/core/validation.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 6,
        "call_count": 30,
        "import_count": 4,
        "relationship_count": 0
      },
      "skilgen/deep_agents_core.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 22,
        "call_count": 30,
        "import_count": 13,
        "relationship_count": 0
      },
      "skilgen/deep_agents_runtime.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 30,
        "call_count": 30,
        "import_count": 20,
        "relationship_count": 0
      },
      "skilgen/delivery.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 4,
        "call_count": 30,
        "import_count": 20,
        "relationship_count": 0
      },
      "skilgen/enterprise_skills.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 30,
        "call_count": 30,
        "import_count": 13,
        "relationship_count": 0
      },
      "skilgen/external_skills.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 30,
        "call_count": 30,
        "import_count": 10,
        "relationship_count": 0
      },
      "skilgen/generators/__init__.py": {
        "language": "python",
        "backend": "empty",
        "symbol_count": 0,
        "call_count": 0,
        "import_count": 0,
        "relationship_count": 0
      },
      "skilgen/generators/package.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 30,
        "call_count": 30,
        "import_count": 19,
        "relationship_count": 0
      },
      "skilgen/generators/skills.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 27,
        "call_count": 30,
        "import_count": 14,
        "relationship_count": 0
      },
      "skilgen/registry_client.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 6,
        "call_count": 24,
        "import_count": 7,
        "relationship_count": 1
      },
      "skilgen/sdk.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 30,
        "call_count": 30,
        "import_count": 9,
        "relationship_count": 0
      },
      "tests/__init__.py": {
        "language": "python",
        "backend": "regex",
        "symbol_count": 0,
        "call_count": 0,
        "import_count": 0,
        "relationship_count": 0
      },
      "tests/oidc_test_utils.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 11,
        "call_count": 30,
        "import_count": 10,
        "relationship_count": 1
      },
      "tests/test_analytics.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 8,
        "call_count": 17,
        "import_count": 5,
        "relationship_count": 1
      },
      "tests/test_api_smoke.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 13,
        "call_count": 30,
        "import_count": 17,
        "relationship_count": 1
      },
      "tests/test_architecture_cli.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 3,
        "call_count": 14,
        "import_count": 6,
        "relationship_count": 1
      },
      "tests/test_architecture_planner.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 4,
        "call_count": 24,
        "import_count": 5,
        "relationship_count": 1
      },
      "tests/test_audit.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 2,
        "call_count": 10,
        "import_count": 7,
        "relationship_count": 1
      },
      "tests/test_auth_claim_mapping.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 5,
        "call_count": 14,
        "import_count": 7,
        "relationship_count": 1
      },
      "tests/test_auth_tokens.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 9,
        "call_count": 16,
        "import_count": 7,
        "relationship_count": 1
      },
      "tests/test_autoupdate.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 2,
        "call_count": 8,
        "import_count": 4,
        "relationship_count": 1
      },
      "tests/test_cli.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 26,
        "call_count": 23,
        "import_count": 6,
        "relationship_count": 1
      },
      "tests/test_codebase_signals.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 6,
        "call_count": 12,
        "import_count": 4,
        "relationship_count": 1
      },
      "tests/test_config.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 5,
        "call_count": 11,
        "import_count": 4,
        "relationship_count": 1
      },
      "tests/test_context.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 3,
        "call_count": 11,
        "import_count": 5,
        "relationship_count": 1
      },
      "tests/test_corpus_cli.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 4,
        "call_count": 14,
        "import_count": 6,
        "relationship_count": 1
      },
      "tests/test_corpus_index.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 3,
        "call_count": 14,
        "import_count": 6,
        "relationship_count": 1
      },
      "tests/test_dashboard_cli.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 6,
        "call_count": 30,
        "import_count": 14,
        "relationship_count": 1
      },
      "tests/test_decision_planner.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 3,
        "call_count": 16,
        "import_count": 8,
        "relationship_count": 1
      },
      "tests/test_delivery.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 23,
        "call_count": 26,
        "import_count": 7,
        "relationship_count": 1
      },
      "tests/test_dependency_risk.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 2,
        "call_count": 11,
        "import_count": 5,
        "relationship_count": 1
      },
      "tests/test_dependency_risk_graph_workstream.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 8,
        "call_count": 14,
        "import_count": 8,
        "relationship_count": 0
      },
      "tests/test_diff.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 12,
        "call_count": 23,
        "import_count": 10,
        "relationship_count": 1
      },
      "tests/test_document_ingestion.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 7,
        "call_count": 30,
        "import_count": 9,
        "relationship_count": 1
      },
      "tests/test_domain_graph_planner.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 9,
        "call_count": 16,
        "import_count": 6,
        "relationship_count": 1
      },
      "tests/test_enterprise_document_formats.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 3,
        "call_count": 15,
        "import_count": 6,
        "relationship_count": 1
      },
      "tests/test_enterprise_policy_cli.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 9,
        "call_count": 20,
        "import_count": 7,
        "relationship_count": 0
      },
      "tests/test_feature_extractor.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 2,
        "call_count": 9,
        "import_count": 4,
        "relationship_count": 1
      },
      "tests/test_framework_fingerprint.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 2,
        "call_count": 8,
        "import_count": 4,
        "relationship_count": 1
      },
      "tests/test_identity_policy_store.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 2,
        "call_count": 14,
        "import_count": 6,
        "relationship_count": 1
      },
      "tests/test_jobs.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 4,
        "call_count": 27,
        "import_count": 9,
        "relationship_count": 1
      },
      "tests/test_model_registry.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 5,
        "call_count": 6,
        "import_count": 4,
        "relationship_count": 1
      },
      "tests/test_org_settings.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 28,
        "call_count": 25,
        "import_count": 13,
        "relationship_count": 0
      },
      "tests/test_overview_data.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 9,
        "call_count": 4,
        "import_count": 3,
        "relationship_count": 0
      },
      "tests/test_packaging.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 3,
        "call_count": 14,
        "import_count": 8,
        "relationship_count": 1
      },
      "tests/test_plan_cli.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 2,
        "call_count": 9,
        "import_count": 6,
        "relationship_count": 1
      },
      "tests/test_pr_comment.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 8,
        "call_count": 9,
        "import_count": 3,
        "relationship_count": 1
      },
      "tests/test_pr_comment_dedup.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 11,
        "call_count": 7,
        "import_count": 5,
        "relationship_count": 0
      },
      "tests/test_rate_limit_store.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 2,
        "call_count": 8,
        "import_count": 5,
        "relationship_count": 1
      },
      "tests/test_registry_api.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 21,
        "call_count": 13,
        "import_count": 9,
        "relationship_count": 0
      },
      "tests/test_registry_cli.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 5,
        "call_count": 28,
        "import_count": 11,
        "relationship_count": 2
      },
      "tests/test_registry_dashboard.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 2,
        "call_count": 3,
        "import_count": 2,
        "relationship_count": 0
      },
      "tests/test_relationship_mapper.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 6,
        "call_count": 9,
        "import_count": 4,
        "relationship_count": 1
      },
      "tests/test_repos_screen.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 5,
        "call_count": 4,
        "import_count": 2,
        "relationship_count": 0
      },
      "tests/test_requirements.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 3,
        "call_count": 13,
        "import_count": 5,
        "relationship_count": 1
      },
      "tests/test_requirements_parser.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 2,
        "call_count": 7,
        "import_count": 4,
        "relationship_count": 1
      },
      "tests/test_roadmap_planner.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 2,
        "call_count": 5,
        "import_count": 3,
        "relationship_count": 1
      },
      "tests/test_roadmap_skills.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 2,
        "call_count": 10,
        "import_count": 5,
        "relationship_count": 1
      },
      "tests/test_run_memory.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 2,
        "call_count": 11,
        "import_count": 5,
        "relationship_count": 1
      },
      "tests/test_runtime_hardening.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 20,
        "call_count": 30,
        "import_count": 8,
        "relationship_count": 1
      },
      "tests/test_runtime_signals.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 2,
        "call_count": 11,
        "import_count": 5,
        "relationship_count": 1
      },
      "tests/test_score.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 15,
        "call_count": 28,
        "import_count": 8,
        "relationship_count": 1
      },
      "tests/test_score_quality_system.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 20,
        "call_count": 30,
        "import_count": 15,
        "relationship_count": 0
      },
      "tests/test_sdk.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 19,
        "call_count": 30,
        "import_count": 9,
        "relationship_count": 1
      },
      "tests/test_skill_detail.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 11,
        "call_count": 9,
        "import_count": 5,
        "relationship_count": 0
      },
      "tests/test_skill_usage_analytics.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 21,
        "call_count": 27,
        "import_count": 12,
        "relationship_count": 0
      },
      "tests/test_skillayer_api_infra.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 19,
        "call_count": 23,
        "import_count": 13,
        "relationship_count": 0
      },
      "tests/test_source_graphs.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 4,
        "call_count": 17,
        "import_count": 5,
        "relationship_count": 1
      },
      "tests/test_stripe_portal.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 17,
        "call_count": 12,
        "import_count": 9,
        "relationship_count": 0
      },
      "tests/test_stripe_webhook.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 29,
        "call_count": 25,
        "import_count": 11,
        "relationship_count": 0
      },
      "tests/test_upgrade_flow.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 8,
        "call_count": 5,
        "import_count": 2,
        "relationship_count": 1
      },
      "tests/test_validate_cli.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 2,
        "call_count": 4,
        "import_count": 4,
        "relationship_count": 1
      },
      "tests/test_vercel_api_deploy.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 3,
        "call_count": 11,
        "import_count": 4,
        "relationship_count": 0
      },
      "tests/test_vercel_dashboard_deploy.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 2,
        "call_count": 7,
        "import_count": 4,
        "relationship_count": 0
      },
      "tests/test_workspace_graph.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 7,
        "call_count": 8,
        "import_count": 4,
        "relationship_count": 1
      }
    },
    "symbol_graph": {
      "scripts/bump_version.py": [
        "from __future__ import annotations",
        "imports argparse",
        "imports re",
        "from pathlib import Path",
        "function replace_version",
        "function main"
      ],
      "scripts/deploy_api.py": [
        "from __future__ import annotations",
        "imports argparse",
        "imports json",
        "imports shutil",
        "imports subprocess",
        "from collections.abc import Iterator",
        "from contextlib import contextmanager",
        "from pathlib import Path",
        "function load_project_link",
        "function deploy_command"
      ],
      "scripts/deploy_dashboard.py": [
        "from __future__ import annotations",
        "imports argparse",
        "imports json",
        "imports subprocess",
        "from collections.abc import Iterator",
        "from contextlib import contextmanager",
        "from pathlib import Path",
        "function load_project_link",
        "function deploy_command",
        "function dashboard_project_link"
      ],
      "scripts/run_requirements_pipeline.py": [
        "from __future__ import annotations",
        "imports argparse",
        "imports json",
        "from pathlib import Path",
        "imports sys",
        "from skilgen.delivery import run_delivery",
        "function main"
      ],
      "setup.py": [
        "from setuptools import setup"
      ],
      "skilgen/__init__.py": [
        "from skilgen.agents import fingerprint_project",
        "from skilgen.autoupdate import auto_update_status, ensure_auto_update_worker, stop_auto_update_worker",
        "from skilgen.delivery import run_delivery",
        "from skilgen.sdk import activate_project_mcp_connector, activate_skill_source, analyze_project, architecture_project"
      ],
      "skilgen/agents/__init__.py": [
        "from skilgen.agents.codebase_signals import analyze_codebase, collect_code_evidence, collect_structural_evidence",
        "from skilgen.agents.architecture_planner import build_architecture_blueprint",
        "from skilgen.agents.evidence_graph import build_evidence_graph",
        "from skilgen.agents.language_parsers import parse_language_evidence",
        "from skilgen.agents.decision_planner import build_agent_decision",
        "from skilgen.agents.domain_graph_planner import build_domain_graph",
        "from skilgen.agents.feature_extractor import extract_features",
        "from skilgen.agents.framework_fingerprint import fingerprint_project",
        "from skilgen.agents.model_registry import resolve_model_settings",
        "from skilgen.agents.relationship_mapper import build_import_graph"
      ],
      "skilgen/agents/architecture_planner.py": [
        "from __future__ import annotations",
        "from dataclasses import asdict",
        "from pathlib import Path",
        "from skilgen.agents.domain_graph_planner import build_domain_graph",
        "from skilgen.agents.evidence_graph import build_evidence_graph",
        "from skilgen.core.config import load_config",
        "from skilgen.deep_agents_core import run_deep_json",
        "from skilgen.core.models import ArchitectureBlueprint, ArchitectureDomain, DomainGraph, DomainGraphNode",
        "function _redact_snippet_lines",
        "function _evidence_graph_payload"
      ],
      "skilgen/agents/codebase_signals.py": [
        "from __future__ import annotations",
        "imports ast",
        "from functools import lru_cache",
        "imports re",
        "from pathlib import Path",
        "from skilgen.core.config import load_config",
        "from skilgen.core.corpus_index import load_corpus_index",
        "from skilgen.core.deep_sampler import select_deep_read_targets",
        "from skilgen.core.document_ingestion import extract_document_text",
        "from skilgen.core.models import CodebaseSignals"
      ],
      "skilgen/agents/decision_planner.py": [
        "from __future__ import annotations",
        "from pathlib import Path",
        "from skilgen.deep_agents_core import run_deep_json",
        "from skilgen.core.freshness import compute_freshness_report, load_freshness_state",
        "from skilgen.core.models import AgentDecision, RequirementsContext, RunMemory",
        "from skilgen.core.run_memory import load_current_run_memory",
        "from skilgen.enterprise_skills import active_enterprise_skills, active_mcp_connectors",
        "from skilgen.external_skills import external_skill_policy, ranked_external_skills",
        "function build_agent_decision_native",
        "function build_agent_decision"
      ],
      "skilgen/agents/domain_graph_planner.py": [
        "from __future__ import annotations",
        "from pathlib import Path",
        "from skilgen.agents.codebase_signals import analyze_codebase, collect_code_evidence, collect_structural_evidence, is_internal_skillayer_monorepo",
        "from skilgen.agents.requirements_parser import parse_project_intent_native",
        "from skilgen.agents.workspace_graph import build_workspace_graph",
        "from skilgen.deep_agents_core import run_deep_json",
        "from skilgen.core.models import CodebaseSignals, DomainGraph, DomainGraphNode, RequirementsContext",
        "function _node",
        "function _top_file",
        "function _python_package_root"
      ],
      "skilgen/agents/evidence_graph.py": [
        "from __future__ import annotations",
        "from pathlib import Path",
        "from skilgen.agents.codebase_signals import analyze_codebase, collect_code_evidence, collect_structural_evidence",
        "from skilgen.agents.relationship_mapper import build_import_graph",
        "from skilgen.agents.source_graphs import build_call_graph, build_config_runtime_graph, build_parser_summary, build_symbol_graph",
        "from skilgen.agents.workspace_graph import build_workspace_graph",
        "from skilgen.core.dependency_risk import build_dependency_risk_graph",
        "from skilgen.core.models import EvidenceGraph, EvidenceItem, RequirementsContext, RuntimeSignals",
        "from skilgen.core.runtime_signals import collect_runtime_signals",
        "function _text_preview"
      ],
      "skilgen/agents/feature_extractor.py": [
        "from __future__ import annotations",
        "from pathlib import Path",
        "from skilgen.agents.codebase_signals import analyze_codebase",
        "from skilgen.agents.requirements_parser import parse_project_intent, parse_project_intent_native",
        "from skilgen.deep_agents_core import run_deep_json",
        "from skilgen.core.models import FeatureRecord",
        "function extract_features_native",
        "function extract_features"
      ],
      "skilgen/agents/framework_fingerprint.py": [
        "from __future__ import annotations",
        "from pathlib import Path",
        "from skilgen.core.models import FrameworkFingerprint, FrameworkMatch",
        "function _gather_files",
        "function _match",
        "function fingerprint_project"
      ],
      "skilgen/agents/language_parsers.py": [
        "from __future__ import annotations",
        "imports ast",
        "imports re",
        "from dataclasses import dataclass, field",
        "from pathlib import Path",
        "class ParsedSymbolRelationship",
        "class ParsedLanguageEvidence",
        "function _safe_text",
        "function _tree_sitter_parse",
        "function _node_name"
      ],
      "skilgen/agents/model_registry.py": [
        "from __future__ import annotations",
        "imports os",
        "from skilgen.core.models import ModelSettings, SkilgenConfig",
        "function normalize_provider",
        "function resolve_model_settings",
        "function provider_supported"
      ],
      "skilgen/agents/relationship_mapper.py": [
        "from __future__ import annotations",
        "imports ast",
        "imports re",
        "imports warnings",
        "from pathlib import Path",
        "from skilgen.agents.codebase_signals import _iter_code_files",
        "function _relative_text_imports",
        "function _resolve_repo_local_import",
        "function _resolve_python_import",
        "function _resolve_python_from_import"
      ],
      "skilgen/agents/requirements_parser.py": [
        "from __future__ import annotations",
        "from pathlib import Path",
        "from skilgen.agents.codebase_signals import analyze_codebase",
        "from skilgen.deep_agents_core import run_deep_json",
        "from skilgen.core.models import ProjectIntent",
        "from skilgen.core.requirements import extract_project_intent, extract_text, normalize_lines",
        "function parse_requirements_file_native",
        "function parse_requirements_file",
        "function parse_project_intent_native",
        "function parse_project_intent"
      ],
      "skilgen/agents/roadmap_planner.py": [
        "from __future__ import annotations",
        "from pathlib import Path",
        "from skilgen.deep_agents_core import run_deep_json",
        "from skilgen.agents.model_registry import resolve_model_settings",
        "from skilgen.core.models import PlanStep, ProjectIntent, RoadmapPlan, SkilgenConfig",
        "function build_roadmap_plan_native",
        "function build_roadmap_plan"
      ],
      "skilgen/agents/source_graphs.py": [
        "from __future__ import annotations",
        "imports ast",
        "from functools import lru_cache",
        "imports re",
        "from pathlib import Path",
        "from skilgen.agents.codebase_signals import _iter_code_files, _is_test, _language_for_path, _language_structure",
        "from skilgen.agents.language_parsers import parse_language_evidence",
        "from skilgen.agents.relationship_mapper import build_import_graph",
        "from skilgen.core.models import SymbolRelationship",
        "function _safe_text"
      ],
      "skilgen/agents/workspace_graph.py": [
        "from __future__ import annotations",
        "imports json",
        "imports re",
        "from pathlib import Path",
        "from skilgen.core.models import WorkspaceDependency, WorkspaceGraph, WorkspacePackage",
        "function _relative",
        "function _package_id",
        "function _safe_json",
        "function _safe_yaml",
        "function _safe_text"
      ],
      "skilgen/api/__init__.py": [
        "from skilgen.api.server import create_server, run_server"
      ],
      "skilgen/api/jobs.py": [
        "from __future__ import annotations",
        "imports json",
        "imports sqlite3",
        "imports uuid",
        "from concurrent.futures import ThreadPoolExecutor",
        "from contextlib import closing",
        "from dataclasses import dataclass, field",
        "from datetime import datetime, timezone",
        "from pathlib import Path",
        "from threading import Lock"
      ],
      "skilgen/api/server.py": [
        "from __future__ import annotations",
        "from dataclasses import dataclass",
        "imports hmac",
        "imports hashlib",
        "imports ipaddress",
        "imports json",
        "imports logging",
        "imports os",
        "imports socket",
        "imports threading"
      ],
      "skilgen/api/service.py": [
        "from __future__ import annotations",
        "from pathlib import Path",
        "from typing import Callable",
        "from skilgen.api.jobs import get_job, job_payload, list_jobs, request_cancel",
        "from skilgen.agents.decision_planner import build_agent_decision",
        "from skilgen.autoupdate import auto_update_status",
        "from skilgen.core.diff import compute_diff",
        "from skilgen.core.analytics import analytics_summary",
        "from skilgen.deep_agents_core import current_runtime_mode, runtime_diagnostics",
        "from skilgen.deep_agents_runtime import DeepAgentsRuntime, native_analyze_payload, native_architecture_payload, native_dashboard_payload"
      ],
      "skilgen/autoupdate.py": [
        "from __future__ import annotations",
        "imports json",
        "imports os",
        "imports signal",
        "imports subprocess",
        "imports sys",
        "imports time",
        "from datetime import UTC, datetime",
        "from pathlib import Path",
        "from skilgen.agents.codebase_signals import is_ignored_path_parts, is_internal_skillayer_monorepo"
      ],
      "skilgen/cli/main.py": [
        "from __future__ import annotations",
        "imports argparse",
        "imports json",
        "imports sys",
        "from dataclasses import dataclass",
        "from pathlib import Path",
        "imports threading",
        "imports time",
        "from skilgen.api.server import run_server",
        "from skilgen.autoupdate import auto_update_status, ensure_auto_update_worker, run_auto_update_worker, stop_auto_update_worker"
      ],
      "skilgen/core/analytics.py": [
        "from __future__ import annotations",
        "imports json",
        "imports os",
        "from collections import Counter, defaultdict",
        "from datetime import UTC, datetime",
        "from pathlib import Path",
        "imports re",
        "from skilgen.external_skills import active_external_skills",
        "function _analytics_path",
        "function _timestamp"
      ],
      "skilgen/core/audit.py": [
        "from __future__ import annotations",
        "imports contextlib",
        "imports fcntl",
        "imports json",
        "from datetime import UTC, datetime",
        "imports os",
        "from pathlib import Path",
        "from threading import Lock",
        "from typing import Any",
        "function audit_log_path"
      ],
      "skilgen/core/auth_tokens.py": [
        "from __future__ import annotations",
        "imports base64",
        "imports hashlib",
        "imports hmac",
        "imports ipaddress",
        "imports json",
        "imports socket",
        "imports threading",
        "imports time",
        "from pathlib import Path"
      ],
      "skilgen/core/config.py": [
        "from __future__ import annotations",
        "from pathlib import Path",
        "from skilgen.core.models import CorpusSettings, SkilgenConfig",
        "function _string_or_none",
        "function _string_list",
        "function _bool_value",
        "function _int_value",
        "function _float_value",
        "function _dict_value",
        "function _parse_scalar"
      ],
      "skilgen/core/context.py": [
        "from __future__ import annotations",
        "from pathlib import Path",
        "from skilgen.agents.domain_graph_planner import _top_level_app_surfaces, build_domain_graph, detect_repo_archetype",
        "from skilgen.agents.framework_fingerprint import fingerprint_project",
        "from skilgen.agents.codebase_signals import analyze_codebase, is_ignored_path_parts, is_internal_skillayer_monorepo",
        "from skilgen.agents.workspace_graph import build_workspace_graph",
        "from skilgen.core.models import CodebaseContext, DomainGraph, DomainGraphNode, DomainRecord",
        "function _build_file_tree",
        "function _domain_records",
        "function _skill_tree"
      ],
      "skilgen/core/corpus_index.py": [
        "from __future__ import annotations",
        "imports fnmatch",
        "imports hashlib",
        "imports json",
        "imports re",
        "from collections import defaultdict",
        "from pathlib import Path, PurePosixPath",
        "from typing import Any",
        "from skilgen.agents.language_parsers import ParsedLanguageEvidence, parse_language_evidence",
        "from skilgen.core.config import load_config"
      ],
      "skilgen/core/deep_sampler.py": [
        "from __future__ import annotations",
        "from pathlib import Path",
        "from typing import Any",
        "from skilgen.core.config import load_config",
        "from skilgen.core.models import CorpusSettings, SkilgenConfig",
        "function select_deep_read_targets",
        "function _entries_by_category",
        "function _sort_key",
        "function _cluster_representatives",
        "function _corpus_settings"
      ],
      "skilgen/core/dependency_risk.py": [
        "from __future__ import annotations",
        "imports json",
        "from pathlib import Path",
        "imports re",
        "from skilgen.agents.relationship_mapper import build_import_graph",
        "from skilgen.agents.workspace_graph import build_workspace_graph",
        "from skilgen.core.models import DependencyFinding, DependencyRiskEdge, DependencyRiskGraph, DependencyRiskNode",
        "function _dependency_key",
        "function _clean_exact_version",
        "function _upgrade_command"
      ],
      "skilgen/core/diff.py": [
        "from __future__ import annotations",
        "from pathlib import Path",
        "from skilgen.core.context import build_codebase_context",
        "from skilgen.core.freshness import compute_freshness_report, load_freshness_state, snapshot_freshness_state",
        "from skilgen.core.repo_state import git_repo_state",
        "from skilgen.core.requirements import load_project_context",
        "from skilgen.core.score import freshness_subscore",
        "function _current_git_event_from_state",
        "function _classify_changed_files",
        "function compute_diff"
      ],
      "skilgen/core/document_ingestion.py": [
        "from __future__ import annotations",
        "imports csv",
        "imports html",
        "imports json",
        "imports re",
        "imports tomllib",
        "imports xml.etree.ElementTree",
        "imports zipfile",
        "from pathlib import Path",
        "function normalize_extracted_text"
      ],
      "skilgen/core/enterprise_policy.py": [
        "from __future__ import annotations",
        "from dataclasses import asdict, dataclass",
        "from datetime import UTC, date, datetime",
        "from pathlib import Path",
        "from typing import Any",
        "imports yaml",
        "from skilgen.core.dependency_risk import analyze_dependency_risks, dependency_report_to_dict",
        "from skilgen.core.score import compute_skillgen_score",
        "from skilgen.enterprise_skills import list_enterprise_skills",
        "from skilgen.external_skills import active_external_skills"
      ],
      "skilgen/core/evals.py": [
        "from __future__ import annotations",
        "imports json",
        "from pathlib import Path",
        "function scaffold_eval_framework",
        "function compare_eval_results"
      ],
      "skilgen/core/freshness.py": [
        "from __future__ import annotations",
        "imports hashlib",
        "imports json",
        "from dataclasses import asdict",
        "from pathlib import Path",
        "from skilgen.core.generated_outputs import is_generated_output_path",
        "from skilgen.core.models import DomainGraph, FreshnessReport, FreshnessState, RequirementsContext",
        "function _is_internal_skillayer_monorepo",
        "function _is_ignored",
        "function _is_trackable_source_path"
      ],
      "skilgen/core/generated_outputs.py": [
        "from __future__ import annotations",
        "from pathlib import Path",
        "function is_generated_output_path"
      ],
      "skilgen/core/identity_policy_store.py": [
        "from __future__ import annotations",
        "from contextlib import closing",
        "from datetime import UTC, datetime",
        "imports json",
        "imports os",
        "from pathlib import Path",
        "imports sqlite3",
        "from typing import Any",
        "function identity_policy_store_path",
        "function _connect"
      ],
      "skilgen/core/models.py": [
        "from __future__ import annotations",
        "from dataclasses import dataclass, field",
        "from pathlib import Path",
        "class SkillSpec",
        "class RequirementsContext",
        "class ProjectIntent",
        "class FeatureRecord",
        "class FrameworkMatch",
        "class FrameworkFingerprint",
        "class CorpusSettings"
      ],
      "skilgen/core/project_memory.py": [
        "from __future__ import annotations",
        "imports json",
        "from dataclasses import asdict",
        "from pathlib import Path",
        "from skilgen.core.models import ProjectMemory, RequirementsContext",
        "function _memory_dir",
        "function _project_memory_path",
        "function build_project_memory",
        "function save_project_memory",
        "function load_project_memory"
      ],
      "skilgen/core/rate_limit_store.py": [
        "from __future__ import annotations",
        "imports math",
        "imports os",
        "from pathlib import Path",
        "imports sqlite3",
        "function rate_limit_store_path",
        "function _connect",
        "function consume_rate_limit",
        "function clear_rate_limit_store"
      ],
      "skilgen/core/repo_state.py": [
        "from __future__ import annotations",
        "imports subprocess",
        "from pathlib import Path",
        "imports re",
        "imports shutil",
        "from skilgen.agents.language_parsers import parse_language_text",
        "function _semantic_path_kind",
        "function _git_dir",
        "function _git_output",
        "function _git_lines"
      ],
      "skilgen/core/requirements.py": [
        "from __future__ import annotations",
        "imports json",
        "imports hashlib",
        "from pathlib import Path",
        "from skilgen.agents.codebase_signals import is_ignored_path_parts, is_internal_skillayer_monorepo",
        "from skilgen.core.document_ingestion import extract_document_text",
        "from skilgen.core.models import ProjectIntent, RequirementsContext",
        "function extract_text",
        "function normalize_lines",
        "function detect_domains"
      ],
      "skilgen/core/run_memory.py": [
        "from __future__ import annotations",
        "imports json",
        "imports uuid",
        "from dataclasses import asdict, replace",
        "from json import JSONDecodeError",
        "from pathlib import Path",
        "from skilgen.core.models import FreshnessReport, RunMemory",
        "function _memory_dir",
        "function _runs_dir",
        "function _current_run_path"
      ],
      "skilgen/core/runtime_data.py": [
        "from __future__ import annotations",
        "imports shutil",
        "imports time",
        "from pathlib import Path",
        "from skilgen.core.config import load_config",
        "function runtime_data_root",
        "function prune_runtime_data",
        "function purge_runtime_data"
      ],
      "skilgen/core/runtime_signals.py": [
        "from __future__ import annotations",
        "imports json",
        "from pathlib import Path",
        "imports re",
        "from xml.etree import ElementTree",
        "from skilgen.core.models import RuntimeSignalArtifact, RuntimeSignals",
        "function _safe_relative",
        "function _read_text",
        "function _looks_like_runtime_artifact",
        "function _parse_junit_xml"
      ],
      "skilgen/core/score.py": [
        "from __future__ import annotations",
        "imports json",
        "imports re",
        "imports subprocess",
        "from datetime import UTC, datetime",
        "from html import escape",
        "from pathlib import Path",
        "from threading import Lock",
        "from urllib.parse import quote",
        "from skilgen.agents.codebase_signals import CODE_EXTENSIONS, is_ignored_path_parts, is_internal_skillayer_monorepo"
      ],
      "skilgen/core/validation.py": [
        "from __future__ import annotations",
        "from pathlib import Path",
        "from skilgen.agents.codebase_signals import analyze_codebase",
        "from skilgen.deep_agents_core import runtime_diagnostics",
        "function _parse_references",
        "function _needs_bidirectional_check",
        "function _skill_paths",
        "function _has_skill_matching",
        "function _repo_native_top_level_skills",
        "function validate_project"
      ],
      "skilgen/deep_agents_core.py": [
        "from __future__ import annotations",
        "imports asyncio",
        "imports json",
        "imports os",
        "imports queue",
        "imports threading",
        "imports time",
        "from typing import Callable",
        "from pathlib import Path",
        "from skilgen.agents.model_registry import provider_supported, resolve_model_settings"
      ],
      "skilgen/deep_agents_runtime.py": [
        "from __future__ import annotations",
        "imports json",
        "imports os",
        "from dataclasses import asdict, is_dataclass",
        "from pathlib import Path",
        "from typing import Any, Callable",
        "from skilgen.agents.codebase_signals import analyze_codebase",
        "from skilgen.agents.domain_graph_planner import _top_level_app_surfaces, detect_repo_archetype",
        "from skilgen.agents.evidence_graph import build_evidence_graph",
        "from skilgen.agents.feature_extractor import extract_features, extract_features_native"
      ],
      "skilgen/delivery.py": [
        "from __future__ import annotations",
        "from dataclasses import replace",
        "imports time",
        "from pathlib import Path",
        "from typing import Callable",
        "from skilgen.agents import build_agent_decision, fingerprint_project",
        "from skilgen.agents.codebase_signals import clear_codebase_signal_caches, is_ignored_path_parts, is_internal_skillayer_monorepo",
        "from skilgen.agents.source_graphs import clear_source_graph_caches",
        "from skilgen.core.audit import append_audit_event",
        "from skilgen.core.analytics import log_skill_usage"
      ],
      "skilgen/enterprise_skills.py": [
        "from __future__ import annotations",
        "from dataclasses import asdict, dataclass",
        "from datetime import UTC, datetime",
        "imports json",
        "imports os",
        "imports re",
        "imports shutil",
        "imports subprocess",
        "from pathlib import Path",
        "from urllib.parse import urlparse"
      ],
      "skilgen/external_skills.py": [
        "from __future__ import annotations",
        "from dataclasses import asdict, dataclass",
        "from datetime import UTC, datetime",
        "imports json",
        "imports os",
        "imports re",
        "imports shutil",
        "imports subprocess",
        "from pathlib import Path",
        "from skilgen.core.config import load_config"
      ],
      "skilgen/generators/package.py": [
        "from __future__ import annotations",
        "from dataclasses import asdict, dataclass",
        "from datetime import datetime",
        "from html import escape",
        "imports json",
        "imports re",
        "imports sys",
        "from pathlib import Path",
        "from typing import Callable",
        "from skilgen.agents import analyze_codebase, build_agent_decision, build_architecture_blueprint, build_evidence_graph"
      ],
      "skilgen/generators/skills.py": [
        "from __future__ import annotations",
        "imports os",
        "from datetime import date",
        "from pathlib import Path",
        "from typing import Callable",
        "from skilgen.agents.architecture_planner import build_architecture_blueprint",
        "from skilgen.agents.codebase_signals import analyze_codebase",
        "from skilgen.agents.requirements_parser import parse_project_intent",
        "from skilgen.agents.roadmap_planner import build_roadmap_plan",
        "from skilgen.core.config import load_config"
      ],
      "skilgen/registry_client.py": [
        "from __future__ import annotations",
        "imports json",
        "imports os",
        "from pathlib import Path",
        "from typing import cast",
        "from urllib.error import HTTPError, URLError",
        "from urllib.request import Request, urlopen",
        "class RegistryClientError",
        "function _api_key",
        "function _api_url"
      ],
      "skilgen/sdk.py": [
        "from __future__ import annotations",
        "from pathlib import Path",
        "from skilgen.api.service import analytics_payload, analyze_payload, architecture_payload, dashboard_payload",
        "from skilgen.autoupdate import auto_update_status, ensure_auto_update_worker, stop_auto_update_worker",
        "from skilgen.core.config import render_default_config",
        "from skilgen.core.evals import compare_eval_results, scaffold_eval_framework",
        "from skilgen.delivery import run_delivery, watch_delivery",
        "from skilgen.enterprise_skills import activate_mcp_connector, active_enterprise_skills, active_mcp_connectors, connector_catalog",
        "from skilgen.external_skills import activate_external_skill, active_external_skills, detect_external_skill_sources, external_skill_lock",
        "function init_project"
      ],
      "tests/oidc_test_utils.py": [
        "from __future__ import annotations",
        "imports base64",
        "imports json",
        "imports threading",
        "imports time",
        "from http.server import BaseHTTPRequestHandler, HTTPServer",
        "from pathlib import Path",
        "from typing import Any",
        "from cryptography.hazmat.primitives import hashes",
        "from cryptography.hazmat.primitives.asymmetric import padding, rsa"
      ],
      "tests/test_analytics.py": [
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports unittest",
        "from skilgen.core.analytics import analytics_summary, log_skill_usage",
        "from skilgen.generators.package import render_analytics_radial_data",
        "class AnalyticsTests"
      ],
      "tests/test_api_smoke.py": [
        "from __future__ import annotations",
        "imports io",
        "imports json",
        "imports logging",
        "imports os",
        "imports threading",
        "imports unittest",
        "from unittest import mock",
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory"
      ],
      "tests/test_architecture_cli.py": [
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports json",
        "imports subprocess",
        "imports sys",
        "imports unittest",
        "class ArchitectureCliTests"
      ],
      "tests/test_architecture_planner.py": [
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports unittest",
        "from skilgen.agents.architecture_planner import _evidence_graph_payload, _sanitize_architecture_payload",
        "from skilgen.core.models import ArchitectureBlueprint, ArchitectureDomain, DependencyRiskGraph, DependencyRiskNode",
        "class ArchitecturePlannerTests"
      ],
      "tests/test_audit.py": [
        "from __future__ import annotations",
        "imports os",
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports unittest",
        "from unittest.mock import patch",
        "from skilgen.core.audit import append_audit_event",
        "class AuditTests"
      ],
      "tests/test_auth_claim_mapping.py": [
        "from __future__ import annotations",
        "imports os",
        "imports unittest",
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "from unittest import mock",
        "from skilgen.api.server import _claims_allowed_roots, _claims_principal, _claims_scope, _claims_tenant",
        "class OidcClaimMappingTests",
        "function json_dumps"
      ],
      "tests/test_auth_tokens.py": [
        "from __future__ import annotations",
        "imports time",
        "imports unittest",
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "from skilgen.core.auth_tokens import SignedTokenError, clear_remote_verifier_caches, mint_signed_token, verify_jwks_token",
        "from tests.oidc_test_utils import LocalOidcServer, generate_rsa_signing_material, mint_rs256_token",
        "class SignedTokenTests"
      ],
      "tests/test_autoupdate.py": [
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports unittest",
        "from skilgen.autoupdate import _file_snapshot",
        "class AutoUpdateTests"
      ],
      "tests/test_cli.py": [
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports json",
        "imports subprocess",
        "imports sys",
        "imports unittest",
        "class CliTests"
      ],
      "tests/test_codebase_signals.py": [
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports unittest",
        "from skilgen.agents.codebase_signals import analyze_codebase, collect_code_evidence, collect_structural_evidence",
        "class CodebaseSignalsTests"
      ],
      "tests/test_config.py": [
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports unittest",
        "from skilgen.core.config import load_config, render_default_config",
        "class ConfigTests"
      ],
      "tests/test_context.py": [
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports unittest",
        "from skilgen.core.context import build_codebase_context",
        "from skilgen.core.requirements import load_requirements",
        "class ContextTests"
      ],
      "tests/test_corpus_cli.py": [
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports json",
        "imports subprocess",
        "imports sys",
        "imports unittest",
        "class CorpusCliTests"
      ],
      "tests/test_corpus_index.py": [
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports unittest",
        "from skilgen.agents.codebase_signals import collect_code_evidence",
        "from skilgen.core.corpus_index import build_corpus_index",
        "from skilgen.core.deep_sampler import select_deep_read_targets",
        "class CorpusIndexTests"
      ],
      "tests/test_dashboard_cli.py": [
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "from datetime import UTC, datetime, timedelta",
        "from contextlib import redirect_stderr, redirect_stdout",
        "from io import StringIO",
        "imports json",
        "imports subprocess",
        "imports sys",
        "imports unittest",
        "from unittest.mock import patch"
      ],
      "tests/test_decision_planner.py": [
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports unittest",
        "imports subprocess",
        "from skilgen.agents.decision_planner import build_agent_decision",
        "from skilgen.core.context import build_codebase_context",
        "from skilgen.core.requirements import load_project_context",
        "from skilgen.external_skills import install_external_skill, remove_external_skill",
        "class DecisionPlannerTests"
      ],
      "tests/test_delivery.py": [
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports unittest",
        "from unittest.mock import patch",
        "from skilgen.core.models import ArchitectureBlueprint, ArchitectureDomain, SkillMaterializationPlan",
        "from skilgen.core.score import compute_skillgen_score",
        "from skilgen.delivery import run_delivery, watch_delivery",
        "class DeliveryTests"
      ],
      "tests/test_dependency_risk.py": [
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports json",
        "imports unittest",
        "from skilgen.core.dependency_risk import build_dependency_risk_graph",
        "class DependencyRiskTests"
      ],
      "tests/test_dependency_risk_graph_workstream.py": [
        "from __future__ import annotations",
        "from datetime import datetime",
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "from types import SimpleNamespace",
        "imports json",
        "from apps.api.api.routes.repos import _dependency_response, _dependency_risk_score",
        "from skilgen.core.dependency_risk import analyze_dependency_risks, dependency_report_to_dict, render_dependency_risk_report",
        "function _read",
        "function test_dependency_report_classifies_cves_and_upgrade_commands"
      ],
      "tests/test_diff.py": [
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports json",
        "imports subprocess",
        "imports sys",
        "imports unittest",
        "from skilgen.core.context import build_codebase_context",
        "from skilgen.core.diff import compute_diff",
        "from skilgen.core.freshness import save_freshness_state, snapshot_freshness_state",
        "from skilgen.core.requirements import load_project_context"
      ],
      "tests/test_document_ingestion.py": [
        "from __future__ import annotations",
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports unittest",
        "imports zipfile",
        "from skilgen.core.document_ingestion import detect_document_type, extract_document_text, normalize_extracted_text",
        "from skilgen.core.requirements import load_requirements",
        "function _write_docx",
        "function _write_pdf",
        "class DocumentIngestionTests"
      ],
      "tests/test_domain_graph_planner.py": [
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports unittest",
        "from unittest.mock import patch",
        "from skilgen.agents.domain_graph_planner import build_domain_graph, build_domain_graph_native",
        "from skilgen.core.requirements import load_requirements, synthesize_requirements_context",
        "class DomainGraphPlannerTests"
      ],
      "tests/test_enterprise_document_formats.py": [
        "from __future__ import annotations",
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports unittest",
        "from skilgen.core.document_ingestion import PdfReader",
        "from skilgen.enterprise_skills import generate_enterprise_skill",
        "function _write_pdf",
        "class EnterpriseDocumentFormatTests"
      ],
      "tests/test_enterprise_policy_cli.py": [
        "from __future__ import annotations",
        "imports json",
        "imports subprocess",
        "imports sys",
        "from datetime import UTC, datetime, timedelta",
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "function _run_cli",
        "function _write_policy",
        "function _write_skill"
      ],
      "tests/test_feature_extractor.py": [
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports unittest",
        "from skilgen.agents.feature_extractor import extract_features",
        "class FeatureExtractorTests"
      ],
      "tests/test_framework_fingerprint.py": [
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports unittest",
        "from skilgen.agents.framework_fingerprint import fingerprint_project",
        "class FrameworkFingerprintTests"
      ],
      "tests/test_identity_policy_store.py": [
        "from __future__ import annotations",
        "imports os",
        "imports unittest",
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "from unittest import mock",
        "from skilgen.core.identity_policy_store import get_identity_policy, identity_policy_store_path, list_identity_policies, resolve_identity_policy",
        "class IdentityPolicyStoreTests"
      ],
      "tests/test_jobs.py": [
        "from contextlib import closing",
        "from pathlib import Path",
        "imports sqlite3",
        "from tempfile import TemporaryDirectory",
        "imports time",
        "imports unittest",
        "from skilgen.api import jobs",
        "from skilgen.api.jobs import get_job, request_cancel, submit_job",
        "from skilgen.api.service import create_deliver_job, job_status_payload, jobs_payload, resume_job_payload",
        "class JobPersistenceTests"
      ],
      "tests/test_model_registry.py": [
        "imports os",
        "imports unittest",
        "from skilgen.agents.model_registry import resolve_model_settings",
        "from skilgen.core.models import SkilgenConfig",
        "class ModelRegistryTests"
      ],
      "tests/test_org_settings.py": [
        "from __future__ import annotations",
        "imports asyncio",
        "from datetime import datetime",
        "from types import SimpleNamespace",
        "from typing import Any",
        "from fastapi import FastAPI",
        "from fastapi.testclient import TestClient",
        "from sqlalchemy.exc import SQLAlchemyError",
        "from apps.api.api.auth import get_current_org_id",
        "from apps.api.api import analysis"
      ],
      "tests/test_overview_data.py": [
        "from __future__ import annotations",
        "from pathlib import Path",
        "from packages.db.schemas import RepoResponse",
        "function read_repo_file",
        "function test_metric_cards_render_with_real_data_and_zero_scores",
        "function test_repos_table_shows_score_badge_colors",
        "function test_relative_time_formatting_covers_short_and_old_dates",
        "function test_empty_state_shows_onboarding_cta",
        "function test_overview_uses_server_loaded_props_without_browser_refetch",
        "function test_overview_page_logs_sanitized_fetch_state"
      ],
      "tests/test_packaging.py": [
        "from pathlib import Path",
        "from tempfile import mkdtemp",
        "imports os",
        "imports shutil",
        "imports subprocess",
        "imports sys",
        "imports time",
        "imports unittest",
        "class PackagingTests"
      ],
      "tests/test_plan_cli.py": [
        "imports json",
        "from pathlib import Path",
        "imports subprocess",
        "imports sys",
        "from tempfile import TemporaryDirectory",
        "imports unittest",
        "class PlanCliTests"
      ],
      "tests/test_pr_comment.py": [
        "from __future__ import annotations",
        "imports unittest",
        "from apps.api.api.pr_comment import _delta_cell, build_comment",
        "function _score",
        "class PrCommentTests"
      ],
      "tests/test_pr_comment_dedup.py": [
        "from __future__ import annotations",
        "from typing import Any",
        "imports httpx",
        "imports pytest",
        "from apps.api.api import pr_comment",
        "class FakeAsyncClient",
        "function fake_github_client",
        "async function test_find_existing_comment_returns_none_when_no_skillayer_comment_exists",
        "async function test_find_existing_comment_returns_id_when_skillayer_comment_found",
        "async function test_update_pr_comment_makes_patch_request"
      ],
      "tests/test_rate_limit_store.py": [
        "from __future__ import annotations",
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports unittest",
        "from skilgen.core.rate_limit_store import consume_rate_limit",
        "class RateLimitStoreTests"
      ],
      "tests/test_registry_api.py": [
        "from __future__ import annotations",
        "from datetime import datetime",
        "from types import SimpleNamespace",
        "from typing import Any",
        "from fastapi import FastAPI",
        "from fastapi.testclient import TestClient",
        "from apps.api.api.auth import get_current_org_id, get_current_user",
        "from apps.api.api.routes import registry",
        "from packages.db.database import get_db",
        "class FakeResult"
      ],
      "tests/test_registry_cli.py": [
        "from __future__ import annotations",
        "imports json",
        "from http.server import BaseHTTPRequestHandler, HTTPServer",
        "imports os",
        "from pathlib import Path",
        "imports subprocess",
        "imports sys",
        "imports threading",
        "from tempfile import TemporaryDirectory",
        "from typing import ClassVar"
      ],
      "tests/test_registry_dashboard.py": [
        "from __future__ import annotations",
        "from pathlib import Path",
        "function test_registry_dashboard_uses_real_api_and_tabs",
        "function test_registry_dashboard_renders_skill_cards_with_filters"
      ],
      "tests/test_relationship_mapper.py": [
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports unittest",
        "from skilgen.agents.relationship_mapper import build_import_graph",
        "class RelationshipMapperTests"
      ],
      "tests/test_repos_screen.py": [
        "from __future__ import annotations",
        "from pathlib import Path",
        "function _read",
        "function test_repos_list_renders_with_data",
        "function test_repo_detail_shows_subscores",
        "function test_score_history_chart_data",
        "function test_analyse_button_triggers_run"
      ],
      "tests/test_requirements.py": [
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports json",
        "imports unittest",
        "from skilgen.core.requirements import load_project_context, load_requirements",
        "class RequirementsTests"
      ],
      "tests/test_requirements_parser.py": [
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports unittest",
        "from skilgen.agents.requirements_parser import parse_requirements_file",
        "class RequirementsParserTests"
      ],
      "tests/test_roadmap_planner.py": [
        "imports unittest",
        "from skilgen.agents.roadmap_planner import build_roadmap_plan",
        "from skilgen.core.models import ProjectIntent, SkilgenConfig",
        "class RoadmapPlannerTests"
      ],
      "tests/test_roadmap_skills.py": [
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports unittest",
        "from skilgen.core.requirements import load_requirements",
        "from skilgen.generators.skills import write_skills",
        "class RoadmapSkillsTests"
      ],
      "tests/test_run_memory.py": [
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports unittest",
        "from skilgen.core.models import FreshnessReport",
        "from skilgen.core.run_memory import create_run_memory, load_current_run_memory, save_run_memory",
        "class RunMemoryTests"
      ],
      "tests/test_runtime_hardening.py": [
        "imports os",
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports time",
        "from types import SimpleNamespace",
        "imports unittest",
        "from unittest.mock import patch",
        "from skilgen.deep_agents_core import _build_chat_model, _classify_model_error, _invoke_with_timeout, run_deep_json",
        "class RuntimeHardeningTests"
      ],
      "tests/test_runtime_signals.py": [
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports json",
        "imports unittest",
        "from skilgen.core.runtime_signals import collect_runtime_signals",
        "class RuntimeSignalsTests"
      ],
      "tests/test_score.py": [
        "from pathlib import Path",
        "imports subprocess",
        "from tempfile import TemporaryDirectory",
        "imports threading",
        "imports unittest",
        "from unittest.mock import patch",
        "from skilgen.core.repo_state import classify_repo_change",
        "from skilgen.core.score import compute_skillgen_score, freshness_subscore, load_score_history, record_score_history",
        "class ScoreTests"
      ],
      "tests/test_score_quality_system.py": [
        "from __future__ import annotations",
        "imports json",
        "imports subprocess",
        "imports sys",
        "from datetime import UTC, datetime",
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "from types import SimpleNamespace",
        "from typing import Any",
        "imports pytest"
      ],
      "tests/test_sdk.py": [
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports json",
        "imports unittest",
        "from unittest.mock import patch",
        "from skilgen.external_skills import ExternalSkillSource, _extract_github_repo_candidates, _normalize_external_skill_install, detect_external_skill_sources",
        "from skilgen.sdk import activate_project_mcp_connector, activate_skill_source, analyze_project, architecture_project",
        "imports time",
        "imports subprocess",
        "class SdkTests"
      ],
      "tests/test_skill_detail.py": [
        "from __future__ import annotations",
        "imports asyncio",
        "from pathlib import Path",
        "from types import SimpleNamespace",
        "from apps.api.api.routes.skills import _build_skill_response",
        "class _ScalarResult",
        "class _FakeDb",
        "function test_skill_response_includes_full_content_repo_and_usage_metadata",
        "function test_skill_detail_page_and_viewer_show_content_versions_and_usage",
        "function test_copy_button_copies_content_and_resets_success_state"
      ],
      "tests/test_skill_usage_analytics.py": [
        "from __future__ import annotations",
        "imports asyncio",
        "from datetime import UTC, datetime",
        "from pathlib import Path",
        "from types import SimpleNamespace",
        "from typing import Any",
        "from fastapi import FastAPI, HTTPException",
        "from fastapi.testclient import TestClient",
        "from apps.api.api.routes import admin, orgs, skills",
        "from apps.api.api.routes.skills import UsagePayload"
      ],
      "tests/test_skillayer_api_infra.py": [
        "from __future__ import annotations",
        "from datetime import datetime",
        "imports hashlib",
        "imports hmac",
        "imports pytest",
        "from fastapi import HTTPException",
        "from fastapi.testclient import TestClient",
        "from apps.api.api import auth",
        "from apps.api.api.index import app",
        "from apps.api.api.routes import metrics"
      ],
      "tests/test_source_graphs.py": [
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports unittest",
        "from skilgen.agents.source_graphs import build_call_graph, build_config_runtime_graph, build_parser_summary, build_symbol_graph",
        "from skilgen.agents.language_parsers import parse_language_evidence",
        "class SourceGraphTests"
      ],
      "tests/test_stripe_portal.py": [
        "from __future__ import annotations",
        "from types import SimpleNamespace",
        "from typing import Any",
        "imports pytest",
        "from fastapi import FastAPI",
        "from fastapi.testclient import TestClient",
        "from apps.api.api.auth import get_current_org_id",
        "from apps.api.api.routes import stripe",
        "from packages.db.database import get_db",
        "class FakeDb"
      ],
      "tests/test_stripe_webhook.py": [
        "from __future__ import annotations",
        "imports json",
        "from types import SimpleNamespace",
        "from typing import Any",
        "imports pytest",
        "from fastapi import FastAPI",
        "from fastapi.testclient import TestClient",
        "from apps.api.api.auth import get_current_org_id, get_current_user",
        "from apps.api.api.routes import stripe",
        "from packages.db.database import get_db"
      ],
      "tests/test_upgrade_flow.py": [
        "from pathlib import Path",
        "imports unittest",
        "function read",
        "class UpgradeFlowTests"
      ],
      "tests/test_validate_cli.py": [
        "imports json",
        "imports subprocess",
        "imports sys",
        "imports unittest",
        "class ValidateCliTests"
      ],
      "tests/test_vercel_api_deploy.py": [
        "from __future__ import annotations",
        "imports json",
        "from pathlib import Path",
        "from scripts.deploy_api import api_project_link, deploy_command, load_project_link",
        "function test_vercel_api_config_targets_python_api_entrypoint",
        "function test_deploy_command_uses_local_api_config_without_turbo_build",
        "function test_api_project_link_restores_previous_root_link"
      ],
      "tests/test_vercel_dashboard_deploy.py": [
        "from __future__ import annotations",
        "imports json",
        "from pathlib import Path",
        "from scripts.deploy_dashboard import dashboard_project_link, deploy_command, load_project_link",
        "function test_dashboard_deploy_command_supports_production_flag",
        "function test_dashboard_project_link_restores_root_link"
      ],
      "tests/test_workspace_graph.py": [
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports unittest",
        "from skilgen.agents.workspace_graph import build_workspace_graph",
        "class WorkspaceGraphTests"
      ]
    },
    "call_graph": {
      "scripts/bump_version.py": [
        "ArgumentParser",
        "Path",
        "SystemExit",
        "add_argument",
        "group",
        "main",
        "parse_args",
        "print",
        "read_text",
        "replace_version",
        "resolve",
        "subn",
        "write_text"
      ],
      "scripts/deploy_api.py": [
        "ArgumentParser",
        "FileNotFoundError",
        "Path",
        "SystemExit",
        "ValueError",
        "add_argument",
        "api_project_link",
        "append",
        "bool",
        "deploy_api",
        "deploy_command",
        "difference",
        "dumps",
        "exists",
        "int",
        "join",
        "load_project_link",
        "loads",
        "main",
        "mkdir",
        "parse_args",
        "print",
        "read_text",
        "resolve"
      ],
      "scripts/deploy_dashboard.py": [
        "ArgumentParser",
        "FileNotFoundError",
        "Path",
        "SystemExit",
        "ValueError",
        "add_argument",
        "append",
        "bool",
        "dashboard_project_link",
        "deploy_command",
        "deploy_dashboard",
        "difference",
        "dumps",
        "exists",
        "int",
        "join",
        "load_project_link",
        "loads",
        "main",
        "mkdir",
        "parse_args",
        "print",
        "read_text",
        "resolve"
      ],
      "scripts/run_requirements_pipeline.py": [
        "ArgumentParser",
        "Path",
        "add_argument",
        "dumps",
        "insert",
        "main",
        "parse_args",
        "print",
        "resolve",
        "run_delivery",
        "str"
      ],
      "setup.py": [
        "setup"
      ],
      "skilgen/agents/architecture_planner.py": [
        "ArchitectureBlueprint",
        "ArchitectureDomain",
        "SkillMaterializationPlan",
        "_evidence_graph_payload",
        "_native_architecture",
        "_redact_snippet_lines",
        "_sanitize_architecture_payload",
        "append",
        "asdict",
        "build_domain_graph",
        "build_evidence_graph",
        "exists",
        "extend",
        "float",
        "fromkeys",
        "get",
        "isinstance",
        "items",
        "join",
        "len",
        "list",
        "load_config",
        "lower",
        "replace"
      ],
      "skilgen/agents/codebase_signals.py": [
        "CodebaseSignals",
        "Path",
        "_evidence_language",
        "_evidence_text",
        "_index_tags",
        "_is_auth_file",
        "_is_backend_route",
        "_is_background_job",
        "_is_component",
        "_is_copybook",
        "_is_data_model",
        "_is_design_system_file",
        "_is_frontend_route",
        "_is_legacy_program",
        "_is_persistence_layer",
        "_is_service",
        "_is_state_file",
        "_is_test",
        "_iter_code_file_strings",
        "_iter_code_files",
        "_language_for_path",
        "_language_structure",
        "_python_structure",
        "_regex_structure"
      ],
      "skilgen/agents/decision_planner.py": [
        "AgentDecision",
        "Path",
        "active_enterprise_skills",
        "active_mcp_connectors",
        "append",
        "as_posix",
        "bool",
        "build_agent_decision_native",
        "compute_freshness_report",
        "external_skill_policy",
        "get",
        "isinstance",
        "join",
        "load_current_run_memory",
        "load_freshness_state",
        "ranked_external_skills",
        "relative_to",
        "resolve",
        "run_deep_json",
        "str"
      ],
      "skilgen/agents/domain_graph_planner.py": [
        "DomainGraph",
        "DomainGraphNode",
        "Path",
        "_app_child_summary",
        "_app_surface_summary",
        "_confidence_value",
        "_node",
        "_package_module_slug",
        "_package_module_summary",
        "_python_package_root",
        "_relative_code_files",
        "_relative_py_files",
        "_top_file",
        "_top_level_app_surfaces",
        "_workspace_domain_name",
        "_workspace_group_summary",
        "_workspace_parent_name",
        "_workspace_summary",
        "add",
        "analyze_codebase",
        "any",
        "append",
        "as_posix",
        "build_domain_graph_native"
      ],
      "skilgen/agents/evidence_graph.py": [
        "EvidenceGraph",
        "EvidenceItem",
        "_collect_config_items",
        "_collect_document_items",
        "_collect_runtime_items",
        "_text_preview",
        "analyze_codebase",
        "append",
        "as_posix",
        "build_call_graph",
        "build_config_runtime_graph",
        "build_dependency_risk_graph",
        "build_import_graph",
        "build_parser_summary",
        "build_symbol_graph",
        "build_symbol_relationships",
        "build_test_mapping",
        "build_workspace_graph",
        "collect_code_evidence",
        "collect_runtime_signals",
        "collect_structural_evidence",
        "extend",
        "get",
        "is_file"
      ],
      "skilgen/agents/feature_extractor.py": [
        "FeatureRecord",
        "analyze_codebase",
        "append",
        "extract_features_native",
        "get",
        "parse_project_intent",
        "parse_project_intent_native",
        "resolve",
        "run_deep_json",
        "str"
      ],
      "skilgen/agents/framework_fingerprint.py": [
        "FrameworkFingerprint",
        "FrameworkMatch",
        "_gather_files",
        "_match",
        "add",
        "any",
        "as_posix",
        "is_file",
        "len",
        "min",
        "relative_to",
        "replace",
        "rglob",
        "set"
      ],
      "skilgen/agents/language_parsers.py": [
        "ParsedLanguageEvidence",
        "ParsedSymbolRelationship",
        "_node_name",
        "_python_ast_parse",
        "_regex_parse",
        "_regex_relationships",
        "_safe_text",
        "_tree_sitter_parse",
        "append",
        "compile",
        "dataclass",
        "encode",
        "extend",
        "field",
        "findall",
        "finditer",
        "fromkeys",
        "fullmatch",
        "get",
        "get_tree_sitter_parser",
        "group",
        "isinstance",
        "join",
        "len"
      ],
      "skilgen/agents/model_registry.py": [
        "ModelSettings",
        "bool",
        "dict",
        "get",
        "getenv",
        "lower",
        "normalize_provider",
        "sorted",
        "strip",
        "tuple"
      ],
      "skilgen/agents/relationship_mapper.py": [
        "_iter_code_files",
        "_relative_text_imports",
        "_resolve_python_from_import",
        "_resolve_python_import",
        "_resolve_repo_local_import",
        "append",
        "as_posix",
        "catch_warnings",
        "compile",
        "exists",
        "extend",
        "findall",
        "is_dir",
        "is_file",
        "isinstance",
        "lower",
        "max",
        "parse",
        "range",
        "read_text",
        "relative_to",
        "replace",
        "resolve",
        "set"
      ],
      "skilgen/agents/requirements_parser.py": [
        "ProjectIntent",
        "analyze_codebase",
        "append",
        "extend",
        "extract_project_intent",
        "extract_text",
        "get",
        "normalize_lines",
        "parse_project_intent_native",
        "parse_requirements_file",
        "parse_requirements_file_native",
        "resolve",
        "run_deep_json",
        "str"
      ],
      "skilgen/agents/roadmap_planner.py": [
        "Path",
        "PlanStep",
        "RoadmapPlan",
        "append",
        "build_roadmap_plan_native",
        "get",
        "resolve",
        "resolve_model_settings",
        "run_deep_json",
        "str"
      ],
      "skilgen/agents/source_graphs.py": [
        "Path",
        "SymbolRelationship",
        "_cached_parse",
        "_cached_text",
        "_import_candidates",
        "_is_test",
        "_iter_code_files",
        "_language_structure",
        "_parsed_language_evidence",
        "_python_call_names",
        "_regex_call_names",
        "_safe_text",
        "_safe_text_cached",
        "_tokenize_stem",
        "add",
        "any",
        "append",
        "as_posix",
        "build_call_graph",
        "build_config_runtime_graph",
        "build_import_graph",
        "build_parser_summary",
        "build_symbol_graph",
        "build_symbol_relationships"
      ],
      "skilgen/agents/workspace_graph.py": [
        "WorkspaceDependency",
        "WorkspaceGraph",
        "WorkspacePackage",
        "_bazel_label_to_id",
        "_bazel_package_dirs",
        "_bazel_workspace_graph",
        "_entrypoints",
        "_internal_dependency_names",
        "_manifest_name",
        "_nx_workspace_graph",
        "_package_config_evidence",
        "_package_edges_from_manifests",
        "_package_from_directory",
        "_package_id",
        "_package_manifest_paths",
        "_package_roots_from_patterns",
        "_package_type",
        "_pnpm_workspace_graph",
        "_python_libs_fallback",
        "_relative",
        "_root_workspace_patterns",
        "_safe_json",
        "_safe_text",
        "_safe_yaml"
      ],
      "skilgen/api/jobs.py": [
        "JobCancelledError",
        "JobRecord",
        "Lock",
        "Path",
        "ThreadPoolExecutor",
        "_connect",
        "_db_path",
        "_job_root",
        "_load_job_from_disk",
        "_next_job_id",
        "_persist_job",
        "_recover_persisted_jobs",
        "_row_to_job",
        "add",
        "append",
        "append_audit_event",
        "append_job_event",
        "bool",
        "closing",
        "connect",
        "dumps",
        "execute",
        "fetchall",
        "fetchone"
      ],
      "skilgen/api/server.py": [
        "ApiPrincipal",
        "BoundedSemaphore",
        "BoundedThreadPoolHTTPServer",
        "FileNotFoundError",
        "JsonFormatter",
        "Lock",
        "OidcClaimMapping",
        "Path",
        "PermissionError",
        "StreamHandler",
        "ThreadPoolExecutor",
        "ValueError",
        "__init__",
        "_allow_insecure_loopback",
        "_allowed_project_roots",
        "_assert_public_remote_host",
        "_auth_is_configured",
        "_bucket_key",
        "_claim_first",
        "_claim_values",
        "_claims_allowed_roots",
        "_claims_principal",
        "_claims_scope",
        "_claims_tenant"
      ],
      "skilgen/api/service.py": [
        "DeepAgentsRuntime",
        "Path",
        "_with_api_meta",
        "activate_external_skill",
        "activate_mcp_connector",
        "active_enterprise_skills",
        "active_external_skills",
        "active_mcp_connectors",
        "analytics_summary",
        "append",
        "auto_update_status",
        "build_agent_decision",
        "build_codebase_context",
        "compute_diff",
        "compute_freshness_report",
        "compute_skillgen_score",
        "connector_catalog",
        "create_deliver_job",
        "current_runtime_mode",
        "deactivate_external_skill",
        "deactivate_mcp_connector",
        "deliver_payload",
        "detect_external_skill_sources",
        "export_external_skill_lock"
      ],
      "skilgen/autoupdate.py": [
        "Path",
        "Popen",
        "_file_snapshot",
        "_record_requirements_path",
        "_requirements_path_for_worker",
        "_requirements_record_path",
        "_snapshot",
        "_state_dir",
        "_state_path",
        "_timestamp",
        "_write_state",
        "as_posix",
        "auto_update_status",
        "classify_repo_change",
        "dumps",
        "exists",
        "get",
        "getpid",
        "git_repo_state",
        "is_file",
        "is_generated_output_path",
        "is_ignored_path_parts",
        "is_internal_skillayer_monorepo",
        "isinstance"
      ],
      "skilgen/cli/main.py": [
        "ArgumentParser",
        "CliProgressReporter",
        "Event",
        "Lock",
        "Path",
        "ProgressMilestone",
        "Thread",
        "_elapsed",
        "_format_analytics_summary",
        "_infer_percent",
        "_render_line",
        "activate_external_skill",
        "activate_mcp_connector",
        "active_external_skills",
        "active_mcp_connectors",
        "add_argument",
        "add_parser",
        "add_subparsers",
        "all",
        "analytics_payload",
        "analyze_dependency_risks",
        "analyze_payload",
        "append",
        "architecture_payload"
      ],
      "skilgen/core/analytics.py": [
        "Counter",
        "Path",
        "_analytics_path",
        "_iter_repo_skill_files",
        "_modeled_attention_score",
        "_normalize_skill_path",
        "_skill_content_metrics",
        "_skill_title_and_summary",
        "_timestamp",
        "active_external_skills",
        "add",
        "append",
        "as_posix",
        "count",
        "defaultdict",
        "dumps",
        "exists",
        "findall",
        "get",
        "getenv",
        "int",
        "is_absolute",
        "is_file",
        "isoformat"
      ],
      "skilgen/core/audit.py": [
        "Lock",
        "Path",
        "_write_audit_payload",
        "audit_log_path",
        "central_audit_log_path",
        "dumps",
        "fileno",
        "flock",
        "flush",
        "fsync",
        "getenv",
        "isoformat",
        "mkdir",
        "now",
        "open",
        "resolve",
        "str",
        "strip",
        "suppress",
        "write"
      ],
      "skilgen/core/auth_tokens.py": [
        "Lock",
        "PKCS1v15",
        "Path",
        "RSAPublicNumbers",
        "Request",
        "SHA256",
        "SignedTokenError",
        "_assert_scope_claim",
        "_assert_secure_url",
        "_audiences",
        "_base64url_decode",
        "_base64url_encode",
        "_base64url_to_int",
        "_is_loopback_host",
        "_issuer_discovery_url",
        "_load_remote_json",
        "_matching_jwk",
        "_normalize_timestamp",
        "_parse_token",
        "_rsa_public_key_from_jwk",
        "_validate_registered_claims",
        "all",
        "any",
        "append"
      ],
      "skilgen/core/config.py": [
        "CorpusSettings",
        "SkilgenConfig",
        "_bool_value",
        "_dict_value",
        "_float_value",
        "_int_value",
        "_parse_scalar",
        "_parse_yaml_like",
        "_string_list",
        "_string_or_none",
        "append",
        "endswith",
        "enumerate",
        "exists",
        "float",
        "get",
        "int",
        "isdigit",
        "isinstance",
        "items",
        "len",
        "list",
        "lower",
        "lstrip"
      ],
      "skilgen/core/context.py": [
        "CodebaseContext",
        "DomainRecord",
        "SkillTreeNode",
        "_build_file_tree",
        "_dependency_map",
        "_domain_records",
        "_skill_tree",
        "_top_level_app_surfaces",
        "analyze_codebase",
        "append",
        "as_posix",
        "build_domain_graph",
        "build_workspace_graph",
        "detect_repo_archetype",
        "exists",
        "fingerprint_project",
        "fromkeys",
        "get",
        "glob",
        "is_dir",
        "is_file",
        "is_ignored_path_parts",
        "is_internal_skillayer_monorepo",
        "iterdir"
      ],
      "skilgen/core/corpus_index.py": [
        "PurePosixPath",
        "_apply_source_importance",
        "_build_clusters",
        "_build_entry",
        "_build_import_graph",
        "_candidate_files",
        "_classify_path",
        "_document_terms",
        "_documentation_score",
        "_enterprise_score",
        "_enterprise_significant",
        "_is_excluded",
        "_iter_indexable_files",
        "_matches_pattern",
        "_module_index",
        "_resolve_import",
        "_runtime_terms",
        "_safe_text",
        "_sha256",
        "_source_terms",
        "add",
        "analyze_codebase",
        "any",
        "append"
      ],
      "skilgen/core/deep_sampler.py": [
        "CorpusSettings",
        "Path",
        "_cluster_representatives",
        "_corpus_settings",
        "_entries_by_category",
        "add",
        "append",
        "extend",
        "float",
        "get",
        "isinstance",
        "items",
        "len",
        "load_config",
        "max",
        "min",
        "resolve",
        "set",
        "sort",
        "sorted",
        "str"
      ],
      "skilgen/core/dependency_risk.py": [
        "DependencyFinding",
        "DependencyRiskEdge",
        "DependencyRiskGraph",
        "DependencyRiskNode",
        "DependencyRiskReport",
        "Path",
        "_cargo_deps",
        "_clean_exact_version",
        "_dependency_key",
        "_external_dependency_signals",
        "_find_cycles",
        "_go_mod_deps",
        "_load_json",
        "_manifest_dependencies",
        "_manifest_dependency_records",
        "_package_json_deps",
        "_pyproject_deps",
        "_requirements_deps",
        "_risk_level",
        "_upgrade_command",
        "_vulnerability_ids",
        "add",
        "analyze_dependency_risks",
        "any"
      ],
      "skilgen/core/diff.py": [
        "Path",
        "_classify_changed_files",
        "_current_git_event_from_state",
        "any",
        "append",
        "build_codebase_context",
        "compute_freshness_report",
        "freshness_subscore",
        "get",
        "git_repo_state",
        "len",
        "load_freshness_state",
        "load_project_context",
        "resolve",
        "set",
        "snapshot_freshness_state",
        "sorted"
      ],
      "skilgen/core/document_ingestion.py": [
        "BeautifulSoup",
        "PdfReader",
        "Presentation",
        "ZipFile",
        "_extract_config",
        "_extract_csv",
        "_extract_docx",
        "_extract_html",
        "_extract_json",
        "_extract_pdf",
        "_extract_pptx",
        "_extract_toml",
        "_extract_xlsx",
        "_extract_xml",
        "_extract_yaml",
        "_flatten",
        "append",
        "decode",
        "enumerate",
        "extend",
        "extract_text",
        "fromstring",
        "get_text",
        "getattr"
      ],
      "skilgen/core/enterprise_policy.py": [
        "EnterprisePolicy",
        "Path",
        "PolicyCheck",
        "ValueError",
        "_blocked_license_hits",
        "_int_field",
        "_license_sources",
        "_license_summary",
        "_materialized_domains",
        "_normalize_license",
        "_skill_last_updated",
        "_stale_skills",
        "_string_list_field",
        "active_external_skills",
        "all",
        "analyze_dependency_risks",
        "any",
        "append",
        "as_posix",
        "asdict",
        "compute_skillgen_score",
        "copy",
        "dataclass",
        "date"
      ],
      "skilgen/core/evals.py": [
        "Path",
        "dumps",
        "float",
        "get",
        "join",
        "loads",
        "mkdir",
        "read_text",
        "resolve",
        "round",
        "str",
        "write_text"
      ],
      "skilgen/core/freshness.py": [
        "FreshnessReport",
        "FreshnessState",
        "Path",
        "_filter_source_hashes",
        "_hash_file",
        "_is_ignored",
        "_is_internal_skillayer_monorepo",
        "_is_trackable_source_path",
        "_iter_source_files",
        "_state_dir",
        "_state_path",
        "_top_level_domains",
        "add",
        "any",
        "append",
        "as_posix",
        "asdict",
        "dumps",
        "endswith",
        "exists",
        "get",
        "hexdigest",
        "is_dir",
        "is_file"
      ],
      "skilgen/core/generated_outputs.py": [
        "Path",
        "frozenset",
        "len"
      ],
      "skilgen/core/identity_policy_store.py": [
        "Path",
        "RuntimeError",
        "ValueError",
        "_connect",
        "_normalize_claim_list",
        "_normalize_group_roots_map",
        "_normalize_group_scope_map",
        "append",
        "closing",
        "connect",
        "cwd",
        "dumps",
        "execute",
        "fetchall",
        "fetchone",
        "get",
        "get_identity_policy",
        "getenv",
        "identity_policy_store_path",
        "isinstance",
        "isoformat",
        "items",
        "loads",
        "lower"
      ],
      "skilgen/core/models.py": [
        "WorkspaceGraph",
        "dataclass",
        "field"
      ],
      "skilgen/core/project_memory.py": [
        "ProjectMemory",
        "_memory_dir",
        "_project_memory_path",
        "asdict",
        "dumps",
        "exists",
        "get",
        "join",
        "list",
        "loads",
        "mkdir",
        "read_text",
        "resolve",
        "sorted",
        "str",
        "write_text"
      ],
      "skilgen/core/rate_limit_store.py": [
        "Path",
        "_connect",
        "ceil",
        "close",
        "connect",
        "cwd",
        "execute",
        "exists",
        "fetchone",
        "float",
        "getenv",
        "int",
        "max",
        "mkdir",
        "rate_limit_store_path",
        "resolve",
        "strip"
      ],
      "skilgen/core/repo_state.py": [
        "Path",
        "_git_dir",
        "_git_lines",
        "_git_output",
        "_git_show",
        "_semantic_path_kind",
        "_structural_signal_summary",
        "abs",
        "any",
        "append",
        "as_posix",
        "classify_commit_intent",
        "exists",
        "get",
        "is_absolute",
        "isinstance",
        "len",
        "lower",
        "max",
        "parse_language_text",
        "resolve",
        "round",
        "run",
        "search"
      ],
      "skilgen/core/requirements.py": [
        "Path",
        "ProjectIntent",
        "RequirementsContext",
        "_remembered_requirements_path",
        "any",
        "append",
        "as_posix",
        "detect_domains",
        "encode",
        "exists",
        "extend",
        "extract_document_text",
        "extract_text",
        "get",
        "hexdigest",
        "is_file",
        "is_ignored_path_parts",
        "is_internal_skillayer_monorepo",
        "isinstance",
        "join",
        "len",
        "load_requirements",
        "loads",
        "lower"
      ],
      "skilgen/core/run_memory.py": [
        "JSONDecoder",
        "Path",
        "RunMemory",
        "_current_run_path",
        "_load_json_recovering",
        "_memory_dir",
        "_runs_dir",
        "_write_json_atomic",
        "append",
        "asdict",
        "dumps",
        "exists",
        "get",
        "isinstance",
        "isspace",
        "len",
        "loads",
        "mkdir",
        "raw_decode",
        "read_text",
        "replace",
        "resolve",
        "save_run_memory",
        "str"
      ],
      "skilgen/core/runtime_data.py": [
        "Path",
        "exists",
        "is_dir",
        "is_file",
        "iterdir",
        "len",
        "load_config",
        "max",
        "next",
        "resolve",
        "rglob",
        "rmdir",
        "rmtree",
        "runtime_data_root",
        "sorted",
        "stat",
        "str",
        "sum",
        "time",
        "unlink"
      ],
      "skilgen/core/runtime_signals.py": [
        "Path",
        "RuntimeSignalArtifact",
        "RuntimeSignals",
        "_collect_trace_paths",
        "_json_load",
        "_looks_like_runtime_artifact",
        "_parse_coverage_xml",
        "_parse_junit_xml",
        "_parse_lcov",
        "_parse_sarif",
        "_parse_trace_json",
        "_read_text",
        "_safe_relative",
        "add",
        "any",
        "append",
        "as_posix",
        "endswith",
        "extend",
        "find",
        "findall",
        "float",
        "fromkeys",
        "fromstring"
      ],
      "skilgen/core/score.py": [
        "Lock",
        "Path",
        "ValueError",
        "_assemble_scorecard",
        "_badge_color",
        "_build_score_context",
        "_coverage_score",
        "_coverage_unit",
        "_domain_key_files",
        "_domain_scorecards",
        "_evidence_hits_for_skill",
        "_freshness_score",
        "_freshness_score_for_skill",
        "_groundedness_score",
        "_groundedness_score_for_skills",
        "_has_git_metadata",
        "_iter_source_files",
        "_materialized_domains",
        "_nodes_by_domain",
        "_parse_check_paths",
        "_parse_references",
        "_quality_gates",
        "_resolve_placeholder_path",
        "_score_history_path"
      ],
      "skilgen/core/validation.py": [
        "Path",
        "_has_skill_matching",
        "_needs_bidirectional_check",
        "_parse_references",
        "_repo_native_top_level_skills",
        "_skill_paths",
        "add",
        "analyze_codebase",
        "any",
        "append",
        "as_posix",
        "bool",
        "endswith",
        "exists",
        "extend",
        "int",
        "items",
        "len",
        "max",
        "min",
        "read_text",
        "relative_to",
        "resolve",
        "rglob"
      ],
      "skilgen/deep_agents_core.py": [
        "Path",
        "Queue",
        "RuntimeError",
        "Thread",
        "TimeoutError",
        "ValueError",
        "_build_chat_model",
        "_classify_model_error",
        "_close_model",
        "_extract_json",
        "_invoke_with_retry",
        "_invoke_with_timeout",
        "_is_transient_error",
        "_message_text",
        "_model_name",
        "_normalize_json_with_model",
        "_provider_docs_url",
        "_provider_env_hint",
        "_redacted_env_name",
        "_resolved_settings",
        "any",
        "append",
        "bool",
        "callable"
      ],
      "skilgen/deep_agents_runtime.py": [
        "Path",
        "RuntimeError",
        "ValueError",
        "_analysis_bundle",
        "_build_chat_model",
        "_build_model",
        "_classify_model_error",
        "_close_model",
        "_extract_json_block",
        "_invoke_with_retry",
        "_make_tools",
        "_message_text",
        "_normalize_json_with_model",
        "_repo_shape_payload",
        "_serialize",
        "_top_level_app_surfaces",
        "active_enterprise_skills",
        "active_external_skills",
        "active_mcp_connectors",
        "add",
        "analytics_summary",
        "analyze_codebase",
        "append",
        "as_posix"
      ],
      "skilgen/delivery.py": [
        "Path",
        "_emit",
        "append",
        "append_audit_event",
        "append_run_event",
        "as_posix",
        "build_agent_decision",
        "build_codebase_context",
        "classify_repo_change",
        "clear_codebase_signal_caches",
        "clear_source_graph_caches",
        "compute_freshness_report",
        "create_run_memory",
        "current_runtime_mode",
        "ensure_corpus_index",
        "ensure_enterprise_skills_for_project",
        "ensure_external_skills_for_project",
        "extend",
        "finalize_run_memory",
        "fingerprint_project",
        "git_repo_state",
        "is_file",
        "is_generated_output_path",
        "is_ignored_path_parts"
      ],
      "skilgen/enterprise_skills.py": [
        "MCPConnector",
        "Path",
        "ValueError",
        "_catalog_connector",
        "_connector_keywords",
        "_connector_manifest_path",
        "_connector_root",
        "_copy_source",
        "_detect_license_text",
        "_download_url_source",
        "_ingest_from_git",
        "_load_connector_manifest",
        "_load_json",
        "_load_policy_pack",
        "_load_skills_manifest",
        "_name_from_git_url",
        "_name_from_url",
        "_normalize_slug",
        "_policy_pack_path",
        "_remote_source_timeout_seconds",
        "_run_git_command",
        "_skills_manifest_path",
        "_skills_root",
        "_summarize_readme"
      ],
      "skilgen/external_skills.py": [
        "ExternalSkillSource",
        "FileExistsError",
        "KeyError",
        "Path",
        "PermissionError",
        "ValueError",
        "_adapter_for_source",
        "_build_install_metadata",
        "_build_provenance_payload",
        "_catalog_entry",
        "_catalog_tags",
        "_collect_normalized_entries",
        "_compute_trust_score",
        "_detect_license",
        "_entry_score",
        "_export_lock_path",
        "_external_skills_root",
        "_extract_adapter_native_view",
        "_extract_anthropic_native_view",
        "_extract_directory_native_view",
        "_extract_github_repo_candidates",
        "_extract_huggingface_native_view",
        "_extract_langchain_native_view",
        "_git_remote_url"
      ],
      "skilgen/generators/package.py": [
        "Path",
        "ProjectAnalysisBundle",
        "_analysis_bundle",
        "_compact_label",
        "_count_phrase",
        "_dependency_domain_for_path",
        "_dependency_risk_level",
        "_display_domain_name",
        "_display_skill_name",
        "_emit_progress",
        "_graph_domain_name",
        "_graph_skill_name",
        "_meaningful_trend_points",
        "_node_id",
        "_render_feature_inventory_native",
        "_render_project_report_native",
        "_render_traceability_report_native",
        "_skilgen_logo_svg",
        "_trend_label",
        "_trend_signature",
        "active_enterprise_skills",
        "active_external_skills",
        "active_mcp_connectors",
        "add"
      ],
      "skilgen/generators/skills.py": [
        "Path",
        "SkillSpec",
        "_architecture_domain_map",
        "_dependency_ecosystems_for_spec",
        "_dynamic_child_specs",
        "_dynamic_parent_specs",
        "_dynamic_summary_paths",
        "_emit_progress",
        "_frontmatter_value",
        "_legacy_child_specs",
        "_looks_generated_skill",
        "_materialization_plan_map",
        "_parent_reference_map",
        "_prune_stale_generated_paths",
        "_relative_skill_ref",
        "_render_skill_native",
        "_select_specs",
        "_should_render_natively",
        "_signal_bullets",
        "_slug_name",
        "_with_dependency_patterns",
        "add",
        "analyze_codebase",
        "any"
      ],
      "skilgen/registry_client.py": [
        "RegistryClientError",
        "Request",
        "_api_key",
        "_api_url",
        "_request_json",
        "cast",
        "decode",
        "dict",
        "dumps",
        "encode",
        "exists",
        "get",
        "getenv",
        "is_dir",
        "is_file",
        "isinstance",
        "loads",
        "read",
        "read_text",
        "rstrip",
        "str",
        "strip",
        "urlopen",
        "write_text"
      ],
      "skilgen/sdk.py": [
        "Path",
        "activate_external_skill",
        "activate_mcp_connector",
        "active_external_skills",
        "active_mcp_connectors",
        "analytics_payload",
        "analyze_payload",
        "architecture_payload",
        "auto_update_status",
        "cancel_job_payload",
        "compare_eval_results",
        "connector_catalog",
        "create_deliver_job",
        "dashboard_payload",
        "deactivate_external_skill",
        "deactivate_mcp_connector",
        "decision_payload",
        "detect_external_skill_sources",
        "diff_payload",
        "ensure_auto_update_worker",
        "exists",
        "export_external_skill_lock",
        "external_skill_lock",
        "external_skill_policy"
      ],
      "tests/oidc_test_utils.py": [
        "HTTPServer",
        "PKCS1v15",
        "Path",
        "SHA256",
        "Thread",
        "_base64url_encode",
        "_int_to_base64url",
        "bit_length",
        "decode",
        "dumps",
        "encode",
        "end_headers",
        "generate_private_key",
        "int",
        "join",
        "len",
        "max",
        "public_key",
        "public_numbers",
        "resolve",
        "rstrip",
        "send_header",
        "send_response",
        "server_close"
      ],
      "tests/test_analytics.py": [
        "Path",
        "TemporaryDirectory",
        "analytics_summary",
        "assertEqual",
        "assertGreater",
        "assertIn",
        "assertNotEqual",
        "assertTrue",
        "len",
        "log_skill_usage",
        "main",
        "mkdir",
        "render_analytics_radial_data",
        "resolve",
        "set",
        "str",
        "write_text"
      ],
      "tests/test_api_smoke.py": [
        "AssertionError",
        "Formatter",
        "LocalOidcServer",
        "Path",
        "Request",
        "StreamHandler",
        "StringIO",
        "TemporaryDirectory",
        "Thread",
        "addHandler",
        "append",
        "assertEqual",
        "assertFalse",
        "assertGreaterEqual",
        "assertIn",
        "assertIsNotNone",
        "assertTrue",
        "create_server",
        "decode",
        "dict",
        "dumps",
        "encode",
        "exists",
        "flush"
      ],
      "tests/test_architecture_cli.py": [
        "Path",
        "TemporaryDirectory",
        "assertEqual",
        "assertIn",
        "assertTrue",
        "exists",
        "loads",
        "lower",
        "main",
        "mkdir",
        "read_text",
        "run",
        "str",
        "write_text"
      ],
      "tests/test_architecture_planner.py": [
        "ArchitectureBlueprint",
        "ArchitectureDomain",
        "DependencyRiskGraph",
        "DependencyRiskNode",
        "DomainGraph",
        "DomainGraphNode",
        "EvidenceGraph",
        "EvidenceItem",
        "Path",
        "RuntimeSignalArtifact",
        "RuntimeSignals",
        "SkillMaterializationPlan",
        "SymbolRelationship",
        "TemporaryDirectory",
        "_evidence_graph_payload",
        "_sanitize_architecture_payload",
        "assertEqual",
        "assertIn",
        "assertTrue",
        "cwd",
        "join",
        "main",
        "mkdir",
        "write_text"
      ],
      "tests/test_audit.py": [
        "Path",
        "TemporaryDirectory",
        "append_audit_event",
        "assertGreaterEqual",
        "assertTrue",
        "dict",
        "exists",
        "main",
        "patch",
        "str"
      ],
      "tests/test_auth_claim_mapping.py": [
        "Path",
        "TemporaryDirectory",
        "_claims_allowed_roots",
        "_claims_principal",
        "_claims_scope",
        "_claims_tenant",
        "_provider_claim_mapping",
        "assertEqual",
        "dict",
        "dumps",
        "json_dumps",
        "main",
        "resolve",
        "str"
      ],
      "tests/test_auth_tokens.py": [
        "LocalOidcServer",
        "Path",
        "TemporaryDirectory",
        "assertEqual",
        "assertRaises",
        "clear_remote_verifier_caches",
        "generate_rsa_signing_material",
        "main",
        "mint_rs256_token",
        "mint_signed_token",
        "resolve",
        "str",
        "time",
        "verify_jwks_token",
        "verify_oidc_token",
        "verify_signed_token"
      ],
      "tests/test_autoupdate.py": [
        "Path",
        "TemporaryDirectory",
        "_file_snapshot",
        "assertEqual",
        "main",
        "mkdir",
        "set",
        "write_text"
      ],
      "tests/test_cli.py": [
        "Path",
        "TemporaryDirectory",
        "assertEqual",
        "assertFalse",
        "assertGreaterEqual",
        "assertIn",
        "assertLessEqual",
        "assertNotEqual",
        "assertNotIn",
        "assertTrue",
        "exists",
        "join",
        "len",
        "loads",
        "lower",
        "main",
        "mkdir",
        "read_text",
        "run",
        "splitlines",
        "str",
        "strip",
        "write_text"
      ],
      "tests/test_codebase_signals.py": [
        "Path",
        "TemporaryDirectory",
        "analyze_codebase",
        "assertEqual",
        "assertIn",
        "assertNotIn",
        "assertTrue",
        "collect_code_evidence",
        "collect_structural_evidence",
        "main",
        "mkdir",
        "write_text"
      ],
      "tests/test_config.py": [
        "Path",
        "TemporaryDirectory",
        "assertEqual",
        "assertIn",
        "assertNotIn",
        "assertTrue",
        "join",
        "load_config",
        "main",
        "render_default_config",
        "write_text"
      ],
      "tests/test_context.py": [
        "Path",
        "TemporaryDirectory",
        "assertEqual",
        "assertIn",
        "assertTrue",
        "build_codebase_context",
        "load_requirements",
        "main",
        "mkdir",
        "next",
        "write_text"
      ],
      "tests/test_corpus_cli.py": [
        "Path",
        "TemporaryDirectory",
        "assertEqual",
        "assertFalse",
        "assertGreaterEqual",
        "assertTrue",
        "exists",
        "loads",
        "main",
        "mkdir",
        "resolve",
        "run",
        "str",
        "write_text"
      ],
      "tests/test_corpus_index.py": [
        "Path",
        "TemporaryDirectory",
        "any",
        "assertIn",
        "assertNotIn",
        "assertTrue",
        "build_corpus_index",
        "collect_code_evidence",
        "exists",
        "main",
        "mkdir",
        "select_deep_read_targets",
        "startswith",
        "write_text"
      ],
      "tests/test_dashboard_cli.py": [
        "Path",
        "StringIO",
        "TemporaryDirectory",
        "_analysis_bundle",
        "any",
        "append",
        "assertEqual",
        "assertIn",
        "assertLess",
        "assertLessEqual",
        "assertNotIn",
        "assertTrue",
        "count",
        "datetime",
        "dumps",
        "get",
        "getvalue",
        "index",
        "isoformat",
        "join",
        "keys",
        "load_project_context",
        "loads",
        "main"
      ],
      "tests/test_decision_planner.py": [
        "Path",
        "TemporaryDirectory",
        "any",
        "assertIn",
        "assertTrue",
        "build_agent_decision",
        "build_codebase_context",
        "install_external_skill",
        "load_project_context",
        "main",
        "mkdir",
        "remove_external_skill",
        "resolve",
        "run",
        "str",
        "write_text"
      ],
      "tests/test_delivery.py": [
        "ArchitectureBlueprint",
        "ArchitectureDomain",
        "Path",
        "SkillMaterializationPlan",
        "TemporaryDirectory",
        "append",
        "assertEqual",
        "assertFalse",
        "assertGreaterEqual",
        "assertIn",
        "assertNotIn",
        "assertTrue",
        "assert_called_once",
        "compute_skillgen_score",
        "exists",
        "join",
        "len",
        "main",
        "mkdir",
        "patch",
        "read_text",
        "resolve",
        "run_delivery",
        "str"
      ],
      "tests/test_dependency_risk.py": [
        "Path",
        "TemporaryDirectory",
        "any",
        "assertTrue",
        "build_dependency_risk_graph",
        "dumps",
        "main",
        "mkdir",
        "next",
        "startswith",
        "write_text"
      ],
      "tests/test_dependency_risk_graph_workstream.py": [
        "Path",
        "SimpleNamespace",
        "TemporaryDirectory",
        "_dependency_response",
        "_dependency_risk_score",
        "_read",
        "analyze_dependency_risks",
        "datetime",
        "dependency_report_to_dict",
        "dumps",
        "read_text",
        "render_dependency_risk_report",
        "resolve",
        "write_text"
      ],
      "tests/test_diff.py": [
        "Path",
        "TemporaryDirectory",
        "_save_baseline",
        "assertEqual",
        "assertIn",
        "assertTrue",
        "build_codebase_context",
        "compute_diff",
        "dumps",
        "isdisjoint",
        "load_project_context",
        "loads",
        "main",
        "mkdir",
        "read_text",
        "run",
        "save_freshness_state",
        "set",
        "snapshot_freshness_state",
        "str",
        "unlink",
        "update",
        "write_text"
      ],
      "tests/test_document_ingestion.py": [
        "AssertionError",
        "Path",
        "Presentation",
        "TemporaryDirectory",
        "Workbook",
        "ZipFile",
        "_write_docx",
        "_write_pdf",
        "add_slide",
        "append",
        "assertEqual",
        "assertIn",
        "assertNotIn",
        "assertTrue",
        "detect_document_type",
        "encode",
        "extend",
        "extract_document_text",
        "join",
        "len",
        "load_requirements",
        "lower",
        "main",
        "make_source"
      ],
      "tests/test_domain_graph_planner.py": [
        "Path",
        "TemporaryDirectory",
        "any",
        "assertIn",
        "assertNotIn",
        "assertTrue",
        "build_domain_graph",
        "build_domain_graph_native",
        "fallback",
        "items",
        "load_requirements",
        "main",
        "mkdir",
        "patch",
        "synthesize_requirements_context",
        "write_text"
      ],
      "tests/test_enterprise_document_formats.py": [
        "Path",
        "TemporaryDirectory",
        "_write_pdf",
        "append",
        "assertIn",
        "encode",
        "extend",
        "generate_enterprise_skill",
        "join",
        "len",
        "main",
        "read_text",
        "skipUnless",
        "write_bytes",
        "write_text"
      ],
      "tests/test_enterprise_policy_cli.py": [
        "Path",
        "TemporaryDirectory",
        "_minimal_source",
        "_run_cli",
        "_write_policy",
        "_write_skill",
        "date",
        "isoformat",
        "join",
        "loads",
        "mkdir",
        "now",
        "read_text",
        "resolve",
        "run",
        "set",
        "str",
        "timedelta",
        "title",
        "write_text"
      ],
      "tests/test_feature_extractor.py": [
        "Path",
        "TemporaryDirectory",
        "assertIn",
        "assertTrue",
        "extract_features",
        "join",
        "main",
        "mkdir",
        "write_text"
      ],
      "tests/test_framework_fingerprint.py": [
        "Path",
        "TemporaryDirectory",
        "assertEqual",
        "assertIsNotNone",
        "fingerprint_project",
        "main",
        "mkdir",
        "write_text"
      ],
      "tests/test_identity_policy_store.py": [
        "Path",
        "TemporaryDirectory",
        "assertEqual",
        "assertIn",
        "assertIsNotNone",
        "dict",
        "get_identity_policy",
        "identity_policy_store_path",
        "list_identity_policies",
        "main",
        "resolve",
        "resolve_identity_policy",
        "str",
        "upsert_identity_policy"
      ],
      "tests/test_jobs.py": [
        "Path",
        "TemporaryDirectory",
        "assertEqual",
        "assertIn",
        "assertIsNotNone",
        "assertTrue",
        "clear",
        "closing",
        "connect",
        "create_deliver_job",
        "execute",
        "exists",
        "get",
        "get_job",
        "job_status_payload",
        "jobs_payload",
        "main",
        "monotonic",
        "range",
        "report",
        "request_cancel",
        "resolve",
        "resume_job_payload",
        "sleep"
      ],
      "tests/test_model_registry.py": [
        "SkilgenConfig",
        "assertEqual",
        "assertIsNone",
        "assertTrue",
        "main",
        "resolve_model_settings"
      ],
      "tests/test_org_settings.py": [
        "FakeDb",
        "FakeResult",
        "FakeScalars",
        "FastAPI",
        "Path",
        "RuntimeError",
        "SQLAlchemyError",
        "SimpleNamespace",
        "TestClient",
        "_client",
        "_notify_stale_skills",
        "_org",
        "_settings_results",
        "datetime",
        "get",
        "include_router",
        "json",
        "patch",
        "pop",
        "post",
        "read_text",
        "resolve",
        "run",
        "setattr"
      ],
      "tests/test_overview_data.py": [
        "Path",
        "read_repo_file",
        "read_text",
        "resolve"
      ],
      "tests/test_packaging.py": [
        "Path",
        "_cleanup_tree",
        "assertIn",
        "assertTrue",
        "copy",
        "exists",
        "main",
        "mkdtemp",
        "range",
        "resolve",
        "rmtree",
        "run",
        "sleep",
        "str"
      ],
      "tests/test_plan_cli.py": [
        "Path",
        "TemporaryDirectory",
        "assertIn",
        "assertTrue",
        "loads",
        "main",
        "run",
        "str",
        "write_text"
      ],
      "tests/test_pr_comment.py": [
        "_delta_cell",
        "_score",
        "assertEqual",
        "assertIn",
        "assertNotIn",
        "build_comment",
        "lower",
        "main",
        "subTest"
      ],
      "tests/test_pr_comment_dedup.py": [
        "Response",
        "append",
        "create_check_run",
        "find_existing_comment",
        "fixture",
        "setattr",
        "update_pr_comment"
      ],
      "tests/test_rate_limit_store.py": [
        "Path",
        "TemporaryDirectory",
        "assertEqual",
        "assertFalse",
        "assertGreaterEqual",
        "assertTrue",
        "consume_rate_limit",
        "main"
      ],
      "tests/test_registry_api.py": [
        "FakeDb",
        "FakeResult",
        "FastAPI",
        "SimpleNamespace",
        "TestClient",
        "_client",
        "_objects",
        "datetime",
        "get",
        "include_router",
        "json",
        "pop",
        "post"
      ],
      "tests/test_registry_cli.py": [
        "HTTPServer",
        "Path",
        "TemporaryDirectory",
        "Thread",
        "append",
        "assertEqual",
        "decode",
        "dumps",
        "encode",
        "end_headers",
        "get",
        "int",
        "join",
        "len",
        "loads",
        "main",
        "mkdir",
        "read",
        "read_text",
        "resolve",
        "run",
        "send_header",
        "send_response",
        "shutdown"
      ],
      "tests/test_registry_dashboard.py": [
        "Path",
        "read_text",
        "resolve"
      ],
      "tests/test_relationship_mapper.py": [
        "Path",
        "TemporaryDirectory",
        "assertIn",
        "assertNotIn",
        "build_import_graph",
        "main",
        "mkdir",
        "write_bytes",
        "write_text"
      ],
      "tests/test_repos_screen.py": [
        "Path",
        "_read",
        "read_text",
        "resolve"
      ],
      "tests/test_requirements.py": [
        "Path",
        "TemporaryDirectory",
        "assertEqual",
        "assertNotEqual",
        "assertTrue",
        "dumps",
        "load_project_context",
        "load_requirements",
        "main",
        "mkdir",
        "resolve",
        "str",
        "write_text"
      ],
      "tests/test_requirements_parser.py": [
        "Path",
        "TemporaryDirectory",
        "assertTrue",
        "join",
        "main",
        "parse_requirements_file",
        "write_text"
      ],
      "tests/test_roadmap_planner.py": [
        "ProjectIntent",
        "SkilgenConfig",
        "assertIn",
        "build_roadmap_plan",
        "main"
      ],
      "tests/test_roadmap_skills.py": [
        "Path",
        "TemporaryDirectory",
        "assertIn",
        "assertTrue",
        "exists",
        "load_requirements",
        "main",
        "read_text",
        "write_skills",
        "write_text"
      ],
      "tests/test_run_memory.py": [
        "FreshnessReport",
        "Path",
        "TemporaryDirectory",
        "assertEqual",
        "assertIsNotNone",
        "create_run_memory",
        "load_current_run_memory",
        "main",
        "read_text",
        "save_run_memory",
        "write_text"
      ],
      "tests/test_runtime_hardening.py": [
        "MalformedAgent",
        "Path",
        "RateLimitedAgent",
        "RuntimeError",
        "SimpleNamespace",
        "SlowAgent",
        "TemporaryDirectory",
        "_build_chat_model",
        "_classify_model_error",
        "_invoke_with_timeout",
        "assertEqual",
        "assertFalse",
        "assertIn",
        "assertNotEqual",
        "assertNotIn",
        "assertRaises",
        "assertTrue",
        "assert_called_once",
        "dict",
        "join",
        "lower",
        "main",
        "object",
        "patch"
      ],
      "tests/test_runtime_signals.py": [
        "Path",
        "TemporaryDirectory",
        "assertEqual",
        "assertIn",
        "collect_runtime_signals",
        "dumps",
        "join",
        "len",
        "main",
        "mkdir",
        "write_text"
      ],
      "tests/test_score.py": [
        "Path",
        "TemporaryDirectory",
        "Thread",
        "_git",
        "assertEqual",
        "assertGreater",
        "assertGreaterEqual",
        "assertIn",
        "assertLessEqual",
        "assertNotIn",
        "assertTrue",
        "classify_repo_change",
        "compute_skillgen_score",
        "freshness_subscore",
        "join",
        "len",
        "load_score_history",
        "main",
        "mkdir",
        "patch",
        "range",
        "record_score_history",
        "run",
        "score_history_payload"
      ],
      "tests/test_score_quality_system.py": [
        "AssertionError",
        "FakeDb",
        "FakeResult",
        "FastAPI",
        "Path",
        "SimpleNamespace",
        "TemporaryDirectory",
        "TestClient",
        "_minimal_project",
        "_run_cli",
        "ci_result",
        "date",
        "endswith",
        "exists",
        "get",
        "get_org_stats",
        "include_router",
        "isoformat",
        "json",
        "len",
        "loads",
        "mkdir",
        "now",
        "pop"
      ],
      "tests/test_sdk.py": [
        "ExternalSkillSource",
        "Path",
        "TemporaryDirectory",
        "__import__",
        "_extract_github_repo_candidates",
        "_normalize_external_skill_install",
        "activate_project_mcp_connector",
        "activate_skill_source",
        "analyze_project",
        "any",
        "architecture_project",
        "as_uri",
        "assertEqual",
        "assertFalse",
        "assertGreater",
        "assertIn",
        "assertIsNone",
        "assertIsNotNone",
        "assertRaises",
        "assertTrue",
        "cancel_job",
        "compare_evals",
        "deactivate_project_mcp_connector",
        "deactivate_skill_source"
      ],
      "tests/test_skill_detail.py": [
        "Path",
        "SimpleNamespace",
        "_FakeDb",
        "_ScalarResult",
        "_build_skill_response",
        "pop",
        "read_text",
        "resolve",
        "run"
      ],
      "tests/test_skill_usage_analytics.py": [
        "AssertionError",
        "FakeDb",
        "FakeResult",
        "FastAPI",
        "Path",
        "SimpleNamespace",
        "TestClient",
        "UsagePayload",
        "_admin_client",
        "append",
        "compile",
        "date",
        "get_org_analytics",
        "include_router",
        "isoformat",
        "json",
        "len",
        "now",
        "pop",
        "post",
        "read_text",
        "record_skill_usage",
        "replace",
        "resolve"
      ],
      "tests/test_skillayer_api_infra.py": [
        "FakeMetricsDb",
        "FakeMetricsResult",
        "FakeMetricsSession",
        "RuntimeError",
        "TestClient",
        "_oidc_jwks_uri",
        "_verify_github_signature",
        "all",
        "datetime",
        "get",
        "getMessage",
        "get_current_user",
        "hasattr",
        "hexdigest",
        "issubset",
        "json",
        "new",
        "pop",
        "raises",
        "set_level",
        "setattr",
        "throw",
        "type"
      ],
      "tests/test_source_graphs.py": [
        "Path",
        "TemporaryDirectory",
        "assertEqual",
        "assertIn",
        "assertNotEqual",
        "assertTrue",
        "build_call_graph",
        "build_config_runtime_graph",
        "build_parser_summary",
        "build_symbol_graph",
        "build_symbol_relationships",
        "build_test_mapping",
        "items",
        "main",
        "mkdir",
        "parse_language_evidence",
        "write_text"
      ],
      "tests/test_stripe_portal.py": [
        "FakeDb",
        "FastAPI",
        "RuntimeError",
        "SimpleNamespace",
        "TestClient",
        "_client",
        "_unauthenticated_client",
        "get",
        "include_router",
        "json",
        "post",
        "setattr"
      ],
      "tests/test_stripe_webhook.py": [
        "CheckoutSessionRequest",
        "FakeDB",
        "FakeRequest",
        "FastAPI",
        "Org",
        "RuntimeError",
        "SimpleNamespace",
        "TestClient",
        "ValueError",
        "_apply_subscription_created_or_updated",
        "_apply_subscription_deleted",
        "_client",
        "_json_response_body",
        "_subscription",
        "create_checkout_session",
        "decode",
        "delenv",
        "dict",
        "include_router",
        "json",
        "loads",
        "post",
        "setattr",
        "setenv"
      ],
      "tests/test_upgrade_flow.py": [
        "Path",
        "assertIn",
        "read",
        "read_text",
        "resolve"
      ],
      "tests/test_validate_cli.py": [
        "assertIn",
        "loads",
        "main",
        "run"
      ],
      "tests/test_vercel_api_deploy.py": [
        "Path",
        "api_project_link",
        "deploy_command",
        "dumps",
        "join",
        "load_project_link",
        "loads",
        "mkdir",
        "read_text",
        "resolve",
        "write_text"
      ],
      "tests/test_vercel_dashboard_deploy.py": [
        "Path",
        "dashboard_project_link",
        "deploy_command",
        "dumps",
        "load_project_link",
        "mkdir",
        "write_text"
      ],
      "tests/test_workspace_graph.py": [
        "Path",
        "TemporaryDirectory",
        "assertEqual",
        "assertIsNone",
        "build_workspace_graph",
        "main",
        "mkdir",
        "write_text"
      ]
    },
    "config_runtime_graph": {
      ".env.example": [
        "env:API_URL",
        "env:DATABASE_URL",
        "env:DEPLOYMENT_MODE",
        "env:GITHUB_APP_ID",
        "env:GITHUB_APP_PRIVATE_KEY",
        "env:GITHUB_WEBHOOK_SECRET",
        "env:NEXT_PUBLIC_API_URL",
        "env:NEXT_PUBLIC_APP_URL",
        "env:NEXT_PUBLIC_DASHBOARD_URL",
        "env:NEXT_PUBLIC_POSTHOG_HOST",
        "env:NEXT_PUBLIC_POSTHOG_KEY",
        "env:NEXT_PUBLIC_WORKOS_REDIRECT_URI",
        "env:OIDC",
        "env:OIDC_AUDIENCE",
        "env:OIDC_ISSUER_URL",
        "env:OIDC_JWKS_URI",
        "env:QSTASH_CURRENT_SIGNING_KEY",
        "env:QSTASH_NEXT_SIGNING_KEY",
        "env:QSTASH_TOKEN",
        "env:REDIS_URL",
        "env:WORKOS_API_KEY",
        "env:WORKOS_CLIENT_ID",
        "env:WORKOS_COOKIE_PASSWORD",
        "env:WORKOS_REDIRECT_URI",
        "runtime:postgres",
        "runtime:redis"
      ],
      ".github/ISSUE_TEMPLATE/bug_report.yml": [
        "env:API",
        "env:CLI",
        "env:SDK"
      ],
      ".github/workflows/skilgen-sync.yml": [
        "env:AGENTS",
        "env:ANALYSIS",
        "env:ANTHROPIC_API_KEY",
        "env:ARCHITECTURE",
        "env:BASE_REQUIREMENTS",
        "env:FEATURES",
        "env:FORCE_JAVASCRIPT_ACTIONS_TO_NODE24",
        "env:GITHUB_ENV",
        "env:HUGGINGFACEHUB_API_TOKEN",
        "env:OPENAI_API_KEY",
        "env:README",
        "env:REPORT",
        "env:RUNNER_TEMP",
        "env:SKILGEN_REQUIREMENTS",
        "env:SKILGEN_SCORE_THRESHOLD",
        "env:TRACEABILITY"
      ],
      ".turbo/cache/05d96156f2209614-manifest.json": [
        "env:BUILD_ID",
        "env:LICENSE",
        "runtime:docker",
        "runtime:s3"
      ],
      ".turbo/cache/088ccf5a78438390-manifest.json": [
        "env:BUILD_ID"
      ],
      ".turbo/cache/1324b94b6a39f947-manifest.json": [
        "env:BUILD_ID"
      ],
      ".turbo/cache/2584744feac7447b-manifest.json": [
        "env:BUILD_ID"
      ],
      ".turbo/cache/2eabdbab3a2e656b-manifest.json": [
        "env:BUILD_ID",
        "env:LICENSE",
        "runtime:docker",
        "runtime:s3"
      ],
      ".turbo/cache/35512ec318708105-manifest.json": [
        "env:BUILD_ID",
        "env:LICENSE",
        "runtime:docker",
        "runtime:s3"
      ],
      ".turbo/cache/3af19f19c1fe0df8-manifest.json": [
        "env:BUILD_ID",
        "env:LICENSE",
        "runtime:docker",
        "runtime:s3"
      ],
      ".turbo/cache/3e91b1f588eef3a1-manifest.json": [
        "env:BUILD_ID"
      ],
      ".turbo/cache/402f872154d7e91c-manifest.json": [
        "env:BUILD_ID",
        "env:LICENSE",
        "runtime:docker",
        "runtime:s3"
      ],
      ".turbo/cache/4af23fbc7dd3950d-manifest.json": [
        "env:BUILD_ID"
      ],
      ".turbo/cache/522dea7d3da16ddd-manifest.json": [
        "env:BUILD_ID",
        "env:LICENSE",
        "runtime:docker",
        "runtime:s3"
      ],
      ".turbo/cache/5411ec82ed63d937-manifest.json": [
        "env:BUILD_ID"
      ],
      ".turbo/cache/57bbe5fb498d6e73-manifest.json": [
        "env:BUILD_ID"
      ],
      ".turbo/cache/5abbf512bbef2d4c-manifest.json": [
        "env:BUILD_ID"
      ],
      ".turbo/cache/5e3ba679fbb8594a-manifest.json": [
        "env:BUILD_ID"
      ],
      ".turbo/cache/608408b38da933ed-manifest.json": [
        "env:BUILD_ID",
        "env:LICENSE",
        "runtime:docker",
        "runtime:s3"
      ],
      ".turbo/cache/728c223a00108c10-manifest.json": [
        "env:BH7",
        "env:BUILD_ID",
        "env:F6T"
      ],
      ".turbo/cache/75539954cf1492af-manifest.json": [
        "env:BUILD_ID"
      ],
      ".turbo/cache/8ab728a3c130dbc4-manifest.json": [
        "env:BUILD_ID"
      ],
      ".turbo/cache/8b577591ff455e0d-manifest.json": [
        "env:BUILD_ID",
        "env:LICENSE",
        "runtime:docker",
        "runtime:s3"
      ],
      ".turbo/cache/8e76ca57f4f23337-manifest.json": [
        "env:BUILD_ID"
      ],
      ".turbo/cache/9563b344098c230a-manifest.json": [
        "env:BUILD_ID"
      ],
      ".turbo/cache/96cf72242e8102b4-manifest.json": [
        "env:BUILD_ID"
      ],
      ".turbo/cache/a164f264df29eb71-manifest.json": [
        "env:BUILD_ID"
      ],
      ".turbo/cache/a6a983669f950262-manifest.json": [
        "env:BUILD_ID"
      ],
      ".turbo/cache/aae74d898a0f8428-manifest.json": [
        "env:BUILD_ID"
      ],
      ".turbo/cache/b3945ac4350e177c-manifest.json": [
        "env:BUILD_ID",
        "env:LICENSE",
        "runtime:docker",
        "runtime:s3"
      ],
      ".turbo/cache/d3bee0fbe167105c-manifest.json": [
        "env:BUILD_ID"
      ],
      ".turbo/cache/e073edeea42eca79-manifest.json": [
        "env:BUILD_ID",
        "env:LICENSE",
        "runtime:docker",
        "runtime:s3"
      ],
      ".turbo/cache/eb16a4a7226b48d1-manifest.json": [
        "env:BUILD_ID"
      ],
      ".turbo/cache/fe6a1306bcbe5bfb-manifest.json": [
        "env:BUILD_ID"
      ],
      ".venv/lib/python3.13/site-packages/hf_xet-1.4.3.dist-info/sboms/hf_xet.cyclonedx.json": [
        "env:AND",
        "env:ANSI",
        "env:API",
        "env:ASCII",
        "env:AVX",
        "env:AWS",
        "env:BLAKE3",
        "env:BSD",
        "env:BSL",
        "env:CC0",
        "env:COM",
        "env:CPU",
        "env:CRC32",
        "env:CSV",
        "env:DPC",
        "env:ECN",
        "env:FFI",
        "env:GNU",
        "env:HTML",
        "env:HTTP",
        "env:HTTPS",
        "env:IANA",
        "env:ICU",
        "env:ICU4X",
        "env:IDNA",
        "env:IEEE",
        "env:IRI",
        "env:ISC",
        "env:JSON",
        "env:LLVM",
        "env:LMDB",
        "env:LRU",
        "env:LZ4",
        "env:MIME",
        "env:MIT",
        "env:MPL",
        "env:MSVC",
        "env:OSA",
        "env:PHF",
        "env:PKI",
        "env:POSIX",
        "env:QUIC",
        "env:RAII",
        "env:README",
        "env:SHA",
        "env:SIMD",
        "env:SSE2",
        "env:SSL",
        "env:TLS",
        "env:UDP",
        "env:UNC",
        "env:URL",
        "env:UTF",
        "env:VPN",
        "env:WASM",
        "env:WHATWG",
        "env:WITH",
        "env:XDG",
        "env:XXH3",
        "env:YOSHIOKA",
        "runtime:docker",
        "runtime:kubernetes"
      ],
      ".venv/lib/python3.13/site-packages/jiter-0.14.0.dist-info/sboms/jiter-python.cyclonedx.json": [
        "env:AES",
        "env:AND",
        "env:API",
        "env:BSD",
        "env:COM",
        "env:FFI",
        "env:JSON",
        "env:LEB128",
        "env:LGPL",
        "env:LLVM",
        "env:MIT",
        "env:MSVC",
        "env:SHA",
        "env:SIMD",
        "env:UEFI",
        "env:WIT",
        "env:WITH",
        "runtime:kubernetes"
      ],
      ".venv/lib/python3.13/site-packages/markdown_it/port.yaml": [
        "env:HTML"
      ],
      ".venv/lib/python3.13/site-packages/orjson-3.11.8.dist-info/sboms/orjson.cyclonedx.json": [
        "env:AND",
        "env:API",
        "env:BSD",
        "env:BSL",
        "env:COM",
        "env:FFI",
        "env:JSON",
        "env:LLVM",
        "env:LRU",
        "env:MIT",
        "env:MPL",
        "env:MSVC",
        "env:SHA",
        "env:SIMD",
        "env:UTF",
        "env:WITH",
        "runtime:kubernetes"
      ],
      ".venv/lib/python3.13/site-packages/pycparser/_c_ast.cfg": [
        "env:AST",
        "env:BSD",
        "env:C99"
      ],
      ".venv/lib/python3.13/site-packages/pydantic_core-2.46.3.dist-info/sboms/pydantic-core.cyclonedx.json": [
        "env:AES",
        "env:AND",
        "env:API",
        "env:ASCII",
        "env:BSD",
        "env:DFS",
        "env:DPC",
        "env:FFI",
        "env:HTML",
        "env:ICU",
        "env:ICU4X",
        "env:IDNA",
        "env:JSON",
        "env:LGPL",
        "env:LLVM",
        "env:LRU",
        "env:MIT",
        "env:SHA",
        "env:SIMD",
        "env:UEFI",
        "env:URL",
        "env:UTF",
        "env:WASI",
        "env:WHATWG",
        "env:WITH",
        "runtime:kubernetes"
      ],
      ".venv/lib/python3.13/site-packages/tree_sitter_language_pack-1.6.2.dist-info/sboms/ts-pack-python.cyclonedx.json": [
        "env:ABI",
        "env:AES",
        "env:AND",
        "env:API",
        "env:ASN",
        "env:BER",
        "env:BSD",
        "env:CC0",
        "env:CDLA",
        "env:CMS",
        "env:COM",
        "env:CPU",
        "env:CRC32",
        "env:DEFLATE",
        "env:DER",
        "env:FFI",
        "env:GNU",
        "env:HTTP",
        "env:IEC",
        "env:IEEE",
        "env:ISC",
        "env:ISO",
        "env:ITU",
        "env:JSON",
        "env:LEB128",
        "env:LGPL",
        "env:LLVM",
        "env:MIT",
        "env:MPL",
        "env:MSVC",
        "env:OID",
        "env:PEM",
        "env:PKCS",
        "env:PKI",
        "env:PKIX",
        "env:POSIX",
        "env:RFC",
        "env:SHA",
        "env:SIMD",
        "env:SSL",
        "env:TAR",
        "env:TLS",
        "env:TOML",
        "env:UEFI",
        "env:UTF",
        "env:WASI",
        "env:WASM",
        "env:WIT",
        "env:WITH",
        "env:XDG",
        "runtime:kubernetes"
      ],
      ".venv/lib/python3.13/site-packages/uuid_utils-0.14.1.dist-info/sboms/uuid-utils.cyclonedx.json": [
        "env:AES",
        "env:AND",
        "env:API",
        "env:BSD",
        "env:DFS",
        "env:DPC",
        "env:FFI",
        "env:LLVM",
        "env:MAC",
        "env:MD5",
        "env:MIT",
        "env:SHA",
        "env:SHA1",
        "env:WITH",
        "runtime:kubernetes"
      ],
      ".venv-api/lib/python3.13/site-packages/hf_xet-1.4.3.dist-info/sboms/hf_xet.cyclonedx.json": [
        "env:AND",
        "env:ANSI",
        "env:API",
        "env:ASCII",
        "env:AVX",
        "env:AWS",
        "env:BLAKE3",
        "env:BSD",
        "env:BSL",
        "env:CC0",
        "env:COM",
        "env:CPU",
        "env:CRC32",
        "env:CSV",
        "env:DPC",
        "env:ECN",
        "env:FFI",
        "env:GNU",
        "env:HTML",
        "env:HTTP",
        "env:HTTPS",
        "env:IANA",
        "env:ICU",
        "env:ICU4X",
        "env:IDNA",
        "env:IEEE",
        "env:IRI",
        "env:ISC",
        "env:JSON",
        "env:LLVM",
        "env:LMDB",
        "env:LRU",
        "env:LZ4",
        "env:MIME",
        "env:MIT",
        "env:MPL",
        "env:MSVC",
        "env:OSA",
        "env:PHF",
        "env:PKI",
        "env:POSIX",
        "env:QUIC",
        "env:RAII",
        "env:README",
        "env:SHA",
        "env:SIMD",
        "env:SSE2",
        "env:SSL",
        "env:TLS",
        "env:UDP",
        "env:UNC",
        "env:URL",
        "env:UTF",
        "env:VPN",
        "env:WASM",
        "env:WHATWG",
        "env:WITH",
        "env:XDG",
        "env:XXH3",
        "env:YOSHIOKA",
        "runtime:docker",
        "runtime:kubernetes"
      ],
      ".venv-api/lib/python3.13/site-packages/jiter-0.14.0.dist-info/sboms/jiter-python.cyclonedx.json": [
        "env:AES",
        "env:AND",
        "env:API",
        "env:BSD",
        "env:COM",
        "env:FFI",
        "env:JSON",
        "env:LEB128",
        "env:LGPL",
        "env:LLVM",
        "env:MIT",
        "env:MSVC",
        "env:SHA",
        "env:SIMD",
        "env:UEFI",
        "env:WIT",
        "env:WITH",
        "runtime:kubernetes"
      ],
      ".venv-api/lib/python3.13/site-packages/markdown_it/port.yaml": [
        "env:HTML"
      ],
      ".venv-api/lib/python3.13/site-packages/orjson-3.11.8.dist-info/sboms/orjson.cyclonedx.json": [
        "env:AND",
        "env:API",
        "env:BSD",
        "env:BSL",
        "env:COM",
        "env:FFI",
        "env:JSON",
        "env:LLVM",
        "env:LRU",
        "env:MIT",
        "env:MPL",
        "env:MSVC",
        "env:SHA",
        "env:SIMD",
        "env:UTF",
        "env:WITH",
        "runtime:kubernetes"
      ],
      ".venv-api/lib/python3.13/site-packages/pycparser/_c_ast.cfg": [
        "env:AST",
        "env:BSD",
        "env:C99"
      ],
      ".venv-api/lib/python3.13/site-packages/pydantic_core-2.46.2.dist-info/sboms/pydantic-core.cyclonedx.json": [
        "env:AES",
        "env:AND",
        "env:API",
        "env:ASCII",
        "env:BSD",
        "env:DFS",
        "env:DPC",
        "env:FFI",
        "env:HTML",
        "env:ICU",
        "env:ICU4X",
        "env:IDNA",
        "env:JSON",
        "env:LGPL",
        "env:LLVM",
        "env:LRU",
        "env:MIT",
        "env:SHA",
        "env:SIMD",
        "env:UEFI",
        "env:URL",
        "env:UTF",
        "env:WASI",
        "env:WHATWG",
        "env:WITH",
        "runtime:kubernetes"
      ],
      ".venv-api/lib/python3.13/site-packages/tree_sitter_language_pack-1.6.2.dist-info/sboms/ts-pack-python.cyclonedx.json": [
        "env:ABI",
        "env:AES",
        "env:AND",
        "env:API",
        "env:ASN",
        "env:BER",
        "env:BSD",
        "env:CC0",
        "env:CDLA",
        "env:CMS",
        "env:COM",
        "env:CPU",
        "env:CRC32",
        "env:DEFLATE",
        "env:DER",
        "env:FFI",
        "env:GNU",
        "env:HTTP",
        "env:IEC",
        "env:IEEE",
        "env:ISC",
        "env:ISO",
        "env:ITU",
        "env:JSON",
        "env:LEB128",
        "env:LGPL",
        "env:LLVM",
        "env:MIT",
        "env:MPL",
        "env:MSVC",
        "env:OID",
        "env:PEM",
        "env:PKCS",
        "env:PKI",
        "env:PKIX",
        "env:POSIX",
        "env:RFC",
        "env:SHA",
        "env:SIMD",
        "env:SSL",
        "env:TAR",
        "env:TLS",
        "env:TOML",
        "env:UEFI",
        "env:UTF",
        "env:WASI",
        "env:WASM",
        "env:WIT",
        "env:WITH",
        "env:XDG",
        "runtime:kubernetes"
      ],
      ".venv-api/lib/python3.13/site-packages/uuid_utils-0.14.1.dist-info/sboms/uuid-utils.cyclonedx.json": [
        "env:AES",
        "env:AND",
        "env:API",
        "env:BSD",
        "env:DFS",
        "env:DPC",
        "env:FFI",
        "env:LLVM",
        "env:MAC",
        "env:MD5",
        "env:MIT",
        "env:SHA",
        "env:SHA1",
        "env:WITH",
        "runtime:kubernetes"
      ],
      ".vercel/output/builds.json": [
        "env:API"
      ],
      ".vercel/output/functions/_not-found.rsc.func/.vc-config.json": [
        "env:BUILD_ID",
        "env:ISR"
      ],
      "apps/api/.env.example": [
        "env:ADMIN_SECRET",
        "env:DATABASE_URL",
        "env:DEPLOYMENT_MODE",
        "env:GITHUB_APP_ID",
        "env:GITHUB_APP_PRIVATE_KEY",
        "env:GITHUB_WEBHOOK_SECRET",
        "env:OIDC_AUDIENCE",
        "env:OIDC_ISSUER_URL",
        "env:OIDC_JWKS_URI",
        "env:QSTASH_BASE_URL",
        "env:QSTASH_CURRENT_SIGNING_KEY",
        "env:QSTASH_NEXT_SIGNING_KEY",
        "env:QSTASH_TOKEN",
        "env:REDIS_URL",
        "env:STRIPE_PRICE_BUSINESS",
        "env:STRIPE_PRICE_TEAM",
        "env:STRIPE_SECRET_KEY",
        "env:STRIPE_WEBHOOK_SECRET",
        "env:WORKOS_API_KEY",
        "env:WORKOS_CLIENT_ID",
        "runtime:postgres",
        "runtime:redis"
      ],
      "apps/api/Dockerfile": [
        "env:CMD",
        "env:COPY",
        "env:EXPOSE",
        "env:FROM",
        "env:HEALTHCHECK",
        "env:RUN",
        "env:WORKDIR"
      ],
      "apps/api/alembic.ini": [
        "env:INFO",
        "env:NOT",
        "env:NOTSET",
        "env:PATH",
        "env:POSIX",
        "env:REVISION_SCRIPT_FILENAME",
        "env:URL",
        "env:WARNING"
      ],
      "apps/api/requirements.txt": [
        "runtime:postgres",
        "runtime:redis"
      ],
      "apps/dashboard/.env.example": [
        "env:API_URL",
        "env:NEXT_PUBLIC_API_URL",
        "env:NEXT_PUBLIC_POSTHOG_HOST",
        "env:NEXT_PUBLIC_POSTHOG_KEY",
        "env:NEXT_PUBLIC_WORKOS_REDIRECT_URI",
        "env:WORKOS_API_KEY",
        "env:WORKOS_CLIENT_ID",
        "env:WORKOS_COOKIE_PASSWORD",
        "env:WORKOS_REDIRECT_URI"
      ],
      "apps/dashboard/.next/next-server.js.nft.json": [
        "env:LICENSE",
        "runtime:docker",
        "runtime:s3"
      ],
      "apps/dashboard/.next/prerender-manifest.json": [
        "runtime:kubernetes"
      ],
      "apps/dashboard/.next/required-server-files.json": [
        "env:BUILD_ID",
        "runtime:kubernetes",
        "runtime:slack"
      ],
      "apps/dashboard/.next/server/middleware-manifest.json": [
        "env:NEXT_SERVER_ACTIONS_ENCRYPTION_KEY"
      ],
      "apps/dashboard/.next/server/server-reference-manifest.json": [
        "env:RSC_SERVER_ACTION_0"
      ],
      "apps/dashboard/.next/standalone/apps/dashboard/.next/prerender-manifest.json": [
        "runtime:kubernetes"
      ],
      "apps/dashboard/.next/standalone/apps/dashboard/.next/required-server-files.json": [
        "env:BUILD_ID",
        "runtime:kubernetes",
        "runtime:slack"
      ],
      "apps/dashboard/.next/standalone/apps/dashboard/.next/server/middleware-manifest.json": [
        "env:NEXT_SERVER_ACTIONS_ENCRYPTION_KEY"
      ],
      "apps/dashboard/.next/standalone/apps/dashboard/.next/server/server-reference-manifest.json": [
        "env:RSC_SERVER_ACTION_0"
      ],
      "apps/dashboard/.next/standalone/node_modules/@img/colour/package.json": [
        "env:ESM",
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/@img/sharp-darwin-arm64/package.json": [
        "env:ARM"
      ],
      "apps/dashboard/.next/standalone/node_modules/@img/sharp-libvips-darwin-arm64/package.json": [
        "env:ARM",
        "env:LGPL"
      ],
      "apps/dashboard/.next/standalone/node_modules/@next/env/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/@opentelemetry/api/package.json": [
        "env:API",
        "env:LICENSE",
        "env:README"
      ],
      "apps/dashboard/.next/standalone/node_modules/client-only/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/detect-libc/package.json": [
        "env:CHANGELOG"
      ],
      "apps/dashboard/.next/standalone/node_modules/nanoid/package.json": [
        "env:MIT",
        "env:URL"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/@edge-runtime/cookies/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/@edge-runtime/ponyfill/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/@edge-runtime/primitives/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/@hapi/accept/package.json": [
        "env:BSD"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/@mswjs/interceptors/ClientRequest/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/@napi-rs/triples/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/@next/font/dist/google/font-data.json": [
        "env:ACT",
        "env:ARRR",
        "env:B612",
        "env:BIZ",
        "env:BLED",
        "env:BNCE",
        "env:CASL",
        "env:CRSV",
        "env:EAN13",
        "env:EDPT",
        "env:EHLT",
        "env:ELGR",
        "env:ELSH",
        "env:ELXP",
        "env:FLAR",
        "env:GFS",
        "env:GRAD",
        "env:HEXP",
        "env:IBM",
        "env:INFM",
        "env:K2D",
        "env:LXGW",
        "env:MONO",
        "env:MORF",
        "env:NSW",
        "env:NTR",
        "env:PLUS",
        "env:QLD",
        "env:REM",
        "env:ROND",
        "env:SAS",
        "env:SCAN",
        "env:SHLN",
        "env:SHRP",
        "env:SIL",
        "env:SOFT",
        "env:SPAC",
        "env:STIX",
        "env:SUSE",
        "env:TAS",
        "env:VIC",
        "env:VLG",
        "env:VOLM",
        "env:VT323",
        "env:WAL",
        "env:WDXL",
        "env:WONK",
        "env:XELA",
        "env:XOPQ",
        "env:XROT",
        "env:XTRA",
        "env:YEAR",
        "env:YELA",
        "env:YOPQ",
        "env:YROT",
        "env:YTAS",
        "env:YTDE",
        "env:YTFI",
        "env:YTLC",
        "env:YTUC",
        "env:ZCOOL",
        "runtime:kubernetes",
        "runtime:slack"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/@next/font/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/@vercel/nft/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/acorn/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/amphtml-validator/package.json": [
        "env:AMP",
        "env:HTML"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/assert/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/async-retry/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/async-sema/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/babel/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/babel-code-frame/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/browserify-zlib/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/browserslist/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/buffer/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/bytes/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/ci-info/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/commander/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/comment-json/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/compression/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/conf/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/constants-browserify/constants.json": [
        "env:DH_CHECK_P_NOT_PRIME",
        "env:DH_CHECK_P_NOT_SAFE_PRIME",
        "env:DH_NOT_SUITABLE_GENERATOR",
        "env:DH_UNABLE_TO_CHECK_GENERATOR",
        "env:E2BIG",
        "env:EACCES",
        "env:EADDRINUSE",
        "env:EADDRNOTAVAIL",
        "env:EAFNOSUPPORT",
        "env:EAGAIN",
        "env:EALREADY",
        "env:EBADF",
        "env:EBADMSG",
        "env:EBUSY",
        "env:ECANCELED",
        "env:ECHILD",
        "env:ECONNABORTED",
        "env:ECONNREFUSED",
        "env:ECONNRESET",
        "env:EDEADLK",
        "env:EDESTADDRREQ",
        "env:EDOM",
        "env:EDQUOT",
        "env:EEXIST",
        "env:EFAULT",
        "env:EFBIG",
        "env:EHOSTUNREACH",
        "env:EIDRM",
        "env:EILSEQ",
        "env:EINPROGRESS",
        "env:EINTR",
        "env:EINVAL",
        "env:EIO",
        "env:EISCONN",
        "env:EISDIR",
        "env:ELOOP",
        "env:EMFILE",
        "env:EMLINK",
        "env:EMSGSIZE",
        "env:EMULTIHOP",
        "env:ENAMETOOLONG",
        "env:ENETDOWN",
        "env:ENETRESET",
        "env:ENETUNREACH",
        "env:ENFILE",
        "env:ENGINE_METHOD_ALL",
        "env:ENGINE_METHOD_CIPHERS",
        "env:ENGINE_METHOD_DH",
        "env:ENGINE_METHOD_DIGESTS",
        "env:ENGINE_METHOD_DSA",
        "env:ENGINE_METHOD_ECDH",
        "env:ENGINE_METHOD_ECDSA",
        "env:ENGINE_METHOD_NONE",
        "env:ENGINE_METHOD_PKEY_ASN1_METHS",
        "env:ENGINE_METHOD_PKEY_METHS",
        "env:ENGINE_METHOD_RAND",
        "env:ENGINE_METHOD_STORE",
        "env:ENOBUFS",
        "env:ENODATA",
        "env:ENODEV",
        "env:ENOENT",
        "env:ENOEXEC",
        "env:ENOLCK",
        "env:ENOLINK",
        "env:ENOMEM",
        "env:ENOMSG",
        "env:ENOPROTOOPT",
        "env:ENOSPC",
        "env:ENOSR",
        "env:ENOSTR",
        "env:ENOSYS",
        "env:ENOTCONN",
        "env:ENOTDIR",
        "env:ENOTEMPTY",
        "env:ENOTSOCK",
        "env:ENOTSUP",
        "env:ENOTTY",
        "env:ENXIO",
        "env:EOPNOTSUPP",
        "env:EOVERFLOW",
        "env:EPERM",
        "env:EPIPE",
        "env:EPROTO",
        "env:EPROTONOSUPPORT",
        "env:EPROTOTYPE",
        "env:ERANGE",
        "env:EROFS",
        "env:ESPIPE",
        "env:ESRCH",
        "env:ESTALE",
        "env:ETIME",
        "env:ETIMEDOUT",
        "env:ETXTBSY",
        "env:EWOULDBLOCK",
        "env:EXDEV",
        "env:F_OK",
        "env:NPN_ENABLED",
        "env:O_APPEND",
        "env:O_CREAT",
        "env:O_DIRECTORY",
        "env:O_EXCL",
        "env:O_NOCTTY",
        "env:O_NOFOLLOW",
        "env:O_NONBLOCK",
        "env:O_RDONLY",
        "env:O_RDWR",
        "env:O_SYMLINK",
        "env:O_SYNC",
        "env:O_TRUNC",
        "env:O_WRONLY",
        "env:POINT_CONVERSION_COMPRESSED",
        "env:POINT_CONVERSION_HYBRID",
        "env:POINT_CONVERSION_UNCOMPRESSED",
        "env:RSA_NO_PADDING",
        "env:RSA_PKCS1_OAEP_PADDING",
        "env:RSA_PKCS1_PADDING",
        "env:RSA_PKCS1_PSS_PADDING",
        "env:RSA_SSLV23_PADDING",
        "env:RSA_X931_PADDING",
        "env:R_OK",
        "env:SIGABRT",
        "env:SIGALRM",
        "env:SIGBUS",
        "env:SIGCHLD",
        "env:SIGCONT",
        "env:SIGFPE",
        "env:SIGHUP",
        "env:SIGILL",
        "env:SIGINT",
        "env:SIGIO",
        "env:SIGIOT",
        "env:SIGKILL",
        "env:SIGPIPE",
        "env:SIGPROF",
        "env:SIGQUIT",
        "env:SIGSEGV",
        "env:SIGSTOP",
        "env:SIGSYS",
        "env:SIGTERM",
        "env:SIGTRAP",
        "env:SIGTSTP",
        "env:SIGTTIN",
        "env:SIGTTOU",
        "env:SIGURG",
        "env:SIGUSR1",
        "env:SIGUSR2",
        "env:SIGVTALRM",
        "env:SIGWINCH",
        "env:SIGXCPU",
        "env:SIGXFSZ",
        "env:SSL_OP_ALL",
        "env:SSL_OP_ALLOW_UNSAFE_LEGACY_RENEGOTIATION",
        "env:SSL_OP_CIPHER_SERVER_PREFERENCE",
        "env:SSL_OP_CISCO_ANYCONNECT",
        "env:SSL_OP_COOKIE_EXCHANGE",
        "env:SSL_OP_CRYPTOPRO_TLSEXT_BUG",
        "env:SSL_OP_DONT_INSERT_EMPTY_FRAGMENTS",
        "env:SSL_OP_EPHEMERAL_RSA",
        "env:SSL_OP_LEGACY_SERVER_CONNECT",
        "env:SSL_OP_MICROSOFT_BIG_SSLV3_BUFFER",
        "env:SSL_OP_MICROSOFT_SESS_ID_BUG",
        "env:SSL_OP_MSIE_SSLV2_RSA_PADDING",
        "env:SSL_OP_NETSCAPE_CA_DN_BUG",
        "env:SSL_OP_NETSCAPE_CHALLENGE_BUG",
        "env:SSL_OP_NETSCAPE_DEMO_CIPHER_CHANGE_BUG",
        "env:SSL_OP_NETSCAPE_REUSE_CIPHER_CHANGE_BUG",
        "env:SSL_OP_NO_COMPRESSION",
        "env:SSL_OP_NO_QUERY_MTU",
        "env:SSL_OP_NO_SESSION_RESUMPTION_ON_RENEGOTIATION",
        "env:SSL_OP_NO_TICKET",
        "env:SSL_OP_PKCS1_CHECK_1",
        "env:SSL_OP_PKCS1_CHECK_2",
        "env:SSL_OP_SINGLE_DH_USE",
        "env:SSL_OP_SINGLE_ECDH_USE",
        "env:SSL_OP_SSLEAY_080_CLIENT_DH_BUG",
        "env:SSL_OP_SSLREF2_REUSE_CERT_TYPE_BUG",
        "env:SSL_OP_TLS_BLOCK_PADDING_BUG",
        "env:SSL_OP_TLS_D5_BUG",
        "env:SSL_OP_TLS_ROLLBACK_BUG",
        "env:S_IFBLK",
        "env:S_IFCHR",
        "env:S_IFDIR",
        "env:S_IFIFO",
        "env:S_IFLNK",
        "env:S_IFMT",
        "env:S_IFREG",
        "env:S_IFSOCK",
        "env:S_IRGRP",
        "env:S_IROTH",
        "env:S_IRUSR",
        "env:S_IRWXG",
        "env:S_IRWXO",
        "env:S_IRWXU",
        "env:S_IWGRP",
        "env:S_IWOTH",
        "env:S_IWUSR",
        "env:S_IXGRP",
        "env:S_IXOTH",
        "env:S_IXUSR",
        "env:UV_UDP_REUSEADDR",
        "env:W_OK",
        "env:X_OK"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/content-disposition/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/cookie/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/cross-spawn/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/crypto-browserify/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/data-uri-to-buffer/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/debug/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/devalue/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/domain-browser/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/edge-runtime/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/events/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/find-up/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/fresh/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/glob/package.json": [
        "env:ISC"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/gzip-size/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/http-proxy/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/http-proxy-agent/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/https-browserify/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/https-proxy-agent/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/icss-utils/package.json": [
        "env:ISC"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/image-size/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/is-animated/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/is-docker/package.json": [
        "env:MIT",
        "runtime:docker"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/is-wsl/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/jest-worker/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/json5/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/jsonwebtoken/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/loader-utils2/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/loader-utils3/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/lodash.curry/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/lru-cache/package.json": [
        "env:ISC"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/mini-css-extract-plugin/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/nanoid/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/neo-async/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/os-browserify/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/p-limit/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/p-queue/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/path-browserify/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/path-to-regexp/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/picomatch/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/postcss-flexbugs-fixes/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/postcss-modules-extract-imports/package.json": [
        "env:ISC"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/postcss-modules-local-by-default/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/postcss-modules-scope/package.json": [
        "env:ISC"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/postcss-modules-values/package.json": [
        "env:ISC"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/postcss-preset-env/package.json": [
        "env:CC0"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/postcss-scss/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/postcss-value-parser/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/process/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/punycode/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/querystring-es3/package.json": [
        "runtime:s3"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/react-is/package.json": [
        "env:LICENSE",
        "env:MIT",
        "env:README"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/react-refresh/package.json": [
        "env:LICENSE",
        "env:MIT",
        "env:README"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/regenerator-runtime/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/safe-stable-stringify/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/sass-loader/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/schema-utils3/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/semver/package.json": [
        "env:ISC"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/send/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/setimmediate/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/shell-quote/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/source-map/package.json": [
        "env:BSD"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/source-map08/package.json": [
        "env:BSD"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/stacktrace-parser/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/stream-browserify/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/stream-http/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/string-hash/package.json": [
        "env:CC0"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/string_decoder/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/strip-ansi/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/superstruct/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/tar/package.json": [
        "env:ISC"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/text-table/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/timers-browserify/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/tty-browserify/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/unistore/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/util/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/vm-browserify/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/watchpack/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/webpack-sources3/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/ws/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/zod/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/compiled/zod-validation-error/package.json": [
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/lib/server-external-packages.json": [
        "runtime:s3"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/dist/server/capsize-font-metrics.json": [
        "env:ACT",
        "env:B612",
        "env:BIZ",
        "env:EAN13",
        "env:FELL",
        "env:GFS",
        "env:IBM",
        "env:K2D",
        "env:LXGW",
        "env:MPLUS1",
        "env:MPLUS2",
        "env:NSW",
        "env:NTR",
        "env:PLUS",
        "env:QLD",
        "env:REM",
        "env:SAS",
        "env:SFNS",
        "env:SIL",
        "env:STIX",
        "env:SUSE",
        "env:TAS",
        "env:VIC",
        "env:VLG",
        "env:VT323",
        "env:WAL",
        "env:ZCOOL",
        "runtime:kubernetes",
        "runtime:s3",
        "runtime:slack"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/node_modules/postcss/package.json": [
        "env:MIT",
        "runtime:docker"
      ],
      "apps/dashboard/.next/standalone/node_modules/next/package.json": [
        "env:BROWSER",
        "env:MIT",
        "env:NEXT_SERVER_NO_MANGLE",
        "runtime:docker",
        "runtime:s3"
      ],
      "apps/dashboard/.next/standalone/node_modules/picocolors/package.json": [
        "env:ANSI",
        "env:ISC"
      ],
      "apps/dashboard/.next/standalone/node_modules/react/package.json": [
        "env:LICENSE",
        "env:MIT",
        "env:README"
      ],
      "apps/dashboard/.next/standalone/node_modules/react-dom/package.json": [
        "env:DOM",
        "env:LICENSE",
        "env:MIT",
        "env:README"
      ],
      "apps/dashboard/.next/standalone/node_modules/sharp/node_modules/semver/package.json": [
        "env:ISC"
      ],
      "apps/dashboard/.next/standalone/node_modules/sharp/package.json": [
        "env:AVIF",
        "env:GIF",
        "env:JPEG",
        "env:PNG",
        "env:TIFF",
        "runtime:s3"
      ],
      "apps/dashboard/.next/standalone/node_modules/source-map-js/package.json": [
        "env:BSD",
        "env:CONTRIBUTING",
        "env:README"
      ],
      "apps/dashboard/.next/standalone/node_modules/styled-jsx/package.json": [
        "env:CSS",
        "env:JSX",
        "env:MIT"
      ],
      "apps/dashboard/.next/standalone/node_modules/typescript/package.json": [
        "env:LICENSE",
        "env:README",
        "env:SECURITY"
      ],
      "apps/dashboard/Dockerfile": [
        "env:CMD",
        "env:COPY",
        "env:ENV",
        "env:EXPOSE",
        "env:FROM",
        "env:NODE_ENV",
        "env:RUN",
        "env:WORKDIR"
      ],
      "apps/web/.next/next-server.js.nft.json": [
        "env:LICENSE"
      ],
      "apps/web/.next/prerender-manifest.json": [
        "runtime:kubernetes"
      ],
      "apps/web/.next/required-server-files.json": [
        "env:BUILD_ID",
        "runtime:kubernetes",
        "runtime:slack"
      ],
      "apps/web/.vercel/output/builds.json": [
        "env:API"
      ],
      "apps/web/.vercel/output/functions/_not-found.rsc.func/.vc-config.json": [
        "env:BUILD_ID",
        "env:ISR"
      ],
      "apps/worker/Dockerfile": [
        "env:CMD",
        "env:COPY",
        "env:FROM",
        "env:RUN",
        "env:WORKDIR"
      ],
      "apps/worker/requirements.txt": [
        "runtime:redis"
      ],
      "docs/examples/librechat-skill-tree/skilgen.yml": [
        "env:ANTHROPIC_API_KEY",
        "env:AZURE_OPENAI_API_KEY",
        "env:GOOGLE_API_KEY",
        "env:HUGGINGFACEHUB_API_TOKEN",
        "env:IAM",
        "env:MODEL_API_KEY",
        "env:OPENAI_API_KEY"
      ],
      "examples/github-actions/skilgen-sync.yml": [
        "env:AGENTS",
        "env:ANALYSIS",
        "env:ANTHROPIC_API_KEY",
        "env:ARCHITECTURE",
        "env:FEATURES",
        "env:FORCE_JAVASCRIPT_ACTIONS_TO_NODE24",
        "env:HUGGINGFACEHUB_API_TOKEN",
        "env:JSON",
        "env:OPENAI_API_KEY",
        "env:README",
        "env:REPORT",
        "env:SKILGEN_SCORE_THRESHOLD",
        "env:TRACEABILITY"
      ],
      "infra/docker/docker-compose.prod.yml": [
        "env:CMD",
        "env:DEPLOYMENT_MODE",
        "env:POSTGRES_DB",
        "env:POSTGRES_PASSWORD",
        "env:POSTGRES_USER",
        "env:SHELL",
        "runtime:docker",
        "runtime:postgres",
        "runtime:redis"
      ],
      "infra/docker/docker-compose.yml": [
        "env:CMD",
        "env:DATABASE_URL",
        "env:DEPLOYMENT_MODE",
        "env:KEYCLOAK_ADMIN",
        "env:KEYCLOAK_ADMIN_PASSWORD",
        "env:KEYCLOAK_PASSWORD",
        "env:NEXT_PUBLIC_API_URL",
        "env:POSTGRES_DB",
        "env:POSTGRES_PASSWORD",
        "env:POSTGRES_USER",
        "env:REDIS_URL",
        "env:SHELL",
        "runtime:docker",
        "runtime:postgres",
        "runtime:redis"
      ],
      "infra/helm/skillayer/templates/configmap.yaml": [
        "env:DEPLOYMENT_MODE",
        "env:GITHUB_APP_ID"
      ],
      "infra/helm/skillayer/templates/deployment-api.yaml": [
        "runtime:docker"
      ],
      "infra/helm/skillayer/templates/deployment-dashboard.yaml": [
        "runtime:docker"
      ],
      "infra/helm/skillayer/templates/deployment-worker.yaml": [
        "runtime:docker"
      ],
      "infra/helm/skillayer/templates/secret.yaml": [
        "env:WORKOS_API_KEY"
      ],
      "infra/helm/skillayer/values.yaml": [
        "runtime:postgres",
        "runtime:redis"
      ],
      "node_modules/.package-lock.json": [
        "env:B4RT",
        "env:BSD",
        "env:CC0",
        "env:G3ZA",
        "env:G5KYP6",
        "env:IICI",
        "env:ISC",
        "env:JTF99U",
        "env:KIN",
        "env:LGPL",
        "env:LHE",
        "env:LICENSE",
        "env:LL8E",
        "env:MFQ",
        "env:MIT",
        "env:MPL",
        "env:O2XJB",
        "env:PAJLD1I",
        "env:PB7X",
        "env:PKQ",
        "env:SEE",
        "env:SU5",
        "env:T4IS",
        "env:TER",
        "env:THO",
        "env:VJH",
        "env:VOS",
        "env:WPS",
        "runtime:kubernetes",
        "runtime:s3"
      ],
      "node_modules/@alloc/quick-lru/package.json": [
        "env:LRU",
        "env:MIT"
      ],
      "node_modules/@eslint/eslintrc/node_modules/globals/globals.json": [
        "env:CSS",
        "env:DDP",
        "env:EJSON",
        "env:HTTP",
        "env:JSON",
        "env:URL",
        "env:UUID",
        "env:WSH",
        "env:YAHOO",
        "env:YUI",
        "runtime:docker",
        "runtime:kubernetes"
      ],
      "node_modules/@eslint/eslintrc/node_modules/globals/package.json": [
        "env:MIT"
      ],
      "node_modules/@eslint/eslintrc/package.json": [
        "env:LICENSE",
        "env:MIT"
      ],
      "node_modules/@eslint/js/package.json": [
        "env:LICENSE",
        "env:MIT",
        "env:README"
      ],
      "node_modules/@eslint-community/eslint-utils/node_modules/eslint-visitor-keys/package.json": [
        "env:AST"
      ],
      "node_modules/@eslint-community/eslint-utils/package.json": [
        "env:MIT"
      ],
      "node_modules/@eslint-community/regexpp/package.json": [
        "env:MIT"
      ],
      "node_modules/@floating-ui/core/package.json": [
        "env:MIT"
      ],
      "node_modules/@floating-ui/dom/package.json": [
        "env:MIT"
      ],
      "node_modules/@floating-ui/react-dom/package.json": [
        "env:DOM",
        "env:MIT"
      ],
      "node_modules/@floating-ui/utils/package.json": [
        "env:MIT"
      ],
      "node_modules/@humanfs/types/tsconfig.json": [
        "env:ES2022"
      ],
      "node_modules/@humanwhocodes/module-importer/package.json": [
        "runtime:kubernetes"
      ],
      "node_modules/@humanwhocodes/retry/package.json": [
        "runtime:kubernetes"
      ],
      "node_modules/@img/colour/package.json": [
        "env:ESM",
        "env:MIT"
      ],
      "node_modules/@img/sharp-darwin-arm64/package.json": [
        "env:ARM"
      ],
      "node_modules/@img/sharp-libvips-darwin-arm64/package.json": [
        "env:ARM",
        "env:LGPL"
      ],
      "node_modules/@jridgewell/gen-mapping/package.json": [
        "env:MIT"
      ],
      "node_modules/@jridgewell/resolve-uri/package.json": [
        "env:MIT",
        "env:URI"
      ],
      "node_modules/@jridgewell/sourcemap-codec/package.json": [
        "env:MIT"
      ],
      "node_modules/@jridgewell/trace-mapping/package.json": [
        "env:MIT"
      ],
      "node_modules/@next/env/package.json": [
        "env:MIT"
      ],
      "node_modules/@next/eslint-plugin-next/package.json": [
        "env:MIT"
      ],
      "node_modules/@next/swc-darwin-arm64/package.json": [
        "env:MIT"
      ],
      "node_modules/@nodelib/fs.scandir/package.json": [
        "env:MIT"
      ],
      "node_modules/@nodelib/fs.stat/package.json": [
        "env:MIT"
      ],
      "node_modules/@nodelib/fs.walk/package.json": [
        "env:MIT"
      ],
      "node_modules/@opentelemetry/api/package.json": [
        "env:API",
        "env:LICENSE",
        "env:README"
      ],
      "node_modules/@opentelemetry/api-logs/package.json": [
        "env:API",
        "env:LICENSE",
        "env:README"
      ],
      "node_modules/@opentelemetry/core/package.json": [
        "env:LICENSE",
        "env:README",
        "env:SDK"
      ],
      "node_modules/@opentelemetry/exporter-logs-otlp-http/package.json": [
        "env:LICENSE",
        "env:README"
      ],
      "node_modules/@opentelemetry/otlp-exporter-base/package.json": [
        "env:LICENSE",
        "env:OTLP",
        "env:README"
      ],
      "node_modules/@opentelemetry/otlp-transformer/node_modules/@opentelemetry/resources/package.json": [
        "env:LICENSE",
        "env:README",
        "env:SDK"
      ],
      "node_modules/@opentelemetry/otlp-transformer/package.json": [
        "env:LICENSE",
        "env:OTLP",
        "env:README",
        "env:SDK"
      ],
      "node_modules/@opentelemetry/resources/node_modules/@opentelemetry/core/package.json": [
        "env:LICENSE",
        "env:README",
        "env:SDK"
      ],
      "node_modules/@opentelemetry/resources/package.json": [
        "env:LICENSE",
        "env:README",
        "env:SDK"
      ],
      "node_modules/@opentelemetry/sdk-logs/node_modules/@opentelemetry/resources/package.json": [
        "env:LICENSE",
        "env:README",
        "env:SDK"
      ],
      "node_modules/@opentelemetry/sdk-logs/package.json": [
        "env:LICENSE",
        "env:README",
        "env:SDK"
      ],
      "node_modules/@opentelemetry/sdk-metrics/node_modules/@opentelemetry/resources/package.json": [
        "env:LICENSE",
        "env:README",
        "env:SDK"
      ],
      "node_modules/@opentelemetry/sdk-metrics/package.json": [
        "env:LICENSE",
        "env:README",
        "env:SDK"
      ],
      "node_modules/@opentelemetry/sdk-trace-base/node_modules/@opentelemetry/resources/package.json": [
        "env:LICENSE",
        "env:README",
        "env:SDK"
      ],
      "node_modules/@opentelemetry/sdk-trace-base/package.json": [
        "env:LICENSE",
        "env:README"
      ],
      "node_modules/@opentelemetry/semantic-conventions/package.json": [
        "env:LICENSE",
        "env:README"
      ],
      "node_modules/@posthog/core/package.json": [
        "env:MIT",
        "env:PACKAGE_DEST"
      ],
      "node_modules/@posthog/types/package.json": [
        "env:MIT",
        "env:PACKAGE_DEST",
        "env:SDK"
      ],
      "node_modules/@protobufjs/aspromise/package.json": [
        "env:BSD"
      ],
      "node_modules/@protobufjs/base64/package.json": [
        "env:BSD"
      ],
      "node_modules/@protobufjs/codegen/package.json": [
        "env:BSD"
      ],
      "node_modules/@protobufjs/eventemitter/package.json": [
        "env:BSD"
      ],
      "node_modules/@protobufjs/fetch/package.json": [
        "env:BSD"
      ],
      "node_modules/@protobufjs/float/package.json": [
        "env:BSD"
      ],
      "node_modules/@protobufjs/inquire/package.json": [
        "env:BSD"
      ],
      "node_modules/@protobufjs/path/package.json": [
        "env:BSD",
        "env:URL"
      ],
      "node_modules/@protobufjs/pool/package.json": [
        "env:BSD"
      ],
      "node_modules/@protobufjs/utf8/package.json": [
        "env:BSD",
        "env:UTF8"
      ],
      "node_modules/@radix-ui/number/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/primitive/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-arrow/node_modules/@radix-ui/react-primitive/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-arrow/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-avatar/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-collection/node_modules/@radix-ui/react-context/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-collection/node_modules/@radix-ui/react-primitive/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-collection/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-compose-refs/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-context/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-dialog/node_modules/@radix-ui/react-context/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-dialog/node_modules/@radix-ui/react-primitive/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-dialog/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-direction/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-dismissable-layer/node_modules/@radix-ui/react-primitive/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-dismissable-layer/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-dropdown-menu/node_modules/@radix-ui/react-context/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-dropdown-menu/node_modules/@radix-ui/react-primitive/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-dropdown-menu/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-focus-guards/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-focus-scope/node_modules/@radix-ui/react-primitive/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-focus-scope/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-id/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-label/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-menu/node_modules/@radix-ui/react-context/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-menu/node_modules/@radix-ui/react-primitive/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-menu/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-popover/node_modules/@radix-ui/react-context/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-popover/node_modules/@radix-ui/react-primitive/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-popover/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-popper/node_modules/@radix-ui/react-context/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-popper/node_modules/@radix-ui/react-primitive/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-popper/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-portal/node_modules/@radix-ui/react-primitive/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-portal/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-presence/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-primitive/node_modules/@radix-ui/react-slot/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-primitive/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-progress/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-roving-focus/node_modules/@radix-ui/react-context/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-roving-focus/node_modules/@radix-ui/react-primitive/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-roving-focus/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-select/node_modules/@radix-ui/react-context/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-select/node_modules/@radix-ui/react-primitive/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-select/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-separator/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-slot/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-switch/node_modules/@radix-ui/react-context/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-switch/node_modules/@radix-ui/react-primitive/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-switch/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-tabs/node_modules/@radix-ui/react-context/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-tabs/node_modules/@radix-ui/react-primitive/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-tabs/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-tooltip/node_modules/@radix-ui/react-context/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-tooltip/node_modules/@radix-ui/react-primitive/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-tooltip/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-use-callback-ref/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-use-controllable-state/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-use-effect-event/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-use-escape-keydown/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-use-is-hydrated/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-use-layout-effect/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-use-previous/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-use-rect/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-use-size/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-visually-hidden/node_modules/@radix-ui/react-primitive/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/react-visually-hidden/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@radix-ui/rect/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/@turbo/darwin-arm64/package.json": [
        "env:MIT"
      ],
      "node_modules/@types/estree/package.json": [
        "env:MIT"
      ],
      "node_modules/@types/json-schema/package.json": [
        "env:MIT"
      ],
      "node_modules/@types/node/package.json": [
        "env:MIT"
      ],
      "node_modules/@types/react/package.json": [
        "env:MIT"
      ],
      "node_modules/@types/react-dom/package.json": [
        "env:MIT"
      ],
      "node_modules/@types/trusted-types/package.json": [
        "env:MIT"
      ],
      "node_modules/@typescript-eslint/eslint-plugin/node_modules/ignore/package.json": [
        "env:ES6",
        "env:IGNORE_ONLY_IGNORES",
        "env:IGNORE_TEST_WIN32",
        "env:LICENSE",
        "env:MIT"
      ],
      "node_modules/@typescript-eslint/eslint-plugin/package.json": [
        "env:LICENSE",
        "env:MIT",
        "env:README"
      ],
      "node_modules/@typescript-eslint/parser/package.json": [
        "env:LICENSE",
        "env:MIT",
        "env:README"
      ],
      "node_modules/@typescript-eslint/project-service/package.json": [
        "env:LICENSE",
        "env:MIT",
        "env:README"
      ],
      "node_modules/@typescript-eslint/scope-manager/package.json": [
        "env:LICENSE",
        "env:MIT",
        "env:README"
      ],
      "node_modules/@typescript-eslint/tsconfig-utils/package.json": [
        "env:LICENSE",
        "env:MIT",
        "env:README"
      ],
      "node_modules/@typescript-eslint/type-utils/package.json": [
        "env:LICENSE",
        "env:MIT",
        "env:README"
      ],
      "node_modules/@typescript-eslint/types/package.json": [
        "env:AST",
        "env:LICENSE",
        "env:MIT",
        "env:README"
      ],
      "node_modules/@typescript-eslint/typescript-estree/node_modules/balanced-match/package.json": [
        "env:MIT"
      ],
      "node_modules/@typescript-eslint/typescript-estree/node_modules/brace-expansion/package.json": [
        "env:MIT"
      ],
      "node_modules/@typescript-eslint/typescript-estree/node_modules/semver/package.json": [
        "env:ISC"
      ],
      "node_modules/@typescript-eslint/typescript-estree/package.json": [
        "env:LICENSE",
        "env:MIT",
        "env:README"
      ],
      "node_modules/@typescript-eslint/utils/package.json": [
        "env:LICENSE",
        "env:MIT",
        "env:README"
      ],
      "node_modules/@typescript-eslint/visitor-keys/node_modules/eslint-visitor-keys/package.json": [
        "env:AST",
        "env:README"
      ],
      "node_modules/@typescript-eslint/visitor-keys/package.json": [
        "env:AST",
        "env:LICENSE",
        "env:MIT",
        "env:README"
      ],
      "node_modules/@workos-inc/authkit-nextjs/package.json": [
        "env:LICENSE",
        "env:MIT",
        "env:README"
      ],
      "node_modules/@workos-inc/node/package.json": [
        "env:API",
        "env:MIT"
      ],
      "node_modules/acorn/package.json": [
        "env:MIT"
      ],
      "node_modules/acorn-jsx/package.json": [
        "env:JSX",
        "env:MIT"
      ],
      "node_modules/ajv/lib/refs/data.json": [
        "env:JSON"
      ],
      "node_modules/ajv/lib/refs/json-schema-secure.json": [
        "env:JSON"
      ],
      "node_modules/ajv/package.json": [
        "env:AJV_FAST_TEST",
        "env:ES5",
        "env:JSON",
        "env:LICENSE",
        "env:MIT"
      ],
      "node_modules/ansi-styles/package.json": [
        "env:ANSI",
        "env:MIT"
      ],
      "node_modules/any-promise/package.json": [
        "env:ES6",
        "env:MIT"
      ],
      "node_modules/anymatch/package.json": [
        "env:ISC"
      ],
      "node_modules/arg/package.json": [
        "env:CLI",
        "env:MIT",
        "env:WARN_EXIT"
      ],
      "node_modules/argparse/package.json": [
        "env:CLI"
      ],
      "node_modules/aria-hidden/package.json": [
        "env:CHANGELOG",
        "env:DOM",
        "env:MIT"
      ],
      "node_modules/aria-query/package.json": [
        "env:ARIA",
        "env:BABEL_ENV"
      ],
      "node_modules/array-buffer-byte-length/package.json": [
        "env:API",
        "env:CHANGELOG",
        "env:MIT",
        "env:README"
      ],
      "node_modules/array-buffer-byte-length/tsconfig.json": [
        "env:ES2021"
      ],
      "node_modules/array-includes/package.json": [
        "env:API",
        "env:CHANGELOG",
        "env:ES2016",
        "env:ES3",
        "env:ES7",
        "env:MIT",
        "env:README",
        "runtime:s3"
      ],
      "node_modules/array.prototype.findlast/package.json": [
        "env:API",
        "env:CHANGELOG",
        "env:ES3",
        "env:MIT",
        "env:README",
        "runtime:s3"
      ],
      "node_modules/array.prototype.flat/package.json": [
        "env:API",
        "env:CHANGELOG",
        "env:ES2019",
        "env:ES3",
        "env:MIT",
        "env:README",
        "runtime:s3"
      ],
      "node_modules/array.prototype.flatmap/package.json": [
        "env:API",
        "env:CHANGELOG",
        "env:ES2019",
        "env:ES3",
        "env:MIT",
        "env:README",
        "runtime:s3"
      ],
      "node_modules/array.prototype.tosorted/package.json": [
        "env:API",
        "env:CHANGELOG",
        "env:ES3",
        "env:MIT",
        "env:README",
        "runtime:s3"
      ],
      "node_modules/arraybuffer.prototype.slice/package.json": [
        "env:API",
        "env:CHANGELOG",
        "env:MIT",
        "env:README"
      ],
      "node_modules/ast-types-flow/package.json": [
        "env:AST",
        "env:MIT"
      ],
      "node_modules/async-function/package.json": [
        "env:CHANGELOG",
        "env:MIT",
        "env:README"
      ],
      "node_modules/autoprefixer/package.json": [
        "env:CSS",
        "env:MIT"
      ],
      "node_modules/available-typed-arrays/package.json": [
        "env:CHANGELOG",
        "env:MIT",
        "env:README"
      ],
      "node_modules/axe-core/locales/_template.json": [
        "env:AAA",
        "env:ARIA",
        "env:CSS",
        "env:DOM",
        "env:HTML",
        "env:URL",
        "env:WCAG"
      ],
      "node_modules/axe-core/locales/da.json": [
        "env:ARIA",
        "env:CSS",
        "env:DOM",
        "runtime:kubernetes"
      ],
      "node_modules/axe-core/locales/de.json": [
        "env:AAA",
        "env:ARIA",
        "env:CSS",
        "env:DOM",
        "env:HTML",
        "env:HTML5",
        "env:WCAG"
      ],
      "node_modules/axe-core/locales/el.json": [
        "env:AAA",
        "env:ARIA",
        "env:CSS",
        "env:DOM",
        "env:HTML",
        "env:URL",
        "env:WCAG"
      ],
      "node_modules/axe-core/locales/es.json": [
        "env:AAA",
        "env:ARIA",
        "env:CSS",
        "env:DOM",
        "env:HTML",
        "env:WCAG"
      ],
      "node_modules/axe-core/locales/eu.json": [
        "env:AAA",
        "env:AREAN",
        "env:ARIA",
        "env:CSS",
        "env:HTML",
        "env:WCAG",
        "runtime:kubernetes"
      ],
      "node_modules/axe-core/locales/fr.json": [
        "env:AAA",
        "env:ARIA",
        "env:CSS",
        "env:DOM",
        "env:HTML",
        "env:URL",
        "env:WCAG"
      ],
      "node_modules/axe-core/locales/he.json": [
        "env:AAA",
        "env:ARIA",
        "env:CSS",
        "env:DOM",
        "env:HTML",
        "env:HTML5",
        "env:URL",
        "env:WCAG"
      ],
      "node_modules/axe-core/locales/it.json": [
        "env:AAA",
        "env:ARIA",
        "env:CSS",
        "env:DOM",
        "env:HTML",
        "env:URL",
        "env:WCAG"
      ],
      "node_modules/axe-core/locales/ja.json": [
        "env:ARIA"
      ],
      "node_modules/axe-core/locales/ko.json": [
        "env:AAA",
        "env:ARIA",
        "env:CSS",
        "env:HTML",
        "env:WCAG"
      ],
      "node_modules/axe-core/locales/nl.json": [
        "env:ARIA",
        "runtime:kubernetes"
      ],
      "node_modules/axe-core/locales/no_NB.json": [
        "env:ARIA",
        "env:CSS",
        "env:DOM",
        "runtime:kubernetes"
      ],
      "node_modules/axe-core/locales/pl.json": [
        "env:AAA",
        "env:ARIA",
        "env:AXE",
        "env:CSS",
        "env:DOM",
        "env:HTML",
        "env:URL",
        "env:WCAG",
        "runtime:kubernetes"
      ],
      "node_modules/axe-core/locales/pt_BR.json": [
        "env:AAA",
        "env:ARIA",
        "env:CSS",
        "env:DOM",
        "env:HTML",
        "env:URL",
        "env:WCAG"
      ],
      "node_modules/axe-core/locales/pt_PT.json": [
        "env:AAA",
        "env:ARIA",
        "env:CSS",
        "env:DOM",
        "env:HTML",
        "env:URL",
        "env:WCAG"
      ],
      "node_modules/axe-core/locales/ru.json": [
        "env:AAA",
        "env:ARIA",
        "env:CSS",
        "env:DOM",
        "env:HTML",
        "env:URL",
        "env:WCAG"
      ],
      "node_modules/axe-core/locales/zh_CN.json": [
        "env:AAA",
        "env:ARIA",
        "env:CSS",
        "env:DOM",
        "env:HTML",
        "env:URL",
        "env:WCAG"
      ],
      "node_modules/axe-core/locales/zh_TW.json": [
        "env:AAA",
        "env:ARIA",
        "env:CSS",
        "env:DOM",
        "env:HTML",
        "env:URL",
        "env:WCAG"
      ],
      "node_modules/axe-core/package.json": [
        "env:LICENSE",
        "env:MPL",
        "env:PARTY",
        "runtime:s3"
      ],
      "node_modules/axe-core/sri-history.json": [
        "env:DKR4SE",
        "env:GY6QNA",
        "env:WSHVQ1",
        "env:WUH",
        "runtime:s3"
      ],
      "node_modules/axobject-query/package.json": [
        "env:BABEL_ENV"
      ],
      "node_modules/balanced-match/package.json": [
        "env:MIT"
      ],
      "node_modules/baseline-browser-mapping/package.json": [
        "env:FALSE",
        "env:LICENSE",
        "env:README",
        "env:TRUE"
      ],
      "node_modules/binary-extensions/binary-extensions.json": [
        "runtime:s3"
      ],
      "node_modules/binary-extensions/package.json": [
        "env:MIT"
      ],
      "node_modules/brace-expansion/package.json": [
        "env:MIT"
      ],
      "node_modules/braces/package.json": [
        "env:MIT"
      ],
      "node_modules/browserslist/package.json": [
        "env:MIT"
      ],
      "node_modules/call-bind/package.json": [
        "env:CHANGELOG",
        "env:MIT",
        "env:README"
      ],
      "node_modules/call-bind-apply-helpers/package.json": [
        "env:CHANGELOG",
        "env:MIT",
        "env:README"
      ],
      "node_modules/call-bound/package.json": [
        "env:CHANGELOG",
        "env:MIT",
        "env:README"
      ],
      "node_modules/callsites/package.json": [
        "env:API",
        "env:MIT"
      ],
      "node_modules/camelcase-css/package.json": [
        "env:CSS",
        "env:DOM",
        "env:MIT",
        "runtime:kubernetes"
      ],
      "node_modules/chalk/package.json": [
        "env:MIT"
      ],
      "node_modules/chokidar/node_modules/glob-parent/package.json": [
        "env:ISC",
        "env:LICENSE"
      ],
      "node_modules/chokidar/package.json": [
        "env:MIT"
      ],
      "node_modules/client-only/package.json": [
        "env:MIT"
      ],
      "node_modules/clsx/package.json": [
        "env:MIT"
      ],
      "node_modules/cmdk/package.json": [
        "env:MIT"
      ],
      "node_modules/color-convert/package.json": [
        "env:MIT"
      ],
      "node_modules/color-name/package.json": [
        "env:MIT"
      ],
      "node_modules/commander/package.json": [
        "env:MIT"
      ],
      "node_modules/concat-map/package.json": [
        "env:MIT"
      ],
      "node_modules/cookie/package.json": [
        "env:HISTORY",
        "env:HTTP",
        "env:LICENSE",
        "env:MIT",
        "env:README",
        "env:SECURITY",
        "runtime:kubernetes"
      ],
      "node_modules/core-js/package.json": [
        "env:ES2015",
        "env:ES2016",
        "env:ES2017",
        "env:ES2018",
        "env:ES2019",
        "env:ES2020",
        "env:ES2021",
        "env:ES2022",
        "env:ES2023",
        "env:ES2024",
        "env:ES2025",
        "env:ES2026",
        "env:ES3",
        "env:ES5",
        "env:ES6",
        "env:ES7",
        "env:MIT",
        "env:URL",
        "runtime:kubernetes",
        "runtime:s3"
      ],
      "node_modules/cross-spawn/package.json": [
        "env:HEAD",
        "env:HUSKY_GIT_PARAMS",
        "env:MIT"
      ],
      "node_modules/cssesc/package.json": [
        "env:ASCII",
        "env:CSS",
        "env:LICENSE",
        "env:MIT"
      ],
      "node_modules/csstype/package.json": [
        "env:MDN",
        "env:MIT"
      ],
      "node_modules/damerau-levenshtein/package.json": [
        "env:BSD"
      ],
      "node_modules/data-view-buffer/.github/FUNDING.yml": [
        "env:URL"
      ],
      "node_modules/data-view-buffer/package.json": [
        "env:CHANGELOG",
        "env:MIT",
        "env:README"
      ],
      "node_modules/data-view-byte-length/.github/FUNDING.yml": [
        "env:URL"
      ],
      "node_modules/data-view-byte-length/package.json": [
        "env:CHANGELOG",
        "env:MIT",
        "env:README"
      ],
      "node_modules/data-view-byte-offset/.github/FUNDING.yml": [
        "env:URL"
      ],
      "node_modules/data-view-byte-offset/package.json": [
        "env:CHANGELOG",
        "env:MIT",
        "env:README"
      ],
      "node_modules/debug/package.json": [
        "env:LICENSE",
        "env:MIT",
        "env:README"
      ],
      "node_modules/deep-is/package.json": [
        "env:MIT"
      ],
      "node_modules/define-data-property/package.json": [
        "env:CHANGELOG",
        "env:MIT",
        "env:README"
      ],
      "node_modules/define-properties/package.json": [
        "env:CHANGELOG",
        "env:ES5",
        "env:MIT"
      ],
      "node_modules/detect-libc/package.json": [
        "env:CHANGELOG"
      ],
      "node_modules/detect-node-es/package.json": [
        "env:ESM",
        "env:MIT"
      ],
      "node_modules/dlv/package.json": [
        "env:MIT"
      ],
      "node_modules/dompurify/package.json": [
        "env:BABEL_ENV",
        "env:DOM",
        "env:HTML",
        "env:MPL",
        "env:NODE_ENV",
        "env:SVG",
        "env:VERSION",
        "env:XSS"
      ],
      "node_modules/dunder-proto/package.json": [
        "env:CHANGELOG",
        "env:MIT",
        "env:README"
      ],
      "node_modules/dunder-proto/tsconfig.json": [
        "env:ES2021"
      ],
      "node_modules/electron-to-chromium/package.json": [
        "env:ISC",
        "env:LICENSE"
      ],
      "node_modules/emoji-regex/package.json": [
        "env:LICENSE",
        "env:MIT",
        "env:NODE_ENV"
      ],
      "node_modules/es-abstract/package.json": [
        "env:ES5",
        "env:ES6",
        "env:ES7",
        "env:MIT"
      ],
      "node_modules/es-define-property/.github/FUNDING.yml": [
        "env:URL"
      ],
      "node_modules/es-define-property/package.json": [
        "env:CHANGELOG",
        "env:MIT",
        "env:README"
      ],
      "node_modules/es-errors/.github/FUNDING.yml": [
        "env:URL"
      ],
      "node_modules/es-errors/package.json": [
        "env:CHANGELOG",
        "env:MIT",
        "env:README"
      ],
      "node_modules/es-iterator-helpers/package.json": [
        "env:API",
        "env:CHANGELOG",
        "env:ES3",
        "env:MIT",
        "env:README",
        "runtime:s3"
      ],
      "node_modules/es-object-atoms/.github/FUNDING.yml": [
        "env:URL"
      ],
      "node_modules/es-object-atoms/package.json": [
        "env:CHANGELOG",
        "env:MIT",
        "env:README"
      ],
      "node_modules/es-set-tostringtag/package.json": [
        "env:CHANGELOG",
        "env:MIT",
        "env:README"
      ],
      "node_modules/es-shim-unscopables/package.json": [
        "env:CHANGELOG",
        "env:MIT",
        "env:README"
      ],
      "node_modules/es-to-primitive/package.json": [
        "env:CHANGELOG",
        "env:ES2015",
        "env:ES5",
        "env:MIT"
      ],
      "node_modules/escalade/package.json": [
        "env:MIT"
      ],
      "node_modules/escape-string-regexp/package.json": [
        "env:MIT"
      ],
      "node_modules/eslint/lib/cli-engine/formatters/formatters-meta.json": [
        "env:API",
        "env:CLI",
        "env:HTML",
        "env:JSON"
      ],
      "node_modules/eslint/package.json": [
        "env:AST",
        "env:LICENSE",
        "env:MIT",
        "env:README",
        "runtime:docker"
      ],
      "node_modules/eslint-plugin-jsx-a11y/package.json": [
        "env:AST",
        "env:CHANGELOG",
        "env:CONTRIBUTING",
        "env:JSX",
        "env:MIT"
      ],
      "node_modules/eslint-plugin-react/package.json": [
        "env:MIT"
      ],
      "node_modules/eslint-plugin-react-hooks/package.json": [
        "env:LICENSE",
        "env:MIT",
        "env:README"
      ],
      "node_modules/eslint-scope/package.json": [
        "env:BSD",
        "env:LICENSE",
        "env:README"
      ],
      "node_modules/eslint-visitor-keys/package.json": [
        "env:AST",
        "env:README"
      ],
      "node_modules/espree/package.json": [
        "env:BSD",
        "env:README"
      ],
      "node_modules/esquery/package.json": [
        "env:AST",
        "env:BSD",
        "env:CSS",
        "env:README"
      ],
      "node_modules/esrecurse/package.json": [
        "env:AST",
        "env:BSD"
      ],
      "node_modules/estraverse/package.json": [
        "env:AST",
        "env:BSD"
      ],
      "node_modules/esutils/package.json": [
        "env:BSD",
        "env:LICENSE",
        "env:README"
      ],
      "node_modules/eventemitter3/package.json": [
        "env:AND",
        "env:MIT"
      ],
      "node_modules/fast-deep-equal/package.json": [
        "env:ES5",
        "env:MIT"
      ],
      "node_modules/fast-glob/node_modules/glob-parent/package.json": [
        "env:ISC",
        "env:LICENSE"
      ],
      "node_modules/fast-glob/package.json": [
        "env:MIT"
      ],
      "node_modules/fast-json-stable-stringify/benchmark/test.json": [
        "env:DANJA",
        "env:FLEXIGEN",
        "env:VERAQ"
      ],
      "node_modules/fast-json-stable-stringify/package.json": [
        "env:JSON",
        "env:MIT"
      ],
      "node_modules/fast-levenshtein/package.json": [
        "env:MIT"
      ],
      "node_modules/fastq/package.json": [
        "env:ISC"
      ],
      "node_modules/fflate/package.json": [
        "env:MIT",
        "env:TS_NODE_PROJECT"
      ],
      "node_modules/file-entry-cache/package.json": [
        "env:MIT"
      ],
      "node_modules/fill-range/package.json": [
        "env:MIT"
      ],
      "node_modules/find-up/package.json": [
        "env:MIT"
      ],
      "node_modules/flat-cache/package.json": [
        "env:MIT"
      ],
      "node_modules/flatted/package.json": [
        "env:ISC",
        "env:JSON",
        "env:LICENSE",
        "env:README"
      ],
      "node_modules/for-each/package.json": [
        "env:CHANGELOG",
        "env:MIT"
      ],
      "node_modules/fraction.js/package.json": [
        "env:MIT",
        "env:RAW"
      ],
      "node_modules/fsevents/package.json": [
        "env:MIT"
      ],
      "node_modules/function-bind/package.json": [
        "env:CHANGELOG",
        "env:MIT"
      ],
      "node_modules/function.prototype.name/package.json": [
        "env:API",
        "env:CHANGELOG",
        "env:ES2015",
        "env:ES6",
        "env:MIT"
      ],
      "node_modules/functions-have-names/package.json": [
        "env:CHANGELOG",
        "env:MIT"
      ],
      "node_modules/generator-function/package.json": [
        "env:CHANGELOG",
        "env:MIT",
        "env:README"
      ],
      "node_modules/get-intrinsic/package.json": [
        "env:CHANGELOG",
        "env:MIT",
        "env:README"
      ],
      "node_modules/get-nonce/package.json": [
        "env:CHANGELOG",
        "env:MIT"
      ],
      "node_modules/get-proto/package.json": [
        "env:CHANGELOG",
        "env:MIT",
        "env:README"
      ],
      "node_modules/get-symbol-description/package.json": [
        "env:CHANGELOG",
        "env:MIT",
        "env:README"
      ],
      "node_modules/get-symbol-description/tsconfig.json": [
        "env:ES2021"
      ],
      "node_modules/glob-parent/package.json": [
        "env:ISC",
        "env:LICENSE"
      ],
      "node_modules/globals/globals.json": [
        "env:CSS",
        "env:DDP",
        "env:EJSON",
        "env:GPU",
        "env:HID",
        "env:HTTP",
        "env:JSON",
        "env:PERSISTENT",
        "env:TEMPORARY",
        "env:URL",
        "env:USB",
        "env:UUID",
        "env:WSH",
        "env:YAHOO",
        "env:YUI",
        "runtime:docker",
        "runtime:kubernetes",
        "runtime:s3"
      ],
      "node_modules/globals/package.json": [
        "env:MIT"
      ],
      "node_modules/globalthis/package.json": [
        "env:API",
        "env:CHANGELOG",
        "env:MIT"
      ],
      "node_modules/gopd/package.json": [
        "env:CHANGELOG",
        "env:MIT",
        "env:README"
      ],
      "node_modules/has-bigints/package.json": [
        "env:CHANGELOG",
        "env:ES2020",
        "env:MIT"
      ],
      "node_modules/has-bigints/tsconfig.json": [
        "env:ES2021"
      ],
      "node_modules/has-flag/package.json": [
        "env:MIT"
      ],
      "node_modules/has-property-descriptors/package.json": [
        "env:CHANGELOG",
        "env:MIT",
        "env:README"
      ],
      "node_modules/has-proto/package.json": [
        "env:CHANGELOG",
        "env:MIT",
        "env:README"
      ],
      "node_modules/has-symbols/package.json": [
        "env:CHANGELOG",
        "env:ES6",
        "env:MIT"
      ],
      "node_modules/has-symbols/tsconfig.json": [
        "env:ES2021"
      ],
      "node_modules/has-tostringtag/package.json": [
        "env:CHANGELOG",
        "env:MIT"
      ],
      "node_modules/hasown/.github/FUNDING.yml": [
        "env:URL"
      ],
      "node_modules/hasown/package.json": [
        "env:CHANGELOG",
        "env:ES3",
        "env:MIT",
        "env:README",
        "runtime:s3"
      ],
      "node_modules/ignore/package.json": [
        "env:ES6",
        "env:IGNORE_ONLY_IGNORES",
        "env:IGNORE_TEST_WIN32",
        "env:LICENSE",
        "env:MIT"
      ],
      "node_modules/import-fresh/package.json": [
        "env:MIT"
      ],
      "node_modules/imurmurhash/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/internal-slot/.github/FUNDING.yml": [
        "env:URL"
      ],
      "node_modules/internal-slot/package.json": [
        "env:CHANGELOG",
        "env:MIT"
      ],
      "node_modules/iron-session/package.json": [
        "env:MIT"
      ],
      "node_modules/iron-webcrypto/package.json": [
        "env:JSON",
        "env:MIT"
      ],
      "node_modules/is-array-buffer/package.json": [
        "env:CHANGELOG",
        "env:MIT"
      ],
      "node_modules/is-array-buffer/tsconfig.json": [
        "env:ES2021"
      ],
      "node_modules/is-async-function/package.json": [
        "env:CHANGELOG",
        "env:MIT"
      ],
      "node_modules/is-async-function/tsconfig.json": [
        "env:ES2021"
      ],
      "node_modules/is-bigint/package.json": [
        "env:CHANGELOG",
        "env:MIT"
      ],
      "node_modules/is-bigint/tsconfig.json": [
        "env:ES2021"
      ],
      "node_modules/is-binary-path/package.json": [
        "env:MIT"
      ],
      "node_modules/is-boolean-object/package.json": [
        "env:CHANGELOG",
        "env:ES6",
        "env:MIT"
      ],
      "node_modules/is-boolean-object/tsconfig.json": [
        "env:ES2021"
      ],
      "node_modules/is-callable/package.json": [
        "env:CHANGELOG",
        "env:ES6",
        "env:MIT"
      ],
      "node_modules/is-core-module/package.json": [
        "env:CHANGELOG",
        "env:MIT"
      ],
      "node_modules/is-data-view/package.json": [
        "env:CHANGELOG",
        "env:ES6",
        "env:MIT",
        "env:README"
      ],
      "node_modules/is-data-view/tsconfig.json": [
        "env:ES2021"
      ],
      "node_modules/is-date-object/package.json": [
        "env:CHANGELOG",
        "env:ES6",
        "env:MIT"
      ],
      "node_modules/is-extglob/package.json": [
        "env:MIT"
      ],
      "node_modules/is-finalizationregistry/package.json": [
        "env:CHANGELOG",
        "env:ES6",
        "env:MIT"
      ],
      "node_modules/is-finalizationregistry/tsconfig.json": [
        "env:ES2021"
      ],
      "node_modules/is-generator-function/package.json": [
        "env:CHANGELOG",
        "env:MIT"
      ],
      "node_modules/is-glob/package.json": [
        "env:MIT"
      ],
      "node_modules/is-map/package.json": [
        "env:CHANGELOG",
        "env:ES6",
        "env:MIT"
      ],
      "node_modules/is-negative-zero/package.json": [
        "env:CHANGELOG",
        "env:MIT"
      ],
      "node_modules/is-number/package.json": [
        "env:MIT"
      ],
      "node_modules/is-number-object/package.json": [
        "env:CHANGELOG",
        "env:ES6",
        "env:MIT"
      ],
      "node_modules/is-number-object/tsconfig.json": [
        "env:ES2021"
      ],
      "node_modules/is-regex/package.json": [
        "env:CHANGELOG",
        "env:ES6",
        "env:MIT"
      ],
      "node_modules/is-regex/tsconfig.json": [
        "env:ES2021"
      ],
      "node_modules/is-set/package.json": [
        "env:CHANGELOG",
        "env:ES6",
        "env:MIT"
      ],
      "node_modules/is-shared-array-buffer/package.json": [
        "env:CHANGELOG",
        "env:MIT"
      ],
      "node_modules/is-shared-array-buffer/tsconfig.json": [
        "env:ES2021"
      ],
      "node_modules/is-string/package.json": [
        "env:CHANGELOG",
        "env:ES6",
        "env:MIT"
      ],
      "node_modules/is-string/tsconfig.json": [
        "env:ES2021"
      ],
      "node_modules/is-symbol/package.json": [
        "env:CHANGELOG",
        "env:ES6",
        "env:MIT"
      ],
      "node_modules/is-symbol/tsconfig.json": [
        "env:ES2021"
      ],
      "node_modules/is-typed-array/package.json": [
        "env:CHANGELOG",
        "env:ES6",
        "env:MIT",
        "env:README"
      ],
      "node_modules/is-weakmap/package.json": [
        "env:CHANGELOG",
        "env:ES6",
        "env:MIT",
        "runtime:kubernetes"
      ],
      "node_modules/is-weakref/package.json": [
        "env:CHANGELOG",
        "env:ES6",
        "env:MIT"
      ],
      "node_modules/is-weakref/tsconfig.json": [
        "env:ES2021"
      ],
      "node_modules/is-weakset/.github/FUNDING.yml": [
        "runtime:kubernetes"
      ],
      "node_modules/is-weakset/package.json": [
        "env:CHANGELOG",
        "env:ES6",
        "env:MIT",
        "runtime:kubernetes"
      ],
      "node_modules/is-weakset/tsconfig.json": [
        "env:ES2021"
      ],
      "node_modules/isarray/package.json": [
        "env:MIT"
      ],
      "node_modules/isexe/package.json": [
        "env:ISC"
      ],
      "node_modules/iterator.prototype/.github/FUNDING.yml": [
        "env:URL"
      ],
      "node_modules/iterator.prototype/package.json": [
        "env:CHANGELOG",
        "env:MIT",
        "env:README"
      ],
      "node_modules/jiti/package.json": [
        "env:ESM",
        "env:JITI_CACHE",
        "env:JITI_DEBUG",
        "env:JITI_REQUIRE_CACHE",
        "env:MIT",
        "env:NODE_ENV"
      ],
      "node_modules/jose/package.json": [
        "env:JWA",
        "env:JWE",
        "env:JWK",
        "env:JWKS",
        "env:JWS",
        "env:JWT",
        "env:MIT"
      ],
      "node_modules/js-tokens/package.json": [
        "env:MIT"
      ],
      "node_modules/js-yaml/package.json": [
        "env:MIT",
        "env:YAML",
        "runtime:kubernetes"
      ],
      "node_modules/json-buffer/package.json": [
        "env:JSON",
        "env:MIT"
      ],
      "node_modules/json-schema-traverse/package.json": [
        "env:JSON",
        "env:MIT"
      ],
      "node_modules/json-stable-stringify-without-jsonify/package.json": [
        "env:JSON",
        "env:MIT"
      ],
      "node_modules/jsx-ast-utils/package.json": [
        "env:AST",
        "env:CHANGELOG",
        "env:JSX",
        "env:MIT"
      ],
      "node_modules/keyv/package.json": [
        "env:MIT"
      ],
      "node_modules/language-subtag-registry/data/json/index.json": [
        "runtime:kubernetes"
      ],
      "node_modules/language-subtag-registry/data/json/language.json": [
        "runtime:kubernetes"
      ],
      "node_modules/language-subtag-registry/data/json/registry.json": [
        "env:ALA",
        "env:API",
        "env:ASL",
        "env:BASL",
        "env:BCE",
        "env:BCI",
        "env:BSV",
        "env:HSL",
        "env:ISBN",
        "env:ISO",
        "env:KLI",
        "env:KQSL",
        "env:PRC",
        "env:SAMPA",
        "env:USA",
        "env:USSR",
        "runtime:kubernetes"
      ],
      "node_modules/language-subtag-registry/package.json": [
        "env:BCP",
        "env:CC0",
        "env:IANA",
        "env:JSON"
      ],
      "node_modules/language-tags/package.json": [
        "env:IANA",
        "env:MIT"
      ],
      "node_modules/levn/package.json": [
        "env:LICENSE",
        "env:MIT",
        "env:README"
      ],
      "node_modules/lilconfig/package.json": [
        "env:MIT",
        "env:NODE_OPTIONS"
      ],
      "node_modules/lines-and-columns/package.json": [
        "env:MIT"
      ],
      "node_modules/locate-path/package.json": [
        "env:MIT"
      ],
      "node_modules/lodash.merge/package.json": [
        "env:MIT"
      ],
      "node_modules/long/package.json": [
        "env:LICENSE",
        "env:README"
      ],
      "node_modules/loose-envify/package.json": [
        "env:AST",
        "env:MIT"
      ],
      "node_modules/lucide-react/package.json": [
        "env:ISC",
        "env:LICENSE",
        "env:SVG"
      ],
      "node_modules/math-intrinsics/.github/FUNDING.yml": [
        "env:URL"
      ],
      "node_modules/math-intrinsics/package.json": [
        "env:CHANGELOG",
        "env:MIT",
        "env:README"
      ],
      "node_modules/merge2/package.json": [
        "env:MIT",
        "env:README"
      ],
      "node_modules/micromatch/package.json": [
        "env:MIT"
      ],
      "node_modules/minimatch/package.json": [
        "env:ISC"
      ],
      "node_modules/ms/package.json": [
        "env:MIT"
      ],
      "node_modules/mz/package.json": [
        "env:MIT"
      ],
      "node_modules/nanoid/package.json": [
        "env:MIT",
        "env:URL"
      ],
      "node_modules/natural-compare/package.json": [
        "env:LICENSE",
        "env:MIT",
        "env:README"
      ],
      "node_modules/next/dist/compiled/@ampproject/toolbox-optimizer/package.json": [
        "env:AMPHTML"
      ],
      "node_modules/next/dist/compiled/@babel/runtime/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/@edge-runtime/cookies/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/@edge-runtime/ponyfill/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/@edge-runtime/primitives/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/@hapi/accept/package.json": [
        "env:BSD"
      ],
      "node_modules/next/dist/compiled/@mswjs/interceptors/ClientRequest/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/@napi-rs/triples/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/@next/font/dist/google/font-data.json": [
        "env:ACT",
        "env:ARRR",
        "env:B612",
        "env:BIZ",
        "env:BLED",
        "env:BNCE",
        "env:CASL",
        "env:CRSV",
        "env:EAN13",
        "env:EDPT",
        "env:EHLT",
        "env:ELGR",
        "env:ELSH",
        "env:ELXP",
        "env:FLAR",
        "env:GFS",
        "env:GRAD",
        "env:HEXP",
        "env:IBM",
        "env:INFM",
        "env:K2D",
        "env:LXGW",
        "env:MONO",
        "env:MORF",
        "env:NSW",
        "env:NTR",
        "env:PLUS",
        "env:QLD",
        "env:REM",
        "env:ROND",
        "env:SAS",
        "env:SCAN",
        "env:SHLN",
        "env:SHRP",
        "env:SIL",
        "env:SOFT",
        "env:SPAC",
        "env:STIX",
        "env:SUSE",
        "env:TAS",
        "env:VIC",
        "env:VLG",
        "env:VOLM",
        "env:VT323",
        "env:WAL",
        "env:WDXL",
        "env:WONK",
        "env:XELA",
        "env:XOPQ",
        "env:XROT",
        "env:XTRA",
        "env:YEAR",
        "env:YELA",
        "env:YOPQ",
        "env:YROT",
        "env:YTAS",
        "env:YTDE",
        "env:YTFI",
        "env:YTLC",
        "env:YTUC",
        "env:ZCOOL",
        "runtime:kubernetes",
        "runtime:slack"
      ],
      "node_modules/next/dist/compiled/@next/font/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/@vercel/nft/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/@vercel/og/package.json": [
        "env:MPL"
      ],
      "node_modules/next/dist/compiled/acorn/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/amphtml-validator/package.json": [
        "env:AMP",
        "env:HTML"
      ],
      "node_modules/next/dist/compiled/anser/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/assert/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/async-retry/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/async-sema/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/babel/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/babel-code-frame/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/browserify-zlib/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/browserslist/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/buffer/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/bytes/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/ci-info/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/cli-select/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/client-only/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/commander/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/comment-json/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/compression/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/conf/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/constants-browserify/constants.json": [
        "env:DH_CHECK_P_NOT_PRIME",
        "env:DH_CHECK_P_NOT_SAFE_PRIME",
        "env:DH_NOT_SUITABLE_GENERATOR",
        "env:DH_UNABLE_TO_CHECK_GENERATOR",
        "env:E2BIG",
        "env:EACCES",
        "env:EADDRINUSE",
        "env:EADDRNOTAVAIL",
        "env:EAFNOSUPPORT",
        "env:EAGAIN",
        "env:EALREADY",
        "env:EBADF",
        "env:EBADMSG",
        "env:EBUSY",
        "env:ECANCELED",
        "env:ECHILD",
        "env:ECONNABORTED",
        "env:ECONNREFUSED",
        "env:ECONNRESET",
        "env:EDEADLK",
        "env:EDESTADDRREQ",
        "env:EDOM",
        "env:EDQUOT",
        "env:EEXIST",
        "env:EFAULT",
        "env:EFBIG",
        "env:EHOSTUNREACH",
        "env:EIDRM",
        "env:EILSEQ",
        "env:EINPROGRESS",
        "env:EINTR",
        "env:EINVAL",
        "env:EIO",
        "env:EISCONN",
        "env:EISDIR",
        "env:ELOOP",
        "env:EMFILE",
        "env:EMLINK",
        "env:EMSGSIZE",
        "env:EMULTIHOP",
        "env:ENAMETOOLONG",
        "env:ENETDOWN",
        "env:ENETRESET",
        "env:ENETUNREACH",
        "env:ENFILE",
        "env:ENGINE_METHOD_ALL",
        "env:ENGINE_METHOD_CIPHERS",
        "env:ENGINE_METHOD_DH",
        "env:ENGINE_METHOD_DIGESTS",
        "env:ENGINE_METHOD_DSA",
        "env:ENGINE_METHOD_ECDH",
        "env:ENGINE_METHOD_ECDSA",
        "env:ENGINE_METHOD_NONE",
        "env:ENGINE_METHOD_PKEY_ASN1_METHS",
        "env:ENGINE_METHOD_PKEY_METHS",
        "env:ENGINE_METHOD_RAND",
        "env:ENGINE_METHOD_STORE",
        "env:ENOBUFS",
        "env:ENODATA",
        "env:ENODEV",
        "env:ENOENT",
        "env:ENOEXEC",
        "env:ENOLCK",
        "env:ENOLINK",
        "env:ENOMEM",
        "env:ENOMSG",
        "env:ENOPROTOOPT",
        "env:ENOSPC",
        "env:ENOSR",
        "env:ENOSTR",
        "env:ENOSYS",
        "env:ENOTCONN",
        "env:ENOTDIR",
        "env:ENOTEMPTY",
        "env:ENOTSOCK",
        "env:ENOTSUP",
        "env:ENOTTY",
        "env:ENXIO",
        "env:EOPNOTSUPP",
        "env:EOVERFLOW",
        "env:EPERM",
        "env:EPIPE",
        "env:EPROTO",
        "env:EPROTONOSUPPORT",
        "env:EPROTOTYPE",
        "env:ERANGE",
        "env:EROFS",
        "env:ESPIPE",
        "env:ESRCH",
        "env:ESTALE",
        "env:ETIME",
        "env:ETIMEDOUT",
        "env:ETXTBSY",
        "env:EWOULDBLOCK",
        "env:EXDEV",
        "env:F_OK",
        "env:NPN_ENABLED",
        "env:O_APPEND",
        "env:O_CREAT",
        "env:O_DIRECTORY",
        "env:O_EXCL",
        "env:O_NOCTTY",
        "env:O_NOFOLLOW",
        "env:O_NONBLOCK",
        "env:O_RDONLY",
        "env:O_RDWR",
        "env:O_SYMLINK",
        "env:O_SYNC",
        "env:O_TRUNC",
        "env:O_WRONLY",
        "env:POINT_CONVERSION_COMPRESSED",
        "env:POINT_CONVERSION_HYBRID",
        "env:POINT_CONVERSION_UNCOMPRESSED",
        "env:RSA_NO_PADDING",
        "env:RSA_PKCS1_OAEP_PADDING",
        "env:RSA_PKCS1_PADDING",
        "env:RSA_PKCS1_PSS_PADDING",
        "env:RSA_SSLV23_PADDING",
        "env:RSA_X931_PADDING",
        "env:R_OK",
        "env:SIGABRT",
        "env:SIGALRM",
        "env:SIGBUS",
        "env:SIGCHLD",
        "env:SIGCONT",
        "env:SIGFPE",
        "env:SIGHUP",
        "env:SIGILL",
        "env:SIGINT",
        "env:SIGIO",
        "env:SIGIOT",
        "env:SIGKILL",
        "env:SIGPIPE",
        "env:SIGPROF",
        "env:SIGQUIT",
        "env:SIGSEGV",
        "env:SIGSTOP",
        "env:SIGSYS",
        "env:SIGTERM",
        "env:SIGTRAP",
        "env:SIGTSTP",
        "env:SIGTTIN",
        "env:SIGTTOU",
        "env:SIGURG",
        "env:SIGUSR1",
        "env:SIGUSR2",
        "env:SIGVTALRM",
        "env:SIGWINCH",
        "env:SIGXCPU",
        "env:SIGXFSZ",
        "env:SSL_OP_ALL",
        "env:SSL_OP_ALLOW_UNSAFE_LEGACY_RENEGOTIATION",
        "env:SSL_OP_CIPHER_SERVER_PREFERENCE",
        "env:SSL_OP_CISCO_ANYCONNECT",
        "env:SSL_OP_COOKIE_EXCHANGE",
        "env:SSL_OP_CRYPTOPRO_TLSEXT_BUG",
        "env:SSL_OP_DONT_INSERT_EMPTY_FRAGMENTS",
        "env:SSL_OP_EPHEMERAL_RSA",
        "env:SSL_OP_LEGACY_SERVER_CONNECT",
        "env:SSL_OP_MICROSOFT_BIG_SSLV3_BUFFER",
        "env:SSL_OP_MICROSOFT_SESS_ID_BUG",
        "env:SSL_OP_MSIE_SSLV2_RSA_PADDING",
        "env:SSL_OP_NETSCAPE_CA_DN_BUG",
        "env:SSL_OP_NETSCAPE_CHALLENGE_BUG",
        "env:SSL_OP_NETSCAPE_DEMO_CIPHER_CHANGE_BUG",
        "env:SSL_OP_NETSCAPE_REUSE_CIPHER_CHANGE_BUG",
        "env:SSL_OP_NO_COMPRESSION",
        "env:SSL_OP_NO_QUERY_MTU",
        "env:SSL_OP_NO_SESSION_RESUMPTION_ON_RENEGOTIATION",
        "env:SSL_OP_NO_TICKET",
        "env:SSL_OP_PKCS1_CHECK_1",
        "env:SSL_OP_PKCS1_CHECK_2",
        "env:SSL_OP_SINGLE_DH_USE",
        "env:SSL_OP_SINGLE_ECDH_USE",
        "env:SSL_OP_SSLEAY_080_CLIENT_DH_BUG",
        "env:SSL_OP_SSLREF2_REUSE_CERT_TYPE_BUG",
        "env:SSL_OP_TLS_BLOCK_PADDING_BUG",
        "env:SSL_OP_TLS_D5_BUG",
        "env:SSL_OP_TLS_ROLLBACK_BUG",
        "env:S_IFBLK",
        "env:S_IFCHR",
        "env:S_IFDIR",
        "env:S_IFIFO",
        "env:S_IFLNK",
        "env:S_IFMT",
        "env:S_IFREG",
        "env:S_IFSOCK",
        "env:S_IRGRP",
        "env:S_IROTH",
        "env:S_IRUSR",
        "env:S_IRWXG",
        "env:S_IRWXO",
        "env:S_IRWXU",
        "env:S_IWGRP",
        "env:S_IWOTH",
        "env:S_IWUSR",
        "env:S_IXGRP",
        "env:S_IXOTH",
        "env:S_IXUSR",
        "env:UV_UDP_REUSEADDR",
        "env:W_OK",
        "env:X_OK"
      ],
      "node_modules/next/dist/compiled/content-disposition/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/content-type/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/cookie/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/cross-spawn/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/crypto-browserify/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/css.escape/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/data-uri-to-buffer/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/debug/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/devalue/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/domain-browser/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/edge-runtime/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/events/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/find-up/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/fresh/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/glob/package.json": [
        "env:ISC"
      ],
      "node_modules/next/dist/compiled/gzip-size/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/http-proxy/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/http-proxy-agent/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/https-browserify/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/https-proxy-agent/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/icss-utils/package.json": [
        "env:ISC"
      ],
      "node_modules/next/dist/compiled/image-size/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/is-animated/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/is-docker/package.json": [
        "env:MIT",
        "runtime:docker"
      ],
      "node_modules/next/dist/compiled/is-wsl/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/jest-worker/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/json5/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/jsonwebtoken/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/loader-runner/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/loader-utils2/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/loader-utils3/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/lodash.curry/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/lru-cache/package.json": [
        "env:ISC"
      ],
      "node_modules/next/dist/compiled/mini-css-extract-plugin/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/nanoid/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/neo-async/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/node-html-parser/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/ora/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/os-browserify/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/p-limit/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/p-queue/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/path-browserify/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/path-to-regexp/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/picomatch/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/postcss-flexbugs-fixes/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/postcss-modules-extract-imports/package.json": [
        "env:ISC"
      ],
      "node_modules/next/dist/compiled/postcss-modules-local-by-default/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/postcss-modules-scope/package.json": [
        "env:ISC"
      ],
      "node_modules/next/dist/compiled/postcss-modules-values/package.json": [
        "env:ISC"
      ],
      "node_modules/next/dist/compiled/postcss-preset-env/package.json": [
        "env:CC0"
      ],
      "node_modules/next/dist/compiled/postcss-safe-parser/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/postcss-scss/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/postcss-value-parser/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/process/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/punycode/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/querystring-es3/package.json": [
        "runtime:s3"
      ],
      "node_modules/next/dist/compiled/raw-body/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/react-is/package.json": [
        "env:LICENSE",
        "env:MIT",
        "env:README"
      ],
      "node_modules/next/dist/compiled/react-refresh/package.json": [
        "env:LICENSE",
        "env:MIT",
        "env:README"
      ],
      "node_modules/next/dist/compiled/regenerator-runtime/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/safe-stable-stringify/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/sass-loader/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/schema-utils2/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/schema-utils3/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/semver/package.json": [
        "env:ISC"
      ],
      "node_modules/next/dist/compiled/send/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/server-only/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/setimmediate/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/shell-quote/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/source-map/package.json": [
        "env:BSD"
      ],
      "node_modules/next/dist/compiled/source-map08/package.json": [
        "env:BSD"
      ],
      "node_modules/next/dist/compiled/stacktrace-parser/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/stream-browserify/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/stream-http/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/string-hash/package.json": [
        "env:CC0"
      ],
      "node_modules/next/dist/compiled/string_decoder/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/strip-ansi/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/superstruct/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/tar/package.json": [
        "env:ISC"
      ],
      "node_modules/next/dist/compiled/terser/package.json": [
        "env:BSD"
      ],
      "node_modules/next/dist/compiled/text-table/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/timers-browserify/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/tty-browserify/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/ua-parser-js/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/unistore/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/util/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/vm-browserify/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/watchpack/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/webpack/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/webpack-sources1/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/webpack-sources3/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/ws/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/zod/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/compiled/zod-validation-error/package.json": [
        "env:MIT"
      ],
      "node_modules/next/dist/esm/lib/server-external-packages.json": [
        "runtime:s3"
      ],
      "node_modules/next/dist/lib/server-external-packages.json": [
        "runtime:s3"
      ],
      "node_modules/next/dist/server/capsize-font-metrics.json": [
        "env:ACT",
        "env:B612",
        "env:BIZ",
        "env:EAN13",
        "env:FELL",
        "env:GFS",
        "env:IBM",
        "env:K2D",
        "env:LXGW",
        "env:MPLUS1",
        "env:MPLUS2",
        "env:NSW",
        "env:NTR",
        "env:PLUS",
        "env:QLD",
        "env:REM",
        "env:SAS",
        "env:SFNS",
        "env:SIL",
        "env:STIX",
        "env:SUSE",
        "env:TAS",
        "env:VIC",
        "env:VLG",
        "env:VT323",
        "env:WAL",
        "env:ZCOOL",
        "runtime:kubernetes",
        "runtime:s3",
        "runtime:slack"
      ],
      "node_modules/next/node_modules/postcss/package.json": [
        "env:MIT",
        "runtime:docker"
      ],
      "node_modules/next/package.json": [
        "env:BROWSER",
        "env:MIT",
        "env:NEXT_SERVER_NO_MANGLE",
        "runtime:docker",
        "runtime:s3"
      ],
      "node_modules/node-exports-info/package.json": [
        "env:CHANGELOG",
        "env:MIT"
      ],
      "node_modules/node-releases/package.json": [
        "env:MIT"
      ],
      "node_modules/normalize-path/package.json": [
        "env:MIT"
      ],
      "node_modules/object-assign/package.json": [
        "env:ES2015",
        "env:MIT"
      ],
      "node_modules/object-hash/package.json": [
        "env:MIT"
      ],
      "node_modules/object-inspect/package.json": [
        "env:CHANGELOG",
        "env:MIT"
      ],
      "node_modules/object-keys/.travis.yml": [
        "env:ALLOW_FAILURE",
        "env:COVERAGE",
        "env:NPM_CONFIG_STRICT_SSL",
        "env:POSTTEST",
        "env:PRETEST",
        "env:TEST",
        "env:TRAVIS_NODE_VERSION"
      ],
      "node_modules/object-keys/package.json": [
        "env:ES5",
        "env:MIT"
      ],
      "node_modules/object.assign/package.json": [
        "env:API",
        "env:ES6",
        "env:MIT"
      ],
      "node_modules/object.entries/package.json": [
        "env:API",
        "env:CHANGELOG",
        "env:ES2017",
        "env:ES7",
        "env:ES8",
        "env:MIT"
      ],
      "node_modules/object.fromentries/package.json": [
        "env:API",
        "env:CHANGELOG",
        "env:ES2017",
        "env:ES7",
        "env:ES8",
        "env:MIT"
      ],
      "node_modules/object.values/package.json": [
        "env:API",
        "env:CHANGELOG",
        "env:ES2017",
        "env:ES7",
        "env:ES8",
        "env:MIT"
      ],
      "node_modules/optionator/package.json": [
        "env:LICENSE",
        "env:MIT",
        "env:README"
      ],
      "node_modules/own-keys/package.json": [
        "env:CHANGELOG",
        "env:MIT",
        "env:README"
      ],
      "node_modules/p-limit/package.json": [
        "env:MIT"
      ],
      "node_modules/p-locate/package.json": [
        "env:MIT"
      ],
      "node_modules/parent-module/package.json": [
        "env:MIT"
      ],
      "node_modules/path-exists/package.json": [
        "env:MIT"
      ],
      "node_modules/path-key/package.json": [
        "env:MIT",
        "env:PATH"
      ],
      "node_modules/path-parse/package.json": [
        "env:MIT"
      ],
      "node_modules/path-to-regexp/package.json": [
        "env:MIT"
      ],
      "node_modules/picocolors/package.json": [
        "env:ANSI",
        "env:ISC"
      ],
      "node_modules/picomatch/package.json": [
        "env:MIT",
        "env:POSIX"
      ],
      "node_modules/pify/package.json": [
        "env:MIT"
      ],
      "node_modules/pirates/package.json": [
        "env:MIT"
      ],
      "node_modules/possible-typed-array-names/.github/FUNDING.yml": [
        "env:URL"
      ],
      "node_modules/possible-typed-array-names/package.json": [
        "env:CHANGELOG",
        "env:MIT",
        "env:README"
      ],
      "node_modules/postcss/package.json": [
        "env:MIT",
        "runtime:docker"
      ],
      "node_modules/postcss-import/node_modules/resolve/package.json": [
        "env:CONTRIBUTING",
        "env:MIT"
      ],
      "node_modules/postcss-import/node_modules/resolve/test/resolver/multirepo/package.json": [
        "env:MIT"
      ],
      "node_modules/postcss-import/node_modules/resolve/test/resolver/multirepo/packages/package-a/package.json": [
        "env:MIT"
      ],
      "node_modules/postcss-import/node_modules/resolve/test/resolver/multirepo/packages/package-b/package.json": [
        "env:MIT"
      ],
      "node_modules/postcss-import/node_modules/resolve/test/resolver/nested_symlinks/mylib/package.json": [
        "env:ISC"
      ],
      "node_modules/postcss-import/package.json": [
        "env:CSS",
        "env:MIT"
      ],
      "node_modules/postcss-js/package.json": [
        "env:CSS",
        "env:MIT"
      ],
      "node_modules/postcss-load-config/package.json": [
        "env:MIT"
      ],
      "node_modules/postcss-nested/package.json": [
        "env:MIT"
      ],
      "node_modules/postcss-selector-parser/package.json": [
        "env:API",
        "env:BABEL_ENV",
        "env:CHANGELOG",
        "env:LICENSE",
        "env:MIT"
      ],
      "node_modules/postcss-value-parser/package.json": [
        "env:MIT"
      ],
      "node_modules/posthog-js/lib/package.json": [
        "env:ESR",
        "env:LICENSE",
        "env:NODE_OPTIONS",
        "env:PACKAGE_DEST",
        "env:SEE",
        "env:VERCEL",
        "env:WRITE_MANGLED_PROPERTIES"
      ],
      "node_modules/posthog-js/package.json": [
        "env:ESR",
        "env:LICENSE",
        "env:NODE_OPTIONS",
        "env:PACKAGE_DEST",
        "env:SEE",
        "env:WRITE_MANGLED_PROPERTIES"
      ],
      "node_modules/posthog-js/react/package.json": [
        "env:NPM"
      ],
      "node_modules/preact/compat/package.json": [
        "env:MIT"
      ],
      "node_modules/preact/debug/package.json": [
        "env:MIT"
      ],
      "node_modules/preact/devtools/package.json": [
        "env:MIT"
      ],
      "node_modules/preact/hooks/package.json": [
        "env:MIT"
      ],
      "node_modules/preact/jsx-runtime/package.json": [
        "env:JSX",
        "env:MIT"
      ],
      "node_modules/preact/package.json": [
        "env:COVERAGE",
        "env:DOM",
        "env:MINIFY",
        "env:MIT"
      ],
      "node_modules/preact/test-utils/package.json": [
        "env:MIT"
      ],
      "node_modules/prelude-ls/package.json": [
        "env:LICENSE",
        "env:MIT",
        "env:README"
      ],
      "node_modules/prop-types/package.json": [
        "env:LICENSE",
        "env:MIT",
        "env:NODE_ENV",
        "env:README"
      ],
      "node_modules/protobufjs/google/protobuf/api.json": [
        "env:SYNTAX_PROTO2",
        "env:SYNTAX_PROTO3"
      ],
      "node_modules/protobufjs/google/protobuf/descriptor.json": [
        "env:ALIAS",
        "env:ALLOW",
        "env:CLOSED",
        "env:CODE_SIZE",
        "env:CORD",
        "env:DECLARATION",
        "env:DEFAULT_SYMBOL_VISIBILITY_UNKNOWN",
        "env:DELIMITED",
        "env:EDITION_1_TEST_ONLY",
        "env:EDITION_2023",
        "env:EDITION_2024",
        "env:EDITION_2_TEST_ONLY",
        "env:EDITION_99997_TEST_ONLY",
        "env:EDITION_99998_TEST_ONLY",
        "env:EDITION_99999_TEST_ONLY",
        "env:EDITION_LEGACY",
        "env:EDITION_MAX",
        "env:EDITION_PROTO2",
        "env:EDITION_PROTO3",
        "env:EDITION_UNKNOWN",
        "env:ENFORCE_NAMING_STYLE_UNKNOWN",
        "env:ENUM_TYPE_UNKNOWN",
        "env:EXPANDED",
        "env:EXPLICIT",
        "env:EXPORT_ALL",
        "env:EXPORT_TOP_LEVEL",
        "env:FIELD_PRESENCE_UNKNOWN",
        "env:GPB",
        "env:IDEMPOTENCY_UNKNOWN",
        "env:IDEMPOTENT",
        "env:IMPLICIT",
        "env:JSON_FORMAT_UNKNOWN",
        "env:JS_NORMAL",
        "env:JS_NUMBER",
        "env:JS_STRING",
        "env:LABEL_OPTIONAL",
        "env:LABEL_REPEATED",
        "env:LABEL_REQUIRED",
        "env:LEGACY_BEST_EFFORT",
        "env:LEGACY_REQUIRED",
        "env:LENGTH_PREFIXED",
        "env:LITE_RUNTIME",
        "env:LOCAL_ALL",
        "env:MESSAGE_ENCODING_UNKNOWN",
        "env:NONE",
        "env:NO_SIDE_EFFECTS",
        "env:OPEN",
        "env:PACKED",
        "env:REPEATED_FIELD_ENCODING_UNKNOWN",
        "env:RETENTION_RUNTIME",
        "env:RETENTION_SOURCE",
        "env:RETENTION_UNKNOWN",
        "env:SET",
        "env:SPEED",
        "env:STRICT",
        "env:STRING",
        "env:STRING_PIECE",
        "env:STYLE2024",
        "env:STYLE_LEGACY",
        "env:TARGET_TYPE_ENUM",
        "env:TARGET_TYPE_ENUM_ENTRY",
        "env:TARGET_TYPE_EXTENSION_RANGE",
        "env:TARGET_TYPE_FIELD",
        "env:TARGET_TYPE_FILE",
        "env:TARGET_TYPE_MESSAGE",
        "env:TARGET_TYPE_METHOD",
        "env:TARGET_TYPE_ONEOF",
        "env:TARGET_TYPE_SERVICE",
        "env:TARGET_TYPE_UNKNOWN",
        "env:TYPE_BOOL",
        "env:TYPE_BYTES",
        "env:TYPE_DOUBLE",
        "env:TYPE_ENUM",
        "env:TYPE_FIXED32",
        "env:TYPE_FIXED64",
        "env:TYPE_FLOAT",
        "env:TYPE_GROUP",
        "env:TYPE_INT32",
        "env:TYPE_INT64",
        "env:TYPE_MESSAGE",
        "env:TYPE_SFIXED32",
        "env:TYPE_SFIXED64",
        "env:TYPE_SINT32",
        "env:TYPE_SINT64",
        "env:TYPE_STRING",
        "env:TYPE_UINT32",
        "env:TYPE_UINT64",
        "env:UNVERIFIED",
        "env:UTF8_VALIDATION_UNKNOWN",
        "env:VERIFY",
        "env:VISIBILITY_EXPORT",
        "env:VISIBILITY_LOCAL",
        "env:VISIBILITY_UNSET"
      ],
      "node_modules/protobufjs/google/protobuf/type.json": [
        "env:CARDINALITY_OPTIONAL",
        "env:CARDINALITY_REPEATED",
        "env:CARDINALITY_REQUIRED",
        "env:CARDINALITY_UNKNOWN",
        "env:SYNTAX_PROTO2",
        "env:SYNTAX_PROTO3",
        "env:TYPE_BOOL",
        "env:TYPE_BYTES",
        "env:TYPE_DOUBLE",
        "env:TYPE_ENUM",
        "env:TYPE_FIXED32",
        "env:TYPE_FIXED64",
        "env:TYPE_FLOAT",
        "env:TYPE_GROUP",
        "env:TYPE_INT32",
        "env:TYPE_INT64",
        "env:TYPE_MESSAGE",
        "env:TYPE_SFIXED32",
        "env:TYPE_SFIXED64",
        "env:TYPE_SINT32",
        "env:TYPE_SINT64",
        "env:TYPE_STRING",
        "env:TYPE_UINT32",
        "env:TYPE_UINT64",
        "env:TYPE_UNKNOWN"
      ],
      "node_modules/protobufjs/package.json": [
        "env:BSD",
        "env:README"
      ],
      "node_modules/protobufjs/tsconfig.json": [
        "env:ES5"
      ],
      "node_modules/punycode/package.json": [
        "env:LICENSE",
        "env:MIT",
        "env:RFC"
      ],
      "node_modules/query-selector-shadow-dom/package.json": [
        "env:MIT"
      ],
      "node_modules/queue-microtask/package.json": [
        "env:MIT"
      ],
      "node_modules/react/package.json": [
        "env:LICENSE",
        "env:MIT",
        "env:README"
      ],
      "node_modules/react-dom/package.json": [
        "env:DOM",
        "env:LICENSE",
        "env:MIT",
        "env:README"
      ],
      "node_modules/react-is/package.json": [
        "env:LICENSE",
        "env:MIT",
        "env:README"
      ],
      "node_modules/react-remove-scroll/package.json": [
        "env:CHANGELOG",
        "env:MIT"
      ],
      "node_modules/react-remove-scroll-bar/package.json": [
        "env:CHANGELOG",
        "env:MIT"
      ],
      "node_modules/react-style-singleton/package.json": [
        "env:CHANGELOG",
        "env:MIT"
      ],
      "node_modules/read-cache/package.json": [
        "env:MIT"
      ],
      "node_modules/readdirp/package.json": [
        "env:API",
        "env:MIT"
      ],
      "node_modules/reflect.getprototypeof/package.json": [
        "env:API",
        "env:CHANGELOG",
        "env:ES2015",
        "env:ES5",
        "env:MIT",
        "env:README"
      ],
      "node_modules/regexp.prototype.flags/package.json": [
        "env:API",
        "env:CHANGELOG",
        "env:ES6",
        "env:MIT",
        "env:README"
      ],
      "node_modules/resolve/package.json": [
        "env:CONTRIBUTING",
        "env:MIT"
      ],
      "node_modules/resolve/test/resolver/multirepo/package.json": [
        "env:MIT"
      ],
      "node_modules/resolve/test/resolver/multirepo/packages/package-a/package.json": [
        "env:MIT"
      ],
      "node_modules/resolve/test/resolver/multirepo/packages/package-b/package.json": [
        "env:MIT"
      ],
      "node_modules/resolve/test/resolver/nested_symlinks/mylib/package.json": [
        "env:ISC"
      ],
      "node_modules/resolve-from/package.json": [
        "env:MIT"
      ],
      "node_modules/reusify/package.json": [
        "env:MIT"
      ],
      "node_modules/run-parallel/package.json": [
        "env:MIT"
      ],
      "node_modules/safe-array-concat/package.json": [
        "env:CHANGELOG",
        "env:MIT",
        "env:README"
      ],
      "node_modules/safe-push-apply/package.json": [
        "env:CHANGELOG",
        "env:MIT",
        "env:README"
      ],
      "node_modules/safe-regex-test/package.json": [
        "env:CHANGELOG",
        "env:MIT"
      ],
      "node_modules/scheduler/package.json": [
        "env:LICENSE",
        "env:MIT",
        "env:README"
      ],
      "node_modules/semver/package.json": [
        "env:ISC"
      ],
      "node_modules/set-function-length/.github/FUNDING.yml": [
        "env:URL"
      ],
      "node_modules/set-function-length/package.json": [
        "env:CHANGELOG",
        "env:MIT",
        "env:README"
      ],
      "node_modules/set-function-name/.github/FUNDING.yml": [
        "env:URL"
      ],
      "node_modules/set-function-name/package.json": [
        "env:CHANGELOG",
        "env:MIT",
        "env:README"
      ],
      "node_modules/set-proto/package.json": [
        "env:CHANGELOG",
        "env:MIT",
        "env:README"
      ],
      "node_modules/sharp/node_modules/semver/package.json": [
        "env:ISC"
      ],
      "node_modules/sharp/package.json": [
        "env:AVIF",
        "env:GIF",
        "env:JPEG",
        "env:PNG",
        "env:TIFF",
        "runtime:s3"
      ],
      "node_modules/shebang-command/package.json": [
        "env:MIT"
      ],
      "node_modules/shebang-regex/package.json": [
        "env:MIT"
      ],
      "node_modules/side-channel/package.json": [
        "env:CHANGELOG",
        "env:MIT"
      ],
      "node_modules/side-channel-list/package.json": [
        "env:CHANGELOG",
        "env:MIT",
        "env:README"
      ],
      "node_modules/side-channel-map/package.json": [
        "env:CHANGELOG",
        "env:MIT",
        "env:README"
      ],
      "node_modules/side-channel-weakmap/package.json": [
        "env:CHANGELOG",
        "env:MIT"
      ],
      "node_modules/source-map-js/package.json": [
        "env:BSD",
        "env:CONTRIBUTING",
        "env:README"
      ],
      "node_modules/stop-iteration-iterator/package.json": [
        "env:CHANGELOG",
        "env:MIT"
      ],
      "node_modules/string.prototype.includes/.github/workflows/publish-on-tag.yml": [
        "env:NPM_TOKEN"
      ],
      "node_modules/string.prototype.includes/.github/workflows/rebase.yml": [
        "env:GITHUB_TOKEN"
      ],
      "node_modules/string.prototype.includes/package.json": [
        "env:MIT"
      ],
      "node_modules/string.prototype.matchall/package.json": [
        "env:CHANGELOG",
        "env:ES2020",
        "env:MIT"
      ],
      "node_modules/string.prototype.repeat/package.json": [
        "env:MIT"
      ],
      "node_modules/string.prototype.trim/package.json": [
        "env:API",
        "env:CHANGELOG",
        "env:ES5",
        "env:MIT"
      ],
      "node_modules/string.prototype.trimend/package.json": [
        "env:CHANGELOG",
        "env:ES2019",
        "env:MIT"
      ],
      "node_modules/string.prototype.trimstart/package.json": [
        "env:CHANGELOG",
        "env:ES2019",
        "env:MIT"
      ],
      "node_modules/strip-json-comments/package.json": [
        "env:JSON",
        "env:MIT"
      ],
      "node_modules/styled-jsx/package.json": [
        "env:CSS",
        "env:JSX",
        "env:MIT"
      ],
      "node_modules/sucrase/package.json": [
        "env:MIT"
      ],
      "node_modules/supports-color/package.json": [
        "env:MIT"
      ],
      "node_modules/supports-preserve-symlinks-flag/package.json": [
        "env:CHANGELOG",
        "env:MIT"
      ],
      "node_modules/tailwind-merge/package.json": [
        "env:CSS",
        "env:DANYS_MACHINE",
        "env:MIT"
      ],
      "node_modules/tailwindcss/node_modules/fast-glob/node_modules/glob-parent/package.json": [
        "env:ISC",
        "env:LICENSE"
      ],
      "node_modules/tailwindcss/node_modules/fast-glob/package.json": [
        "env:MIT"
      ],
      "node_modules/tailwindcss/node_modules/resolve/package.json": [
        "env:CONTRIBUTING",
        "env:MIT"
      ],
      "node_modules/tailwindcss/node_modules/resolve/test/resolver/multirepo/package.json": [
        "env:MIT"
      ],
      "node_modules/tailwindcss/node_modules/resolve/test/resolver/multirepo/packages/package-a/package.json": [
        "env:MIT"
      ],
      "node_modules/tailwindcss/node_modules/resolve/test/resolver/multirepo/packages/package-b/package.json": [
        "env:MIT"
      ],
      "node_modules/tailwindcss/node_modules/resolve/test/resolver/nested_symlinks/mylib/package.json": [
        "env:ISC"
      ],
      "node_modules/tailwindcss/package.json": [
        "env:CSS",
        "env:CSS_TRANSFORMER_WASM",
        "env:MIT"
      ],
      "node_modules/thenify/package.json": [
        "env:MIT"
      ],
      "node_modules/thenify-all/package.json": [
        "env:MIT"
      ],
      "node_modules/tinyglobby/node_modules/fdir/package.json": [
        "env:MIT"
      ],
      "node_modules/tinyglobby/node_modules/picomatch/package.json": [
        "env:MIT",
        "env:POSIX"
      ],
      "node_modules/tinyglobby/package.json": [
        "env:MIT"
      ],
      "node_modules/to-regex-range/package.json": [
        "env:MIT"
      ],
      "node_modules/ts-api-utils/package.json": [
        "env:API",
        "env:MIT"
      ],
      "node_modules/turbo/package.json": [
        "env:MIT"
      ],
      "node_modules/turbo/schema.json": [
        "env:API",
        "env:AWS_SECRET_KEY",
        "env:CORS",
        "env:HMAC",
        "env:HTTP",
        "env:JSON",
        "env:OPTIONS",
        "env:SHA256",
        "env:TURBO_REMOTE_CACHE_SIGNATURE_KEY",
        "env:URL"
      ],
      "node_modules/type-check/package.json": [
        "env:LICENSE",
        "env:MIT",
        "env:README"
      ],
      "node_modules/typed-array-buffer/.github/FUNDING.yml": [
        "env:URL"
      ],
      "node_modules/typed-array-buffer/package.json": [
        "env:CHANGELOG",
        "env:MIT"
      ],
      "node_modules/typed-array-byte-length/package.json": [
        "env:CHANGELOG",
        "env:MIT",
        "env:README"
      ],
      "node_modules/typed-array-byte-length/tsconfig.json": [
        "env:ES2021"
      ],
      "node_modules/typed-array-byte-offset/package.json": [
        "env:CHANGELOG",
        "env:MIT",
        "env:README"
      ],
      "node_modules/typed-array-byte-offset/tsconfig.json": [
        "env:ES2021"
      ],
      "node_modules/typed-array-length/package.json": [
        "env:CHANGELOG",
        "env:MIT",
        "env:README"
      ],
      "node_modules/typed-array-length/tsconfig.json": [
        "env:ES2021"
      ],
      "node_modules/typescript/lib/cs/diagnosticMessages.generated.json": [
        "env:ALL_COMPILER_OPTIONS_6917",
        "env:AMD",
        "env:AND",
        "env:API",
        "env:ASCII",
        "env:BUILD_OPTIONS_6919",
        "env:COMMAND_LINE_FLAGS_6921",
        "env:COMMON_COMMANDS_6916",
        "env:COMMON_COMPILER_OPTIONS_6920",
        "env:CRLF",
        "env:DIRECTORY_6038",
        "env:DRUH",
        "env:ES2015",
        "env:ES2018",
        "env:ES2020",
        "env:ES2022",
        "env:ES5",
        "env:ES6",
        "env:ES7",
        "env:ESM",
        "env:FILE_6035",
        "env:FILE_OR_DIRECTORY_6040",
        "env:HTML",
        "env:JSON",
        "env:JSX",
        "env:KIND_6034",
        "env:LOCATION_6037",
        "env:NEBO",
        "env:NEWLINE_6061",
        "env:PARAMETRY",
        "env:SOUBOR",
        "env:STRATEGIE",
        "env:STRATEGY_6039",
        "env:TSC",
        "env:UMD",
        "env:URI",
        "env:URL",
        "env:UTF",
        "env:VERSION_6036",
        "env:VERZE",
        "env:WATCH_OPTIONS_6918",
        "runtime:docker"
      ],
      "node_modules/typescript/lib/de/diagnosticMessages.generated.json": [
        "env:ALLE",
        "env:ALLGEMEINE",
        "env:ALL_COMPILER_OPTIONS_6917",
        "env:AMD",
        "env:API",
        "env:ART",
        "env:ASCII",
        "env:BEFEHLE",
        "env:BEFEHLSZEILENFLAGS",
        "env:BOM",
        "env:BUILDOPTIONEN",
        "env:BUILD_OPTIONS_6919",
        "env:COMMAND_LINE_FLAGS_6921",
        "env:COMMON_COMMANDS_6916",
        "env:COMMON_COMPILER_OPTIONS_6920",
        "env:COMPILEROPTIONEN",
        "env:CPU",
        "env:CRLF",
        "env:DATEI",
        "env:DIRECTORY_6038",
        "env:DOS",
        "env:ES2015",
        "env:ES2018",
        "env:ES2020",
        "env:ES2022",
        "env:ES5",
        "env:ES6",
        "env:ES7",
        "env:ESC",
        "env:ESM",
        "env:FALSE",
        "env:FALSY",
        "env:FILE_6035",
        "env:FILE_OR_DIRECTORY_6040",
        "env:GET",
        "env:HTML",
        "env:JSON",
        "env:JSX",
        "env:KIND_6034",
        "env:LOCATION_6037",
        "env:MAP",
        "env:NEUE",
        "env:NEWLINE_6061",
        "env:NULL",
        "env:NULLISH",
        "env:ODER",
        "env:REST",
        "env:SET",
        "env:SPEICHERORT",
        "env:STRATEGIE",
        "env:STRATEGY_6039",
        "env:TRUE",
        "env:TRUTHY",
        "env:TSBUILDINFO",
        "env:UMD",
        "env:URI",
        "env:URL",
        "env:UTF",
        "env:VERSION",
        "env:VERSION_6036",
        "env:VERZEICHNIS",
        "env:WATCH_OPTIONS_6918",
        "env:ZEILE",
        "runtime:docker",
        "runtime:kubernetes"
      ],
      "node_modules/typescript/lib/es/diagnosticMessages.generated.json": [
        "env:ALL_COMPILER_OPTIONS_6917",
        "env:AMD",
        "env:API",
        "env:ARCHIVO",
        "env:ASCII",
        "env:BOM",
        "env:BUILD_OPTIONS_6919",
        "env:COMANDOS",
        "env:COMMAND_LINE_FLAGS_6921",
        "env:COMMON_COMMANDS_6916",
        "env:COMMON_COMPILER_OPTIONS_6920",
        "env:COMPILADOR",
        "env:COMUNES",
        "env:CPU",
        "env:CRLF",
        "env:CTS",
        "env:DEL",
        "env:DIRECTORIO",
        "env:DIRECTORY_6038",
        "env:ES2015",
        "env:ES2018",
        "env:ES2020",
        "env:ES2022",
        "env:ES5",
        "env:ES6",
        "env:ES7",
        "env:ESM",
        "env:ESTRATEGIA",
        "env:FILE_6035",
        "env:FILE_OR_DIRECTORY_6040",
        "env:HTML",
        "env:JSON",
        "env:JSX",
        "env:KIND_6034",
        "env:LAS",
        "env:LOCATION_6037",
        "env:MARCAS",
        "env:NEWLINE_6061",
        "env:NUEVA",
        "env:NULL",
        "env:OPCIONES",
        "env:REST",
        "env:STRATEGY_6039",
        "env:STRICT",
        "env:TIPO",
        "env:TODAS",
        "env:UMD",
        "env:URI",
        "env:URL",
        "env:UTF",
        "env:VERSION_6036",
        "env:WATCH_OPTIONS_6918",
        "runtime:docker"
      ],
      "node_modules/typescript/lib/fr/diagnosticMessages.generated.json": [
        "env:ALL_COMPILER_OPTIONS_6917",
        "env:AMD",
        "env:API",
        "env:ASCII",
        "env:BOM",
        "env:BUILD",
        "env:BUILD_OPTIONS_6919",
        "env:COMMANDE",
        "env:COMMANDES",
        "env:COMMAND_LINE_FLAGS_6921",
        "env:COMMON_COMMANDS_6916",
        "env:COMMON_COMPILER_OPTIONS_6920",
        "env:COMPILATEUR",
        "env:COURANTES",
        "env:CRLF",
        "env:DIRECTORY_6038",
        "env:EMPLACEMENT",
        "env:ES2015",
        "env:ES2018",
        "env:ES2020",
        "env:ES2022",
        "env:ES5",
        "env:ES6",
        "env:ES7",
        "env:ESM",
        "env:FICHIER",
        "env:FILE_6035",
        "env:FILE_OR_DIRECTORY_6040",
        "env:GENRE",
        "env:HTML",
        "env:INDICATEURS",
        "env:JSON",
        "env:JSX",
        "env:KIND_6034",
        "env:LES",
        "env:LIGNE",
        "env:LOCATION_6037",
        "env:NEWLINE_6061",
        "env:NOUVELLE",
        "env:OBSERVATION",
        "env:OPTIONS",
        "env:REST",
        "env:STRATEGY_6039",
        "env:TOUTES",
        "env:UMD",
        "env:URI",
        "env:URL",
        "env:UTF",
        "env:VERSION",
        "env:VERSION_6036",
        "env:WATCH_OPTIONS_6918",
        "runtime:docker"
      ],
      "node_modules/typescript/lib/it/diagnosticMessages.generated.json": [
        "env:ALL_COMPILER_OPTIONS_6917",
        "env:AMD",
        "env:AND",
        "env:API",
        "env:ASCII",
        "env:BOM",
        "env:BUILD_OPTIONS_6919",
        "env:COMANDI",
        "env:COMANDO",
        "env:COMMAND_LINE_FLAGS_6921",
        "env:COMMON_COMMANDS_6916",
        "env:COMMON_COMPILER_OPTIONS_6920",
        "env:COMPILATORE",
        "env:COMPILAZIONE",
        "env:COMUNI",
        "env:CONTROLLO",
        "env:CPU",
        "env:CRLF",
        "env:CTS",
        "env:DEL",
        "env:DELL",
        "env:DELLA",
        "env:DIRECTORY",
        "env:DIRECTORY_6038",
        "env:DOS",
        "env:ES2015",
        "env:ES2018",
        "env:ES2020",
        "env:ES2022",
        "env:ES5",
        "env:ES6",
        "env:ES7",
        "env:ESM",
        "env:ESPRESSIONE",
        "env:FILE",
        "env:FILE_6035",
        "env:FILE_OR_DIRECTORY_6040",
        "env:FLAG",
        "env:GLOB",
        "env:HTML",
        "env:JSON",
        "env:JSX",
        "env:KIND_6034",
        "env:LOCATION_6037",
        "env:MTS",
        "env:NEWLINE_6061",
        "env:NUOVA",
        "env:OPZIONI",
        "env:PERCORSO",
        "env:REST",
        "env:RIGA",
        "env:STRATEGIA",
        "env:STRATEGY_6039",
        "env:TIPOLOGIA",
        "env:TUTTE",
        "env:UMD",
        "env:UNIX",
        "env:URI",
        "env:URL",
        "env:UTF",
        "env:VERSIONE",
        "env:VERSION_6036",
        "env:WATCH_OPTIONS_6918",
        "runtime:docker"
      ],
      "node_modules/typescript/lib/ja/diagnosticMessages.generated.json": [
        "env:ALL_COMPILER_OPTIONS_6917",
        "env:AMD",
        "env:AND",
        "env:API",
        "env:ASCII",
        "env:BOM",
        "env:BUILD_OPTIONS_6919",
        "env:COMMAND_LINE_FLAGS_6921",
        "env:COMMON_COMMANDS_6916",
        "env:COMMON_COMPILER_OPTIONS_6920",
        "env:CPU",
        "env:CRLF",
        "env:DIRECTORY_6038",
        "env:ES2015",
        "env:ES2018",
        "env:ES2020",
        "env:ES2022",
        "env:ES5",
        "env:ES6",
        "env:ES7",
        "env:ESM",
        "env:FILE_6035",
        "env:FILE_OR_DIRECTORY_6040",
        "env:HTML",
        "env:JSON",
        "env:JSX",
        "env:KIND_6034",
        "env:LOCATION_6037",
        "env:NEWLINE_6061",
        "env:NULL",
        "env:STRATEGY_6039",
        "env:UMD",
        "env:URI",
        "env:URL",
        "env:UTF",
        "env:VERSION_6036",
        "env:WATCH_OPTIONS_6918",
        "runtime:docker"
      ],
      "node_modules/typescript/lib/ko/diagnosticMessages.generated.json": [
        "env:ALL_COMPILER_OPTIONS_6917",
        "env:AMD",
        "env:AND",
        "env:ASCII",
        "env:BOM",
        "env:BUILD_OPTIONS_6919",
        "env:COMMAND_LINE_FLAGS_6921",
        "env:COMMON_COMMANDS_6916",
        "env:COMMON_COMPILER_OPTIONS_6920",
        "env:CPU",
        "env:CRLF",
        "env:DIRECTORY_6038",
        "env:ES2015",
        "env:ES2018",
        "env:ES2020",
        "env:ES2022",
        "env:ES5",
        "env:ES6",
        "env:ES7",
        "env:ESM",
        "env:FILE_6035",
        "env:FILE_OR_DIRECTORY_6040",
        "env:GLOB",
        "env:HTML",
        "env:JSON",
        "env:JSX",
        "env:KIND",
        "env:KIND_6034",
        "env:LOCATION_6037",
        "env:NEWLINE_6061",
        "env:REST",
        "env:STRATEGY_6039",
        "env:UMD",
        "env:URL",
        "env:UTF",
        "env:VERSION_6036",
        "env:WATCH_OPTIONS_6918",
        "runtime:docker"
      ],
      "node_modules/typescript/lib/pl/diagnosticMessages.generated.json": [
        "env:ALL_COMPILER_OPTIONS_6917",
        "env:AMD",
        "env:API",
        "env:ASCII",
        "env:BUILD_OPTIONS_6919",
        "env:COMMAND_LINE_FLAGS_6921",
        "env:COMMON_COMMANDS_6916",
        "env:COMMON_COMPILER_OPTIONS_6920",
        "env:CPU",
        "env:CRLF",
        "env:CTS",
        "env:DIRECTORY_6038",
        "env:ES2015",
        "env:ES2018",
        "env:ES2020",
        "env:ES2022",
        "env:ES5",
        "env:ES6",
        "env:ES7",
        "env:ESM",
        "env:FILE_6035",
        "env:FILE_OR_DIRECTORY_6040",
        "env:FLAGI",
        "env:HTML",
        "env:JSON",
        "env:JSX",
        "env:KATALOG",
        "env:KIND_6034",
        "env:KOMPILACJI",
        "env:KOMPILATORA",
        "env:LOCATION_6037",
        "env:LOKALIZACJA",
        "env:LUB",
        "env:MTS",
        "env:NEWLINE_6061",
        "env:NOWY",
        "env:OBSERWACJI",
        "env:OPCJE",
        "env:ORAZ",
        "env:PLIK",
        "env:POLECENIA",
        "env:REST",
        "env:RODZAJ",
        "env:STRATEGIA",
        "env:STRATEGY_6039",
        "env:TYPOWE",
        "env:UMD",
        "env:URI",
        "env:URL",
        "env:UTF",
        "env:VERSION_6036",
        "env:WATCH_OPTIONS_6918",
        "env:WERSJA",
        "env:WIERSZ",
        "env:WIERSZA",
        "env:WSZYSTKIE",
        "runtime:docker",
        "runtime:kubernetes"
      ],
      "node_modules/typescript/lib/pt-br/diagnosticMessages.generated.json": [
        "env:ALL_COMPILER_OPTIONS_6917",
        "env:AMD",
        "env:API",
        "env:ARQUIVO",
        "env:ASCII",
        "env:BOM",
        "env:BUILD",
        "env:BUILD_OPTIONS_6919",
        "env:COMANDO",
        "env:COMANDOS",
        "env:COMMAND_LINE_FLAGS_6921",
        "env:COMMON_COMMANDS_6916",
        "env:COMMON_COMPILER_OPTIONS_6920",
        "env:COMPILADOR",
        "env:COMUNS",
        "env:CPU",
        "env:CRLF",
        "env:DIRECTORY_6038",
        "env:ES2015",
        "env:ES2018",
        "env:ES2020",
        "env:ES2022",
        "env:ES5",
        "env:ES6",
        "env:ES7",
        "env:ESM",
        "env:FILE_6035",
        "env:FILE_OR_DIRECTORY_6040",
        "env:HTML",
        "env:JSON",
        "env:JSX",
        "env:KIND_6034",
        "env:LINHA",
        "env:LOCAL",
        "env:LOCATION_6037",
        "env:NEWLINE",
        "env:NEWLINE_6061",
        "env:REST",
        "env:SINALIZADORES",
        "env:STRATEGY_6039",
        "env:TIPO",
        "env:TODAS",
        "env:UMD",
        "env:URI",
        "env:URL",
        "env:UTF",
        "env:VERSION_6036",
        "env:WATCH_OPTIONS_6918",
        "runtime:docker"
      ],
      "node_modules/typescript/lib/ru/diagnosticMessages.generated.json": [
        "env:ALL_COMPILER_OPTIONS_6917",
        "env:AMD",
        "env:API",
        "env:ASCII",
        "env:BUILD_OPTIONS_6919",
        "env:COMMAND_LINE_FLAGS_6921",
        "env:COMMON_COMMANDS_6916",
        "env:COMMON_COMPILER_OPTIONS_6920",
        "env:CRLF",
        "env:CTS",
        "env:DIRECTORY_6038",
        "env:DOS",
        "env:ES2015",
        "env:ES2018",
        "env:ES2020",
        "env:ES2022",
        "env:ES5",
        "env:ES6",
        "env:ES7",
        "env:ESM",
        "env:FILE_6035",
        "env:FILE_OR_DIRECTORY_6040",
        "env:HTML",
        "env:JSON",
        "env:JSX",
        "env:KIND_6034",
        "env:LOCATION_6037",
        "env:MTS",
        "env:NEWLINE_6061",
        "env:NULL",
        "env:REST",
        "env:STRATEGY_6039",
        "env:TSBUILDINFO",
        "env:TSC",
        "env:UMD",
        "env:UNIX",
        "env:URI",
        "env:URL",
        "env:UTF",
        "env:VERSION_6036",
        "env:WATCH_OPTIONS_6918",
        "runtime:docker"
      ],
      "node_modules/typescript/lib/tr/diagnosticMessages.generated.json": [
        "env:ALL_COMPILER_OPTIONS_6917",
        "env:AMD",
        "env:API",
        "env:ASCII",
        "env:BAYRAKLARI",
        "env:BOM",
        "env:BUILD_OPTIONS_6919",
        "env:COMMAND_LINE_FLAGS_6921",
        "env:COMMON_COMMANDS_6916",
        "env:COMMON_COMPILER_OPTIONS_6920",
        "env:CPU",
        "env:CRLF",
        "env:DERLEME",
        "env:DIRECTORY_6038",
        "env:DOSYA",
        "env:DRY",
        "env:ES2015",
        "env:ES2018",
        "env:ES2020",
        "env:ES2022",
        "env:ES5",
        "env:ES6",
        "env:ES7",
        "env:ESM",
        "env:FILE_6035",
        "env:FILE_OR_DIRECTORY_6040",
        "env:HTML",
        "env:JSON",
        "env:JSX",
        "env:KIND_6034",
        "env:KOMUT",
        "env:KOMUTLAR",
        "env:KONUM",
        "env:LOCATION_6037",
        "env:NEWLINE_6061",
        "env:ORTAK",
        "env:REST",
        "env:SATIR",
        "env:SATIRI",
        "env:STRATEGY_6039",
        "env:UMD",
        "env:URI",
        "env:UTF",
        "env:VERSION_6036",
        "env:VEYA",
        "env:WATCH_OPTIONS_6918",
        "runtime:docker",
        "runtime:kubernetes"
      ],
      "node_modules/typescript/lib/typesMap.json": [
        "env:ES6",
        "env:SAT",
        "env:UUID",
        "runtime:redis"
      ],
      "node_modules/typescript/lib/zh-cn/diagnosticMessages.generated.json": [
        "env:ALL_COMPILER_OPTIONS_6917",
        "env:AMD",
        "env:AND",
        "env:API",
        "env:ASCII",
        "env:BOM",
        "env:BUILD_OPTIONS_6919",
        "env:COMMAND_LINE_FLAGS_6921",
        "env:COMMON_COMMANDS_6916",
        "env:COMMON_COMPILER_OPTIONS_6920",
        "env:CPU",
        "env:CRLF",
        "env:DIRECTORY_6038",
        "env:ES2015",
        "env:ES2018",
        "env:ES2020",
        "env:ES2022",
        "env:ES5",
        "env:ES6",
        "env:ES7",
        "env:ESM",
        "env:FILE_6035",
        "env:FILE_OR_DIRECTORY_6040",
        "env:HTML",
        "env:JSON",
        "env:JSX",
        "env:KIND_6034",
        "env:LOCATION_6037",
        "env:NEWLINE_6061",
        "env:NULL",
        "env:STRATEGY_6039",
        "env:UMD",
        "env:URI",
        "env:URL",
        "env:UTF",
        "env:VERSION_6036",
        "env:WATCH_OPTIONS_6918",
        "runtime:docker"
      ],
      "node_modules/typescript/lib/zh-tw/diagnosticMessages.generated.json": [
        "env:ALL_COMPILER_OPTIONS_6917",
        "env:AMD",
        "env:AND",
        "env:API",
        "env:ASCII",
        "env:BOM",
        "env:BUILD_OPTIONS_6919",
        "env:COMMAND_LINE_FLAGS_6921",
        "env:COMMON_COMMANDS_6916",
        "env:COMMON_COMPILER_OPTIONS_6920",
        "env:CPU",
        "env:CRLF",
        "env:DIRECTORY_6038",
        "env:DOS",
        "env:DRY",
        "env:ES2015",
        "env:ES2018",
        "env:ES2020",
        "env:ES2022",
        "env:ES5",
        "env:ES6",
        "env:ES7",
        "env:ESM",
        "env:FILE_6035",
        "env:FILE_OR_DIRECTORY_6040",
        "env:HTML",
        "env:JSON",
        "env:JSX",
        "env:KIND_6034",
        "env:LOCATION_6037",
        "env:NEWLINE_6061",
        "env:REST",
        "env:STRATEGY_6039",
        "env:UMD",
        "env:UNIX",
        "env:URI",
        "env:URL",
        "env:UTF",
        "env:VERSION_6036",
        "env:WATCH_OPTIONS_6918",
        "runtime:docker"
      ],
      "node_modules/typescript/package.json": [
        "env:LICENSE",
        "env:README",
        "env:SECURITY"
      ],
      "node_modules/typescript-eslint/package.json": [
        "env:LICENSE",
        "env:MIT",
        "env:README"
      ],
      "node_modules/unbox-primitive/package.json": [
        "env:CHANGELOG",
        "env:MIT"
      ],
      "node_modules/uncrypto/package.json": [
        "env:API",
        "env:MIT"
      ],
      "node_modules/undici-types/package.json": [
        "env:MIT"
      ],
      "node_modules/update-browserslist-db/package.json": [
        "env:CLI",
        "env:MIT"
      ],
      "node_modules/uri-js/package.json": [
        "env:BSD",
        "env:CHANGELOG",
        "env:HTTP",
        "env:HTTPS",
        "env:IDN",
        "env:IRI",
        "env:LICENSE",
        "env:MAILTO",
        "env:README",
        "env:RFC",
        "env:RFC2141",
        "env:RFC2616",
        "env:RFC2818",
        "env:RFC3986",
        "env:RFC3987",
        "env:RFC4122",
        "env:RFC4291",
        "env:RFC5891",
        "env:RFC5952",
        "env:RFC6068",
        "env:RFC6455",
        "env:RFC6874",
        "env:URI",
        "env:URN",
        "env:UUID",
        "env:WSS"
      ],
      "node_modules/use-callback-ref/package.json": [
        "env:CHANGELOG",
        "env:MIT"
      ],
      "node_modules/use-sidecar/package.json": [
        "env:CHANGELOG",
        "env:MIT"
      ],
      "node_modules/use-sync-external-store/package.json": [
        "env:LICENSE",
        "env:MIT",
        "env:README"
      ],
      "node_modules/util-deprecate/package.json": [
        "env:MIT"
      ],
      "node_modules/web-vitals/package.json": [
        "env:CLS",
        "env:FCP",
        "env:INP",
        "env:LCP",
        "env:TTFB"
      ],
      "node_modules/which/package.json": [
        "env:CHANGELOG",
        "env:ISC",
        "env:PATH"
      ],
      "node_modules/which-boxed-primitive/package.json": [
        "env:CHANGELOG",
        "env:MIT"
      ],
      "node_modules/which-boxed-primitive/tsconfig.json": [
        "env:ES2021"
      ],
      "node_modules/which-builtin-type/package.json": [
        "env:CHANGELOG",
        "env:MIT",
        "env:README"
      ],
      "node_modules/which-builtin-type/tsconfig.json": [
        "env:ES2021"
      ],
      "node_modules/which-collection/package.json": [
        "env:CHANGELOG",
        "env:MIT",
        "runtime:kubernetes"
      ],
      "node_modules/which-typed-array/package.json": [
        "env:CHANGELOG",
        "env:ES6",
        "env:MIT"
      ],
      "node_modules/word-wrap/package.json": [
        "env:MIT"
      ],
      "node_modules/yocto-queue/package.json": [
        "env:MIT"
      ],
      "package-lock.json": [
        "env:AND",
        "env:B4RT",
        "env:BSD",
        "env:CC0",
        "env:G3ZA",
        "env:G5KYP6",
        "env:IICI",
        "env:ISC",
        "env:JTF99U",
        "env:KIN",
        "env:L7G8",
        "env:LGPL",
        "env:LHE",
        "env:LICENSE",
        "env:LL8E",
        "env:MFQ",
        "env:MIT",
        "env:MPL",
        "env:O2XJB",
        "env:PAJLD1I",
        "env:PB7X",
        "env:PKQ",
        "env:SEE",
        "env:SU5",
        "env:T4IS",
        "env:TER",
        "env:THO",
        "env:VJH",
        "env:VOS",
        "env:WPS",
        "env:YNEFAF",
        "env:YNV",
        "env:YZA",
        "runtime:kubernetes",
        "runtime:s3"
      ],
      "packages/config/tsconfig.base.json": [
        "env:ES2022"
      ],
      "packages/db/alembic.ini": [
        "env:INFO",
        "env:NOTSET",
        "env:WARN"
      ],
      "pyproject.toml": [
        "env:LICENSE",
        "env:MIT",
        "env:OSI",
        "env:README",
        "runtime:postgres",
        "runtime:redis"
      ],
      "skilgen.yml": [
        "env:OPENAI_API_KEY"
      ]
    },
    "test_mapping": {
      "tests/__init__.py": [
        "skilgen/__init__.py",
        "skilgen/agents/__init__.py",
        "skilgen/api/__init__.py",
        "skilgen/cli/__init__.py",
        "skilgen/core/__init__.py",
        "skilgen/generators/__init__.py"
      ],
      "tests/test_analytics.py": [
        "skilgen/core/analytics.py"
      ],
      "tests/test_api_smoke.py": [
        "scripts/deploy_api.py",
        "skilgen/api/__init__.py",
        "skilgen/api/jobs.py",
        "skilgen/api/server.py",
        "skilgen/api/service.py"
      ],
      "tests/test_architecture_cli.py": [
        "skilgen/agents/architecture_planner.py",
        "skilgen/cli/__init__.py",
        "skilgen/cli/main.py"
      ],
      "tests/test_architecture_planner.py": [
        "skilgen/agents/architecture_planner.py",
        "skilgen/agents/decision_planner.py",
        "skilgen/agents/domain_graph_planner.py",
        "skilgen/agents/roadmap_planner.py"
      ],
      "tests/test_audit.py": [
        "skilgen/core/audit.py"
      ],
      "tests/test_auth_claim_mapping.py": [
        "skilgen/core/auth_tokens.py"
      ],
      "tests/test_auth_tokens.py": [
        "skilgen/core/auth_tokens.py"
      ],
      "tests/test_autoupdate.py": [
        "skilgen/autoupdate.py"
      ],
      "tests/test_cli.py": [
        "skilgen/cli/__init__.py",
        "skilgen/cli/main.py"
      ],
      "tests/test_codebase_signals.py": [
        "skilgen/agents/codebase_signals.py",
        "skilgen/core/runtime_signals.py"
      ],
      "tests/test_config.py": [
        "skilgen/core/config.py"
      ],
      "tests/test_context.py": [
        "skilgen/core/context.py"
      ],
      "tests/test_corpus_cli.py": [
        "skilgen/cli/__init__.py",
        "skilgen/cli/main.py",
        "skilgen/core/corpus_index.py"
      ],
      "tests/test_corpus_index.py": [
        "skilgen/core/corpus_index.py"
      ],
      "tests/test_dashboard_cli.py": [
        "scripts/deploy_dashboard.py",
        "skilgen/cli/__init__.py",
        "skilgen/cli/main.py"
      ],
      "tests/test_decision_planner.py": [
        "skilgen/agents/decision_planner.py",
        "skilgen/agents/architecture_planner.py",
        "skilgen/agents/domain_graph_planner.py",
        "skilgen/agents/roadmap_planner.py"
      ],
      "tests/test_delivery.py": [
        "skilgen/delivery.py"
      ],
      "tests/test_dependency_risk.py": [
        "skilgen/core/dependency_risk.py"
      ],
      "tests/test_dependency_risk_graph_workstream.py": [
        "skilgen/core/dependency_risk.py",
        "skilgen/agents/domain_graph_planner.py",
        "skilgen/agents/evidence_graph.py",
        "skilgen/agents/workspace_graph.py"
      ],
      "tests/test_diff.py": [
        "skilgen/core/diff.py"
      ],
      "tests/test_document_ingestion.py": [
        "skilgen/core/document_ingestion.py"
      ],
      "tests/test_domain_graph_planner.py": [
        "skilgen/agents/domain_graph_planner.py",
        "skilgen/agents/architecture_planner.py",
        "skilgen/agents/decision_planner.py",
        "skilgen/agents/evidence_graph.py",
        "skilgen/agents/roadmap_planner.py",
        "skilgen/agents/workspace_graph.py"
      ],
      "tests/test_enterprise_document_formats.py": [
        "skilgen/core/document_ingestion.py",
        "skilgen/core/enterprise_policy.py",
        "skilgen/enterprise_skills.py"
      ],
      "tests/test_enterprise_policy_cli.py": [
        "skilgen/core/enterprise_policy.py",
        "skilgen/cli/__init__.py",
        "skilgen/cli/main.py",
        "skilgen/core/identity_policy_store.py",
        "skilgen/enterprise_skills.py"
      ],
      "tests/test_feature_extractor.py": [
        "skilgen/agents/feature_extractor.py"
      ],
      "tests/test_framework_fingerprint.py": [
        "skilgen/agents/framework_fingerprint.py"
      ],
      "tests/test_identity_policy_store.py": [
        "skilgen/core/identity_policy_store.py",
        "skilgen/core/enterprise_policy.py",
        "skilgen/core/rate_limit_store.py"
      ],
      "tests/test_jobs.py": [
        "skilgen/api/jobs.py"
      ],
      "tests/test_model_registry.py": [
        "skilgen/agents/model_registry.py",
        "skilgen/registry_client.py"
      ],
      "tests/test_overview_data.py": [
        "skilgen/core/runtime_data.py"
      ],
      "tests/test_plan_cli.py": [
        "skilgen/cli/__init__.py",
        "skilgen/cli/main.py"
      ],
      "tests/test_rate_limit_store.py": [
        "skilgen/core/rate_limit_store.py",
        "skilgen/core/identity_policy_store.py"
      ],
      "tests/test_registry_api.py": [
        "scripts/deploy_api.py",
        "skilgen/agents/model_registry.py",
        "skilgen/api/__init__.py",
        "skilgen/api/jobs.py",
        "skilgen/api/server.py",
        "skilgen/api/service.py"
      ],
      "tests/test_registry_cli.py": [
        "skilgen/agents/model_registry.py",
        "skilgen/cli/__init__.py",
        "skilgen/cli/main.py",
        "skilgen/registry_client.py"
      ],
      "tests/test_registry_dashboard.py": [
        "scripts/deploy_dashboard.py",
        "skilgen/agents/model_registry.py",
        "skilgen/registry_client.py"
      ],
      "tests/test_relationship_mapper.py": [
        "skilgen/agents/relationship_mapper.py"
      ],
      "tests/test_requirements.py": [
        "scripts/run_requirements_pipeline.py",
        "skilgen/agents/requirements_parser.py",
        "skilgen/core/requirements.py"
      ],
      "tests/test_requirements_parser.py": [
        "skilgen/agents/requirements_parser.py",
        "scripts/run_requirements_pipeline.py",
        "skilgen/core/requirements.py"
      ],
      "tests/test_roadmap_planner.py": [
        "skilgen/agents/roadmap_planner.py",
        "skilgen/agents/architecture_planner.py",
        "skilgen/agents/decision_planner.py",
        "skilgen/agents/domain_graph_planner.py"
      ],
      "tests/test_roadmap_skills.py": [
        "skilgen/agents/roadmap_planner.py",
        "skilgen/enterprise_skills.py",
        "skilgen/external_skills.py",
        "skilgen/generators/skills.py"
      ],
      "tests/test_run_memory.py": [
        "skilgen/core/run_memory.py",
        "scripts/run_requirements_pipeline.py",
        "skilgen/core/project_memory.py"
      ],
      "tests/test_runtime_hardening.py": [
        "skilgen/core/runtime_data.py",
        "skilgen/core/runtime_signals.py",
        "skilgen/deep_agents_runtime.py"
      ],
      "tests/test_runtime_signals.py": [
        "skilgen/core/runtime_signals.py",
        "skilgen/agents/codebase_signals.py",
        "skilgen/core/runtime_data.py",
        "skilgen/deep_agents_runtime.py"
      ],
      "tests/test_score.py": [
        "skilgen/core/score.py"
      ],
      "tests/test_score_quality_system.py": [
        "skilgen/core/score.py"
      ],
      "tests/test_sdk.py": [
        "skilgen/sdk.py"
      ],
      "tests/test_skill_usage_analytics.py": [
        "skilgen/core/analytics.py"
      ],
      "tests/test_skillayer_api_infra.py": [
        "scripts/deploy_api.py",
        "skilgen/api/__init__.py",
        "skilgen/api/jobs.py",
        "skilgen/api/server.py",
        "skilgen/api/service.py"
      ],
      "tests/test_source_graphs.py": [
        "skilgen/agents/source_graphs.py"
      ],
      "tests/test_validate_cli.py": [
        "skilgen/cli/__init__.py",
        "skilgen/cli/main.py"
      ],
      "tests/test_vercel_api_deploy.py": [
        "scripts/deploy_api.py",
        "scripts/deploy_dashboard.py",
        "skilgen/api/__init__.py",
        "skilgen/api/jobs.py",
        "skilgen/api/server.py",
        "skilgen/api/service.py"
      ],
      "tests/test_vercel_dashboard_deploy.py": [
        "scripts/deploy_dashboard.py",
        "scripts/deploy_api.py"
      ],
      "tests/test_workspace_graph.py": [
        "skilgen/agents/workspace_graph.py",
        "skilgen/agents/domain_graph_planner.py",
        "skilgen/agents/evidence_graph.py"
      ]
    },
    "workspace_graph": {
      "tool": "turbo",
      "packages": [
        {
          "id": "apps-dashboard",
          "name": "skillayer-dashboard",
          "root_path": "apps/dashboard",
          "package_type": null,
          "manifest_paths": [
            "apps/dashboard/package.json"
          ],
          "config_evidence": [
            "apps/dashboard/package.json",
            "turbo.json"
          ]
        },
        {
          "id": "apps-web",
          "name": "skillayer-web",
          "root_path": "apps/web",
          "package_type": "app",
          "manifest_paths": [
            "apps/web/package.json"
          ],
          "config_evidence": [
            "apps/web/package.json",
            "turbo.json"
          ]
        },
        {
          "id": "packages-config",
          "name": "@skillayer/config",
          "root_path": "packages/config",
          "package_type": "library",
          "manifest_paths": [
            "packages/config/package.json"
          ],
          "config_evidence": [
            "packages/config/package.json",
            "turbo.json"
          ]
        },
        {
          "id": "packages-db",
          "name": "@skillayer/db",
          "root_path": "packages/db",
          "package_type": "library",
          "manifest_paths": [
            "packages/db/package.json"
          ],
          "config_evidence": [
            "packages/db/package.json",
            "turbo.json"
          ]
        },
        {
          "id": "packages-types",
          "name": "@skillayer/types",
          "root_path": "packages/types",
          "package_type": "library",
          "manifest_paths": [
            "packages/types/package.json"
          ],
          "config_evidence": [
            "packages/types/package.json",
            "turbo.json"
          ]
        },
        {
          "id": "packages-ui",
          "name": "@skillayer/ui",
          "root_path": "packages/ui",
          "package_type": "library",
          "manifest_paths": [
            "packages/ui/package.json"
          ],
          "config_evidence": [
            "packages/ui/package.json",
            "turbo.json"
          ]
        }
      ],
      "dependencies": [
        {
          "source": "apps-dashboard",
          "target": "packages-config",
          "evidence": [
            "apps/dashboard/package.json:@skillayer/config"
          ]
        },
        {
          "source": "apps-dashboard",
          "target": "packages-types",
          "evidence": [
            "apps/dashboard/package.json:@skillayer/types"
          ]
        },
        {
          "source": "apps-dashboard",
          "target": "packages-ui",
          "evidence": [
            "apps/dashboard/package.json:@skillayer/ui"
          ]
        },
        {
          "source": "apps-web",
          "target": "packages-config",
          "evidence": [
            "apps/web/package.json:@skillayer/config"
          ]
        },
        {
          "source": "apps-web",
          "target": "packages-types",
          "evidence": [
            "apps/web/package.json:@skillayer/types"
          ]
        },
        {
          "source": "apps-web",
          "target": "packages-ui",
          "evidence": [
            "apps/web/package.json:@skillayer/ui"
          ]
        },
        {
          "source": "packages-types",
          "target": "packages-config",
          "evidence": [
            "packages/types/package.json:@skillayer/config"
          ]
        },
        {
          "source": "packages-ui",
          "target": "packages-config",
          "evidence": [
            "packages/ui/package.json:@skillayer/config"
          ]
        }
      ],
      "entrypoints": [
        "apps-dashboard",
        "apps-web"
      ],
      "confidence": 0.92,
      "detection_evidence": [
        "turbo.json"
      ]
    },
    "symbol_relationships": [
      {
        "source_path": "skilgen/api/jobs.py",
        "source_symbol": "JobCancelledError",
        "relationship": "extends",
        "target_symbol": "RuntimeError",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "skilgen/api/server.py",
        "source_symbol": "BoundedThreadPoolHTTPServer",
        "relationship": "extends",
        "target_symbol": "HTTPServer",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "skilgen/api/server.py",
        "source_symbol": "JsonFormatter",
        "relationship": "extends",
        "target_symbol": "logging.Formatter",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "skilgen/api/server.py",
        "source_symbol": "SkilgenHandler",
        "relationship": "extends",
        "target_symbol": "BaseHTTPRequestHandler",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "skilgen/core/auth_tokens.py",
        "source_symbol": "SignedTokenError",
        "relationship": "extends",
        "target_symbol": "ValueError",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "skilgen/registry_client.py",
        "source_symbol": "RegistryClientError",
        "relationship": "extends",
        "target_symbol": "RuntimeError",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/oidc_test_utils.py",
        "source_symbol": "Handler",
        "relationship": "extends",
        "target_symbol": "BaseHTTPRequestHandler",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_analytics.py",
        "source_symbol": "AnalyticsTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_api_smoke.py",
        "source_symbol": "ApiSmokeTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_architecture_cli.py",
        "source_symbol": "ArchitectureCliTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_architecture_planner.py",
        "source_symbol": "ArchitecturePlannerTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_audit.py",
        "source_symbol": "AuditTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_auth_claim_mapping.py",
        "source_symbol": "OidcClaimMappingTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_auth_tokens.py",
        "source_symbol": "SignedTokenTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_autoupdate.py",
        "source_symbol": "AutoUpdateTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_cli.py",
        "source_symbol": "CliTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_codebase_signals.py",
        "source_symbol": "CodebaseSignalsTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_config.py",
        "source_symbol": "ConfigTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_context.py",
        "source_symbol": "ContextTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_corpus_cli.py",
        "source_symbol": "CorpusCliTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_corpus_index.py",
        "source_symbol": "CorpusIndexTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_dashboard_cli.py",
        "source_symbol": "DashboardCliTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_decision_planner.py",
        "source_symbol": "DecisionPlannerTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_delivery.py",
        "source_symbol": "DeliveryTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_dependency_risk.py",
        "source_symbol": "DependencyRiskTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_diff.py",
        "source_symbol": "DiffTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_document_ingestion.py",
        "source_symbol": "DocumentIngestionTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_domain_graph_planner.py",
        "source_symbol": "DomainGraphPlannerTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_enterprise_document_formats.py",
        "source_symbol": "EnterpriseDocumentFormatTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_feature_extractor.py",
        "source_symbol": "FeatureExtractorTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_framework_fingerprint.py",
        "source_symbol": "FrameworkFingerprintTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_identity_policy_store.py",
        "source_symbol": "IdentityPolicyStoreTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_jobs.py",
        "source_symbol": "JobPersistenceTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_model_registry.py",
        "source_symbol": "ModelRegistryTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_packaging.py",
        "source_symbol": "PackagingTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_plan_cli.py",
        "source_symbol": "PlanCliTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_pr_comment.py",
        "source_symbol": "PrCommentTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_rate_limit_store.py",
        "source_symbol": "RateLimitStoreTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_registry_cli.py",
        "source_symbol": "RegistryCliTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_registry_cli.py",
        "source_symbol": "Handler",
        "relationship": "extends",
        "target_symbol": "BaseHTTPRequestHandler",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_relationship_mapper.py",
        "source_symbol": "RelationshipMapperTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_requirements.py",
        "source_symbol": "RequirementsTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_requirements_parser.py",
        "source_symbol": "RequirementsParserTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_roadmap_planner.py",
        "source_symbol": "RoadmapPlannerTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_roadmap_skills.py",
        "source_symbol": "RoadmapSkillsTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_run_memory.py",
        "source_symbol": "RunMemoryTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_runtime_hardening.py",
        "source_symbol": "RuntimeHardeningTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_runtime_signals.py",
        "source_symbol": "RuntimeSignalsTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_score.py",
        "source_symbol": "ScoreTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_sdk.py",
        "source_symbol": "SdkTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_source_graphs.py",
        "source_symbol": "SourceGraphTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_upgrade_flow.py",
        "source_symbol": "UpgradeFlowTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_validate_cli.py",
        "source_symbol": "ValidateCliTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_workspace_graph.py",
        "source_symbol": "WorkspaceGraphTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      }
    ],
    "runtime_signals": {
      "artifacts": [
        {
          "path": ".vercel/output/diagnostics/cli_traces.json",
          "kind": "traces",
          "format": "json",
          "signal_count": 0,
          "related_paths": [],
          "summary": "0 spans across 0 services"
        },
        {
          "path": "apps/web/.vercel/output/diagnostics/cli_traces.json",
          "kind": "traces",
          "format": "json",
          "signal_count": 0,
          "related_paths": [],
          "summary": "0 spans across 0 services"
        }
      ],
      "coverage_by_path": {},
      "test_results": {},
      "sast_findings": {},
      "trace_services": [],
      "recommendations": []
    },
    "dependency_risk_graph": {
      "nodes": [
        {
          "id": "skilgen/agents/codebase_signals.py",
          "kind": "source-file",
          "risk_score": 0.3,
          "signals": [
            "fanout:high",
            "cycle:internal"
          ],
          "dependencies": [
            "__future__",
            "ast",
            "functools",
            "pathlib",
            "re",
            "skilgen/core/config.py",
            "skilgen/core/corpus_index.py",
            "skilgen/core/deep_sampler.py",
            "skilgen/core/document_ingestion.py",
            "skilgen/core/models.py"
          ]
        },
        {
          "id": "skilgen/autoupdate.py",
          "kind": "source-file",
          "risk_score": 0.3,
          "signals": [
            "fanout:high",
            "cycle:internal"
          ],
          "dependencies": [
            "__future__",
            "datetime",
            "json",
            "os",
            "pathlib",
            "signal",
            "skilgen/agents/codebase_signals.py",
            "skilgen/core/config.py",
            "skilgen/core/generated_outputs.py",
            "skilgen/core/repo_state.py",
            "skilgen/delivery.py",
            "subprocess",
            "sys",
            "time"
          ]
        },
        {
          "id": "skilgen/core/corpus_index.py",
          "kind": "source-file",
          "risk_score": 0.3,
          "signals": [
            "fanout:high",
            "cycle:internal"
          ],
          "dependencies": [
            "__future__",
            "collections",
            "fnmatch",
            "hashlib",
            "json",
            "pathlib",
            "re",
            "skilgen/agents/codebase_signals.py",
            "skilgen/agents/language_parsers.py",
            "skilgen/core/config.py",
            "skilgen/core/document_ingestion.py",
            "skilgen/core/models.py",
            "typing"
          ]
        },
        {
          "id": "skilgen/deep_agents_runtime.py",
          "kind": "source-file",
          "risk_score": 0.3,
          "signals": [
            "fanout:high",
            "cycle:internal"
          ],
          "dependencies": [
            "__future__",
            "dataclasses",
            "deepagents",
            "json",
            "langchain.chat_models",
            "langchain_core.tools",
            "os",
            "pathlib",
            "skilgen/agents/codebase_signals.py",
            "skilgen/agents/decision_planner.py",
            "skilgen/agents/domain_graph_planner.py",
            "skilgen/agents/evidence_graph.py",
            "skilgen/agents/feature_extractor.py",
            "skilgen/agents/framework_fingerprint.py",
            "skilgen/agents/model_registry.py",
            "skilgen/agents/relationship_mapper.py"
          ]
        },
        {
          "id": "skilgen/delivery.py",
          "kind": "source-file",
          "risk_score": 0.3,
          "signals": [
            "fanout:high",
            "cycle:internal"
          ],
          "dependencies": [
            "__future__",
            "dataclasses",
            "pathlib",
            "skilgen/agents/__init__.py",
            "skilgen/agents/codebase_signals.py",
            "skilgen/agents/source_graphs.py",
            "skilgen/core/analytics.py",
            "skilgen/core/audit.py",
            "skilgen/core/config.py",
            "skilgen/core/context.py",
            "skilgen/core/corpus_index.py",
            "skilgen/core/freshness.py",
            "skilgen/core/generated_outputs.py",
            "skilgen/core/models.py",
            "skilgen/core/repo_state.py",
            "skilgen/core/requirements.py"
          ]
        },
        {
          "id": "skilgen/generators/package.py",
          "kind": "source-file",
          "risk_score": 0.3,
          "signals": [
            "fanout:high",
            "cycle:internal"
          ],
          "dependencies": [
            "__future__",
            "dataclasses",
            "datetime",
            "html",
            "json",
            "pathlib",
            "re",
            "skilgen/agents/__init__.py",
            "skilgen/agents/feature_extractor.py",
            "skilgen/agents/requirements_parser.py",
            "skilgen/core/config.py",
            "skilgen/core/context.py",
            "skilgen/core/models.py",
            "skilgen/deep_agents_core.py",
            "skilgen/deep_agents_runtime.py",
            "skilgen/enterprise_skills.py"
          ]
        },
        {
          "id": "manifest:packages/ui/package.json",
          "kind": "manifest",
          "risk_score": 0.25,
          "signals": [
            "fanout:large-manifest"
          ],
          "dependencies": [
            "@radix-ui/react-avatar",
            "@radix-ui/react-dialog",
            "@radix-ui/react-dropdown-menu",
            "@radix-ui/react-label",
            "@radix-ui/react-popover",
            "@radix-ui/react-progress",
            "@radix-ui/react-select",
            "@radix-ui/react-separator",
            "@radix-ui/react-switch",
            "@radix-ui/react-tabs",
            "@radix-ui/react-tooltip",
            "class-variance-authority",
            "clsx",
            "cmdk",
            "lucide-react",
            "tailwind-merge",
            "tailwindcss",
            "@skillayer/config",
            "@types/node",
            "@types/react",
            "@types/react-dom",
            "eslint",
            "typescript",
            "react",
            "react-dom"
          ]
        },
        {
          "id": "manifest:pyproject.toml",
          "kind": "manifest",
          "risk_score": 0.25,
          "signals": [
            "fanout:large-manifest"
          ],
          "dependencies": [
            "beautifulsoup4",
            "cryptography",
            "deepagents",
            "langchain",
            "langchain-anthropic",
            "langchain-google-genai",
            "langchain-huggingface",
            "langchain-openai",
            "openpyxl",
            "pypdf",
            "python-pptx",
            "PyYAML",
            "tree-sitter-language-pack",
            "fastapi",
            "uvicorn",
            "sqlalchemy",
            "asyncpg",
            "alembic",
            "psycopg2-binary",
            "pydantic",
            "pydantic-settings",
            "python-jose",
            "httpx",
            "redis",
            "celery"
          ]
        },
        {
          "id": "package:@eslint/js",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:@radix-ui/react-avatar",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:@radix-ui/react-dialog",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:@radix-ui/react-dropdown-menu",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:@radix-ui/react-label",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:@radix-ui/react-popover",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:@radix-ui/react-progress",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:@radix-ui/react-select",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:@radix-ui/react-separator",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:@radix-ui/react-switch",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:@radix-ui/react-tabs",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:@radix-ui/react-tooltip",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:@skillayer/config",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:@skillayer/types",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:@skillayer/ui",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:@types/node",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:@types/react",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:@types/react-dom",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:@workos-inc/authkit-nextjs",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:PyYAML",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:alembic",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:asyncpg",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:autoprefixer",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:beautifulsoup4",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:celery",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:class-variance-authority",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:clsx",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:cmdk",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:cryptography",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:deepagents",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:eslint",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:eslint-plugin-jsx-a11y",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:eslint-plugin-react",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:eslint-plugin-react-hooks",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:fastapi",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:globals",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:httpx",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:langchain",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:langchain-anthropic",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:langchain-google-genai",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:langchain-huggingface",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:langchain-openai",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:lucide-react",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:openpyxl",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:postcss",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:posthog-js",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:psycopg2-binary",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:pydantic",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:pydantic-settings",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:pypdf",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:python-pptx",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:react",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:react-dom",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:redis",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:sqlalchemy",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:stripe",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:tailwind-merge",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:tailwindcss",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:tree-sitter-language-pack",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:turbo",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:typescript",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "package:typescript-eslint",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
        },
        {
          "id": "scripts/deploy_api.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "argparse",
            "collections.abc",
            "contextlib",
            "json",
            "pathlib",
            "shutil",
            "subprocess"
          ]
        },
        {
          "id": "skilgen/agents/__init__.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "skilgen/agents/architecture_planner.py",
            "skilgen/agents/codebase_signals.py",
            "skilgen/agents/decision_planner.py",
            "skilgen/agents/domain_graph_planner.py",
            "skilgen/agents/evidence_graph.py",
            "skilgen/agents/feature_extractor.py",
            "skilgen/agents/framework_fingerprint.py",
            "skilgen/agents/language_parsers.py",
            "skilgen/agents/model_registry.py",
            "skilgen/agents/relationship_mapper.py",
            "skilgen/agents/requirements_parser.py",
            "skilgen/agents/roadmap_planner.py",
            "skilgen/agents/source_graphs.py",
            "skilgen/agents/workspace_graph.py"
          ]
        },
        {
          "id": "skilgen/agents/architecture_planner.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "dataclasses",
            "pathlib",
            "skilgen/agents/domain_graph_planner.py",
            "skilgen/agents/evidence_graph.py",
            "skilgen/core/config.py",
            "skilgen/core/models.py",
            "skilgen/deep_agents_core.py"
          ]
        },
        {
          "id": "skilgen/agents/decision_planner.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "pathlib",
            "skilgen/core/freshness.py",
            "skilgen/core/models.py",
            "skilgen/core/run_memory.py",
            "skilgen/deep_agents_core.py",
            "skilgen/enterprise_skills.py",
            "skilgen/external_skills.py"
          ]
        },
        {
          "id": "skilgen/agents/evidence_graph.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "pathlib",
            "skilgen/agents/codebase_signals.py",
            "skilgen/agents/relationship_mapper.py",
            "skilgen/agents/source_graphs.py",
            "skilgen/agents/workspace_graph.py",
            "skilgen/core/dependency_risk.py",
            "skilgen/core/models.py",
            "skilgen/core/runtime_signals.py"
          ]
        },
        {
          "id": "skilgen/agents/source_graphs.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "ast",
            "functools",
            "pathlib",
            "re",
            "skilgen/agents/codebase_signals.py",
            "skilgen/agents/language_parsers.py",
            "skilgen/agents/relationship_mapper.py",
            "skilgen/core/models.py"
          ]
        },
        {
          "id": "skilgen/api/jobs.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "concurrent.futures",
            "contextlib",
            "dataclasses",
            "datetime",
            "json",
            "pathlib",
            "skilgen/core/audit.py",
            "sqlite3",
            "threading",
            "typing",
            "uuid"
          ]
        },
        {
          "id": "skilgen/api/server.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "concurrent.futures",
            "dataclasses",
            "hashlib",
            "hmac",
            "http.server",
            "ipaddress",
            "json",
            "logging",
            "os",
            "pathlib",
            "skilgen/api/service.py",
            "skilgen/core/audit.py",
            "skilgen/core/auth_tokens.py",
            "skilgen/core/identity_policy_store.py",
            "skilgen/core/rate_limit_store.py"
          ]
        },
        {
          "id": "skilgen/api/service.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "pathlib",
            "skilgen/agents/decision_planner.py",
            "skilgen/api/jobs.py",
            "skilgen/autoupdate.py",
            "skilgen/core/analytics.py",
            "skilgen/core/context.py",
            "skilgen/core/diff.py",
            "skilgen/core/freshness.py",
            "skilgen/core/identity_policy_store.py",
            "skilgen/core/requirements.py",
            "skilgen/core/run_memory.py",
            "skilgen/core/score.py",
            "skilgen/deep_agents_core.py",
            "skilgen/deep_agents_runtime.py",
            "skilgen/delivery.py"
          ]
        },
        {
          "id": "skilgen/cli/main.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "argparse",
            "dataclasses",
            "json",
            "pathlib",
            "skilgen/__init__.py",
            "skilgen/agents/__init__.py",
            "skilgen/agents/requirements_parser.py",
            "skilgen/api/server.py",
            "skilgen/api/service.py",
            "skilgen/autoupdate.py",
            "skilgen/core/analytics.py",
            "skilgen/core/config.py",
            "skilgen/core/corpus_index.py",
            "skilgen/core/dependency_risk.py",
            "skilgen/core/enterprise_policy.py"
          ]
        },
        {
          "id": "skilgen/core/analytics.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "collections",
            "datetime",
            "json",
            "os",
            "pathlib",
            "re",
            "skilgen/external_skills.py"
          ]
        },
        {
          "id": "skilgen/core/audit.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "contextlib",
            "datetime",
            "fcntl",
            "json",
            "os",
            "pathlib",
            "threading",
            "typing"
          ]
        },
        {
          "id": "skilgen/core/auth_tokens.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "base64",
            "cryptography.exceptions",
            "cryptography.hazmat.primitives",
            "cryptography.hazmat.primitives.asymmetric",
            "hashlib",
            "hmac",
            "ipaddress",
            "json",
            "pathlib",
            "socket",
            "threading",
            "time",
            "typing",
            "urllib.parse",
            "urllib.request"
          ]
        },
        {
          "id": "skilgen/core/dependency_risk.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "json",
            "pathlib",
            "re",
            "skilgen/agents/relationship_mapper.py",
            "skilgen/agents/workspace_graph.py",
            "skilgen/core/models.py",
            "tomllib"
          ]
        },
        {
          "id": "skilgen/core/document_ingestion.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "bs4",
            "csv",
            "html",
            "json",
            "openpyxl",
            "pathlib",
            "pptx",
            "pypdf",
            "re",
            "tomllib",
            "xml.etree.ElementTree",
            "yaml",
            "zipfile"
          ]
        },
        {
          "id": "skilgen/core/enterprise_policy.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "dataclasses",
            "datetime",
            "pathlib",
            "skilgen/core/dependency_risk.py",
            "skilgen/core/score.py",
            "skilgen/enterprise_skills.py",
            "skilgen/external_skills.py",
            "typing",
            "yaml"
          ]
        },
        {
          "id": "skilgen/core/identity_policy_store.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "contextlib",
            "datetime",
            "json",
            "os",
            "pathlib",
            "sqlite3",
            "typing"
          ]
        },
        {
          "id": "skilgen/core/score.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "datetime",
            "html",
            "json",
            "pathlib",
            "re",
            "skilgen/agents/codebase_signals.py",
            "skilgen/core/context.py",
            "skilgen/core/freshness.py",
            "skilgen/core/requirements.py",
            "skilgen/core/validation.py",
            "subprocess",
            "threading",
            "urllib.parse"
          ]
        },
        {
          "id": "skilgen/deep_agents_core.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "asyncio",
            "deepagents",
            "json",
            "langchain.chat_models",
            "os",
            "pathlib",
            "queue",
            "skilgen/agents/model_registry.py",
            "skilgen/core/config.py",
            "threading",
            "time",
            "typing"
          ]
        },
        {
          "id": "skilgen/enterprise_skills.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "dataclasses",
            "datetime",
            "json",
            "os",
            "pathlib",
            "re",
            "shutil",
            "skilgen/core/config.py",
            "skilgen/core/document_ingestion.py",
            "subprocess",
            "urllib.parse",
            "urllib.request"
          ]
        },
        {
          "id": "skilgen/external_skills.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "dataclasses",
            "datetime",
            "json",
            "os",
            "pathlib",
            "re",
            "shutil",
            "skilgen/core/config.py",
            "subprocess"
          ]
        },
        {
          "id": "skilgen/generators/skills.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "datetime",
            "os",
            "pathlib",
            "skilgen/agents/architecture_planner.py",
            "skilgen/agents/codebase_signals.py",
            "skilgen/agents/requirements_parser.py",
            "skilgen/agents/roadmap_planner.py",
            "skilgen/core/config.py",
            "skilgen/core/context.py",
            "skilgen/core/dependency_risk.py",
            "skilgen/core/models.py",
            "skilgen/deep_agents_core.py",
            "typing"
          ]
        },
        {
          "id": "skilgen/sdk.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "pathlib",
            "skilgen/api/service.py",
            "skilgen/autoupdate.py",
            "skilgen/core/config.py",
            "skilgen/core/evals.py",
            "skilgen/delivery.py",
            "skilgen/enterprise_skills.py",
            "skilgen/external_skills.py"
          ]
        },
        {
          "id": "tests/oidc_test_utils.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "base64",
            "cryptography.hazmat.primitives",
            "cryptography.hazmat.primitives.asymmetric",
            "http.server",
            "json",
            "pathlib",
            "threading",
            "time",
            "typing"
          ]
        },
        {
          "id": "tests/test_api_smoke.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "io",
            "json",
            "logging",
            "os",
            "pathlib",
            "skilgen/api/server.py",
            "skilgen/core/auth_tokens.py",
            "subprocess",
            "tempfile",
            "tests/oidc_test_utils.py",
            "threading",
            "time",
            "unittest",
            "urllib.error",
            "urllib.parse"
          ]
        },
        {
          "id": "tests/test_dashboard_cli.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "contextlib",
            "datetime",
            "io",
            "json",
            "pathlib",
            "skilgen/autoupdate.py",
            "skilgen/cli/main.py",
            "skilgen/core/requirements.py",
            "skilgen/generators/package.py",
            "subprocess",
            "sys",
            "tempfile",
            "unittest",
            "unittest.mock"
          ]
        },
        {
          "id": "tests/test_decision_planner.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "pathlib",
            "skilgen/agents/decision_planner.py",
            "skilgen/core/context.py",
            "skilgen/core/requirements.py",
            "skilgen/external_skills.py",
            "subprocess",
            "tempfile",
            "unittest"
          ]
        },
        {
          "id": "tests/test_dependency_risk_graph_workstream.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "apps/api/api/routes/repos.py",
            "datetime",
            "json",
            "pathlib",
            "skilgen/core/dependency_risk.py",
            "tempfile",
            "types"
          ]
        },
        {
          "id": "tests/test_diff.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "json",
            "pathlib",
            "skilgen/core/context.py",
            "skilgen/core/diff.py",
            "skilgen/core/freshness.py",
            "skilgen/core/requirements.py",
            "subprocess",
            "sys",
            "tempfile",
            "unittest"
          ]
        },
        {
          "id": "tests/test_document_ingestion.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "openpyxl",
            "pathlib",
            "pptx",
            "skilgen/core/document_ingestion.py",
            "skilgen/core/requirements.py",
            "tempfile",
            "unittest",
            "zipfile"
          ]
        },
        {
          "id": "tests/test_jobs.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "contextlib",
            "pathlib",
            "skilgen/api/jobs.py",
            "skilgen/api/service.py",
            "sqlite3",
            "tempfile",
            "time",
            "unittest"
          ]
        },
        {
          "id": "tests/test_org_settings.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "apps/api/api/analysis.py",
            "apps/api/api/auth.py",
            "apps/api/api/routes/orgs.py",
            "asyncio",
            "datetime",
            "fastapi",
            "fastapi.testclient",
            "packages/db/database.py",
            "pathlib",
            "sqlalchemy.exc",
            "types",
            "typing"
          ]
        },
        {
          "id": "tests/test_packaging.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "os",
            "pathlib",
            "shutil",
            "subprocess",
            "sys",
            "tempfile",
            "time",
            "unittest"
          ]
        },
        {
          "id": "tests/test_registry_api.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "apps/api/api/auth.py",
            "apps/api/api/routes/registry.py",
            "datetime",
            "fastapi",
            "fastapi.testclient",
            "packages/db/database.py",
            "types",
            "typing"
          ]
        },
        {
          "id": "tests/test_registry_cli.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "http.server",
            "json",
            "os",
            "pathlib",
            "subprocess",
            "sys",
            "tempfile",
            "threading",
            "typing",
            "unittest"
          ]
        },
        {
          "id": "tests/test_runtime_hardening.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "os",
            "pathlib",
            "skilgen/deep_agents_core.py",
            "tempfile",
            "time",
            "types",
            "unittest",
            "unittest.mock"
          ]
        },
        {
          "id": "tests/test_score.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "pathlib",
            "skilgen/core/repo_state.py",
            "skilgen/core/score.py",
            "subprocess",
            "tempfile",
            "threading",
            "unittest",
            "unittest.mock"
          ]
        },
        {
          "id": "tests/test_score_quality_system.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "apps/api/api/routes/orgs.py",
            "apps/api/api/routes/repos.py",
            "datetime",
            "fastapi",
            "fastapi.testclient",
            "json",
            "packages/db/database.py",
            "pathlib",
            "pytest",
            "skilgen/core/score.py",
            "subprocess",
            "sys",
            "tempfile",
            "types",
            "typing"
          ]
        },
        {
          "id": "tests/test_sdk.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "json",
            "pathlib",
            "skilgen/external_skills.py",
            "skilgen/sdk.py",
            "subprocess",
            "tempfile",
            "time",
            "unittest",
            "unittest.mock"
          ]
        },
        {
          "id": "tests/test_skill_usage_analytics.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "apps/api/api/routes/admin.py",
            "apps/api/api/routes/orgs.py",
            "apps/api/api/routes/skills.py",
            "asyncio",
            "datetime",
            "fastapi",
            "fastapi.testclient",
            "packages/db/config.py",
            "packages/db/database.py",
            "pathlib",
            "types",
            "typing"
          ]
        },
        {
          "id": "tests/test_skillayer_api_infra.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "apps/api/api/auth.py",
            "apps/api/api/index.py",
            "apps/api/api/routes/metrics.py",
            "apps/api/api/routes/webhook.py",
            "datetime",
            "fastapi",
            "fastapi.testclient",
            "hashlib",
            "hmac",
            "packages/db/config.py",
            "packages/db/models/Base.py",
            "packages/db/models/Org.py",
            "packages/db/models/Repo.py",
            "pytest"
          ]
        },
        {
          "id": "tests/test_stripe_portal.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "apps/api/api/auth.py",
            "apps/api/api/routes/stripe.py",
            "fastapi",
            "fastapi.testclient",
            "packages/db/database.py",
            "pytest",
            "types",
            "typing"
          ]
        },
        {
          "id": "tests/test_stripe_webhook.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "apps/api/api/auth.py",
            "apps/api/api/routes/stripe.py",
            "fastapi",
            "fastapi.testclient",
            "json",
            "packages/db/database.py",
            "packages/db/models/Org.py",
            "pytest",
            "types",
            "typing"
          ]
        },
        {
          "id": "manifest:apps/api/requirements.txt",
          "kind": "manifest",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "fastapi",
            "sqlalchemy",
            "asyncpg",
            "alembic",
            "psycopg2-binary",
            "pydantic",
            "pydantic-settings",
            "httpx",
            "redis",
            "celery",
            "stripe"
          ]
        },
        {
          "id": "manifest:apps/dashboard/.next/standalone/apps/dashboard/package.json",
          "kind": "manifest",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "@skillayer/config",
            "@skillayer/types",
            "@skillayer/ui",
            "@workos-inc/authkit-nextjs",
            "autoprefixer",
            "lucide-react",
            "next",
            "postcss",
            "posthog-js",
            "react",
            "react-dom",
            "tailwindcss",
            "@types/node",
            "@types/react",
            "@types/react-dom",
            "eslint",
            "typescript"
          ]
        },
        {
          "id": "manifest:apps/dashboard/.next/standalone/package.json",
          "kind": "manifest",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "turbo",
            "typescript"
          ]
        },
        {
          "id": "manifest:apps/dashboard/package.json",
          "kind": "manifest",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "@skillayer/config",
            "@skillayer/types",
            "@skillayer/ui",
            "@workos-inc/authkit-nextjs",
            "autoprefixer",
            "lucide-react",
            "next",
            "postcss",
            "posthog-js",
            "react",
            "react-dom",
            "tailwindcss",
            "@types/node",
            "@types/react",
            "@types/react-dom",
            "eslint",
            "typescript"
          ]
        },
        {
          "id": "manifest:apps/web/package.json",
          "kind": "manifest",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "@skillayer/config",
            "@skillayer/types",
            "@skillayer/ui",
            "autoprefixer",
            "next",
            "postcss",
            "react",
            "react-dom",
            "tailwindcss",
            "@types/node",
            "@types/react",
            "@types/react-dom",
            "eslint",
            "typescript"
          ]
        },
        {
          "id": "manifest:apps/worker/requirements.txt",
          "kind": "manifest",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "sqlalchemy",
            "asyncpg",
            "alembic",
            "pydantic",
            "pydantic-settings",
            "httpx",
            "redis",
            "celery"
          ]
        },
        {
          "id": "manifest:package.json",
          "kind": "manifest",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "turbo",
            "typescript"
          ]
        },
        {
          "id": "manifest:packages/config/package.json",
          "kind": "manifest",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "@eslint/js",
            "@next/eslint-plugin-next",
            "@types/node",
            "eslint",
            "eslint-plugin-jsx-a11y",
            "eslint-plugin-react",
            "eslint-plugin-react-hooks",
            "globals",
            "tailwindcss",
            "typescript-eslint"
          ]
        },
        {
          "id": "manifest:packages/types/package.json",
          "kind": "manifest",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "@skillayer/config",
            "@types/node",
            "eslint",
            "typescript"
          ]
        },
        {
          "id": "package:@next/eslint-plugin-next",
          "kind": "external-package",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": []
        },
        {
          "id": "package:next",
          "kind": "external-package",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": []
        },
        {
          "id": "package:python-jose",
          "kind": "external-package",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": []
        },
        {
          "id": "package:uvicorn",
          "kind": "external-package",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": []
        },
        {
          "id": "scripts/bump_version.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "argparse",
            "pathlib",
            "re"
          ]
        },
        {
          "id": "scripts/deploy_dashboard.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "argparse",
            "collections.abc",
            "contextlib",
            "json",
            "pathlib",
            "subprocess"
          ]
        },
        {
          "id": "scripts/run_requirements_pipeline.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "argparse",
            "json",
            "pathlib",
            "skilgen/delivery.py",
            "sys"
          ]
        },
        {
          "id": "setup.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "setuptools"
          ]
        },
        {
          "id": "skilgen/__init__.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "skilgen/agents/__init__.py",
            "skilgen/autoupdate.py",
            "skilgen/delivery.py",
            "skilgen/sdk.py"
          ]
        },
        {
          "id": "skilgen/agents/domain_graph_planner.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "pathlib",
            "skilgen/agents/codebase_signals.py",
            "skilgen/agents/requirements_parser.py",
            "skilgen/agents/workspace_graph.py",
            "skilgen/core/models.py",
            "skilgen/deep_agents_core.py"
          ]
        },
        {
          "id": "skilgen/agents/feature_extractor.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "pathlib",
            "skilgen/agents/codebase_signals.py",
            "skilgen/agents/requirements_parser.py",
            "skilgen/core/models.py",
            "skilgen/deep_agents_core.py"
          ]
        },
        {
          "id": "skilgen/agents/framework_fingerprint.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "pathlib",
            "skilgen/core/models.py"
          ]
        },
        {
          "id": "skilgen/agents/language_parsers.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "ast",
            "dataclasses",
            "pathlib",
            "re",
            "tree_sitter_language_pack"
          ]
        },
        {
          "id": "skilgen/agents/model_registry.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "os",
            "skilgen/core/models.py"
          ]
        },
        {
          "id": "skilgen/agents/relationship_mapper.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "ast",
            "pathlib",
            "re",
            "skilgen/agents/codebase_signals.py",
            "warnings"
          ]
        },
        {
          "id": "skilgen/agents/requirements_parser.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "pathlib",
            "skilgen/agents/codebase_signals.py",
            "skilgen/core/models.py",
            "skilgen/core/requirements.py",
            "skilgen/deep_agents_core.py"
          ]
        },
        {
          "id": "skilgen/agents/roadmap_planner.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "pathlib",
            "skilgen/agents/model_registry.py",
            "skilgen/core/models.py",
            "skilgen/deep_agents_core.py"
          ]
        },
        {
          "id": "skilgen/agents/workspace_graph.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "json",
            "pathlib",
            "re",
            "skilgen/core/models.py",
            "yaml"
          ]
        },
        {
          "id": "skilgen/api/__init__.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "skilgen/api/server.py"
          ]
        },
        {
          "id": "skilgen/cli/__init__.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": []
        },
        {
          "id": "skilgen/core/__init__.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": []
        },
        {
          "id": "skilgen/core/config.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "pathlib",
            "skilgen/core/models.py"
          ]
        },
        {
          "id": "skilgen/core/context.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "pathlib",
            "skilgen/agents/codebase_signals.py",
            "skilgen/agents/domain_graph_planner.py",
            "skilgen/agents/framework_fingerprint.py",
            "skilgen/agents/workspace_graph.py",
            "skilgen/core/models.py"
          ]
        },
        {
          "id": "skilgen/core/deep_sampler.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "pathlib",
            "skilgen/core/config.py",
            "skilgen/core/models.py",
            "typing"
          ]
        },
        {
          "id": "skilgen/core/diff.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "pathlib",
            "skilgen/core/context.py",
            "skilgen/core/freshness.py",
            "skilgen/core/repo_state.py",
            "skilgen/core/requirements.py",
            "skilgen/core/score.py"
          ]
        },
        {
          "id": "skilgen/core/evals.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "json",
            "pathlib"
          ]
        },
        {
          "id": "skilgen/core/freshness.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "dataclasses",
            "hashlib",
            "json",
            "pathlib",
            "skilgen/core/generated_outputs.py",
            "skilgen/core/models.py"
          ]
        },
        {
          "id": "skilgen/core/generated_outputs.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "pathlib"
          ]
        },
        {
          "id": "skilgen/core/models.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "dataclasses",
            "pathlib"
          ]
        },
        {
          "id": "skilgen/core/project_memory.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "dataclasses",
            "json",
            "pathlib",
            "skilgen/core/models.py"
          ]
        },
        {
          "id": "skilgen/core/rate_limit_store.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "math",
            "os",
            "pathlib",
            "sqlite3"
          ]
        },
        {
          "id": "skilgen/core/repo_state.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "pathlib",
            "re",
            "shutil",
            "skilgen/agents/language_parsers.py",
            "subprocess"
          ]
        },
        {
          "id": "skilgen/core/requirements.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "hashlib",
            "json",
            "pathlib",
            "skilgen/agents/codebase_signals.py",
            "skilgen/core/document_ingestion.py",
            "skilgen/core/models.py"
          ]
        },
        {
          "id": "skilgen/core/run_memory.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "dataclasses",
            "json",
            "pathlib",
            "skilgen/core/models.py",
            "uuid"
          ]
        },
        {
          "id": "skilgen/core/runtime_data.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "pathlib",
            "shutil",
            "skilgen/core/config.py",
            "time"
          ]
        },
        {
          "id": "skilgen/core/runtime_signals.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "json",
            "pathlib",
            "re",
            "skilgen/core/models.py",
            "xml.etree"
          ]
        },
        {
          "id": "skilgen/core/validation.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "pathlib",
            "skilgen/agents/codebase_signals.py",
            "skilgen/deep_agents_core.py"
          ]
        },
        {
          "id": "skilgen/generators/__init__.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": []
        },
        {
          "id": "skilgen/registry_client.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "json",
            "os",
            "pathlib",
            "typing",
            "urllib.error",
            "urllib.request"
          ]
        },
        {
          "id": "tests/__init__.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": []
        },
        {
          "id": "tests/test_analytics.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "pathlib",
            "skilgen/core/analytics.py",
            "skilgen/generators/package.py",
            "tempfile",
            "unittest"
          ]
        },
        {
          "id": "tests/test_architecture_cli.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "json",
            "pathlib",
            "subprocess",
            "sys",
            "tempfile",
            "unittest"
          ]
        },
        {
          "id": "tests/test_architecture_planner.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "pathlib",
            "skilgen/agents/architecture_planner.py",
            "skilgen/core/models.py",
            "tempfile",
            "unittest"
          ]
        },
        {
          "id": "tests/test_audit.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "os",
            "pathlib",
            "skilgen/core/audit.py",
            "tempfile",
            "unittest",
            "unittest.mock"
          ]
        },
        {
          "id": "tests/test_auth_claim_mapping.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "json",
            "os",
            "pathlib",
            "skilgen/api/server.py",
            "tempfile",
            "unittest"
          ]
        },
        {
          "id": "tests/test_auth_tokens.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "pathlib",
            "skilgen/core/auth_tokens.py",
            "tempfile",
            "tests/oidc_test_utils.py",
            "time",
            "unittest"
          ]
        },
        {
          "id": "tests/test_autoupdate.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "pathlib",
            "skilgen/autoupdate.py",
            "tempfile",
            "unittest"
          ]
        },
        {
          "id": "tests/test_cli.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "json",
            "pathlib",
            "subprocess",
            "sys",
            "tempfile",
            "unittest"
          ]
        },
        {
          "id": "tests/test_codebase_signals.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "pathlib",
            "skilgen/agents/codebase_signals.py",
            "tempfile",
            "unittest"
          ]
        },
        {
          "id": "tests/test_config.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "pathlib",
            "skilgen/core/config.py",
            "tempfile",
            "unittest"
          ]
        },
        {
          "id": "tests/test_context.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "pathlib",
            "skilgen/core/context.py",
            "skilgen/core/requirements.py",
            "tempfile",
            "unittest"
          ]
        },
        {
          "id": "tests/test_corpus_cli.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "json",
            "pathlib",
            "subprocess",
            "sys",
            "tempfile",
            "unittest"
          ]
        },
        {
          "id": "tests/test_corpus_index.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "pathlib",
            "skilgen/agents/codebase_signals.py",
            "skilgen/core/corpus_index.py",
            "skilgen/core/deep_sampler.py",
            "tempfile",
            "unittest"
          ]
        },
        {
          "id": "tests/test_delivery.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "pathlib",
            "skilgen/core/models.py",
            "skilgen/core/score.py",
            "skilgen/delivery.py",
            "tempfile",
            "unittest",
            "unittest.mock"
          ]
        },
        {
          "id": "tests/test_dependency_risk.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "json",
            "pathlib",
            "skilgen/core/dependency_risk.py",
            "tempfile",
            "unittest"
          ]
        },
        {
          "id": "tests/test_domain_graph_planner.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "pathlib",
            "skilgen/agents/domain_graph_planner.py",
            "skilgen/core/requirements.py",
            "tempfile",
            "unittest",
            "unittest.mock"
          ]
        },
        {
          "id": "tests/test_enterprise_document_formats.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "pathlib",
            "skilgen/core/document_ingestion.py",
            "skilgen/enterprise_skills.py",
            "tempfile",
            "unittest"
          ]
        },
        {
          "id": "tests/test_enterprise_policy_cli.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "datetime",
            "json",
            "pathlib",
            "subprocess",
            "sys",
            "tempfile"
          ]
        },
        {
          "id": "tests/test_feature_extractor.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "pathlib",
            "skilgen/agents/feature_extractor.py",
            "tempfile",
            "unittest"
          ]
        },
        {
          "id": "tests/test_framework_fingerprint.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "pathlib",
            "skilgen/agents/framework_fingerprint.py",
            "tempfile",
            "unittest"
          ]
        },
        {
          "id": "tests/test_identity_policy_store.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "os",
            "pathlib",
            "skilgen/core/identity_policy_store.py",
            "tempfile",
            "unittest"
          ]
        },
        {
          "id": "tests/test_model_registry.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "os",
            "skilgen/agents/model_registry.py",
            "skilgen/core/models.py",
            "unittest"
          ]
        },
        {
          "id": "tests/test_overview_data.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "packages/db/schemas.py",
            "pathlib"
          ]
        },
        {
          "id": "tests/test_plan_cli.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "json",
            "pathlib",
            "subprocess",
            "sys",
            "tempfile",
            "unittest"
          ]
        },
        {
          "id": "tests/test_pr_comment.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "apps/api/api/pr_comment.py",
            "unittest"
          ]
        },
        {
          "id": "tests/test_pr_comment_dedup.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "apps/api/api/pr_comment.py",
            "httpx",
            "pytest",
            "typing"
          ]
        },
        {
          "id": "tests/test_rate_limit_store.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "pathlib",
            "skilgen/core/rate_limit_store.py",
            "tempfile",
            "unittest"
          ]
        },
        {
          "id": "tests/test_registry_dashboard.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "pathlib"
          ]
        },
        {
          "id": "tests/test_relationship_mapper.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "pathlib",
            "skilgen/agents/relationship_mapper.py",
            "tempfile",
            "unittest"
          ]
        },
        {
          "id": "tests/test_repos_screen.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "pathlib"
          ]
        },
        {
          "id": "tests/test_requirements.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "json",
            "pathlib",
            "skilgen/core/requirements.py",
            "tempfile",
            "unittest"
          ]
        },
        {
          "id": "tests/test_requirements_parser.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "pathlib",
            "skilgen/agents/requirements_parser.py",
            "tempfile",
            "unittest"
          ]
        },
        {
          "id": "tests/test_roadmap_planner.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "skilgen/agents/roadmap_planner.py",
            "skilgen/core/models.py",
            "unittest"
          ]
        },
        {
          "id": "tests/test_roadmap_skills.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "pathlib",
            "skilgen/core/requirements.py",
            "skilgen/generators/skills.py",
            "tempfile",
            "unittest"
          ]
        },
        {
          "id": "tests/test_run_memory.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "pathlib",
            "skilgen/core/models.py",
            "skilgen/core/run_memory.py",
            "tempfile",
            "unittest"
          ]
        },
        {
          "id": "tests/test_runtime_signals.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "json",
            "pathlib",
            "skilgen/core/runtime_signals.py",
            "tempfile",
            "unittest"
          ]
        },
        {
          "id": "tests/test_skill_detail.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "apps/api/api/routes/skills.py",
            "asyncio",
            "pathlib",
            "types"
          ]
        },
        {
          "id": "tests/test_source_graphs.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "pathlib",
            "skilgen/agents/language_parsers.py",
            "skilgen/agents/source_graphs.py",
            "tempfile",
            "unittest"
          ]
        },
        {
          "id": "tests/test_upgrade_flow.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "pathlib",
            "unittest"
          ]
        },
        {
          "id": "tests/test_validate_cli.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "json",
            "subprocess",
            "sys",
            "unittest"
          ]
        },
        {
          "id": "tests/test_vercel_api_deploy.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "json",
            "pathlib",
            "scripts/deploy_api.py"
          ]
        },
        {
          "id": "tests/test_vercel_dashboard_deploy.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "json",
            "pathlib",
            "scripts/deploy_dashboard.py"
          ]
        },
        {
          "id": "tests/test_workspace_graph.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "pathlib",
            "skilgen/agents/workspace_graph.py",
            "tempfile",
            "unittest"
          ]
        },
        {
          "id": "workspace:apps-dashboard",
          "kind": "workspace-package",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "packages/config",
            "packages/types",
            "packages/ui"
          ]
        },
        {
          "id": "workspace:apps-web",
          "kind": "workspace-package",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "packages/config",
            "packages/types",
            "packages/ui"
          ]
        },
        {
          "id": "workspace:packages-config",
          "kind": "workspace-package",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": []
        },
        {
          "id": "workspace:packages-db",
          "kind": "workspace-package",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": []
        },
        {
          "id": "workspace:packages-types",
          "kind": "workspace-package",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "packages/config"
          ]
        },
        {
          "id": "workspace:packages-ui",
          "kind": "workspace-package",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "packages/config"
          ]
        }
      ],
      "edges": [
        {
          "source": "manifest:apps/api/requirements.txt",
          "target": "package:alembic",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/api/requirements.txt",
          "target": "package:asyncpg",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/api/requirements.txt",
          "target": "package:celery",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/api/requirements.txt",
          "target": "package:fastapi",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/api/requirements.txt",
          "target": "package:httpx",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/api/requirements.txt",
          "target": "package:psycopg2-binary",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/api/requirements.txt",
          "target": "package:pydantic",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/api/requirements.txt",
          "target": "package:pydantic-settings",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/api/requirements.txt",
          "target": "package:redis",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/api/requirements.txt",
          "target": "package:sqlalchemy",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/api/requirements.txt",
          "target": "package:stripe",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/dashboard/.next/standalone/apps/dashboard/package.json",
          "target": "package:@skillayer/config",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/dashboard/.next/standalone/apps/dashboard/package.json",
          "target": "package:@skillayer/types",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/dashboard/.next/standalone/apps/dashboard/package.json",
          "target": "package:@skillayer/ui",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/dashboard/.next/standalone/apps/dashboard/package.json",
          "target": "package:@types/node",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/dashboard/.next/standalone/apps/dashboard/package.json",
          "target": "package:@types/react",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/dashboard/.next/standalone/apps/dashboard/package.json",
          "target": "package:@types/react-dom",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/dashboard/.next/standalone/apps/dashboard/package.json",
          "target": "package:@workos-inc/authkit-nextjs",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/dashboard/.next/standalone/apps/dashboard/package.json",
          "target": "package:autoprefixer",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/dashboard/.next/standalone/apps/dashboard/package.json",
          "target": "package:eslint",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/dashboard/.next/standalone/apps/dashboard/package.json",
          "target": "package:lucide-react",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/dashboard/.next/standalone/apps/dashboard/package.json",
          "target": "package:next",
          "kind": "external-package",
          "risk_signals": []
        },
        {
          "source": "manifest:apps/dashboard/.next/standalone/apps/dashboard/package.json",
          "target": "package:postcss",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/dashboard/.next/standalone/apps/dashboard/package.json",
          "target": "package:posthog-js",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/dashboard/.next/standalone/apps/dashboard/package.json",
          "target": "package:react",
          "kind": "external-package",
          "risk_signals": []
        },
        {
          "source": "manifest:apps/dashboard/.next/standalone/apps/dashboard/package.json",
          "target": "package:react-dom",
          "kind": "external-package",
          "risk_signals": []
        },
        {
          "source": "manifest:apps/dashboard/.next/standalone/apps/dashboard/package.json",
          "target": "package:tailwindcss",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/dashboard/.next/standalone/apps/dashboard/package.json",
          "target": "package:typescript",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/dashboard/.next/standalone/package.json",
          "target": "package:turbo",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/dashboard/.next/standalone/package.json",
          "target": "package:typescript",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/dashboard/package.json",
          "target": "package:@skillayer/config",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/dashboard/package.json",
          "target": "package:@skillayer/types",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/dashboard/package.json",
          "target": "package:@skillayer/ui",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/dashboard/package.json",
          "target": "package:@types/node",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/dashboard/package.json",
          "target": "package:@types/react",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/dashboard/package.json",
          "target": "package:@types/react-dom",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/dashboard/package.json",
          "target": "package:@workos-inc/authkit-nextjs",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/dashboard/package.json",
          "target": "package:autoprefixer",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/dashboard/package.json",
          "target": "package:eslint",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/dashboard/package.json",
          "target": "package:lucide-react",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/dashboard/package.json",
          "target": "package:next",
          "kind": "external-package",
          "risk_signals": []
        },
        {
          "source": "manifest:apps/dashboard/package.json",
          "target": "package:postcss",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/dashboard/package.json",
          "target": "package:posthog-js",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/dashboard/package.json",
          "target": "package:react",
          "kind": "external-package",
          "risk_signals": []
        },
        {
          "source": "manifest:apps/dashboard/package.json",
          "target": "package:react-dom",
          "kind": "external-package",
          "risk_signals": []
        },
        {
          "source": "manifest:apps/dashboard/package.json",
          "target": "package:tailwindcss",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/dashboard/package.json",
          "target": "package:typescript",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/web/package.json",
          "target": "package:@skillayer/config",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/web/package.json",
          "target": "package:@skillayer/types",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/web/package.json",
          "target": "package:@skillayer/ui",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/web/package.json",
          "target": "package:@types/node",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/web/package.json",
          "target": "package:@types/react",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/web/package.json",
          "target": "package:@types/react-dom",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/web/package.json",
          "target": "package:autoprefixer",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/web/package.json",
          "target": "package:eslint",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/web/package.json",
          "target": "package:next",
          "kind": "external-package",
          "risk_signals": []
        },
        {
          "source": "manifest:apps/web/package.json",
          "target": "package:postcss",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/web/package.json",
          "target": "package:react",
          "kind": "external-package",
          "risk_signals": []
        },
        {
          "source": "manifest:apps/web/package.json",
          "target": "package:react-dom",
          "kind": "external-package",
          "risk_signals": []
        },
        {
          "source": "manifest:apps/web/package.json",
          "target": "package:tailwindcss",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/web/package.json",
          "target": "package:typescript",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/worker/requirements.txt",
          "target": "package:alembic",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/worker/requirements.txt",
          "target": "package:asyncpg",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/worker/requirements.txt",
          "target": "package:celery",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/worker/requirements.txt",
          "target": "package:httpx",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/worker/requirements.txt",
          "target": "package:pydantic",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/worker/requirements.txt",
          "target": "package:pydantic-settings",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/worker/requirements.txt",
          "target": "package:redis",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/worker/requirements.txt",
          "target": "package:sqlalchemy",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:package.json",
          "target": "package:turbo",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:package.json",
          "target": "package:typescript",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:packages/config/package.json",
          "target": "package:@eslint/js",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:packages/config/package.json",
          "target": "package:@next/eslint-plugin-next",
          "kind": "external-package",
          "risk_signals": []
        },
        {
          "source": "manifest:packages/config/package.json",
          "target": "package:@types/node",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:packages/config/package.json",
          "target": "package:eslint",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:packages/config/package.json",
          "target": "package:eslint-plugin-jsx-a11y",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:packages/config/package.json",
          "target": "package:eslint-plugin-react",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:packages/config/package.json",
          "target": "package:eslint-plugin-react-hooks",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:packages/config/package.json",
          "target": "package:globals",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:packages/config/package.json",
          "target": "package:tailwindcss",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:packages/config/package.json",
          "target": "package:typescript-eslint",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:packages/types/package.json",
          "target": "package:@skillayer/config",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:packages/types/package.json",
          "target": "package:@types/node",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:packages/types/package.json",
          "target": "package:eslint",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:packages/types/package.json",
          "target": "package:typescript",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:packages/ui/package.json",
          "target": "package:@radix-ui/react-avatar",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:packages/ui/package.json",
          "target": "package:@radix-ui/react-dialog",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:packages/ui/package.json",
          "target": "package:@radix-ui/react-dropdown-menu",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:packages/ui/package.json",
          "target": "package:@radix-ui/react-label",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:packages/ui/package.json",
          "target": "package:@radix-ui/react-popover",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:packages/ui/package.json",
          "target": "package:@radix-ui/react-progress",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:packages/ui/package.json",
          "target": "package:@radix-ui/react-select",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:packages/ui/package.json",
          "target": "package:@radix-ui/react-separator",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:packages/ui/package.json",
          "target": "package:@radix-ui/react-switch",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:packages/ui/package.json",
          "target": "package:@radix-ui/react-tabs",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:packages/ui/package.json",
          "target": "package:@radix-ui/react-tooltip",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:packages/ui/package.json",
          "target": "package:@skillayer/config",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:packages/ui/package.json",
          "target": "package:@types/node",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:packages/ui/package.json",
          "target": "package:@types/react",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:packages/ui/package.json",
          "target": "package:@types/react-dom",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:packages/ui/package.json",
          "target": "package:class-variance-authority",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:packages/ui/package.json",
          "target": "package:clsx",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:packages/ui/package.json",
          "target": "package:cmdk",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:packages/ui/package.json",
          "target": "package:eslint",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:packages/ui/package.json",
          "target": "package:lucide-react",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:packages/ui/package.json",
          "target": "package:react",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:packages/ui/package.json",
          "target": "package:react-dom",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:packages/ui/package.json",
          "target": "package:tailwind-merge",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:packages/ui/package.json",
          "target": "package:tailwindcss",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:packages/ui/package.json",
          "target": "package:typescript",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:pyproject.toml",
          "target": "package:PyYAML",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:pyproject.toml",
          "target": "package:alembic",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:pyproject.toml",
          "target": "package:asyncpg",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:pyproject.toml",
          "target": "package:beautifulsoup4",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:pyproject.toml",
          "target": "package:celery",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:pyproject.toml",
          "target": "package:cryptography",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:pyproject.toml",
          "target": "package:deepagents",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:pyproject.toml",
          "target": "package:fastapi",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:pyproject.toml",
          "target": "package:httpx",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:pyproject.toml",
          "target": "package:langchain",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:pyproject.toml",
          "target": "package:langchain-anthropic",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:pyproject.toml",
          "target": "package:langchain-google-genai",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:pyproject.toml",
          "target": "package:langchain-huggingface",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:pyproject.toml",
          "target": "package:langchain-openai",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:pyproject.toml",
          "target": "package:openpyxl",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:pyproject.toml",
          "target": "package:psycopg2-binary",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:pyproject.toml",
          "target": "package:pydantic",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:pyproject.toml",
          "target": "package:pydantic-settings",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:pyproject.toml",
          "target": "package:pypdf",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:pyproject.toml",
          "target": "package:python-jose",
          "kind": "external-package",
          "risk_signals": []
        },
        {
          "source": "manifest:pyproject.toml",
          "target": "package:python-pptx",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:pyproject.toml",
          "target": "package:redis",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:pyproject.toml",
          "target": "package:sqlalchemy",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:pyproject.toml",
          "target": "package:tree-sitter-language-pack",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:pyproject.toml",
          "target": "package:uvicorn",
          "kind": "external-package",
          "risk_signals": []
        },
        {
          "source": "scripts/run_requirements_pipeline.py",
          "target": "skilgen/delivery.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/__init__.py",
          "target": "skilgen/agents/__init__.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/__init__.py",
          "target": "skilgen/autoupdate.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/__init__.py",
          "target": "skilgen/delivery.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/__init__.py",
          "target": "skilgen/sdk.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/__init__.py",
          "target": "skilgen/agents/architecture_planner.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/__init__.py",
          "target": "skilgen/agents/codebase_signals.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/__init__.py",
          "target": "skilgen/agents/decision_planner.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/__init__.py",
          "target": "skilgen/agents/domain_graph_planner.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/__init__.py",
          "target": "skilgen/agents/evidence_graph.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/__init__.py",
          "target": "skilgen/agents/feature_extractor.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/__init__.py",
          "target": "skilgen/agents/framework_fingerprint.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/__init__.py",
          "target": "skilgen/agents/language_parsers.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/__init__.py",
          "target": "skilgen/agents/model_registry.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/__init__.py",
          "target": "skilgen/agents/relationship_mapper.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/__init__.py",
          "target": "skilgen/agents/requirements_parser.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/__init__.py",
          "target": "skilgen/agents/roadmap_planner.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/__init__.py",
          "target": "skilgen/agents/source_graphs.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/__init__.py",
          "target": "skilgen/agents/workspace_graph.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/architecture_planner.py",
          "target": "skilgen/agents/domain_graph_planner.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/architecture_planner.py",
          "target": "skilgen/agents/evidence_graph.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/architecture_planner.py",
          "target": "skilgen/core/config.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/architecture_planner.py",
          "target": "skilgen/core/models.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/architecture_planner.py",
          "target": "skilgen/deep_agents_core.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/codebase_signals.py",
          "target": "skilgen/core/config.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/codebase_signals.py",
          "target": "skilgen/core/corpus_index.py",
          "kind": "repo-import",
          "risk_signals": [
            "cycle:internal"
          ]
        },
        {
          "source": "skilgen/agents/codebase_signals.py",
          "target": "skilgen/core/deep_sampler.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/codebase_signals.py",
          "target": "skilgen/core/document_ingestion.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/codebase_signals.py",
          "target": "skilgen/core/models.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/decision_planner.py",
          "target": "skilgen/core/freshness.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/decision_planner.py",
          "target": "skilgen/core/models.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/decision_planner.py",
          "target": "skilgen/core/run_memory.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/decision_planner.py",
          "target": "skilgen/deep_agents_core.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/decision_planner.py",
          "target": "skilgen/enterprise_skills.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/decision_planner.py",
          "target": "skilgen/external_skills.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/domain_graph_planner.py",
          "target": "skilgen/agents/codebase_signals.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/domain_graph_planner.py",
          "target": "skilgen/agents/requirements_parser.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/domain_graph_planner.py",
          "target": "skilgen/agents/workspace_graph.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/domain_graph_planner.py",
          "target": "skilgen/core/models.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/domain_graph_planner.py",
          "target": "skilgen/deep_agents_core.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/evidence_graph.py",
          "target": "skilgen/agents/codebase_signals.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/evidence_graph.py",
          "target": "skilgen/agents/relationship_mapper.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/evidence_graph.py",
          "target": "skilgen/agents/source_graphs.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/evidence_graph.py",
          "target": "skilgen/agents/workspace_graph.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/evidence_graph.py",
          "target": "skilgen/core/dependency_risk.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/evidence_graph.py",
          "target": "skilgen/core/models.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/evidence_graph.py",
          "target": "skilgen/core/runtime_signals.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/feature_extractor.py",
          "target": "skilgen/agents/codebase_signals.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/feature_extractor.py",
          "target": "skilgen/agents/requirements_parser.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/feature_extractor.py",
          "target": "skilgen/core/models.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/feature_extractor.py",
          "target": "skilgen/deep_agents_core.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/framework_fingerprint.py",
          "target": "skilgen/core/models.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/model_registry.py",
          "target": "skilgen/core/models.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/relationship_mapper.py",
          "target": "skilgen/agents/codebase_signals.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/requirements_parser.py",
          "target": "skilgen/agents/codebase_signals.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/requirements_parser.py",
          "target": "skilgen/core/models.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/requirements_parser.py",
          "target": "skilgen/core/requirements.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/requirements_parser.py",
          "target": "skilgen/deep_agents_core.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/roadmap_planner.py",
          "target": "skilgen/agents/model_registry.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/roadmap_planner.py",
          "target": "skilgen/core/models.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/roadmap_planner.py",
          "target": "skilgen/deep_agents_core.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/source_graphs.py",
          "target": "skilgen/agents/codebase_signals.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/source_graphs.py",
          "target": "skilgen/agents/language_parsers.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/source_graphs.py",
          "target": "skilgen/agents/relationship_mapper.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/source_graphs.py",
          "target": "skilgen/core/models.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/agents/workspace_graph.py",
          "target": "skilgen/core/models.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/api/__init__.py",
          "target": "skilgen/api/server.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/api/jobs.py",
          "target": "skilgen/core/audit.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/api/server.py",
          "target": "skilgen/api/service.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/api/server.py",
          "target": "skilgen/core/audit.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/api/server.py",
          "target": "skilgen/core/auth_tokens.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/api/server.py",
          "target": "skilgen/core/identity_policy_store.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/api/server.py",
          "target": "skilgen/core/rate_limit_store.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/api/server.py",
          "target": "skilgen/core/runtime_data.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/api/service.py",
          "target": "skilgen/agents/decision_planner.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/api/service.py",
          "target": "skilgen/api/jobs.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/api/service.py",
          "target": "skilgen/autoupdate.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/api/service.py",
          "target": "skilgen/core/analytics.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/api/service.py",
          "target": "skilgen/core/context.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/api/service.py",
          "target": "skilgen/core/diff.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/api/service.py",
          "target": "skilgen/core/freshness.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/api/service.py",
          "target": "skilgen/core/identity_policy_store.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/api/service.py",
          "target": "skilgen/core/requirements.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/api/service.py",
          "target": "skilgen/core/run_memory.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/api/service.py",
          "target": "skilgen/core/score.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/api/service.py",
          "target": "skilgen/deep_agents_core.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/api/service.py",
          "target": "skilgen/deep_agents_runtime.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/api/service.py",
          "target": "skilgen/delivery.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/api/service.py",
          "target": "skilgen/enterprise_skills.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/api/service.py",
          "target": "skilgen/external_skills.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/autoupdate.py",
          "target": "skilgen/agents/codebase_signals.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/autoupdate.py",
          "target": "skilgen/core/config.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/autoupdate.py",
          "target": "skilgen/core/generated_outputs.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/autoupdate.py",
          "target": "skilgen/core/repo_state.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/autoupdate.py",
          "target": "skilgen/delivery.py",
          "kind": "repo-import",
          "risk_signals": [
            "cycle:internal"
          ]
        },
        {
          "source": "skilgen/cli/main.py",
          "target": "skilgen/__init__.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/cli/main.py",
          "target": "skilgen/agents/__init__.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/cli/main.py",
          "target": "skilgen/agents/requirements_parser.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/cli/main.py",
          "target": "skilgen/api/server.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/cli/main.py",
          "target": "skilgen/api/service.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/cli/main.py",
          "target": "skilgen/autoupdate.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/cli/main.py",
          "target": "skilgen/core/analytics.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/cli/main.py",
          "target": "skilgen/core/config.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/cli/main.py",
          "target": "skilgen/core/corpus_index.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/cli/main.py",
          "target": "skilgen/core/dependency_risk.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/cli/main.py",
          "target": "skilgen/core/enterprise_policy.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/cli/main.py",
          "target": "skilgen/core/evals.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/cli/main.py",
          "target": "skilgen/core/runtime_data.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/cli/main.py",
          "target": "skilgen/core/score.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/cli/main.py",
          "target": "skilgen/deep_agents_core.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/cli/main.py",
          "target": "skilgen/delivery.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/cli/main.py",
          "target": "skilgen/enterprise_skills.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/cli/main.py",
          "target": "skilgen/external_skills.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/cli/main.py",
          "target": "skilgen/registry_client.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/analytics.py",
          "target": "skilgen/external_skills.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/config.py",
          "target": "skilgen/core/models.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/context.py",
          "target": "skilgen/agents/codebase_signals.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/context.py",
          "target": "skilgen/agents/domain_graph_planner.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/context.py",
          "target": "skilgen/agents/framework_fingerprint.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/context.py",
          "target": "skilgen/agents/workspace_graph.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/context.py",
          "target": "skilgen/core/models.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/corpus_index.py",
          "target": "skilgen/agents/codebase_signals.py",
          "kind": "repo-import",
          "risk_signals": [
            "cycle:internal"
          ]
        },
        {
          "source": "skilgen/core/corpus_index.py",
          "target": "skilgen/agents/language_parsers.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/corpus_index.py",
          "target": "skilgen/core/config.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/corpus_index.py",
          "target": "skilgen/core/document_ingestion.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/corpus_index.py",
          "target": "skilgen/core/models.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/deep_sampler.py",
          "target": "skilgen/core/config.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/deep_sampler.py",
          "target": "skilgen/core/models.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/dependency_risk.py",
          "target": "skilgen/agents/relationship_mapper.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/dependency_risk.py",
          "target": "skilgen/agents/workspace_graph.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/dependency_risk.py",
          "target": "skilgen/core/models.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/diff.py",
          "target": "skilgen/core/context.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/diff.py",
          "target": "skilgen/core/freshness.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/diff.py",
          "target": "skilgen/core/repo_state.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/diff.py",
          "target": "skilgen/core/requirements.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/diff.py",
          "target": "skilgen/core/score.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/enterprise_policy.py",
          "target": "skilgen/core/dependency_risk.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/enterprise_policy.py",
          "target": "skilgen/core/score.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/enterprise_policy.py",
          "target": "skilgen/enterprise_skills.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/enterprise_policy.py",
          "target": "skilgen/external_skills.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/freshness.py",
          "target": "skilgen/core/generated_outputs.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/freshness.py",
          "target": "skilgen/core/models.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/project_memory.py",
          "target": "skilgen/core/models.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/repo_state.py",
          "target": "skilgen/agents/language_parsers.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/requirements.py",
          "target": "skilgen/agents/codebase_signals.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/requirements.py",
          "target": "skilgen/core/document_ingestion.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/requirements.py",
          "target": "skilgen/core/models.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/run_memory.py",
          "target": "skilgen/core/models.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/runtime_data.py",
          "target": "skilgen/core/config.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/runtime_signals.py",
          "target": "skilgen/core/models.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/score.py",
          "target": "skilgen/agents/codebase_signals.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/score.py",
          "target": "skilgen/core/context.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/score.py",
          "target": "skilgen/core/freshness.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/score.py",
          "target": "skilgen/core/requirements.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/score.py",
          "target": "skilgen/core/validation.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/validation.py",
          "target": "skilgen/agents/codebase_signals.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/core/validation.py",
          "target": "skilgen/deep_agents_core.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/deep_agents_core.py",
          "target": "skilgen/agents/model_registry.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/deep_agents_core.py",
          "target": "skilgen/core/config.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/deep_agents_runtime.py",
          "target": "skilgen/agents/codebase_signals.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/deep_agents_runtime.py",
          "target": "skilgen/agents/decision_planner.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/deep_agents_runtime.py",
          "target": "skilgen/agents/domain_graph_planner.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/deep_agents_runtime.py",
          "target": "skilgen/agents/evidence_graph.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/deep_agents_runtime.py",
          "target": "skilgen/agents/feature_extractor.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/deep_agents_runtime.py",
          "target": "skilgen/agents/framework_fingerprint.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/deep_agents_runtime.py",
          "target": "skilgen/agents/model_registry.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/deep_agents_runtime.py",
          "target": "skilgen/agents/relationship_mapper.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/deep_agents_runtime.py",
          "target": "skilgen/agents/requirements_parser.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/deep_agents_runtime.py",
          "target": "skilgen/agents/roadmap_planner.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/deep_agents_runtime.py",
          "target": "skilgen/agents/workspace_graph.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/deep_agents_runtime.py",
          "target": "skilgen/autoupdate.py",
          "kind": "repo-import",
          "risk_signals": [
            "cycle:internal"
          ]
        },
        {
          "source": "skilgen/deep_agents_runtime.py",
          "target": "skilgen/core/analytics.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/deep_agents_runtime.py",
          "target": "skilgen/core/config.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/deep_agents_runtime.py",
          "target": "skilgen/core/context.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/deep_agents_runtime.py",
          "target": "skilgen/core/corpus_index.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/delivery.py",
          "target": "skilgen/agents/__init__.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/delivery.py",
          "target": "skilgen/agents/codebase_signals.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/delivery.py",
          "target": "skilgen/agents/source_graphs.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/delivery.py",
          "target": "skilgen/core/analytics.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/delivery.py",
          "target": "skilgen/core/audit.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/delivery.py",
          "target": "skilgen/core/config.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/delivery.py",
          "target": "skilgen/core/context.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/delivery.py",
          "target": "skilgen/core/corpus_index.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/delivery.py",
          "target": "skilgen/core/freshness.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/delivery.py",
          "target": "skilgen/core/generated_outputs.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/delivery.py",
          "target": "skilgen/core/models.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/delivery.py",
          "target": "skilgen/core/repo_state.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/delivery.py",
          "target": "skilgen/core/requirements.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/delivery.py",
          "target": "skilgen/core/run_memory.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/delivery.py",
          "target": "skilgen/core/runtime_data.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/delivery.py",
          "target": "skilgen/core/score.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/delivery.py",
          "target": "skilgen/deep_agents_core.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/delivery.py",
          "target": "skilgen/enterprise_skills.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/delivery.py",
          "target": "skilgen/external_skills.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/delivery.py",
          "target": "skilgen/generators/package.py",
          "kind": "repo-import",
          "risk_signals": [
            "cycle:internal"
          ]
        },
        {
          "source": "skilgen/delivery.py",
          "target": "skilgen/generators/skills.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/enterprise_skills.py",
          "target": "skilgen/core/config.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/enterprise_skills.py",
          "target": "skilgen/core/document_ingestion.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/external_skills.py",
          "target": "skilgen/core/config.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/generators/package.py",
          "target": "skilgen/agents/__init__.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/generators/package.py",
          "target": "skilgen/agents/feature_extractor.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/generators/package.py",
          "target": "skilgen/agents/requirements_parser.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/generators/package.py",
          "target": "skilgen/core/config.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/generators/package.py",
          "target": "skilgen/core/context.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/generators/package.py",
          "target": "skilgen/core/models.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/generators/package.py",
          "target": "skilgen/deep_agents_core.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/generators/package.py",
          "target": "skilgen/deep_agents_runtime.py",
          "kind": "repo-import",
          "risk_signals": [
            "cycle:internal"
          ]
        },
        {
          "source": "skilgen/generators/package.py",
          "target": "skilgen/enterprise_skills.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/generators/package.py",
          "target": "skilgen/external_skills.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/generators/skills.py",
          "target": "skilgen/agents/architecture_planner.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/generators/skills.py",
          "target": "skilgen/agents/codebase_signals.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/generators/skills.py",
          "target": "skilgen/agents/requirements_parser.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/generators/skills.py",
          "target": "skilgen/agents/roadmap_planner.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/generators/skills.py",
          "target": "skilgen/core/config.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/generators/skills.py",
          "target": "skilgen/core/context.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/generators/skills.py",
          "target": "skilgen/core/dependency_risk.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/generators/skills.py",
          "target": "skilgen/core/models.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/generators/skills.py",
          "target": "skilgen/deep_agents_core.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/sdk.py",
          "target": "skilgen/api/service.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/sdk.py",
          "target": "skilgen/autoupdate.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/sdk.py",
          "target": "skilgen/core/config.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/sdk.py",
          "target": "skilgen/core/evals.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/sdk.py",
          "target": "skilgen/delivery.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/sdk.py",
          "target": "skilgen/enterprise_skills.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/sdk.py",
          "target": "skilgen/external_skills.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_analytics.py",
          "target": "skilgen/core/analytics.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_analytics.py",
          "target": "skilgen/generators/package.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_api_smoke.py",
          "target": "skilgen/api/server.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_api_smoke.py",
          "target": "skilgen/core/auth_tokens.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_api_smoke.py",
          "target": "tests/oidc_test_utils.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_architecture_planner.py",
          "target": "skilgen/agents/architecture_planner.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_architecture_planner.py",
          "target": "skilgen/core/models.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_audit.py",
          "target": "skilgen/core/audit.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_auth_claim_mapping.py",
          "target": "skilgen/api/server.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_auth_tokens.py",
          "target": "skilgen/core/auth_tokens.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_auth_tokens.py",
          "target": "tests/oidc_test_utils.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_autoupdate.py",
          "target": "skilgen/autoupdate.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_codebase_signals.py",
          "target": "skilgen/agents/codebase_signals.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_config.py",
          "target": "skilgen/core/config.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_context.py",
          "target": "skilgen/core/context.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_context.py",
          "target": "skilgen/core/requirements.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_corpus_index.py",
          "target": "skilgen/agents/codebase_signals.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_corpus_index.py",
          "target": "skilgen/core/corpus_index.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_corpus_index.py",
          "target": "skilgen/core/deep_sampler.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_dashboard_cli.py",
          "target": "skilgen/autoupdate.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_dashboard_cli.py",
          "target": "skilgen/cli/main.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_dashboard_cli.py",
          "target": "skilgen/core/requirements.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_dashboard_cli.py",
          "target": "skilgen/generators/package.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_decision_planner.py",
          "target": "skilgen/agents/decision_planner.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_decision_planner.py",
          "target": "skilgen/core/context.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_decision_planner.py",
          "target": "skilgen/core/requirements.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_decision_planner.py",
          "target": "skilgen/external_skills.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_delivery.py",
          "target": "skilgen/core/models.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_delivery.py",
          "target": "skilgen/core/score.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_delivery.py",
          "target": "skilgen/delivery.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_dependency_risk.py",
          "target": "skilgen/core/dependency_risk.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_dependency_risk_graph_workstream.py",
          "target": "apps/api/api/routes/repos.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_dependency_risk_graph_workstream.py",
          "target": "skilgen/core/dependency_risk.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_diff.py",
          "target": "skilgen/core/context.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_diff.py",
          "target": "skilgen/core/diff.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_diff.py",
          "target": "skilgen/core/freshness.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_diff.py",
          "target": "skilgen/core/requirements.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_document_ingestion.py",
          "target": "skilgen/core/document_ingestion.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_document_ingestion.py",
          "target": "skilgen/core/requirements.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_domain_graph_planner.py",
          "target": "skilgen/agents/domain_graph_planner.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_domain_graph_planner.py",
          "target": "skilgen/core/requirements.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_enterprise_document_formats.py",
          "target": "skilgen/core/document_ingestion.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_enterprise_document_formats.py",
          "target": "skilgen/enterprise_skills.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_feature_extractor.py",
          "target": "skilgen/agents/feature_extractor.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_framework_fingerprint.py",
          "target": "skilgen/agents/framework_fingerprint.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_identity_policy_store.py",
          "target": "skilgen/core/identity_policy_store.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_jobs.py",
          "target": "skilgen/api/jobs.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_jobs.py",
          "target": "skilgen/api/service.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_model_registry.py",
          "target": "skilgen/agents/model_registry.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_model_registry.py",
          "target": "skilgen/core/models.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_org_settings.py",
          "target": "apps/api/api/analysis.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_org_settings.py",
          "target": "apps/api/api/auth.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_org_settings.py",
          "target": "apps/api/api/routes/orgs.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_org_settings.py",
          "target": "packages/db/database.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_overview_data.py",
          "target": "packages/db/schemas.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_pr_comment.py",
          "target": "apps/api/api/pr_comment.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_pr_comment_dedup.py",
          "target": "apps/api/api/pr_comment.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_rate_limit_store.py",
          "target": "skilgen/core/rate_limit_store.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_registry_api.py",
          "target": "apps/api/api/auth.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_registry_api.py",
          "target": "apps/api/api/routes/registry.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_registry_api.py",
          "target": "packages/db/database.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_relationship_mapper.py",
          "target": "skilgen/agents/relationship_mapper.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_requirements.py",
          "target": "skilgen/core/requirements.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_requirements_parser.py",
          "target": "skilgen/agents/requirements_parser.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_roadmap_planner.py",
          "target": "skilgen/agents/roadmap_planner.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_roadmap_planner.py",
          "target": "skilgen/core/models.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_roadmap_skills.py",
          "target": "skilgen/core/requirements.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_roadmap_skills.py",
          "target": "skilgen/generators/skills.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_run_memory.py",
          "target": "skilgen/core/models.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_run_memory.py",
          "target": "skilgen/core/run_memory.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_runtime_hardening.py",
          "target": "skilgen/deep_agents_core.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_runtime_signals.py",
          "target": "skilgen/core/runtime_signals.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_score.py",
          "target": "skilgen/core/repo_state.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_score.py",
          "target": "skilgen/core/score.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_score_quality_system.py",
          "target": "apps/api/api/routes/orgs.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_score_quality_system.py",
          "target": "apps/api/api/routes/repos.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_score_quality_system.py",
          "target": "packages/db/database.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_score_quality_system.py",
          "target": "skilgen/core/score.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_sdk.py",
          "target": "skilgen/external_skills.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_sdk.py",
          "target": "skilgen/sdk.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_skill_detail.py",
          "target": "apps/api/api/routes/skills.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_skill_usage_analytics.py",
          "target": "apps/api/api/routes/admin.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_skill_usage_analytics.py",
          "target": "apps/api/api/routes/orgs.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_skill_usage_analytics.py",
          "target": "apps/api/api/routes/skills.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_skill_usage_analytics.py",
          "target": "packages/db/config.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_skill_usage_analytics.py",
          "target": "packages/db/database.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_skillayer_api_infra.py",
          "target": "apps/api/api/auth.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_skillayer_api_infra.py",
          "target": "apps/api/api/index.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_skillayer_api_infra.py",
          "target": "apps/api/api/routes/metrics.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_skillayer_api_infra.py",
          "target": "apps/api/api/routes/webhook.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_skillayer_api_infra.py",
          "target": "packages/db/config.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_skillayer_api_infra.py",
          "target": "packages/db/models/Base.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_skillayer_api_infra.py",
          "target": "packages/db/models/Org.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_skillayer_api_infra.py",
          "target": "packages/db/models/Repo.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_source_graphs.py",
          "target": "skilgen/agents/language_parsers.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_source_graphs.py",
          "target": "skilgen/agents/source_graphs.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_stripe_portal.py",
          "target": "apps/api/api/auth.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_stripe_portal.py",
          "target": "apps/api/api/routes/stripe.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_stripe_portal.py",
          "target": "packages/db/database.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_stripe_webhook.py",
          "target": "apps/api/api/auth.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_stripe_webhook.py",
          "target": "apps/api/api/routes/stripe.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_stripe_webhook.py",
          "target": "packages/db/database.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_stripe_webhook.py",
          "target": "packages/db/models/Org.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_vercel_api_deploy.py",
          "target": "scripts/deploy_api.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_vercel_dashboard_deploy.py",
          "target": "scripts/deploy_dashboard.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_workspace_graph.py",
          "target": "skilgen/agents/workspace_graph.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "workspace:apps-dashboard",
          "target": "workspace:packages-config",
          "kind": "workspace-package",
          "risk_signals": []
        },
        {
          "source": "workspace:apps-dashboard",
          "target": "workspace:packages-types",
          "kind": "workspace-package",
          "risk_signals": []
        },
        {
          "source": "workspace:apps-dashboard",
          "target": "workspace:packages-ui",
          "kind": "workspace-package",
          "risk_signals": []
        },
        {
          "source": "workspace:apps-web",
          "target": "workspace:packages-config",
          "kind": "workspace-package",
          "risk_signals": []
        },
        {
          "source": "workspace:apps-web",
          "target": "workspace:packages-types",
          "kind": "workspace-package",
          "risk_signals": []
        },
        {
          "source": "workspace:apps-web",
          "target": "workspace:packages-ui",
          "kind": "workspace-package",
          "risk_signals": []
        },
        {
          "source": "workspace:packages-types",
          "target": "workspace:packages-config",
          "kind": "workspace-package",
          "risk_signals": []
        },
        {
          "source": "workspace:packages-ui",
          "target": "workspace:packages-config",
          "kind": "workspace-package",
          "risk_signals": []
        }
      ],
      "cycles": [
        [
          "skilgen/agents/codebase_signals.py",
          "skilgen/core/corpus_index.py",
          "skilgen/agents/codebase_signals.py"
        ],
        [
          "skilgen/delivery.py",
          "skilgen/generators/package.py",
          "skilgen/deep_agents_runtime.py",
          "skilgen/autoupdate.py",
          "skilgen/delivery.py"
        ],
        [
          "skilgen/generators/package.py",
          "skilgen/deep_agents_runtime.py",
          "skilgen/generators/package.py"
        ]
      ],
      "recommendations": [
        "Break internal dependency cycles before materializing fine-grained skills around those files or packages.",
        "High fan-out dependency hotspots surfaced in: scripts/deploy_api.py, skilgen/agents/__init__.py, skilgen/agents/architecture_planner.py, skilgen/agents/codebase_signals.py, skilgen/agents/decision_planner.py.",
        "Loosely pinned external dependencies increase drift risk: package:@eslint/js, package:@radix-ui/react-avatar, package:@radix-ui/react-dialog, package:@radix-ui/react-dropdown-menu, package:@radix-ui/react-label, package:@radix-ui/react-popover."
      ]
    }
  },
  "architecture": {
    "headline": "Evidence-backed architecture blueprint for the codebase",
    "system_summary": "Skilgen identified 2 top-level architecture domains from 91 evidence items and 12 domain graph nodes. Parser backends in use: empty, python-ast, regex. Source comprehension currently tracks 124 symbol-bearing files, 121 call-bearing files, 54 mapped tests, and 6 workspace packages.",
    "domains": [
      {
        "name": "platform",
        "summary": "Tooling and runtime domain covering Skilgen's internal engine, CLI, planners, generators, and maintenance scripts.",
        "confidence": 0.9,
        "responsibilities": [
          "Tooling and runtime domain covering Skilgen's internal engine, CLI, planners, generators, and maintenance scripts.",
          "Coordinates subdomains: platform-runtime, platform-agents, platform-cli, platform-core.",
          "tooling platform",
          "generation engine"
        ],
        "evidence_paths": [
          "skilgen/__init__.py",
          "skilgen/autoupdate.py",
          "skilgen/agents/__init__.py",
          "skilgen/agents/architecture_planner.py",
          "skilgen/cli/__init__.py",
          "skilgen/cli/main.py"
        ],
        "related_domains": [
          "roadmap"
        ],
        "recommended_skill_path": "skills/platform/SKILL.md"
      },
      {
        "name": "roadmap",
        "summary": "Delivery sequencing domain that keeps phases, next steps, and implementation order explicit for agents.",
        "confidence": 0.84,
        "responsibilities": [
          "Delivery sequencing domain that keeps phases, next steps, and implementation order explicit for agents.",
          "Coordinates subdomains: roadmap-phase-0, roadmap-phase-1, roadmap-phase-2, roadmap-phase-3.",
          "phase-based delivery",
          "sequenced implementation planning"
        ],
        "evidence_paths": [
          "skills/roadmap/SKILL.md",
          "REPORT.md"
        ],
        "related_domains": [
          "requirements",
          "backend",
          "frontend"
        ],
        "recommended_skill_path": "skills/roadmap/SKILL.md"
      }
    ],
    "hotspots": [
      "Dominant languages: python."
    ],
    "recommendations": [
      "Use architecture domains as the parents for the skill tree, and keep sub-skills close to strong evidence files.",
      "Regenerate skills when dominant domain evidence or domain boundaries change materially.",
      "Use high-signal source evidence to define domain boundaries before generating skills.",
      "Prefer domains that are supported by both code evidence and requirements intent."
    ],
    "materialization_plan": [
      {
        "domain": "platform",
        "parent_skill_path": "skills/platform/SKILL.md",
        "child_skill_paths": [
          "skills/platform/runtime/SKILL.md",
          "skills/platform/agents/SKILL.md",
          "skills/platform/cli/SKILL.md",
          "skills/platform/core/SKILL.md",
          "skills/platform/generators/SKILL.md",
          "skills/platform/scripts/SKILL.md"
        ],
        "cross_links": [
          "skills/roadmap/SKILL.md"
        ],
        "decision": "split",
        "rationale": "Split because 6 concrete child skill surfaces emerged from 6 grounded evidence paths. The parent skill can hold shared context while child skills isolate the distinct capability seams around platform-runtime, platform-agents, platform-cli."
      },
      {
        "domain": "roadmap",
        "parent_skill_path": "skills/roadmap/SKILL.md",
        "child_skill_paths": [
          "skills/roadmap/phase-0/SKILL.md",
          "skills/roadmap/phase-1/SKILL.md",
          "skills/roadmap/phase-2/SKILL.md",
          "skills/roadmap/phase-3/SKILL.md"
        ],
        "cross_links": [],
        "decision": "split",
        "rationale": "Split because 4 concrete child skill surfaces emerged from 2 grounded evidence paths. The parent skill can hold shared context while child skills isolate the distinct capability seams around roadmap-phase-0, roadmap-phase-1, roadmap-phase-2."
      }
    ]
  }
}
```
