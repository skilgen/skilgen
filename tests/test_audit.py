from __future__ import annotations

import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from skilgen.core.audit import append_audit_event


class AuditTests(unittest.TestCase):
    def test_append_audit_event_uses_file_locking_for_local_and_central_logs(self) -> None:
        with TemporaryDirectory() as tmp, TemporaryDirectory() as audit_tmp:
            root = Path(tmp)
            audit_root = Path(audit_tmp)
            with patch.dict(os.environ, {"SKILGEN_AUDIT_LOG_ROOT": str(audit_root)}, clear=False), patch(
                "skilgen.core.audit.fcntl.flock"
            ) as mock_flock:
                append_audit_event(root, action="deliver", outcome="success", source="test")
            self.assertTrue((root / ".skilgen" / "audit" / "events.jsonl").exists())
            self.assertTrue((audit_root / "audit" / "events.jsonl").exists())
            self.assertGreaterEqual(mock_flock.call_count, 4)


if __name__ == "__main__":
    unittest.main()
