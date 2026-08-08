import { fetchJson } from "../core/http.js";
import { showContainerStatus } from "../core/status.js";
import { getSafeHttpUrl } from "../utils/safe-url.js";
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
            const slide = createSlide(item, index === 0);
            newsContainer.appendChild(slide);
        });

        startSlider(newsContainer);
        initAnimations(newsContainer);
    } catch (error) {
        console.error("Fehler beim Laden der news.json:", error);
        showContainerStatus(newsContainer, "Die Neuigkeiten konnten nicht geladen werden.", "error");
    }
}

function createSlide(item, active) {
    const slide = document.createElement("article");
    slide.className = "news-slide";
    slide.classList.toggle("active", active);

    const body = document.createElement("div");
    body.className = "news-slide__body";

    const copy = document.createElement("div");
    copy.className = "news-slide__copy";

    const title = document.createElement("h3");
    title.textContent = item?.title || "Neuigkeit";
    copy.appendChild(title);

    const text = document.createElement("p");
    text.textContent = item?.text || "";
    copy.appendChild(text);
    body.appendChild(copy);

    const imageUrl = getSafeHttpUrl(item?.image);
    if (imageUrl) {
        const media = document.createElement("div");
        media.className = "news-slide__media";

        const image = document.createElement("img");
        image.src = imageUrl;
        image.alt = item?.title || "Vereinsneuigkeit";
        image.loading = active ? "eager" : "lazy";
        image.decoding = "async";
        media.appendChild(image);
        body.appendChild(media);
    } else {
        slide.classList.add("news-slide--without-image");
    }

    const readMoreUrl = getSafeHttpUrl(item?.link);
    if (readMoreUrl) {
        slide.dataset.readMoreUrl = readMoreUrl;
        slide.dataset.readMoreLabel = `Mehr lesen: ${title.textContent}`;
    }

    slide.appendChild(body);
    return slide;
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

    const footer = document.createElement("div");
    footer.className = "news-slider__footer";

    const readMore = document.createElement("a");
    readMore.className = "read-more news-slider__read-more";
    readMore.textContent = "Mehr lesen";
    readMore.hidden = true;
    footer.appendChild(readMore);

    const controls = document.createElement("div");
    controls.className = "news-slider__controls";
    controls.setAttribute("aria-label", "Neuigkeiten steuern");

    let previousButton = null;
    let toggleButton = null;
    let nextButton = null;
    let status = null;

    if (slides.length > 1) {
        newsContainer.classList.add("news-slider--controlled");
        previousButton = createSliderButton("‹", "Vorherige Neuigkeit", "news-slider__button news-slider__button--previous");
        toggleButton = createSliderButton("Pause", "Automatischen Wechsel pausieren", "news-slider__button news-slider__button--toggle");
        status = document.createElement("span");
        status.className = "news-slider__status";
        status.setAttribute("aria-live", "off");
        status.setAttribute("aria-atomic", "true");
        nextButton = createSliderButton("›", "Nächste Neuigkeit", "news-slider__button news-slider__button--next");
        controls.append(previousButton, toggleButton, status, nextButton);
        footer.appendChild(controls);
    }

    newsContainer.classList.add("news-slider--has-footer");
    newsContainer.appendChild(footer);

    const reducedMotionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    let index = 0;
    let intervalId = null;
    let userPaused = reducedMotionQuery.matches;
    let temporarilyPaused = false;

    function updateReadMore(slide) {
        const url = slide.dataset.readMoreUrl;
        if (!url) {
            readMore.hidden = true;
            readMore.removeAttribute("href");
            readMore.removeAttribute("aria-label");
            return;
        }

        readMore.href = url;
        readMore.hidden = false;
        readMore.setAttribute("aria-label", slide.dataset.readMoreLabel || "Mehr lesen");
    }

    function showSlide(nextIndex, announce = false) {
        index = (nextIndex + slides.length) % slides.length;
        slides.forEach((slide, slideIndex) => {
            setSlideAccessibility(slide, slideIndex === index);
        });
        updateReadMore(slides[index]);

        if (status) {
            status.setAttribute("aria-live", announce ? "polite" : "off");
            status.textContent = `${index + 1} / ${slides.length}`;
            if (announce) {
                window.setTimeout(() => status.setAttribute("aria-live", "off"), 250);
            }
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
        if (slides.length <= 1 || userPaused || temporarilyPaused || document.hidden) {
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
        if (!toggleButton) {
            return;
        }
        toggleButton.textContent = userPaused ? "Abspielen" : "Pause";
        toggleButton.setAttribute(
            "aria-label",
            userPaused ? "Automatischen Wechsel starten" : "Automatischen Wechsel pausieren"
        );
    }

    previousButton?.addEventListener("click", () => {
        showSlide(index - 1, true);
        syncAutomaticChange();
    });
    nextButton?.addEventListener("click", () => {
        showSlide(index + 1, true);
        syncAutomaticChange();
    });
    toggleButton?.addEventListener("click", () => {
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
