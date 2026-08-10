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
