.PHONY: verify-enterprise

verify-enterprise:
	npm --workspace apps/dashboard run type-check
	npm --workspace apps/dashboard run build
	python -m compileall apps/api/api packages/skillayer_agent scripts
	python -m pytest apps/api/tests/test_device_flow.py apps/api/tests/test_connect_status.py apps/api/tests/test_v8_settings_rbac.py -q
	python -m unittest tests.test_openai_compliance_sync tests.test_anthropic_compliance_sync tests.test_agent_runs_smoke tests.test_skillayer_agent_cli tests.test_codex_cli_runtime tests.test_cursor_importer tests.test_windsurf_importer tests.test_import_codex_sessions -v
	python scripts/import_codex_sessions.py --providers codex,claude --dry-run --project-root .
	python -m packages.skillayer_agent.cli status --providers codex,claude --project-root . --dry-run --json
