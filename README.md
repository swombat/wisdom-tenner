# Wisdom, sleeping..

A static, maintainable edition of Michael Tenner's writing at
`wisdom.tenner.org`, migrated from Weebly.

## Editing content

The writing lives in `src/content/` as Markdown files with a short metadata
header. An agent or human editor can change a page with any text editor:

```md
---
title: What is Wisdom?
permalink: /what-is-wisdom.html
layout: page.njk
---

The page text begins here.
```

Keep the `permalink` unchanged unless you deliberately want to change a public
URL. Images live under `src/assets/uploads/`.

## Local preview

```sh
npm install
npm run serve
```

Eleventy prints the local preview address, normally `http://localhost:8080/`.

## Re-importing from Weebly

The importer is retained for provenance and repeatability:

```sh
python3 -m pip install -r requirements-import.txt
npm run import
```

It reads the public sitemap and does not require a Weebly password. Re-importing
overwrites imported content, so commit editorial changes first.

## Refreshing the Nasreddin stories

The complete 111-story collection uses the later Blogspot compilation as its
canonical source:

```sh
python3 -m pip install -r requirements-import.txt
python3 scripts/import_nasredin.py
```

The importer preserves established story permalinks and lead images, updates
the canonical text, and assigns explicit `story_number` metadata. It is safe to
run repeatedly, but—as with any bulk content operation—review and commit local
editorial work first.

## Verification

```sh
npm run build
npm run check
```

The checker validates expected pages, internal links, and local assets in the
built site.

## Deployment

Every push to `main` runs `.github/workflows/pages.yml` and deploys the built
site to GitHub Pages. The workflow currently uses the project-site prefix
`/wisdom-tenner/`; when `wisdom.tenner.org` is moved here, remove
`SITE_PREFIX: /wisdom-tenner/` and add the GitHub Pages custom domain.
