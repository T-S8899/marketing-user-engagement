from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import yaml

from src.utils.config import PROJECT_ROOT


TOKEN_RE = re.compile(r"[\w\u0600-\u06FF]+", re.UNICODE)

COMMENT_ANALYSIS_FIELDS = [
    "record_id",
    "platform",
    "brand",
    "brand_or_competitor",
    "source_account",
    "posted_at",
    "text",
    "sentiment_label",
    "sentiment_confidence",
    "sentiment_reason",
    "concern_category_id",
    "concern_category_label",
    "category_confidence",
    "category_reason",
    "keywords",
    "keyword_confidence",
    "urgency_flag",
    "urgency_confidence",
    "urgency_reason",
    "recommended_action",
    "raw_record_hash",
    "raw_file_path",
    "raw_record_index",
]

SUMMARY_FIELDS = [
    "group",
    "label",
    "comments_count",
    "share_of_total",
    "avg_confidence",
    "positive_count",
    "neutral_count",
    "negative_count",
    "urgent_count",
    "example_record_id",
    "example_text",
]

KEYWORD_FIELDS = [
    "keyword",
    "comments_count",
    "platforms",
    "brands",
    "avg_sentiment_score",
    "urgent_count",
    "example_record_id",
    "example_text",
]

OPPORTUNITY_FIELDS = [
    "opportunity_id",
    "type",
    "platform",
    "brand_or_competitor",
    "concern_category_label",
    "keyword",
    "comments_count",
    "confidence",
    "reason",
    "recommended_action",
    "example_record_id",
    "example_text",
]

ESCALATION_FIELDS = [
    "record_id",
    "platform",
    "brand",
    "brand_or_competitor",
    "source_account",
    "posted_at",
    "text",
    "urgency_confidence",
    "urgency_reason",
    "concern_category_label",
    "sentiment_label",
    "recommended_action",
    "raw_file_path",
]


@dataclass(frozen=True)
class AnalysisOutputs:
    output_dir: Path
    comments_count: int


class MarketingAnalyzer:
    def __init__(self, project_root: Path = PROJECT_ROOT) -> None:
        self.project_root = project_root
        self.processed_path = project_root / "data" / "processed" / "market_comments.csv"
        self.output_dir = project_root / "data" / "analysis"
        self.concern_categories = self._load_concern_categories()
        self.rules = self._load_analysis_rules()

    def run(self) -> AnalysisOutputs:
        comments = self._read_market_comments()
        analyzed = [self._analyze_comment(comment) for comment in comments]

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._write_csv(self.output_dir / "comment_analysis.csv", COMMENT_ANALYSIS_FIELDS, analyzed)
        self._write_csv(self.output_dir / "concern_category_summary.csv", SUMMARY_FIELDS, self._summary(analyzed, "concern_category_label"))
        self._write_csv(self.output_dir / "sentiment_summary.csv", SUMMARY_FIELDS, self._summary(analyzed, "sentiment_label"))
        self._write_csv(self.output_dir / "platform_summary.csv", SUMMARY_FIELDS, self._summary(analyzed, "platform"))
        self._write_csv(self.output_dir / "brand_competitor_summary.csv", SUMMARY_FIELDS, self._summary(analyzed, "brand_or_competitor"))
        self._write_csv(self.output_dir / "keyword_summary.csv", KEYWORD_FIELDS, self._keyword_summary(analyzed))
        self._write_csv(self.output_dir / "emerging_concerns.csv", OPPORTUNITY_FIELDS, self._emerging_concerns(analyzed))
        self._write_csv(self.output_dir / "urgent_comments.csv", COMMENT_ANALYSIS_FIELDS, [row for row in analyzed if row["urgency_flag"] == "true"])
        self._write_csv(self.output_dir / "marketing_opportunities.csv", OPPORTUNITY_FIELDS, self._marketing_opportunities(analyzed))
        self._write_csv(self.output_dir / "content_ideas.csv", OPPORTUNITY_FIELDS, self._content_ideas(analyzed))
        self._write_csv(self.output_dir / "escalation_items.csv", ESCALATION_FIELDS, self._escalation_items(analyzed))

        return AnalysisOutputs(output_dir=self.output_dir, comments_count=len(analyzed))

    def _analyze_comment(self, comment: dict[str, str]) -> dict[str, Any]:
        text = comment.get("text", "")
        sentiment = self._sentiment(text, comment.get("rating", ""))
        category = self._category(text)
        keywords = self._keywords(text)
        urgency = self._urgency(comment, text, sentiment)

        return {
            "record_id": comment.get("record_id"),
            "platform": comment.get("platform"),
            "brand": comment.get("brand"),
            "brand_or_competitor": comment.get("brand_or_competitor") or comment.get("brand"),
            "source_account": comment.get("source_account"),
            "posted_at": comment.get("posted_at"),
            "text": text,
            "sentiment_label": sentiment["label"],
            "sentiment_confidence": sentiment["confidence"],
            "sentiment_reason": sentiment["reason"],
            "concern_category_id": category["id"],
            "concern_category_label": category["label"],
            "category_confidence": category["confidence"],
            "category_reason": category["reason"],
            "keywords": keywords["keywords"],
            "keyword_confidence": keywords["confidence"],
            "urgency_flag": "true" if urgency["flag"] else "false",
            "urgency_confidence": urgency["confidence"],
            "urgency_reason": urgency["reason"],
            "recommended_action": self._recommended_action(sentiment["label"], category["label"], urgency["flag"]),
            "raw_record_hash": comment.get("raw_record_hash"),
            "raw_file_path": comment.get("raw_file_path"),
            "raw_record_index": comment.get("raw_record_index"),
        }

    def _sentiment(self, text: str, rating: str) -> dict[str, Any]:
        rules = self.rules.get("sentiment", {})
        if not rules.get("enabled", True):
            return {"label": "unknown", "confidence": 0.0, "reason": "Sentiment analysis disabled in config."}

        tokens = set(self._tokenize(text))
        positive_hits = self._keyword_hits(text, tokens, rules.get("positive_keywords", []))
        negative_hits = self._keyword_hits(text, tokens, rules.get("negative_keywords", []))
        rating_score = self._rating_score(rating)
        score = len(positive_hits) - len(negative_hits) + rating_score

        if score > 0:
            label = "positive"
        elif score < 0:
            label = "negative"
        else:
            label = "neutral"

        evidence = abs(score) + len(positive_hits) + len(negative_hits)
        confidence = min(1.0, 0.35 + (evidence * 0.15)) if evidence else 0.25
        reason_parts = []
        if positive_hits:
            reason_parts.append("positive keywords: " + ", ".join(positive_hits[:5]))
        if negative_hits:
            reason_parts.append("negative keywords: " + ", ".join(negative_hits[:5]))
        if rating_score:
            reason_parts.append(f"rating signal: {rating}")
        reason = "; ".join(reason_parts) or "No configured sentiment keywords or rating signal matched."
        return {"label": label, "confidence": round(confidence, 3), "reason": reason}

    def _category(self, text: str) -> dict[str, Any]:
        tokens = set(self._tokenize(text))
        best: dict[str, Any] | None = None
        for category in self.concern_categories:
            keywords = self._category_keywords(category)
            hits = sorted(tokens.intersection(keywords))
            if not hits:
                continue
            confidence = min(1.0, 0.35 + (len(hits) * 0.2))
            candidate = {
                "id": str(category.get("id") or category.get("label") or "unknown"),
                "label": str(category.get("label") or category.get("id") or "unknown"),
                "confidence": round(confidence, 3),
                "reason": "matched category keywords: " + ", ".join(hits[:8]),
                "hits": len(hits),
            }
            if best is None or candidate["hits"] > best["hits"]:
                best = candidate

        if best is None:
            return {
                "id": "uncategorized",
                "label": "uncategorized",
                "confidence": 0.0,
                "reason": "No concern category keywords matched from config/concern_categories.yaml.",
            }
        return best

    def _keywords(self, text: str) -> dict[str, Any]:
        rules = self.rules.get("keywords", {})
        min_length = int(rules.get("min_length", 3) or 3)
        stopwords = self._lower_list(rules.get("stopwords", []))
        tokens = [token for token in self._tokenize(text) if len(token) >= min_length and token not in stopwords]
        counts = Counter(tokens)
        top_n = int(self.rules.get("aggregation", {}).get("top_n_themes", 25) or 25)
        keywords = [keyword for keyword, _count in counts.most_common(top_n)]
        confidence = min(1.0, len(keywords) / 5) if keywords else 0.0
        return {"keywords": ", ".join(keywords), "confidence": round(confidence, 3)}

    def _urgency(self, comment: dict[str, str], text: str, sentiment: dict[str, Any]) -> dict[str, Any]:
        rules = self.rules.get("urgency", {})
        if not rules.get("enabled", True):
            return {"flag": False, "confidence": 0.0, "reason": "Urgency detection disabled in config."}

        tokens = set(self._tokenize(text))
        urgency_hits = self._keyword_hits(text, tokens, rules.get("keywords", []))
        engagement = self._number(comment.get("likes")) + self._number(comment.get("replies")) + self._number(comment.get("shares"))
        min_engagement = self._number(rules.get("min_engagement_for_urgent", 0))
        negative_is_urgent = bool(rules.get("negative_sentiment_is_urgent", False))

        reasons = []
        score = 0
        if urgency_hits:
            score += len(urgency_hits)
            reasons.append("urgent keywords: " + ", ".join(urgency_hits[:8]))
        if min_engagement and engagement >= min_engagement:
            score += 1
            reasons.append(f"high engagement: {int(engagement)}")
        if negative_is_urgent and sentiment["label"] == "negative":
            score += 1
            reasons.append("negative sentiment marked urgent by config")

        flag = score > 0
        confidence = min(1.0, 0.4 + (score * 0.2)) if flag else 0.0
        return {"flag": flag, "confidence": round(confidence, 3), "reason": "; ".join(reasons) or "No urgency rules matched."}

    def _summary(self, rows: list[dict[str, Any]], field: str) -> list[dict[str, Any]]:
        total = len(rows) or 1
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            grouped[row.get(field) or "unknown"].append(row)

        output = []
        for label, group_rows in sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0])):
            example = group_rows[0]
            output.append(
                {
                    "group": field,
                    "label": label,
                    "comments_count": len(group_rows),
                    "share_of_total": round(len(group_rows) / total, 4),
                    "avg_confidence": self._avg([self._number(row.get("sentiment_confidence")) for row in group_rows]),
                    "positive_count": self._count_label(group_rows, "positive"),
                    "neutral_count": self._count_label(group_rows, "neutral"),
                    "negative_count": self._count_label(group_rows, "negative"),
                    "urgent_count": sum(1 for row in group_rows if row.get("urgency_flag") == "true"),
                    "example_record_id": example.get("record_id"),
                    "example_text": example.get("text"),
                }
            )
        return output

    def _keyword_summary(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            for keyword in [part.strip() for part in row.get("keywords", "").split(",") if part.strip()]:
                grouped[keyword].append(row)
        top_n = int(self.rules.get("keywords", {}).get("top_n", 100) or 100)
        output = []
        for keyword, group_rows in sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0]))[:top_n]:
            example = group_rows[0]
            output.append(
                {
                    "keyword": keyword,
                    "comments_count": len(group_rows),
                    "platforms": ", ".join(sorted({row.get("platform", "") for row in group_rows if row.get("platform")})),
                    "brands": ", ".join(sorted({row.get("brand_or_competitor", "") for row in group_rows if row.get("brand_or_competitor")})),
                    "avg_sentiment_score": self._avg([self._sentiment_score(row.get("sentiment_label", "")) for row in group_rows]),
                    "urgent_count": sum(1 for row in group_rows if row.get("urgency_flag") == "true"),
                    "example_record_id": example.get("record_id"),
                    "example_text": example.get("text"),
                }
            )
        return output

    def _emerging_concerns(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        days = int(self.rules.get("aggregation", {}).get("emerging_recent_days", 14) or 14)
        min_recent = int(self.rules.get("aggregation", {}).get("emerging_min_recent_count", 3) or 3)
        growth_ratio = float(self.rules.get("aggregation", {}).get("emerging_growth_ratio", 1.5) or 1.5)
        now = self._latest_datetime(rows) or datetime.now(timezone.utc)
        cutoff = now - timedelta(days=days)

        grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            grouped[(row.get("concern_category_label") or "uncategorized", row.get("platform") or "unknown")].append(row)

        output = []
        for (category, platform), group_rows in grouped.items():
            recent = [row for row in group_rows if self._parse_datetime(row.get("posted_at")) and self._parse_datetime(row.get("posted_at")) >= cutoff]
            older = [row for row in group_rows if row not in recent]
            older_rate = len(older) / max(1, days)
            recent_rate = len(recent) / max(1, days)
            if len(recent) < min_recent or recent_rate < older_rate * growth_ratio:
                continue
            example = recent[0]
            output.append(self._opportunity_row("emerging_concern", platform, example, len(recent), min(1.0, recent_rate / max(older_rate, 0.1)), f"Recent mentions grew to {len(recent)} in {days} days.", "Investigate this concern and prepare response messaging."))
        return output

    def _marketing_opportunities(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        positive_rows = [row for row in rows if row.get("sentiment_label") == "positive"]
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in positive_rows:
            for keyword in [part.strip() for part in row.get("keywords", "").split(",") if part.strip()]:
                grouped[keyword].append(row)
        output = []
        for keyword, group_rows in sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0]))[:25]:
            example = group_rows[0]
            output.append(self._opportunity_row("marketing_opportunity", example.get("platform"), example, len(group_rows), self._avg([self._number(row.get("sentiment_confidence")) for row in group_rows]), f"Positive keyword repeated: {keyword}.", "Use this theme in proof points, ads, or social replies.", keyword=keyword))
        return output

    def _content_ideas(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        candidates = [row for row in rows if row.get("sentiment_label") in {"negative", "neutral"} and row.get("concern_category_label") != "uncategorized"]
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in candidates:
            grouped[row.get("concern_category_label") or "unknown"].append(row)
        output = []
        for category, group_rows in sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0]))[:25]:
            example = group_rows[0]
            output.append(self._opportunity_row("content_idea", example.get("platform"), example, len(group_rows), self._avg([self._number(row.get("category_confidence")) for row in group_rows]), f"Repeated concern category: {category}.", "Create FAQ, explainer, or comparison content addressing this concern."))
        return output

    def _escalation_items(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        urgent = [row for row in rows if row.get("urgency_flag") == "true"]
        return [
            {
                "record_id": row.get("record_id"),
                "platform": row.get("platform"),
                "brand": row.get("brand"),
                "brand_or_competitor": row.get("brand_or_competitor"),
                "source_account": row.get("source_account"),
                "posted_at": row.get("posted_at"),
                "text": row.get("text"),
                "urgency_confidence": row.get("urgency_confidence"),
                "urgency_reason": row.get("urgency_reason"),
                "concern_category_label": row.get("concern_category_label"),
                "sentiment_label": row.get("sentiment_label"),
                "recommended_action": row.get("recommended_action"),
                "raw_file_path": row.get("raw_file_path"),
            }
            for row in sorted(urgent, key=lambda item: self._number(item.get("urgency_confidence")), reverse=True)
        ]

    def _opportunity_row(
        self,
        row_type: str,
        platform: str | None,
        example: dict[str, Any],
        count: int,
        confidence: float,
        reason: str,
        action: str,
        keyword: str = "",
    ) -> dict[str, Any]:
        return {
            "opportunity_id": self._stable_id(row_type, platform, example.get("brand_or_competitor"), example.get("concern_category_label"), keyword),
            "type": row_type,
            "platform": platform,
            "brand_or_competitor": example.get("brand_or_competitor"),
            "concern_category_label": example.get("concern_category_label"),
            "keyword": keyword,
            "comments_count": count,
            "confidence": round(float(confidence), 3),
            "reason": reason,
            "recommended_action": action,
            "example_record_id": example.get("record_id"),
            "example_text": example.get("text"),
        }

    def _recommended_action(self, sentiment: str, category: str, urgent: bool) -> str:
        if urgent:
            return "Escalate for immediate review and prepare a direct response."
        if sentiment == "negative" and category != "uncategorized":
            return "Address this concern in messaging and monitor repeated mentions."
        if sentiment == "positive":
            return "Reuse this positive theme in content, ads, or community replies."
        return "Monitor for repetition before taking action."

    def _read_market_comments(self) -> list[dict[str, str]]:
        if not self.processed_path.exists():
            return []
        with self.processed_path.open("r", newline="", encoding="utf-8-sig") as handle:
            return list(csv.DictReader(handle))

    def _load_concern_categories(self) -> list[dict[str, Any]]:
        path = self.project_root / "config" / "concern_categories.yaml"
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        categories = payload.get("categories", [])
        if not isinstance(categories, list):
            return []
        return [category for category in categories if isinstance(category, dict)]

    def _load_analysis_rules(self) -> dict[str, Any]:
        path = self.project_root / "config" / "analysis_rules.yaml"
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return payload if isinstance(payload, dict) else {}

    def _category_keywords(self, category: dict[str, Any]) -> set[str]:
        configured = category.get("keywords", [])
        keywords = configured if isinstance(configured, list) else []
        fallback = [category.get("id", ""), category.get("label", ""), category.get("description", "")]
        return set(self._tokenize(" ".join([*map(str, keywords), *map(str, fallback)])))

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return [token.lower() for token in TOKEN_RE.findall(text or "")]

    @staticmethod
    def _lower_list(values: Any) -> set[str]:
        if not isinstance(values, list):
            return set()
        return {str(value).lower() for value in values if str(value).strip()}

    def _keyword_hits(self, text: str, tokens: set[str], values: Any) -> list[str]:
        if not isinstance(values, list):
            return []
        text_lower = (text or "").lower()
        hits = set()
        for value in values:
            keyword = str(value).strip().lower()
            if not keyword:
                continue
            if " " in keyword:
                if keyword in text_lower:
                    hits.add(keyword)
            elif keyword in tokens:
                hits.add(keyword)
        return sorted(hits)

    @staticmethod
    def _rating_score(rating: str) -> int:
        try:
            value = float(rating)
        except (TypeError, ValueError):
            return 0
        if value >= 4:
            return 1
        if value <= 2:
            return -1
        return 0

    @staticmethod
    def _number(value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _avg(values: list[float]) -> float:
        values = [value for value in values if value is not None]
        return round(sum(values) / len(values), 4) if values else 0.0

    @staticmethod
    def _count_label(rows: list[dict[str, Any]], label: str) -> int:
        return sum(1 for row in rows if row.get("sentiment_label") == label)

    @staticmethod
    def _sentiment_score(label: str) -> int:
        if label == "positive":
            return 1
        if label == "negative":
            return -1
        return 0

    @staticmethod
    def _parse_datetime(value: Any) -> datetime | None:
        if not value:
            return None
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return None
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed

    def _latest_datetime(self, rows: list[dict[str, Any]]) -> datetime | None:
        dates = [self._parse_datetime(row.get("posted_at")) for row in rows]
        dates = [date for date in dates if date is not None]
        return max(dates) if dates else None

    @staticmethod
    def _stable_id(*parts: Any) -> str:
        payload = json.dumps(parts, ensure_ascii=False, sort_keys=True, default=str)
        import hashlib

        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _write_csv(self, path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
        with path.open("w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            for row in rows:
                writer.writerow({field: self._csv_value(row.get(field)) for field in fields})

    @staticmethod
    def _csv_value(value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False, sort_keys=True)
        return str(value)
