from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

FRONTEND_FILES = [
    "index.html",
    "announcement.html",
    "internal_insights.html",
]

DATA_DIRS = [
    ROOT / "data" / "analysis",
    ROOT / "data" / "processed",
]

CONFIG_FILES = [
    ROOT / "config" / "concern_categories.yaml",
]


def copy_tree(source: Path, destination: Path) -> None:
    if not source.exists():
        return
    shutil.copytree(source, destination, dirs_exist_ok=True)


def copy_file(source: Path, destination: Path) -> None:
    if not source.exists():
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def rewrite_text_file(path: Path, replacements: dict[str, str]) -> None:
    text = path.read_text(encoding="utf-8")
    for old, new in replacements.items():
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    if DOCS.exists():
        shutil.rmtree(DOCS)
    DOCS.mkdir(parents=True)

    for filename in FRONTEND_FILES:
        copy_file(ROOT / "frontend" / filename, DOCS / filename)

    copy_tree(ROOT / "frontend" / "src", DOCS / "src")

    for data_dir in DATA_DIRS:
        copy_tree(data_dir, DOCS / "data" / data_dir.name)

    for config_file in CONFIG_FILES:
        copy_file(config_file, DOCS / "config" / config_file.name)

    copy_file(ROOT / "README.md", DOCS / "README.md")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")

    rewrite_text_file(
        DOCS / "src" / "data" / "adapter.js",
        {
            "../../../data/": "../../data/",
            "../../../config/": "../../config/",
        },
    )
    rewrite_text_file(
        DOCS / "src" / "data" / "rawTables.js",
        {
            'downloadPath: "../data/': 'downloadPath: "data/',
            "../../../data/": "../../data/",
        },
    )
    rewrite_text_file(
        DOCS / "src" / "internal_insights.js",
        {
            "../../data/": "../data/",
        },
    )

    print(f"Built GitHub Pages preview in {DOCS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
