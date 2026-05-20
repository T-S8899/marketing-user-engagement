from __future__ import annotations

import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from src.utils.config import PROJECT_ROOT


REPORT_FILES = {
    "executive_summary": "executive_summary.md",
    "top_concerns": "top_concerns_report.md",
    "sentiment_trust": "sentiment_trust_report.md",
    "brand_vs_competitors": "brand_vs_competitors_report.md",
    "platform": "platform_report.md",
    "emerging_concerns": "emerging_concerns_report.md",
    "marketing_opportunities": "marketing_opportunities_report.md",
    "content_ideas": "content_ideas_report.md",
    "escalation": "escalation_report.md",
    "data_quality": "data_quality_report.md",
}

INPUT_FILES = {
    "market_comments": "data/processed/market_comments.csv",
    "comment_analysis": "data/analysis/comment_analysis.csv",
    "concern_summary": "data/analysis/concern_category_summary.csv",
    "sentiment_summary": "data/analysis/sentiment_summary.csv",
    "platform_summary": "data/analysis/platform_summary.csv",
    "brand_summary": "data/analysis/brand_competitor_summary.csv",
    "keyword_summary": "data/analysis/keyword_summary.csv",
    "emerging_concerns": "data/analysis/emerging_concerns.csv",
    "urgent_comments": "data/analysis/urgent_comments.csv",
    "marketing_opportunities": "data/analysis/marketing_opportunities.csv",
    "content_ideas": "data/analysis/content_ideas.csv",
    "escalation_items": "data/analysis/escalation_items.csv",
}


@dataclass(frozen=True)
class ReportBuildResult:
    reports_dir: Path
    reports: list[Path]


class MarkdownReportBuilder:
    def __init__(self, project_root: Path = PROJECT_ROOT) -> None:
        self.project_root = project_root
        self.reports_dir = project_root / "data" / "reports"
        self.data = {name: self._read_csv(project_root / path) for name, path in INPUT_FILES.items()}
        self.categories = self._load_categories()
        self.brands = self._load_brands()
        self.generated_at = datetime.now(timezone.utc).isoformat()

    def build_all(self) -> ReportBuildResult:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        report_map = {
            "executive_summary": self.executive_summary(),
            "top_concerns": self.top_concerns_report(),
            "sentiment_trust": self.sentiment_trust_report(),
            "brand_vs_competitors": self.brand_vs_competitors_report(),
            "platform": self.platform_report(),
            "emerging_concerns": self.emerging_concerns_report(),
            "marketing_opportunities": self.marketing_opportunities_report(),
            "content_ideas": self.content_ideas_report(),
            "escalation": self.escalation_report(),
            "data_quality": self.data_quality_report(),
        }
        paths: list[Path] = []
        for key, content in report_map.items():
            path = self.reports_dir / REPORT_FILES[key]
            path.write_text(content, encoding="utf-8")
            paths.append(path)
        return ReportBuildResult(self.reports_dir, paths)

    def executive_summary(self) -> str:
        comments = self.comments
        risks = [row for row in self._top_risk_categories(5) if int(row.get("count", 0)) > 0]
        opportunities = self.data["marketing_opportunities"][:5]
        urgent = self.escalations[:5]
        mood = self._market_mood()
        trend = self._comment_trend()
        next_action = self._next_marketing_action(risks, opportunities)
        return self._report(
            "Executive Summary",
            [
                self._kv_section(
                    "Key Answers",
                    [
                        ("What changed?", trend),
                        ("What are customers saying?", mood),
                        ("What are the top risks?", self._join_labels(risks, "label")),
                        ("What are the top opportunities?", self._join_labels(opportunities, "keyword", fallback_key="concern_category_label")),
                        ("What should marketing do next?", next_action),
                        ("What needs escalation outside marketing?", self._join_labels(urgent, "concern_category_label")),
                    ],
                ),
                self._evidence_section("Evidence excerpts", comments[:5]),
                self._limitations(),
            ],
        )

    def top_concerns_report(self) -> str:
        rows = self._top_risk_categories(5)
        return self._report(
            "Top Concerns Report",
            [
                "## Frequency Ranking\n\n" + self._table(
                    ["Rank", "Category", "Arabic label", "Count", "Share", "Sentiment split", "Recommended action", "Escalation owner"],
                    [
                        [
                            index + 1,
                            row.get("label", ""),
                            row.get("label_ar", ""),
                            row.get("count", 0),
                            self._share(row.get("count", 0), len(self.comments)),
                            self._sentiment_text(row.get("sentiment", {})),
                            row.get("recommended_action", ""),
                            row.get("escalation_team", ""),
                        ]
                        for index, row in enumerate(rows)
                    ],
                ),
                self._category_evidence(rows),
                self._limitations(),
            ],
        )

    def sentiment_trust_report(self) -> str:
        trust_rows = self._category_group_comments("credibility")[:10]
        negative_rows = [row for row in self.comments if row.get("sentiment_label") == "negative"][:10]
        return self._report(
            "Sentiment & Trust Report",
            [
                "## Overall Sentiment\n\n" + self._summary_table(self.data["sentiment_summary"], ["label", "comments_count", "share_of_total", "urgent_count"]),
                "## Sentiment by Platform\n\n" + self._summary_table(self.data["platform_summary"], ["label", "comments_count", "positive_count", "neutral_count", "negative_count", "urgent_count"]),
                "## Sentiment by Brand / Competitor\n\n" + self._summary_table(self.data["brand_summary"], ["label", "comments_count", "positive_count", "neutral_count", "negative_count", "urgent_count"]),
                self._evidence_section("Trust-risk comments", trust_rows),
                self._evidence_section("Negative sentiment evidence", negative_rows),
                self._limitations(),
            ],
        )

    def brand_vs_competitors_report(self) -> str:
        positive_competitor = [row for row in self.comments if row.get("sentiment_label") == "positive" and self._is_competitor(row)][:8]
        negative_competitor = [row for row in self.comments if row.get("sentiment_label") == "negative" and self._is_competitor(row)][:8]
        our_concerns = [row for row in self.comments if not self._is_competitor(row)]
        return self._report(
            "Brand vs Competitors Report",
            [
                "## Sentiment Comparison\n\n" + self._summary_table(self.data["brand_summary"], ["label", "comments_count", "positive_count", "neutral_count", "negative_count", "urgent_count"]),
                "## Our Most Common Concerns\n\n" + self._counter_table(Counter(row.get("concern_category_label") or "unknown" for row in our_concerns), "Concern"),
                self._evidence_section("Competitor strengths", positive_competitor),
                self._evidence_section("Competitor weaknesses", negative_competitor),
                "## Messaging Opportunities\n\n" + self._opportunity_table(self.data["marketing_opportunities"][:10]),
                "## Risks Where Competitors May Outperform Us\n\n" + self._risk_comparison_note(positive_competitor, negative_competitor),
                self._limitations(),
            ],
        )

    def platform_report(self) -> str:
        return self._report(
            "Platform Report",
            [
                "## Volume and Sentiment by Platform\n\n" + self._summary_table(self.data["platform_summary"], ["label", "comments_count", "positive_count", "neutral_count", "negative_count", "urgent_count"]),
                "## Concerns by Platform\n\n" + self._platform_concern_tables(),
                "## Keywords by Platform\n\n" + self._keyword_by_group("platform"),
                "## Platform-Specific Opportunities\n\n" + self._opportunity_table(self.data["content_ideas"][:10]),
                self._limitations(),
            ],
        )

    def emerging_concerns_report(self) -> str:
        rows = self.data["emerging_concerns"]
        return self._report(
            "Emerging Concerns Report",
            [
                "## Emerging Signals\n\n" + self._summary_table(rows, ["concern_category_label", "platform", "comments_count", "confidence", "reason", "recommended_action"]),
                self._evidence_section("Emerging concern evidence", self._examples_from_analysis(rows)),
                self._limitations(),
            ],
        )

    def marketing_opportunities_report(self) -> str:
        return self._report(
            "Marketing Opportunities Report",
            [
                "## Campaign and Positioning Ideas\n\n" + self._opportunity_table(self.data["marketing_opportunities"]),
                "## FAQ and Content Ideas\n\n" + self._opportunity_table(self.data["content_ideas"]),
                "## Objections to Address\n\n" + self._counter_table(Counter(row.get("concern_category_label") or "unknown" for row in self.comments if row.get("sentiment_label") in {"negative", "neutral"}), "Objection / theme"),
                "## Promotional and Service Demand Signals\n\n" + self._summary_table(self.data["keyword_summary"][:20], ["keyword", "comments_count", "platforms", "brands", "urgent_count"]),
                self._limitations(),
            ],
        )

    def content_ideas_report(self) -> str:
        repeated_questions = [row for row in self.comments if "question" in (row.get("keywords") or "").lower()][:10]
        return self._report(
            "Content Ideas / FAQ Report",
            [
                "## Suggested FAQ Entries and Social Posts\n\n" + self._opportunity_table(self.data["content_ideas"]),
                self._evidence_section("Repeated question evidence", repeated_questions),
                "## Suggested Response Templates\n\n" + self._response_templates(),
                self._limitations(),
            ],
        )

    def escalation_report(self) -> str:
        return self._report(
            "Escalation Report",
            [
                "## Urgent Comments\n\n" + self._table(
                    ["Record ID", "Platform", "Category", "Evidence excerpt", "Suggested escalation team", "Recommended next action", "Source"],
                    [
                        [
                            row.get("record_id", ""),
                            row.get("platform", ""),
                            row.get("concern_category_label", ""),
                            self._excerpt(row),
                            self._escalation_team(row),
                            row.get("recommended_action", ""),
                            self._source_ref(row),
                        ]
                        for row in self.escalations[:50]
                    ],
                ),
                self._limitations(),
            ],
        )

    def data_quality_report(self) -> str:
        input_status = [
            [name, INPUT_FILES[name], len(self.data[name]), "available" if (self.project_root / INPUT_FILES[name]).exists() else "missing"]
            for name in INPUT_FILES
        ]
        missing_text = sum(1 for row in self.data["market_comments"] if not row.get("text"))
        missing_sentiment = sum(1 for row in self.comments if not row.get("sentiment_label"))
        missing_category = sum(1 for row in self.comments if not row.get("concern_category_label"))
        return self._report(
            "Data Quality Report",
            [
                "## Input File Status\n\n" + self._table(["Input", "Path", "Rows", "Status"], input_status),
                self._kv_section(
                    "Quality Checks",
                    [
                        ("Processed comments", str(len(self.data["market_comments"]))),
                        ("Analyzed comments", str(len(self.comments))),
                        ("Missing text rows", str(missing_text)),
                        ("Missing sentiment rows", str(missing_sentiment)),
                        ("Missing category rows", str(missing_category)),
                        ("Configured concern categories", str(len(self.categories))),
                    ],
                ),
                self._limitations(),
            ],
        )

    @property
    def comments(self) -> list[dict[str, str]]:
        return self.data["comment_analysis"] or self.data["market_comments"]

    @property
    def escalations(self) -> list[dict[str, str]]:
        return self.data["escalation_items"] or self.data["urgent_comments"] or [row for row in self.comments if row.get("urgency_flag") == "true"]

    def _top_risk_categories(self, limit: int) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for category in self.categories:
            comments = [row for row in self.comments if self._same_category(row, category)]
            sentiment = Counter(row.get("sentiment_label") or "unknown" for row in comments)
            rows.append(
                {
                    **category,
                    "count": len(comments),
                    "sentiment": sentiment,
                    "examples": comments[:3],
                }
            )
        return sorted(rows, key=lambda row: (-int(row.get("count", 0)), int(row.get("dashboard_priority") or 999)))[:limit]

    def _category_evidence(self, rows: list[dict[str, Any]]) -> str:
        sections = []
        for row in rows:
            sections.append(f"## Evidence: {row.get('label', 'Unknown')}\n\n" + self._evidence_table(row.get("examples", [])))
        return "\n\n".join(sections)

    def _category_group_comments(self, group: str) -> list[dict[str, str]]:
        category_ids = {category.get("id") for category in self.categories if category.get("dashboard_group") == group}
        labels = {category.get("label") for category in self.categories if category.get("dashboard_group") == group}
        return [row for row in self.comments if row.get("concern_category_id") in category_ids or row.get("concern_category_label") in labels]

    def _platform_concern_tables(self) -> str:
        grouped: dict[str, Counter[str]] = defaultdict(Counter)
        for row in self.comments:
            grouped[row.get("platform") or "unknown"][row.get("concern_category_label") or "unknown"] += 1
        if not grouped:
            return "_No platform concern data available._"
        return "\n\n".join(f"### {platform}\n\n{self._counter_table(counter, 'Concern')}" for platform, counter in sorted(grouped.items()))

    def _keyword_by_group(self, group_key: str) -> str:
        grouped: dict[str, Counter[str]] = defaultdict(Counter)
        for row in self.comments:
            group = row.get(group_key) or "unknown"
            for keyword in self._split_keywords(row.get("keywords", "")):
                grouped[group][keyword] += 1
        if not grouped:
            return "_No keyword data available._"
        return "\n\n".join(f"### {group}\n\n{self._counter_table(counter, 'Keyword')}" for group, counter in sorted(grouped.items()))

    def _response_templates(self) -> str:
        rows = [
            [category.get("label", ""), category.get("label_ar", ""), category.get("recommended_action", ""), category.get("escalation_team", "")]
            for category in self.categories
        ]
        return self._table(["Theme", "Arabic label", "Suggested response direction", "Owner"], rows)

    def _examples_from_analysis(self, rows: list[dict[str, str]]) -> list[dict[str, str]]:
        examples = []
        for row in rows:
            example_id = row.get("example_record_id")
            match = next((comment for comment in self.comments if comment.get("record_id") == example_id), None)
            examples.append(match or {"record_id": example_id or "", "text": row.get("example_text", ""), "platform": row.get("platform", ""), "concern_category_label": row.get("concern_category_label", "")})
        return examples

    def _market_mood(self) -> str:
        counts = Counter(row.get("sentiment_label") or "unknown" for row in self.comments)
        if not counts:
            return "No analyzed comments are available yet."
        label, count = counts.most_common(1)[0]
        return f"The dominant sentiment signal is {label} ({count} of {len(self.comments)} analyzed comments)."

    def _comment_trend(self) -> str:
        dated = Counter((row.get("posted_at") or "")[:10] for row in self.comments if row.get("posted_at"))
        if len(dated) < 2:
            return "Not enough dated comments are available to describe change over time."
        ordered = sorted(dated.items())
        midpoint = len(ordered) // 2
        previous = sum(count for _date, count in ordered[:midpoint])
        recent = sum(count for _date, count in ordered[midpoint:])
        if recent > previous:
            direction = "increased"
        elif recent < previous:
            direction = "decreased"
        else:
            direction = "stayed stable"
        return f"Comment volume {direction}: recent period {recent}, previous period {previous}."

    def _risk_comparison_note(self, positives: list[dict[str, str]], negatives: list[dict[str, str]]) -> str:
        if not positives and not negatives:
            return "_No competitor-specific evidence is available in the current analysis files._"
        lines = []
        if positives:
            lines.append("- Competitor praise signals should be reviewed before positioning claims are finalized.")
        if negatives:
            lines.append("- Competitor complaint signals can inform differentiation, but claims should stay evidence-based.")
        return "\n".join(lines)

    def _next_marketing_action(self, risks: list[dict[str, Any]], opportunities: list[dict[str, str]]) -> str:
        if risks:
            return risks[0].get("recommended_action", "Review the top traceable risk signal before finalizing messaging.")
        if opportunities:
            return opportunities[0].get("recommended_action", "Review the top traceable opportunity before campaign planning.")
        return "No evidence-backed marketing action is available yet. Run scraping, normalization, and analysis with real comments before making decisions."

    def _opportunity_table(self, rows: list[dict[str, str]]) -> str:
        return self._summary_table(rows, ["type", "keyword", "concern_category_label", "comments_count", "recommended_action", "example_record_id", "example_text"])

    def _summary_table(self, rows: list[dict[str, str]], columns: list[str]) -> str:
        return self._table([self._title(column) for column in columns], [[row.get(column, "") for column in columns] for row in rows])

    def _counter_table(self, counter: Counter[str], label: str, limit: int = 10) -> str:
        return self._table([label, "Count"], [[key, value] for key, value in counter.most_common(limit)])

    def _evidence_section(self, title: str, rows: list[dict[str, str]]) -> str:
        return f"## {title}\n\n" + self._evidence_table(rows)

    def _evidence_table(self, rows: list[dict[str, str]]) -> str:
        return self._table(
            ["Record ID", "Platform", "Category", "Evidence excerpt", "Source"],
            [[row.get("record_id", ""), row.get("platform", ""), row.get("concern_category_label", ""), self._excerpt(row), self._source_ref(row)] for row in rows],
        )

    def _limitations(self) -> str:
        limitations = [
            "Findings are based only on local processed and analysis CSV files available at report generation time.",
            "Small samples, missing dates, missing source URLs, or empty analysis files reduce confidence.",
            "Reports summarize prepared rule-based outputs and do not add unsupported claims beyond the evidence excerpts.",
            "Concern category names, Arabic labels, recommended actions, and owners are loaded from config files.",
        ]
        return "## Data Limitations\n\n" + "\n".join(f"- {item}" for item in limitations)

    def _kv_section(self, title: str, rows: list[tuple[str, str]]) -> str:
        return f"## {title}\n\n" + "\n".join(f"- **{key}:** {value}" for key, value in rows)

    def _report(self, title: str, sections: list[str]) -> str:
        return f"# {title}\n\nGenerated: `{self.generated_at}`\n\n" + "\n\n".join(sections).strip() + "\n"

    def _table(self, headers: list[Any], rows: list[list[Any]]) -> str:
        if not rows:
            return "_No data available._"
        header = "| " + " | ".join(str(item) for item in headers) + " |"
        divider = "| " + " | ".join("---" for _ in headers) + " |"
        body = ["| " + " | ".join(self._cell(value) for value in row) + " |" for row in rows]
        return "\n".join([header, divider, *body])

    def _load_categories(self) -> list[dict[str, Any]]:
        path = self.project_root / "config" / "concern_categories.yaml"
        if not path.exists():
            return []
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        categories = payload.get("categories", [])
        return [category for category in categories if isinstance(category, dict)] if isinstance(categories, list) else []

    def _load_brands(self) -> dict[str, Any]:
        path = self.project_root / "config" / "brands.yaml"
        if not path.exists():
            return {}
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return payload if isinstance(payload, dict) else {}

    def _read_csv(self, path: Path) -> list[dict[str, str]]:
        if not path.exists():
            return []
        with path.open("r", newline="", encoding="utf-8-sig") as handle:
            return list(csv.DictReader(handle))

    def _same_category(self, row: dict[str, str], category: dict[str, Any]) -> bool:
        return row.get("concern_category_id") == category.get("id") or row.get("concern_category_label") == category.get("label")

    def _is_competitor(self, row: dict[str, str]) -> bool:
        row_values = {
            self._normalise_name(row.get("brand_or_competitor", "")),
            self._normalise_name(row.get("brand", "")),
        }
        competitor_values: set[str] = set()
        for competitor in self.brands.get("competitors", []) or []:
            if isinstance(competitor, dict):
                competitor_values.add(self._normalise_name(competitor.get("name", "")))
                competitor_values.add(self._normalise_name(competitor.get("display_name", "")))
        return bool(row_values.intersection(value for value in competitor_values if value))

    def _escalation_team(self, row: dict[str, str]) -> str:
        category = self._category_for_row(row)
        team = category.get("escalation_team") if category else ""
        return self._normalise_team(team)

    def _category_for_row(self, row: dict[str, str]) -> dict[str, Any]:
        return next((category for category in self.categories if self._same_category(row, category)), {})

    def _normalise_team(self, team: str) -> str:
        allowed = {"Customer Care", "Operations", "Finance", "Fleet", "Marketing", "Product"}
        aliases = {
            "Customer Experience": "Customer Care",
            "Finance Operations": "Finance",
            "Fleet Quality": "Fleet",
            "Brand Trust": "Marketing",
            "Review owner": "Marketing",
        }
        normalised = aliases.get(team, team)
        return normalised if normalised in allowed else "Marketing"

    def _sentiment_text(self, sentiment: Counter[str]) -> str:
        return f"positive {sentiment.get('positive', 0)}, neutral {sentiment.get('neutral', 0)}, negative {sentiment.get('negative', 0)}"

    def _share(self, count: Any, total: int) -> str:
        total = total or 1
        return f"{(int(count or 0) / total) * 100:.1f}%"

    def _excerpt(self, row: dict[str, str], limit: int = 220) -> str:
        text = row.get("text") or row.get("example_text") or ""
        return text[: limit - 3] + "..." if len(text) > limit else text

    def _source_ref(self, row: dict[str, str]) -> str:
        return self._first_non_empty(row.get("source_url", ""), row.get("raw_file_path", ""), row.get("raw_record_hash", ""), row.get("record_id", ""))

    def _join_labels(self, rows: list[dict[str, Any]], key: str, fallback_key: str = "label") -> str:
        values = [self._first_non_empty(str(row.get(key, "")), str(row.get(fallback_key, ""))) for row in rows]
        values = [value for value in values if value]
        return ", ".join(values[:5]) if values else "No evidence available."

    @staticmethod
    def _split_keywords(value: str) -> list[str]:
        return [item.strip() for item in value.split(",") if item.strip()]

    @staticmethod
    def _first_non_empty(*values: str) -> str:
        for value in values:
            if value:
                return value
        return ""

    @staticmethod
    def _title(value: str) -> str:
        return value.replace("_", " ").title()

    @staticmethod
    def _cell(value: Any) -> str:
        text = str(value if value is not None else "")
        return text.replace("|", "\\|").replace("\n", " ").strip()

    @staticmethod
    def _normalise_name(value: Any) -> str:
        return str(value or "").strip().lower()
