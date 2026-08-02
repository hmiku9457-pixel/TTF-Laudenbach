import { fetchJson } from "../core/http.js";
import { showContainerStatus } from "../core/status.js";
import { initAnimations } from "./animations.js";

export async function initNewsSlider() {
    const newsContainer = document.querySelector(".news-slider");

    if (!newsContainer) {
        return;
    }

    try {
        const data = await fetchJson("/assets/data/news.json");

        if (!Array.isArray(data)) {
            throw new Error("news.json enthält keine Liste.");
        }

        newsContainer.innerHTML = "";

        if (data.length === 0) {
            showContainerStatus(newsContainer, "Aktuell sind keine Neuigkeiten vorhanden.", "empty");
            return;
        }

        data.forEach((item, index) => {
            const slide = document.createElement("article");
            slide.className = "news-slide";
            slide.classList.toggle("active", index === 0);

            if (item.image) {
                const image = document.createElement("img");
                image.src = item.image;
                image.alt = item.title || "Vereinsneuigkeit";
                image.loading = index === 0 ? "eager" : "lazy";
                slide.appendChild(image);
            }

            const title = document.createElement("h3");
            title.textContent = item.title || "Neuigkeit";
            slide.appendChild(title);

            const text = document.createElement("p");
            text.textContent = item.text || "";
            slide.appendChild(text);

            if (item.link) {
                const link = document.createElement("a");
                link.href = item.link;
                link.className = "read-more";
                link.textContent = "Mehr lesen";
                slide.appendChild(link);
            }

            newsContainer.appendChild(slide);
        });

        startSlider(newsContainer);
        initAnimations(newsContainer);
    } catch (error) {
        console.error("Fehler beim Laden der news.json:", error);
        showContainerStatus(newsContainer, "Die Neuigkeiten konnten nicht geladen werden.", "error");
    }
}

function startSlider(newsContainer) {
    const slides = Array.from(newsContainer.querySelectorAll(".news-slide"));

    if (slides.length === 0) {
        return;
    }

    newsContainer.setAttribute("role", "region");
    newsContainer.setAttribute("aria-roledescription", "Karussell");
    newsContainer.setAttribute("aria-label", "Neuigkeiten");

    slides.forEach((slide, slideIndex) => {
        slide.setAttribute("role", "group");
        slide.setAttribute("aria-roledescription", "Folie");
        slide.setAttribute("aria-label", `${slideIndex + 1} von ${slides.length}`);
    });

    if (slides.length === 1) {
        setSlideAccessibility(slides[0], true);
        return;
    }

    newsContainer.classList.add("news-slider--controlled");

    const controls = document.createElement("div");
    controls.className = "news-slider__controls";
    controls.setAttribute("aria-label", "Neuigkeiten steuern");

    const previousButton = createSliderButton("‹", "Vorherige Neuigkeit", "news-slider__button news-slider__button--previous");
    const toggleButton = createSliderButton("Pause", "Automatischen Wechsel pausieren", "news-slider__button news-slider__button--toggle");
    const status = document.createElement("span");
    status.className = "news-slider__status";
    status.setAttribute("aria-live", "off");
    status.setAttribute("aria-atomic", "true");
    const nextButton = createSliderButton("›", "Nächste Neuigkeit", "news-slider__button news-slider__button--next");

    controls.append(previousButton, toggleButton, status, nextButton);
    newsContainer.appendChild(controls);

    const reducedMotionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    let index = 0;
    let intervalId = null;
    let userPaused = reducedMotionQuery.matches;
    let temporarilyPaused = false;

    function showSlide(nextIndex, announce = false) {
        index = (nextIndex + slides.length) % slides.length;
        slides.forEach((slide, slideIndex) => {
            setSlideAccessibility(slide, slideIndex === index);
        });

        status.setAttribute("aria-live", announce ? "polite" : "off");
        status.textContent = `${index + 1} / ${slides.length}`;

        if (announce) {
            window.setTimeout(() => status.setAttribute("aria-live", "off"), 250);
        }
    }

    function stopAutomaticChange() {
        if (intervalId !== null) {
            window.clearInterval(intervalId);
            intervalId = null;
        }
    }

    function syncAutomaticChange() {
        stopAutomaticChange();

        if (userPaused || temporarilyPaused || document.hidden) {
            return;
        }

        intervalId = window.setInterval(() => {
            if (!newsContainer.isConnected) {
                stopAutomaticChange();
                return;
            }

            showSlide(index + 1);
        }, 10000);
    }

    function updateToggleButton() {
        toggleButton.textContent = userPaused ? "Abspielen" : "Pause";
        toggleButton.setAttribute(
            "aria-label",
            userPaused ? "Automatischen Wechsel starten" : "Automatischen Wechsel pausieren"
        );
    }

    previousButton.addEventListener("click", () => {
        showSlide(index - 1, true);
        syncAutomaticChange();
    });
    nextButton.addEventListener("click", () => {
        showSlide(index + 1, true);
        syncAutomaticChange();
    });
    toggleButton.addEventListener("click", () => {
        userPaused = !userPaused;
        updateToggleButton();
        syncAutomaticChange();
    });
    newsContainer.addEventListener("mouseenter", () => {
        temporarilyPaused = true;
        syncAutomaticChange();
    });
    newsContainer.addEventListener("mouseleave", () => {
        temporarilyPaused = false;
        syncAutomaticChange();
    });
    newsContainer.addEventListener("focusin", () => {
        temporarilyPaused = true;
        syncAutomaticChange();
    });
    newsContainer.addEventListener("focusout", event => {
        if (!newsContainer.contains(event.relatedTarget)) {
            temporarilyPaused = false;
            syncAutomaticChange();
        }
    });
    document.addEventListener("visibilitychange", syncAutomaticChange);
    reducedMotionQuery.addEventListener?.("change", event => {
        if (event.matches) {
            userPaused = true;
            updateToggleButton();
            syncAutomaticChange();
        }
    });

    showSlide(0);
    updateToggleButton();
    syncAutomaticChange();
}

function setSlideAccessibility(slide, isActive) {
    slide.classList.toggle("active", isActive);
    slide.setAttribute("aria-hidden", String(!isActive));
    slide.toggleAttribute("inert", !isActive);
}

function createSliderButton(text, label, className) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = className;
    button.textContent = text;
    button.setAttribute("aria-label", label);
    return button;
}
