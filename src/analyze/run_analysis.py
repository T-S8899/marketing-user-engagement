from __future__ import annotations

import sys

from src.analyze.marketing_analysis import MarketingAnalyzer


def main() -> int:
    try:
        outputs = MarketingAnalyzer().run()
    except Exception as exc:
        print(f"Analysis failed: {exc}", file=sys.stderr)
        return 1

    print(f"Analyzed {outputs.comments_count} comments -> {outputs.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
