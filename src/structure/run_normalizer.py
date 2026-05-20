from __future__ import annotations

import sys

from src.structure.normalization import MarketCommentsNormalizer


def main() -> int:
    try:
        outputs = MarketCommentsNormalizer().normalize_all()
    except Exception as exc:
        print(f"Normalization failed: {exc}", file=sys.stderr)
        return 1

    print(f"market_comments.csv: {outputs.records_count} records -> {outputs.market_comments_path}")
    print(f"posts.csv: {outputs.posts_count} records -> {outputs.posts_path}")
    print(f"sources.csv: {outputs.sources_count} records -> {outputs.sources_path}")
    print(f"normalization_errors.csv: {outputs.errors_count} records -> {outputs.errors_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
