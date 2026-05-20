from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.utils.config import PROJECT_ROOT


PLATFORMS = ("tiktok", "instagram", "x", "app_store")

MARKET_COMMENT_FIELDS = [
    "record_id",
    "raw_record_hash",
    "platform",
    "source_type",
    "scrape_run_id",
    "raw_file_path",
    "raw_record_index",
    "brand",
    "brand_or_competitor",
    "source_account",
    "source_id",
    "source_url",
    "post_id",
    "comment_id",
    "parent_id",
    "author_id",
    "author_username",
    "author_display_name",
    "text",
    "language",
    "posted_at",
    "posted_at_raw",
    "scraped_at",
    "likes",
    "replies",
    "shares",
    "views",
    "rating",
    "app_version",
    "country",
    "sentiment_label",
    "concern_category",
    "urgency_flag",
    "raw_field_names",
    "raw_record_json",
]

POST_FIELDS = [
    "post_record_id",
    "platform",
    "scrape_run_id",
    "raw_file_path",
    "source_id",
    "source_account",
    "post_id",
    "post_url",
    "post_text",
    "posted_at",
    "posted_at_raw",
    "likes",
    "comments",
    "shares",
    "views",
    "raw_record_hash",
]

SOURCE_FIELDS = [
    "source_record_id",
    "platform",
    "source_id",
    "source_account",
    "source_url",
    "brand",
    "brand_or_competitor",
    "scrape_run_id",
    "raw_file_path",
]

ERROR_FIELDS = [
    "error_id",
    "platform",
    "scrape_run_id",
    "raw_file_path",
    "raw_record_index",
    "error_message",
    "raw_record_hash",
]


@dataclass(frozen=True)
class NormalizationOutputs:
    market_comments_path: Path
    posts_path: Path
    sources_path: Path
    errors_path: Path
    records_count: int
    posts_count: int
    sources_count: int
    errors_count: int


class MarketCommentsNormalizer:
    def __init__(self, project_root: Path = PROJECT_ROOT) -> None:
        self.project_root = project_root
        self.raw_root = project_root / "data" / "raw"
        self.processed_root = project_root / "data" / "processed"

    def normalize_all(self) -> NormalizationOutputs:
        comments: list[dict[str, Any]] = []
        posts: list[dict[str, Any]] = []
        sources: list[dict[str, Any]] = []
        errors: list[dict[str, Any]] = []

        for platform in PLATFORMS:
            platform_dir = self.raw_root / platform
            if not platform_dir.exists():
                continue
            for raw_file_path in sorted(platform_dir.glob("*.json")):
                self._normalize_file(platform, raw_file_path, comments, posts, sources, errors)

        comments = self._dedupe_by_keys(comments, ("record_id", "raw_record_hash"))
        posts = self._dedupe_by_keys(posts, ("post_record_id", "raw_record_hash"))
        sources = self._dedupe_by_keys(sources, ("source_record_id",))

        market_comments_path = self.processed_root / "market_comments.csv"
        posts_path = self.processed_root / "posts.csv"
        sources_path = self.processed_root / "sources.csv"
        errors_path = self.processed_root / "normalization_errors.csv"

        self._write_csv(market_comments_path, MARKET_COMMENT_FIELDS, comments)
        self._write_csv(posts_path, POST_FIELDS, posts)
        self._write_csv(sources_path, SOURCE_FIELDS, sources)
        self._write_csv(errors_path, ERROR_FIELDS, errors)

        return NormalizationOutputs(
            market_comments_path=market_comments_path,
            posts_path=posts_path,
            sources_path=sources_path,
            errors_path=errors_path,
            records_count=len(comments),
            posts_count=len(posts),
            sources_count=len(sources),
            errors_count=len(errors),
        )

    def _normalize_file(
        self,
        platform: str,
        raw_file_path: Path,
        comments: list[dict[str, Any]],
        posts: list[dict[str, Any]],
        sources: list[dict[str, Any]],
        errors: list[dict[str, Any]],
    ) -> None:
        scrape_run_id = raw_file_path.stem
        metadata = self._load_metadata(scrape_run_id)
        try:
            payload = json.loads(raw_file_path.read_text(encoding="utf-8"))
            records = payload if isinstance(payload, list) else [payload]
        except Exception as exc:
            errors.append(self._error(platform, scrape_run_id, raw_file_path, None, str(exc), None))
            return

        for index, record in enumerate(records):
            if not isinstance(record, dict):
                errors.append(self._error(platform, scrape_run_id, raw_file_path, index, "Raw record is not a JSON object.", record))
                continue
            try:
                comment = self._comment_row(platform, scrape_run_id, raw_file_path, index, record, metadata)
                comments.append(comment)

                post = self._post_row(platform, scrape_run_id, raw_file_path, record, comment)
                if post["post_record_id"]:
                    posts.append(post)

                source = self._source_row(platform, scrape_run_id, raw_file_path, comment)
                if source["source_record_id"]:
                    sources.append(source)
            except Exception as exc:
                errors.append(self._error(platform, scrape_run_id, raw_file_path, index, str(exc), record))

    def _comment_row(
        self,
        platform: str,
        scrape_run_id: str,
        raw_file_path: Path,
        index: int,
        record: dict[str, Any],
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        text = self._first_text(record, ("text", "comment", "commentText", "review", "reviewText", "content", "fullText", "caption"))
        posted_at_raw = self._first_text(record, ("createdAt", "created_at", "timestamp", "date", "publishedAt", "postedAt", "time"))
        posted_at = self._parse_timestamp(posted_at_raw)
        source_url = self._first_text(record, ("url", "postUrl", "tweetUrl", "videoUrl", "inputUrl", "reviewUrl"))
        source_id = self._first_text(record, ("sourceId", "ownerId", "userId", "authorId", "appId", "profileId", "accountId"))
        source_account = self._first_text(record, ("sourceAccount", "username", "authorUsername", "ownerUsername", "handle", "screenName"))
        comment_id = self._first_text(record, ("id", "commentId", "comment_id", "reviewId", "review_id", "tweetId", "tweet_id"))
        post_id = self._first_text(record, ("postId", "post_id", "videoId", "video_id", "tweetId", "tweet_id", "threadId"))

        brand = self._first_non_empty(metadata.get("brand"), metadata.get("brand_or_competitor"))
        brand_or_competitor = self._first_non_empty(metadata.get("brand_or_competitor"), brand)
        if not source_account:
            source_account = self._safe_text(metadata.get("source_account"))

        raw_hash = self._stable_hash(record)
        record_id = self._record_id(platform, source_id or source_url, comment_id or text, posted_at or posted_at_raw)

        return {
            "record_id": record_id,
            "raw_record_hash": raw_hash,
            "platform": platform,
            "source_type": "app_review" if platform == "app_store" else "social_comment",
            "scrape_run_id": scrape_run_id,
            "raw_file_path": str(raw_file_path),
            "raw_record_index": index,
            "brand": brand,
            "brand_or_competitor": brand_or_competitor,
            "source_account": source_account,
            "source_id": source_id,
            "source_url": source_url,
            "post_id": post_id,
            "comment_id": comment_id,
            "parent_id": self._first_text(record, ("parentId", "parent_id", "inReplyToId", "replyToId")),
            "author_id": self._first_text(record, ("authorId", "author_id", "userId", "user_id")),
            "author_username": self._first_text(record, ("authorUsername", "username", "userName", "screenName", "handle")),
            "author_display_name": self._first_text(record, ("authorName", "displayName", "fullName", "userFullName", "name")),
            "text": text,
            "language": self._first_text(record, ("language", "lang", "locale")),
            "posted_at": posted_at,
            "posted_at_raw": posted_at_raw,
            "scraped_at": metadata.get("created_at"),
            "likes": self._first_number(record, ("likes", "likeCount", "likesCount", "favoriteCount", "favorites")),
            "replies": self._first_number(record, ("replies", "replyCount", "commentsCount", "commentCount")),
            "shares": self._first_number(record, ("shares", "shareCount", "retweetCount", "reposts")),
            "views": self._first_number(record, ("views", "viewCount", "playCount")),
            "rating": self._first_number(record, ("rating", "score", "stars")),
            "app_version": self._first_text(record, ("appVersion", "version", "app_version")),
            "country": self._first_text(record, ("country", "countryCode", "region")),
            "sentiment_label": None,
            "concern_category": None,
            "urgency_flag": None,
            "raw_field_names": sorted(record.keys()),
            "raw_record_json": record,
        }

    def _post_row(
        self,
        platform: str,
        scrape_run_id: str,
        raw_file_path: Path,
        record: dict[str, Any],
        comment: dict[str, Any],
    ) -> dict[str, Any]:
        post_id = self._safe_text(comment.get("post_id"))
        post_url = self._first_text(record, ("postUrl", "tweetUrl", "videoUrl", "url"))
        post_text = self._first_text(record, ("postText", "caption", "tweetText", "title"))
        post_key = post_id or post_url
        post_record_id = self._stable_hash({"platform": platform, "source": comment.get("source_id") or post_url, "post": post_key}) if post_key else None
        return {
            "post_record_id": post_record_id,
            "platform": platform,
            "scrape_run_id": scrape_run_id,
            "raw_file_path": str(raw_file_path),
            "source_id": comment.get("source_id"),
            "source_account": comment.get("source_account"),
            "post_id": post_id,
            "post_url": post_url,
            "post_text": post_text,
            "posted_at": comment.get("posted_at"),
            "posted_at_raw": comment.get("posted_at_raw"),
            "likes": self._first_number(record, ("postLikes", "likes", "likeCount")),
            "comments": self._first_number(record, ("comments", "commentsCount", "commentCount")),
            "shares": self._first_number(record, ("postShares", "shares", "shareCount")),
            "views": self._first_number(record, ("postViews", "views", "viewCount", "playCount")),
            "raw_record_hash": comment.get("raw_record_hash"),
        }

    def _source_row(
        self,
        platform: str,
        scrape_run_id: str,
        raw_file_path: Path,
        comment: dict[str, Any],
    ) -> dict[str, Any]:
        source_id = self._safe_text(comment.get("source_id"))
        source_account = self._safe_text(comment.get("source_account"))
        source_url = self._safe_text(comment.get("source_url"))
        source_key = source_id or source_account or source_url
        source_record_id = self._stable_hash({"platform": platform, "source": source_key}) if source_key else None
        return {
            "source_record_id": source_record_id,
            "platform": platform,
            "source_id": source_id,
            "source_account": source_account,
            "source_url": source_url,
            "brand": comment.get("brand"),
            "brand_or_competitor": comment.get("brand_or_competitor"),
            "scrape_run_id": scrape_run_id,
            "raw_file_path": str(raw_file_path),
        }

    def _load_metadata(self, scrape_run_id: str) -> dict[str, Any]:
        path = self.raw_root / "runs" / scrape_run_id / "run_metadata.json"
        if not path.exists():
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            return payload if isinstance(payload, dict) else {}
        except Exception:
            return {}

    def _dedupe_by_keys(self, rows: list[dict[str, Any]], keys: tuple[str, ...]) -> list[dict[str, Any]]:
        best_by_key: dict[str, dict[str, Any]] = {}
        for row in rows:
            candidate_keys = [self._safe_text(row.get(key)) for key in keys if self._safe_text(row.get(key))]
            if not candidate_keys:
                candidate_keys = [self._stable_hash(row)]

            existing_rows = [best_by_key[key] for key in candidate_keys if key in best_by_key]
            if existing_rows:
                best = max([row, *existing_rows], key=self._quality_score)
                for key in candidate_keys:
                    best_by_key[key] = best
                for existing in existing_rows:
                    for existing_key, existing_row in list(best_by_key.items()):
                        if existing_row is existing:
                            best_by_key[existing_key] = best
            else:
                for key in candidate_keys:
                    best_by_key[key] = row

        unique: dict[int, dict[str, Any]] = {}
        for row in best_by_key.values():
            unique[id(row)] = row
        return sorted(unique.values(), key=lambda item: self._safe_text(item.get(keys[0] if keys else "record_id")))

    def _quality_score(self, row: dict[str, Any]) -> tuple[int, str, int]:
        populated = sum(1 for value in row.values() if value not in (None, "", [], {}))
        timestamp = self._safe_text(row.get("posted_at") or row.get("scraped_at") or row.get("posted_at_raw"))
        text_length = len(self._safe_text(row.get("text") or row.get("post_text")))
        return populated, timestamp, text_length

    def _write_csv(self, path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            for row in rows:
                writer.writerow({field: self._csv_value(row.get(field)) for field in fields})

    def _error(
        self,
        platform: str,
        scrape_run_id: str,
        raw_file_path: Path,
        index: int | None,
        message: str,
        raw_record: Any,
    ) -> dict[str, Any]:
        raw_hash = self._stable_hash(raw_record) if raw_record is not None else None
        return {
            "error_id": self._stable_hash({"path": str(raw_file_path), "index": index, "message": message, "raw_hash": raw_hash}),
            "platform": platform,
            "scrape_run_id": scrape_run_id,
            "raw_file_path": str(raw_file_path),
            "raw_record_index": index,
            "error_message": message,
            "raw_record_hash": raw_hash,
        }

    def _record_id(self, platform: str, source: str | None, comment: str | None, posted_at: str | None) -> str:
        return self._stable_hash(
            {
                "platform": platform,
                "source_id_or_url": self._safe_text(source),
                "comment_id_or_text": self._safe_text(comment),
                "datetime": self._safe_text(posted_at),
            }
        )

    @staticmethod
    def _stable_hash(value: Any) -> str:
        payload = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @staticmethod
    def _csv_value(value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False, sort_keys=True)
        return str(value)

    @staticmethod
    def _first_text(record: dict[str, Any], keys: tuple[str, ...]) -> str | None:
        for key in keys:
            value = record.get(key)
            if value not in (None, ""):
                return str(value)
        return None

    @staticmethod
    def _first_number(record: dict[str, Any], keys: tuple[str, ...]) -> int | float | None:
        for key in keys:
            value = record.get(key)
            if value in (None, ""):
                continue
            try:
                number = float(value)
            except (TypeError, ValueError):
                continue
            return int(number) if number.is_integer() else number
        return None

    @staticmethod
    def _first_non_empty(*values: Any) -> str | None:
        for value in values:
            if value not in (None, ""):
                return str(value)
        return None

    @staticmethod
    def _safe_text(value: Any) -> str:
        if value in (None, ""):
            return ""
        return str(value)

    @staticmethod
    def _parse_timestamp(value: str | None) -> str | None:
        if not value:
            return None
        text = str(value).strip()
        if not text:
            return None
        if text.isdigit():
            number = int(text)
            if number > 10_000_000_000:
                number = number / 1000
            try:
                return datetime.fromtimestamp(number, tz=timezone.utc).isoformat()
            except (OverflowError, OSError, ValueError):
                return None
        normalized = text.replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError:
            for pattern in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
                try:
                    parsed = datetime.strptime(text, pattern)
                    break
                except ValueError:
                    parsed = None
            if parsed is None:
                return None
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc).isoformat()
