# Temporary GitHub Pages Preview

The root-level `index.html`, `announcement.html`, and `internal_insights.html` files are a temporary GitHub Pages preview copy for quick stakeholder navigation and MVP demos. The root-level `preview-src/` folder is also a temporary preview copy of the frontend runtime files.

The original project structure remains the source of truth:

- Frontend source: `frontend/`
- Python pipeline and dashboard server code: `src/`
- Prepared data: `data/`
- Project configuration: `config/`

These root files load assets and modules from `preview-src/` while the original source folders stay unmoved and unrewritten. Future production hosting should use the original structured source/build setup instead of treating the repository root as the application source.

If the frontend entry files, asset paths, or preview data change, regenerate or recopy the root preview files from the source structure before sharing the GitHub Pages URL again.
