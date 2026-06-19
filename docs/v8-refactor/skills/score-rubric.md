# Skilgen Score Rubric

Source: existing implementation in `apps/api/api/routes/repos.py` (`_compute_skill_score`). PR-5 moves and documents the rubric only; it does not change the algorithm.

## Inputs

- Word count from the skill body.
- Heading presence and heading count for Markdown `#`, `##`, and `###`.
- Code-block presence using fenced backticks.
- File-reference count for backticked paths ending in `.py`, `.ts`, `.tsx`, `.js`, `.go`, `.rs`, `.java`, `.cs`, `.rb`, or `.php`.
- Pattern/example/how-to signal from text matching `pattern`, `example`, `usage`, or `how.to`.
- Version/freshness signal from text matching `v<major>.<minor>`, `version`, `last.verified`, or `updated`.
- Bullet count from Markdown `-` or `*` list items.

## Subscores

Each subscore is capped at 25 points.

| Subscore | Existing calculation |
| --- | --- |
| Groundedness | `min(25, file_ref_count * 4 + (8 if code blocks exist else 0) + (5 if pattern/example/how-to signal exists else 0))` |
| Coverage | `min(25, word_count // 20 + heading_count * 3 + bullet_count // 2)` |
| Freshness | `min(25, 10 + (15 if version/freshness signal exists else 0))` |
| Structure | `min(25, (10 if headings exist else 0) + heading_count * 3 + (5 if bullet_count >= 3 else 0))` |

## Total

`total = groundedness + coverage + freshness + structure`

The v8 Skills Score tab surfaces these four subscores as the existing Skilgen Score. Algorithm changes, threshold changes, and grammar changes are out of scope for PR-5.
