import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class PlanCliTests(unittest.TestCase):
    def test_plan_command_outputs_steps(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            requirements = Path(tmpdir) / "requirements.md"
            requirements.write_text(
                "# Requirements\n\n"
                "- Add endpoint-aware feature extraction.\n"
                "- Add dashboard UI flow.\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "skilgen.cli.main",
                    "plan",
                    "--requirements",
                    str(requirements),
                    "--project-root",
                    tmpdir,
                ],
                text=True,
                capture_output=True,
                check=True,
            )
        payload = json.loads(result.stdout)
        self.assertIn("model", payload)
        self.assertTrue(payload["steps"])


if __name__ == "__main__":
    unittest.main()
