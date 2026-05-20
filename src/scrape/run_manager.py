from __future__ import annotations

import hashlib
import importlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from src.scrape.apify_client import ApifyClient, ApifyClientError, ApifyRun
from src.scrape.platforms.base import brand_or_competitor, source_account
from src.utils.config import PROJECT_ROOT, ConfigError, get_actor_config, get_actor_id, get_platform_targets
from src.utils.logging import append_raw_record_rows, append_scrape_run, write_json


SUPPORTED_PLATFORMS = {"tiktok", "instagram", "x", "app_store"}


@dataclass(frozen=True)
class ScrapeResult:
    run_id: str
    platform: str
    status: str
    records_count: int
    raw_path: Path
    metadata_path: Path


class RunManager:
    def __init__(
        self,
        client: ApifyClient,
        brands_config: dict[str, Any],
        actors_config: dict[str, Any],
        project_root: Path = PROJECT_ROOT,
    ) -> None:
        self.client = client
        self.brands_config = brands_config
        self.actors_config = actors_config
        self.project_root = project_root

    def run_platform(self, platform: str) -> list[ScrapeResult]:
        platform = platform.lower()
        if platform not in SUPPORTED_PLATFORMS:
            raise ConfigError(f"Unsupported platform {platform}. Expected one of {sorted(SUPPORTED_PLATFORMS)}.")
        targets = get_platform_targets(self.brands_config, platform)
        return [self.run_target(platform, target) for target in targets]

    def run_target(self, platform: str, target: dict[str, Any]) -> ScrapeResult:
        run_id = self._new_run_id(platform)
        actor_config = get_actor_config(self.actors_config, platform)
        defaults = self.actors_config.get("defaults", {})
        platform_module = importlib.import_module(f"src.scrape.platforms.{platform}")
        actor_input = platform_module.build_input(target, actor_config, defaults)
        actor_ids = [get_actor_id(actor_config)]
        if platform == "x":
            fallback_id = str(actor_config.get("fallback_actor_id", "")).strip()
            if fallback_id:
                actor_ids.append(fallback_id)

        records: list[dict[str, Any]] = []
        actor_runs: list[dict[str, Any]] = []
        status = "SUCCEEDED"
        error_message = ""

        try:
            for index, actor_id in enumerate(actor_ids):
                if platform == "x" and index == 1 and records:
                    break
                actor_run, dataset_records = self._run_actor(actor_id, actor_input)
                actor_runs.append(
                    {
                        "actor_id": actor_id,
                        "apify_run_id": actor_run.id,
                        "dataset_id": actor_run.dataset_id,
                        "status": actor_run.status,
                        "records_count": len(dataset_records),
                    }
                )
                records.extend(dataset_records)
            if platform == "x":
                records = platform_module.dedupe_records(records)
        except Exception as exc:
            status = "FAILED"
            error_message = str(exc)

        raw_path = self.project_root / "data" / "raw" / platform / f"{run_id}.json"
        metadata_path = self.project_root / "data" / "raw" / "runs" / run_id / "run_metadata.json"
        write_json(raw_path, records)
        metadata = self._metadata(
            run_id=run_id,
            platform=platform,
            target=target,
            actor_ids=actor_ids,
            actor_input=actor_input,
            actor_runs=actor_runs,
            records_count=len(records),
            status=status,
            error_message=error_message,
            raw_path=raw_path,
        )
        write_json(metadata_path, metadata)
        self._log_run(metadata)
        self._log_raw_records(metadata, records, raw_path)

        if status == "FAILED":
            raise ApifyClientError(f"Scrape run {run_id} failed: {error_message}")
        return ScrapeResult(run_id, platform, status, len(records), raw_path, metadata_path)

    def _run_actor(self, actor_id: str, actor_input: dict[str, Any]) -> tuple[ApifyRun, list[dict[str, Any]]]:
        started_run = self.client.start_run(actor_id, actor_input)
        finished_run = self.client.wait_for_run(started_run.id)
        if finished_run.status != "SUCCEEDED":
            raise ApifyClientError(f"Apify run {finished_run.id} ended with status {finished_run.status}.")
        records = self.client.fetch_dataset_items(finished_run.dataset_id) if finished_run.dataset_id else []
        return finished_run, records

    def _metadata(
        self,
        run_id: str,
        platform: str,
        target: dict[str, Any],
        actor_ids: list[str],
        actor_input: dict[str, Any],
        actor_runs: list[dict[str, Any]],
        records_count: int,
        status: str,
        error_message: str,
        raw_path: Path,
    ) -> dict[str, Any]:
        dataset_ids = [run["dataset_id"] for run in actor_runs if run.get("dataset_id")]
        return {
            "run_id": run_id,
            "platform": platform,
            "brand_or_competitor": brand_or_competitor(target),
            "source_account": source_account(target),
            "actor_id": ",".join(actor_ids),
            "input_json": actor_input,
            "dataset_id": ",".join(dataset_ids),
            "records_count": records_count,
            "status": status,
            "error_message": error_message,
            "raw_file_path": str(raw_path),
            "actor_runs": actor_runs,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def _log_run(self, metadata: dict[str, Any]) -> None:
        append_scrape_run(self.project_root / "data" / "processed" / "scrape_runs.csv", metadata)

    def _log_raw_records(self, metadata: dict[str, Any], records: list[dict[str, Any]], raw_path: Path) -> None:
        rows = []
        for index, record in enumerate(records):
            rows.append(
                {
                    "run_id": metadata["run_id"],
                    "platform": metadata["platform"],
                    "brand_or_competitor": metadata["brand_or_competitor"],
                    "source_account": metadata["source_account"],
                    "actor_id": metadata["actor_id"],
                    "dataset_id": metadata["dataset_id"],
                    "record_index": index,
                    "record_key": self._record_key(record),
                    "raw_file_path": str(raw_path),
                }
            )
        append_raw_record_rows(self.project_root / "data" / "processed" / "raw_records_log.csv", rows)

    @staticmethod
    def _record_key(record: dict[str, Any]) -> str:
        for key in ("id", "tweetId", "tweet_id", "commentId", "reviewId", "url"):
            value = str(record.get(key, "")).strip()
            if value:
                return f"{key}:{value}"
        payload = json.dumps(record, ensure_ascii=True, sort_keys=True)
        return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @staticmethod
    def _new_run_id(platform: str) -> str:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        return f"{platform}_{stamp}_{uuid4().hex[:8]}"
