import { renderAnnouncementPage } from "./views/AnnouncementPage.js";

const app = document.querySelector("#announcement-app");
const state = {
  language: "ar",
  selectedFeature: 0,
  brand: {},
  content: null
};

init();

async function init() {
  const [brand, content] = await Promise.all([
    fetchJson("./src/config/brand_config.json", {}),
    fetchJson("./src/config/announcement_content.json", null)
  ]);

  state.brand = brand;
  state.content = content;
  state.language = content?.default_language || "ar";
  app.classList.add(brand.themeClass || "brand-telgani");
  render();
}

function render() {
  app.innerHTML = renderAnnouncementPage({
    brand: state.brand,
    content: state.content,
    language: state.language,
    selectedFeature: state.selectedFeature
  });
  bindInteractions();
}

function bindInteractions() {
  app.querySelectorAll("[data-fallback-image]").forEach((image) => {
    image.addEventListener("error", () => {
      const wrapper = image.parentElement;
      image.hidden = true;
      wrapper?.querySelector(".announcement-logo-text, .announcement-asset-fallback")?.removeAttribute("hidden");
      wrapper?.classList.add("asset-missing");
    }, { once: true });
  });

  app.querySelector("[data-language-toggle]")?.addEventListener("click", () => {
    state.language = state.language === "ar" ? "en" : "ar";
    render();
  });

  app.querySelectorAll("[data-feature-index]").forEach((card) => {
    card.addEventListener("click", () => {
      state.selectedFeature = Number(card.dataset.featureIndex || 0);
      render();
      document.querySelector("#features")?.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  });

  app.querySelectorAll("[data-section-link]").forEach((link) => {
    link.addEventListener("click", () => {
      app.querySelectorAll("[data-section-link]").forEach((item) => item.classList.remove("active"));
      link.classList.add("active");
    });
  });
}

async function fetchJson(path, fallback) {
  try {
    const response = await fetch(path);
    if (!response.ok) throw new Error(path);
    return await response.json();
  } catch (_error) {
    return fallback;
  }
}
