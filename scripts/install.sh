#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Install the Skillayer local agent helper.

Usage:
  scripts/install.sh [--install-dir DIR] [--bin-dir DIR] [--version VERSION] [--package SPEC] [--dry-run]

Environment:
  SKILLAYER_AGENT_HOME       Install directory. Default: ~/.skillayer/agent-runtime
  SKILLAYER_AGENT_BIN_DIR    Directory for the skillayer-agent shim. Default: ~/.local/bin
  SKILLAYER_AGENT_VERSION    Package version when installing from PyPI. Default: current checkout if available, otherwise latest
  SKILLAYER_AGENT_PACKAGE    Explicit pip package spec or local checkout path.
  PYTHON                     Python executable. Default: python3
USAGE
}

dry_run=0
install_dir="${SKILLAYER_AGENT_HOME:-$HOME/.skillayer/agent-runtime}"
bin_dir="${SKILLAYER_AGENT_BIN_DIR:-$HOME/.local/bin}"
version="${SKILLAYER_AGENT_VERSION:-}"
package_spec="${SKILLAYER_AGENT_PACKAGE:-}"
python_bin="${PYTHON:-python3}"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --install-dir)
      install_dir="$2"
      shift 2
      ;;
    --bin-dir)
      bin_dir="$2"
      shift 2
      ;;
    --version)
      version="$2"
      shift 2
      ;;
    --package)
      package_spec="$2"
      shift 2
      ;;
    --dry-run)
      dry_run=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "error: unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"
venv_dir="$install_dir/venv"
shim_path="$bin_dir/skillayer-agent"

if [ -z "$package_spec" ]; then
  if [ -f "$repo_root/pyproject.toml" ] && [ -d "$repo_root/packages/skillayer_agent" ]; then
    package_spec="$repo_root"
  elif [ -n "$version" ]; then
    package_spec="skilgen==$version"
  else
    package_spec="skilgen"
  fi
fi

run() {
  if [ "$dry_run" -eq 1 ]; then
    printf '+'
    printf ' %q' "$@"
    printf '\n'
  else
    "$@"
  fi
}

write_shim() {
  if [ "$dry_run" -eq 1 ]; then
    printf '+ write %q\n' "$shim_path"
    return
  fi
  cat >"$shim_path" <<SHIM
#!/usr/bin/env bash
exec "$venv_dir/bin/python" -m packages.skillayer_agent.cli "\$@"
SHIM
  chmod 0755 "$shim_path"
}

run mkdir -p "$install_dir" "$bin_dir"
run "$python_bin" -m venv "$venv_dir"
run "$venv_dir/bin/python" -m pip install --upgrade pip
run "$venv_dir/bin/python" -m pip install --upgrade "$package_spec"
write_shim

if [ "$dry_run" -eq 1 ]; then
  echo "Dry run complete. No files changed."
else
  echo "Installed skillayer-agent at $shim_path"
  echo "Run: $shim_path status --dry-run"
fi
