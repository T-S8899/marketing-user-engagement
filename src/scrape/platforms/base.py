from __future__ import annotations

from copy import deepcopy
from typing import Any


def build_actor_input(target: dict[str, Any], actor_config: dict[str, Any], defaults: dict[str, Any]) -> dict[str, Any]:
    actor_input = deepcopy(defaults.get("input", {})) if isinstance(defaults.get("input", {}), dict) else {}
    actor_input.update(deepcopy(actor_config.get("input", {})) if isinstance(actor_config.get("input", {}), dict) else {})
    actor_input.update(deepcopy(target.get("input", {})) if isinstance(target.get("input", {}), dict) else {})

    source_value = _source_account(target)
    if source_value and "source" not in actor_input:
        actor_input["source"] = source_value
    return actor_input


def brand_or_competitor(target: dict[str, Any]) -> str:
    return str(target.get("brand") or target.get("name") or target.get("role") or "").strip()


def source_account(target: dict[str, Any]) -> str:
    return _source_account(target)


def _source_account(target: dict[str, Any]) -> str:
    for key in ("account", "username", "handle", "url", "app_id", "appId", "source"):
        value = str(target.get(key, "")).strip()
        if value:
            return value
    return ""
