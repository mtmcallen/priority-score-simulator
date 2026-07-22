#!/usr/bin/env python3
"""Local server for the Prisma ambient listening metrics dashboard."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

DOCS = Path(__file__).resolve().parent
DEFAULT_PORT = 8765
_BUILD_SLIDE = None


def get_build_slide():
    global _BUILD_SLIDE
    if _BUILD_SLIDE is None:
        spec = importlib.util.spec_from_file_location(
            "generate_prisma_ambient_metrics_slide",
            DOCS / "generate-prisma-ambient-metrics-slide.py",
        )
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        sys.path.insert(0, str(DOCS))
        spec.loader.exec_module(module)
        _BUILD_SLIDE = module.build_slide
    return _BUILD_SLIDE


class DashboardHandler(BaseHTTPRequestHandler):

    def log_message(self, fmt: str, *args) -> None:
        if self.path != "/favicon.ico":
            super().log_message(fmt, *args)

    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html"):
            self._serve_file(DOCS / "prisma-ambient-metrics-dashboard.html", "text/html; charset=utf-8")
            return
        if path == "/prisma-ambient-metrics-dashboard.js":
            self._serve_file(DOCS / "prisma-ambient-metrics-dashboard.js", "application/javascript; charset=utf-8")
            return
        if path == "/health":
            self._json_response(200, {"ok": True})
            return
        self.send_error(404)

    def do_POST(self) -> None:
        if self.path != "/api/pptx":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", 0))
        payload = json.loads(self.rfile.read(length).decode("utf-8"))
        csv_text = payload.get("csv") or ""
        care_provider = payload.get("careProvider") or payload.get("care_provider") or None
        rounder = payload.get("rounder") or None
        unit = payload.get("unit") or None
        if care_provider == "":
            care_provider = None
        if rounder == "":
            rounder = None
        if unit == "":
            unit = None
        if not csv_text.strip():
            self._json_response(400, {"error": "Missing CSV data"})
            return

        tmp_path = None
        out_path = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as tmp:
                tmp.write(csv_text)
                tmp_path = Path(tmp.name)
            with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as out:
                out_path = Path(tmp.name)
            _, _ = get_build_slide()(
                tmp_path,
                care_provider=care_provider,
                rounder=rounder,
                unit=unit,
                output_path=out_path,
            )
            data = out_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/vnd.openxmlformats-officedocument.presentationml.presentation")
            self.send_header("Content-Disposition", 'attachment; filename="prisma-health-ambient-listening-metrics.pptx"')
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except Exception as exc:  # noqa: BLE001
            self._json_response(500, {"error": str(exc)})
        finally:
            if tmp_path and tmp_path.exists():
                tmp_path.unlink(missing_ok=True)
            if out_path and out_path.exists():
                out_path.unlink(missing_ok=True)

    def _serve_file(self, path: Path, content_type: str) -> None:
        if not path.exists():
            self.send_error(404)
            return
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _json_response(self, code: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    server = HTTPServer(("127.0.0.1", port), DashboardHandler)
    url = f"http://127.0.0.1:{port}/"
    print(f"Prisma AL Metrics Dashboard running at {url}")
    print("Press Ctrl+C to stop.")
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
