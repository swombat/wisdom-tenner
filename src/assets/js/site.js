const button = document.querySelector(".menu-button");
const navigation = document.querySelector(".site-nav");

if (button && navigation) {
  button.addEventListener("click", () => {
    const open = button.getAttribute("aria-expanded") === "true";
    button.setAttribute("aria-expanded", String(!open));
    navigation.classList.toggle("is-open", !open);
  });
}

// Drop cap: mark the first *text* paragraph of an essay (skip image-only
// paragraphs and paragraphs too short or oddly-started to carry a cap).
const essay = document.querySelector(".prose--essay");
if (essay) {
  const paragraphs = essay.querySelectorAll(":scope > p");
  for (const p of paragraphs) {
    const text = p.textContent.trim();
    if (!text || p.querySelector("img")) continue;
    if (text.length > 80 && /^[A-Za-z“"]/.test(text)) {
      p.classList.add("has-dropcap");
    }
    break;
  }
}

// Search: type a keyword or phrase and find every page that carries it.
// The index is fetched only when someone actually searches.
const searchBox = document.querySelector(".site-search");

if (searchBox) {
  const form = searchBox.querySelector("form");
  const input = searchBox.querySelector(".site-search-input");
  const output = searchBox.querySelector(".site-search-results");
  const indexUrl = searchBox.dataset.index;

  let index = null;
  let loading = null;

  const loadIndex = () => {
    if (index) return Promise.resolve(index);
    if (!loading) {
      loading = fetch(indexUrl)
        .then((response) => {
          if (!response.ok) throw new Error(String(response.status));
          return response.json();
        })
        .then((data) => {
          index = data;
          return index;
        });
    }
    return loading;
  };

  const escapeHtml = (value) =>
    value.replace(
      /[&<>"]/g,
      (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c],
    );

  // One snippet of surrounding sentence, with the searched words marked.
  const snippet = (body, terms) => {
    const haystack = body.toLowerCase();
    let at = -1;
    for (const term of terms) {
      const found = haystack.indexOf(term);
      if (found !== -1 && (at === -1 || found < at)) at = found;
    }
    if (at === -1) return "";
    let start = Math.max(0, at - 90);
    let end = Math.min(body.length, at + 190);
    if (start > 0) start = body.indexOf(" ", start) + 1;
    if (end < body.length) end = body.lastIndexOf(" ", end);
    let text = escapeHtml(body.slice(start, end));
    for (const term of terms) {
      const pattern = new RegExp(
        `(${term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`,
        "gi",
      );
      text = text.replace(pattern, "<mark>$1</mark>");
    }
    return `${start > 0 ? "…" : ""}${text}${end < body.length ? "…" : ""}`;
  };

  const render = (query) => {
    const terms = query
      .toLowerCase()
      .split(/\s+/)
      .map((term) => term.trim())
      .filter(Boolean);

    if (!terms.length) {
      output.innerHTML = "";
      return;
    }

    const hits = [];
    for (const entry of index) {
      const body = `${entry.t} ${entry.b}`.toLowerCase();
      if (!terms.every((term) => body.includes(term))) continue;
      let score = 0;
      for (const term of terms) {
        score += body.split(term).length - 1;
        if (entry.t.toLowerCase().includes(term)) score += 40;
      }
      hits.push({ entry, score });
    }

    hits.sort((a, b) => b.score - a.score);

    if (!hits.length) {
      output.innerHTML = `<p class="site-search-empty">Nothing here carries ${escapeHtml(query)}. Try one word instead of several, or a different spelling.</p>`;
      return;
    }

    const list = hits
      .slice(0, 40)
      .map(({ entry }) => {
        const kind = entry.k
          ? `<span class="site-search-kind">${escapeHtml(entry.k)}</span>`
          : "";
        const line = snippet(entry.b, terms);
        return `<li><a href="${entry.u}"><span class="site-search-title">${escapeHtml(entry.t)}</span>${kind}</a><p class="site-search-snippet">${line}</p></li>`;
      })
      .join("");

    const counted =
      hits.length === 1
        ? "One page carries it."
        : `${hits.length} pages carry it${hits.length > 40 ? "; the closest forty are shown" : ""}.`;

    output.innerHTML = `<p class="site-search-count">${counted}</p><ol class="site-search-list">${list}</ol>`;
  };

  const run = (query) => {
    if (!query.trim()) {
      output.innerHTML = "";
      return;
    }
    output.innerHTML = `<p class="site-search-count">Looking…</p>`;
    loadIndex()
      .then(() => render(query))
      .catch(() => {
        output.innerHTML = `<p class="site-search-empty">The search index could not be loaded. Please reload the page and try again.</p>`;
      });
  };

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    run(input.value);
  });

  input.addEventListener("focus", loadIndex, { once: true });

  const asked = new URLSearchParams(window.location.search).get("q");
  if (asked) {
    input.value = asked;
    run(asked);
  }
}
