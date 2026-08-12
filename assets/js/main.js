import {
    initHeaderAccessibility,
    initPageStructure,
    initTableSemantics
} from "./core/page-structure.js";
import { initSiteComponents } from "./core/site-components.js";

document.documentElement.classList.add("js");

const has = selector => Boolean(document.querySelector(selector));

async function loadFeature(path, initializer, ...args) {
    const module = await import(path);
    const fn = module[initializer];
    if (typeof fn !== "function") {
        throw new TypeError(`${initializer} wurde in ${path} nicht gefunden.`);
    }
    return fn(...args);
}

async function initializePage() {
    await initSiteComponents();

    initPageStructure();
    initHeaderAccessibility();
    initTableSemantics();

    const tasks = [];
    let tablesModule = null;

    if (has("table")) {
        tablesModule = await import("./features/tables.js");
        tablesModule.initTableScrollContainers();
        tablesModule.initTableSearch();
        tasks.push(tablesModule.loadAllTables());
    }

    if (has("#themeSwitcher")) {
        tasks.push(loadFeature("./features/theme-switcher.js", "initThemeSwitcher"));
    }
    if (has(".iframe-consent")) {
        tasks.push(loadFeature("./features/iframe-consent.js", "initIframeConsent"));
    }
    if (has("#contactForm")) {
        tasks.push(loadFeature("./features/contact-form.js", "initContactForm"));
    }
    if (has(".news-slider")) {
        tasks.push(loadFeature("./features/news-slider.js", "initNewsSlider"));
    }
    if (has("#images-gallery-container, #images-event-list")) {
        tasks.push(loadFeature("./features/gallery.js", "initHistoricalImages"));
    }
    if (has("#spieler-mannschaft")) {
        tasks.push(loadFeature("./features/player-list.js", "initSpielerliste"));
    }
    if (has('[id^="gruppe-"], [id^="link-tabelle"], [id^="link-spiele"], [id^="link-sponsor"]')) {
        tasks.push(loadFeature("./features/links.js", "loadLinks"));
    }

    const needsAnimations = has(".box, .team-box, .news-slider, .button, .table-ewigeRangliste");
    let animationsModule = null;
    if (needsAnimations) {
        animationsModule = await import("./features/animations.js");
        animationsModule.initAnimations();
        animationsModule.initAnimationObserver([
            initTableSemantics,
            root => tablesModule?.initTableScrollContainers(root)
        ]);
    }

    const results = await Promise.allSettled(tasks);
    results.filter(result => result.status === "rejected").forEach(result => {
        console.error("Feature konnte nicht initialisiert werden:", result.reason);
    });

    initTableSemantics();
    tablesModule?.initTableScrollContainers();
    animationsModule?.initAnimations();
}

document.addEventListener("DOMContentLoaded", () => {
    initializePage().catch(error => {
        console.error("Unerwarteter Fehler bei der Seiteninitialisierung:", error);
    });
});
