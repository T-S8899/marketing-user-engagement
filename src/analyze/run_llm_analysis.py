from __future__ import annotations

import sys

from src.analyze.llm_analysis import OptionalLlmAnalyzer


def main() -> int:
    try:
        outputs = OptionalLlmAnalyzer().run()
    except Exception as exc:
        print(f"LLM analysis failed: {exc}", file=sys.stderr)
        return 1

    print(
        f"LLM analysis {outputs.status}: {outputs.processed_count} rows, "
        f"{outputs.cache_hits} cache hits, {outputs.errors_count} errors -> {outputs.comments_path}"
    )
    print(f"LLM summary -> {outputs.summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
