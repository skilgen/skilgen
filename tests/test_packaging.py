from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest


class PackagingTests(unittest.TestCase):
    def test_local_pip_install_exposes_cli(self) -> None:
        project_root = Path(__file__).resolve().parent.parent
        with TemporaryDirectory() as tmp:
            venv_dir = Path(tmp) / "venv"
            subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)

            bin_dir = venv_dir / ("Scripts" if sys.platform == "win32" else "bin")
            python_bin = bin_dir / ("python.exe" if sys.platform == "win32" else "python")
            skilgen_bin = bin_dir / ("skilgen.exe" if sys.platform == "win32" else "skilgen")

            subprocess.run(
                [str(python_bin), "-m", "pip", "install", str(project_root)],
                check=True,
                capture_output=True,
                text=True,
            )

            version = subprocess.run(
                [str(skilgen_bin), "--version"],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn("0.2.0", version.stdout)

            with TemporaryDirectory() as project_tmp:
                init_result = subprocess.run(
                    [str(skilgen_bin), "init", "--project-root", project_tmp],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                self.assertIn("skilgen.yml", init_result.stdout)
                self.assertTrue((Path(project_tmp) / "skilgen.yml").exists())


if __name__ == "__main__":
    unittest.main()
