from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from skilgen.core.rate_limit_store import consume_rate_limit


class RateLimitStoreTests(unittest.TestCase):
    def test_consume_rate_limit_shares_counts_in_sqlite_window(self) -> None:
        with TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "rate-limit.sqlite"
            allowed, retry_after = consume_rate_limit("bucket-a", max_count=1, window_seconds=60, now=100.0, db_path=db_path)
            self.assertTrue(allowed)
            self.assertEqual(retry_after, 0)

            allowed, retry_after = consume_rate_limit("bucket-a", max_count=1, window_seconds=60, now=101.0, db_path=db_path)
            self.assertFalse(allowed)
            self.assertGreaterEqual(retry_after, 1)

            allowed, retry_after = consume_rate_limit("bucket-a", max_count=1, window_seconds=60, now=161.0, db_path=db_path)
            self.assertTrue(allowed)
            self.assertEqual(retry_after, 0)


if __name__ == "__main__":
    unittest.main()
