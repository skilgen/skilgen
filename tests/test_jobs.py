from contextlib import closing
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
import time
import unittest

from skilgen.api import jobs as jobs_module
from skilgen.api.jobs import get_job, request_cancel, submit_job
from skilgen.api.service import create_deliver_job, job_status_payload, jobs_payload, resume_job_payload


class JobPersistenceTests(unittest.TestCase):
    def test_deliver_job_persists_status_to_project_root(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            requirements = root / "requirements.md"
            requirements.write_text("Backend endpoint\nFrontend route\n", encoding="utf-8")

            job = create_deliver_job(requirements, root)
            self.assertIn("progress", job)
            self.assertIn("created_at", job)

            current = job
            for _ in range(40):
                current = job_status_payload(job["job_id"], root)
                if current["status"] in {"completed", "failed"}:
                    break
                time.sleep(0.05)

            self.assertEqual(current["status"], "completed")
            self.assertEqual(current["progress"], 100)
            job_db = root / ".skilgen" / "jobs" / "jobs.sqlite"
            self.assertTrue(job_db.exists())

            listed = jobs_payload(root)
            self.assertTrue(listed["jobs"])
            self.assertEqual(listed["jobs"][0]["payload"]["project_root"], str(root.resolve()))
            self.assertEqual(current["api_version"], "1.0")

    def test_job_can_be_cancelled_and_deliver_job_can_be_resumed(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            requirements = root / "requirements.md"
            requirements.write_text("Backend endpoint\n", encoding="utf-8")
            cancelled = submit_job(
                "deliver",
                {"project_root": str(root.resolve()), "requirements": str(requirements.resolve())},
                lambda report: (time.sleep(0.2), report(50, "halfway"), {"ok": True})[-1],
            )
            request_cancel(cancelled.job_id, root)

            current = {}
            for _ in range(20):
                job = get_job(cancelled.job_id, root)
                current = {} if job is None else {"status": job.status, "progress": job.progress}
                if current.get("status") in {"cancelled", "completed", "failed"}:
                    break
                time.sleep(0.05)

            self.assertEqual(current["status"], "cancelled")

            resumed = resume_job_payload(cancelled.job_id, root)
            self.assertEqual(resumed["api_version"], "1.0")
            self.assertEqual(resumed["job_type"], "deliver")
            resumed_id = resumed["job_id"]
            current_resumed = resumed
            for _ in range(40):
                current_resumed = job_status_payload(resumed_id, root)
                if current_resumed["status"] in {"completed", "failed", "cancelled"}:
                    break
                time.sleep(0.05)
            self.assertIn(current_resumed["status"], {"completed", "failed"})

    def test_running_job_recovers_as_interrupted_after_runtime_reset(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            requirements = root / "requirements.md"
            requirements.write_text("Backend endpoint\n", encoding="utf-8")
            job = create_deliver_job(requirements, root)
            job_db = root / ".skilgen" / "jobs" / "jobs.sqlite"

            deadline = time.monotonic() + 5.0
            current = job
            while time.monotonic() < deadline:
                current = job_status_payload(job["job_id"], root)
                if current["status"] in {"completed", "failed"}:
                    break
                time.sleep(0.05)
            self.assertIn(current["status"], {"completed", "failed"})

            with closing(sqlite3.connect(job_db)) as connection, connection:
                connection.execute(
                    "UPDATE jobs SET status = ?, message = ?, finished_at = NULL, error = NULL WHERE job_id = ?",
                    ("running", "running", job["job_id"]),
                )

            jobs_module._runtime_jobs.clear()
            jobs_module._recovered_roots.clear()

            recovered = get_job(job["job_id"], root)
            self.assertIsNotNone(recovered)
            assert recovered is not None
            self.assertEqual(recovered.status, "interrupted")
            self.assertEqual(recovered.message, "interrupted")
            self.assertEqual(recovered.error, "job interrupted after restart")

            resumed = resume_job_payload(job["job_id"], root)
            self.assertEqual(resumed["api_version"], "1.0")
            self.assertEqual(resumed["job_type"], "deliver")
            resumed_id = resumed["job_id"]

            deadline = time.monotonic() + 5.0
            while time.monotonic() < deadline:
                current = job_status_payload(resumed_id, root)
                if current["status"] in {"completed", "failed", "cancelled"}:
                    break
                time.sleep(0.05)


if __name__ == "__main__":
    unittest.main()
