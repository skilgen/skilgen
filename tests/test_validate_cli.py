import json
import subprocess
import sys
import unittest


class ValidateCliTests(unittest.TestCase):
    def test_validate_command_outputs_validity(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "skilgen.cli.main", "validate", "--project-root", "."],
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(result.stdout)
        self.assertIn("valid", payload)
        self.assertIn("completeness_score", payload)
        self.assertIn("recommendations", payload)


if __name__ == "__main__":
    unittest.main()
