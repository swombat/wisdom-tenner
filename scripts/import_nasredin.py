#!/usr/bin/env python3
"""Import the canonical 111-story Nasreddin collection from Blogspot.

The Blogspot collection is a single long post. This importer splits it into
maintainable Markdown pages, preserving the existing Wisdom-site permalinks and
lead images for stories that were already migrated from Weebly.
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path

import requests
import yaml
from bs4 import BeautifulSoup, Tag
from markdownify import markdownify


SOURCE_URL = (
    "https://nasredin.blogspot.com/2010/12/"
    "this-reminds-me-of-story-111-teaching.html"
)
STORIES_DIR = Path("src/content/stories")


def compact(text: str) -> str:
    return " ".join(text.replace("\xa0", " ").replace("\u200b", "").split())


def slugify(title: str) -> str:
    ascii_title = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_title.lower()).strip("-")


def split_front_matter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) != 3:
        raise ValueError(f"{path} has no YAML front matter")
    return yaml.safe_load(parts[1]) or {}, parts[2].lstrip()


def leading_media(body: str) -> str:
    """Keep an existing story's lead image or figure."""
    if body.startswith("<figure>"):
        match = re.match(r"(<figure>.*?</figure>)", body, flags=re.DOTALL)
        return match.group(1).strip() if match else ""
    if body.startswith("!["):
        return body.splitlines()[0].strip()
    return ""


def existing_story_map() -> tuple[
    dict[int, tuple[Path, dict, str]],
    dict[int, tuple[Path, dict, str]],
    tuple[Path, dict, str],
]:
    by_order: dict[int, tuple[Path, dict, str]] = {}
    by_number: dict[int, tuple[Path, dict, str]] = {}
    foreword = None
    for path in STORIES_DIR.glob("*.md"):
        data, body = split_front_matter(path)
        if path.name == "foreword.md":
            foreword = (path, data, body)
        if isinstance(data.get("order"), int):
            by_order[data["order"]] = (path, data, body)
        number = data.get("story_number")
        if isinstance(number, int) and 1 <= number <= 111:
            if number in by_number:
                raise RuntimeError(f"Duplicate story_number {number}")
            by_number[number] = (path, data, body)
    if foreword is None:
        raise RuntimeError("Expected src/content/stories/foreword.md")
    return by_order, by_number, foreword


def existing_record_for(
    number: int,
    by_order: dict[int, tuple[Path, dict, str]],
    by_number: dict[int, tuple[Path, dict, str]],
):
    if number in by_number:
        return by_number[number]
    if number == 3 or number >= 74:
        return None
    # The Weebly sequence omitted story 3 and contained one additional story
    # between canonical stories 56 and 57.
    order = 160 - number if number <= 2 or number >= 57 else 161 - number
    return by_order.get(order)


def heading_blocks(post_body: Tag) -> list[tuple[int, str]]:
    blocks = post_body.find_all("div", recursive=False)
    headings = []
    for index, block in enumerate(blocks):
        heading = block.find(
            "span",
            style=lambda value: value and "font-weight: bold" in value,
        )
        if heading:
            title = compact(heading.get_text(" ", strip=True))
            if title:
                headings.append((index, title))
    if len(headings) != 112 or headings[0][1] != "Foreword":
        raise RuntimeError(
            f"Expected Foreword plus 111 stories; found {len(headings)} headings"
        )
    return headings


def segment_markdown(
    blocks: list[Tag], start: int, end: int, *, italicize_first: bool
) -> str:
    fragment = BeautifulSoup(
        "".join(str(block) for block in blocks[start:end]), "html.parser"
    )
    # Blogger expresses emphasis through deeply nested styled spans. Unwrapping
    # those spans avoids malformed Markdown such as overlapping `*` markers.
    # Story introductions are restored as one clean italic paragraph below.
    for span in fragment.find_all("span"):
        span.unwrap()
    for italic in fragment.find_all("i"):
        italic.unwrap()

    text = markdownify(str(fragment), heading_style="ATX")
    text = text.replace("\xa0", " ").replace("\u200b", "")
    text = "\n".join(line.rstrip() for line in text.splitlines())
    paragraphs = [part.strip() for part in re.split(r"\n{2,}", text) if part.strip()]
    if italicize_first and paragraphs:
        paragraphs[0] = f"*{paragraphs[0]}*"
    return "\n\n".join(paragraphs)


def teaser(markdown: str, limit: int = 190) -> str:
    first = markdown.split("\n\n", 1)[0]
    first = re.sub(r"!?\[([^\]]*)\]\([^)]+\)", r"\1", first)
    first = re.sub(r"[*_`>#]", "", first)
    first = compact(first)
    first = re.sub(
        r"\s*This reminds me of a story:\s*$", "", first, flags=re.IGNORECASE
    )
    if len(first) <= limit:
        return first
    return first[:limit].rsplit(" ", 1)[0].rstrip(" ,;:") + "…"


def front_matter(
    *,
    title: str,
    description: str,
    permalink: str,
    story_number: int,
) -> str:
    return "\n".join(
        [
            "---",
            f"title: {json.dumps(title, ensure_ascii=False)}",
            f"description: {json.dumps(description, ensure_ascii=False)}",
            "layout: page.njk",
            f"permalink: {permalink}",
            f"source_url: {SOURCE_URL}",
            "eyebrow: This reminds me of a story",
            f"story_number: {story_number}",
            "hide_published: true",
            "tags:",
            "  - story",
            "---",
        ]
    )


def write_story(
    number: int,
    title: str,
    body: str,
    existing: tuple[Path, dict, str] | None,
) -> Path:
    if existing:
        path, data, old_body = existing
        permalink = data["permalink"]
        media = leading_media(old_body)
    else:
        path = STORIES_DIR / f"{slugify(title)}.md"
        permalink = f"/this-reminds-me-of-a-story/{slugify(title)}/"
        media = ""

    parts = [front_matter(
        title=title,
        description=teaser(body),
        permalink=permalink,
        story_number=number,
    )]
    if media:
        parts.append(media)
    parts.append(body)
    path.write_text("\n\n".join(parts).rstrip() + "\n", encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source-file",
        type=Path,
        help="Read previously downloaded Blogspot HTML instead of fetching it.",
    )
    args = parser.parse_args()

    if args.source_file:
        html = args.source_file.read_text(encoding="utf-8")
    else:
        response = requests.get(SOURCE_URL, timeout=30)
        response.raise_for_status()
        html = response.text

    soup = BeautifulSoup(html, "html.parser")
    post_body = soup.select_one(".post-body")
    if post_body is None:
        raise RuntimeError("Could not find the Blogspot post body")

    blocks = post_body.find_all("div", recursive=False)
    headings = heading_blocks(post_body)
    by_order, by_number, foreword_record = existing_story_map()

    written = []
    for heading_index, (block_index, title) in enumerate(headings):
        next_index = (
            headings[heading_index + 1][0]
            if heading_index + 1 < len(headings)
            else len(blocks)
        )
        body = segment_markdown(
            blocks,
            block_index + 1,
            next_index,
            italicize_first=heading_index > 0,
        )

        if heading_index == 0:
            path, data, old_body = foreword_record
            media = leading_media(old_body)
            content = front_matter(
                title="Foreword",
                description=teaser(body),
                permalink=data["permalink"],
                story_number=0,
            )
            path.write_text(
                "\n\n".join(part for part in (content, media, body) if part).rstrip()
                + "\n",
                encoding="utf-8",
            )
            written.append(path)
            continue

        number = heading_index
        written.append(
            write_story(
                number,
                title,
                body,
                existing_record_for(number, by_order, by_number),
            )
        )

    print(f"Imported Foreword and {len(written) - 1} stories from {SOURCE_URL}")
    print(f"Wrote {len(written)} Markdown files under {STORIES_DIR}")


if __name__ == "__main__":
    main()
