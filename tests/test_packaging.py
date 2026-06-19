from pathlib import Path
from tempfile import mkdtemp
import os
import shutil
import subprocess
import sys
import time
import unittest


class PackagingTests(unittest.TestCase):
    def _cleanup_tree(self, path: Path) -> None:
        for _ in range(5):
            try:
                shutil.rmtree(path)
                return
            except FileNotFoundError:
                return
            except OSError:
                time.sleep(0.2)
        shutil.rmtree(path)

    def test_local_pip_install_exposes_cli(self) -> None:
        project_root = Path(__file__).resolve().parent.parent
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"

        tmp = Path(mkdtemp())
        try:
            venv_dir = tmp / "venv"
            subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)

            bin_dir = venv_dir / ("Scripts" if sys.platform == "win32" else "bin")
            python_bin = bin_dir / ("python.exe" if sys.platform == "win32" else "python")
            skilgen_bin = bin_dir / ("skilgen.exe" if sys.platform == "win32" else "skilgen")

            subprocess.run(
                [str(python_bin), "-m", "pip", "install", "--no-compile", str(project_root)],
                check=True,
                capture_output=True,
                text=True,
                env=env,
            )

            version = subprocess.run(
                [str(skilgen_bin), "--version"],
                check=True,
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertIn("0.6.0", version.stdout)

            project_tmp = Path(mkdtemp())
            try:
                init_result = subprocess.run(
                    [str(skilgen_bin), "init", "--project-root", str(project_tmp)],
                    check=True,
                    capture_output=True,
                    text=True,
                    env=env,
                )
                self.assertIn("skilgen.yml", init_result.stdout)
                self.assertTrue((project_tmp / "skilgen.yml").exists())
            finally:
                self._cleanup_tree(project_tmp)
        finally:
            self._cleanup_tree(tmp)


if __name__ == "__main__":
    unittest.main()
