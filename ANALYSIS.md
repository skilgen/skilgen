# Analysis

```json
{
  "framework_fingerprint": {
    "frontend": {
      "name": "nextjs",
      "confidence": 0.65,
      "evidence": [
        "app/"
      ]
    },
    "backend": {
      "name": "fastapi",
      "confidence": 0.8500000000000001,
      "evidence": [
        "main.py",
        "pyproject.toml"
      ]
    },
    "test_framework": {
      "name": "unittest",
      "confidence": 0.65,
      "evidence": [
        "test_"
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
      "tests/test_diff.py",
      "tests/test_document_ingestion.py",
      "tests/test_domain_graph_planner.py",
      "tests/test_enterprise_document_formats.py",
      "tests/test_feature_extractor.py",
      "tests/test_framework_fingerprint.py",
      "tests/test_identity_policy_store.py",
      "tests/test_jobs.py",
      "tests/test_model_registry.py",
      "tests/test_packaging.py",
      "tests/test_plan_cli.py",
      "tests/test_rate_limit_store.py",
      "tests/test_relationship_mapper.py",
      "tests/test_requirements.py",
      "tests/test_requirements_parser.py",
      "tests/test_roadmap_planner.py",
      "tests/test_roadmap_skills.py",
      "tests/test_run_memory.py",
      "tests/test_runtime_hardening.py",
      "tests/test_runtime_signals.py",
      "tests/test_score.py",
      "tests/test_sdk.py",
      "tests/test_source_graphs.py",
      "tests/test_validate_cli.py",
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
      "python": 105
    }
  },
  "repo_archetype": "skilgen-platform",
  "workspace_graph": {
    "tool": null,
    "packages": [],
    "dependencies": [],
    "entrypoints": [],
    "confidence": 0.0,
    "detection_evidence": []
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
      "skilgen/core/evals.py",
      "skilgen/core/runtime_data.py",
      "skilgen/deep_agents_core.py",
      "skilgen/delivery.py",
      "skilgen/enterprise_skills.py",
      "skilgen/external_skills.py",
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
      "skilgen/agents/language_parsers.py",
      "subprocess"
    ],
    "skilgen/core/requirements.py": [
      "__future__",
      "hashlib",
      "json",
      "pathlib",
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
      "json",
      "pathlib",
      "re",
      "skilgen/agents/codebase_signals.py",
      "skilgen/core/context.py",
      "skilgen/core/freshness.py",
      "skilgen/core/requirements.py",
      "skilgen/core/validation.py",
      "threading"
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
      "skilgen/core/models.py",
      "skilgen/deep_agents_core.py",
      "typing"
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
    "tests/test_rate_limit_store.py": [
      "__future__",
      "pathlib",
      "skilgen/core/rate_limit_store.py",
      "tempfile",
      "unittest"
    ],
    "tests/test_relationship_mapper.py": [
      "pathlib",
      "skilgen/agents/relationship_mapper.py",
      "tempfile",
      "unittest"
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
      "unittest"
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
    "tests/test_source_graphs.py": [
      "pathlib",
      "skilgen/agents/language_parsers.py",
      "skilgen/agents/source_graphs.py",
      "tempfile",
      "unittest"
    ],
    "tests/test_validate_cli.py": [
      "json",
      "subprocess",
      "sys",
      "unittest"
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
      "python": 105
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
        "skilgen/core/evals.py",
        "skilgen/core/runtime_data.py",
        "skilgen/deep_agents_core.py",
        "skilgen/delivery.py",
        "skilgen/enterprise_skills.py",
        "skilgen/external_skills.py",
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
        "skilgen/agents/language_parsers.py",
        "subprocess"
      ],
      "skilgen/core/requirements.py": [
        "__future__",
        "hashlib",
        "json",
        "pathlib",
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
        "json",
        "pathlib",
        "re",
        "skilgen/agents/codebase_signals.py",
        "skilgen/core/context.py",
        "skilgen/core/freshness.py",
        "skilgen/core/requirements.py",
        "skilgen/core/validation.py",
        "threading"
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
        "skilgen/core/models.py",
        "skilgen/deep_agents_core.py",
        "typing"
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
      "tests/test_rate_limit_store.py": [
        "__future__",
        "pathlib",
        "skilgen/core/rate_limit_store.py",
        "tempfile",
        "unittest"
      ],
      "tests/test_relationship_mapper.py": [
        "pathlib",
        "skilgen/agents/relationship_mapper.py",
        "tempfile",
        "unittest"
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
        "unittest"
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
      "tests/test_source_graphs.py": [
        "pathlib",
        "skilgen/agents/language_parsers.py",
        "skilgen/agents/source_graphs.py",
        "tempfile",
        "unittest"
      ],
      "tests/test_validate_cli.py": [
        "json",
        "subprocess",
        "sys",
        "unittest"
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
          "Scanned 401 files from the project root.",
          "Observed: .DS_Store",
          "Observed: .github/CODEOWNERS",
          "Observed: .github/ISSUE_TEMPLATE/bug_report.yml",
          "Observed: .github/ISSUE_TEMPLATE/config.yml"
        ],
        "related_imports": []
      },
      {
        "path": "skilgen/api/__init__.py",
        "kind": "source",
        "language": "python",
        "tags": [
          "backend_routes"
        ],
        "snippet": [
          "from skilgen.api.server import create_server, run_server",
          "__all__ = [\"create_server\", \"run_server\"]"
        ],
        "related_imports": [
          "skilgen/api/server.py"
        ]
      },
      {
        "path": "skilgen/api/jobs.py",
        "kind": "source",
        "language": "python",
        "tags": [
          "backend_routes",
          "background_jobs"
        ],
        "snippet": [
          "from __future__ import annotations",
          "import json",
          "import sqlite3",
          "import uuid",
          "from concurrent.futures import ThreadPoolExecutor",
          "from contextlib import closing",
          "from dataclasses import dataclass, field",
          "from datetime import datetime, timezone",
          "from pathlib import Path",
          "from threading import Lock",
          "from typing import Callable",
          "from skilgen.core.audit import append_audit_event"
        ],
        "related_imports": [
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
        "path": "skilgen/api/server.py",
        "kind": "source",
        "language": "python",
        "tags": [
          "backend_routes"
        ],
        "snippet": [
          "from __future__ import annotations",
          "from dataclasses import dataclass",
          "import hmac",
          "import hashlib",
          "import ipaddress",
          "import json",
          "import logging",
          "import os",
          "import socket",
          "import threading",
          "import time",
          "import uuid"
        ],
        "related_imports": [
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
        ]
      },
      {
        "path": "skilgen/api/service.py",
        "kind": "source",
        "language": "python",
        "tags": [
          "backend_routes",
          "services"
        ],
        "snippet": [
          "from __future__ import annotations",
          "from pathlib import Path",
          "from typing import Callable",
          "from skilgen.api.jobs import get_job, job_payload, list_jobs, request_cancel, submit_job",
          "from skilgen.agents.decision_planner import build_agent_decision",
          "from skilgen.autoupdate import auto_update_status",
          "from skilgen.core.diff import compute_diff",
          "from skilgen.core.analytics import analytics_summary",
          "from skilgen.deep_agents_core import current_runtime_mode, runtime_diagnostics",
          "from skilgen.deep_agents_runtime import (",
          "DeepAgentsRuntime,",
          "native_analyze_payload,"
        ],
        "related_imports": [
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
        ]
      },
      {
        "path": "skilgen/core/auth_tokens.py",
        "kind": "source",
        "language": "python",
        "tags": [
          "auth_files"
        ],
        "snippet": [
          "from __future__ import annotations",
          "import base64",
          "import hashlib",
          "import hmac",
          "import ipaddress",
          "import json",
          "import socket",
          "import threading",
          "import time",
          "from pathlib import Path",
          "from typing import Any",
          "from urllib.parse import urlparse"
        ],
        "related_imports": [
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
        "path": "tests/test_auth_claim_mapping.py",
        "kind": "source",
        "language": "python",
        "tags": [
          "auth_files",
          "tests"
        ],
        "snippet": [
          "from __future__ import annotations",
          "import os",
          "import unittest",
          "from pathlib import Path",
          "from tempfile import TemporaryDirectory",
          "from unittest import mock",
          "from skilgen.api.server import (",
          "_claims_allowed_roots,",
          "_claims_principal,",
          "_claims_scope,",
          "_claims_tenant,",
          "_provider_claim_mapping,"
        ],
        "related_imports": [
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
        "path": "tests/test_auth_tokens.py",
        "kind": "source",
        "language": "python",
        "tags": [
          "auth_files",
          "tests"
        ],
        "snippet": [
          "from __future__ import annotations",
          "import time",
          "import unittest",
          "from pathlib import Path",
          "from tempfile import TemporaryDirectory",
          "from skilgen.core.auth_tokens import (",
          "SignedTokenError,",
          "clear_remote_verifier_caches,",
          "mint_signed_token,",
          "verify_jwks_token,",
          "verify_oidc_token,",
          "verify_signed_token,"
        ],
        "related_imports": [
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
        "path": "tests/test_jobs.py",
        "kind": "source",
        "language": "python",
        "tags": [
          "background_jobs",
          "tests"
        ],
        "snippet": [
          "from contextlib import closing",
          "from pathlib import Path",
          "import sqlite3",
          "from tempfile import TemporaryDirectory",
          "import time",
          "import unittest",
          "from skilgen.api import jobs as jobs_module",
          "from skilgen.api.jobs import get_job, request_cancel, submit_job",
          "from skilgen.api.service import create_deliver_job, job_status_payload, jobs_payload, resume_job_payload",
          "class JobPersistenceTests(unittest.TestCase):",
          "def test_deliver_job_persists_status_to_project_root(self) -> None:",
          "with TemporaryDirectory() as tmp:"
        ],
        "related_imports": [
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
        "path": "scripts/bump_version.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "#!/usr/bin/env python3",
          "from __future__ import annotations",
          "import argparse",
          "import re",
          "from pathlib import Path",
          "def replace_version(path: Path, pattern: str, version: str) -> None:",
          "text = path.read_text(encoding=\"utf-8\")",
          "updated, count = re.subn(pattern, lambda match: f\"{match.group(1)}{version}{match.group(3)}\", text)",
          "if count != 1:",
          "raise SystemExit(f\"Could not update version in {path}\")",
          "path.write_text(updated, encoding=\"utf-8\")",
          "def main() -> None:"
        ],
        "related_imports": [
          "__future__",
          "argparse",
          "pathlib",
          "re"
        ]
      },
      {
        "path": "scripts/run_requirements_pipeline.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "#!/usr/bin/env python3",
          "\"\"\"Compatibility wrapper for the requirements-driven Skilgen delivery pipeline.\"\"\"",
          "from __future__ import annotations",
          "import argparse",
          "import json",
          "from pathlib import Path",
          "import sys",
          "ROOT = Path(__file__).resolve().parents[1]",
          "if str(ROOT) not in sys.path:",
          "sys.path.insert(0, str(ROOT))",
          "from skilgen.delivery import run_delivery",
          "def main() -> None:"
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
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from setuptools import setup",
          "setup()"
        ],
        "related_imports": [
          "setuptools"
        ]
      },
      {
        "path": "skilgen/__init__.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "\"\"\"Skilgen package.\"\"\"",
          "from skilgen.agents import fingerprint_project",
          "from skilgen.autoupdate import auto_update_status, ensure_auto_update_worker, stop_auto_update_worker",
          "from skilgen.delivery import run_delivery",
          "from skilgen.sdk import (",
          "activate_project_mcp_connector,",
          "activate_skill_source,",
          "analyze_project,",
          "architecture_project,",
          "project_dashboard,",
          "cancel_job,",
          "deactivate_project_mcp_connector,"
        ],
        "related_imports": [
          "skilgen/agents/__init__.py",
          "skilgen/autoupdate.py",
          "skilgen/delivery.py",
          "skilgen/sdk.py"
        ]
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
          "from skilgen.agents.codebase_signals import analyze_codebase, collect_code_evidence, collect_structural_evidence",
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
        "path": "skilgen/agents/relationship_mapper.py",
        "kind": "structure",
        "language": "python",
        "tags": [
          "structural-evidence"
        ],
        "snippet": [
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
        "related_imports": [
          "__future__",
          "ast",
          "pathlib",
          "re",
          "skilgen/agents/codebase_signals.py",
          "warnings"
        ]
      },
      {
        "path": "skilgen/agents/requirements_parser.py",
        "kind": "structure",
        "language": "python",
        "tags": [
          "structural-evidence"
        ],
        "snippet": [
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
        "related_imports": [
          "__future__",
          "pathlib",
          "skilgen/agents/codebase_signals.py",
          "skilgen/core/models.py",
          "skilgen/core/requirements.py",
          "skilgen/deep_agents_core.py"
        ]
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
        "path": "FEATURES.md",
        "kind": "documentation",
        "language": null,
        "tags": [
          "docs"
        ],
        "snippet": [
          "# Features",
          "Search this file before implementing any feature to avoid duplicating work.",
          "| Feature Name | Domain | Location | Description | Status | Last Modified |",
          "| --- | --- | --- | --- | --- | --- |",
          "| Project folder analysis | analysis | `skilgen-upstream-work` | Analyze the input folder and generate outputs into that same folder. | active | current |",
          "| Backend route: skilgen/api/__init__.py | backend | `skilgen/api/__init__.py` | Detected route or handler implementation in the scanned codebase. | active | current |",
          "| Backend route: skilgen/api/jobs.py | backend | `skilgen/api/jobs.py` | Detected route or handler implementation in the scanned codebase. | active | current |",
          "| Backend route: skilgen/api/server.py | backend | `skilgen/api/server.py` | Detected route or handler implementation in the scanned codebase. | active | current |"
        ],
        "related_imports": []
      },
      {
        "path": "README.md",
        "kind": "documentation",
        "language": null,
        "tags": [
          "docs"
        ],
        "snippet": [
          "<p align=\"center\">",
          "<img src=\"docs/assets/skilgen.svg\" alt=\"Skilgen\" width=\"480\" />",
          "</p>",
          "<h2 align=\"center\">The living skill system for AI coding agents</h2>",
          "<p align=\"center\">",
          "Every agent session starts from zero. Skilgen ends that.<br/>",
          "Generate, govern, and keep your codebase's agent knowledge current automatically.",
          "</p>"
        ],
        "related_imports": []
      },
      {
        "path": "REPORT.md",
        "kind": "documentation",
        "language": null,
        "tags": [
          "docs"
        ],
        "snippet": [
          "# Report",
          "## Summary",
          "- Detected domains: platform, platform-runtime, platform-agents, platform-cli, platform-core, platform-generators, platform-scripts, roadmap, roadmap-phase-0, roadmap-phase-1, road",
          "- Feature inventory entries: 9",
          "- Backend route files: 4",
          "- Frontend route files: 0",
          "- Component files: 0",
          "- Service files: 1"
        ],
        "related_imports": []
      },
      {
        "path": "TRACEABILITY.md",
        "kind": "documentation",
        "language": null,
        "tags": [
          "docs"
        ],
        "snippet": [
          "# Traceability",
          "This file maps requirements and detected code evidence to the generated Skilgen outputs.",
          "## Requirements Source",
          "- Source file: `codebase-only input`",
          "- Source hash: `54b3e3912fb4`",
          "## Intent To Output Mapping",
          "### Endpoints",
          "- Intent: Detected route: skilgen/api/__init__.py"
        ],
        "related_imports": []
      },
      {
        "path": "docs/examples/README.md",
        "kind": "documentation",
        "language": null,
        "tags": [
          "docs"
        ],
        "snippet": [
          "# Dashboard Examples",
          "These are committed, self-contained HTML dashboard snapshots generated with Skilgen and saved into the repo so people can inspect real output.",
          "GitHub will show the HTML source in the repo view. Download the file or open it locally in a browser to see the full interactive dashboard.",
          "## Anthropic claude-code",
          "- Source repo: [anthropics/claude-code](https://github.com/anthropics/claude-code)",
          "- Source commit: `5a7bf28`",
          "- Dashboard file: [`claude-code-dashboard.html`](claude-code-dashboard.html)",
          "- Generated `AGENTS.md`: [`claude-code-AGENTS.md`](claude-code-AGENTS.md)"
        ],
        "related_imports": []
      },
      {
        "path": "docs/examples/librechat-skill-tree/skilgen.yml",
        "kind": "config",
        "language": null,
        "tags": [
          "config"
        ],
        "snippet": [
          "# Skilgen configuration",
          "include_paths:",
          "- .",
          "exclude_paths:",
          "- .git",
          "- __pycache__",
          "- .venv",
          "- node_modules"
        ],
        "related_imports": []
      },
      {
        "path": "pyproject.toml",
        "kind": "config",
        "language": null,
        "tags": [
          "config"
        ],
        "snippet": [
          "[build-system]",
          "requires = [\"setuptools>=68\"]",
          "build-backend = \"setuptools.build_meta\"",
          "[project]",
          "name = \"skilgen\"",
          "version = \"0.6.0\"",
          "description = \"Generate agent-readable project skills and starter scaffolds from requirements documents.\"",
          "readme = \"README.md\""
        ],
        "related_imports": []
      },
      {
        "path": "skilgen.yml",
        "kind": "config",
        "language": null,
        "tags": [
          "config"
        ],
        "snippet": [
          "# Skilgen configuration",
          "include_paths:",
          "- .",
          "exclude_paths:",
          "- .git",
          "- __pycache__",
          "- .venv",
          "- node_modules"
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
      "Use cross-file symbol relationships to keep inheritance and interface seams aligned with the skill tree.",
      "Break internal dependency cycles before materializing fine-grained skills around those files or packages.",
      "High fan-out dependency hotspots surfaced in: skilgen/agents/__init__.py, skilgen/agents/architecture_planner.py, skilgen/agents/codebase_signals.py, skilgen/agents/decision_planner.py, skilgen/agents/evidence_graph.py."
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
        "symbol_count": 29,
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
        "import_count": 13,
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
        "symbol_count": 13,
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
        "call_count": 28,
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
        "symbol_count": 11,
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
        "symbol_count": 9,
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
        "import_count": 5,
        "relationship_count": 0
      },
      "skilgen/core/requirements.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 9,
        "call_count": 30,
        "import_count": 6,
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
        "import_count": 11,
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
        "symbol_count": 25,
        "call_count": 30,
        "import_count": 13,
        "relationship_count": 0
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
        "symbol_count": 25,
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
      "tests/test_diff.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 11,
        "call_count": 20,
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
      "tests/test_rate_limit_store.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 2,
        "call_count": 8,
        "import_count": 5,
        "relationship_count": 1
      },
      "tests/test_relationship_mapper.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 6,
        "call_count": 9,
        "import_count": 4,
        "relationship_count": 1
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
        "symbol_count": 11,
        "call_count": 25,
        "import_count": 7,
        "relationship_count": 1
      },
      "tests/test_sdk.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 19,
        "call_count": 30,
        "import_count": 9,
        "relationship_count": 1
      },
      "tests/test_source_graphs.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 4,
        "call_count": 17,
        "import_count": 5,
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
        "from skilgen.agents.codebase_signals import analyze_codebase, collect_code_evidence, collect_structural_evidence",
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
        "from skilgen.core.config import load_config"
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
        "from skilgen.agents.codebase_signals import analyze_codebase",
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
        "from skilgen.core.models import DependencyRiskEdge, DependencyRiskGraph, DependencyRiskNode",
        "function _find_cycles",
        "function _external_dependency_signals",
        "function _load_json"
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
        "function _state_dir",
        "function _state_path",
        "function _iter_source_files"
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
        "from skilgen.agents.language_parsers import parse_language_text",
        "function _semantic_path_kind",
        "function _git_dir",
        "function _git_output",
        "function _git_lines",
        "function _git_show"
      ],
      "skilgen/core/requirements.py": [
        "from __future__ import annotations",
        "imports json",
        "imports hashlib",
        "from pathlib import Path",
        "from skilgen.core.document_ingestion import extract_document_text",
        "from skilgen.core.models import ProjectIntent, RequirementsContext",
        "function extract_text",
        "function normalize_lines",
        "function detect_domains",
        "function summarize_requirements"
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
        "from datetime import UTC, datetime",
        "from pathlib import Path",
        "from threading import Lock",
        "from skilgen.agents.codebase_signals import CODE_EXTENSIONS, IGNORED_PARTS",
        "from skilgen.core.context import build_codebase_context",
        "from skilgen.core.freshness import compute_freshness_report, load_freshness_state",
        "from skilgen.core.requirements import load_project_context"
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
        "from skilgen.agents.codebase_signals import clear_codebase_signal_caches",
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
      "tests/test_rate_limit_store.py": [
        "from __future__ import annotations",
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports unittest",
        "from skilgen.core.rate_limit_store import consume_rate_limit",
        "class RateLimitStoreTests"
      ],
      "tests/test_relationship_mapper.py": [
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports unittest",
        "from skilgen.agents.relationship_mapper import build_import_graph",
        "class RelationshipMapperTests"
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
        "from skilgen.core.repo_state import classify_repo_change",
        "from skilgen.core.score import compute_skillgen_score, load_score_history, record_score_history, score_history_payload",
        "class ScoreTests"
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
      "tests/test_source_graphs.py": [
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports unittest",
        "from skilgen.agents.source_graphs import build_call_graph, build_config_runtime_graph, build_parser_summary, build_symbol_graph",
        "from skilgen.agents.language_parsers import parse_language_evidence",
        "class SourceGraphTests"
      ],
      "tests/test_validate_cli.py": [
        "imports json",
        "imports subprocess",
        "imports sys",
        "imports unittest",
        "class ValidateCliTests"
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
        "isinstance",
        "isoformat",
        "kill"
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
        "_infer_percent",
        "_render_line",
        "activate_external_skill",
        "activate_mcp_connector",
        "active_external_skills",
        "active_mcp_connectors",
        "add_argument",
        "add_parser",
        "add_subparsers",
        "analytics_payload",
        "analyze_payload",
        "append",
        "architecture_payload",
        "auto_update_status",
        "build_corpus_index",
        "build_import_graph"
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
        "iterdir",
        "list",
        "relative_to"
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
        "DependencyRiskEdge",
        "DependencyRiskGraph",
        "DependencyRiskNode",
        "Path",
        "_cargo_deps",
        "_external_dependency_signals",
        "_find_cycles",
        "_go_mod_deps",
        "_load_json",
        "_manifest_dependencies",
        "_package_json_deps",
        "_pyproject_deps",
        "_requirements_deps",
        "add",
        "any",
        "append",
        "as_posix",
        "build_import_graph",
        "build_workspace_graph",
        "compile",
        "extend",
        "fromkeys",
        "get",
        "group"
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
        "_hash_file",
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
        "exists",
        "get",
        "hexdigest",
        "is_file",
        "is_generated_output_path",
        "items",
        "list",
        "loads",
        "mkdir",
        "read_bytes",
        "read_text"
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
        "isinstance",
        "join",
        "len",
        "load_requirements",
        "loads",
        "lower",
        "normalize_lines",
        "read_text"
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
        "_iter_source_files",
        "_materialized_domains",
        "_nodes_by_domain",
        "_parse_check_paths",
        "_parse_references",
        "_quality_gates",
        "_resolve_placeholder_path",
        "_score_history_path",
        "_score_rating",
        "_skill_content"
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
        "join"
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
        "add",
        "analyze_codebase",
        "any",
        "append",
        "as_posix"
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
      "tests/test_diff.py": [
        "Path",
        "TemporaryDirectory",
        "_save_baseline",
        "assertEqual",
        "assertIn",
        "assertTrue",
        "build_codebase_context",
        "compute_diff",
        "isdisjoint",
        "load_project_context",
        "loads",
        "main",
        "mkdir",
        "run",
        "save_freshness_state",
        "set",
        "snapshot_freshness_state",
        "str",
        "unlink",
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
        "assertTrue",
        "classify_repo_change",
        "compute_skillgen_score",
        "join",
        "len",
        "load_score_history",
        "main",
        "mkdir",
        "range",
        "record_score_history",
        "run",
        "score_history_payload",
        "start",
        "str",
        "strip"
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
      "tests/test_validate_cli.py": [
        "assertIn",
        "loads",
        "main",
        "run"
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
      "pyproject.toml": [
        "env:LICENSE",
        "env:MIT",
        "env:OSI",
        "env:README"
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
        "skilgen/core/rate_limit_store.py"
      ],
      "tests/test_jobs.py": [
        "skilgen/api/jobs.py"
      ],
      "tests/test_model_registry.py": [
        "skilgen/agents/model_registry.py"
      ],
      "tests/test_plan_cli.py": [
        "skilgen/cli/__init__.py",
        "skilgen/cli/main.py"
      ],
      "tests/test_rate_limit_store.py": [
        "skilgen/core/rate_limit_store.py",
        "skilgen/core/identity_policy_store.py"
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
      "tests/test_sdk.py": [
        "skilgen/sdk.py"
      ],
      "tests/test_source_graphs.py": [
        "skilgen/agents/source_graphs.py"
      ],
      "tests/test_validate_cli.py": [
        "skilgen/cli/__init__.py",
        "skilgen/cli/main.py"
      ],
      "tests/test_workspace_graph.py": [
        "skilgen/agents/workspace_graph.py",
        "skilgen/agents/domain_graph_planner.py",
        "skilgen/agents/evidence_graph.py"
      ]
    },
    "workspace_graph": {
      "tool": null,
      "packages": [],
      "dependencies": [],
      "entrypoints": [],
      "confidence": 0.0,
      "detection_evidence": []
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
        "source_path": "tests/test_rate_limit_store.py",
        "source_symbol": "RateLimitStoreTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
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
      "artifacts": [],
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
          "id": "package:PyYAML",
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
          "id": "package:openpyxl",
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
          "id": "package:tree-sitter-language-pack",
          "kind": "external-package",
          "risk_score": 0.2,
          "signals": [
            "version:loosely-pinned"
          ],
          "dependencies": []
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
            "skilgen/core/evals.py",
            "skilgen/core/runtime_data.py"
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
            "json",
            "pathlib",
            "re",
            "skilgen/agents/codebase_signals.py",
            "skilgen/core/context.py",
            "skilgen/core/freshness.py",
            "skilgen/core/requirements.py",
            "skilgen/core/validation.py",
            "threading"
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
          "id": "manifest:pyproject.toml",
          "kind": "manifest",
          "risk_score": 0.0,
          "signals": [],
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
            "tree-sitter-language-pack"
          ]
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
          "id": "tests/test_score.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "pathlib",
            "skilgen/core/repo_state.py",
            "skilgen/core/score.py",
            "subprocess",
            "tempfile",
            "threading",
            "unittest"
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
        }
      ],
      "edges": [
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
          "target": "package:beautifulsoup4",
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
          "target": "package:pypdf",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
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
          "target": "package:tree-sitter-language-pack",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
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
          "source": "tests/test_rate_limit_store.py",
          "target": "skilgen/core/rate_limit_store.py",
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
          "source": "tests/test_workspace_graph.py",
          "target": "skilgen/agents/workspace_graph.py",
          "kind": "repo-import",
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
        "High fan-out dependency hotspots surfaced in: skilgen/agents/__init__.py, skilgen/agents/architecture_planner.py, skilgen/agents/codebase_signals.py, skilgen/agents/decision_planner.py, skilgen/agents/evidence_graph.py.",
        "Loosely pinned external dependencies increase drift risk: package:PyYAML, package:beautifulsoup4, package:cryptography, package:deepagents, package:langchain, package:langchain-anthropic."
      ]
    }
  },
  "architecture": {
    "headline": "Evidence-backed architecture blueprint for the codebase",
    "system_summary": "Skilgen identified 2 top-level architecture domains from 38 evidence items and 12 domain graph nodes. Parser backends in use: empty, python-ast, regex. Source comprehension currently tracks 101 symbol-bearing files, 98 call-bearing files, 43 mapped tests, and 0 workspace packages.",
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
