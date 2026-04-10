from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from skilgen.agents.codebase_signals import analyze_codebase, collect_code_evidence


class CodebaseSignalsTests(unittest.TestCase):
    def test_analyze_codebase_detects_routes_components_and_tests(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "api" / "routes").mkdir(parents=True)
            (root / "api" / "routes" / "users.py").write_text("def handler():\n    return {}\n", encoding="utf-8")
            (root / "services").mkdir(parents=True)
            (root / "services" / "users_service.py").write_text("def run():\n    return True\n", encoding="utf-8")
            (root / "models").mkdir(parents=True)
            (root / "models" / "user_model.py").write_text("class User: pass\n", encoding="utf-8")
            (root / "repository").mkdir(parents=True)
            (root / "repository" / "users_repository.py").write_text("def load():\n    return []\n", encoding="utf-8")
            (root / "jobs").mkdir(parents=True)
            (root / "jobs" / "sync_job.py").write_text("def run():\n    return True\n", encoding="utf-8")
            (root / "auth").mkdir(parents=True)
            (root / "auth" / "session.py").write_text("def current_user():\n    return None\n", encoding="utf-8")
            (root / "src" / "routes").mkdir(parents=True)
            (root / "src" / "routes" / "dashboard.tsx").write_text("export default function Dashboard() { return null; }\n", encoding="utf-8")
            (root / "src" / "components").mkdir(parents=True)
            (root / "src" / "components" / "SkillCard.tsx").write_text("export function SkillCard() { return null; }\n", encoding="utf-8")
            (root / "src" / "state").mkdir(parents=True)
            (root / "src" / "state" / "appStore.ts").write_text("export const appStore = {};\n", encoding="utf-8")
            (root / "src" / "theme").mkdir(parents=True)
            (root / "src" / "theme" / "tokens.ts").write_text("export const tokens = {};\n", encoding="utf-8")
            (root / "tests").mkdir(parents=True)
            (root / "tests" / "users_test.py").write_text("def test_users():\n    assert True\n", encoding="utf-8")

            signals = analyze_codebase(root)

            self.assertIn("api/routes/users.py", signals.backend_routes)
            self.assertIn("src/routes/dashboard.tsx", signals.frontend_routes)
            self.assertIn("src/components/SkillCard.tsx", signals.components)
            self.assertIn("services/users_service.py", signals.services)
            self.assertIn("tests/users_test.py", signals.tests)
            self.assertIn("models/user_model.py", signals.data_models)
            self.assertIn("repository/users_repository.py", signals.persistence_layers)
            self.assertIn("jobs/sync_job.py", signals.background_jobs)
            self.assertIn("auth/session.py", signals.auth_files)
            self.assertIn("src/state/appStore.ts", signals.state_files)
            self.assertIn("src/theme/tokens.ts", signals.design_system_files)
            self.assertEqual(signals.language_inventory["python"], 7)
            self.assertEqual(signals.language_inventory["typescript-react"], 2)
            self.assertEqual(signals.language_inventory["typescript"], 2)

    def test_analyze_codebase_detects_cobol_copybooks_and_language_inventory(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "cobol" / "transactions").mkdir(parents=True)
            (root / "cobol" / "transactions" / "customer_lookup.cbl").write_text(
                "IDENTIFICATION DIVISION.\nPROGRAM-ID. CUSTOMER-LOOKUP.\nPROCEDURE DIVISION.\nDISPLAY 'OK'.\n",
                encoding="utf-8",
            )
            (root / "batch").mkdir(parents=True)
            (root / "batch" / "nightly_job.cob").write_text(
                "IDENTIFICATION DIVISION.\nPROGRAM-ID. NIGHTLY-JOB.\nPROCEDURE DIVISION.\nSTOP RUN.\n",
                encoding="utf-8",
            )
            (root / "copybooks").mkdir(parents=True)
            (root / "copybooks" / "customer_record.cpy").write_text(
                "01 CUSTOMER-RECORD.\n   05 CUSTOMER-ID PIC X(10).\n",
                encoding="utf-8",
            )

            signals = analyze_codebase(root)

            self.assertIn("cobol/transactions/customer_lookup.cbl", signals.backend_routes)
            self.assertIn("cobol/transactions/customer_lookup.cbl", signals.services)
            self.assertIn("batch/nightly_job.cob", signals.background_jobs)
            self.assertIn("copybooks/customer_record.cpy", signals.copybooks)
            self.assertIn("copybooks/customer_record.cpy", signals.data_models)
            self.assertIn("cobol/transactions/customer_lookup.cbl", signals.legacy_programs)
            self.assertEqual(signals.language_inventory["cobol"], 2)
            self.assertEqual(signals.language_inventory["copybook"], 1)

    def test_collect_code_evidence_reads_real_source_snippets(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "cobol").mkdir(parents=True)
            (root / "cobol" / "customer_lookup.cbl").write_text(
                "IDENTIFICATION DIVISION.\nPROGRAM-ID. CUSTOMER-LOOKUP.\nPROCEDURE DIVISION.\nDISPLAY 'OK'.\n",
                encoding="utf-8",
            )

            evidence = collect_code_evidence(root, limit=5)

            self.assertTrue(evidence)
            self.assertEqual(evidence[0]["language"], "cobol")
            self.assertIn("PROGRAM-ID. CUSTOMER-LOOKUP.", evidence[0]["snippet"])


if __name__ == "__main__":
    unittest.main()
