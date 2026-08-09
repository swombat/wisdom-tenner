#!/usr/bin/env python3
"""Check the built static site for missing migrated pages, links, and assets."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
MANIFEST = ROOT / "migration-manifest.json"


def target_for_url(value: str) -> Path | None:
    parsed = urlparse(value)
    if parsed.scheme or parsed.netloc or value.startswith("#"):
        return None
    path = unquote(parsed.path)
    if not path.startswith("/"):
        return None
    if path == "/":
        return SITE / "index.html"
    target = SITE / path.lstrip("/")
    if target.suffix:
        return target
    return target / "index.html"


def main() -> int:
    if not SITE.exists():
        print("Missing _site; run npm run build first.", file=sys.stderr)
        return 1
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    problems: list[str] = []

    expected = {"/", "/blog.html", "/this-reminds-me-of-a-story.html"}
    for page in manifest["pages"]:
        expected.add(page["permalink"])

    for permalink in sorted(expected):
        target = target_for_url(permalink)
        if target and not target.exists():
            problems.append(f"missing migrated page: {permalink} -> {target.relative_to(ROOT)}")

    html_files = sorted(SITE.rglob("*.html"))
    checked_links = 0
    for html_file in html_files:
        soup = BeautifulSoup(html_file.read_text(encoding="utf-8"), "html.parser")
        for element, attribute in [
            (node, "href") for node in soup.select("[href]")
        ] + [
            (node, "src") for node in soup.select("[src]")
        ]:
            value = element.get(attribute, "")
            target = target_for_url(value)
            if not target:
                continue
            checked_links += 1
            if not target.exists():
                problems.append(
                    f"broken local reference in {html_file.relative_to(SITE)}: {value}"
                )

    print(
        f"Checked {len(expected)} expected URLs, {len(html_files)} HTML files, "
        f"and {checked_links} local references."
    )
    if problems:
        for problem in problems[:100]:
            print(f"ERROR: {problem}", file=sys.stderr)
        if len(problems) > 100:
            print(f"... and {len(problems) - 100} more", file=sys.stderr)
        return 1
    print("Site check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
