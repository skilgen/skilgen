import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


class PlanCliTests(unittest.TestCase):
    def test_plan_command_outputs_steps(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            requirements = root / "requirements.md"
            requirements.write_text(
                "# Product Requirements\n\n- Add a backend scan endpoint\n- Add a dashboard UI flow\n",
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
                    str(root),
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
