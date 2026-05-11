# Analysis

```json
{
  "framework_fingerprint": {
    "frontend": {
      "name": "react",
      "confidence": 0.99,
      "evidence": [
        "package.json",
        "src/",
        ".tsx"
      ]
    },
    "backend": {
      "name": "fastapi",
      "confidence": 0.99,
      "evidence": [
        "main.py",
        "app/api",
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
      "tests/test_api_key.py",
      "tests/test_api_smoke.py",
      "tests/test_api_spec_parsers.py",
      "tests/test_architecture_cli.py",
      "tests/test_architecture_planner.py",
      "tests/test_audit.py",
      "tests/test_audit_log.py",
      "tests/test_auth_claim_mapping.py",
      "tests/test_auth_tokens.py",
      "tests/test_autoupdate.py",
      "tests/test_cli.py",
      "tests/test_cli_sources.py",
      "tests/test_codebase_signals.py",
      "tests/test_config.py",
      "tests/test_context.py",
      "tests/test_corpus_cli.py",
      "tests/test_corpus_index.py",
      "tests/test_dashboard_cli.py",
      "tests/test_dashboard_error_boundaries.py",
      "tests/test_data_parsers.py",
      "tests/test_decision_planner.py",
      "tests/test_delivery.py",
      "tests/test_dependency_risk.py",
      "tests/test_dependency_risk_graph_workstream.py",
      "tests/test_diff.py",
      "tests/test_document_ingestion.py",
      "tests/test_domain_graph_planner.py",
      "tests/test_enterprise_document_formats.py",
      "tests/test_enterprise_policy_cli.py",
      "tests/test_eval.py",
      "tests/test_eval_cli.py",
      "tests/test_feature_extractor.py",
      "tests/test_framework_fingerprint.py",
      "tests/test_generation_quality.py",
      "tests/test_half_life.py",
      "tests/test_identity_policy_store.py",
      "tests/test_improvement_loop.py",
      "tests/test_incident_parsers.py",
      "tests/test_infra_parsers.py",
      "tests/test_jobs.py",
      "tests/test_llm_config.py",
      "tests/test_memory_capture.py",
      "tests/test_memory_cli.py",
      "tests/test_model_registry.py",
      "tests/test_org_intelligence_api.py",
      "tests/test_org_settings.py",
      "tests/test_overview_data.py",
      "tests/test_packaging.py",
      "tests/test_plan_cli.py",
      "tests/test_policy_engine.py",
      "tests/test_pr_comment.py",
      "tests/test_pr_comment_dedup.py",
      "tests/test_process_parsers.py",
      "tests/test_rate_limit_store.py",
      "tests/test_red_flags.py",
      "tests/test_registry.py",
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
      "tests/test_security_parsers.py",
      "tests/test_skill_detail.py",
      "tests/test_skill_sources_api.py",
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
    "data_models": [
      "skilgen/parsers/sql_schema.py"
    ],
    "persistence_layers": [
      "skilgen/parsers/dbt.py",
      "skilgen/parsers/sql_schema.py"
    ],
    "background_jobs": [
      "skilgen/api/jobs.py",
      "tests/test_jobs.py"
    ],
    "auth_files": [
      "skilgen/core/auth_tokens.py",
      "skilgen/parsers/security_policy.py",
      "tests/test_auth_claim_mapping.py",
      "tests/test_auth_tokens.py",
      "tests/test_security_parsers.py"
    ],
    "state_files": [],
    "design_system_files": [],
    "legacy_programs": [],
    "copybooks": [],
    "language_inventory": {
      "python": 179,
      "typescript": 4
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
        "name": "requirements",
        "summary": "Planning and product-intent domain used to keep the skill tree aligned with requirements and changing scope.",
        "confidence": 0.99,
        "key_files": [
          "README.md"
        ],
        "key_patterns": [
          "requirements-first planning",
          "skill scaffolding",
          "agent operating guidance"
        ],
        "parent_domain": null,
        "child_domains": [],
        "related_domains": [
          "backend",
          "frontend",
          "roadmap"
        ],
        "skill_path": "skills/requirements/SKILL.md"
      },
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
          "scripts/deploy_web.py",
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
      "name": "requirements",
      "confidence": 0.99,
      "key_files": [
        "README.md"
      ],
      "key_patterns": [
        "requirements-first planning",
        "skill scaffolding",
        "agent operating guidance"
      ],
      "sub_domains": []
    },
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
        "scripts/deploy_web.py",
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
      "path": "skills/requirements/SKILL.md",
      "domain": "requirements",
      "parent_skill": null,
      "child_skills": [],
      "cross_references": [
        "skills/roadmap/SKILL.md"
      ]
    },
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
        "skills/requirements/SKILL.md",
        "skills/roadmap/SKILL.md"
      ]
    },
    {
      "path": "skills/platform/runtime/SKILL.md",
      "domain": "platform-runtime",
      "parent_skill": "skills/platform/SKILL.md",
      "child_skills": [],
      "cross_references": [
        "skills/requirements/SKILL.md",
        "skills/roadmap/SKILL.md"
      ]
    },
    {
      "path": "skills/platform/agents/SKILL.md",
      "domain": "platform-agents",
      "parent_skill": "skills/platform/SKILL.md",
      "child_skills": [],
      "cross_references": [
        "skills/requirements/SKILL.md",
        "skills/roadmap/SKILL.md"
      ]
    },
    {
      "path": "skills/platform/cli/SKILL.md",
      "domain": "platform-cli",
      "parent_skill": "skills/platform/SKILL.md",
      "child_skills": [],
      "cross_references": [
        "skills/requirements/SKILL.md",
        "skills/roadmap/SKILL.md"
      ]
    },
    {
      "path": "skills/platform/core/SKILL.md",
      "domain": "platform-core",
      "parent_skill": "skills/platform/SKILL.md",
      "child_skills": [],
      "cross_references": [
        "skills/requirements/SKILL.md",
        "skills/roadmap/SKILL.md"
      ]
    },
    {
      "path": "skills/platform/generators/SKILL.md",
      "domain": "platform-generators",
      "parent_skill": "skills/platform/SKILL.md",
      "child_skills": [],
      "cross_references": [
        "skills/requirements/SKILL.md",
        "skills/roadmap/SKILL.md"
      ]
    },
    {
      "path": "skills/platform/scripts/SKILL.md",
      "domain": "platform-scripts",
      "parent_skill": "skills/platform/SKILL.md",
      "child_skills": [],
      "cross_references": [
        "skills/requirements/SKILL.md",
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
      "cross_references": [
        "skills/requirements/SKILL.md"
      ]
    },
    {
      "path": "skills/roadmap/phase-0/SKILL.md",
      "domain": "roadmap-phase-0",
      "parent_skill": "skills/roadmap/SKILL.md",
      "child_skills": [],
      "cross_references": [
        "skills/requirements/SKILL.md"
      ]
    },
    {
      "path": "skills/roadmap/phase-1/SKILL.md",
      "domain": "roadmap-phase-1",
      "parent_skill": "skills/roadmap/SKILL.md",
      "child_skills": [],
      "cross_references": [
        "skills/requirements/SKILL.md"
      ]
    },
    {
      "path": "skills/roadmap/phase-2/SKILL.md",
      "domain": "roadmap-phase-2",
      "parent_skill": "skills/roadmap/SKILL.md",
      "child_skills": [],
      "cross_references": [
        "skills/requirements/SKILL.md"
      ]
    },
    {
      "path": "skills/roadmap/phase-3/SKILL.md",
      "domain": "roadmap-phase-3",
      "parent_skill": "skills/roadmap/SKILL.md",
      "child_skills": [],
      "cross_references": [
        "skills/requirements/SKILL.md"
      ]
    }
  ],
  "import_graph": {
    "extensions/vscode-skillayer/src/check.ts": [
      "vscode"
    ],
    "extensions/vscode-skillayer/src/config.ts": [
      "vscode"
    ],
    "extensions/vscode-skillayer/src/diagnostics.ts": [
      "extensions/vscode-skillayer/src/check.ts",
      "vscode"
    ],
    "extensions/vscode-skillayer/src/extension.ts": [
      "extensions/vscode-skillayer/src/check.ts",
      "extensions/vscode-skillayer/src/config.ts",
      "extensions/vscode-skillayer/src/diagnostics.ts",
      "vscode"
    ],
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
    "scripts/deploy_web.py": [
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
      "datetime",
      "json",
      "os",
      "pathlib",
      "skilgen/__init__.py",
      "skilgen/agents/__init__.py",
      "skilgen/agents/requirements_parser.py",
      "skilgen/api/server.py",
      "skilgen/api/service.py",
      "skilgen/autoupdate.py",
      "skilgen/commands/check.py",
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
      "skilgen/hooks/cursor_watcher.py",
      "skilgen/parsers/runner.py",
      "skilgen/parsers/sources.py",
      "skilgen/registry_client.py",
      "sys",
      "threading",
      "time",
      "urllib.error",
      "urllib.parse",
      "urllib.request",
      "uuid"
    ],
    "skilgen/commands/__init__.py": [],
    "skilgen/commands/check.py": [
      "__future__",
      "dataclasses",
      "json",
      "os",
      "pathlib",
      "subprocess",
      "sys",
      "typing",
      "urllib.error",
      "urllib.request"
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
      "asyncio",
      "dataclasses",
      "json",
      "os",
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
      "typing",
      "urllib.error",
      "urllib.request",
      "uuid"
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
      "re",
      "skilgen/agents/architecture_planner.py",
      "skilgen/agents/codebase_signals.py",
      "skilgen/agents/requirements_parser.py",
      "skilgen/agents/roadmap_planner.py",
      "skilgen/core/analytics.py",
      "skilgen/core/config.py",
      "skilgen/core/context.py",
      "skilgen/core/dependency_risk.py",
      "skilgen/core/models.py",
      "skilgen/deep_agents_core.py",
      "typing"
    ],
    "skilgen/hooks/__init__.py": [],
    "skilgen/hooks/claude_code.py": [
      "__future__",
      "pathlib"
    ],
    "skilgen/hooks/claude_code_hook.py": [
      "__future__",
      "json",
      "os",
      "pathlib",
      "skilgen/core/analytics.py",
      "sys",
      "time",
      "typing",
      "urllib.request"
    ],
    "skilgen/hooks/cursor.py": [
      "__future__",
      "pathlib"
    ],
    "skilgen/hooks/cursor_watcher.py": [
      "__future__",
      "os",
      "pathlib",
      "skilgen/core/analytics.py",
      "subprocess",
      "sys",
      "time"
    ],
    "skilgen/parsers/__init__.py": [
      "__future__",
      "dataclasses",
      "skilgen/parsers/dbt.py",
      "skilgen/parsers/helm.py",
      "skilgen/parsers/kafka.py",
      "skilgen/parsers/kubernetes.py",
      "skilgen/parsers/runbook.py",
      "skilgen/parsers/sarif.py",
      "skilgen/parsers/sbom.py",
      "skilgen/parsers/security_policy.py",
      "skilgen/parsers/sql_schema.py",
      "skilgen/parsers/terraform.py"
    ],
    "skilgen/parsers/auto_detect.py": [
      "__future__",
      "pathlib",
      "skilgen/core/config.py",
      "skilgen/core/models.py",
      "skilgen/parsers/sources.py",
      "typing"
    ],
    "skilgen/parsers/confluence.py": [
      "__future__",
      "html.parser",
      "pathlib",
      "re",
      "skilgen/parsers/runbook.py",
      "tempfile",
      "xml.etree.ElementTree",
      "zipfile"
    ],
    "skilgen/parsers/dbt.py": [
      "__future__",
      "dataclasses",
      "pathlib",
      "re",
      "typing",
      "yaml"
    ],
    "skilgen/parsers/graphql.py": [
      "__future__",
      "json",
      "pathlib",
      "re",
      "skilgen/parsers/__init__.py",
      "typing"
    ],
    "skilgen/parsers/helm.py": [
      "__future__",
      "collections",
      "dataclasses",
      "pathlib",
      "re",
      "typing",
      "yaml"
    ],
    "skilgen/parsers/incident.py": [
      "__future__",
      "collections",
      "dataclasses",
      "datetime",
      "json",
      "os",
      "pathlib",
      "re",
      "time",
      "typing",
      "urllib.error",
      "urllib.parse",
      "urllib.request"
    ],
    "skilgen/parsers/kafka.py": [
      "__future__",
      "dataclasses",
      "json",
      "pathlib",
      "typing",
      "yaml"
    ],
    "skilgen/parsers/kubernetes.py": [
      "__future__",
      "collections",
      "dataclasses",
      "pathlib",
      "typing",
      "yaml"
    ],
    "skilgen/parsers/notion.py": [
      "__future__",
      "httpx",
      "json",
      "os",
      "pathlib",
      "skilgen/parsers/runbook.py",
      "time",
      "typing"
    ],
    "skilgen/parsers/openapi.py": [
      "__future__",
      "collections.abc",
      "json",
      "pathlib",
      "re",
      "skilgen/parsers/__init__.py",
      "typing",
      "yaml"
    ],
    "skilgen/parsers/postman.py": [
      "__future__",
      "json",
      "pathlib",
      "re",
      "skilgen/parsers/__init__.py",
      "typing"
    ],
    "skilgen/parsers/runbook.py": [
      "__future__",
      "dataclasses",
      "pathlib",
      "re"
    ],
    "skilgen/parsers/runner.py": [
      "__future__",
      "pathlib",
      "skilgen/core/models.py",
      "skilgen/parsers/auto_detect.py",
      "skilgen/parsers/sources.py",
      "typing"
    ],
    "skilgen/parsers/sarif.py": [
      "__future__",
      "dataclasses",
      "json",
      "pathlib",
      "re",
      "typing"
    ],
    "skilgen/parsers/sbom.py": [
      "__future__",
      "dataclasses",
      "json",
      "pathlib",
      "re",
      "skilgen/core/dependency_risk.py",
      "typing",
      "urllib.parse",
      "xml.etree"
    ],
    "skilgen/parsers/security_policy.py": [
      "__future__",
      "dataclasses",
      "json",
      "pathlib",
      "re",
      "typing",
      "yaml"
    ],
    "skilgen/parsers/sources.py": [
      "__future__",
      "dataclasses",
      "importlib",
      "pathlib",
      "re",
      "typing"
    ],
    "skilgen/parsers/sql_schema.py": [
      "__future__",
      "dataclasses",
      "json",
      "pathlib",
      "re",
      "typing"
    ],
    "skilgen/parsers/terraform.py": [
      "__future__",
      "collections",
      "dataclasses",
      "hcl2",
      "pathlib",
      "re"
    ],
    "skilgen/registry_client.py": [
      "__future__",
      "json",
      "os",
      "pathlib",
      "typing",
      "urllib.error",
      "urllib.parse",
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
    "tests/test_api_key.py": [
      "__future__",
      "apps/api/api/auth.py",
      "apps/api/api/routes/orgs.py",
      "asyncio",
      "fastapi",
      "fastapi.testclient",
      "packages/db/database.py",
      "types",
      "typing"
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
    "tests/test_api_spec_parsers.py": [
      "__future__",
      "pathlib",
      "skilgen/parsers/__init__.py",
      "skilgen/parsers/graphql.py",
      "skilgen/parsers/openapi.py",
      "skilgen/parsers/postman.py",
      "tempfile",
      "unittest"
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
    "tests/test_audit_log.py": [
      "__future__",
      "apps/api/api/routes/orgs.py",
      "apps/api/api/services/audit.py",
      "datetime",
      "types",
      "unittest"
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
    "tests/test_cli_sources.py": [
      "__future__",
      "apps/api/api/analysis.py",
      "pathlib",
      "skilgen/cli/main.py",
      "skilgen/parsers/auto_detect.py",
      "skilgen/parsers/runner.py",
      "tempfile"
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
    "tests/test_dashboard_error_boundaries.py": [
      "__future__",
      "pathlib"
    ],
    "tests/test_data_parsers.py": [
      "pathlib",
      "skilgen/parsers/dbt.py",
      "skilgen/parsers/kafka.py",
      "skilgen/parsers/sql_schema.py",
      "tempfile",
      "unittest"
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
    "tests/test_eval.py": [
      "__future__",
      "apps/api/api/auth.py",
      "datetime",
      "fastapi",
      "fastapi.testclient",
      "importlib",
      "packages/db/database.py",
      "pytest",
      "types",
      "typing"
    ],
    "tests/test_eval_cli.py": [
      "__future__",
      "pytest",
      "skilgen/cli/main.py",
      "sys"
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
    "tests/test_generation_quality.py": [
      "__future__",
      "asyncio",
      "json",
      "os",
      "pathlib",
      "skilgen/core/analytics.py",
      "skilgen/core/models.py",
      "skilgen/delivery.py",
      "skilgen/generators/skills.py",
      "skilgen/hooks/claude_code_hook.py",
      "skilgen/hooks/cursor_watcher.py",
      "tempfile",
      "time",
      "unittest",
      "unittest.mock"
    ],
    "tests/test_half_life.py": [
      "__future__",
      "apps/api/api/services/half_life.py",
      "datetime",
      "pathlib",
      "types"
    ],
    "tests/test_identity_policy_store.py": [
      "__future__",
      "os",
      "pathlib",
      "skilgen/core/identity_policy_store.py",
      "tempfile",
      "unittest"
    ],
    "tests/test_improvement_loop.py": [
      "__future__",
      "apps/api/api/routes/repos.py",
      "datetime",
      "pathlib",
      "types"
    ],
    "tests/test_incident_parsers.py": [
      "__future__",
      "pathlib",
      "skilgen/parsers/incident.py",
      "tempfile",
      "unittest",
      "unittest.mock"
    ],
    "tests/test_infra_parsers.py": [
      "__future__",
      "pathlib",
      "skilgen/parsers/helm.py",
      "skilgen/parsers/kubernetes.py",
      "skilgen/parsers/terraform.py",
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
    "tests/test_llm_config.py": [
      "__future__",
      "apps/api/api/services/llm_config.py",
      "unittest"
    ],
    "tests/test_memory_capture.py": [
      "__future__",
      "apps/api/api/services/memory.py",
      "asyncio",
      "dataclasses",
      "datetime",
      "packages/db/models/__init__.py",
      "pathlib",
      "pytest"
    ],
    "tests/test_memory_cli.py": [
      "__future__",
      "http.server",
      "json",
      "os",
      "pathlib",
      "subprocess",
      "sys",
      "threading"
    ],
    "tests/test_model_registry.py": [
      "os",
      "skilgen/agents/model_registry.py",
      "skilgen/core/models.py",
      "unittest"
    ],
    "tests/test_org_intelligence_api.py": [
      "__future__",
      "apps/api/api/auth.py",
      "apps/api/api/routes/orgs.py",
      "datetime",
      "fastapi",
      "fastapi.testclient",
      "packages/db/database.py",
      "packages/db/models/__init__.py",
      "typing"
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
    "tests/test_policy_engine.py": [
      "__future__",
      "apps/api/api/services/policy.py",
      "datetime",
      "types",
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
    "tests/test_process_parsers.py": [
      "__future__",
      "json",
      "pathlib",
      "skilgen/parsers/confluence.py",
      "skilgen/parsers/notion.py",
      "skilgen/parsers/runbook.py",
      "tempfile",
      "unittest",
      "zipfile"
    ],
    "tests/test_rate_limit_store.py": [
      "__future__",
      "pathlib",
      "skilgen/core/rate_limit_store.py",
      "tempfile",
      "unittest"
    ],
    "tests/test_red_flags.py": [
      "__future__",
      "apps/api/api/auth.py",
      "apps/api/api/routes/orgs.py",
      "apps/api/api/services/redflags.py",
      "datetime",
      "fastapi",
      "fastapi.testclient",
      "packages/db/database.py",
      "packages/db/models/__init__.py",
      "typing"
    ],
    "tests/test_registry.py": [
      "__future__",
      "apps/api/api/routes/registry.py",
      "datetime",
      "pathlib",
      "types"
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
    "tests/test_security_parsers.py": [
      "__future__",
      "json",
      "pathlib",
      "skilgen/parsers/sarif.py",
      "skilgen/parsers/sbom.py",
      "skilgen/parsers/security_policy.py",
      "tempfile",
      "unittest"
    ],
    "tests/test_skill_detail.py": [
      "__future__",
      "apps/api/api/routes/skills.py",
      "asyncio",
      "pathlib",
      "types"
    ],
    "tests/test_skill_sources_api.py": [
      "__future__",
      "apps/api/api/routes/repos.py",
      "packages/db/models/skill.py",
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
      "packages/db/models/__init__.py",
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
      "packages/db/models/__init__.py",
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
      "python": 179,
      "typescript": 4
    },
    "dominant_languages": [
      "python",
      "typescript"
    ],
    "import_graph": {
      "extensions/vscode-skillayer/src/check.ts": [
        "vscode"
      ],
      "extensions/vscode-skillayer/src/config.ts": [
        "vscode"
      ],
      "extensions/vscode-skillayer/src/diagnostics.ts": [
        "extensions/vscode-skillayer/src/check.ts",
        "vscode"
      ],
      "extensions/vscode-skillayer/src/extension.ts": [
        "extensions/vscode-skillayer/src/check.ts",
        "extensions/vscode-skillayer/src/config.ts",
        "extensions/vscode-skillayer/src/diagnostics.ts",
        "vscode"
      ],
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
      "scripts/deploy_web.py": [
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
        "datetime",
        "json",
        "os",
        "pathlib",
        "skilgen/__init__.py",
        "skilgen/agents/__init__.py",
        "skilgen/agents/requirements_parser.py",
        "skilgen/api/server.py",
        "skilgen/api/service.py",
        "skilgen/autoupdate.py",
        "skilgen/commands/check.py",
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
        "skilgen/hooks/cursor_watcher.py",
        "skilgen/parsers/runner.py",
        "skilgen/parsers/sources.py",
        "skilgen/registry_client.py",
        "sys",
        "threading",
        "time",
        "urllib.error",
        "urllib.parse",
        "urllib.request",
        "uuid"
      ],
      "skilgen/commands/__init__.py": [],
      "skilgen/commands/check.py": [
        "__future__",
        "dataclasses",
        "json",
        "os",
        "pathlib",
        "subprocess",
        "sys",
        "typing",
        "urllib.error",
        "urllib.request"
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
        "asyncio",
        "dataclasses",
        "json",
        "os",
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
        "typing",
        "urllib.error",
        "urllib.request",
        "uuid"
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
        "re",
        "skilgen/agents/architecture_planner.py",
        "skilgen/agents/codebase_signals.py",
        "skilgen/agents/requirements_parser.py",
        "skilgen/agents/roadmap_planner.py",
        "skilgen/core/analytics.py",
        "skilgen/core/config.py",
        "skilgen/core/context.py",
        "skilgen/core/dependency_risk.py",
        "skilgen/core/models.py",
        "skilgen/deep_agents_core.py",
        "typing"
      ],
      "skilgen/hooks/__init__.py": [],
      "skilgen/hooks/claude_code.py": [
        "__future__",
        "pathlib"
      ],
      "skilgen/hooks/claude_code_hook.py": [
        "__future__",
        "json",
        "os",
        "pathlib",
        "skilgen/core/analytics.py",
        "sys",
        "time",
        "typing",
        "urllib.request"
      ],
      "skilgen/hooks/cursor.py": [
        "__future__",
        "pathlib"
      ],
      "skilgen/hooks/cursor_watcher.py": [
        "__future__",
        "os",
        "pathlib",
        "skilgen/core/analytics.py",
        "subprocess",
        "sys",
        "time"
      ],
      "skilgen/parsers/__init__.py": [
        "__future__",
        "dataclasses",
        "skilgen/parsers/dbt.py",
        "skilgen/parsers/helm.py",
        "skilgen/parsers/kafka.py",
        "skilgen/parsers/kubernetes.py",
        "skilgen/parsers/runbook.py",
        "skilgen/parsers/sarif.py",
        "skilgen/parsers/sbom.py",
        "skilgen/parsers/security_policy.py",
        "skilgen/parsers/sql_schema.py",
        "skilgen/parsers/terraform.py"
      ],
      "skilgen/parsers/auto_detect.py": [
        "__future__",
        "pathlib",
        "skilgen/core/config.py",
        "skilgen/core/models.py",
        "skilgen/parsers/sources.py",
        "typing"
      ],
      "skilgen/parsers/confluence.py": [
        "__future__",
        "html.parser",
        "pathlib",
        "re",
        "skilgen/parsers/runbook.py",
        "tempfile",
        "xml.etree.ElementTree",
        "zipfile"
      ],
      "skilgen/parsers/dbt.py": [
        "__future__",
        "dataclasses",
        "pathlib",
        "re",
        "typing",
        "yaml"
      ],
      "skilgen/parsers/graphql.py": [
        "__future__",
        "json",
        "pathlib",
        "re",
        "skilgen/parsers/__init__.py",
        "typing"
      ],
      "skilgen/parsers/helm.py": [
        "__future__",
        "collections",
        "dataclasses",
        "pathlib",
        "re",
        "typing",
        "yaml"
      ],
      "skilgen/parsers/incident.py": [
        "__future__",
        "collections",
        "dataclasses",
        "datetime",
        "json",
        "os",
        "pathlib",
        "re",
        "time",
        "typing",
        "urllib.error",
        "urllib.parse",
        "urllib.request"
      ],
      "skilgen/parsers/kafka.py": [
        "__future__",
        "dataclasses",
        "json",
        "pathlib",
        "typing",
        "yaml"
      ],
      "skilgen/parsers/kubernetes.py": [
        "__future__",
        "collections",
        "dataclasses",
        "pathlib",
        "typing",
        "yaml"
      ],
      "skilgen/parsers/notion.py": [
        "__future__",
        "httpx",
        "json",
        "os",
        "pathlib",
        "skilgen/parsers/runbook.py",
        "time",
        "typing"
      ],
      "skilgen/parsers/openapi.py": [
        "__future__",
        "collections.abc",
        "json",
        "pathlib",
        "re",
        "skilgen/parsers/__init__.py",
        "typing",
        "yaml"
      ],
      "skilgen/parsers/postman.py": [
        "__future__",
        "json",
        "pathlib",
        "re",
        "skilgen/parsers/__init__.py",
        "typing"
      ],
      "skilgen/parsers/runbook.py": [
        "__future__",
        "dataclasses",
        "pathlib",
        "re"
      ],
      "skilgen/parsers/runner.py": [
        "__future__",
        "pathlib",
        "skilgen/core/models.py",
        "skilgen/parsers/auto_detect.py",
        "skilgen/parsers/sources.py",
        "typing"
      ],
      "skilgen/parsers/sarif.py": [
        "__future__",
        "dataclasses",
        "json",
        "pathlib",
        "re",
        "typing"
      ],
      "skilgen/parsers/sbom.py": [
        "__future__",
        "dataclasses",
        "json",
        "pathlib",
        "re",
        "skilgen/core/dependency_risk.py",
        "typing",
        "urllib.parse",
        "xml.etree"
      ],
      "skilgen/parsers/security_policy.py": [
        "__future__",
        "dataclasses",
        "json",
        "pathlib",
        "re",
        "typing",
        "yaml"
      ],
      "skilgen/parsers/sources.py": [
        "__future__",
        "dataclasses",
        "importlib",
        "pathlib",
        "re",
        "typing"
      ],
      "skilgen/parsers/sql_schema.py": [
        "__future__",
        "dataclasses",
        "json",
        "pathlib",
        "re",
        "typing"
      ],
      "skilgen/parsers/terraform.py": [
        "__future__",
        "collections",
        "dataclasses",
        "hcl2",
        "pathlib",
        "re"
      ],
      "skilgen/registry_client.py": [
        "__future__",
        "json",
        "os",
        "pathlib",
        "typing",
        "urllib.error",
        "urllib.parse",
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
      "tests/test_api_key.py": [
        "__future__",
        "apps/api/api/auth.py",
        "apps/api/api/routes/orgs.py",
        "asyncio",
        "fastapi",
        "fastapi.testclient",
        "packages/db/database.py",
        "types",
        "typing"
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
      "tests/test_api_spec_parsers.py": [
        "__future__",
        "pathlib",
        "skilgen/parsers/__init__.py",
        "skilgen/parsers/graphql.py",
        "skilgen/parsers/openapi.py",
        "skilgen/parsers/postman.py",
        "tempfile",
        "unittest"
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
      "tests/test_audit_log.py": [
        "__future__",
        "apps/api/api/routes/orgs.py",
        "apps/api/api/services/audit.py",
        "datetime",
        "types",
        "unittest"
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
      "tests/test_cli_sources.py": [
        "__future__",
        "apps/api/api/analysis.py",
        "pathlib",
        "skilgen/cli/main.py",
        "skilgen/parsers/auto_detect.py",
        "skilgen/parsers/runner.py",
        "tempfile"
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
      "tests/test_dashboard_error_boundaries.py": [
        "__future__",
        "pathlib"
      ],
      "tests/test_data_parsers.py": [
        "pathlib",
        "skilgen/parsers/dbt.py",
        "skilgen/parsers/kafka.py",
        "skilgen/parsers/sql_schema.py",
        "tempfile",
        "unittest"
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
      "tests/test_eval.py": [
        "__future__",
        "apps/api/api/auth.py",
        "datetime",
        "fastapi",
        "fastapi.testclient",
        "importlib",
        "packages/db/database.py",
        "pytest",
        "types",
        "typing"
      ],
      "tests/test_eval_cli.py": [
        "__future__",
        "pytest",
        "skilgen/cli/main.py",
        "sys"
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
      "tests/test_generation_quality.py": [
        "__future__",
        "asyncio",
        "json",
        "os",
        "pathlib",
        "skilgen/core/analytics.py",
        "skilgen/core/models.py",
        "skilgen/delivery.py",
        "skilgen/generators/skills.py",
        "skilgen/hooks/claude_code_hook.py",
        "skilgen/hooks/cursor_watcher.py",
        "tempfile",
        "time",
        "unittest",
        "unittest.mock"
      ],
      "tests/test_half_life.py": [
        "__future__",
        "apps/api/api/services/half_life.py",
        "datetime",
        "pathlib",
        "types"
      ],
      "tests/test_identity_policy_store.py": [
        "__future__",
        "os",
        "pathlib",
        "skilgen/core/identity_policy_store.py",
        "tempfile",
        "unittest"
      ],
      "tests/test_improvement_loop.py": [
        "__future__",
        "apps/api/api/routes/repos.py",
        "datetime",
        "pathlib",
        "types"
      ],
      "tests/test_incident_parsers.py": [
        "__future__",
        "pathlib",
        "skilgen/parsers/incident.py",
        "tempfile",
        "unittest",
        "unittest.mock"
      ],
      "tests/test_infra_parsers.py": [
        "__future__",
        "pathlib",
        "skilgen/parsers/helm.py",
        "skilgen/parsers/kubernetes.py",
        "skilgen/parsers/terraform.py",
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
      "tests/test_llm_config.py": [
        "__future__",
        "apps/api/api/services/llm_config.py",
        "unittest"
      ],
      "tests/test_memory_capture.py": [
        "__future__",
        "apps/api/api/services/memory.py",
        "asyncio",
        "dataclasses",
        "datetime",
        "packages/db/models/__init__.py",
        "pathlib",
        "pytest"
      ],
      "tests/test_memory_cli.py": [
        "__future__",
        "http.server",
        "json",
        "os",
        "pathlib",
        "subprocess",
        "sys",
        "threading"
      ],
      "tests/test_model_registry.py": [
        "os",
        "skilgen/agents/model_registry.py",
        "skilgen/core/models.py",
        "unittest"
      ],
      "tests/test_org_intelligence_api.py": [
        "__future__",
        "apps/api/api/auth.py",
        "apps/api/api/routes/orgs.py",
        "datetime",
        "fastapi",
        "fastapi.testclient",
        "packages/db/database.py",
        "packages/db/models/__init__.py",
        "typing"
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
      "tests/test_policy_engine.py": [
        "__future__",
        "apps/api/api/services/policy.py",
        "datetime",
        "types",
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
      "tests/test_process_parsers.py": [
        "__future__",
        "json",
        "pathlib",
        "skilgen/parsers/confluence.py",
        "skilgen/parsers/notion.py",
        "skilgen/parsers/runbook.py",
        "tempfile",
        "unittest",
        "zipfile"
      ],
      "tests/test_rate_limit_store.py": [
        "__future__",
        "pathlib",
        "skilgen/core/rate_limit_store.py",
        "tempfile",
        "unittest"
      ],
      "tests/test_red_flags.py": [
        "__future__",
        "apps/api/api/auth.py",
        "apps/api/api/routes/orgs.py",
        "apps/api/api/services/redflags.py",
        "datetime",
        "fastapi",
        "fastapi.testclient",
        "packages/db/database.py",
        "packages/db/models/__init__.py",
        "typing"
      ],
      "tests/test_registry.py": [
        "__future__",
        "apps/api/api/routes/registry.py",
        "datetime",
        "pathlib",
        "types"
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
      "tests/test_security_parsers.py": [
        "__future__",
        "json",
        "pathlib",
        "skilgen/parsers/sarif.py",
        "skilgen/parsers/sbom.py",
        "skilgen/parsers/security_policy.py",
        "tempfile",
        "unittest"
      ],
      "tests/test_skill_detail.py": [
        "__future__",
        "apps/api/api/routes/skills.py",
        "asyncio",
        "pathlib",
        "types"
      ],
      "tests/test_skill_sources_api.py": [
        "__future__",
        "apps/api/api/routes/repos.py",
        "packages/db/models/skill.py",
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
        "packages/db/models/__init__.py",
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
        "packages/db/models/__init__.py",
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
        "path": "README.md",
        "kind": "requirements",
        "language": null,
        "tags": [
          "requirements"
        ],
        "snippet": [
          "# Skillayer",
          "Skillayer is a governance plane for AI coding agents. It helps platform, security, and engineering leadership answer the questions that matter once Claude Code, Codex, Cursor, GitHub Copilot, and internal agents are active across a company:",
          "- What did agents do across repos, tools, sessions, and users?",
          "- Which skills are trusted, stale, drifted, quarantined, or bound to policy?",
          "- Where is fleet risk increasing across agents, repos, skills, and critical operations?",
          "The current product direction is defined by `docs/PRD-v8.docx`: Skillayer v8 reduces the product to six enterprise surfaces and treats the older skill-generation system as the substrate underneath the governance experience.",
          "The migrated v8 app lives under `apps/dashboard/app/(v8)` and uses the Skillayer governance shell.",
          "| Activity | The default investigation homepage for live agent activity, sessions, replay, and heatmaps. | `/activity`, `/activity/live-feed`, `/activity/sessions`, `/activity/replay`, `/activity/heatmap` |"
        ],
        "related_imports": []
      },
      {
        "path": "packages/db/database.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "from collections.abc import AsyncGenerator",
          "import ssl",
          "from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine",
          "from packages.db.config import settings",
          "_engine: AsyncEngine | None = None",
          "_sessionmaker: async_sessionmaker[AsyncSession] | None = None",
          "def _database_url_and_connect_args() -> tuple[str, dict[str, object]]:",
          "database_url = settings.DATABASE_URL or settings.DATABASE_URL_UNPOOLED",
          "if database_url.startswith(\"postgres://\"):",
          "database_url = database_url.replace(\"postgres://\", \"postgresql+asyncpg://\", 1)",
          "elif database_url.startswith(\"postgresql://\"):"
        ],
        "related_imports": []
      },
      {
        "path": "apps/api/api/auth.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "import hmac",
          "import os",
          "import time",
          "from urllib.parse import urlparse",
          "from typing import Any",
          "import httpx",
          "from fastapi import Depends, Header, HTTPException",
          "from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer",
          "from jose import JWTError, jwk, jwt",
          "from jose.utils import base64url_decode",
          "from sqlalchemy import select"
        ],
        "related_imports": []
      },
      {
        "path": "packages/db/models/base.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "from datetime import datetime",
          "import uuid",
          "from sqlalchemy.orm import DeclarativeBase",
          "def utcnow() -> datetime:",
          "return datetime.utcnow()",
          "def new_uuid() -> str:",
          "return str(uuid.uuid4())",
          "class Base(DeclarativeBase):",
          "pass"
        ],
        "related_imports": []
      },
      {
        "path": "skilgen/core/models.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "from dataclasses import dataclass, field",
          "from pathlib import Path",
          "SourceConfigValue = bool | str | list[str]",
          "@dataclass(frozen=True)",
          "class SkillSpec:",
          "path: str",
          "name: str",
          "domain: str",
          "sub_domain: str",
          "overview: str",
          "checks: list[str]"
        ],
        "related_imports": [
          "__future__",
          "dataclasses",
          "pathlib"
        ]
      },
      {
        "path": "skilgen/agents/codebase_signals.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "import ast",
          "from functools import lru_cache",
          "import re",
          "from pathlib import Path",
          "from skilgen.core.config import load_config",
          "from skilgen.core.corpus_index import load_corpus_index",
          "from skilgen.core.deep_sampler import select_deep_read_targets",
          "from skilgen.core.document_ingestion import extract_document_text",
          "from skilgen.core.models import CodebaseSignals",
          "CODE_EXTENSIONS = {",
          "\".py\","
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
        "path": "packages/db/models/repo.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "from datetime import datetime",
          "from typing import TYPE_CHECKING",
          "from sqlalchemy import BigInteger, ForeignKey, String",
          "from sqlalchemy.orm import Mapped, mapped_column, relationship",
          "from packages.db.models.base import Base, new_uuid, utcnow",
          "if TYPE_CHECKING:",
          "from packages.db.models.analysis_run import AnalysisRun",
          "from packages.db.models.pull_request import Commit, PullRequest",
          "from packages.db.models.dependency import Dependency",
          "from packages.db.models.org import Org",
          "from packages.db.models.skill import Skill"
        ],
        "related_imports": []
      },
      {
        "path": "skilgen/core/config.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "from pathlib import Path",
          "from skilgen.core.models import CorpusSettings, SkilgenConfig, SourceConfigValue",
          "DEFAULT_CONFIG = SkilgenConfig(",
          "include_paths=[\".\"],",
          "exclude_paths=[\".git\", \"__pycache__\", \".venv\", \"node_modules\", \".skilgen\"],",
          "domains_override=[],",
          "skill_depth=2,",
          "update_trigger=\"auto\",",
          "langsmith_project=None,",
          "model_provider=\"openai\",",
          "model=\"gpt-4.1-mini\","
        ],
        "related_imports": [
          "__future__",
          "pathlib",
          "skilgen/core/models.py"
        ]
      },
      {
        "path": "apps/api/api/routes/orgs.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "import asyncio",
          "import base64",
          "from collections import Counter, defaultdict",
          "from itertools import combinations",
          "import json",
          "import socket",
          "import urllib.error",
          "import urllib.request",
          "from dataclasses import asdict",
          "from datetime import UTC, datetime, timedelta",
          "import hashlib"
        ],
        "related_imports": []
      },
      {
        "path": "skilgen/core/requirements.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "import json",
          "import hashlib",
          "from pathlib import Path",
          "from skilgen.agents.codebase_signals import is_ignored_path_parts, is_internal_skillayer_monorepo",
          "from skilgen.core.document_ingestion import extract_document_text",
          "from skilgen.core.models import ProjectIntent, RequirementsContext",
          "def extract_text(path: Path) -> str:",
          "return extract_document_text(path)",
          "def normalize_lines(text: str) -> list[str]:",
          "return [line.strip() for line in text.splitlines() if line.strip()]",
          "def detect_domains(lines: list[str]) -> dict[str, bool]:"
        ],
        "related_imports": [
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
        "path": "packages/db/models/skill.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "from datetime import datetime",
          "from typing import TYPE_CHECKING",
          "from sqlalchemy import Boolean, ForeignKey, JSON, String, Text",
          "from sqlalchemy.orm import Mapped, mapped_column, relationship",
          "from packages.db.models.base import Base, new_uuid, utcnow",
          "if TYPE_CHECKING:",
          "from packages.db.models.repo import Repo",
          "from packages.db.models.skill_version import SkillVersion",
          "SOURCE_TYPE_TO_CATEGORY: dict[str, str] = {",
          "\"code\": \"codebase_architecture\",",
          "\"openapi\": \"internal_tools\","
        ],
        "related_imports": []
      },
      {
        "path": "skilgen/delivery.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "import asyncio",
          "from dataclasses import replace",
          "import json",
          "import os",
          "import time",
          "import uuid",
          "from pathlib import Path",
          "from typing import Callable",
          "from urllib.error import HTTPError, URLError",
          "from urllib.request import Request, urlopen",
          "from skilgen.agents import build_agent_decision, fingerprint_project"
        ],
        "related_imports": [
          "__future__",
          "asyncio",
          "dataclasses",
          "json",
          "os",
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
          "typing",
          "urllib.error",
          "urllib.request",
          "uuid"
        ]
      },
      {
        "path": "packages/db/models/org.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "from datetime import datetime",
          "from typing import TYPE_CHECKING",
          "from sqlalchemy import JSON, BigInteger, String, Text",
          "from sqlalchemy.orm import Mapped, mapped_column, relationship",
          "from packages.db.models.base import Base, new_uuid, utcnow",
          "if TYPE_CHECKING:",
          "from packages.db.models.digest_config import DigestConfig",
          "from packages.db.models.repo import Repo",
          "from packages.db.models.rbac import Role, RoleBinding",
          "from packages.db.models.source_connection import SourceConnection",
          "class Org(Base):"
        ],
        "related_imports": []
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
        "path": "apps/api/api/routes/repos.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "import hashlib",
          "import re",
          "from datetime import UTC, datetime, timedelta",
          "from difflib import unified_diff",
          "from typing import Any, Literal",
          "from uuid import uuid4",
          "from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request, Response",
          "from fastapi.responses import JSONResponse",
          "from pydantic import BaseModel, Field",
          "from sqlalchemy import desc, func, select, update",
          "from sqlalchemy.ext.asyncio import AsyncSession"
        ],
        "related_imports": []
      },
      {
        "path": "apps/api/api/analysis.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "from datetime import datetime",
          "import hashlib",
          "import logging",
          "from pathlib import Path",
          "import shutil",
          "import sys",
          "import tempfile",
          "import traceback",
          "from typing import Any",
          "import httpx",
          "from sqlalchemy import delete, func, select, update"
        ],
        "related_imports": []
      },
      {
        "path": "skilgen/deep_agents_core.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "import asyncio",
          "import json",
          "import os",
          "import queue",
          "import threading",
          "import time",
          "from typing import Callable",
          "from pathlib import Path",
          "from skilgen.agents.model_registry import provider_supported, resolve_model_settings",
          "from skilgen.core.config import DEFAULT_CONFIG, load_config",
          "try:"
        ],
        "related_imports": [
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
        "path": "packages/db/config.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "from pydantic_settings import BaseSettings, SettingsConfigDict",
          "class Settings(BaseSettings):",
          "DATABASE_URL: str = \"\"",
          "DATABASE_URL_UNPOOLED: str = \"\"",
          "DEBUG: bool = False",
          "GITHUB_APP_ID: str = \"\"",
          "GITHUB_APP_PRIVATE_KEY: str = \"\"",
          "GITHUB_WEBHOOK_SECRET: str = \"\"",
          "WORKOS_API_KEY: str = \"\"",
          "WORKOS_CLIENT_ID: str = \"\"",
          "OIDC_ISSUER_URL: str = \"\""
        ],
        "related_imports": []
      },
      {
        "path": "packages/db/models/__init__.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from packages.db.models.agent_session import AgentSession",
          "from packages.db.models.agent_load_event import AgentLoadEvent",
          "from packages.db.models.analysis_run import AnalysisRun",
          "from packages.db.models.audit_event import AuditEvent",
          "from packages.db.models.audit_chain import AuditHashChain, AuditWormRoot",
          "from packages.db.models.autopilot_task import AutopilotTask",
          "from packages.db.models.base import Base",
          "from packages.db.models.dependency import Dependency",
          "from packages.db.models.cross_repo_opportunity import CrossRepoOpportunity",
          "from packages.db.models.coverage_gap import CoverageGap",
          "from packages.db.models.dependency_graph_cache import DependencyGraphCache",
          "from packages.db.models.digest_config import DigestConfig"
        ],
        "related_imports": []
      },
      {
        "path": "skilgen/core/context.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "from pathlib import Path",
          "from skilgen.agents.domain_graph_planner import _top_level_app_surfaces, build_domain_graph, detect_repo_archetype",
          "from skilgen.agents.framework_fingerprint import fingerprint_project",
          "from skilgen.agents.codebase_signals import analyze_codebase, is_ignored_path_parts, is_internal_skillayer_monorepo",
          "from skilgen.agents.workspace_graph import build_workspace_graph",
          "from skilgen.core.models import (",
          "CodebaseContext,",
          "DomainGraph,",
          "DomainGraphNode,",
          "DomainRecord,",
          "RequirementsContext,"
        ],
        "related_imports": [
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
        "path": "apps/api/api/index.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "import json",
          "import logging",
          "import time",
          "import uuid",
          "import importlib",
          "from collections.abc import Awaitable, Callable",
          "from datetime import datetime, timezone",
          "from pathlib import Path",
          "from fastapi import FastAPI, Request",
          "from fastapi.middleware.cors import CORSMiddleware",
          "from fastapi.responses import JSONResponse"
        ],
        "related_imports": []
      },
      {
        "path": "apps/api/api/services/llm.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "import re",
          "from typing import Any",
          "import httpx",
          "from packages.db.llm_key import decrypt_key",
          "class LLMNotConfiguredError(Exception):",
          "pass",
          "class LLMCallError(Exception):",
          "pass",
          "def _provider_settings(org_settings: dict[str, Any] | None) -> tuple[str, str, str, str | None]:",
          "settings = org_settings or {}",
          "provider = str(settings.get(\"llm_provider\") or \"\").lower()"
        ],
        "related_imports": []
      },
      {
        "path": "skilgen/agents/requirements_parser.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "from pathlib import Path",
          "from skilgen.agents.codebase_signals import analyze_codebase",
          "from skilgen.deep_agents_core import run_deep_json",
          "from skilgen.core.models import ProjectIntent",
          "from skilgen.core.requirements import extract_project_intent, extract_text, normalize_lines",
          "def parse_requirements_file_native(path: Path) -> ProjectIntent:",
          "return extract_project_intent(normalize_lines(extract_text(path)))",
          "def parse_requirements_file(path: Path) -> ProjectIntent:",
          "resolved = path.resolve()",
          "text = extract_text(resolved)",
          "native_intent = extract_project_intent(normalize_lines(text))"
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
        "path": "skilgen/autoupdate.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "import json",
          "import os",
          "import signal",
          "import subprocess",
          "import sys",
          "import time",
          "from datetime import UTC, datetime",
          "from pathlib import Path",
          "from skilgen.agents.codebase_signals import is_ignored_path_parts, is_internal_skillayer_monorepo",
          "from skilgen.core.config import load_config",
          "from skilgen.core.generated_outputs import is_generated_output_path"
        ],
        "related_imports": [
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
        "path": "skilgen/core/dependency_risk.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "import json",
          "from pathlib import Path",
          "import re",
          "try:",
          "import tomllib",
          "except ImportError:  # pragma: no cover",
          "tomllib = None  # type: ignore[assignment]",
          "from skilgen.agents.relationship_mapper import build_import_graph",
          "from skilgen.agents.workspace_graph import build_workspace_graph",
          "from skilgen.core.models import (",
          "DependencyFinding,"
        ],
        "related_imports": [
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
        "path": "apps/api/alembic/env.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "import os",
          "from logging.config import fileConfig",
          "from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit",
          "from sqlalchemy import engine_from_config, pool",
          "from alembic import context",
          "from dotenv import load_dotenv",
          "load_dotenv(\".env.local\")",
          "load_dotenv(\"../../.env.local\")",
          "config = context.config",
          "if config.config_file_name is not None:",
          "fileConfig(config.config_file_name)",
          "DATABASE_URL = os.getenv(\"DATABASE_URL\", \"\")"
        ],
        "related_imports": []
      },
      {
        "path": "apps/api/api/v8/audit/router.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "from datetime import UTC, datetime, timedelta",
          "from io import StringIO",
          "import csv",
          "import json",
          "import os",
          "from typing import Any, Literal",
          "from fastapi import APIRouter, Depends, HTTPException, Query, Request",
          "from fastapi.responses import JSONResponse, Response, StreamingResponse",
          "from pydantic import BaseModel, Field",
          "from sqlalchemy import desc, func, select, text",
          "from sqlalchemy.ext.asyncio import AsyncSession"
        ],
        "related_imports": []
      },
      {
        "path": "skilgen/deep_agents_runtime.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "import json",
          "import os",
          "from dataclasses import asdict, is_dataclass",
          "from pathlib import Path",
          "from typing import Any, Callable",
          "from skilgen.agents.codebase_signals import analyze_codebase",
          "from skilgen.agents.domain_graph_planner import _top_level_app_surfaces, detect_repo_archetype",
          "from skilgen.agents.evidence_graph import build_evidence_graph",
          "from skilgen.agents.feature_extractor import extract_features, extract_features_native",
          "from skilgen.agents.framework_fingerprint import fingerprint_project",
          "from skilgen.agents.model_registry import resolve_model_settings"
        ],
        "related_imports": [
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
        ]
      },
      {
        "path": "skilgen/agents/domain_graph_planner.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "from pathlib import Path",
          "from skilgen.agents.codebase_signals import (",
          "analyze_codebase,",
          "collect_code_evidence,",
          "collect_structural_evidence,",
          "is_internal_skillayer_monorepo,",
          ")",
          "from skilgen.agents.requirements_parser import parse_project_intent_native",
          "from skilgen.agents.workspace_graph import build_workspace_graph",
          "from skilgen.deep_agents_core import run_deep_json",
          "from skilgen.core.models import CodebaseSignals, DomainGraph, DomainGraphNode, RequirementsContext, WorkspaceGraph, WorkspacePackage"
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
        "path": "skilgen/core/score.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "import json",
          "import re",
          "import subprocess",
          "from datetime import UTC, datetime",
          "from html import escape",
          "from pathlib import Path",
          "from threading import Lock",
          "from urllib.parse import quote",
          "from skilgen.agents.codebase_signals import CODE_EXTENSIONS, is_ignored_path_parts, is_internal_skillayer_monorepo",
          "from skilgen.core.context import build_codebase_context",
          "from skilgen.core.freshness import compute_freshness_report, load_freshness_state"
        ],
        "related_imports": [
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
        "path": "apps/api/api/services/commit_check.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "import time",
          "from dataclasses import dataclass",
          "from datetime import datetime",
          "from typing import Any",
          "import httpx",
          "from sqlalchemy import select",
          "from sqlalchemy.ext.asyncio import AsyncSession",
          "from apps.api.api.github import get_installation_token",
          "from apps.api.api.pr_comment import (",
          "build_violation_comment,",
          "create_skill_review_check_run,"
        ],
        "related_imports": []
      },
      {
        "path": "skilgen/cli/main.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "import argparse",
          "import json",
          "import os",
          "import sys",
          "from dataclasses import dataclass",
          "from datetime import UTC, datetime",
          "from pathlib import Path",
          "import threading",
          "import time",
          "import uuid",
          "from urllib.error import HTTPError, URLError"
        ],
        "related_imports": [
          "__future__",
          "argparse",
          "dataclasses",
          "datetime",
          "json",
          "os",
          "pathlib",
          "skilgen/__init__.py",
          "skilgen/agents/__init__.py",
          "skilgen/agents/requirements_parser.py",
          "skilgen/api/server.py",
          "skilgen/api/service.py",
          "skilgen/autoupdate.py",
          "skilgen/commands/check.py",
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
          "skilgen/hooks/cursor_watcher.py",
          "skilgen/parsers/runner.py",
          "skilgen/parsers/sources.py",
          "skilgen/registry_client.py",
          "sys",
          "threading",
          "time",
          "urllib.error",
          "urllib.parse",
          "urllib.request",
          "uuid"
        ]
      },
      {
        "path": "skilgen/core/analytics.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "import json",
          "import os",
          "from collections import Counter, defaultdict",
          "from datetime import UTC, datetime",
          "from pathlib import Path",
          "import re",
          "from skilgen.external_skills import active_external_skills",
          "def _compute_richness_score(content: str, spec: object) -> dict[str, int]:",
          "lines = content.splitlines()",
          "words = len(content.split())",
          "code_blocks = content.count(\"```\") // 2"
        ],
        "related_imports": [
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
        "path": "skilgen/external_skills.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "from dataclasses import asdict, dataclass",
          "from datetime import UTC, datetime",
          "import json",
          "import os",
          "import re",
          "import shutil",
          "import subprocess",
          "from pathlib import Path",
          "from skilgen.core.config import load_config",
          "TRUST_SCORES = {",
          "\"official\": 5,"
        ],
        "related_imports": [
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
        "path": "skilgen/agents/__init__.py",
        "kind": "source",
        "language": "python",
        "tags": [],
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
          "from skilgen.agents.relationship_mapper import build_import_graph",
          "from skilgen.agents.requirements_parser import parse_requirements_file",
          "from skilgen.agents.roadmap_planner import build_roadmap_plan"
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
        "path": "apps/api/api/v8/flags.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "import os",
          "from contextvars import ContextVar",
          "from collections.abc import AsyncGenerator",
          "from typing import Any",
          "from fastapi import APIRouter, Depends, HTTPException",
          "from pydantic import BaseModel",
          "from sqlalchemy.ext.asyncio import AsyncSession",
          "from apps.api.api.auth import get_current_org_id",
          "from packages.db.database import AsyncSessionLocal, get_db",
          "from packages.db.models import Org",
          "router = APIRouter(prefix=\"/v8/orgs/{org_id}/flags\", tags=[\"v8-flags\"])"
        ],
        "related_imports": []
      },
      {
        "path": "skilgen/agents/evidence_graph.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "from pathlib import Path",
          "from skilgen.agents.codebase_signals import analyze_codebase, collect_code_evidence, collect_structural_evidence",
          "from skilgen.agents.relationship_mapper import build_import_graph",
          "from skilgen.agents.source_graphs import (",
          "build_call_graph,",
          "build_config_runtime_graph,",
          "build_parser_summary,",
          "build_symbol_graph,",
          "build_symbol_relationships,",
          "build_test_mapping,",
          ")"
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
        "path": "skilgen/generators/skills.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "import os",
          "import re",
          "from datetime import date",
          "from pathlib import Path",
          "from typing import Callable",
          "from skilgen.agents.architecture_planner import build_architecture_blueprint",
          "from skilgen.agents.codebase_signals import analyze_codebase",
          "from skilgen.agents.requirements_parser import parse_project_intent",
          "from skilgen.agents.roadmap_planner import build_roadmap_plan",
          "from skilgen.core.config import load_config",
          "from skilgen.core.analytics import _compute_richness_score"
        ],
        "related_imports": [
          "__future__",
          "datetime",
          "os",
          "pathlib",
          "re",
          "skilgen/agents/architecture_planner.py",
          "skilgen/agents/codebase_signals.py",
          "skilgen/agents/requirements_parser.py",
          "skilgen/agents/roadmap_planner.py",
          "skilgen/core/analytics.py",
          "skilgen/core/config.py",
          "skilgen/core/context.py",
          "skilgen/core/dependency_risk.py",
          "skilgen/core/models.py",
          "skilgen/deep_agents_core.py",
          "typing"
        ]
      },
      {
        "path": "skilgen/agents/decision_planner.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "from pathlib import Path",
          "from skilgen.deep_agents_core import run_deep_json",
          "from skilgen.core.freshness import compute_freshness_report, load_freshness_state",
          "from skilgen.core.models import AgentDecision, RequirementsContext, RunMemory",
          "from skilgen.core.run_memory import load_current_run_memory",
          "from skilgen.enterprise_skills import active_enterprise_skills, active_mcp_connectors",
          "from skilgen.external_skills import external_skill_policy, ranked_external_skills",
          "def build_agent_decision_native(",
          "project_root: Path,",
          "requirements: RequirementsContext,",
          "domain_graph,"
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
        "path": "skilgen/agents/workspace_graph.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "from __future__ import annotations",
          "import json",
          "import re",
          "from pathlib import Path",
          "try:",
          "import yaml",
          "except ImportError:  # pragma: no cover - dependency is declared in pyproject",
          "yaml = None",
          "from skilgen.core.models import WorkspaceDependency, WorkspaceGraph, WorkspacePackage",
          "_IGNORED_DIRS = {",
          "\".git\",",
          "\".skilgen\","
        ],
        "related_imports": [
          "__future__",
          "json",
          "pathlib",
          "re",
          "skilgen/core/models.py",
          "yaml"
        ]
      },
      {
        "path": "tests/test_api_spec_parsers.py",
        "kind": "source",
        "language": "python",
        "tags": [
          "tests"
        ],
        "snippet": [
          "from __future__ import annotations",
          "from pathlib import Path",
          "from tempfile import TemporaryDirectory",
          "import unittest",
          "from skilgen.parsers import ApiSpecParserError",
          "from skilgen.parsers.graphql import parse_graphql_schema",
          "from skilgen.parsers.openapi import parse_openapi_spec",
          "from skilgen.parsers.postman import parse_postman_collection",
          "FIXTURES = Path(__file__).parent / \"fixtures\"",
          "class ApiSpecParserTests(unittest.TestCase):",
          "def test_openapi_parser_extracts_enterprise_signals(self) -> None:",
          "result = parse_openapi_spec(FIXTURES / \"openapi_petstore.yaml\")"
        ],
        "related_imports": [
          "__future__",
          "pathlib",
          "skilgen/parsers/__init__.py",
          "skilgen/parsers/graphql.py",
          "skilgen/parsers/openapi.py",
          "skilgen/parsers/postman.py",
          "tempfile",
          "unittest"
        ]
      },
      {
        "path": "skilgen/parsers/graphql.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "\"\"\"Parser for GraphQL SDL, .gql files, and introspection schema JSON.\"\"\"",
          "from __future__ import annotations",
          "import json",
          "import re",
          "from pathlib import Path",
          "from typing import Any",
          "from skilgen.parsers import ApiSpecFinding, ApiSpecItem, ApiSpecParseResult, ApiSpecParserError",
          "TYPE_BLOCK_RE = re.compile(",
          "r\"\\b(?P<kind>type|interface|input|enum)\\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\"",
          "r\"(?:\\s+implements\\s+[^{]+)?\\s*(?P<directives>(?:@[A-Za-z_][A-Za-z0-9_]*(?:\\([^)]*\\))?\\s*)*)\\{(?P<body>.*?)\\}\",",
          "re.DOTALL,",
          ")"
        ],
        "related_imports": [
          "__future__",
          "json",
          "pathlib",
          "re",
          "skilgen/parsers/__init__.py",
          "typing"
        ]
      },
      {
        "path": "apps/web/components/HexGrid.tsx",
        "kind": "source",
        "language": "typescript",
        "tags": [],
        "snippet": [
          "\"use client\";",
          "import { useCallback, useEffect, useRef } from \"react\";",
          "type CellState = \"incoming\" | \"locking\" | \"locked\" | \"active\" | \"departing\";",
          "type Slot = {",
          "id: number;",
          "label: string;",
          "targetX: number;",
          "targetY: number;",
          "};",
          "type Cell = Slot & {",
          "activeUntil: number;",
          "activationAt: number;"
        ],
        "related_imports": []
      },
      {
        "path": "scripts/deploy_api.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "\"\"\"Deploy the Skillayer API from the monorepo root with shared packages bundled.\"\"\"",
          "from __future__ import annotations",
          "import argparse",
          "import json",
          "import shutil",
          "import subprocess",
          "from collections.abc import Iterator",
          "from contextlib import contextmanager",
          "from pathlib import Path",
          "ROOT = Path(__file__).resolve().parents[1]",
          "API_PROJECT_LINK = ROOT / \"apps\" / \"api\" / \".vercel\" / \"project.json\"",
          "ROOT_PROJECT_LINK = ROOT / \".vercel\" / \"project.json\""
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
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "\"\"\"Deploy the Skillayer dashboard from the monorepo root.\"\"\"",
          "from __future__ import annotations",
          "import argparse",
          "import json",
          "import subprocess",
          "from collections.abc import Iterator",
          "from contextlib import contextmanager",
          "from pathlib import Path",
          "ROOT = Path(__file__).resolve().parents[1]",
          "DASHBOARD_PROJECT_LINK = ROOT / \"apps\" / \"dashboard\" / \".vercel\" / \"project.json\"",
          "ROOT_PROJECT_LINK = ROOT / \".vercel\" / \"project.json\"",
          "DASHBOARD_VERCEL_CONFIG = ROOT / \"vercel.dashboard.json\""
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
        "path": "skilgen/parsers/incident.py",
        "kind": "source",
        "language": "python",
        "tags": [],
        "snippet": [
          "\"\"\"Parsers for incident, PIR, and postmortem source artifacts.",
          "The parser keeps incident evidence structured enough for downstream skill",
          "generation without assuming a single enterprise template. It supports Markdown",
          "postmortems/PIRs and PagerDuty JSON exports, plus a small GitHub issue helper",
          "that only uses the ``GITHUB_TOKEN`` environment variable when available.",
          "\"\"\"",
          "from __future__ import annotations",
          "from collections import Counter, defaultdict",
          "from dataclasses import dataclass, field",
          "from datetime import datetime, timezone",
          "from json import JSONDecodeError",
          "import json"
        ],
        "related_imports": [
          "__future__",
          "collections",
          "dataclasses",
          "datetime",
          "json",
          "os",
          "pathlib",
          "re",
          "time",
          "typing",
          "urllib.error",
          "urllib.parse",
          "urllib.request"
        ]
      },
      {
        "path": "tests/__init__.py",
        "kind": "source",
        "language": "python",
        "tags": [
          "tests"
        ],
        "snippet": [
          "# Test package marker for shared fixtures."
        ],
        "related_imports": []
      },
      {
        "path": "tests/test_architecture_cli.py",
        "kind": "source",
        "language": "python",
        "tags": [
          "tests"
        ],
        "snippet": [
          "from pathlib import Path",
          "from tempfile import TemporaryDirectory",
          "import json",
          "import subprocess",
          "import sys",
          "import unittest",
          "class ArchitectureCliTests(unittest.TestCase):",
          "def test_architecture_command_outputs_markdown_and_json_export(self) -> None:",
          "with TemporaryDirectory() as tmp:",
          "root = Path(tmp)",
          "requirements = root / \"requirements.md\"",
          "requirements.write_text(\"Support COBOL transaction flows and backend services.\\n\", encoding=\"utf-8\")"
        ],
        "related_imports": [
          "json",
          "pathlib",
          "subprocess",
          "sys",
          "tempfile",
          "unittest"
        ]
      },
      {
        "path": "tests/test_audit_log.py",
        "kind": "source",
        "language": "python",
        "tags": [
          "tests"
        ],
        "snippet": [
          "from __future__ import annotations",
          "from datetime import datetime",
          "from types import SimpleNamespace",
          "import unittest",
          "from apps.api.api.services import audit",
          "from apps.api.api.routes import orgs",
          "class _FakeDb:",
          "def __init__(self, fail: bool = False) -> None:",
          "self.fail = fail",
          "self.added: list[object] = []",
          "def add(self, value: object) -> None:",
          "if self.fail:"
        ],
        "related_imports": [
          "__future__",
          "apps/api/api/routes/orgs.py",
          "apps/api/api/services/audit.py",
          "datetime",
          "types",
          "unittest"
        ]
      },
      {
        "path": "tests/test_cli.py",
        "kind": "source",
        "language": "python",
        "tags": [
          "tests"
        ],
        "snippet": [
          "from pathlib import Path",
          "from tempfile import TemporaryDirectory",
          "import json",
          "import subprocess",
          "import sys",
          "import unittest",
          "class CliTests(unittest.TestCase):",
          "def test_init_creates_config(self) -> None:",
          "with TemporaryDirectory() as tmp:",
          "result = subprocess.run(",
          "[sys.executable, \"-m\", \"skilgen.cli.main\", \"init\", \"--project-root\", tmp],",
          "text=True,"
        ],
        "related_imports": [
          "json",
          "pathlib",
          "subprocess",
          "sys",
          "tempfile",
          "unittest"
        ]
      },
      {
        "path": ".env.example",
        "kind": "source",
        "language": "config",
        "tags": [
          "config"
        ],
        "snippet": [
          "# Self-hosted root environment file used by Docker Compose and local container runs.",
          "# -- Database / cache ------------------",
          "DATABASE_URL=postgresql+asyncpg://skillayer:change-me@postgres:5432/skillayer",
          "POSTGRES_PASSWORD=change-me",
          "REDIS_URL=redis://redis:6379/0",
          "DEPLOYMENT_MODE=selfhosted",
          "NEXT_PUBLIC_DASHBOARD_URL=http://localhost:3000",
          "NEXT_PUBLIC_API_URL=http://localhost:8000",
          "API_URL=http://localhost:8000",
          "NEXT_PUBLIC_APP_URL=http://localhost:3000",
          "GITHUB_APP_ID=",
          "GITHUB_APP_PRIVATE_KEY="
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
        "path": "infra/helm/skillayer/values.yaml",
        "kind": "source",
        "language": "config",
        "tags": [
          "config"
        ],
        "snippet": [
          "global.imageRegistry",
          "global.imagePullSecrets",
          "api.image.repository: skillayer/api",
          "api.image.tag: latest",
          "api.image.pullPolicy: IfNotPresent",
          "api.replicas: 2",
          "api.service.type: ClusterIP",
          "api.service.port: 8000",
          "api.resources.requests.memory: 256Mi",
          "api.resources.requests.cpu: 250m",
          "api.resources.limits.memory: 1Gi",
          "api.resources.limits.cpu: 1000m"
        ],
        "related_imports": []
      },
      {
        "path": "tests/fixtures/terraform_main.tf",
        "kind": "source",
        "language": "config",
        "tags": [
          "config"
        ],
        "snippet": [
          "terraform {",
          "required_version = \">= 1.6.0\"",
          "required_providers {",
          "aws = {",
          "source = \"hashicorp/aws\"",
          "version = \"~> 5.0\"",
          "}",
          "google = {",
          "source = \"hashicorp/google\"",
          "version = \"~> 5.0\"",
          "}",
          "azurerm = {"
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
        "path": "tests/fixtures/runbook_deploy.md",
        "kind": "source",
        "language": "documentation",
        "tags": [
          "documentation"
        ],
        "snippet": [
          "---",
          "owner: release-engineering",
          "service: payments-api",
          "Use this runbook when deploying the payments API to production.",
          "1. Confirm the release candidate and freeze window.",
          "2. Run the deployment workflow from the release branch.",
          "3. Notify the incident channel when the rollout starts.",
          "- Check `/health` returns 200 in every region.",
          "- Confirm the deploy dashboard is green.",
          "- Validate https://status.example.com/payments before closing the change.",
          "- Do NOT skip the database backup.",
          "- Never deploy while an active incident is open."
        ],
        "related_imports": []
      },
      {
        "path": "docs/specs/AgentRun_v0.md",
        "kind": "source",
        "language": "documentation",
        "tags": [
          "documentation"
        ],
        "snippet": [
          "# AgentRun Webhook Spec v0",
          "AgentRun is Skillayer's vendor-neutral event format for AI coding agent sessions. Any agent vendor can POST one event when a session starts, updates, or completes so Skillayer can ",
          "## Endpoint",
          "```http",
          "POST https://api.skillayer.com/orgs/{org_id}/agent-runs",
          "Authorization: Bearer sk-...",
          "Content-Type: application/json",
          "```",
          "The API key is the same org API key used by `/repos/{repo_id}/skills/load`.",
          "```json",
          "{",
          "\"$schema\": \"https://json-schema.org/draft/2020-12/schema\","
        ],
        "related_imports": []
      },
      {
        "path": "docs/PRD-v8.docx",
        "kind": "source",
        "language": "enterprise_document",
        "tags": [
          "enterprise_document"
        ],
        "snippet": [
          "PRD",
          "The Agent Governance Plane",
          "Skilgen / Skillayer \u00b7 v8.0 \u2014 Repositioning from skill platform to coding-agent governance",
          "Author: Ravi",
          "Status: Draft for engineering review",
          "Date: May 1, 2026",
          "Supersedes: PRD v7 (skill platform framing)",
          "One-line pitch: You don't know what your coding agents did last night. We do.",
          "This document defines the strategic reframing of Skilgen/Skillayer from an enterprise skill platform into a cross-provider governance plane for coding agents. It covers the new pro",
          "1. Why this PRD exists",
          "1.1 The problem with v7",
          "PRD v7 framed Skilgen as a skill platform. The sidebar grew to ~30 items (Overview, Repos, Skills, PR Inbox, Review, Agent Scorecard, AI Readiness, Connect Agent, My Code Today, Le"
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
        "path": "extensions/vscode-skillayer/src/check.ts",
        "kind": "structure",
        "language": "typescript",
        "tags": [
          "structural-evidence"
        ],
        "snippet": [
          "function checkDiff",
          "function diffCurrentFile",
          "function getStagedDiff"
        ],
        "related_imports": [
          "vscode"
        ]
      },
      {
        "path": "extensions/vscode-skillayer/src/config.ts",
        "kind": "structure",
        "language": "typescript",
        "tags": [
          "structural-evidence"
        ],
        "snippet": [
          "function getConfig",
          "function isConfigured"
        ],
        "related_imports": [
          "vscode"
        ]
      },
      {
        "path": "extensions/vscode-skillayer/src/diagnostics.ts",
        "kind": "structure",
        "language": "typescript",
        "tags": [
          "structural-evidence"
        ],
        "snippet": [
          "function findingsToDiagnostics"
        ],
        "related_imports": [
          "extensions/vscode-skillayer/src/check.ts",
          "vscode"
        ]
      },
      {
        "path": "extensions/vscode-skillayer/src/extension.ts",
        "kind": "structure",
        "language": "typescript",
        "tags": [
          "structural-evidence"
        ],
        "snippet": [
          "function toSeverity",
          "function activate",
          "function checkDocument",
          "function checkCurrentFile",
          "function checkStaged",
          "function deactivate"
        ],
        "related_imports": [
          "extensions/vscode-skillayer/src/check.ts",
          "extensions/vscode-skillayer/src/config.ts",
          "extensions/vscode-skillayer/src/diagnostics.ts",
          "vscode"
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
        "path": "scripts/deploy_web.py",
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
          "function web_project_link"
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
          "The current input mode was: `requirements + codebase`.",
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
          "| Requirements-driven scan | requirements | `README.md` | Parse the requirements input and generate skills and project docs. | active | current |",
          "| Project folder analysis | analysis | `skilgen` | Analyze the input folder and generate outputs into that same folder. | active | current |",
          "| Backend route: skilgen/api/__init__.py | backend | `skilgen/api/__init__.py` | Detected route or handler implementation in the scanned codebase. | active | current |",
          "| Backend route: skilgen/api/jobs.py | backend | `skilgen/api/jobs.py` | Detected route or handler implementation in the scanned codebase. | active | current |"
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
          "# Skillayer",
          "Skillayer is a governance plane for AI coding agents. It helps platform, security, and engineering leadership answer the questions that matter once Claude Code, Codex, Cursor, GitH",
          "- What did agents do across repos, tools, sessions, and users?",
          "- Which actions violated policy, and were they blocked, approved, or sent for more review?",
          "- Which skills are trusted, stale, drifted, quarantined, or bound to policy?",
          "- Can audit evidence be exported with attribution, policy decisions, and tamper-evident history?",
          "- Where is fleet risk increasing across agents, repos, skills, and critical operations?",
          "The current product direction is defined by `docs/PRD-v8.docx`: Skillayer v8 reduces the product to six enterprise surfaces and treats the older skill-generation system as the subs"
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
          "- Detected domains: requirements, platform, platform-runtime, platform-agents, platform-cli, platform-core, platform-generators, platform-scripts, roadmap, roadmap-phase-0, roadmap",
          "- Feature inventory entries: 18",
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
          "- Source file: `README.md`",
          "- Source hash: `886c076cfa1f`",
          "## Intent To Output Mapping",
          "### Endpoints",
          "- Intent: | Surface | Purpose | Key Routes |"
        ],
        "related_imports": []
      },
      {
        "path": "docs/AGENTS.md",
        "kind": "documentation",
        "language": null,
        "tags": [
          "docs"
        ],
        "snippet": [
          "# AGENTS.md \u2014 Skillayer v8 Governance-Plane Refactor",
          "> **This file is your mission brief.** Read it fully before any tool call. Re-read sections relevant to your current task before each major change.",
          "*Version 8.0.1 \u2014 terminology aligned with prompt set; conventions doc pointer added in \u00a77.*",
          "---",
          "## 1. Mission",
          "Refactor the existing Skilgen / Skillayer codebase from the v7 information architecture (~30 sidebar items, \"skill platform\" framing) to the v8 information architecture (6 sidebar ",
          "The refactor must:",
          "1. Preserve every piece of customer data, every existing API contract, and every URL that an authenticated customer might have bookmarked."
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
        "path": "apps/dashboard/Dockerfile",
        "kind": "config",
        "language": null,
        "tags": [
          "config"
        ],
        "snippet": [
          "FROM node:20-alpine AS builder",
          "WORKDIR /app",
          "ARG NEXT_PUBLIC_API_URL=http://localhost:8000",
          "ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}",
          "# Enable standalone output for Docker (see next.config.ts)",
          "ENV BUILD_STANDALONE=1",
          "COPY package*.json turbo.json ./",
          "COPY apps/dashboard/package*.json ./apps/dashboard/"
        ],
        "related_imports": []
      },
      {
        "path": "apps/dashboard/package.json",
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
        "path": "apps/web/package.json",
        "kind": "config",
        "language": null,
        "tags": [
          "config"
        ],
        "snippet": [
          "{",
          "\"name\": \"skillayer-web\",",
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
        "path": "apps/worker/Dockerfile",
        "kind": "config",
        "language": null,
        "tags": [
          "config"
        ],
        "snippet": [
          "FROM python:3.12-slim",
          "WORKDIR /app",
          "RUN apt-get update && apt-get install -y \\",
          "git build-essential \\",
          "&& rm -rf /var/lib/apt/lists/*",
          "COPY pyproject.toml setup.py ./",
          "COPY skilgen/ ./skilgen/",
          "COPY packages/db/ ./packages/db/"
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
        "path": "tests/fixtures/semgrep_results.sarif",
        "kind": "runtime",
        "language": null,
        "tags": [
          "runtime",
          "sast",
          "sarif"
        ],
        "snippet": [
          "SAST findings across 2 files",
          "Related paths: src/app.py, src/templates.py"
        ],
        "related_imports": [
          "src/app.py",
          "src/templates.py"
        ]
      }
    ],
    "recommendations": [
      "Use high-signal source evidence to define domain boundaries before generating skills.",
      "Prefer domains that are supported by both code evidence and requirements intent.",
      "Optimize skill synthesis around the dominant languages: python, typescript.",
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
      "extensions/vscode-skillayer/src/check.ts": {
        "language": "typescript",
        "backend": "regex",
        "symbol_count": 5,
        "call_count": 16,
        "import_count": 0,
        "relationship_count": 0
      },
      "extensions/vscode-skillayer/src/config.ts": {
        "language": "typescript",
        "backend": "regex",
        "symbol_count": 2,
        "call_count": 3,
        "import_count": 0,
        "relationship_count": 0
      },
      "extensions/vscode-skillayer/src/diagnostics.ts": {
        "language": "typescript",
        "backend": "regex",
        "symbol_count": 1,
        "call_count": 8,
        "import_count": 1,
        "relationship_count": 1
      },
      "extensions/vscode-skillayer/src/extension.ts": {
        "language": "typescript",
        "backend": "regex",
        "symbol_count": 6,
        "call_count": 27,
        "import_count": 0,
        "relationship_count": 6
      },
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
      "scripts/deploy_web.py": {
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
        "symbol_count": 20,
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
        "symbol_count": 25,
        "call_count": 30,
        "import_count": 20,
        "relationship_count": 0
      },
      "skilgen/commands/__init__.py": {
        "language": "python",
        "backend": "regex",
        "symbol_count": 0,
        "call_count": 0,
        "import_count": 0,
        "relationship_count": 0
      },
      "skilgen/commands/check.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 13,
        "call_count": 30,
        "import_count": 10,
        "relationship_count": 1
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
        "symbol_count": 13,
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
        "symbol_count": 11,
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
        "symbol_count": 11,
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
        "symbol_count": 30,
        "call_count": 30,
        "import_count": 16,
        "relationship_count": 0
      },
      "skilgen/hooks/__init__.py": {
        "language": "python",
        "backend": "regex",
        "symbol_count": 0,
        "call_count": 0,
        "import_count": 0,
        "relationship_count": 0
      },
      "skilgen/hooks/claude_code.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 1,
        "call_count": 5,
        "import_count": 2,
        "relationship_count": 0
      },
      "skilgen/hooks/claude_code_hook.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 24,
        "call_count": 30,
        "import_count": 9,
        "relationship_count": 0
      },
      "skilgen/hooks/cursor.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 1,
        "call_count": 5,
        "import_count": 2,
        "relationship_count": 0
      },
      "skilgen/hooks/cursor_watcher.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 3,
        "call_count": 15,
        "import_count": 7,
        "relationship_count": 0
      },
      "skilgen/parsers/__init__.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 6,
        "call_count": 4,
        "import_count": 12,
        "relationship_count": 1
      },
      "skilgen/parsers/auto_detect.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 9,
        "call_count": 23,
        "import_count": 6,
        "relationship_count": 0
      },
      "skilgen/parsers/confluence.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 30,
        "call_count": 30,
        "import_count": 8,
        "relationship_count": 1
      },
      "skilgen/parsers/dbt.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 23,
        "call_count": 30,
        "import_count": 6,
        "relationship_count": 1
      },
      "skilgen/parsers/graphql.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 13,
        "call_count": 30,
        "import_count": 6,
        "relationship_count": 0
      },
      "skilgen/parsers/helm.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 11,
        "call_count": 30,
        "import_count": 7,
        "relationship_count": 1
      },
      "skilgen/parsers/incident.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 30,
        "call_count": 30,
        "import_count": 13,
        "relationship_count": 1
      },
      "skilgen/parsers/kafka.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 24,
        "call_count": 30,
        "import_count": 6,
        "relationship_count": 1
      },
      "skilgen/parsers/kubernetes.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 25,
        "call_count": 30,
        "import_count": 6,
        "relationship_count": 1
      },
      "skilgen/parsers/notion.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 11,
        "call_count": 30,
        "import_count": 8,
        "relationship_count": 0
      },
      "skilgen/parsers/openapi.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 18,
        "call_count": 30,
        "import_count": 8,
        "relationship_count": 0
      },
      "skilgen/parsers/postman.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 13,
        "call_count": 30,
        "import_count": 6,
        "relationship_count": 0
      },
      "skilgen/parsers/runbook.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 25,
        "call_count": 30,
        "import_count": 4,
        "relationship_count": 1
      },
      "skilgen/parsers/runner.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 3,
        "call_count": 20,
        "import_count": 6,
        "relationship_count": 0
      },
      "skilgen/parsers/sarif.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 19,
        "call_count": 30,
        "import_count": 6,
        "relationship_count": 0
      },
      "skilgen/parsers/sbom.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 27,
        "call_count": 30,
        "import_count": 9,
        "relationship_count": 0
      },
      "skilgen/parsers/security_policy.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 13,
        "call_count": 30,
        "import_count": 7,
        "relationship_count": 0
      },
      "skilgen/parsers/sources.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 21,
        "call_count": 30,
        "import_count": 6,
        "relationship_count": 0
      },
      "skilgen/parsers/sql_schema.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 30,
        "call_count": 30,
        "import_count": 6,
        "relationship_count": 1
      },
      "skilgen/parsers/terraform.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 30,
        "call_count": 30,
        "import_count": 6,
        "relationship_count": 1
      },
      "skilgen/registry_client.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 10,
        "call_count": 25,
        "import_count": 8,
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
        "symbol_count": 10,
        "call_count": 19,
        "import_count": 5,
        "relationship_count": 1
      },
      "tests/test_api_key.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 20,
        "call_count": 18,
        "import_count": 10,
        "relationship_count": 0
      },
      "tests/test_api_smoke.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 13,
        "call_count": 30,
        "import_count": 17,
        "relationship_count": 1
      },
      "tests/test_api_spec_parsers.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 9,
        "call_count": 12,
        "import_count": 8,
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
      "tests/test_audit_log.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 11,
        "call_count": 13,
        "import_count": 6,
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
      "tests/test_cli_sources.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 7,
        "call_count": 13,
        "import_count": 7,
        "relationship_count": 0
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
      "tests/test_dashboard_error_boundaries.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 4,
        "call_count": 5,
        "import_count": 2,
        "relationship_count": 0
      },
      "tests/test_data_parsers.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 16,
        "call_count": 15,
        "import_count": 6,
        "relationship_count": 3
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
      "tests/test_eval.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 30,
        "call_count": 28,
        "import_count": 10,
        "relationship_count": 0
      },
      "tests/test_eval_cli.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 5,
        "call_count": 5,
        "import_count": 4,
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
      "tests/test_generation_quality.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 15,
        "call_count": 30,
        "import_count": 15,
        "relationship_count": 1
      },
      "tests/test_half_life.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 11,
        "call_count": 8,
        "import_count": 5,
        "relationship_count": 0
      },
      "tests/test_identity_policy_store.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 2,
        "call_count": 14,
        "import_count": 6,
        "relationship_count": 1
      },
      "tests/test_improvement_loop.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 14,
        "call_count": 17,
        "import_count": 5,
        "relationship_count": 0
      },
      "tests/test_incident_parsers.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 8,
        "call_count": 19,
        "import_count": 6,
        "relationship_count": 1
      },
      "tests/test_infra_parsers.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 13,
        "call_count": 13,
        "import_count": 7,
        "relationship_count": 3
      },
      "tests/test_jobs.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 4,
        "call_count": 27,
        "import_count": 9,
        "relationship_count": 1
      },
      "tests/test_llm_config.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 9,
        "call_count": 11,
        "import_count": 3,
        "relationship_count": 1
      },
      "tests/test_memory_capture.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 22,
        "call_count": 26,
        "import_count": 8,
        "relationship_count": 0
      },
      "tests/test_memory_cli.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 6,
        "call_count": 25,
        "import_count": 8,
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
      "tests/test_org_intelligence_api.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 29,
        "call_count": 30,
        "import_count": 9,
        "relationship_count": 0
      },
      "tests/test_org_settings.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 30,
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
      "tests/test_policy_engine.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 14,
        "call_count": 15,
        "import_count": 5,
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
      "tests/test_process_parsers.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 18,
        "call_count": 22,
        "import_count": 9,
        "relationship_count": 3
      },
      "tests/test_rate_limit_store.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 2,
        "call_count": 8,
        "import_count": 5,
        "relationship_count": 1
      },
      "tests/test_red_flags.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 22,
        "call_count": 21,
        "import_count": 10,
        "relationship_count": 0
      },
      "tests/test_registry.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 15,
        "call_count": 5,
        "import_count": 5,
        "relationship_count": 0
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
      "tests/test_security_parsers.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 16,
        "call_count": 16,
        "import_count": 8,
        "relationship_count": 3
      },
      "tests/test_skill_detail.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 11,
        "call_count": 9,
        "import_count": 5,
        "relationship_count": 0
      },
      "tests/test_skill_sources_api.py": {
        "language": "python",
        "backend": "python-ast",
        "symbol_count": 10,
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
      "extensions/vscode-skillayer/src/check.ts": [
        "function checkDiff",
        "function diffCurrentFile",
        "function getStagedDiff",
        "CheckResult",
        "Finding",
        "checkDiff",
        "diffCurrentFile",
        "getStagedDiff"
      ],
      "extensions/vscode-skillayer/src/config.ts": [
        "function getConfig",
        "function isConfigured",
        "getConfig",
        "isConfigured"
      ],
      "extensions/vscode-skillayer/src/diagnostics.ts": [
        "function findingsToDiagnostics",
        "findingsToDiagnostics"
      ],
      "extensions/vscode-skillayer/src/extension.ts": [
        "function toSeverity",
        "function activate",
        "function checkDocument",
        "function checkCurrentFile",
        "function checkStaged",
        "function deactivate",
        "activate",
        "checkCurrentFile",
        "checkDocument",
        "checkStaged",
        "deactivate",
        "toSeverity"
      ],
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
      "scripts/deploy_web.py": [
        "from __future__ import annotations",
        "imports argparse",
        "imports json",
        "imports subprocess",
        "from collections.abc import Iterator",
        "from contextlib import contextmanager",
        "from pathlib import Path",
        "function load_project_link",
        "function deploy_command",
        "function web_project_link"
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
        "from concurrent.futures import Future, ThreadPoolExecutor",
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
        "imports os",
        "imports sys",
        "from dataclasses import dataclass",
        "from datetime import UTC, datetime",
        "from pathlib import Path",
        "imports threading",
        "imports time"
      ],
      "skilgen/commands/check.py": [
        "from __future__ import annotations",
        "imports json",
        "imports os",
        "imports subprocess",
        "imports sys",
        "from dataclasses import dataclass",
        "from pathlib import Path",
        "from typing import Any",
        "from urllib.error import HTTPError, URLError",
        "from urllib.request import Request, urlopen"
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
        "function _compute_richness_score",
        "function _analytics_path"
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
        "from skilgen.core.models import CorpusSettings, SkilgenConfig, SourceConfigValue",
        "function _string_or_none",
        "function _string_list",
        "function _bool_value",
        "function _int_value",
        "function _float_value",
        "function _dict_value",
        "function _source_dict_value"
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
        "imports asyncio",
        "from dataclasses import replace",
        "imports json",
        "imports os",
        "imports time",
        "imports uuid",
        "from pathlib import Path",
        "from typing import Callable",
        "from urllib.error import HTTPError, URLError"
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
        "imports re",
        "from datetime import date",
        "from pathlib import Path",
        "from typing import Callable",
        "from skilgen.agents.architecture_planner import build_architecture_blueprint",
        "from skilgen.agents.codebase_signals import analyze_codebase",
        "from skilgen.agents.requirements_parser import parse_project_intent",
        "from skilgen.agents.roadmap_planner import build_roadmap_plan"
      ],
      "skilgen/hooks/claude_code.py": [
        "from __future__ import annotations",
        "from pathlib import Path",
        "function write_claude_code_hook"
      ],
      "skilgen/hooks/claude_code_hook.py": [
        "from __future__ import annotations",
        "imports json",
        "imports os",
        "from pathlib import Path",
        "imports sys",
        "imports time",
        "from typing import Any",
        "imports urllib.request",
        "from skilgen.core.analytics import log_skill_usage",
        "function _session_id"
      ],
      "skilgen/hooks/cursor.py": [
        "from __future__ import annotations",
        "from pathlib import Path",
        "function write_cursor_watcher"
      ],
      "skilgen/hooks/cursor_watcher.py": [
        "from __future__ import annotations",
        "imports os",
        "imports subprocess",
        "imports sys",
        "imports time",
        "from pathlib import Path",
        "function _skills_dir",
        "function watch_skills"
      ],
      "skilgen/parsers/__init__.py": [
        "from __future__ import annotations",
        "from dataclasses import asdict, dataclass, field",
        "from skilgen.parsers.dbt import DbtProjectAnalysis, DbtProjectParseError, parse_dbt_project",
        "from skilgen.parsers.helm import HelmChartParseResult, HelmParserError, parse_helm_chart",
        "from skilgen.parsers.kafka import KafkaAnalysis, KafkaParseError, parse_kafka_artifact",
        "from skilgen.parsers.kubernetes import KubernetesManifestParseResult, KubernetesParserError, parse_kubernetes_manifests",
        "from skilgen.parsers.runbook import ProcessParserError, ProcessSource, parse_runbook_file, parse_runbook_source",
        "from skilgen.parsers.sarif import SarifFinding, SarifResult, SarifTool, parse_sarif",
        "from skilgen.parsers.sbom import SbomPackage, SbomResult, parse_sbom",
        "from skilgen.parsers.security_policy import SecurityPolicyResult, parse_security_policy"
      ],
      "skilgen/parsers/auto_detect.py": [
        "from __future__ import annotations",
        "from pathlib import Path",
        "from typing import Iterable",
        "from skilgen.core.config import load_config",
        "from skilgen.core.models import SourceConfigValue",
        "from skilgen.parsers.sources import SOURCE_ALIASES, SOURCE_TYPES",
        "function normalize_source_name",
        "function load_source_config",
        "function detect_source_paths",
        "function resolve_source_paths"
      ],
      "skilgen/parsers/confluence.py": [
        "from __future__ import annotations",
        "from html.parser import HTMLParser",
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports re",
        "imports xml.etree.ElementTree",
        "imports zipfile",
        "from skilgen.parsers.runbook import ProcessParserError, ProcessSource, _dedupe",
        "function parse_confluence_file",
        "function parse_confluence_source"
      ],
      "skilgen/parsers/dbt.py": [
        "from __future__ import annotations",
        "imports re",
        "from dataclasses import dataclass, field",
        "from pathlib import Path",
        "from typing import Any",
        "imports yaml",
        "class DbtProjectParseError",
        "class DbtIssue",
        "class DbtColumn",
        "class DbtModel"
      ],
      "skilgen/parsers/graphql.py": [
        "from __future__ import annotations",
        "imports json",
        "imports re",
        "from pathlib import Path",
        "from typing import Any",
        "from skilgen.parsers import ApiSpecFinding, ApiSpecItem, ApiSpecParseResult, ApiSpecParserError",
        "function parse_graphql_schema",
        "function parse_graphql",
        "function parse",
        "function _parse_sdl"
      ],
      "skilgen/parsers/helm.py": [
        "from __future__ import annotations",
        "imports re",
        "from collections import Counter",
        "from dataclasses import dataclass, field",
        "from pathlib import Path",
        "from typing import Any",
        "imports yaml",
        "class HelmParserError",
        "class HelmTemplateSummary",
        "class HelmChartParseResult"
      ],
      "skilgen/parsers/incident.py": [
        "from __future__ import annotations",
        "from collections import Counter, defaultdict",
        "from dataclasses import dataclass, field",
        "from datetime import datetime, timezone",
        "from json import JSONDecodeError",
        "imports json",
        "imports os",
        "from pathlib import Path",
        "imports re",
        "imports time"
      ],
      "skilgen/parsers/kafka.py": [
        "from __future__ import annotations",
        "imports json",
        "from dataclasses import dataclass, field",
        "from pathlib import Path",
        "from typing import Any",
        "imports yaml",
        "class KafkaParseError",
        "class KafkaIssue",
        "class KafkaTopic",
        "class KafkaField"
      ],
      "skilgen/parsers/kubernetes.py": [
        "from __future__ import annotations",
        "from collections import Counter",
        "from dataclasses import dataclass, field",
        "from pathlib import Path",
        "from typing import Any",
        "imports yaml",
        "class KubernetesParserError",
        "class KubernetesObjectSummary",
        "class KubernetesManifestParseResult",
        "function parse_kubernetes_manifests"
      ],
      "skilgen/parsers/notion.py": [
        "from __future__ import annotations",
        "imports json",
        "imports os",
        "from pathlib import Path",
        "imports time",
        "from typing import Any",
        "from skilgen.parsers.runbook import ProcessParserError, ProcessSource, _parse_markdown_document, _parse_markdown_text",
        "function parse_notion_file",
        "function parse_notion_source",
        "function parse_notion_api_json"
      ],
      "skilgen/parsers/openapi.py": [
        "from __future__ import annotations",
        "imports json",
        "imports re",
        "from collections.abc import Iterable",
        "from pathlib import Path",
        "from typing import Any",
        "imports yaml",
        "from skilgen.parsers import ApiSpecFinding, ApiSpecItem, ApiSpecParseResult, ApiSpecParserError",
        "function parse_openapi_spec",
        "function parse_openapi"
      ],
      "skilgen/parsers/postman.py": [
        "from __future__ import annotations",
        "imports json",
        "imports re",
        "from pathlib import Path",
        "from typing import Any",
        "from skilgen.parsers import ApiSpecFinding, ApiSpecItem, ApiSpecParseResult, ApiSpecParserError",
        "function parse_postman_collection",
        "function parse_postman",
        "function parse",
        "function _load_collection"
      ],
      "skilgen/parsers/runbook.py": [
        "from __future__ import annotations",
        "from dataclasses import dataclass, field",
        "from pathlib import Path",
        "imports re",
        "class ProcessParserError",
        "class ProcessSource",
        "function parse_runbook_file",
        "function parse_runbook_source",
        "function parse_runbook_dir",
        "function _parse_markdown_document"
      ],
      "skilgen/parsers/runner.py": [
        "from __future__ import annotations",
        "from pathlib import Path",
        "from typing import Iterable",
        "from skilgen.core.models import SourceConfigValue",
        "from skilgen.parsers.auto_detect import detect_source_paths, normalize_source_name",
        "from skilgen.parsers.sources import SOURCE_TYPES, SkillSource, SourceRunResult, _call_parser",
        "function run_source_parsers",
        "function _selected_sources",
        "function _resolved_paths"
      ],
      "skilgen/parsers/sarif.py": [
        "from __future__ import annotations",
        "from dataclasses import dataclass, field",
        "imports json",
        "from pathlib import Path",
        "imports re",
        "from typing import Any",
        "class SarifTool",
        "class SarifFinding",
        "class SarifResult",
        "function parse_sarif"
      ],
      "skilgen/parsers/sbom.py": [
        "from __future__ import annotations",
        "from dataclasses import dataclass, field",
        "imports json",
        "from pathlib import Path",
        "imports re",
        "from typing import Any",
        "from urllib.parse import unquote",
        "from xml.etree import ElementTree",
        "class SbomPackage",
        "class SbomResult"
      ],
      "skilgen/parsers/security_policy.py": [
        "from __future__ import annotations",
        "from dataclasses import dataclass, field",
        "imports json",
        "from pathlib import Path",
        "imports re",
        "from typing import Any",
        "imports yaml",
        "class SecurityPolicyResult",
        "function parse_security_policy",
        "function _parse_structured_yaml"
      ],
      "skilgen/parsers/sources.py": [
        "from __future__ import annotations",
        "from dataclasses import dataclass, field",
        "from importlib import import_module",
        "from pathlib import Path",
        "imports re",
        "from typing import Callable, Iterable",
        "class SkillSource",
        "class SourceRunResult",
        "function slugify",
        "function _field_list"
      ],
      "skilgen/parsers/sql_schema.py": [
        "from __future__ import annotations",
        "imports json",
        "imports re",
        "from dataclasses import dataclass, field",
        "from pathlib import Path",
        "from typing import Any",
        "class SqlSchemaParseError",
        "class SqlIssue",
        "class SqlColumn",
        "class SqlIndex"
      ],
      "skilgen/parsers/terraform.py": [
        "from __future__ import annotations",
        "imports re",
        "from collections import Counter",
        "from dataclasses import dataclass, field",
        "from pathlib import Path",
        "class TerraformParserError",
        "class TerraformResource",
        "class TerraformParseResult",
        "function parse_terraform_directory",
        "function parse_terraform_dir"
      ],
      "skilgen/registry_client.py": [
        "from __future__ import annotations",
        "imports json",
        "imports os",
        "from pathlib import Path",
        "from typing import cast",
        "from urllib.error import HTTPError, URLError",
        "from urllib.parse import urlencode",
        "from urllib.request import Request, urlopen",
        "class RegistryClientError",
        "function _api_key"
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
        "from unittest import mock",
        "from skilgen.core.analytics import _detect_agent_runtime, analytics_summary, log_skill_usage",
        "from skilgen.generators.package import render_analytics_radial_data",
        "class AnalyticsTests"
      ],
      "tests/test_api_key.py": [
        "from __future__ import annotations",
        "imports asyncio",
        "from types import SimpleNamespace",
        "from typing import Any",
        "from fastapi import FastAPI",
        "from fastapi.testclient import TestClient",
        "from apps.api.api import auth",
        "from apps.api.api.auth import get_current_org_id",
        "from apps.api.api.routes import orgs",
        "from packages.db.database import get_db"
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
      "tests/test_api_spec_parsers.py": [
        "from __future__ import annotations",
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports unittest",
        "from skilgen.parsers import ApiSpecParserError",
        "from skilgen.parsers.graphql import parse_graphql_schema",
        "from skilgen.parsers.openapi import parse_openapi_spec",
        "from skilgen.parsers.postman import parse_postman_collection",
        "class ApiSpecParserTests"
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
      "tests/test_audit_log.py": [
        "from __future__ import annotations",
        "from datetime import datetime",
        "from types import SimpleNamespace",
        "imports unittest",
        "from apps.api.api.services import audit",
        "from apps.api.api.routes import orgs",
        "class _FakeDb",
        "class AuditLogTests"
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
      "tests/test_cli_sources.py": [
        "from __future__ import annotations",
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "from apps.api.api.analysis import _source_skill_files",
        "from skilgen.cli.main import _render_source_summary",
        "from skilgen.parsers.auto_detect import detect_source_paths",
        "from skilgen.parsers.runner import run_source_parsers",
        "function test_detect_source_paths_honors_sparse_sources_config_and_aliases",
        "function test_run_source_parsers_supports_explicit_paths_without_persisting",
        "function test_explicit_source_selection_overrides_disabled_config_entry"
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
      "tests/test_dashboard_error_boundaries.py": [
        "from __future__ import annotations",
        "from pathlib import Path",
        "function read",
        "function test_dashboard_routes_define_segment_error_boundaries",
        "function test_section_error_boundary_uses_shared_fallback_text",
        "function test_dashboard_sections_are_wrapped_with_error_boundaries"
      ],
      "tests/test_data_parsers.py": [
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports unittest",
        "from skilgen.parsers.dbt import DbtProjectParseError, parse_dbt_project",
        "from skilgen.parsers.kafka import KafkaParseError, parse_kafka_artifact",
        "from skilgen.parsers.sql_schema import SqlSchemaParseError, parse_sql_schema",
        "class DbtParserTests",
        "class SqlSchemaParserTests",
        "class KafkaParserTests"
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
      "tests/test_eval.py": [
        "from __future__ import annotations",
        "from datetime import datetime, timedelta",
        "imports importlib",
        "from types import SimpleNamespace",
        "from typing import Any",
        "imports pytest",
        "from fastapi import FastAPI",
        "from fastapi.testclient import TestClient",
        "from apps.api.api.auth import get_current_org_id",
        "from packages.db.database import get_db"
      ],
      "tests/test_eval_cli.py": [
        "from __future__ import annotations",
        "imports sys",
        "imports pytest",
        "from skilgen.cli import main",
        "function run_cli",
        "function test_eval_record_success_posts",
        "function test_eval_record_failure_warns_on_gap",
        "function test_eval_status_prints_roi",
        "function test_eval_gaps_lists_commands"
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
      "tests/test_generation_quality.py": [
        "from __future__ import annotations",
        "imports asyncio",
        "imports json",
        "imports os",
        "imports time",
        "imports unittest",
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "from unittest.mock import patch",
        "from skilgen.core.analytics import _compute_richness_score, analytics_summary"
      ],
      "tests/test_half_life.py": [
        "from __future__ import annotations",
        "from datetime import datetime, timedelta",
        "from pathlib import Path",
        "from types import SimpleNamespace",
        "from apps.api.api.services import half_life",
        "function _source",
        "function test_compute_half_life_high_churn_uses_five_point_decay",
        "function test_compute_half_life_moderate_churn_uses_two_point_decay",
        "function test_compute_half_life_stable_uses_slow_decay_and_ninety_day_cap",
        "function test_compute_half_life_already_stale_sets_zero_days"
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
      "tests/test_improvement_loop.py": [
        "from __future__ import annotations",
        "from datetime import datetime, timedelta",
        "from pathlib import Path",
        "from types import SimpleNamespace",
        "from apps.api.api.routes.repos import _improvement_plan, _skill_code_block_count, _skill_improvement_plan, _skill_word_count",
        "function _read",
        "function _skill",
        "function test_improvement_plan_for_score_15_flags_multiple_dimensions",
        "function test_improvement_plan_for_score_75_returns_not_improvable_when_dimensions_are_strong",
        "function test_improvement_plan_potential_score_never_exceeds_100"
      ],
      "tests/test_incident_parsers.py": [
        "from __future__ import annotations",
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports unittest",
        "from unittest.mock import patch",
        "from skilgen.parsers.incident import IncidentParseError, fetch_github_incident_issues, parse_incident_sources, parse_markdown_postmortem",
        "class IncidentParserTests"
      ],
      "tests/test_infra_parsers.py": [
        "from __future__ import annotations",
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports unittest",
        "from skilgen.parsers.helm import HelmParserError, parse_helm_chart",
        "from skilgen.parsers.kubernetes import KubernetesParserError, parse_kubernetes_manifests",
        "from skilgen.parsers.terraform import TerraformParserError, parse_terraform_directory",
        "class TerraformParserTests",
        "class KubernetesParserTests",
        "class HelmParserTests"
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
      "tests/test_llm_config.py": [
        "from __future__ import annotations",
        "imports unittest",
        "from apps.api.api.services import llm_config",
        "class LLMConfigTests"
      ],
      "tests/test_memory_capture.py": [
        "from __future__ import annotations",
        "from dataclasses import dataclass",
        "from datetime import UTC, datetime, timedelta",
        "from pathlib import Path",
        "imports asyncio",
        "imports pytest",
        "from apps.api.api.services import memory",
        "from packages.db.models import AgentSession, Skill",
        "class Message",
        "class FakeScalarResult"
      ],
      "tests/test_memory_cli.py": [
        "from __future__ import annotations",
        "imports json",
        "imports os",
        "imports subprocess",
        "imports sys",
        "imports threading",
        "from http.server import BaseHTTPRequestHandler, HTTPServer",
        "from pathlib import Path",
        "function test_memory_init_session_creates_valid_json",
        "function test_memory_upload_missing_api_key_exits_one"
      ],
      "tests/test_model_registry.py": [
        "imports os",
        "imports unittest",
        "from skilgen.agents.model_registry import resolve_model_settings",
        "from skilgen.core.models import SkilgenConfig",
        "class ModelRegistryTests"
      ],
      "tests/test_org_intelligence_api.py": [
        "from __future__ import annotations",
        "from datetime import UTC, datetime, timedelta",
        "from typing import Any",
        "from fastapi import FastAPI",
        "from fastapi.testclient import TestClient",
        "from apps.api.api.auth import get_current_org_id",
        "from apps.api.api.routes import orgs",
        "from packages.db.database import get_db",
        "from packages.db.models import AnalysisRun, Org, Repo, ScoreHistory",
        "function _now"
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
      "tests/test_policy_engine.py": [
        "from __future__ import annotations",
        "from datetime import datetime, timedelta",
        "from types import SimpleNamespace",
        "imports unittest",
        "from apps.api.api.services import policy",
        "function _policy",
        "function _repo",
        "function _skill",
        "class PolicyEngineTests"
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
      "tests/test_process_parsers.py": [
        "from __future__ import annotations",
        "imports json",
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports unittest",
        "imports zipfile",
        "from skilgen.parsers.confluence import parse_confluence_file, parse_confluence_source",
        "from skilgen.parsers.notion import parse_notion_api_json, parse_notion_file, parse_notion_source",
        "from skilgen.parsers.runbook import ProcessParserError, parse_runbook_file, parse_runbook_source",
        "class RunbookParserTests"
      ],
      "tests/test_rate_limit_store.py": [
        "from __future__ import annotations",
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports unittest",
        "from skilgen.core.rate_limit_store import consume_rate_limit",
        "class RateLimitStoreTests"
      ],
      "tests/test_red_flags.py": [
        "from __future__ import annotations",
        "from datetime import UTC, datetime, timedelta",
        "from typing import Any",
        "from fastapi import FastAPI",
        "from fastapi.testclient import TestClient",
        "from apps.api.api.auth import get_current_org_id",
        "from apps.api.api.routes import orgs",
        "from apps.api.api.services.redflags import compute_repo_red_flags",
        "from packages.db.database import get_db",
        "from packages.db.models import Org, Repo, Skill"
      ],
      "tests/test_registry.py": [
        "from __future__ import annotations",
        "from datetime import datetime, timedelta",
        "from pathlib import Path",
        "from types import SimpleNamespace",
        "from apps.api.api.routes import registry",
        "function _source",
        "function test_publish_skill_creates_registry_entry_with_scores",
        "function test_publish_same_skill_twice_has_no_conflict_guard",
        "function test_get_org_entries_filters_visibility_and_search",
        "function test_install_marketplace_entry_increments_install_count"
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
      "tests/test_security_parsers.py": [
        "from __future__ import annotations",
        "from pathlib import Path",
        "from tempfile import TemporaryDirectory",
        "imports json",
        "imports unittest",
        "from skilgen.parsers.sarif import parse_sarif",
        "from skilgen.parsers.sbom import parse_sbom",
        "from skilgen.parsers.security_policy import parse_security_policy",
        "class SarifParserTests",
        "class SbomParserTests"
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
      "tests/test_skill_sources_api.py": [
        "from __future__ import annotations",
        "from pathlib import Path",
        "from types import SimpleNamespace",
        "from apps.api.api.routes.repos import _build_coverage_map, _compute_skill_score, _coverage_score",
        "from packages.db.models.skill import skill_category_for_source_type",
        "function _read",
        "function test_repo_skill_sources_endpoint_requires_auth_and_returns_coverage_contract",
        "function test_analyze_source_endpoint_validates_body_and_queues_job",
        "function test_skill_content_update_endpoint_versions_content_and_requires_org_scope",
        "function test_compute_skill_score_for_manual_content_update"
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
      "extensions/vscode-skillayer/src/check.ts": [
        "Error",
        "checkDiff",
        "cwd",
        "diffCurrentFile",
        "execAsync",
        "fetch",
        "getStagedDiff",
        "import",
        "join",
        "json",
        "map",
        "promisify",
        "slice",
        "split",
        "startsWith",
        "stringify"
      ],
      "extensions/vscode-skillayer/src/config.ts": [
        "getConfig",
        "getConfiguration",
        "isConfigured"
      ],
      "extensions/vscode-skillayer/src/diagnostics.ts": [
        "Diagnostic",
        "endsWith",
        "filter",
        "findingsToDiagnostics",
        "lineAt",
        "map",
        "max",
        "min"
      ],
      "extensions/vscode-skillayer/src/extension.ts": [
        "activate",
        "async",
        "checkCurrentFile",
        "checkDiff",
        "checkDocument",
        "checkStaged",
        "clear",
        "createDiagnosticCollection",
        "createStatusBarItem",
        "deactivate",
        "diffCurrentFile",
        "dispose",
        "findingsToDiagnostics",
        "getConfig",
        "getStagedDiff",
        "getText",
        "isConfigured",
        "onDidSaveTextDocument",
        "push",
        "registerCommand",
        "set",
        "show",
        "showErrorMessage",
        "showInformationMessage"
      ],
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
      "scripts/deploy_web.py": [
        "ArgumentParser",
        "FileNotFoundError",
        "Path",
        "SystemExit",
        "ValueError",
        "add_argument",
        "append",
        "bool",
        "deploy_command",
        "deploy_web",
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
        "resolve",
        "run"
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
        "add_done_callback",
        "append",
        "append_audit_event",
        "append_job_event",
        "bool",
        "closing",
        "connect",
        "dumps",
        "execute",
        "fetchall"
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
        "Request",
        "Thread",
        "_elapsed",
        "_eval_api_key",
        "_eval_api_request",
        "_eval_api_url",
        "_eval_org_id",
        "_format_analytics_summary",
        "_infer_percent",
        "_memory_session_files",
        "_print_eval_gaps",
        "_print_eval_status",
        "_render_line",
        "_render_source_summary",
        "_upload_memory_sessions",
        "_write_memory_session_template",
        "activate_external_skill",
        "activate_mcp_connector"
      ],
      "skilgen/commands/check.py": [
        "CheckConfig",
        "CheckConfigError",
        "Path",
        "Request",
        "_first_nonempty",
        "_format_item",
        "_hook_template",
        "_items",
        "append",
        "bool",
        "chmod",
        "cwd",
        "dataclass",
        "decode",
        "dumps",
        "encode",
        "exists",
        "get",
        "getattr",
        "getenv",
        "install_hook",
        "isinstance",
        "join",
        "len"
      ],
      "skilgen/core/analytics.py": [
        "Counter",
        "Path",
        "_analytics_path",
        "_detect_agent_runtime",
        "_frontmatter_int",
        "_iter_repo_skill_files",
        "_modeled_attention_score",
        "_normalize_skill_path",
        "_richness_score",
        "_skill_content_metrics",
        "_skill_title_and_summary",
        "_timestamp",
        "active_external_skills",
        "add",
        "any",
        "append",
        "as_posix",
        "count",
        "defaultdict",
        "dumps",
        "endswith",
        "exists",
        "findall",
        "float"
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
        "_source_dict_value",
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
        "lower"
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
        "_frontmatter_number",
        "_groundedness_score",
        "_groundedness_score_for_skills",
        "_has_git_metadata",
        "_iter_source_files",
        "_materialized_domains",
        "_nodes_by_domain",
        "_parse_check_paths",
        "_parse_references",
        "_quality_gates",
        "_resolve_placeholder_path"
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
        "Request",
        "_auto_sync_to_skillayer",
        "_emit",
        "_has_skilgen_hook",
        "_local_analytics_events",
        "_upload_analytics",
        "_write_claude_code_hook",
        "any",
        "append",
        "append_audit_event",
        "append_run_event",
        "as_posix",
        "build_agent_decision",
        "build_codebase_context",
        "classify_repo_change",
        "clear_codebase_signal_caches",
        "clear_source_graph_caches",
        "close",
        "compute_freshness_report",
        "create_run_memory",
        "current_runtime_mode",
        "decode",
        "dumps"
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
        "_anti_pattern_title",
        "_anti_patterns_for_spec",
        "_architecture_domain_map",
        "_candidate_source_paths",
        "_compute_richness_score",
        "_dependency_ecosystems_for_spec",
        "_dynamic_child_specs",
        "_dynamic_parent_specs",
        "_dynamic_summary_paths",
        "_emit_progress",
        "_extract_code_example",
        "_extract_code_examples",
        "_frontmatter_value",
        "_interesting_code_window",
        "_invert_pattern",
        "_language_for_path",
        "_legacy_child_specs",
        "_looks_generated_skill",
        "_materialization_plan_map",
        "_parent_reference_map",
        "_prune_stale_generated_paths",
        "_relative_skill_ref"
      ],
      "skilgen/hooks/claude_code.py": [
        "Path",
        "chmod",
        "mkdir",
        "resolve",
        "write_text"
      ],
      "skilgen/hooks/claude_code_hook.py": [
        "Path",
        "Request",
        "_absolute_path",
        "_after_content_for_tool",
        "_already_fired",
        "_api_base",
        "_artifact_cache_path",
        "_capture_before",
        "_file_path_for_tool",
        "_fire_skill_load",
        "_handle_post_tool",
        "_handle_pre_tool",
        "_hook_event_name",
        "_load_event",
        "_mark_fired",
        "_pop_before",
        "_post_json",
        "_read_content",
        "_repo_root",
        "_session_id",
        "_session_lock_path",
        "_tool_input",
        "_tool_name",
        "_tool_response"
      ],
      "skilgen/hooks/cursor.py": [
        "Path",
        "chmod",
        "mkdir",
        "resolve",
        "write_text"
      ],
      "skilgen/hooks/cursor_watcher.py": [
        "Path",
        "Popen",
        "_skills_dir",
        "exists",
        "items",
        "len",
        "list",
        "log_skill_usage",
        "print",
        "resolve",
        "rglob",
        "scan",
        "sleep",
        "stat",
        "str"
      ],
      "skilgen/parsers/__init__.py": [
        "asdict",
        "dataclass",
        "field",
        "values"
      ],
      "skilgen/parsers/auto_detect.py": [
        "Path",
        "_candidate_sources",
        "_configured_paths",
        "_detect_with_defaults",
        "_resolve_entries",
        "_selected_sources",
        "any",
        "append",
        "exists",
        "extend",
        "fromkeys",
        "get",
        "glob",
        "is_absolute",
        "isinstance",
        "items",
        "load_config",
        "load_source_config",
        "normalize_source_name",
        "resolve",
        "sorted",
        "str",
        "strip"
      ],
      "skilgen/parsers/confluence.py": [
        "Path",
        "ProcessParserError",
        "ProcessSource",
        "TemporaryDirectory",
        "ZipFile",
        "_ConfluenceHTMLExtractor",
        "__init__",
        "_clean_ordered_item",
        "_clean_text",
        "_dedupe",
        "_extract_meta",
        "_first_paragraph",
        "_local_name",
        "_normalize_body",
        "_ordered_items",
        "_parse_confluence_html",
        "_parse_confluence_xml",
        "_parse_confluence_zip",
        "_section_groups",
        "_section_items",
        "_title_from_filename",
        "_xml_code_blocks",
        "_xml_labels",
        "_xml_table_rows"
      ],
      "skilgen/parsers/dbt.py": [
        "DbtColumn",
        "DbtIssue",
        "DbtMacro",
        "DbtModel",
        "DbtProjectAnalysis",
        "DbtProjectParseError",
        "DbtSourceTable",
        "Path",
        "_as_list",
        "_collect_macros",
        "_collect_schema_docs",
        "_configured_paths",
        "_find_cycles",
        "_hardcoded_relations",
        "_infer_model_group",
        "_is_under_model_roots",
        "_iter_sql_models",
        "_load_yaml_mapping",
        "_normalize_tests",
        "_optional_string",
        "_parse_columns",
        "add",
        "any",
        "append"
      ],
      "skilgen/parsers/graphql.py": [
        "ApiSpecFinding",
        "ApiSpecItem",
        "ApiSpecParseResult",
        "ApiSpecParserError",
        "Path",
        "_graphql_result",
        "_is_paginated",
        "_looks_like_list_object",
        "_mostly_lower_camel",
        "_named_type",
        "_parse_introspection",
        "_parse_sdl",
        "_read_non_empty",
        "_render_type",
        "_unique",
        "add",
        "append",
        "bool",
        "compile",
        "endswith",
        "exists",
        "extend",
        "findall",
        "finditer"
      ],
      "skilgen/parsers/helm.py": [
        "Counter",
        "HelmChartParseResult",
        "HelmParserError",
        "HelmTemplateSummary",
        "Path",
        "_chart_metadata",
        "_dependencies",
        "_load_yaml_file",
        "_template_summaries",
        "_type_name",
        "_values_schema",
        "add",
        "any",
        "append",
        "as_posix",
        "compile",
        "dataclass",
        "dict",
        "exists",
        "field",
        "findall",
        "fromkeys",
        "get",
        "is_dir"
      ],
      "skilgen/parsers/incident.py": [
        "Counter",
        "GitHubIncidentIssue",
        "IncidentParseError",
        "IncidentRecord",
        "IncidentSourceAnalysis",
        "PagerDutyMetrics",
        "Path",
        "Request",
        "_MarkdownSection",
        "_analysis_from_incidents",
        "_clean_evidence_lines",
        "_clean_inline_markdown",
        "_cluster_title",
        "_coerce_pagerduty_incidents",
        "_dedupe",
        "_dedupe_paths",
        "_derive_incident_patterns",
        "_derive_service_domain",
        "_extract_body_summary",
        "_extract_duration_minutes",
        "_extract_markdown_title",
        "_extract_pagerduty_urgency",
        "_first_paragraph",
        "_first_string"
      ],
      "skilgen/parsers/kafka.py": [
        "KafkaAnalysis",
        "KafkaField",
        "KafkaIssue",
        "KafkaParseError",
        "KafkaSchema",
        "KafkaTopic",
        "Path",
        "_audit_schemas",
        "_audit_topics",
        "_avro_schema_from_mapping",
        "_avro_type_allows_null",
        "_avro_type_name",
        "_collect_configs",
        "_int_or_none",
        "_is_kafka_candidate",
        "_json_schema_from_mapping",
        "_json_type_name",
        "_parse_avro_schema",
        "_parse_json_schema",
        "_schema_from_mapping",
        "_string_or_none",
        "_topic_from_payload",
        "any",
        "append"
      ],
      "skilgen/parsers/kubernetes.py": [
        "Counter",
        "KubernetesManifestParseResult",
        "KubernetesObjectSummary",
        "KubernetesParserError",
        "Path",
        "_candidate_manifest_roots",
        "_collect_patterns",
        "_container_runs_non_root",
        "_containers",
        "_data_keys",
        "_has_probe",
        "_has_resource_limits",
        "_ingress_hosts",
        "_is_privileged",
        "_is_within_helm_chart",
        "_load_yaml_documents",
        "_looks_like_kubernetes_manifest",
        "_looks_sensitive_key",
        "_manifest_files",
        "_nonzero_user",
        "_pod_spec",
        "_runs_non_root",
        "_safe_port",
        "_summarize_object"
      ],
      "skilgen/parsers/notion.py": [
        "Client",
        "Path",
        "ProcessParserError",
        "ProcessSource",
        "_blocks_to_markdown",
        "_notion_get",
        "_notion_labels",
        "_notion_title",
        "_parse_markdown_document",
        "_parse_markdown_text_source",
        "_rate_limit",
        "_rich_text",
        "_source_from_markdown_text",
        "append",
        "exists",
        "extend",
        "fromkeys",
        "get",
        "int",
        "is_dir",
        "is_file",
        "isdigit",
        "isinstance",
        "join"
      ],
      "skilgen/parsers/openapi.py": [
        "ApiSpecFinding",
        "ApiSpecItem",
        "ApiSpecParseResult",
        "ApiSpecParserError",
        "Path",
        "_auth_schemes",
        "_compact",
        "_error_responses",
        "_examples",
        "_load_mapping",
        "_path_group",
        "_rate_limits",
        "_raw_pii_examples",
        "_schema_names",
        "_schema_refs",
        "_security_names",
        "_spec_version",
        "_title",
        "_unique",
        "_walk_pairs",
        "any",
        "append",
        "compile",
        "dumps"
      ],
      "skilgen/parsers/postman.py": [
        "ApiSpecFinding",
        "ApiSpecItem",
        "ApiSpecParseResult",
        "ApiSpecParserError",
        "Path",
        "_auth_names",
        "_event_list",
        "_hardcoded_tokens",
        "_hardcoded_urls",
        "_iter_requests",
        "_load_collection",
        "_method",
        "_scripts",
        "_unique",
        "_url",
        "append",
        "compile",
        "dumps",
        "exists",
        "extend",
        "findall",
        "fromkeys",
        "get",
        "isinstance"
      ],
      "skilgen/parsers/runbook.py": [
        "Path",
        "ProcessParserError",
        "ProcessSource",
        "_clean_inline",
        "_clean_list_marker",
        "_dedupe",
        "_extract_anti_patterns",
        "_extract_check_paths",
        "_extract_code_blocks",
        "_extract_description",
        "_extract_evidence",
        "_extract_patterns",
        "_extract_steps",
        "_extract_title",
        "_is_table_line",
        "_list_or_paragraph_items",
        "_looks_like_runbook_path",
        "_numbered_items",
        "_parse_markdown_document",
        "_parse_markdown_text",
        "_section_map",
        "_strip_frontmatter",
        "_title_from_filename",
        "add"
      ],
      "skilgen/parsers/runner.py": [
        "Path",
        "SourceRunResult",
        "_call_parser",
        "_resolved_paths",
        "_selected_sources",
        "append",
        "detect_source_paths",
        "extend",
        "fromkeys",
        "get",
        "is_absolute",
        "items",
        "normalize_skill_sources",
        "normalize_source_name",
        "resolve",
        "setdefault",
        "sorted",
        "str",
        "strip",
        "write_skill_sources"
      ],
      "skilgen/parsers/sarif.py": [
        "Path",
        "SarifFinding",
        "SarifResult",
        "SarifTool",
        "ValueError",
        "_anti_patterns_from_rule",
        "_categories_for",
        "_dedupe_tools",
        "_extract_cwes",
        "_extract_tags",
        "_file_paths_from_result",
        "_flatten_rule_metadata",
        "_load_sarif_json",
        "_normalize_label",
        "_patterns",
        "_result_severity",
        "_rule_id_from_index",
        "_rules_from_run",
        "_string_value",
        "_tool_from_run",
        "add",
        "append",
        "compile",
        "dataclass"
      ],
      "skilgen/parsers/sbom.py": [
        "Path",
        "SbomPackage",
        "SbomResult",
        "ValueError",
        "_build_result",
        "_component_name",
        "_cyclonedx_licenses",
        "_cyclonedx_xml_licenses",
        "_cyclonedx_xml_spec_version",
        "_dedupe_license_values",
        "_dependency_risk_key",
        "_ecosystem_from_cpes",
        "_ecosystem_from_purls",
        "_is_cyclonedx_json",
        "_is_spdx",
        "_load_json",
        "_local_name",
        "_namespace",
        "_normalize_license",
        "_parse_cyclonedx_json",
        "_parse_cyclonedx_xml",
        "_parse_spdx_json",
        "_patterns",
        "_read_non_empty"
      ],
      "skilgen/parsers/security_policy.py": [
        "Path",
        "SecurityPolicyResult",
        "ValueError",
        "_dedupe",
        "_disclosure_terms",
        "_parse_security_markdown",
        "_parse_structured_json",
        "_parse_structured_payload",
        "_parse_structured_yaml",
        "_read_non_empty",
        "_reporting_lines",
        "_string_list",
        "_string_list_or_mapping",
        "_supported_version_lines",
        "add",
        "any",
        "append",
        "compile",
        "dataclass",
        "field",
        "findall",
        "finditer",
        "fromkeys",
        "get"
      ],
      "skilgen/parsers/sources.py": [
        "AttributeError",
        "SkillSource",
        "SourceRunResult",
        "_append_section",
        "_call_parser",
        "_dedupe",
        "_default_domain",
        "_description",
        "_existing",
        "_field_list",
        "_finding_messages",
        "_first_callable",
        "_glob_existing",
        "_normalize_grouped_api_result",
        "_selected_sources",
        "_title",
        "add",
        "append",
        "callable",
        "dataclass",
        "detect_source_paths",
        "exists",
        "extend",
        "field"
      ],
      "skilgen/parsers/sql_schema.py": [
        "Path",
        "SqlColumn",
        "SqlConstraint",
        "SqlIndex",
        "SqlIssue",
        "SqlSchemaAnalysis",
        "SqlSchemaParseError",
        "SqlTable",
        "_audit_schema",
        "_column_foreign_key_constraint",
        "_constraint_from_export",
        "_extract_create_tables",
        "_find_matching_paren",
        "_foreign_key_constraint_from_export",
        "_format_fk_target",
        "_json_type_to_sql",
        "_normalize_name",
        "_optional_name",
        "_parse_column",
        "_parse_indexes",
        "_parse_table_constraint",
        "_split_fk_target",
        "_split_identifier_list",
        "_split_top_level"
      ],
      "skilgen/parsers/terraform.py": [
        "Counter",
        "Path",
        "TerraformParseResult",
        "TerraformParserError",
        "TerraformResource",
        "_advance_to_next_line",
        "_as_list",
        "_contains_key",
        "_extract_block_body",
        "_hardcoded_value_findings",
        "_has_any_tags",
        "_has_key",
        "_has_remote_state_data",
        "_iter_backends",
        "_iter_named_blocks",
        "_iter_resources",
        "_load_hcl",
        "_looks_sensitive",
        "_matching_brace_index",
        "_parse_hcl_mapping",
        "_public_mapping",
        "_read_hcl_scalar",
        "_read_text",
        "_redacted_value"
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
        "urlencode",
        "urlopen"
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
        "_detect_agent_runtime",
        "analytics_summary",
        "assertEqual",
        "assertGreater",
        "assertIn",
        "assertNotEqual",
        "assertTrue",
        "dict",
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
      "tests/test_api_key.py": [
        "FakeDb",
        "FakeResult",
        "FastAPI",
        "SimpleNamespace",
        "TestClient",
        "_client",
        "_credentials",
        "_org",
        "append",
        "get",
        "get_current_org_id",
        "include_router",
        "json",
        "pop",
        "post",
        "run",
        "setattr",
        "update"
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
      "tests/test_api_spec_parsers.py": [
        "Path",
        "TemporaryDirectory",
        "any",
        "assertEqual",
        "assertIn",
        "assertRaisesRegex",
        "assertTrue",
        "main",
        "parse_graphql_schema",
        "parse_openapi_spec",
        "parse_postman_collection",
        "write_text"
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
      "tests/test_audit_log.py": [
        "RuntimeError",
        "SimpleNamespace",
        "_FakeDb",
        "_audit_event_response",
        "append",
        "assertEqual",
        "assertIn",
        "emit",
        "len",
        "main",
        "open",
        "read",
        "utcnow"
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
      "tests/test_cli_sources.py": [
        "Path",
        "Result",
        "TemporaryDirectory",
        "_render_source_summary",
        "_source_skill_files",
        "detect_source_paths",
        "join",
        "len",
        "mkdir",
        "read_text",
        "run_source_parsers",
        "sorted",
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
      "tests/test_dashboard_error_boundaries.py": [
        "Path",
        "items",
        "read",
        "read_text",
        "resolve"
      ],
      "tests/test_data_parsers.py": [
        "Path",
        "TemporaryDirectory",
        "any",
        "assertEqual",
        "assertIn",
        "assertNotIn",
        "assertRaisesRegex",
        "assertTrue",
        "len",
        "main",
        "next",
        "parse_dbt_project",
        "parse_kafka_artifact",
        "parse_sql_schema",
        "write_text"
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
      "tests/test_eval.py": [
        "FakeDb",
        "FakeResult",
        "FakeScalars",
        "FastAPI",
        "SimpleNamespace",
        "TestClient",
        "_detect_skill_gaps",
        "append",
        "client",
        "extend",
        "get",
        "import_module",
        "include_router",
        "isoformat",
        "json",
        "len",
        "patch",
        "payload",
        "pop",
        "post",
        "range",
        "repo",
        "setattr",
        "skill"
      ],
      "tests/test_eval_cli.py": [
        "main",
        "readouterr",
        "run_cli",
        "setattr",
        "setenv"
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
      "tests/test_generation_quality.py": [
        "Path",
        "SkillSpec",
        "TemporaryDirectory",
        "_auto_sync_to_skillayer",
        "_compute_richness_score",
        "_extract_code_example",
        "_spec",
        "_write_claude_code_hook",
        "analytics_summary",
        "assertEqual",
        "assertFalse",
        "assertGreater",
        "assertGreaterEqual",
        "assertIn",
        "assertIsNone",
        "assertNotIn",
        "assertTrue",
        "count",
        "dict",
        "join",
        "len",
        "loads",
        "main",
        "mkdir"
      ],
      "tests/test_half_life.py": [
        "Path",
        "SimpleNamespace",
        "_source",
        "abs",
        "datetime",
        "read_text",
        "resolve",
        "timedelta"
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
      "tests/test_improvement_loop.py": [
        "Path",
        "SimpleNamespace",
        "_improvement_plan",
        "_read",
        "_skill",
        "_skill_code_block_count",
        "_skill_improvement_plan",
        "_skill_word_count",
        "issubset",
        "len",
        "read_text",
        "resolve",
        "set",
        "split",
        "timedelta",
        "update",
        "utcnow"
      ],
      "tests/test_incident_parsers.py": [
        "Path",
        "TemporaryDirectory",
        "any",
        "assertEqual",
        "assertIn",
        "assertIsNone",
        "assertIsNotNone",
        "assertRaisesRegex",
        "assertTrue",
        "dict",
        "fetch_github_incident_issues",
        "join",
        "len",
        "main",
        "parse_incident_sources",
        "parse_markdown_postmortem",
        "parse_pagerduty_export",
        "resolve",
        "write_text"
      ],
      "tests/test_infra_parsers.py": [
        "Path",
        "TemporaryDirectory",
        "assertEqual",
        "assertIn",
        "assertNotIn",
        "assertRaisesRegex",
        "assertTrue",
        "main",
        "parse_helm_chart",
        "parse_kubernetes_manifests",
        "parse_terraform_directory",
        "repr",
        "write_text"
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
      "tests/test_llm_config.py": [
        "assertEqual",
        "assertIn",
        "assertNotEqual",
        "assertNotIn",
        "decrypt_key",
        "encrypt_key",
        "index",
        "key_hint",
        "main",
        "open",
        "read"
      ],
      "tests/test_memory_capture.py": [
        "AgentSession",
        "FakeDb",
        "FakeResult",
        "FakeScalarResult",
        "Message",
        "Path",
        "Skill",
        "_build_transcript_text",
        "_extract_session_knowledge",
        "_session",
        "_skill",
        "_summarise_transcript",
        "append",
        "delenv",
        "getattr",
        "len",
        "now",
        "range",
        "read_text",
        "replace",
        "resolve",
        "run",
        "setattr",
        "startswith"
      ],
      "tests/test_memory_cli.py": [
        "HTTPServer",
        "Thread",
        "dumps",
        "encode",
        "end_headers",
        "get",
        "glob",
        "int",
        "items",
        "join",
        "len",
        "list",
        "loads",
        "mkdir",
        "read",
        "read_text",
        "run",
        "send_header",
        "send_response",
        "set",
        "shutdown",
        "start",
        "str",
        "write"
      ],
      "tests/test_model_registry.py": [
        "SkilgenConfig",
        "assertEqual",
        "assertIsNone",
        "assertTrue",
        "main",
        "resolve_model_settings"
      ],
      "tests/test_org_intelligence_api.py": [
        "AnalysisRun",
        "AssertionError",
        "FakeDb",
        "FakeResult",
        "FakeScalarResult",
        "FastAPI",
        "Org",
        "Repo",
        "ScoreHistory",
        "Skill",
        "TestClient",
        "_client",
        "_history",
        "_now",
        "_populated_db",
        "_repo",
        "_run",
        "_skill",
        "append",
        "get",
        "include_router",
        "int",
        "isinstance",
        "json"
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
      "tests/test_policy_engine.py": [
        "SimpleNamespace",
        "_evaluate_rule",
        "_policy",
        "_repo",
        "_skill",
        "assertEqual",
        "assertIn",
        "assertTrue",
        "len",
        "main",
        "open",
        "read",
        "timedelta",
        "update",
        "utcnow"
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
      "tests/test_process_parsers.py": [
        "Path",
        "TemporaryDirectory",
        "ZipFile",
        "any",
        "assertEqual",
        "assertIn",
        "assertRaisesRegex",
        "assertTrue",
        "len",
        "loads",
        "main",
        "mkdir",
        "parse_confluence_file",
        "parse_confluence_source",
        "parse_notion_api_json",
        "parse_notion_file",
        "parse_notion_source",
        "parse_runbook_file",
        "parse_runbook_source",
        "read_text",
        "write",
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
      "tests/test_red_flags.py": [
        "AssertionError",
        "FakeDb",
        "FakeResult",
        "FakeScalarResult",
        "FastAPI",
        "Repo",
        "Skill",
        "TestClient",
        "_client",
        "_repo",
        "_skill",
        "any",
        "compute_repo_red_flags",
        "get",
        "include_router",
        "json",
        "now",
        "pop",
        "replace",
        "sorted",
        "timedelta"
      ],
      "tests/test_registry.py": [
        "Path",
        "_source",
        "read_text",
        "resolve",
        "split"
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
      "tests/test_security_parsers.py": [
        "Path",
        "TemporaryDirectory",
        "any",
        "assertEqual",
        "assertFalse",
        "assertIn",
        "assertRaisesRegex",
        "assertTrue",
        "dumps",
        "main",
        "parse_sarif",
        "parse_sbom",
        "parse_security_policy",
        "resolve",
        "str",
        "write_text"
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
      "tests/test_skill_sources_api.py": [
        "Path",
        "SimpleNamespace",
        "_build_coverage_map",
        "_compute_skill_score",
        "_coverage_score",
        "_read",
        "read_text",
        "resolve",
        "skill_category_for_source_type"
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
      ".claude/settings.json": [
        "env:CLAUDE_TOOL_INPUT_FILE_PATH",
        "env:SKILLAYER_API_KEY",
        "env:SKILLAYER_REPO_ID"
      ],
      ".env.example": [
        "env:ADMIN_SECRET",
        "env:API_URL",
        "env:CRON_SECRET",
        "env:DATABASE_URL",
        "env:DEPLOYMENT_MODE",
        "env:GITHUB_APP_ID",
        "env:GITHUB_APP_PRIVATE_KEY",
        "env:GITHUB_WEBHOOK_SECRET",
        "env:NEXT_PUBLIC_ADMIN_EMAILS",
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
        "env:POSTGRES_PASSWORD",
        "env:QSTASH_CURRENT_SIGNING_KEY",
        "env:QSTASH_NEXT_SIGNING_KEY",
        "env:QSTASH_TOKEN",
        "env:REDIS_URL",
        "env:SMTP",
        "env:SMTP_FROM",
        "env:SMTP_HOST",
        "env:SMTP_PASSWORD",
        "env:SMTP_PORT",
        "env:SMTP_USER",
        "env:WORKOS_API_KEY",
        "env:WORKOS_CLIENT_ID",
        "env:WORKOS_COOKIE_PASSWORD",
        "env:WORKOS_REDIRECT_URI",
        "runtime:docker",
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
      ".github/workflows/vercel-production.yml": [
        "env:API",
        "env:JSON",
        "env:VERCEL_API_PROJECT_ID",
        "env:VERCEL_DASHBOARD_PROJECT_ID",
        "env:VERCEL_ORG_ID",
        "env:VERCEL_PROJECT_ID",
        "env:VERCEL_SCOPE",
        "env:VERCEL_TOKEN"
      ],
      "apps/api/.env.example": [
        "env:ADMIN_SECRET",
        "env:CRON_SECRET",
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
        "env:SKILLAYER_INSTANCE",
        "env:SKILLAYER_VERSION",
        "env:SMTP_FROM",
        "env:SMTP_HOST",
        "env:SMTP_PASSWORD",
        "env:SMTP_PORT",
        "env:SMTP_USER",
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
        "env:ENTRYPOINT",
        "env:EXPOSE",
        "env:FROM",
        "env:HEALTHCHECK",
        "env:RUN",
        "env:WORKDIR",
        "runtime:docker"
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
      "apps/api/api/v8/insights/critical_ops.yaml": [
        "env:SLA"
      ],
      "apps/api/api/v8/policy/starter_packs/agent-compliance.yaml": [
        "env:CC6",
        "env:CLI",
        "env:SOC2"
      ],
      "apps/api/api/v8/policy/starter_packs/fedramp-mod.yaml": [
        "env:DLP",
        "env:NIST"
      ],
      "apps/api/api/v8/policy/starter_packs/hipaa.yaml": [
        "env:HIPAA",
        "env:PHI"
      ],
      "apps/api/api/v8/policy/starter_packs/license-hygiene.yaml": [
        "env:AGPL",
        "env:GPL"
      ],
      "apps/api/api/v8/policy/starter_packs/soc2.yaml": [
        "env:CC6",
        "env:CC7",
        "env:CC8",
        "env:SOC2",
        "runtime:kubernetes"
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
      "apps/dashboard/Dockerfile": [
        "env:ARG",
        "env:BUILD_STANDALONE",
        "env:CMD",
        "env:COPY",
        "env:ENV",
        "env:EXPOSE",
        "env:FROM",
        "env:NEXT_PUBLIC_API_URL",
        "env:NODE_ENV",
        "env:RUN",
        "env:WORKDIR",
        "runtime:docker"
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
      "extensions/vscode-skillayer/package-lock.json": [
        "env:MIT",
        "runtime:s3"
      ],
      "extensions/vscode-skillayer/package.json": [
        "env:API",
        "env:URL"
      ],
      "extensions/vscode-skillayer/tsconfig.json": [
        "env:DOM",
        "env:ES2022"
      ],
      "infra/docker/docker-compose.prod.yml": [
        "env:CMD",
        "env:DEPLOYMENT_MODE",
        "env:NEXT_PUBLIC_API_URL",
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
        "env:API_URL",
        "env:DEPLOYMENT_MODE",
        "env:GITHUB_APP_ID",
        "env:NEXT_PUBLIC_API_URL"
      ],
      "infra/helm/skillayer/templates/deployment-api.yaml": [
        "runtime:docker"
      ],
      "infra/helm/skillayer/templates/deployment-dashboard.yaml": [
        "env:API_URL",
        "env:NEXT_PUBLIC_API_URL",
        "runtime:docker"
      ],
      "infra/helm/skillayer/templates/deployment-worker.yaml": [
        "env:HOSTNAME",
        "runtime:docker"
      ],
      "infra/helm/skillayer/templates/job-migrate.yaml": [
        "runtime:docker",
        "runtime:kubernetes"
      ],
      "infra/helm/skillayer/templates/secret.yaml": [
        "env:WORKOS_API_KEY"
      ],
      "infra/helm/skillayer/values.yaml": [
        "runtime:kubernetes",
        "runtime:postgres",
        "runtime:redis"
      ],
      "mkdocs.yml": [
        "env:API",
        "env:CLI"
      ],
      "package-lock.json": [
        "env:AND",
        "env:B4RT",
        "env:BSD",
        "env:CC0",
        "env:DDKA",
        "env:DJ8BJS4E",
        "env:G3ZA",
        "env:G5KYP6",
        "env:HBV",
        "env:IICI",
        "env:ISC",
        "env:JTF99U",
        "env:K9ZGHG",
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
        "env:RB0",
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
      ],
      "tests/fixtures/cyclonedx_bom.json": [
        "env:BSD",
        "env:GPL",
        "env:NOASSERTION"
      ],
      "tests/fixtures/helm_chart/Chart.yaml": [
        "runtime:postgres"
      ],
      "tests/fixtures/helm_chart/templates/deployment.yaml": [
        "runtime:docker"
      ],
      "tests/fixtures/helm_chart/templates/job.yaml": [
        "runtime:docker",
        "runtime:kubernetes"
      ],
      "tests/fixtures/helm_chart/values.yaml": [
        "runtime:postgres"
      ],
      "tests/fixtures/k8s_deployment.yaml": [
        "env:API_TOKEN",
        "env:LOG_LEVEL",
        "runtime:docker"
      ],
      "tests/fixtures/kafka_topic.yaml": [
        "env:BACKWARD"
      ],
      "tests/fixtures/pagerduty_export.json": [
        "env:API",
        "env:SLO"
      ],
      "tests/fixtures/postman_collection.json": [
        "env:GET",
        "env:POST"
      ],
      "tests/fixtures/security_policy.yml": [
        "env:AGPL",
        "env:GPL"
      ],
      "tests/fixtures/spdx_sbom.json": [
        "env:CC0",
        "env:DOCUMENT",
        "env:GPL",
        "env:MANAGER",
        "env:NOASSERTION",
        "env:PACKAGE",
        "env:SECURITY",
        "env:SPDX",
        "env:SPDXID"
      ],
      "tests/fixtures/terraform_main.tf": [
        "runtime:kubernetes",
        "runtime:s3"
      ]
    },
    "test_mapping": {
      "tests/__init__.py": [
        "skilgen/__init__.py",
        "skilgen/agents/__init__.py",
        "skilgen/api/__init__.py",
        "skilgen/cli/__init__.py",
        "skilgen/commands/__init__.py",
        "skilgen/core/__init__.py"
      ],
      "tests/test_analytics.py": [
        "skilgen/core/analytics.py"
      ],
      "tests/test_api_key.py": [
        "scripts/deploy_api.py",
        "skilgen/api/__init__.py",
        "skilgen/api/jobs.py",
        "skilgen/api/server.py",
        "skilgen/api/service.py"
      ],
      "tests/test_api_smoke.py": [
        "scripts/deploy_api.py",
        "skilgen/api/__init__.py",
        "skilgen/api/jobs.py",
        "skilgen/api/server.py",
        "skilgen/api/service.py"
      ],
      "tests/test_api_spec_parsers.py": [
        "scripts/deploy_api.py",
        "skilgen/agents/language_parsers.py",
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
      "tests/test_audit_log.py": [
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
      "tests/test_cli_sources.py": [
        "skilgen/cli/__init__.py",
        "skilgen/cli/main.py",
        "skilgen/parsers/sources.py"
      ],
      "tests/test_codebase_signals.py": [
        "skilgen/agents/codebase_signals.py",
        "skilgen/core/runtime_signals.py"
      ],
      "tests/test_config.py": [
        "extensions/vscode-skillayer/src/config.ts",
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
      "tests/test_dashboard_error_boundaries.py": [
        "scripts/deploy_dashboard.py"
      ],
      "tests/test_data_parsers.py": [
        "skilgen/agents/language_parsers.py",
        "skilgen/core/runtime_data.py",
        "skilgen/parsers/__init__.py",
        "skilgen/parsers/auto_detect.py",
        "skilgen/parsers/confluence.py",
        "skilgen/parsers/dbt.py"
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
        "skilgen/enterprise_skills.py",
        "skilgen/parsers/security_policy.py"
      ],
      "tests/test_eval_cli.py": [
        "skilgen/cli/__init__.py",
        "skilgen/cli/main.py"
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
        "skilgen/core/rate_limit_store.py",
        "skilgen/parsers/security_policy.py"
      ],
      "tests/test_incident_parsers.py": [
        "skilgen/parsers/incident.py",
        "skilgen/agents/language_parsers.py",
        "skilgen/parsers/__init__.py",
        "skilgen/parsers/auto_detect.py",
        "skilgen/parsers/confluence.py",
        "skilgen/parsers/dbt.py"
      ],
      "tests/test_infra_parsers.py": [
        "skilgen/agents/language_parsers.py",
        "skilgen/parsers/__init__.py",
        "skilgen/parsers/auto_detect.py",
        "skilgen/parsers/confluence.py",
        "skilgen/parsers/dbt.py",
        "skilgen/parsers/graphql.py"
      ],
      "tests/test_jobs.py": [
        "skilgen/api/jobs.py"
      ],
      "tests/test_llm_config.py": [
        "extensions/vscode-skillayer/src/config.ts",
        "skilgen/core/config.py"
      ],
      "tests/test_memory_capture.py": [
        "skilgen/core/project_memory.py",
        "skilgen/core/run_memory.py"
      ],
      "tests/test_memory_cli.py": [
        "skilgen/cli/__init__.py",
        "skilgen/cli/main.py",
        "skilgen/core/project_memory.py",
        "skilgen/core/run_memory.py"
      ],
      "tests/test_model_registry.py": [
        "skilgen/agents/model_registry.py",
        "skilgen/registry_client.py"
      ],
      "tests/test_org_intelligence_api.py": [
        "scripts/deploy_api.py",
        "skilgen/api/__init__.py",
        "skilgen/api/jobs.py",
        "skilgen/api/server.py",
        "skilgen/api/service.py"
      ],
      "tests/test_overview_data.py": [
        "skilgen/core/runtime_data.py"
      ],
      "tests/test_plan_cli.py": [
        "skilgen/cli/__init__.py",
        "skilgen/cli/main.py"
      ],
      "tests/test_policy_engine.py": [
        "skilgen/core/enterprise_policy.py",
        "skilgen/core/identity_policy_store.py",
        "skilgen/parsers/security_policy.py"
      ],
      "tests/test_process_parsers.py": [
        "skilgen/agents/language_parsers.py",
        "skilgen/parsers/__init__.py",
        "skilgen/parsers/auto_detect.py",
        "skilgen/parsers/confluence.py",
        "skilgen/parsers/dbt.py",
        "skilgen/parsers/graphql.py"
      ],
      "tests/test_rate_limit_store.py": [
        "skilgen/core/rate_limit_store.py",
        "skilgen/core/identity_policy_store.py"
      ],
      "tests/test_registry.py": [
        "skilgen/agents/model_registry.py",
        "skilgen/registry_client.py"
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
      "tests/test_security_parsers.py": [
        "skilgen/parsers/security_policy.py",
        "skilgen/agents/language_parsers.py",
        "skilgen/parsers/__init__.py",
        "skilgen/parsers/auto_detect.py",
        "skilgen/parsers/confluence.py",
        "skilgen/parsers/dbt.py"
      ],
      "tests/test_skill_sources_api.py": [
        "scripts/deploy_api.py",
        "skilgen/api/__init__.py",
        "skilgen/api/jobs.py",
        "skilgen/api/server.py",
        "skilgen/api/service.py",
        "skilgen/parsers/sources.py"
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
        "scripts/deploy_web.py",
        "skilgen/api/__init__.py",
        "skilgen/api/jobs.py",
        "skilgen/api/server.py"
      ],
      "tests/test_vercel_dashboard_deploy.py": [
        "scripts/deploy_dashboard.py",
        "scripts/deploy_api.py",
        "scripts/deploy_web.py"
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
        "source_path": "extensions/vscode-skillayer/src/diagnostics.ts",
        "source_symbol": "Finding",
        "relationship": "imports",
        "target_symbol": "./check",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "extensions/vscode-skillayer/src/extension.ts",
        "source_symbol": "getConfig",
        "relationship": "imports",
        "target_symbol": "./config",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "extensions/vscode-skillayer/src/extension.ts",
        "source_symbol": "isConfigured",
        "relationship": "imports",
        "target_symbol": "./config",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "extensions/vscode-skillayer/src/extension.ts",
        "source_symbol": "checkDiff",
        "relationship": "imports",
        "target_symbol": "./check",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "extensions/vscode-skillayer/src/extension.ts",
        "source_symbol": "diffCurrentFile",
        "relationship": "imports",
        "target_symbol": "./check",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "extensions/vscode-skillayer/src/extension.ts",
        "source_symbol": "getStagedDiff",
        "relationship": "imports",
        "target_symbol": "./check",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "extensions/vscode-skillayer/src/extension.ts",
        "source_symbol": "findingsToDiagnostics",
        "relationship": "imports",
        "target_symbol": "./diagnostics",
        "target_path": null,
        "confidence": 0.35
      },
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
        "source_path": "skilgen/commands/check.py",
        "source_symbol": "CheckConfigError",
        "relationship": "extends",
        "target_symbol": "ValueError",
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
        "source_path": "skilgen/parsers/__init__.py",
        "source_symbol": "ApiSpecParserError",
        "relationship": "extends",
        "target_symbol": "ValueError",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "skilgen/parsers/confluence.py",
        "source_symbol": "_ConfluenceHTMLExtractor",
        "relationship": "extends",
        "target_symbol": "HTMLParser",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "skilgen/parsers/dbt.py",
        "source_symbol": "DbtProjectParseError",
        "relationship": "extends",
        "target_symbol": "ValueError",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "skilgen/parsers/helm.py",
        "source_symbol": "HelmParserError",
        "relationship": "extends",
        "target_symbol": "ValueError",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "skilgen/parsers/incident.py",
        "source_symbol": "IncidentParseError",
        "relationship": "extends",
        "target_symbol": "ValueError",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "skilgen/parsers/kafka.py",
        "source_symbol": "KafkaParseError",
        "relationship": "extends",
        "target_symbol": "ValueError",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "skilgen/parsers/kubernetes.py",
        "source_symbol": "KubernetesParserError",
        "relationship": "extends",
        "target_symbol": "ValueError",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "skilgen/parsers/runbook.py",
        "source_symbol": "ProcessParserError",
        "relationship": "extends",
        "target_symbol": "ValueError",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "skilgen/parsers/sql_schema.py",
        "source_symbol": "SqlSchemaParseError",
        "relationship": "extends",
        "target_symbol": "ValueError",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "skilgen/parsers/terraform.py",
        "source_symbol": "TerraformParserError",
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
        "source_path": "tests/test_api_spec_parsers.py",
        "source_symbol": "ApiSpecParserTests",
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
        "source_path": "tests/test_audit_log.py",
        "source_symbol": "AuditLogTests",
        "relationship": "extends",
        "target_symbol": "unittest.IsolatedAsyncioTestCase",
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
        "source_path": "tests/test_data_parsers.py",
        "source_symbol": "DbtParserTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_data_parsers.py",
        "source_symbol": "SqlSchemaParserTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_data_parsers.py",
        "source_symbol": "KafkaParserTests",
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
        "source_path": "tests/test_generation_quality.py",
        "source_symbol": "GenerationQualityTests",
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
        "source_path": "tests/test_incident_parsers.py",
        "source_symbol": "IncidentParserTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_infra_parsers.py",
        "source_symbol": "TerraformParserTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_infra_parsers.py",
        "source_symbol": "KubernetesParserTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_infra_parsers.py",
        "source_symbol": "HelmParserTests",
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
        "source_path": "tests/test_llm_config.py",
        "source_symbol": "LLMConfigTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_memory_cli.py",
        "source_symbol": "UploadHandler",
        "relationship": "extends",
        "target_symbol": "BaseHTTPRequestHandler",
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
        "source_path": "tests/test_policy_engine.py",
        "source_symbol": "PolicyEngineTests",
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
        "source_path": "tests/test_process_parsers.py",
        "source_symbol": "RunbookParserTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_process_parsers.py",
        "source_symbol": "ConfluenceParserTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_process_parsers.py",
        "source_symbol": "NotionParserTests",
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
        "source_path": "tests/test_security_parsers.py",
        "source_symbol": "SarifParserTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_security_parsers.py",
        "source_symbol": "SbomParserTests",
        "relationship": "extends",
        "target_symbol": "unittest.TestCase",
        "target_path": null,
        "confidence": 0.35
      },
      {
        "source_path": "tests/test_security_parsers.py",
        "source_symbol": "SecurityPolicyParserTests",
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
          "path": "tests/fixtures/semgrep_results.sarif",
          "kind": "sast",
          "format": "sarif",
          "signal_count": 2,
          "related_paths": [
            "src/app.py",
            "src/templates.py"
          ],
          "summary": "SAST findings across 2 files"
        }
      ],
      "coverage_by_path": {},
      "test_results": {},
      "sast_findings": {
        "src/app.py": [
          "error:python.lang.security.audit.sql-injection"
        ],
        "src/templates.py": [
          "warning:python.flask.security.xss.audit.template-autoescape"
        ]
      },
      "trace_services": [],
      "recommendations": [
        "Treat SARIF findings as first-class evidence when prioritizing skill hardening and security guidance."
      ]
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
            "asyncio",
            "dataclasses",
            "json",
            "os",
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
            "skilgen/core/generated_outputs.py"
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
          "id": "manifest:apps/dashboard/package.json",
          "kind": "manifest",
          "risk_score": 0.25,
          "signals": [
            "fanout:large-manifest"
          ],
          "dependencies": [
            "@skillayer/config",
            "@skillayer/types",
            "@skillayer/ui",
            "@types/d3",
            "@workos-inc/authkit-nextjs",
            "autoprefixer",
            "d3",
            "lucide-react",
            "next",
            "postcss",
            "posthog-js",
            "react",
            "react-dom",
            "recharts",
            "swr",
            "tailwindcss",
            "@playwright/test",
            "@types/node",
            "@types/react",
            "@types/react-dom",
            "eslint",
            "typescript"
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
          "id": "package:@playwright/test",
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
          "id": "package:@types/d3",
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
          "id": "package:@types/vscode",
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
          "id": "package:d3",
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
          "id": "package:greenlet",
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
          "id": "package:recharts",
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
          "id": "package:swr",
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
            "datetime",
            "json",
            "os",
            "pathlib",
            "skilgen/__init__.py",
            "skilgen/agents/__init__.py",
            "skilgen/agents/requirements_parser.py",
            "skilgen/api/server.py",
            "skilgen/api/service.py",
            "skilgen/autoupdate.py",
            "skilgen/commands/check.py",
            "skilgen/core/analytics.py",
            "skilgen/core/config.py"
          ]
        },
        {
          "id": "skilgen/commands/check.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "dataclasses",
            "json",
            "os",
            "pathlib",
            "subprocess",
            "sys",
            "typing",
            "urllib.error",
            "urllib.request"
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
            "re",
            "skilgen/agents/architecture_planner.py",
            "skilgen/agents/codebase_signals.py",
            "skilgen/agents/requirements_parser.py",
            "skilgen/agents/roadmap_planner.py",
            "skilgen/core/analytics.py",
            "skilgen/core/config.py",
            "skilgen/core/context.py",
            "skilgen/core/dependency_risk.py",
            "skilgen/core/models.py",
            "skilgen/deep_agents_core.py",
            "typing"
          ]
        },
        {
          "id": "skilgen/hooks/claude_code_hook.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "json",
            "os",
            "pathlib",
            "skilgen/core/analytics.py",
            "sys",
            "time",
            "typing",
            "urllib.request"
          ]
        },
        {
          "id": "skilgen/parsers/__init__.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "dataclasses",
            "skilgen/parsers/dbt.py",
            "skilgen/parsers/helm.py",
            "skilgen/parsers/kafka.py",
            "skilgen/parsers/kubernetes.py",
            "skilgen/parsers/runbook.py",
            "skilgen/parsers/sarif.py",
            "skilgen/parsers/sbom.py",
            "skilgen/parsers/security_policy.py",
            "skilgen/parsers/sql_schema.py",
            "skilgen/parsers/terraform.py"
          ]
        },
        {
          "id": "skilgen/parsers/confluence.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "html.parser",
            "pathlib",
            "re",
            "skilgen/parsers/runbook.py",
            "tempfile",
            "xml.etree.ElementTree",
            "zipfile"
          ]
        },
        {
          "id": "skilgen/parsers/incident.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "collections",
            "dataclasses",
            "datetime",
            "json",
            "os",
            "pathlib",
            "re",
            "time",
            "typing",
            "urllib.error",
            "urllib.parse",
            "urllib.request"
          ]
        },
        {
          "id": "skilgen/parsers/notion.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "httpx",
            "json",
            "os",
            "pathlib",
            "skilgen/parsers/runbook.py",
            "time",
            "typing"
          ]
        },
        {
          "id": "skilgen/parsers/openapi.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "collections.abc",
            "json",
            "pathlib",
            "re",
            "skilgen/parsers/__init__.py",
            "typing",
            "yaml"
          ]
        },
        {
          "id": "skilgen/parsers/sbom.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "dataclasses",
            "json",
            "pathlib",
            "re",
            "skilgen/core/dependency_risk.py",
            "typing",
            "urllib.parse",
            "xml.etree"
          ]
        },
        {
          "id": "skilgen/registry_client.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "json",
            "os",
            "pathlib",
            "typing",
            "urllib.error",
            "urllib.parse",
            "urllib.request"
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
          "id": "tests/test_api_key.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "apps/api/api/auth.py",
            "apps/api/api/routes/orgs.py",
            "asyncio",
            "fastapi",
            "fastapi.testclient",
            "packages/db/database.py",
            "types",
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
          "id": "tests/test_api_spec_parsers.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "pathlib",
            "skilgen/parsers/__init__.py",
            "skilgen/parsers/graphql.py",
            "skilgen/parsers/openapi.py",
            "skilgen/parsers/postman.py",
            "tempfile",
            "unittest"
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
          "id": "tests/test_eval.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "apps/api/api/auth.py",
            "datetime",
            "fastapi",
            "fastapi.testclient",
            "importlib",
            "packages/db/database.py",
            "pytest",
            "types",
            "typing"
          ]
        },
        {
          "id": "tests/test_generation_quality.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "asyncio",
            "json",
            "os",
            "pathlib",
            "skilgen/core/analytics.py",
            "skilgen/core/models.py",
            "skilgen/delivery.py",
            "skilgen/generators/skills.py",
            "skilgen/hooks/claude_code_hook.py",
            "skilgen/hooks/cursor_watcher.py",
            "tempfile",
            "time",
            "unittest",
            "unittest.mock"
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
          "id": "tests/test_memory_capture.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "apps/api/api/services/memory.py",
            "asyncio",
            "dataclasses",
            "datetime",
            "packages/db/models/__init__.py",
            "pathlib",
            "pytest"
          ]
        },
        {
          "id": "tests/test_memory_cli.py",
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
            "threading"
          ]
        },
        {
          "id": "tests/test_org_intelligence_api.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "apps/api/api/auth.py",
            "apps/api/api/routes/orgs.py",
            "datetime",
            "fastapi",
            "fastapi.testclient",
            "packages/db/database.py",
            "packages/db/models/__init__.py",
            "typing"
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
          "id": "tests/test_process_parsers.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "json",
            "pathlib",
            "skilgen/parsers/confluence.py",
            "skilgen/parsers/notion.py",
            "skilgen/parsers/runbook.py",
            "tempfile",
            "unittest",
            "zipfile"
          ]
        },
        {
          "id": "tests/test_red_flags.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "apps/api/api/auth.py",
            "apps/api/api/routes/orgs.py",
            "apps/api/api/services/redflags.py",
            "datetime",
            "fastapi",
            "fastapi.testclient",
            "packages/db/database.py",
            "packages/db/models/__init__.py",
            "typing"
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
          "id": "tests/test_security_parsers.py",
          "kind": "source-file",
          "risk_score": 0.15,
          "signals": [
            "fanout:high"
          ],
          "dependencies": [
            "__future__",
            "json",
            "pathlib",
            "skilgen/parsers/sarif.py",
            "skilgen/parsers/sbom.py",
            "skilgen/parsers/security_policy.py",
            "tempfile",
            "unittest"
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
            "packages/db/models/__init__.py",
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
            "packages/db/models/__init__.py",
            "pytest",
            "types",
            "typing"
          ]
        },
        {
          "id": "extensions/vscode-skillayer/src/check.ts",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "vscode"
          ]
        },
        {
          "id": "extensions/vscode-skillayer/src/config.ts",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "vscode"
          ]
        },
        {
          "id": "extensions/vscode-skillayer/src/diagnostics.ts",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "extensions/vscode-skillayer/src/check.ts",
            "vscode"
          ]
        },
        {
          "id": "extensions/vscode-skillayer/src/extension.ts",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "extensions/vscode-skillayer/src/check.ts",
            "extensions/vscode-skillayer/src/config.ts",
            "extensions/vscode-skillayer/src/diagnostics.ts",
            "vscode"
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
            "greenlet",
            "asyncpg",
            "alembic",
            "psycopg2-binary",
            "pydantic",
            "pydantic-settings",
            "httpx",
            "redis",
            "celery",
            "stripe",
            "cryptography"
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
          "id": "manifest:extensions/vscode-skillayer/package.json",
          "kind": "manifest",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "@types/node",
            "@types/vscode",
            "typescript"
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
          "id": "scripts/deploy_web.py",
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
          "id": "skilgen/commands/__init__.py",
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
          "id": "skilgen/hooks/__init__.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": []
        },
        {
          "id": "skilgen/hooks/claude_code.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "pathlib"
          ]
        },
        {
          "id": "skilgen/hooks/cursor.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "pathlib"
          ]
        },
        {
          "id": "skilgen/hooks/cursor_watcher.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "os",
            "pathlib",
            "skilgen/core/analytics.py",
            "subprocess",
            "sys",
            "time"
          ]
        },
        {
          "id": "skilgen/parsers/auto_detect.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "pathlib",
            "skilgen/core/config.py",
            "skilgen/core/models.py",
            "skilgen/parsers/sources.py",
            "typing"
          ]
        },
        {
          "id": "skilgen/parsers/dbt.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "dataclasses",
            "pathlib",
            "re",
            "typing",
            "yaml"
          ]
        },
        {
          "id": "skilgen/parsers/graphql.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "json",
            "pathlib",
            "re",
            "skilgen/parsers/__init__.py",
            "typing"
          ]
        },
        {
          "id": "skilgen/parsers/helm.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "collections",
            "dataclasses",
            "pathlib",
            "re",
            "typing",
            "yaml"
          ]
        },
        {
          "id": "skilgen/parsers/kafka.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "dataclasses",
            "json",
            "pathlib",
            "typing",
            "yaml"
          ]
        },
        {
          "id": "skilgen/parsers/kubernetes.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "collections",
            "dataclasses",
            "pathlib",
            "typing",
            "yaml"
          ]
        },
        {
          "id": "skilgen/parsers/postman.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "json",
            "pathlib",
            "re",
            "skilgen/parsers/__init__.py",
            "typing"
          ]
        },
        {
          "id": "skilgen/parsers/runbook.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "dataclasses",
            "pathlib",
            "re"
          ]
        },
        {
          "id": "skilgen/parsers/runner.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "pathlib",
            "skilgen/core/models.py",
            "skilgen/parsers/auto_detect.py",
            "skilgen/parsers/sources.py",
            "typing"
          ]
        },
        {
          "id": "skilgen/parsers/sarif.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "dataclasses",
            "json",
            "pathlib",
            "re",
            "typing"
          ]
        },
        {
          "id": "skilgen/parsers/security_policy.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "dataclasses",
            "json",
            "pathlib",
            "re",
            "typing",
            "yaml"
          ]
        },
        {
          "id": "skilgen/parsers/sources.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "dataclasses",
            "importlib",
            "pathlib",
            "re",
            "typing"
          ]
        },
        {
          "id": "skilgen/parsers/sql_schema.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "dataclasses",
            "json",
            "pathlib",
            "re",
            "typing"
          ]
        },
        {
          "id": "skilgen/parsers/terraform.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "collections",
            "dataclasses",
            "hcl2",
            "pathlib",
            "re"
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
          "id": "tests/test_audit_log.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "apps/api/api/routes/orgs.py",
            "apps/api/api/services/audit.py",
            "datetime",
            "types",
            "unittest"
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
          "id": "tests/test_cli_sources.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "apps/api/api/analysis.py",
            "pathlib",
            "skilgen/cli/main.py",
            "skilgen/parsers/auto_detect.py",
            "skilgen/parsers/runner.py",
            "tempfile"
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
          "id": "tests/test_dashboard_error_boundaries.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "pathlib"
          ]
        },
        {
          "id": "tests/test_data_parsers.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "pathlib",
            "skilgen/parsers/dbt.py",
            "skilgen/parsers/kafka.py",
            "skilgen/parsers/sql_schema.py",
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
          "id": "tests/test_eval_cli.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "pytest",
            "skilgen/cli/main.py",
            "sys"
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
          "id": "tests/test_half_life.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "apps/api/api/services/half_life.py",
            "datetime",
            "pathlib",
            "types"
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
          "id": "tests/test_improvement_loop.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "apps/api/api/routes/repos.py",
            "datetime",
            "pathlib",
            "types"
          ]
        },
        {
          "id": "tests/test_incident_parsers.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "pathlib",
            "skilgen/parsers/incident.py",
            "tempfile",
            "unittest",
            "unittest.mock"
          ]
        },
        {
          "id": "tests/test_infra_parsers.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "pathlib",
            "skilgen/parsers/helm.py",
            "skilgen/parsers/kubernetes.py",
            "skilgen/parsers/terraform.py",
            "tempfile",
            "unittest"
          ]
        },
        {
          "id": "tests/test_llm_config.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "apps/api/api/services/llm_config.py",
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
          "id": "tests/test_policy_engine.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "apps/api/api/services/policy.py",
            "datetime",
            "types",
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
          "id": "tests/test_registry.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "apps/api/api/routes/registry.py",
            "datetime",
            "pathlib",
            "types"
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
          "id": "tests/test_skill_sources_api.py",
          "kind": "source-file",
          "risk_score": 0.0,
          "signals": [],
          "dependencies": [
            "__future__",
            "apps/api/api/routes/repos.py",
            "packages/db/models/skill.py",
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
          "source": "extensions/vscode-skillayer/src/diagnostics.ts",
          "target": "extensions/vscode-skillayer/src/check.ts",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "extensions/vscode-skillayer/src/extension.ts",
          "target": "extensions/vscode-skillayer/src/check.ts",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "extensions/vscode-skillayer/src/extension.ts",
          "target": "extensions/vscode-skillayer/src/config.ts",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "extensions/vscode-skillayer/src/extension.ts",
          "target": "extensions/vscode-skillayer/src/diagnostics.ts",
          "kind": "repo-import",
          "risk_signals": []
        },
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
          "target": "package:cryptography",
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
          "target": "package:greenlet",
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
          "source": "manifest:apps/dashboard/package.json",
          "target": "package:@playwright/test",
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
          "target": "package:@types/d3",
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
          "target": "package:d3",
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
          "target": "package:recharts",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:apps/dashboard/package.json",
          "target": "package:swr",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
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
          "source": "manifest:extensions/vscode-skillayer/package.json",
          "target": "package:@types/node",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:extensions/vscode-skillayer/package.json",
          "target": "package:@types/vscode",
          "kind": "external-package",
          "risk_signals": [
            "version:loosely-pinned"
          ]
        },
        {
          "source": "manifest:extensions/vscode-skillayer/package.json",
          "target": "package:typescript",
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
          "target": "skilgen/commands/check.py",
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
          "target": "skilgen/core/analytics.py",
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
          "source": "skilgen/hooks/claude_code_hook.py",
          "target": "skilgen/core/analytics.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/hooks/cursor_watcher.py",
          "target": "skilgen/core/analytics.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/parsers/__init__.py",
          "target": "skilgen/parsers/dbt.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/parsers/__init__.py",
          "target": "skilgen/parsers/helm.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/parsers/__init__.py",
          "target": "skilgen/parsers/kafka.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/parsers/__init__.py",
          "target": "skilgen/parsers/kubernetes.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/parsers/__init__.py",
          "target": "skilgen/parsers/runbook.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/parsers/__init__.py",
          "target": "skilgen/parsers/sarif.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/parsers/__init__.py",
          "target": "skilgen/parsers/sbom.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/parsers/__init__.py",
          "target": "skilgen/parsers/security_policy.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/parsers/__init__.py",
          "target": "skilgen/parsers/sql_schema.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/parsers/__init__.py",
          "target": "skilgen/parsers/terraform.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/parsers/auto_detect.py",
          "target": "skilgen/core/config.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/parsers/auto_detect.py",
          "target": "skilgen/core/models.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/parsers/auto_detect.py",
          "target": "skilgen/parsers/sources.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/parsers/confluence.py",
          "target": "skilgen/parsers/runbook.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/parsers/graphql.py",
          "target": "skilgen/parsers/__init__.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/parsers/notion.py",
          "target": "skilgen/parsers/runbook.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/parsers/openapi.py",
          "target": "skilgen/parsers/__init__.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/parsers/postman.py",
          "target": "skilgen/parsers/__init__.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/parsers/runner.py",
          "target": "skilgen/core/models.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/parsers/runner.py",
          "target": "skilgen/parsers/auto_detect.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/parsers/runner.py",
          "target": "skilgen/parsers/sources.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "skilgen/parsers/sbom.py",
          "target": "skilgen/core/dependency_risk.py",
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
          "source": "tests/test_api_key.py",
          "target": "apps/api/api/auth.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_api_key.py",
          "target": "apps/api/api/routes/orgs.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_api_key.py",
          "target": "packages/db/database.py",
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
          "source": "tests/test_api_spec_parsers.py",
          "target": "skilgen/parsers/__init__.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_api_spec_parsers.py",
          "target": "skilgen/parsers/graphql.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_api_spec_parsers.py",
          "target": "skilgen/parsers/openapi.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_api_spec_parsers.py",
          "target": "skilgen/parsers/postman.py",
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
          "source": "tests/test_audit_log.py",
          "target": "apps/api/api/routes/orgs.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_audit_log.py",
          "target": "apps/api/api/services/audit.py",
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
          "source": "tests/test_cli_sources.py",
          "target": "apps/api/api/analysis.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_cli_sources.py",
          "target": "skilgen/cli/main.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_cli_sources.py",
          "target": "skilgen/parsers/auto_detect.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_cli_sources.py",
          "target": "skilgen/parsers/runner.py",
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
          "source": "tests/test_data_parsers.py",
          "target": "skilgen/parsers/dbt.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_data_parsers.py",
          "target": "skilgen/parsers/kafka.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_data_parsers.py",
          "target": "skilgen/parsers/sql_schema.py",
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
          "source": "tests/test_eval.py",
          "target": "apps/api/api/auth.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_eval.py",
          "target": "packages/db/database.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_eval_cli.py",
          "target": "skilgen/cli/main.py",
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
          "source": "tests/test_generation_quality.py",
          "target": "skilgen/core/analytics.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_generation_quality.py",
          "target": "skilgen/core/models.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_generation_quality.py",
          "target": "skilgen/delivery.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_generation_quality.py",
          "target": "skilgen/generators/skills.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_generation_quality.py",
          "target": "skilgen/hooks/claude_code_hook.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_generation_quality.py",
          "target": "skilgen/hooks/cursor_watcher.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_half_life.py",
          "target": "apps/api/api/services/half_life.py",
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
          "source": "tests/test_improvement_loop.py",
          "target": "apps/api/api/routes/repos.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_incident_parsers.py",
          "target": "skilgen/parsers/incident.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_infra_parsers.py",
          "target": "skilgen/parsers/helm.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_infra_parsers.py",
          "target": "skilgen/parsers/kubernetes.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_infra_parsers.py",
          "target": "skilgen/parsers/terraform.py",
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
          "source": "tests/test_llm_config.py",
          "target": "apps/api/api/services/llm_config.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_memory_capture.py",
          "target": "apps/api/api/services/memory.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_memory_capture.py",
          "target": "packages/db/models/__init__.py",
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
          "source": "tests/test_org_intelligence_api.py",
          "target": "apps/api/api/auth.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_org_intelligence_api.py",
          "target": "apps/api/api/routes/orgs.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_org_intelligence_api.py",
          "target": "packages/db/database.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_org_intelligence_api.py",
          "target": "packages/db/models/__init__.py",
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
          "source": "tests/test_policy_engine.py",
          "target": "apps/api/api/services/policy.py",
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
          "source": "tests/test_process_parsers.py",
          "target": "skilgen/parsers/confluence.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_process_parsers.py",
          "target": "skilgen/parsers/notion.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_process_parsers.py",
          "target": "skilgen/parsers/runbook.py",
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
          "source": "tests/test_red_flags.py",
          "target": "apps/api/api/auth.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_red_flags.py",
          "target": "apps/api/api/routes/orgs.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_red_flags.py",
          "target": "apps/api/api/services/redflags.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_red_flags.py",
          "target": "packages/db/database.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_red_flags.py",
          "target": "packages/db/models/__init__.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_registry.py",
          "target": "apps/api/api/routes/registry.py",
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
          "source": "tests/test_security_parsers.py",
          "target": "skilgen/parsers/sarif.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_security_parsers.py",
          "target": "skilgen/parsers/sbom.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_security_parsers.py",
          "target": "skilgen/parsers/security_policy.py",
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
          "source": "tests/test_skill_sources_api.py",
          "target": "apps/api/api/routes/repos.py",
          "kind": "repo-import",
          "risk_signals": []
        },
        {
          "source": "tests/test_skill_sources_api.py",
          "target": "packages/db/models/skill.py",
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
          "target": "packages/db/models/__init__.py",
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
          "target": "packages/db/models/__init__.py",
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
        "Loosely pinned external dependencies increase drift risk: package:@eslint/js, package:@playwright/test, package:@radix-ui/react-avatar, package:@radix-ui/react-dialog, package:@radix-ui/react-dropdown-menu, package:@radix-ui/react-label."
      ]
    }
  },
  "architecture": {
    "headline": "Evidence-backed architecture blueprint for the codebase",
    "system_summary": "Skilgen identified 3 top-level architecture domains from 90 evidence items and 13 domain graph nodes. Parser backends in use: empty, python-ast, regex. Source comprehension currently tracks 177 symbol-bearing files, 174 call-bearing files, 72 mapped tests, and 6 workspace packages.",
    "domains": [
      {
        "name": "requirements",
        "summary": "Planning and product-intent domain used to keep the skill tree aligned with requirements and changing scope.",
        "confidence": 0.99,
        "responsibilities": [
          "Planning and product-intent domain used to keep the skill tree aligned with requirements and changing scope.",
          "requirements-first planning",
          "skill scaffolding"
        ],
        "evidence_paths": [
          "README.md"
        ],
        "related_domains": [
          "roadmap"
        ],
        "recommended_skill_path": "skills/requirements/SKILL.md"
      },
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
          "requirements",
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
          "requirements"
        ],
        "recommended_skill_path": "skills/roadmap/SKILL.md"
      }
    ],
    "hotspots": [
      "Dominant languages: python, typescript."
    ],
    "recommendations": [
      "Use architecture domains as the parents for the skill tree, and keep sub-skills close to strong evidence files.",
      "Regenerate skills when dominant domain evidence or domain boundaries change materially.",
      "Use high-signal source evidence to define domain boundaries before generating skills.",
      "Prefer domains that are supported by both code evidence and requirements intent."
    ],
    "materialization_plan": [
      {
        "domain": "requirements",
        "parent_skill_path": "skills/requirements/SKILL.md",
        "child_skill_paths": [],
        "cross_links": [
          "skills/roadmap/SKILL.md"
        ],
        "decision": "keep",
        "rationale": "Keep as a first-class boundary because confidence is 0.99, 1 evidence paths cluster around one coherent responsibility set, and the boundary is clearer as a single skill than as shallower splits."
      },
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
          "skills/requirements/SKILL.md",
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
        "cross_links": [
          "skills/requirements/SKILL.md"
        ],
        "decision": "split",
        "rationale": "Split because 4 concrete child skill surfaces emerged from 2 grounded evidence paths. The parent skill can hold shared context while child skills isolate the distinct capability seams around roadmap-phase-0, roadmap-phase-1, roadmap-phase-2."
      }
    ]
  }
}
```
