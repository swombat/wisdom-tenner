// Build the full-text search index from the rendered site.
//
// The index is what makes the book a network of thought rather than a pile of
// pages: every page, article, thought and story is searchable by any word in
// it. We read the *rendered* HTML rather than the Markdown so that what is
// searched is exactly what a reader can see.

import { readdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";

const SITE = path.resolve("_site");
const PREFIX = (() => {
  const value = process.env.SITE_PREFIX || "/";
  if (value === "/") return "/";
  return `/${value.replace(/^\/|\/$/g, "")}/`;
})();

async function htmlFiles(dir) {
  const found = [];
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) found.push(...(await htmlFiles(full)));
    else if (entry.name.endsWith(".html")) found.push(full);
  }
  return found;
}

const stripTags = (html) =>
  html
    .replace(/<(script|style)\b[^>]*>[\s\S]*?<\/\1>/gi, " ")
    .replace(/<[^>]+>/g, " ");

const decode = (text) =>
  text
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#(\d+);/g, (_m, code) => String.fromCodePoint(Number(code)))
    .replace(/&[a-z]+;/gi, " ");

const tidy = (text) => decode(stripTags(text)).replace(/\s+/g, " ").trim();

const entries = [];

for (const file of (await htmlFiles(SITE)).sort()) {
  const html = await readFile(file, "utf8");

  const relative = path.relative(SITE, file).split(path.sep).join("/");
  if (relative === "404.html") continue;
  const url = PREFIX + relative.replace(/(^|\/)index\.html$/, "$1");

  const main = html.match(/<main\b[^>]*>([\s\S]*?)<\/main>/i);
  // The search box itself and the repeated page furniture are not content.
  const inner = (main ? main[1] : html)
    .replace(/<div class="site-search"[\s\S]*?<\/div>\s*<\/div>/i, " ")
    .replace(/<header\b[^>]*>[\s\S]*?<\/header>/gi, " ");
  const body = tidy(inner);
  if (!body) continue;

  const heading = html.match(/<h1\b[^>]*>([\s\S]*?)<\/h1>/i);
  const titleTag = html.match(/<title\b[^>]*>([\s\S]*?)<\/title>/i);
  const title = tidy(heading ? heading[1] : titleTag ? titleTag[1] : relative);

  const eyebrow = html.match(/<p class="eyebrow">([\s\S]*?)<\/p>/i);

  entries.push({
    u: url,
    t: title,
    k: eyebrow ? tidy(eyebrow[1]) : "",
    b: body,
  });
}

const out = path.join(SITE, "search-index.json");
await writeFile(out, JSON.stringify(entries), "utf8");

const bytes = JSON.stringify(entries).length;
console.log(
  `[search] indexed ${entries.length} pages, ${(bytes / 1024).toFixed(0)} KB -> ${path.relative(process.cwd(), out)}`,
);
