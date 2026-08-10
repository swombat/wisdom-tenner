import path from "node:path";

const prefix = (() => {
  const value = process.env.SITE_PREFIX || "/";
  if (value === "/") return "/";
  return `/${value.replace(/^\/|\/$/g, "")}/`;
})();

export default function (eleventyConfig) {
  eleventyConfig.addPassthroughCopy({ "src/assets": "assets" });

  eleventyConfig.addCollection("articles", (api) =>
    api.getFilteredByTag("article").sort((a, b) => a.data.order - b.data.order),
  );
  eleventyConfig.addCollection("blog", (api) =>
    api.getFilteredByTag("blog").sort((a, b) => b.date - a.date),
  );
  eleventyConfig.addCollection("stories", (api) =>
    api
      .getFilteredByTag("story")
      .sort(
        (a, b) =>
          (a.data.story_number ?? Number.MAX_SAFE_INTEGER) -
          (b.data.story_number ?? Number.MAX_SAFE_INTEGER),
      ),
  );

  eleventyConfig.addFilter("readableDate", (value) => {
    const date = value instanceof Date ? value : new Date(value);
    return new Intl.DateTimeFormat("en-GB", {
      day: "numeric",
      month: "long",
      year: "numeric",
      timeZone: "UTC",
    }).format(date);
  });

  eleventyConfig.addFilter("prefixUrl", (value = "/") => {
    if (!value.startsWith("/") || value.startsWith("//")) return value;
    if (prefix === "/") return value;
    return `${prefix.replace(/\/$/, "")}${value}`;
  });

  eleventyConfig.addTransform("project-pages-prefix", function (content) {
    if (prefix === "/" || this.page.outputPath?.endsWith(".xml")) return content;
    if (!this.page.outputPath?.endsWith(".html")) return content;

    return content.replace(
      /\b(href|src)=(["'])\/(?!\/)/g,
      (_match, attribute, quote) =>
        `${attribute}=${quote}${prefix}`,
    );
  });

  return {
    pathPrefix: prefix,
    dir: {
      input: "src",
      output: "_site",
      includes: "_includes",
      data: "_data",
    },
    markdownTemplateEngine: "njk",
    htmlTemplateEngine: "njk",
  };
}
