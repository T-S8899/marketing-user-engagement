from __future__ import annotations

import sys

from src.reports.report_builder import MarkdownReportBuilder


def main() -> int:
    try:
        result = MarkdownReportBuilder().build_all()
    except Exception as exc:
        print(f"Report generation failed: {exc}", file=sys.stderr)
        return 1

    print(f"Generated {len(result.reports)} reports -> {result.reports_dir}")
    for path in result.reports:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
