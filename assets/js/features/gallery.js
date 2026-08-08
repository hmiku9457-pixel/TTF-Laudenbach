import { fetchJson } from "../core/http.js";
import { showContainerStatus } from "../core/status.js";
import { getSafeHttpUrl } from "../utils/safe-url.js";
import { initAnimations } from "./animations.js";

export async function initHistoricalImages() {
    const galleryContainer = document.getElementById("images-gallery-container");
    const eventList = document.getElementById("images-event-list");
    const loadingBox = document.getElementById("images-loading");
    const navigationPanel = eventList?.closest(".images-event-list");

    if (!galleryContainer || !eventList || !navigationPanel) {
        return;
    }

    const galleryNavigation = initGalleryNavigation(navigationPanel);

    try {
        const data = await fetchJson("/assets/data/gallerie.json");
        const galleries = Array.isArray(data.galleries) ? data.galleries : [];
        const defaultGalleryId = data.defaultGallery || "general";

        if (galleries.length === 0) {
            showContainerStatus(galleryContainer, "Keine Bilder gefunden.", "empty");
            eventList.innerHTML = "";
            hideLoadingBox(loadingBox);
            return;
        }

        function renderGallery(galleryId) {
            const gallery = galleries.find(item => item.id === galleryId);
            if (!gallery) {
                showContainerStatus(galleryContainer, "Die ausgewählte Galerie wurde nicht gefunden.", "error");
                return;
            }

            galleryContainer.innerHTML = "";
            const section = document.createElement("section");
            section.className = "box images-gallery is-active";
            section.dataset.gallery = gallery.id;
            section.setAttribute("aria-live", "polite");

            const title = document.createElement("h2");
            title.className = "u-text-center";
            title.textContent = gallery.title;
            section.appendChild(title);

            const masonry = document.createElement("div");
            masonry.className = "masonry-gallery";
            const images = Array.isArray(gallery.images) ? gallery.images : [];

            if (images.length === 0) {
                const empty = document.createElement("p");
                empty.className = "dynamic-status dynamic-status--empty";
                empty.textContent = "In dieser Galerie sind noch keine Bilder vorhanden.";
                masonry.appendChild(empty);
            } else {
                images.forEach((entry, index) => {
                    const source = typeof entry === "string" ? entry : entry?.src;
                    const safeSource = getSafeHttpUrl(source);
                    if (!safeSource) {
                        console.warn("Ungültiger Galeriepfad wurde übersprungen:", source);
                        return;
                    }

                    const image = document.createElement("img");
                    image.src = safeSource;
                    image.alt = getImageAlt(entry, gallery.title, index);
                    image.loading = "lazy";
                    image.decoding = "async";
                    masonry.appendChild(image);
                });
            }

            section.appendChild(masonry);
            galleryContainer.appendChild(section);

            eventList.querySelectorAll(".images-event-button").forEach(button => {
                const active = button.dataset.target === gallery.id;
                button.classList.toggle("is-active", active);
                button.setAttribute("aria-pressed", String(active));
            });

            hideLoadingBox(loadingBox);
            initAnimations(section);
            galleryNavigation.close({ returnFocus: false });
        }

        eventList.innerHTML = "";
        galleries.forEach(gallery => {
            const button = document.createElement("button");
            button.type = "button";
            button.className = "images-event-button";
            button.dataset.target = gallery.id;
            button.textContent = gallery.title;
            const active = gallery.id === defaultGalleryId;
            button.classList.toggle("is-active", active);
            button.setAttribute("aria-pressed", String(active));
            button.addEventListener("click", () => renderGallery(gallery.id));
            eventList.appendChild(button);
        });

        const initialGallery = galleries.some(gallery => gallery.id === defaultGalleryId)
            ? defaultGalleryId
            : galleries[0].id;
        renderGallery(initialGallery);
    } catch (error) {
        console.error("Fehler beim Laden der gallerie.json:", error);
        showContainerStatus(galleryContainer, "Die Bilder konnten nicht geladen werden.", "error");
        eventList.innerHTML = "";
        hideLoadingBox(loadingBox);
    }
}

function initGalleryNavigation(panel) {
    const page = panel.closest(".images-page");
    if (!page) {
        return { close: () => {} };
    }

    panel.id ||= "images-navigation-panel";

    let toggle = page.querySelector(".images-nav-toggle");
    if (!toggle) {
        toggle = document.createElement("button");
        toggle.type = "button";
        toggle.className = "button images-nav-toggle";
        toggle.textContent = "Galerien öffnen";
        toggle.setAttribute("aria-controls", panel.id);
        toggle.setAttribute("aria-expanded", "false");
        page.insertBefore(toggle, page.querySelector(".images-content"));
    }

    let closeButton = panel.querySelector(".images-nav-close");
    if (!closeButton) {
        closeButton = document.createElement("button");
        closeButton.type = "button";
        closeButton.className = "images-nav-close";
        closeButton.setAttribute("aria-label", "Galerien schließen");
        closeButton.textContent = "×";

        const heading = panel.querySelector("h2");
        const header = document.createElement("div");
        header.className = "images-event-list__header";
        heading?.insertAdjacentElement("beforebegin", header);
        if (heading) {
            header.appendChild(heading);
        }
        header.appendChild(closeButton);
    }

    let backdrop = document.querySelector(".images-nav-backdrop");
    if (!backdrop) {
        backdrop = document.createElement("button");
        backdrop.type = "button";
        backdrop.className = "images-nav-backdrop";
        backdrop.setAttribute("aria-label", "Galerien schließen");
        backdrop.tabIndex = -1;
        document.body.appendChild(backdrop);
    }

    const open = () => {
        panel.classList.add("is-open");
        backdrop.classList.add("is-visible");
        document.body.classList.add("gallery-nav-open");
        toggle.setAttribute("aria-expanded", "true");
        closeButton.focus();
    };

    const close = ({ returnFocus = true } = {}) => {
        const wasOpen = panel.classList.contains("is-open");
        panel.classList.remove("is-open");
        backdrop.classList.remove("is-visible");
        document.body.classList.remove("gallery-nav-open");
        toggle.setAttribute("aria-expanded", "false");
        if (wasOpen && returnFocus) {
            toggle.focus();
        }
    };

    toggle.addEventListener("click", () => {
        panel.classList.contains("is-open") ? close() : open();
    });
    closeButton.addEventListener("click", () => close());
    backdrop.addEventListener("click", () => close());

    document.addEventListener("keydown", event => {
        if (event.key === "Escape" && panel.classList.contains("is-open")) {
            close();
        }
    });

    window.matchMedia("(min-width: 769px)").addEventListener?.("change", event => {
        if (event.matches) {
            close({ returnFocus: false });
        }
    });

    return { open, close };
}

function getImageAlt(entry, galleryTitle, index) {
    if (entry && typeof entry === "object" && typeof entry.alt === "string" && entry.alt.trim()) {
        return entry.alt.trim();
    }

    const source = typeof entry === "string" ? entry : entry?.src;
    const filename = String(source || "")
        .split("/")
        .pop()
        ?.replace(/\.[a-z0-9]+$/i, "")
        .replace(/[-_]+/g, " ")
        .replace(/\s+/g, " ")
        .trim();

    return filename
        ? `${galleryTitle}: ${decodeURIComponent(filename)}`
        : `${galleryTitle}, Bild ${index + 1}`;
}

function hideLoadingBox(loadingBox) {
    if (loadingBox) {
        loadingBox.style.display = "none";
    }
}
