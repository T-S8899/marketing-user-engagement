from __future__ import annotations

import argparse
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from src.utils.config import PROJECT_ROOT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serve the local dashboard.")
    parser.add_argument("--host", default="localhost", help="Host to bind. Defaults to localhost.")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind. Defaults to 8000.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    handler = partial(SimpleHTTPRequestHandler, directory=str(PROJECT_ROOT))
    try:
        server = ThreadingHTTPServer((args.host, args.port), handler)
    except OSError as exc:
        print(f"Dashboard server failed to start on {args.host}:{args.port}: {exc}", file=sys.stderr)
        return 1

    url = f"http://{args.host}:{args.port}/frontend/"
    print(f"Dashboard server running at {url}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard server stopped.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
