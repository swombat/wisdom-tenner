const button = document.querySelector(".menu-button");
const navigation = document.querySelector(".site-nav");

if (button && navigation) {
  button.addEventListener("click", () => {
    const open = button.getAttribute("aria-expanded") === "true";
    button.setAttribute("aria-expanded", String(!open));
    navigation.classList.toggle("is-open", !open);
  });
}
