from __future__ import annotations

import csv
import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import yaml

from src.analyze.marketing_analysis import COMMENT_ANALYSIS_FIELDS, MarketingAnalyzer
from src.utils.config import PROJECT_ROOT, load_dotenv


LLM_COMMENT_FIELDS = [
    "record_id",
    "platform",
    "brand",
    "brand_or_competitor",
    "source_account",
    "posted_at",
    "text",
    "rule_sentiment_label",
    "rule_concern_category_label",
    "rule_urgency_flag",
    "llm_sentiment_label",
    "llm_sentiment_confidence",
    "llm_concern_category_id",
    "llm_concern_category_label",
    "llm_category_confidence",
    "llm_urgency_flag",
    "llm_urgency_confidence",
    "llm_keywords",
    "llm_marketing_opportunity",
    "llm_content_idea",
    "llm_escalation_recommendation",
    "llm_reason",
    "model",
    "cache_hit",
    "error_message",
    "raw_record_hash",
    "raw_file_path",
    "raw_record_index",
]


@dataclass(frozen=True)
class LlmAnalysisOutputs:
    comments_path: Path
    summary_path: Path
    status: str
    processed_count: int
    cache_hits: int
    errors_count: int


class OptionalLlmAnalyzer:
    def __init__(self, project_root: Path = PROJECT_ROOT) -> None:
        self.project_root = project_root
        self.analysis_dir = project_root / "data" / "analysis"
        self.rules = self._load_analysis_rules()
        self.llm_config = self.rules.get("llm", {}) if isinstance(self.rules.get("llm", {}), dict) else {}
        self.concern_categories = self._load_concern_categories()

    def run(self) -> LlmAnalysisOutputs:
        self.analysis_dir.mkdir(parents=True, exist_ok=True)
        comments_path = self.analysis_dir / "llm_comment_analysis.csv"
        summary_path = self.analysis_dir / "llm_insight_summary.json"

        if not self.llm_config.get("enabled", False):
            self._write_csv(comments_path, LLM_COMMENT_FIELDS, [])
            summary = self._summary("disabled", [], 0, 0, ["LLM analysis is disabled in config/analysis_rules.yaml."])
            self._write_json(summary_path, summary)
            return LlmAnalysisOutputs(comments_path, summary_path, "disabled", 0, 0, 0)

        source_rows = self._load_source_analysis()
        max_records = max(0, int(self.llm_config.get("max_records", 50) or 50))
        batch_size = max(1, int(self.llm_config.get("batch_size", 10) or 10))
        retry_limit = max(0, int(self.llm_config.get("retry_limit", 2) or 2))
        selected_rows = source_rows[:max_records]
        cache = self._load_cache()

        output_rows: list[dict[str, Any]] = []
        cache_hits = 0
        errors: list[str] = []

        for batch in self._batches(selected_rows, batch_size):
            uncached_batch = []
            for row in batch:
                key = self._cache_key(row)
                cached = cache.get(key)
                if cached:
                    output_rows.append(self._merge_row(row, cached, cache_hit=True))
                    cache_hits += 1
                else:
                    uncached_batch.append(row)

            if not uncached_batch:
                continue

            try:
                batch_results = self._request_batch(uncached_batch, retry_limit)
            except Exception as exc:
                message = str(exc)
                errors.append(message)
                for row in uncached_batch:
                    output_rows.append(self._error_row(row, message))
                continue

            result_by_id = {str(item.get("record_id", "")): item for item in batch_results if isinstance(item, dict)}
            for row in uncached_batch:
                result = result_by_id.get(row.get("record_id", ""))
                if result is None:
                    message = "LLM response did not include this record_id."
                    errors.append(message)
                    output_rows.append(self._error_row(row, message))
                    continue
                cache[self._cache_key(row)] = result
                output_rows.append(self._merge_row(row, result, cache_hit=False))

        self._save_cache(cache)
        self._write_csv(comments_path, LLM_COMMENT_FIELDS, output_rows)
        summary = self._summary("completed", output_rows, cache_hits, len(errors), errors)
        self._write_json(summary_path, summary)
        return LlmAnalysisOutputs(comments_path, summary_path, "completed", len(output_rows), cache_hits, len(errors))

    def _request_batch(self, rows: list[dict[str, str]], retry_limit: int) -> list[dict[str, Any]]:
        last_error: Exception | None = None
        for attempt in range(retry_limit + 1):
            try:
                return self._call_openai_compatible(rows)
            except Exception as exc:
                last_error = exc
                if attempt < retry_limit:
                    time.sleep(2**attempt)
        raise RuntimeError(f"LLM request failed after {retry_limit + 1} attempt(s): {last_error}")

    def _call_openai_compatible(self, rows: list[dict[str, str]]) -> list[dict[str, Any]]:
        load_dotenv()
        api_key_env = str(self.llm_config.get("api_key_env", "OPENAI_API_KEY"))
        api_key = os.environ.get(api_key_env, "").strip()
        if not api_key:
            raise RuntimeError(f"Missing {api_key_env} in .env or environment.")

        model = str(self.llm_config.get("model", "")).strip()
        if not model:
            raise RuntimeError("Missing llm.model in config/analysis_rules.yaml.")

        base_url = str(self.llm_config.get("base_url", "https://api.openai.com/v1")).rstrip("/")
        payload = {
            "model": model,
            "temperature": float(self.llm_config.get("temperature", 0) or 0),
            "max_tokens": int(self.llm_config.get("max_output_tokens", 1200) or 1200),
            "messages": [
                {"role": "system", "content": self._system_prompt()},
                {"role": "user", "content": json.dumps(self._user_payload(rows), ensure_ascii=False)},
            ],
        }
        request = Request(
            f"{base_url}/chat/completions",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            method="POST",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        )
        timeout = int(self.llm_config.get("timeout_seconds", 60) or 60)
        try:
            with urlopen(request, timeout=timeout) as response:
                response_payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"LLM HTTP {exc.code}: {details}") from exc
        except URLError as exc:
            raise RuntimeError(f"LLM network error: {exc.reason}") from exc

        content = response_payload["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        results = parsed.get("comments", parsed) if isinstance(parsed, dict) else parsed
        if not isinstance(results, list):
            raise RuntimeError("LLM response must be a JSON list or an object with a comments list.")
        return results

    def _system_prompt(self) -> str:
        categories = [
            {
                "id": category.get("id", ""),
                "label": category.get("label", ""),
                "description": category.get("description", ""),
            }
            for category in self.concern_categories
        ]
        return (
            "You analyze marketing comments. Return only valid JSON. Do not include chain-of-thought, "
            "step-by-step reasoning, markdown, or prose outside JSON. Use short evidence-based reasons. "
            "Choose concern categories only from this list; use uncategorized if none fit: "
            + json.dumps(categories, ensure_ascii=False)
        )

    @staticmethod
    def _user_payload(rows: list[dict[str, str]]) -> dict[str, Any]:
        return {
            "task": "For each comment, produce concise explainable marketing labels without chain-of-thought.",
            "schema": {
                "record_id": "same input record_id",
                "llm_sentiment_label": "positive | neutral | negative | mixed | unknown",
                "llm_sentiment_confidence": "0.0 to 1.0",
                "llm_concern_category_id": "configured category id or uncategorized",
                "llm_concern_category_label": "configured category label or uncategorized",
                "llm_category_confidence": "0.0 to 1.0",
                "llm_urgency_flag": "true or false",
                "llm_urgency_confidence": "0.0 to 1.0",
                "llm_keywords": "comma-separated keywords",
                "llm_marketing_opportunity": "short opportunity or empty string",
                "llm_content_idea": "short content idea or empty string",
                "llm_escalation_recommendation": "short escalation recommendation or empty string",
                "llm_reason": "brief evidence summary, no hidden reasoning",
            },
            "comments": [
                {
                    "record_id": row.get("record_id"),
                    "platform": row.get("platform"),
                    "brand_or_competitor": row.get("brand_or_competitor"),
                    "rule_sentiment_label": row.get("sentiment_label"),
                    "rule_concern_category_label": row.get("concern_category_label"),
                    "rule_urgency_flag": row.get("urgency_flag"),
                    "text": row.get("text"),
                }
                for row in rows
            ],
        }

    def _merge_row(self, source: dict[str, str], llm_result: dict[str, Any], cache_hit: bool) -> dict[str, Any]:
        return {
            **self._base_output_row(source),
            "llm_sentiment_label": llm_result.get("llm_sentiment_label"),
            "llm_sentiment_confidence": llm_result.get("llm_sentiment_confidence"),
            "llm_concern_category_id": llm_result.get("llm_concern_category_id"),
            "llm_concern_category_label": llm_result.get("llm_concern_category_label"),
            "llm_category_confidence": llm_result.get("llm_category_confidence"),
            "llm_urgency_flag": str(llm_result.get("llm_urgency_flag", "")).lower(),
            "llm_urgency_confidence": llm_result.get("llm_urgency_confidence"),
            "llm_keywords": llm_result.get("llm_keywords"),
            "llm_marketing_opportunity": llm_result.get("llm_marketing_opportunity"),
            "llm_content_idea": llm_result.get("llm_content_idea"),
            "llm_escalation_recommendation": llm_result.get("llm_escalation_recommendation"),
            "llm_reason": llm_result.get("llm_reason"),
            "model": self.llm_config.get("model"),
            "cache_hit": "true" if cache_hit else "false",
            "error_message": "",
        }

    def _error_row(self, source: dict[str, str], error_message: str) -> dict[str, Any]:
        return {**self._base_output_row(source), "model": self.llm_config.get("model"), "cache_hit": "false", "error_message": error_message}

    @staticmethod
    def _base_output_row(source: dict[str, str]) -> dict[str, Any]:
        return {
            "record_id": source.get("record_id"),
            "platform": source.get("platform"),
            "brand": source.get("brand"),
            "brand_or_competitor": source.get("brand_or_competitor"),
            "source_account": source.get("source_account"),
            "posted_at": source.get("posted_at"),
            "text": source.get("text"),
            "rule_sentiment_label": source.get("sentiment_label"),
            "rule_concern_category_label": source.get("concern_category_label"),
            "rule_urgency_flag": source.get("urgency_flag"),
            "raw_record_hash": source.get("raw_record_hash"),
            "raw_file_path": source.get("raw_file_path"),
            "raw_record_index": source.get("raw_record_index"),
        }

    def _summary(self, status: str, rows: list[dict[str, Any]], cache_hits: int, errors_count: int, errors: list[str]) -> dict[str, Any]:
        sentiment_counts: dict[str, int] = {}
        urgency_count = 0
        for row in rows:
            sentiment = str(row.get("llm_sentiment_label") or "unknown")
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
            if str(row.get("llm_urgency_flag", "")).lower() == "true":
                urgency_count += 1
        return {
            "status": status,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "enabled": bool(self.llm_config.get("enabled", False)),
            "model": self.llm_config.get("model", ""),
            "max_records": self.llm_config.get("max_records", 50),
            "batch_size": self.llm_config.get("batch_size", 10),
            "retry_limit": self.llm_config.get("retry_limit", 2),
            "processed_count": len(rows),
            "cache_hits": cache_hits,
            "errors_count": errors_count,
            "errors": errors[:20],
            "sentiment_counts": sentiment_counts,
            "urgent_count": urgency_count,
            "note": "LLM outputs are separate from rule-based analysis and do not overwrite comment_analysis.csv.",
        }

    def _load_source_analysis(self) -> list[dict[str, str]]:
        source_path = self.analysis_dir / "comment_analysis.csv"
        if not source_path.exists():
            MarketingAnalyzer(self.project_root).run()
        with source_path.open("r", newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)
        return [row for row in rows if row.get("record_id")]

    def _load_analysis_rules(self) -> dict[str, Any]:
        path = self.project_root / "config" / "analysis_rules.yaml"
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return payload if isinstance(payload, dict) else {}

    def _load_concern_categories(self) -> list[dict[str, Any]]:
        path = self.project_root / "config" / "concern_categories.yaml"
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        categories = payload.get("categories", [])
        return [category for category in categories if isinstance(category, dict)] if isinstance(categories, list) else []

    def _cache_path(self) -> Path:
        configured = Path(str(self.llm_config.get("cache_path", "data/analysis/cache/llm_comment_analysis_cache.json")))
        return configured if configured.is_absolute() else self.project_root / configured

    def _load_cache(self) -> dict[str, Any]:
        path = self._cache_path()
        if not path.exists():
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            return payload if isinstance(payload, dict) else {}
        except json.JSONDecodeError:
            return {}

    def _save_cache(self, cache: dict[str, Any]) -> None:
        path = self._cache_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(cache, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    def _cache_key(self, row: dict[str, str]) -> str:
        return self._stable_key(
            {
                "record_id": row.get("record_id"),
                "raw_record_hash": row.get("raw_record_hash"),
                "text": row.get("text"),
                "model": self.llm_config.get("model"),
                "categories": self.concern_categories,
                "version": 1,
            }
        )

    @staticmethod
    def _stable_key(payload: dict[str, Any]) -> str:
        import hashlib

        serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    @staticmethod
    def _batches(rows: list[dict[str, str]], size: int) -> list[list[dict[str, str]]]:
        return [rows[index : index + size] for index in range(0, len(rows), size)]

    @staticmethod
    def _write_csv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            for row in rows:
                writer.writerow({field: OptionalLlmAnalyzer._csv_value(row.get(field)) for field in fields})

    @staticmethod
    def _write_json(path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    @staticmethod
    def _csv_value(value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False, sort_keys=True)
        return str(value)
