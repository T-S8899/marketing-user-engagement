from __future__ import annotations

import hashlib
import json
from typing import Any

from src.scrape.platforms.base import build_actor_input


def build_input(target: dict[str, Any], actor_config: dict[str, Any], defaults: dict[str, Any]) -> dict[str, Any]:
    return build_actor_input(target, actor_config, defaults)


def dedupe_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for record in records:
        key = record_key(record)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(record)
    return deduped


def record_key(record: dict[str, Any]) -> str:
    for key in ("id", "tweetId", "tweet_id", "url", "text"):
        value = str(record.get(key, "")).strip()
        if value:
            return f"{key}:{value}"
    payload = json.dumps(record, ensure_ascii=True, sort_keys=True)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()
