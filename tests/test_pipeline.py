from __future__ import annotations

import csv
import json
import shutil
import unittest
from uuid import uuid4
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from src.analyze.marketing_analysis import COMMENT_ANALYSIS_FIELDS, MarketingAnalyzer
from src.reports.report_builder import MarkdownReportBuilder
from src.scrape.apify_client import ApifyRun
from src.scrape.run_manager import RunManager
from src.structure.normalization import MARKET_COMMENT_FIELDS, MarketCommentsNormalizer
from src.utils.config import get_actor_config


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


@contextmanager
def workspace_tempdir():
    tmp_root = Path(__file__).resolve().parent / ".tmp"
    path = tmp_root / f"case_{uuid4().hex}"
    path.mkdir(parents=True, exist_ok=False)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def write_test_configs(root: Path) -> None:
    (root / "config").mkdir(parents=True, exist_ok=True)
    (root / "config" / "brands.yaml").write_text(
        """
primary_brand:
  name: "telgani"
  display_name: "Telgani"
competitors:
  - name: "rival"
    display_name: "Rival"
platform_targets: {}
""".strip(),
        encoding="utf-8",
    )
    (root / "config" / "concern_categories.yaml").write_text(
        """
categories:
  - id: "poor_slow_customer_service"
    label: "Poor or Slow Customer Service"
    label_ar: "خدمة عملاء ضعيفة أو بطيئة"
    dashboard_priority: 1
    dashboard_group: "service"
    recommended_action: "Clarify response expectations and route repeated support signals."
    escalation_team: "Customer Experience"
    keywords:
      - "support"
      - "slow"
      - "no response"
      - "خدمة"
      - "ما يردون"
  - id: "refund_insurance_fee_issues"
    label: "Refund/Insurance/Fee Issues"
    label_ar: "مشاكل الاسترداد أو التأمين أو الرسوم"
    dashboard_priority: 4
    dashboard_group: "refund"
    recommended_action: "Clarify refund and fee expectations."
    escalation_team: "Finance Operations"
    keywords:
      - "refund"
      - "insurance"
      - "fee"
      - "استرداد"
""".strip(),
        encoding="utf-8",
    )
    (root / "config" / "analysis_rules.yaml").write_text(
        """
sentiment:
  enabled: true
  positive_keywords: ["great", "fast", "excellent", "ممتاز"]
  negative_keywords: ["bad", "slow", "refund", "no response", "سيء"]
urgency:
  enabled: true
  keywords: ["urgent", "no response", "safety", "refund", "ما يردون"]
  min_engagement_for_urgent: 100
  negative_sentiment_is_urgent: false
keywords:
  min_length: 3
  top_n: 50
  stopwords: ["the", "and", "for"]
aggregation:
  top_n_themes: 10
  emerging_recent_days: 7
  emerging_min_recent_count: 1
  emerging_growth_ratio: 1.0
""".strip(),
        encoding="utf-8",
    )


class FakeApifyClient:
    def __init__(self) -> None:
        self.started_inputs: list[tuple[str, dict[str, Any]]] = []

    def start_run(self, actor_id: str, actor_input: dict[str, Any]) -> ApifyRun:
        self.started_inputs.append((actor_id, actor_input))
        return ApifyRun(id="remote-run-1", status="RUNNING", dataset_id="", raw={})

    def wait_for_run(self, run_id: str) -> ApifyRun:
        return ApifyRun(id=run_id, status="SUCCEEDED", dataset_id="dataset-1", raw={})

    def fetch_dataset_items(self, dataset_id: str) -> list[dict[str, Any]]:
        return [{"id": "c1", "text": "خدمة بطيئة", "createdAt": "2026-05-01T10:00:00Z"}]


class PipelineTests(unittest.TestCase):
    def test_apify_run_logging_and_raw_json_preservation(self) -> None:
        with workspace_tempdir() as root:
            brands = {"platform_targets": {"tiktok": [{"brand": "telgani", "account": "telganiapp"}]}}
            actors = {"tiktok": {"comments_actor": "clockworks~tiktok-comments-scraper"}, "defaults": {}}
            client = FakeApifyClient()

            result = RunManager(client, brands, actors, project_root=root).run_platform("tiktok")[0]

            raw_payload = json.loads(result.raw_path.read_text(encoding="utf-8"))
            self.assertEqual(raw_payload[0]["text"], "خدمة بطيئة")
            self.assertTrue((root / "data" / "raw" / "runs" / result.run_id / "run_metadata.json").exists())
            scrape_rows = read_csv(root / "data" / "processed" / "scrape_runs.csv")
            raw_log_rows = read_csv(root / "data" / "processed" / "raw_records_log.csv")
            self.assertEqual(scrape_rows[0]["status"], "SUCCEEDED")
            self.assertEqual(scrape_rows[0]["actor_id"], "clockworks~tiktok-comments-scraper")
            self.assertEqual(raw_log_rows[0]["record_key"], "id:c1")

    def test_actor_config_supports_current_yaml_shape(self) -> None:
        current_shape = {
            "x": {
                "main_actor": "main-x-actor",
                "fallback_replies_actor": "fallback-x-actor",
            },
            "app_store": {"actor": "app-store-actor", "default_input": {"maxReviews": 100}},
        }
        x_config = get_actor_config(current_shape, "x")
        app_config = get_actor_config(current_shape, "app_store")

        self.assertEqual(x_config["actor_id"], "main-x-actor")
        self.assertEqual(x_config["fallback_actor_id"], "fallback-x-actor")
        self.assertEqual(app_config["actor_id"], "app-store-actor")
        self.assertEqual(app_config["input"]["maxReviews"], 100)

    def test_normalization_schema_deduplication_arabic_and_timestamps(self) -> None:
        with workspace_tempdir() as root:
            run_ids = {
                "tiktok": "tiktok_fixture",
                "instagram": "instagram_fixture",
                "x": "x_fixture",
                "app_store": "app_store_fixture",
            }
            for platform, run_id in run_ids.items():
                write_json(
                    root / "data" / "raw" / "runs" / run_id / "run_metadata.json",
                    {
                        "brand": "telgani",
                        "brand_or_competitor": "telgani",
                        "source_account": f"{platform}_account",
                        "created_at": "2026-05-06T00:00:00+00:00",
                    },
                )

            tiktok_record = {
                "id": "tt-1",
                "text": "التأخير في التسليم سيء",
                "createdAt": "2026-05-01T10:00:00Z",
                "url": "https://tiktok.example/video/1",
                "username": "user_tt",
            }
            write_json(root / "data" / "raw" / "tiktok" / "tiktok_fixture.json", [tiktok_record, dict(tiktok_record)])
            write_json(
                root / "data" / "raw" / "instagram" / "instagram_fixture.json",
                [{"commentId": "ig-1", "commentText": "support slow no response", "created_at": "2026-05-02 12:00:00"}],
            )
            write_json(
                root / "data" / "raw" / "x" / "x_fixture.json",
                [{"tweetId": "tw-1", "fullText": "refund issue urgent", "timestamp": "1714567200000", "tweetUrl": "https://x.example/1"}],
            )
            write_json(
                root / "data" / "raw" / "app_store" / "app_store_fixture.json",
                [{"reviewId": "rv-1", "reviewText": "Great app", "date": "05/03/2026", "rating": 5, "appVersion": "1.0"}],
            )

            outputs = MarketCommentsNormalizer(project_root=root).normalize_all()
            rows = read_csv(outputs.market_comments_path)

            self.assertEqual(outputs.records_count, 4)
            self.assertEqual(list(rows[0].keys()), MARKET_COMMENT_FIELDS)
            self.assertEqual(len({row["record_id"] for row in rows}), 4)
            self.assertEqual(len({row["raw_record_hash"] for row in rows}), 4)
            self.assertTrue(any("التأخير" in row["text"] for row in rows))
            self.assertTrue(all(row["posted_at"].endswith("+00:00") for row in rows if row["posted_at"]))
            self.assertEqual(MarketCommentsNormalizer._parse_timestamp("bad-date"), None)
            normalizer = MarketCommentsNormalizer(project_root=root)
            first = normalizer._record_id("x", "source", "comment", "2026-05-01T00:00:00+00:00")
            second = normalizer._record_id("x", "source", "comment", "2026-05-01T00:00:00+00:00")
            self.assertEqual(first, second)

    def test_analysis_outputs_key_schemas_and_groupings(self) -> None:
        with workspace_tempdir() as root:
            write_test_configs(root)
            rows = [
                market_row("r1", "x", "telgani", "slow support no response", "2026-05-01T00:00:00+00:00", likes="5"),
                market_row("r2", "instagram", "telgani", "great fast service", "2026-05-02T00:00:00+00:00"),
                market_row("r3", "app_store", "rival", "refund urgent bad", "2026-05-03T00:00:00+00:00", rating="1"),
                market_row("r4", "tiktok", "telgani", "ما يردون خدمة سيء", "2026-05-04T00:00:00+00:00"),
            ]
            write_csv(root / "data" / "processed" / "market_comments.csv", MARKET_COMMENT_FIELDS, rows)

            MarketingAnalyzer(project_root=root).run()

            analysis_rows = read_csv(root / "data" / "analysis" / "comment_analysis.csv")
            concern_rows = read_csv(root / "data" / "analysis" / "concern_category_summary.csv")
            emerging_rows = read_csv(root / "data" / "analysis" / "emerging_concerns.csv")
            urgent_rows = read_csv(root / "data" / "analysis" / "urgent_comments.csv")
            brand_rows = read_csv(root / "data" / "analysis" / "brand_competitor_summary.csv")
            keyword_rows = read_csv(root / "data" / "analysis" / "keyword_summary.csv")

            self.assertEqual(list(analysis_rows[0].keys()), COMMENT_ANALYSIS_FIELDS)
            self.assertEqual(analysis_rows[0]["concern_category_label"], "Poor or Slow Customer Service")
            self.assertEqual(analysis_rows[0]["sentiment_label"], "negative")
            self.assertTrue(any(row["urgency_flag"] == "true" for row in urgent_rows))
            self.assertEqual(concern_rows[0]["label"], "Poor or Slow Customer Service")
            self.assertIn("opportunity_id", emerging_rows[0].keys())
            self.assertEqual({row["label"] for row in brand_rows}, {"telgani", "rival"})
            self.assertIn("keyword", keyword_rows[0].keys())
            self.assertIn("comments_count", keyword_rows[0].keys())

    def test_report_generation_with_small_fixture_csvs(self) -> None:
        with workspace_tempdir() as root:
            write_test_configs(root)
            comments = [
                market_row("r1", "x", "telgani", "slow support no response", "2026-05-01T00:00:00+00:00"),
                market_row("r2", "app_store", "rival", "refund urgent bad", "2026-05-02T00:00:00+00:00", rating="1"),
            ]
            write_csv(root / "data" / "processed" / "market_comments.csv", MARKET_COMMENT_FIELDS, comments)
            MarketingAnalyzer(project_root=root).run()

            result = MarkdownReportBuilder(project_root=root).build_all()

            self.assertEqual(len(result.reports), 10)
            executive = (root / "data" / "reports" / "executive_summary.md").read_text(encoding="utf-8")
            escalation = (root / "data" / "reports" / "escalation_report.md").read_text(encoding="utf-8")
            self.assertIn("What should marketing do next?", executive)
            self.assertIn("r1", executive)
            self.assertIn("Customer Care", escalation)


def market_row(
    record_id: str,
    platform: str,
    brand: str,
    text: str,
    posted_at: str,
    rating: str = "",
    likes: str = "",
) -> dict[str, str]:
    row = {field: "" for field in MARKET_COMMENT_FIELDS}
    row.update(
        {
            "record_id": record_id,
            "raw_record_hash": f"hash-{record_id}",
            "platform": platform,
            "source_type": "app_review" if platform == "app_store" else "social_comment",
            "scrape_run_id": f"{platform}-run",
            "raw_file_path": f"data/raw/{platform}/{platform}-run.json",
            "raw_record_index": "0",
            "brand": brand,
            "brand_or_competitor": brand,
            "source_account": f"{brand}_account",
            "source_url": f"https://example.com/{record_id}",
            "comment_id": record_id,
            "text": text,
            "posted_at": posted_at,
            "posted_at_raw": posted_at,
            "likes": likes,
            "rating": rating,
            "raw_field_names": "[]",
            "raw_record_json": "{}",
        }
    )
    return row


if __name__ == "__main__":
    unittest.main()
