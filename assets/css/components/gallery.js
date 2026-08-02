import { fetchJson } from "../core/http.js";
import { showContainerStatus } from "../core/status.js";
import { initAnimations } from "./animations.js";

export async function initHistoricalImages() {
    const galleryContainer = document.getElementById("images-gallery-container");
    const eventList = document.getElementById("images-event-list");
    const loadingBox = document.getElementById("images-loading");

    if (!galleryContainer || !eventList) {
        return;
    }

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
            const title = document.createElement("h3");
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
                images.forEach((imagePath, index) => {
                    const image = document.createElement("img");
                    image.src = imagePath;
                    image.alt = `${gallery.title} Bild ${index + 1}`;
                    image.loading = "lazy";
                    masonry.appendChild(image);
                });
            }

            section.appendChild(masonry);
            galleryContainer.appendChild(section);
            document.querySelectorAll(".images-event-button").forEach(button => {
                button.classList.toggle("is-active", button.dataset.target === gallery.id);
            });
            hideLoadingBox(loadingBox);
            initAnimations(section);
        }

        eventList.innerHTML = "";
        galleries.forEach(gallery => {
            const button = document.createElement("button");
            button.type = "button";
            button.className = "images-event-button";
            button.dataset.target = gallery.id;
            button.textContent = gallery.title;
            button.classList.toggle("is-active", gallery.id === defaultGalleryId);
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

function hideLoadingBox(loadingBox) {
    if (loadingBox) {
        loadingBox.style.display = "none";
    }
}
