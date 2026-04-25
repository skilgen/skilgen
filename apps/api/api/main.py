from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

try:
    from apps.api.api.index import app
except ModuleNotFoundError:  # Allows `cd apps/api && python -c "from api.main import app"`.
    from api.index import app

__all__ = ["app"]
