const fallbackContent = {
  locale: "ar-SA",
  default_language: "ar",
  direction: "rtl",
  navLabel: "تنقل صفحة الإعلان",
  brand_name: "Telgani",
  eyebrow_ar: "إطلاق جديد",
  eyebrow_en: "New launch",
  assets: {
    logo_path: "",
    hero_car_image: "",
    hero_sticker_image: ""
  },
  sections: {
    hook: "hook",
    features: "features",
    proof: "proof",
    final_cta: "final-cta"
  },
  nav: [
    { id: "hook", label_ar: "ليش؟", label_en: "Why" },
    { id: "features", label_ar: "الجديد", label_en: "New" },
    { id: "proof", label_ar: "الكروت", label_en: "Cards" }
  ],
  hero: {
    title_ar: "وصلنا لمرحلة جديدة",
    subtitle_ar: "مو تحديث... هذا تحول كامل",
    body_ar: "تجربة أخف وأوضح، مصممة لقرار أسرع بدون زحمة.",
    primary_cta_ar: "جرب الآن",
    secondary_cta_ar: "اكتشف الجديد",
    title_en: "A new stage just landed",
    subtitle_en: "Not an update. A whole shift.",
    body_en: "A cleaner, faster experience built for quicker decisions.",
    primary_cta_en: "Try now",
    secondary_cta_en: "See what is new"
  },
  hooks: [
    { text_ar: "تعبك من الحجز المعقد؟", text_en: "Tired of complicated booking?" },
    { text_ar: "من الأسعار اللي تتغير فجأة؟", text_en: "Prices changing at the last second?" },
    { text_ar: "من الردود المتأخرة؟", text_en: "Slow replies?" },
    { text_ar: "خلصنا هذا كله.", text_en: "We cleaned that up." }
  ],
  features: [
    {
      title_ar: "أسرع حجز",
      description_ar: "خطوات أقل وتجربة أخف.",
      expanded_text_ar: "خلي الطريق من الاختيار للتأكيد أقصر وأوضح.",
      title_en: "Faster booking",
      description_en: "Fewer steps. Lighter flow.",
      expanded_text_en: "A shorter path from choosing to confirming.",
      sticker_path: ""
    },
    {
      title_ar: "شفافية كاملة",
      description_ar: "المهم يكون واضح من البداية.",
      expanded_text_ar: "نصوص الحملة تقدر تشرح السعر، الرسوم، وما يحتاجه العميل قبل القرار.",
      title_en: "Full clarity",
      description_en: "Key details upfront.",
      expanded_text_en: "Campaign copy can make pricing and key terms clear before conversion.",
      sticker_path: ""
    },
    {
      title_ar: "دعم حقيقي",
      description_ar: "مسار أوضح للمتابعة.",
      expanded_text_ar: "بدون وعود كبيرة. بس توقعات أوضح وطريقة متابعة مفهومة.",
      title_en: "Real support",
      description_en: "A clearer follow-up path.",
      expanded_text_en: "No overpromising. Clearer expectations and response paths.",
      sticker_path: ""
    },
    {
      title_ar: "خيارات أكثر",
      description_ar: "اختيارات أوسع تناسب يومك.",
      expanded_text_ar: "المساحة هنا قابلة للتعديل حسب العرض أو الرسالة الفعلية.",
      title_en: "More options",
      description_en: "More ways to match your day.",
      expanded_text_en: "This space can adapt to the real offer or campaign message.",
      sticker_path: ""
    }
  ],
  proof: {
    eyebrow_ar: "قابل للتعديل",
    eyebrow_en: "Editable",
    title_ar: "كروت سوشال جاهزة للتبديل",
    title_en: "Swipe-ready social cards",
    note_ar: "هذه أمثلة نصية وليست مراجعات عملاء موثقة.",
    note_en: "These are editable examples, not verified customer reviews."
  },
  quotes: [
    {
      label_ar: "Placeholder",
      text_ar: "استخدم هذا الكرت لاحقا لرسالة حملة معتمدة أو اقتباس موثق.",
      source_ar: "Editable campaign card",
      label_en: "Placeholder",
      text_en: "Use this later for approved campaign copy or sourced proof.",
      source_en: "Editable campaign card"
    }
  ],
  finalCta: {
    eyebrow_ar: "الخطوة الجاية",
    headline_ar: "جاهز تشوف الجديد؟",
    text_ar: "عدّل النصوص، الصور، والروابط من ملفات الإعداد فقط.",
    primary_cta_ar: "ابدأ الآن",
    secondary_cta_ar: "رجوع للوحة",
    eyebrow_en: "Next step",
    headline_en: "Ready to see it?",
    text_en: "Edit copy, images, and links from config files only.",
    primary_cta_en: "Start now",
    secondary_cta_en: "Back to dashboard"
  },
  links: {
    primary: "#features",
    secondary: "#features",
    finalPrimary: "#features",
    finalSecondary: "./"
  }
};

export function renderAnnouncementPage({ brand = {}, content = null, language = "ar", selectedFeature = 0 } = {}) {
  const page = normalizeContent(content);
  const lang = pageHasLanguage(page, language) ? language : page.default_language || "ar";
  const dir = lang === "ar" ? "rtl" : "ltr";
  const brandName = brand.brandName || page.brand_name || "Telgani";
  const logoPath = brand.logoPath || brand.logo_path || page.assets.logo_path || "";
  const logoText = brand.logoText || brandName;
  const selected = clamp(Number(selectedFeature || 0), 0, page.features.length - 1);

  return `
    <main class="announcement-page" lang="${escapeAttr(lang === "ar" ? "ar-SA" : "en")}" dir="${escapeAttr(dir)}">
      <div class="announcement-bg" aria-hidden="true"></div>
      ${nav({ page, brandName, logoText, logoPath, lang })}
      ${content ? "" : emptyNotice(lang)}
      ${hero({ page, brandName, lang })}
      ${hooks({ page, lang })}
      ${features({ page, lang, selected })}
      ${proof({ page, lang })}
      ${finalCta({ page, lang })}
      <a class="announcement-sticky-cta" href="${escapeAttr(page.links.primary)}">${escapeHtml(t(page.hero, "primary_cta", lang))}</a>
    </main>
  `;
}

function nav({ page, brandName, logoText, logoPath, lang }) {
  return `
    <nav class="announcement-nav" aria-label="${escapeAttr(page.navLabel || "Campaign navigation")}">
      <a class="announcement-brand" href="./" aria-label="${escapeAttr(brandName)}">
        ${brandMark({ logoPath, logoText, brandName })}
      </a>
      <div class="announcement-section-nav">
        ${page.nav.map((item) => `<a href="#${escapeAttr(item.id)}" data-section-link="${escapeAttr(item.id)}">${escapeHtml(t(item, "label", lang))}</a>`).join("")}
      </div>
      <div class="announcement-nav-actions">
        ${languageToggle(page, lang)}
        <a class="announcement-mini-cta" href="${escapeAttr(page.links.primary)}">${escapeHtml(t(page.hero, "primary_cta", lang))}</a>
      </div>
    </nav>
  `;
}

function brandMark({ logoPath, logoText, brandName }) {
  const fallback = escapeHtml(logoText || brandName || "Telgani");
  if (!logoPath) {
    return `<span class="announcement-logo-text">${fallback}</span>`;
  }
  return `
    <span class="announcement-logo-lockup">
      <img src="${escapeAttr(logoPath)}" alt="${escapeAttr(brandName)}" data-fallback-image />
      <span class="announcement-logo-text" hidden>${fallback}</span>
    </span>
  `;
}

function languageToggle(page, lang) {
  if (!hasEnglish(page)) return "";
  return `
    <button class="announcement-lang-toggle" type="button" data-language-toggle aria-label="Toggle language">
      ${lang === "ar" ? "EN" : "عربي"}
    </button>
  `;
}

function hero({ page, brandName, lang }) {
  return `
    <section class="announcement-hero" id="top">
      <div class="announcement-hero-copy">
        <span class="announcement-eyebrow">${escapeHtml(t(page, "eyebrow", lang))}</span>
        <h1>${escapeHtml(t(page.hero, "title", lang))}</h1>
        <p class="announcement-subtitle">${escapeHtml(t(page.hero, "subtitle", lang))}</p>
        <p class="announcement-body">${escapeHtml(t(page.hero, "body", lang))}</p>
        <div class="announcement-cta-row">
          <a class="announcement-cta primary" href="${escapeAttr(page.links.primary)}">${escapeHtml(t(page.hero, "primary_cta", lang))}</a>
          <a class="announcement-cta secondary" href="${escapeAttr(page.links.secondary)}">${escapeHtml(t(page.hero, "secondary_cta", lang))}</a>
        </div>
      </div>
      <div class="announcement-visual" aria-label="${escapeAttr(brandName)} campaign visual">
        <div class="announcement-car-stage">
          ${assetOrPlaceholder(page.assets.hero_car_image, "announcement-car-image", carPlaceholder(lang))}
          <div class="announcement-speed-lines" aria-hidden="true"><i></i><i></i><i></i></div>
        </div>
        <div class="announcement-sticker-card">
          ${assetOrPlaceholder(page.assets.hero_sticker_image, "announcement-sticker-image", stickerPlaceholder(lang))}
          <span>${escapeHtml(t(page.hero, "secondary_cta", lang))}</span>
        </div>
        <div class="announcement-orbit-card">
          <span>${escapeHtml(brandName)}</span>
          <strong>${escapeHtml(t(page.hero, "subtitle", lang))}</strong>
          <p>${escapeHtml(t(page.hero, "body", lang))}</p>
          <div class="announcement-progress"><i></i></div>
        </div>
      </div>
    </section>
  `;
}

function hooks({ page, lang }) {
  return `
    <section class="announcement-hooks" id="${escapeAttr(page.sections.hook)}" aria-label="Campaign hooks">
      ${page.hooks.map((hook, index) => `<p style="--delay:${index * 70}ms">${escapeHtml(t(hook, "text", lang))}</p>`).join("")}
    </section>
  `;
}

function features({ page, lang, selected }) {
  return `
    <section class="announcement-feature-section" id="${escapeAttr(page.sections.features)}" aria-label="Campaign features">
      <div class="announcement-section-heading">
        <span>${escapeHtml(lang === "ar" ? "ردودنا على تعليقاتكم" : "Responses to your comments")}</span>
        <h2>${escapeHtml(lang === "ar" ? "وش سوّينا بناءً على اللي وصلنا؟" : "What are we doing with your feedback?")}</h2>
      </div>
      <div class="announcement-features">
        ${page.features.map((feature, index) => featureCard({ feature, index, lang, active: index === selected })).join("")}
      </div>
    </section>
  `;
}

function featureCard({ feature, index, lang, active }) {
  return `
    <button class="announcement-feature-card ${active ? "active" : ""}" type="button" data-feature-index="${index}" style="--delay:${index * 80}ms" aria-expanded="${active ? "true" : "false"}">
      <span>${String(index + 1).padStart(2, "0")}</span>
      ${assetOrPlaceholder(feature.sticker_path, "announcement-feature-sticker", featureIcon(index))}
      <h3>${escapeHtml(t(feature, "title", lang))}</h3>
      <p>${escapeHtml(t(feature, "description", lang))}</p>
      <div class="announcement-feature-expanded">
        ${escapeHtml(t(feature, "expanded_text", lang))}
      </div>
    </button>
  `;
}

function proof({ page, lang }) {
  return `
    <section class="announcement-social-proof" id="${escapeAttr(page.sections.proof)}" aria-label="Editable campaign message cards">
      <div class="announcement-section-heading">
        <span>${escapeHtml(t(page.proof, "eyebrow", lang))}</span>
        <h2>${escapeHtml(t(page.proof, "title", lang))}</h2>
        <p>${escapeHtml(t(page.proof, "note", lang))}</p>
      </div>
      <div class="announcement-quote-grid" tabindex="0" aria-label="Horizontally scrollable cards">
        ${page.quotes.map((quote) => quoteCard(quote, lang)).join("")}
      </div>
    </section>
  `;
}

function quoteCard(quote, lang) {
  return `
    <article class="announcement-quote-card">
      <span>${escapeHtml(t(quote, "label", lang))}</span>
      <p>${escapeHtml(t(quote, "text", lang))}</p>
      <strong>${escapeHtml(t(quote, "source", lang))}</strong>
    </article>
  `;
}

function finalCta({ page, lang }) {
  return `
    <section class="announcement-final" id="${escapeAttr(page.sections.final_cta)}">
      <div>
        <span class="announcement-eyebrow">${escapeHtml(t(page.finalCta, "eyebrow", lang))}</span>
        <h2>${escapeHtml(t(page.finalCta, "headline", lang))}</h2>
        <p>${escapeHtml(t(page.finalCta, "text", lang))}</p>
      </div>
      <div class="announcement-cta-row">
        <a class="announcement-cta primary" href="${escapeAttr(page.links.finalPrimary)}">${escapeHtml(t(page.finalCta, "primary_cta", lang))}</a>
        <a class="announcement-cta secondary" href="${escapeAttr(page.links.finalSecondary || "./")}">${escapeHtml(t(page.finalCta, "secondary_cta", lang))}</a>
      </div>
    </section>
  `;
}

function assetOrPlaceholder(path, className, placeholder) {
  if (!path) return placeholder;
  return `
    <span class="${className}">
      <img src="${escapeAttr(path)}" alt="" data-fallback-image />
      <span class="announcement-asset-fallback" hidden>${placeholder}</span>
    </span>
  `;
}

function carPlaceholder(lang) {
  return `<span class="announcement-car-placeholder" aria-hidden="true"><b>↝</b><strong>${escapeHtml(lang === "ar" ? "سيارتك جاهزة" : "Your car is ready")}</strong></span>`;
}

function stickerPlaceholder(lang) {
  return `<span class="announcement-sticker-placeholder" aria-hidden="true">${escapeHtml(lang === "ar" ? "جاهز" : "Ready")}</span>`;
}

function featureIcon(index) {
  const icons = ["⚡", "◇", "↗", "+"];
  return `<span class="announcement-feature-icon" aria-hidden="true">${icons[index % icons.length]}</span>`;
}

function emptyNotice(lang) {
  const text = lang === "ar"
    ? "لم يتم تحميل ملف المحتوى. يتم عرض نسخة احتياطية آمنة من داخل المكوّن."
    : "Content config was not loaded. Safe fallback copy is being displayed.";
  return `<aside class="announcement-config-notice">${escapeHtml(text)}</aside>`;
}

function normalizeContent(content) {
  const page = content && typeof content === "object" ? content : fallbackContent;
  return {
    ...fallbackContent,
    ...page,
    assets: { ...fallbackContent.assets, ...(page.assets || {}) },
    sections: { ...fallbackContent.sections, ...(page.sections || {}) },
    hero: { ...fallbackContent.hero, ...(page.hero || {}) },
    proof: { ...fallbackContent.proof, ...(page.proof || {}) },
    finalCta: { ...fallbackContent.finalCta, ...(page.finalCta || {}) },
    links: { ...fallbackContent.links, ...(page.links || {}) },
    nav: Array.isArray(page.nav) && page.nav.length ? page.nav : fallbackContent.nav,
    hooks: Array.isArray(page.hooks) && page.hooks.length ? page.hooks : fallbackContent.hooks,
    features: Array.isArray(page.features) && page.features.length ? page.features : fallbackContent.features,
    quotes: Array.isArray(page.quotes) && page.quotes.length ? page.quotes : fallbackContent.quotes
  };
}

function hasEnglish(page) {
  return Boolean(page.hero?.title_en || page.hero?.headline_en || page.finalCta?.headline_en);
}

function pageHasLanguage(page, lang) {
  return lang === "ar" || (lang === "en" && hasEnglish(page));
}

function t(object, key, lang) {
  if (!object) return "";
  const languageValue = object[`${key}_${lang}`];
  if (languageValue) return languageValue;
  if (lang === "ar" && object[key]) return object[key];
  return object[`${key}_ar`] || object[key] || "";
}

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

function escapeAttr(value) {
  return String(value ?? "").replace(/"/g, "&quot;");
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}
