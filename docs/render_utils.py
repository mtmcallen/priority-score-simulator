#!/usr/bin/env python3
"""Shared helpers for rendering branded docs with system Chrome or Playwright."""

from __future__ import annotations

import subprocess
from pathlib import Path

CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
DARK_ANCHOR = "#2d2660"


def chrome_available() -> bool:
    return CHROME.exists()


def render_logo_png(svg_path: Path, out_path: Path, size: int = 112) -> None:
    """Render the logo mark to a transparent PNG for use on dark backgrounds."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    padding = 4
    viewport = size + padding * 2
    html = f"""<!DOCTYPE html>
<html>
  <head>
    <style>
      html, body {{
        margin: 0;
        width: {viewport}px;
        height: {viewport}px;
        background: {DARK_ANCHOR};
      }}
      img {{
        display: block;
        width: {size}px;
        height: {size}px;
        margin: {padding}px;
      }}
    </style>
  </head>
  <body>
    <img src="{svg_path.as_uri()}" alt="">
  </body>
</html>"""

    wrapper = out_path.parent / f".{out_path.stem}-render.html"
    wrapper.write_text(html, encoding="utf-8")

    if chrome_available():
        subprocess.run(
            [
                str(CHROME),
                "--headless=new",
                "--disable-gpu",
                "--hide-scrollbars",
                f"--window-size={viewport},{viewport}",
                f"--screenshot={out_path}",
                wrapper.as_uri(),
            ],
            check=True,
            capture_output=True,
        )
    else:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page(viewport={"width": viewport, "height": viewport})
            page.set_content(html)
            page.screenshot(path=str(out_path))
            browser.close()

    _strip_dark_fringe(out_path, DARK_ANCHOR)


def _strip_dark_fringe(png_path: Path, bg_hex: str) -> None:
    from PIL import Image

    bg = tuple(int(bg_hex[i : i + 2], 16) for i in (1, 3, 5))
    img = Image.open(png_path).convert("RGBA")
    pixels = img.load()
    tolerance = 24
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = pixels[x, y]
            if (
                abs(r - bg[0]) <= tolerance
                and abs(g - bg[1]) <= tolerance
                and abs(b - bg[2]) <= tolerance
            ):
                pixels[x, y] = (r, g, b, 0)
    img.save(png_path)


def render_file_to_pdf(html_path: Path, out_path: Path) -> None:
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(channel="chrome")
            page = browser.new_page()
            page.goto(html_path.as_uri(), wait_until="networkidle")
            page.emulate_media(media="print")
            content_height = page.evaluate("() => document.documentElement.scrollHeight")
            printable_height = 1056 - int(0.4 * 96) - int(0.32 * 96)
            scale = min(1.0, printable_height / content_height) if content_height > printable_height else 1.0
            page.pdf(
                path=str(out_path),
                format="Letter",
                print_background=True,
                margin={"top": "0.4in", "right": "0.38in", "bottom": "0.32in", "left": "0.38in"},
                scale=scale,
            )
            browser.close()
        return
    except Exception:
        pass

    if chrome_available():
        subprocess.run(
            [
                str(CHROME),
                "--headless=new",
                "--disable-gpu",
                "--no-pdf-header-footer",
                f"--print-to-pdf={out_path}",
                html_path.as_uri(),
            ],
            check=True,
            capture_output=True,
        )
        return

    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.goto(html_path.as_uri(), wait_until="networkidle")
        page.emulate_media(media="print")
        page.pdf(
            path=str(out_path),
            format="Letter",
            print_background=True,
            margin={"top": "0.4in", "right": "0.38in", "bottom": "0.32in", "left": "0.38in"},
        )
        browser.close()
