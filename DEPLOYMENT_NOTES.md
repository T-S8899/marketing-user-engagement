# Temporary GitHub Pages Preview

The root-level `index.html`, `announcement.html`, and `internal_insights.html` files are a temporary GitHub Pages preview copy for quick stakeholder navigation and MVP demos.

The original project structure remains the source of truth:

- Frontend source: `frontend/`
- Python pipeline and dashboard server code: `src/`
- Prepared data: `data/`
- Project configuration: `config/`

These root files use a browser `<base href="./frontend/">` tag so they resolve assets and modules from `frontend/src/` while the original source folders stay unmoved and unrewritten. Future production hosting should use the original structured source/build setup instead of treating the repository root as the application source.

If the frontend entry files or asset paths change, regenerate or recopy the root preview files from the source structure before sharing the GitHub Pages URL again.
