from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from apps.api.api.v8.policy.dsl.parser import parse_policy_yaml


STARTER_PACK_DIR = Path(__file__).with_name("starter_packs")


@lru_cache(maxsize=1)
def load_starter_packs() -> list[dict[str, object]]:
    packs: list[dict[str, object]] = []
    for path in sorted(STARTER_PACK_DIR.glob("*.yaml")):
        source = path.read_text(encoding="utf-8")
        rule = parse_policy_yaml(source, source_pack=path.stem)
        packs.append(
            {
                "pack_id": path.stem,
                "id": rule.id,
                "title": rule.title,
                "decision": rule.decision,
                "compliance_tags": list(rule.compliance_tags),
                "yaml": source,
            }
        )
    return packs

