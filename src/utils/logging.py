from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


SCRAPE_RUN_FIELDS = [
    "run_id",
    "platform",
    "brand_or_competitor",
    "source_account",
    "actor_id",
    "input_json",
    "dataset_id",
    "records_count",
    "status",
    "error_message",
]

RAW_RECORD_FIELDS = [
    "run_id",
    "platform",
    "brand_or_competitor",
    "source_account",
    "actor_id",
    "dataset_id",
    "record_index",
    "record_key",
    "raw_file_path",
]


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: Any) -> None:
    ensure_parent(path)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")


def append_csv_row(path: Path, fieldnames: list[str], row: dict[str, Any]) -> None:
    ensure_parent(path)
    write_header = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow({field: _format_csv_value(row.get(field, "")) for field in fieldnames})


def append_scrape_run(path: Path, row: dict[str, Any]) -> None:
    append_csv_row(path, SCRAPE_RUN_FIELDS, row)


def append_raw_record_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        ensure_parent(path)
        if not path.exists():
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=RAW_RECORD_FIELDS)
                writer.writeheader()
        return
    for row in rows:
        append_csv_row(path, RAW_RECORD_FIELDS, row)


def _format_csv_value(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=True, sort_keys=True)
    if value is None:
        return ""
    return str(value)
