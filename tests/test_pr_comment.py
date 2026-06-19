from __future__ import annotations

import unittest

from apps.api.api.pr_comment import _delta_cell, build_comment


def _score(total: int) -> dict[str, int]:
    """Build a complete score dictionary for comment tests."""
    return {
        "total": total,
        "groundedness": 18,
        "coverage": 19,
        "freshness": 21,
        "structure": 16,
    }


class PrCommentTests(unittest.TestCase):
    def test_build_comment_with_no_base_score(self) -> None:
        """Comment omits base delta and uses neutral per-dimension deltas."""
        comment = build_comment(_score(74), None, "1234567890abcdef")

        self.assertIn("## 🟡 Skilgen Score: 74/100", comment)
        self.assertNotIn("vs base", comment)
        self.assertIn("**Good** — AI agent readiness for this branch", comment)
        self.assertIn("| Groundedness | 18/25 | — |", comment)
        self.assertIn("| Coverage | 19/25 | — |", comment)
        self.assertIn("Run ID: `12345678`", comment)

    def test_build_comment_includes_real_domain_badges(self) -> None:
        """Comment includes a compact summary of analysed skill domains."""
        comment = build_comment(
            _score(74),
            None,
            "run-domains",
            domains=["backend/api", "frontend", "backend", "roadmap", "auth", "billing", "data"],
        )

        self.assertIn("**6 domains analysed:**", comment)
        self.assertIn("`auth` `backend` `billing` `data` `frontend` `roadmap`", comment)
        self.assertNotIn("placeholder", comment.lower())

    def test_build_comment_with_positive_delta(self) -> None:
        """Comment includes positive total and dimension deltas."""
        comment = build_comment(
            _score(74),
            {
                "total": 70,
                "groundedness": 15,
                "coverage": 19,
                "freshness": 20,
                "structure": 18,
            },
            "run-positive",
        )

        self.assertIn("Skilgen Score: 74/100 (+4 vs base)", comment)
        self.assertIn("| Groundedness | 18/25 | `+3` |", comment)
        self.assertIn("| Freshness | 21/25 | `+1` |", comment)
        self.assertIn("| Coverage | 19/25 | — |", comment)

    def test_build_comment_with_negative_delta(self) -> None:
        """Comment includes negative total and dimension deltas."""
        comment = build_comment(
            _score(47),
            {
                "total": 52,
                "groundedness": 20,
                "coverage": 17,
                "freshness": 23,
                "structure": 16,
            },
            "run-negative",
        )

        self.assertIn("Skilgen Score: 47/100 (-5 vs base)", comment)
        self.assertIn("| Groundedness | 18/25 | `-2` |", comment)
        self.assertIn("| Freshness | 21/25 | `-2` |", comment)
        self.assertIn("| Structure | 16/25 | — |", comment)

    def test_emoji_and_label_thresholds(self) -> None:
        """Comment chooses the expected emoji and label at score thresholds."""
        cases = [
            (85, "## 🟢 Skilgen Score: 85/100\n\n**Excellent**"),
            (70, "## 🟡 Skilgen Score: 70/100\n\n**Good**"),
            (50, "## 🟠 Skilgen Score: 50/100\n\n**Needs work**"),
            (49, "## 🔴 Skilgen Score: 49/100\n\n**Poor**"),
        ]
        for total, expected in cases:
            with self.subTest(total=total):
                self.assertIn(
                    expected,
                    build_comment(_score(total), None, "run-threshold"),
                )

    def test_delta_cell_formatting(self) -> None:
        """Delta cells use backticks for changes and an em dash for no change."""
        base = {"groundedness": 15, "coverage": 20, "freshness": 21}

        self.assertEqual(_delta_cell(18, base, "groundedness"), "`+3`")
        self.assertEqual(_delta_cell(19, base, "coverage"), "`-1`")
        self.assertEqual(_delta_cell(21, base, "freshness"), "—")
        self.assertEqual(_delta_cell(21, None, "freshness"), "—")


if __name__ == "__main__":
    unittest.main()
