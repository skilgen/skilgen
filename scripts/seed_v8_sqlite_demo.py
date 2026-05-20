from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path


ALEMBIC_HEAD = "20260505_0006"


def _create_schema(cursor: sqlite3.Cursor) -> None:
    cursor.execute("PRAGMA journal_mode=WAL;")

    cursor.execute("CREATE TABLE IF NOT EXISTS alembic_version (version_num TEXT NOT NULL);")
    cursor.execute("DELETE FROM alembic_version;")
    cursor.execute("INSERT INTO alembic_version(version_num) VALUES (?)", (ALEMBIC_HEAD,))

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS orgs (
          id TEXT PRIMARY KEY,
          github_org_id INTEGER NOT NULL,
          login TEXT NOT NULL,
          name TEXT NOT NULL,
          plan TEXT NOT NULL,
          seat_count INTEGER NOT NULL DEFAULT 0,
          stripe_customer_id TEXT,
          stripe_subscription_id TEXT,
          stripe_subscription_status TEXT,
          plan_seat_limit INTEGER NOT NULL DEFAULT 3,
          score_threshold INTEGER NOT NULL DEFAULT 60,
          slack_webhook_url TEXT,
          slack_signing_secret TEXT,
          slack_team_id TEXT,
          slack_standup_enabled BOOLEAN NOT NULL DEFAULT 0,
          slack_standup_hour INTEGER NOT NULL DEFAULT 9,
          digest_email TEXT,
          digest_enabled BOOLEAN NOT NULL DEFAULT 0,
          digest_day INTEGER NOT NULL DEFAULT 1,
          digest_hour INTEGER NOT NULL DEFAULT 8,
          is_suspended BOOLEAN NOT NULL DEFAULT 0,
          suspended_at TEXT,
          suspended_reason TEXT,
          notify_on_pr BOOLEAN NOT NULL DEFAULT 1,
          notify_on_stale BOOLEAN NOT NULL DEFAULT 1,
          notification_settings TEXT,
          settings TEXT,
          siem_webhook_url TEXT,
          siem_webhook_secret TEXT,
          siem_webhook_enabled BOOLEAN NOT NULL DEFAULT 0,
          siem_event_filter TEXT,
          workos_org_id TEXT,
          github_installation_id INTEGER,
          api_key TEXT,
          created_at TEXT,
          updated_at TEXT
        );
        """.strip()
    )
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_orgs_github_org_id ON orgs(github_org_id);")
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_orgs_login ON orgs(login);")
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_orgs_api_key ON orgs(api_key);")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS roles (
          id TEXT PRIMARY KEY,
          org_id TEXT NOT NULL,
          name TEXT NOT NULL,
          description TEXT,
          permissions TEXT NOT NULL DEFAULT '[]',
          created_at TEXT,
          updated_at TEXT,
          FOREIGN KEY(org_id) REFERENCES orgs(id) ON DELETE CASCADE
        );
        """.strip()
    )
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_roles_org_name ON roles(org_id, name);")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_roles_org_id ON roles(org_id);")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS role_bindings (
          id TEXT PRIMARY KEY,
          org_id TEXT NOT NULL,
          role_id TEXT NOT NULL,
          principal_type TEXT NOT NULL,
          principal_id TEXT NOT NULL,
          scope_expression TEXT DEFAULT '{}',
          created_at TEXT,
          updated_at TEXT,
          FOREIGN KEY(org_id) REFERENCES orgs(id) ON DELETE CASCADE,
          FOREIGN KEY(role_id) REFERENCES roles(id) ON DELETE CASCADE
        );
        """.strip()
    )
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_role_bindings_org_principal ON role_bindings(org_id, principal_type, principal_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_role_bindings_role_id ON role_bindings(role_id);")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS digest_configs (
          id TEXT PRIMARY KEY,
          org_id TEXT NOT NULL,
          title TEXT NOT NULL DEFAULT 'Weekly AI Readiness Digest',
          subject TEXT NOT NULL DEFAULT 'Your Weekly AI Readiness Report',
          frequency TEXT NOT NULL DEFAULT 'weekly',
          recipients TEXT NOT NULL DEFAULT '[]',
          widgets TEXT NOT NULL DEFAULT '[]',
          layout TEXT DEFAULT '{}',
          created_at TEXT,
          updated_at TEXT,
          FOREIGN KEY(org_id) REFERENCES orgs(id) ON DELETE CASCADE
        );
        """.strip()
    )
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_digest_configs_org_id ON digest_configs(org_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_digest_configs_org_id ON digest_configs(org_id);")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS repos (
          id TEXT PRIMARY KEY,
          org_id TEXT NOT NULL,
          github_repo_id INTEGER NOT NULL,
          github_installation_id INTEGER,
          full_name TEXT NOT NULL,
          name TEXT NOT NULL,
          default_branch TEXT NOT NULL DEFAULT 'main',
          language TEXT,
          sensitivity_tier TEXT DEFAULT 'internal',
          is_monorepo BOOLEAN NOT NULL DEFAULT 0,
          is_active BOOLEAN NOT NULL DEFAULT 1,
          last_analysed_at TEXT,
          last_debt_analysis_at TEXT,
          created_at TEXT
        );
        """.strip()
    )
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_repos_github_repo_id ON repos(github_repo_id);")
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_repos_full_name ON repos(full_name);")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS analysis_runs (
          id TEXT PRIMARY KEY,
          repo_id TEXT NOT NULL,
          trigger TEXT NOT NULL,
          status TEXT NOT NULL DEFAULT 'queued',
          commit_sha TEXT,
          branch TEXT,
          pr_number INTEGER,
          score_total INTEGER,
          score_groundedness INTEGER,
          score_coverage INTEGER,
          score_freshness INTEGER,
          score_structure INTEGER,
          domain_count INTEGER,
          skill_count INTEGER,
          error_message TEXT,
          started_at TEXT,
          completed_at TEXT,
          created_at TEXT
        );
        """.strip()
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS score_history (
          id TEXT PRIMARY KEY,
          repo_id TEXT NOT NULL,
          run_id TEXT NOT NULL,
          score_total INTEGER NOT NULL,
          score_groundedness INTEGER NOT NULL,
          score_coverage INTEGER NOT NULL,
          score_freshness INTEGER NOT NULL,
          score_structure INTEGER NOT NULL,
          recorded_at TEXT
        );
        """.strip()
    )
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_score_history_repo_recorded_at ON score_history(repo_id, recorded_at);")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS skills (
          id TEXT PRIMARY KEY,
          repo_id TEXT NOT NULL,
          run_id TEXT NOT NULL,
          domain TEXT NOT NULL,
          skill_path TEXT NOT NULL,
          content TEXT,
          content_hash TEXT,
          source_type TEXT,
          skill_category TEXT,
          score_total INTEGER NOT NULL DEFAULT 0,
          score_groundedness INTEGER NOT NULL DEFAULT 0,
          score_coverage INTEGER NOT NULL DEFAULT 0,
          score_freshness INTEGER NOT NULL DEFAULT 0,
          score_structure INTEGER NOT NULL DEFAULT 0,
          is_stale BOOLEAN NOT NULL DEFAULT 0,
          is_enterprise BOOLEAN NOT NULL DEFAULT 0,
          anti_patterns TEXT,
          load_count_30d INTEGER NOT NULL DEFAULT 0,
          last_loaded_at TEXT,
          created_at TEXT,
          updated_at TEXT
        );
        """.strip()
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS skill_usage_events (
          id TEXT PRIMARY KEY,
          org_id TEXT NOT NULL,
          repo_id TEXT NOT NULL,
          skill_id TEXT NOT NULL,
          agent_runtime TEXT NOT NULL,
          session_id TEXT NOT NULL,
          loaded_at TEXT
        );
        """.strip()
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS agent_sessions (
          id TEXT PRIMARY KEY,
          repo_id TEXT NOT NULL,
          org_id TEXT NOT NULL,
          session_id TEXT NOT NULL,
          agent_runtime TEXT NOT NULL,
          task_description TEXT,
          engineer_login TEXT,
          duration_minutes INTEGER,
          files_touched TEXT NOT NULL DEFAULT '[]',
          skill_paths_loaded TEXT NOT NULL DEFAULT '[]',
          transcript_summary TEXT,
          raw_message_count INTEGER,
          extraction_status TEXT NOT NULL DEFAULT 'pending',
          discoveries_found INTEGER NOT NULL DEFAULT 0,
          session_start TEXT,
          session_end TEXT,
          skills_loaded TEXT NOT NULL DEFAULT '[]',
          code_produced TEXT,
          produced_artifacts TEXT NOT NULL DEFAULT '[]',
          produced_file_hashes TEXT NOT NULL DEFAULT '{}',
          closed_at TEXT,
          inactivity_timeout_minutes INTEGER NOT NULL DEFAULT 30,
          last_artifact_at TEXT,
          outcome TEXT,
          notes TEXT,
          created_at TEXT
        );
        """.strip()
    )
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_agent_sessions_repo_session ON agent_sessions(repo_id, session_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_agent_sessions_org_created_at ON agent_sessions(org_id, created_at);")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_agent_sessions_repo_created_at ON agent_sessions(repo_id, created_at);")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_events (
          id TEXT PRIMARY KEY,
          org_id TEXT NOT NULL,
          event_type TEXT NOT NULL,
          actor_login TEXT,
          actor_ip TEXT,
          repo_id TEXT,
          repo_name TEXT,
          skill_id TEXT,
          skill_domain TEXT,
          resource_type TEXT,
          resource_id TEXT,
          action TEXT NOT NULL,
          summary TEXT NOT NULL,
          metadata TEXT NOT NULL DEFAULT '{}',
          severity TEXT NOT NULL DEFAULT 'info',
          created_at TEXT
        );
        """.strip()
    )
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_audit_events_org_created_at ON audit_events(org_id, created_at);")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_audit_events_org_event_type_created_at ON audit_events(org_id, event_type, created_at);")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_audit_events_org_repo_created_at ON audit_events(org_id, repo_id, created_at);")


def seed(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        _create_schema(cursor)

        org_id = "org_skilgen"
        repo_id = "repo_skilgen"
        run_id = "run_skilgen_1"
        skill_id = "skill_activity"
        session_db_id = "sess_skilgen_codex_1"
        api_key = "sk-local-demo"
        now = "2026-05-12T02:30:00"

        cursor.execute(
            "INSERT INTO orgs (id, github_org_id, login, name, plan, settings, api_key, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?)",
            (org_id, 1, "Skilgen", "Skilgen", "dev", json.dumps({"feature_flags": {"IA_V8": True}}), api_key, now, now),
        )
        cursor.execute(
            "INSERT INTO roles (id, org_id, name, description, permissions, created_at, updated_at) VALUES (?,?,?,?,?,?,?)",
            (
                "role_bootstrap_admin",
                org_id,
                "Bootstrap admin",
                "Local bootstrap role for demo UX + screenshots.",
                json.dumps(["settings.*", "audit.*", "insights.*", "policy.*", "skills.*"]),
                now,
                now,
            ),
        )
        cursor.execute(
            "INSERT INTO role_bindings (id, org_id, role_id, principal_type, principal_id, scope_expression, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?)",
            (
                "binding_bootstrap_admin",
                org_id,
                "role_bootstrap_admin",
                "user",
                "bootstrap@skillayer.com",
                json.dumps({}),
                now,
                now,
            ),
        )
        cursor.execute(
            "INSERT INTO digest_configs (id, org_id, title, subject, frequency, recipients, widgets, layout, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (
                "digest_cfg_1",
                org_id,
                "Weekly AI Readiness Digest",
                "Your Weekly AI Readiness Report",
                "weekly",
                json.dumps(["platform@example.com"]),
                json.dumps(["memory_score", "agent_loads", "active_repos", "top_skill", "skill_gaps", "roi_multiplier"]),
                json.dumps({"columns": 2}),
                now,
                now,
            ),
        )
        cursor.execute(
            "INSERT INTO repos (id, org_id, github_repo_id, full_name, name, default_branch, language, sensitivity_tier, is_active, created_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (repo_id, org_id, 1, "ravichanduummadisetti/skilgen", "skilgen", "main", "python", "internal", 1, now),
        )
        cursor.execute(
            """
            INSERT INTO analysis_runs (
              id, repo_id, trigger, status, commit_sha, branch, pr_number,
              score_total, score_groundedness, score_coverage, score_freshness, score_structure,
              domain_count, skill_count, started_at, completed_at, created_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """.strip(),
            (run_id, repo_id, "seed", "complete", "deadbeef", "main", None, 82, 20, 20, 21, 21, 1, 1, now, now, now),
        )
        cursor.execute(
            """
            INSERT INTO score_history (
              id, repo_id, run_id, score_total, score_groundedness, score_coverage, score_freshness, score_structure, recorded_at
            ) VALUES (?,?,?,?,?,?,?,?,?)
            """.strip(),
            ("hist_1", repo_id, run_id, 82, 20, 20, 21, 21, now),
        )
        cursor.execute(
            "INSERT INTO skills (id, repo_id, run_id, domain, skill_path, content, content_hash, source_type, skill_category, score_total, score_groundedness, score_coverage, score_freshness, score_structure, is_stale, is_enterprise, anti_patterns, load_count_30d, last_loaded_at, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                skill_id,
                repo_id,
                run_id,
                "activity",
                "skills/platform/runtime/SKILL.md",
                None,
                "hash",
                "code",
                "internal_tools",
                82,
                20,
                20,
                21,
                21,
                0,
                0,
                json.dumps([]),
                3,
                now,
                now,
                now,
            ),
        )
        cursor.execute(
            "INSERT INTO skill_usage_events (id, org_id, repo_id, skill_id, agent_runtime, session_id, loaded_at) VALUES (?,?,?,?,?,?,?)",
            ("evt_load_1", org_id, repo_id, skill_id, "codex", "sess_ext_1", now),
        )
        cursor.execute(
            "INSERT INTO agent_sessions (id, repo_id, org_id, session_id, agent_runtime, task_description, engineer_login, duration_minutes, files_touched, skill_paths_loaded, transcript_summary, raw_message_count, extraction_status, discoveries_found, session_start, session_end, skills_loaded, code_produced, produced_artifacts, produced_file_hashes, closed_at, inactivity_timeout_minutes, last_artifact_at, outcome, notes, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                session_db_id,
                repo_id,
                org_id,
                "sess_ext_1",
                "codex",
                "PAY-4421 Investigate activity feed",
                "ravi",
                3,
                json.dumps(
                    [
                        "apps/dashboard/app/(v8)/activity/heatmap/page.tsx",
                        "apps/api/api/v8/activity/router.py",
                    ]
                ),
                json.dumps([]),
                None,
                12,
                "done",
                2,
                now,
                None,
                json.dumps([]),
                None,
                json.dumps(
                    [
                        {
                            "tool": "Write",
                            "file_path": "apps/dashboard/app/(v8)/activity/heatmap/page.tsx",
                            "diff": "+metric grid",
                            "after_hash": "hash1",
                            "ts": now,
                        },
                        {
                            "tool": "Write",
                            "file_path": "apps/api/api/v8/activity/router.py",
                            "diff": "+session fallback",
                            "after_hash": "hash2",
                            "ts": now,
                        },
                    ]
                ),
                json.dumps({"apps/api/api/v8/activity/router.py": "hash2"}),
                None,
                30,
                now,
                "success",
                None,
                now,
            ),
        )

        metadata = {
            "provider": "openai",
            "model": "gpt-5.2",
            "intelligence_tier": "standard",
            "access_scope": "repo",
            "policy_decision": "allowed",
            "tokens_input": 1200,
            "tokens_output": 400,
            "cost_usd": 0.23,
            "tool_calls": 5,
            "mcp_tools": ["web.run"],
            "file_targets": ["apps/api/api/v8/activity/router.py"],
            "source_record_types": ["codex_live"],
            "content_retention": "metadata-only",
        }
        cursor.execute(
            "INSERT INTO audit_events (id, org_id, event_type, actor_login, actor_ip, repo_id, repo_name, skill_id, skill_domain, resource_type, resource_id, action, summary, metadata, severity, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                "audit_1",
                org_id,
                "agent.compliance",
                "ravi",
                None,
                repo_id,
                "ravichanduummadisetti/skilgen",
                None,
                None,
                "agent_session",
                session_db_id,
                "tool_call",
                "Codex ran tool calls",
                json.dumps(metadata),
                "info",
                now,
            ),
        )

        high_tier_metadata = {
            "provider": "openai",
            "model": "gpt-5.2-high",
            "intelligence_tier": "high",
            "task_type": "documentation",
            "access_scope": "repo",
            "policy_decision": "require_approval",
            "approval_status": "pending",
            "tokens_input": 52000,
            "tokens_output": 18000,
            "cost_usd": 12.45,
            "latency_ms": 3400,
            "pr_number": 128,
            "pr_title": "v8 Activity intelligence usage",
            "branch": "v8/02-activity",
            "session_id": "codex-run-pr-128",
            "mcp_tools": ["browser-use"],
            "file_targets": ["apps/dashboard/app/(v8)/insights/_components/insights-shell.tsx"],
            "source_record_types": ["codex_live"],
            "content_retention": "metadata-only",
        }
        cursor.execute(
            "INSERT INTO audit_events (id, org_id, event_type, actor_login, actor_ip, repo_id, repo_name, skill_id, skill_domain, resource_type, resource_id, action, summary, metadata, severity, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                "audit_2",
                org_id,
                "agent.compliance",
                "ravi",
                None,
                repo_id,
                "ravichanduummadisetti/skilgen",
                None,
                None,
                "pull_request",
                "pr_128",
                "commit",
                "High-tier tokens used for documentation + PR push",
                json.dumps(high_tier_metadata),
                "warning",
                "2026-05-12T03:10:00",
            ),
        )

        conn.commit()
    finally:
        conn.close()


def main() -> None:
    default_path = Path(os.getenv("SKILLAYER_DEMO_DB", "/private/tmp/skillayer_v8_seed.db"))
    seed(default_path)
    db_url_path = default_path.as_posix().lstrip("/")
    print(f"Seeded demo DB at: {default_path}")
    print("\nRun API:")
    print(
        "  "
        f"DATABASE_URL=sqlite:////{db_url_path} "
        "DEPLOYMENT_MODE=bootstrap IA_V8_DEFAULT=1 "
        "uvicorn apps.api.api.index:app --port 8000 --reload"
    )
    print("\nRun dashboard:")
    print(
        "  IA_V8_DEFAULT=1 NEXT_PUBLIC_API_URL=http://127.0.0.1:8000 "
        "API_URL=http://127.0.0.1:8000 WATCHPACK_POLLING=true "
        "npm --workspace apps/dashboard run dev -- --port 4325"
    )


if __name__ == "__main__":
    main()
