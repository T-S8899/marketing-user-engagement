from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class ConfigError(RuntimeError):
    """Raised when required local configuration is missing or invalid."""


ACTOR_ID_KEYS_BY_PLATFORM = {
    "tiktok": ("actor_id", "comments_actor", "profile_actor"),
    "instagram": ("actor_id", "comments_actor", "posts_actor"),
    "x": ("actor_id", "main_actor"),
    "app_store": ("actor_id", "actor"),
}

FALLBACK_ACTOR_ID_KEYS = ("fallback_actor_id", "fallback_actor", "fallback_replies_actor")


def load_dotenv(path: Path | None = None) -> dict[str, str]:
    env_path = path or PROJECT_ROOT / ".env"
    values: dict[str, str] = {}
    if not env_path.exists():
        return values

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        values[key] = value
        os.environ.setdefault(key, value)
    return values


def require_env(name: str) -> str:
    load_dotenv()
    value = os.environ.get(name, "").strip()
    if not value:
        raise ConfigError(f"Missing required environment variable {name}. Add it to .env.")
    return value


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ConfigError(f"Missing config file: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ConfigError(f"Config file must contain a YAML mapping: {path}")
    return data


def load_brands_config() -> dict[str, Any]:
    return load_yaml(PROJECT_ROOT / "config" / "brands.yaml")


def load_apify_actors_config() -> dict[str, Any]:
    return load_yaml(PROJECT_ROOT / "config" / "apify_actors.yaml")


def get_platform_targets(brands_config: dict[str, Any], platform: str) -> list[dict[str, Any]]:
    targets = brands_config.get("platform_targets", {}).get(platform, [])
    if not targets:
        raise ConfigError(f"No platform targets configured for {platform} in config/brands.yaml.")
    if not isinstance(targets, list):
        raise ConfigError(f"platform_targets.{platform} must be a list in config/brands.yaml.")
    return [target for target in targets if isinstance(target, dict)]


def get_actor_config(actors_config: dict[str, Any], platform: str) -> dict[str, Any]:
    actor_config = _platform_actor_mapping(actors_config, platform)
    if not isinstance(actor_config, dict):
        raise ConfigError(f"{platform} actor config must be a mapping in config/apify_actors.yaml.")

    actor_config = dict(actor_config)
    actor_id = _first_actor_id(actor_config, ACTOR_ID_KEYS_BY_PLATFORM.get(platform, ("actor_id",)))
    if not actor_id:
        expected = ", ".join(ACTOR_ID_KEYS_BY_PLATFORM.get(platform, ("actor_id",)))
        raise ConfigError(f"Missing actor ID for {platform} in config/apify_actors.yaml. Expected one of: {expected}.")

    actor_config["actor_id"] = actor_id
    fallback_actor_id = _first_actor_id(actor_config, FALLBACK_ACTOR_ID_KEYS)
    if fallback_actor_id:
        actor_config["fallback_actor_id"] = fallback_actor_id
    if isinstance(actor_config.get("default_input"), dict) and "input" not in actor_config:
        actor_config["input"] = actor_config["default_input"]
    return actor_config


def get_actor_id(actor_config: dict[str, Any], key: str = "actor_id") -> str:
    actor_id = str(actor_config.get(key, "")).strip()
    if not actor_id:
        raise ConfigError(f"Missing {key} in Apify actor config.")
    return actor_id


def _platform_actor_mapping(actors_config: dict[str, Any], platform: str) -> dict[str, Any]:
    nested = actors_config.get("actors", {})
    if isinstance(nested, dict) and platform in nested:
        return nested.get(platform, {})
    return actors_config.get(platform, {})


def _first_actor_id(actor_config: dict[str, Any], keys: tuple[str, ...]) -> str:
    for key in keys:
        value = str(actor_config.get(key, "")).strip()
        if value:
            return value
    return ""
