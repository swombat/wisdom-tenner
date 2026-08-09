#!/usr/bin/env python3
"""Import the public Weebly site into agent-friendly Markdown source files."""

from __future__ import annotations

import concurrent.futures
import datetime as dt
import json
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse

import requests
import yaml
from bs4 import BeautifulSoup, Tag
from markdownify import markdownify

ORIGIN = "http://wisdom.tenner.org"
SITEMAP = f"{ORIGIN}/sitemap.xml"
ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "src" / "content"
ASSETS = ROOT / "src" / "assets" / "uploads"
MANIFEST = ROOT / "migration-manifest.json"
TIMEOUT = 45
WORKERS = 10

SESSION = requests.Session()
SESSION.headers.update(
    {
        "User-Agent": (
            "wisdom-tenner-migration/1.0 "
            "(public archival migration; contact: github.com/swombat)"
        )
    }
)


def fetch(url: str) -> requests.Response:
    last_error = None
    for attempt in range(4):
        try:
            response = SESSION.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            return response
        except requests.RequestException as error:
            last_error = error
            if attempt == 3:
                raise
    raise RuntimeError(last_error)


def sitemap_urls() -> list[str]:
    root = ET.fromstring(fetch(SITEMAP).content)
    namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    return [
        element.text
        for element in root.findall(f"{namespace}url/{namespace}loc")
        if element.text
    ]


def normalise_site_url(value: str, page_url: str) -> str:
    absolute = urljoin(page_url, value)
    parsed = urlparse(absolute)
    if parsed.netloc in {"wisdom.tenner.org", "www.wisdom.tenner.org"}:
        path = parsed.path or "/"

        legacy_post = re.fullmatch(
            r"/1/post/\d{4}/\d{2}/([^/]+)\.html",
            path,
        )
        if legacy_post:
            path = f"/blog/{legacy_post.group(1)}/"
        elif re.fullmatch(r"/(?:1|blog)/category/.*", path):
            path = "/blog.html"
        elif path == "/blog/main.php" and parsed.fragment:
            return f"#{parsed.fragment}"
        elif "wisdom.tenner.org/blog/" in path:
            # One source page contains two blog URLs accidentally joined
            # together. Keep the final, valid destination.
            path = "/blog/" + path.rsplit("wisdom.tenner.org/blog/", 1)[1].strip("/") + "/"

        result = path
        if parsed.query and "/uploads/" not in parsed.path:
            result += f"?{parsed.query}"
        if parsed.fragment:
            result += f"#{parsed.fragment}"
        return result
    return absolute


def asset_path(value: str, page_url: str) -> tuple[str, str] | None:
    absolute = urljoin(page_url, value)
    parsed = urlparse(absolute)
    if parsed.netloc not in {"wisdom.tenner.org", "www.wisdom.tenner.org"}:
        return None
    if "/uploads/" not in parsed.path:
        return None
    relative = unquote(parsed.path.split("/uploads/", 1)[1]).lstrip("/")
    return absolute.split("?", 1)[0], f"/assets/uploads/{relative}"


def clean_fragment(fragment: Tag, page_url: str) -> tuple[str, set[tuple[str, str]]]:
    assets: set[tuple[str, str]] = set()

    for selector in [
        "script",
        "style",
        "noscript",
        "form",
        ".blog-social",
        ".blog-comments",
        ".blog-comments-bottom",
        ".blog-post-separator",
        ".blog-separator",
        ".wsite-social",
        ".wsite-spacer",
        ".wsite-button",
    ]:
        for node in fragment.select(selector):
            node.decompose()

    for image in fragment.select("img"):
        source = image.get("data-src") or image.get("src")
        if not source:
            image.decompose()
            continue
        local = asset_path(source, page_url)
        if local:
            assets.add(local)
            image["src"] = local[1]
        else:
            image["src"] = urljoin(page_url, source)
        image.attrs.pop("data-src", None)
        image.attrs.pop("srcset", None)
        image.attrs.pop("style", None)
        image.attrs.pop("width", None)
        image.attrs.pop("height", None)
        if not image.get("alt"):
            image["alt"] = ""

    for anchor in fragment.select("a[href]"):
        local = asset_path(anchor["href"], page_url)
        if local:
            assets.add(local)
            anchor["href"] = local[1]
        else:
            anchor["href"] = normalise_site_url(anchor["href"], page_url)
        anchor.attrs.pop("style", None)
        anchor.attrs.pop("target", None)

    # Weebly uses many layout-only wrappers. Markdown linearises them into a
    # readable document while preserving headings, links, lists, and images.
    text = markdownify(
        str(fragment),
        heading_style="ATX",
        bullets="-",
        strip=["span"],
    )
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip() + "\n", assets


def page_title(soup: BeautifulSoup, path: str) -> str:
    blog_title = soup.select_one(".blog-title")
    if blog_title and blog_title.get_text(" ", strip=True):
        return blog_title.get_text(" ", strip=True)

    heading = soup.select_one("#wsite-content h2.wsite-content-title")
    if heading and heading.get_text(" ", strip=True):
        return heading.get_text(" ", strip=True)

    og_title = soup.select_one('meta[property="og:title"]')
    if og_title and og_title.get("content"):
        return og_title["content"].strip()

    if path in {"/", "/index.html"}:
        return "Wisdom, sleeping.."
    return path.rsplit("/", 1)[-1].replace(".html", "").replace("-", " ").title()


def page_description(soup: BeautifulSoup, body: Tag) -> str:
    meta = soup.select_one('meta[name="description"]')
    value = meta.get("content", "").strip() if meta else ""
    if value and value.lower() not in {"worldly wisdom,", "worldly wisdom"}:
        return value
    text = re.sub(r"\s+", " ", body.get_text(" ", strip=True))
    return (text[:177].rstrip() + "…") if len(text) > 180 else text


def parse_date(soup: BeautifulSoup) -> str | None:
    node = soup.select_one(".blog-date")
    if not node:
        return None
    value = node.get_text(" ", strip=True)
    for pattern in ("%m/%d/%Y", "%d/%m/%Y"):
        try:
            return dt.datetime.strptime(value, pattern).date().isoformat()
        except ValueError:
            pass
    return None


def output_details(path: str) -> tuple[Path, str, str, str]:
    if path.startswith("/blog/"):
        slug = path.removeprefix("/blog/").strip("/")
        return CONTENT / "blog" / f"{slug}.md", f"/blog/{slug}/", "blog", "Blog"
    if path.startswith("/this-reminds-me-of-a-story/"):
        slug = path.removeprefix("/this-reminds-me-of-a-story/").strip("/")
        return (
            CONTENT / "stories" / f"{slug}.md",
            f"/this-reminds-me-of-a-story/{slug}/",
            "story",
            "This reminds me of a story",
        )
    slug = path.strip("/") or "index.html"
    stem = Path(slug).stem
    permalink = "/" if path in {"/", "/index.html"} else path
    return CONTENT / "pages" / f"{stem}.md", permalink, "article", "Essay"


def import_page(index_and_url: tuple[int, str]) -> dict:
    index, url = index_and_url
    path = urlparse(url).path
    response = fetch(url)
    soup = BeautifulSoup(response.text, "html.parser")

    body = soup.select_one("#wsite-content")
    if not body:
        raise RuntimeError(f"No #wsite-content found at {url}")

    title = page_title(soup, path)
    published = parse_date(soup)
    output, permalink, kind, eyebrow = output_details(path)

    if kind in {"blog", "story"}:
        fragment = soup.select_one(".blog-content")
    else:
        fragment = body
        first_title = fragment.select_one(":scope > h2.wsite-content-title")
        if first_title:
            first_title.decompose()

    if not fragment:
        raise RuntimeError(f"No usable content found at {url}")

    description = page_description(soup, fragment)
    markdown, assets = clean_fragment(fragment, url)

    data = {
        "title": title,
        "description": description,
        "layout": "page.njk",
        "permalink": permalink,
        "source_url": url,
        "eyebrow": eyebrow,
        "order": index,
    }
    if kind in {"blog", "story"}:
        data["tags"] = [kind]
    if published:
        data["date"] = published
        data["published"] = published

    if path == "/index.html":
        data["layout"] = "home.njk"
        data["permalink"] = "/"
        data["title"] = "Wisdom, sleeping.."
        data["eyebrow"] = "Worldly wisdom"

    output.parent.mkdir(parents=True, exist_ok=True)
    frontmatter = yaml.safe_dump(
        data,
        allow_unicode=True,
        sort_keys=False,
        width=1000,
    ).strip()
    output.write_text(f"---\n{frontmatter}\n---\n\n{markdown}", encoding="utf-8")

    return {
        "source": url,
        "path": path,
        "output": str(output.relative_to(ROOT)),
        "permalink": data["permalink"],
        "title": data["title"],
        "kind": kind,
        "assets": sorted(assets),
    }


def download_asset(item: tuple[str, str]) -> dict:
    source, public_path = item
    relative = public_path.removeprefix("/assets/uploads/")
    output = ASSETS / relative
    output.parent.mkdir(parents=True, exist_ok=True)
    response = fetch(source)
    output.write_bytes(response.content)
    return {
        "source": source,
        "path": public_path,
        "bytes": len(response.content),
    }


def write_collection_indexes() -> None:
    indexes = {
        CONTENT / "blog-index.md": {
            "title": "Blog",
            "description": "Essays, provocations and notes on the practice of worldly wisdom.",
            "layout": "collection.njk",
            "permalink": "/blog.html",
            "eyebrow": "Reflections",
            "collection_name": "blog",
        },
        CONTENT / "stories-index.md": {
            "title": "This reminds me of a story",
            "description": "Brief stories, parables and jokes that carry more than one meaning.",
            "layout": "collection.njk",
            "permalink": "/this-reminds-me-of-a-story.html",
            "eyebrow": "Stories",
            "collection_name": "stories",
        },
    }
    for output, data in indexes.items():
        output.parent.mkdir(parents=True, exist_ok=True)
        frontmatter = yaml.safe_dump(data, allow_unicode=True, sort_keys=False).strip()
        output.write_text(f"---\n{frontmatter}\n---\n", encoding="utf-8")


def main() -> int:
    urls = sitemap_urls()
    print(f"Found {len(urls)} sitemap URLs.")

    if CONTENT.exists():
        shutil.rmtree(CONTENT)
    CONTENT.mkdir(parents=True)

    # These collection indexes are rebuilt from all individual entries, so the
    # original Weebly index pages are deliberately not imported as duplicate
    # ten-post snapshots.
    skipped = {
        f"{ORIGIN}/blog.html",
        f"{ORIGIN}/this-reminds-me-of-a-story.html",
    }
    import_urls = [url for url in urls if url not in skipped]

    pages = []
    errors = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = {
            executor.submit(import_page, item): item[1]
            for item in enumerate(import_urls)
        }
        for count, future in enumerate(concurrent.futures.as_completed(futures), 1):
            url = futures[future]
            try:
                pages.append(future.result())
                print(f"[{count:>3}/{len(import_urls)}] imported {url}")
            except Exception as error:
                errors.append({"url": url, "error": str(error)})
                print(f"ERROR {url}: {error}", file=sys.stderr)

    write_collection_indexes()

    all_assets = sorted(
        {
            tuple(asset)
            for page in pages
            for asset in page.pop("assets")
        }
    )
    print(f"Downloading {len(all_assets)} referenced local assets.")
    if ASSETS.exists():
        shutil.rmtree(ASSETS)
    ASSETS.mkdir(parents=True)

    downloaded = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = {
            executor.submit(download_asset, asset): asset[0]
            for asset in all_assets
        }
        for count, future in enumerate(concurrent.futures.as_completed(futures), 1):
            source = futures[future]
            try:
                downloaded.append(future.result())
                if count % 25 == 0 or count == len(all_assets):
                    print(f"[{count:>3}/{len(all_assets)}] downloaded assets")
            except Exception as error:
                errors.append({"url": source, "error": str(error)})
                print(f"ERROR asset {source}: {error}", file=sys.stderr)

    pages.sort(key=lambda page: page["source"])
    downloaded.sort(key=lambda asset: asset["source"])
    manifest = {
        "origin": ORIGIN,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "sitemap_urls": len(urls),
        "imported_pages": len(pages),
        "collection_indexes": 2,
        "downloaded_assets": len(downloaded),
        "pages": pages,
        "assets": downloaded,
        "errors": errors,
    }
    MANIFEST.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(
        f"Imported {len(pages)} pages plus 2 collection indexes and "
        f"{len(downloaded)} assets."
    )
    if errors:
        print(f"Import completed with {len(errors)} errors; see {MANIFEST}.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
