import { loadComponent } from "./core/components.js";
import {
    initHeaderAccessibility,
    initPageStructure,
    initTableSemantics
} from "./core/page-structure.js";
import { initAnimationObserver, initAnimations } from "./features/animations.js";
import { initContactForm } from "./features/contact-form.js";
import { initHistoricalImages } from "./features/gallery.js";
import { initIframeConsent } from "./features/iframe-consent.js";
import { loadLinks } from "./features/links.js";
import { initNewsSlider } from "./features/news-slider.js";
import { initSpielerliste } from "./features/player-list.js";
import {
    initTableScrollContainers,
    initTableSearch,
    loadAllTables
} from "./features/tables.js";
import { initThemeSwitcher } from "./features/theme-switcher.js";

document.documentElement.classList.add("js");

async function initializePage() {
    // Fallbacks bleiben erhalten, die reguläre Struktur steht aber statisch im HTML.
    initPageStructure();
    initTableSemantics();
    initTableScrollContainers();
    initTableSearch();
    initIframeConsent();
    initContactForm();
    initAnimations();
    initAnimationObserver([
        initTableSemantics,
        initTableScrollContainers
    ]);

    const [headerLoaded] = await Promise.all([
        loadComponent(
            "header-container",
            "/components/header.html",
            "Die Navigation konnte nicht geladen werden."
        ),
        loadComponent(
            "footer-container",
            "/components/footer.html",
            "Der Seitenfuß konnte nicht geladen werden."
        )
    ]);

    if (headerLoaded) {
        initThemeSwitcher();
        initHeaderAccessibility();
    }

    await loadLinks();

    await Promise.allSettled([
        initNewsSlider(),
        loadAllTables(),
        initHistoricalImages(),
        initSpielerliste()
    ]);

    initTableSemantics();
    initTableScrollContainers();
    initAnimations();
}

document.addEventListener("DOMContentLoaded", () => {
    initializePage().catch(error => {
        console.error("Unerwarteter Fehler bei der Seiteninitialisierung:", error);
    });
});
