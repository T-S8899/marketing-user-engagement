from __future__ import annotations

from typing import Any

from src.scrape.platforms.base import build_actor_input


def build_input(target: dict[str, Any], actor_config: dict[str, Any], defaults: dict[str, Any]) -> dict[str, Any]:
    return build_actor_input(target, actor_config, defaults)
