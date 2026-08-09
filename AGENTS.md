# Maintenance guide for agents

This repository is the maintainable source for **Wisdom, sleeping..**

## Where to work

- Essays and main pages: `src/content/pages/`
- Blog posts: `src/content/blog/`
- Short stories: `src/content/stories/`
- Images and downloads: `src/assets/uploads/`
- Site-wide navigation and identity: `src/_data/site.json`
- Layouts: `src/_includes/`
- Visual design: `src/assets/css/site.css`

Content files use Markdown with YAML metadata at the top. Preserve each
`permalink` unless a URL change is explicitly requested.

## Editing rules

1. Make editorial changes in `src/content`, not in `_site`.
2. Do not run the Weebly importer over human-edited files unless the user
   explicitly requests a fresh import. It overwrites imported content.
3. Keep historical wording, spelling, punctuation, and attribution intact
   unless asked to edit them.
4. Put new images under `src/assets/uploads/` and reference them with a
   root-relative path such as `/assets/uploads/example.jpg`.
5. Before publishing, run:

   ```sh
   npm ci
   npm run build
   npm run check
   ```

6. Inspect the changed page in a browser. A successful build alone is not proof
   that typography, images, and links are correct.

## Adding a blog post

Create `src/content/blog/my-post-slug.md`:

```md
---
title: My post title
description: A short summary.
layout: page.njk
permalink: /blog/my-post-slug/
eyebrow: Blog
tags:
  - blog
date: 2026-08-09
published: 2026-08-09
---

Post content goes here.
```

The post will automatically appear on `/blog.html`.

## Adding a story

Use the same structure under `src/content/stories/`, with:

```yaml
permalink: /this-reminds-me-of-a-story/my-story-slug/
eyebrow: This reminds me of a story
tags:
  - story
```

It will automatically appear on the stories index.
