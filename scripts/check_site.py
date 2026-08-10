#!/usr/bin/env python3
"""Check the built static site for missing migrated pages, links, and assets."""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
MANIFEST = ROOT / "migration-manifest.json"
STORIES = ROOT / "src" / "content" / "stories"


class ReferenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.references: list[str] = []
        self.figure_stack: list[dict[str, int]] = []
        self.figure_issues: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "figure":
            self.figure_stack.append({"images": 0, "captions": 0})
        elif tag == "img" and self.figure_stack:
            self.figure_stack[-1]["images"] += 1
        elif tag == "figcaption" and self.figure_stack:
            self.figure_stack[-1]["captions"] += 1

        for name, value in attrs:
            if name in {"href", "src"} and value:
                self.references.append(value)

    def handle_endtag(self, tag: str) -> None:
        if tag != "figure":
            return
        if not self.figure_stack:
            self.figure_issues.append("closing figure without opening figure")
            return
        figure = self.figure_stack.pop()
        if figure != {"images": 1, "captions": 1}:
            self.figure_issues.append(
                f"figure contains {figure['images']} images and "
                f"{figure['captions']} captions"
            )


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

    story_numbers: dict[int, Path] = {}
    for story_file in STORIES.glob("*.md"):
        source = story_file.read_text(encoding="utf-8")
        number_match = re.search(r"^story_number:\s*(\d+)\s*$", source, re.MULTILINE)
        if not number_match:
            continue
        number = int(number_match.group(1))
        if number in story_numbers:
            problems.append(
                f"duplicate story_number {number}: "
                f"{story_numbers[number].name} and {story_file.name}"
            )
        story_numbers[number] = story_file

        permalink_match = re.search(r"^permalink:\s*(\S+)\s*$", source, re.MULTILINE)
        if not permalink_match:
            problems.append(f"numbered story has no permalink: {story_file.name}")
        else:
            expected.add(permalink_match.group(1))

    missing_story_numbers = sorted(set(range(1, 112)) - set(story_numbers))
    if missing_story_numbers:
        problems.append(f"missing canonical story numbers: {missing_story_numbers}")

    for permalink in sorted(expected):
        target = target_for_url(permalink)
        if target and not target.exists():
            problems.append(f"missing migrated page: {permalink} -> {target.relative_to(ROOT)}")

    html_files = sorted(SITE.rglob("*.html"))
    checked_links = 0
    for html_file in html_files:
        parser = ReferenceParser()
        parser.feed(html_file.read_text(encoding="utf-8"))
        for issue in parser.figure_issues:
            problems.append(f"invalid figure in {html_file.relative_to(SITE)}: {issue}")
        if parser.figure_stack:
            problems.append(f"unclosed figure in {html_file.relative_to(SITE)}")
        for value in parser.references:
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
