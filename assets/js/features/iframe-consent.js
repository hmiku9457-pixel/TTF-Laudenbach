import {
    getStorageValue,
    removeStorageValue,
    setStorageValue
} from "../core/storage.js";
import { getSafeEmbedUrl } from "../utils/safe-url.js";

const iframePlaceholders = new WeakMap();

export function initIframeConsent() {
    const containers = Array.from(document.querySelectorAll(".iframe-consent"));
    if (containers.length === 0) {
        return;
    }

    const legacyConsent = getStorageValue("externalContentAccepted") === "true";

    containers.forEach(container => {
        rememberIframePlaceholder(container);
        bindConsentButton(container);
        const safeSrc = getSafeEmbedUrl(container.dataset.src);

        if (!safeSrc) {
            markInvalidEmbed(container);
            return;
        }

        const provider = getIframeProvider(container, safeSrc);
        container.dataset.providerId = provider.id;

        if (legacyConsent) {
            setStorageValue(getIframeStorageKey(provider.id), "true");
        }

        if (getStorageValue(getIframeStorageKey(provider.id)) === "true") {
            createIframe(container, safeSrc);
        }
    });

    if (legacyConsent) {
        removeStorageValue("externalContentAccepted");
    }
}

function bindConsentButton(container) {
    const button = container.querySelector("[data-iframe-consent-load]");
    if (!button || button.dataset.listenerBound === "true") {
        return;
    }

    button.dataset.listenerBound = "true";
    button.addEventListener("click", () => {
        const safeSrc = getSafeEmbedUrl(container.dataset.src);
        if (!safeSrc) {
            markInvalidEmbed(container);
            return;
        }

        const provider = getIframeProvider(container, safeSrc);
        setStorageValue(getIframeStorageKey(provider.id), "true");
        loadAcceptedIframes(provider.id);
    });
}

function rememberIframePlaceholder(container) {
    if (!iframePlaceholders.has(container)) {
        iframePlaceholders.set(container, container.innerHTML);
    }
}

function getIframeProvider(container, src) {
    const hostname = new URL(src).hostname.toLowerCase();
    const explicitProvider = container.dataset.provider?.trim();

    if (explicitProvider) {
        return {
            id: explicitProvider.toLowerCase().replace(/[^a-z0-9-]/g, "-"),
            name: container.dataset.providerName || explicitProvider
        };
    }

    if (hostname.includes("google")) {
        return { id: "google-maps", name: "Google Maps" };
    }
    if (hostname.includes("youtube") || hostname.includes("youtu.be")) {
        return { id: "youtube", name: "YouTube" };
    }

    return {
        id: hostname.replace(/[^a-z0-9-]/g, "-"),
        name: hostname
    };
}

function getIframeStorageKey(providerId) {
    return `externalContentAccepted:${providerId}`;
}

function getIframeTitle(container, provider) {
    if (container.dataset.iframeTitle) {
        return container.dataset.iframeTitle;
    }

    const section = container.closest("section, .box, .team-box");
    const heading = section?.querySelector("h1, h2, h3, h4");
    const context = heading?.textContent?.trim();
    return context ? `${provider.name} – ${context}` : `${provider.name} – externer Inhalt`;
}

function createIframe(container, src) {
    rememberIframePlaceholder(container);
    const provider = getIframeProvider(container, src);
    const iframe = document.createElement("iframe");
    iframe.src = src;
    iframe.title = getIframeTitle(container, provider);
    iframe.style.width = "100%";
    iframe.style.height = "250px";
    iframe.style.border = "0";
    iframe.loading = "lazy";
    iframe.referrerPolicy = "no-referrer";
    iframe.allowFullscreen = true;

    const controls = document.createElement("div");
    controls.className = "iframe-embed__controls";
    const status = document.createElement("span");
    status.textContent = `Externer Inhalt von ${provider.name} ist aktiviert.`;
    const revokeButton = document.createElement("button");
    revokeButton.type = "button";
    revokeButton.className = "iframe-revoke-button";
    revokeButton.textContent = "Externe Inhalte deaktivieren";
    revokeButton.addEventListener("click", () => revokeIframeConsent(provider.id));
    controls.append(status, revokeButton);

    container.innerHTML = "";
    container.dataset.providerId = provider.id;
    container.dataset.iframeLoaded = "true";
    container.append(iframe, controls);
}

function restoreIframePlaceholder(container) {
    const placeholderHtml = iframePlaceholders.get(container);
    if (typeof placeholderHtml === "string") {
        container.innerHTML = placeholderHtml;
        delete container.dataset.iframeLoaded;
        bindConsentButton(container);
    }
}

function loadAcceptedIframes(providerId) {
    document.querySelectorAll(".iframe-consent").forEach(container => {
        const safeSrc = getSafeEmbedUrl(container.dataset.src);
        if (safeSrc && getIframeProvider(container, safeSrc).id === providerId) {
            createIframe(container, safeSrc);
        }
    });
}

function revokeIframeConsent(providerId) {
    removeStorageValue(getIframeStorageKey(providerId));
    document.querySelectorAll(".iframe-consent").forEach(container => {
        const safeSrc = getSafeEmbedUrl(container.dataset.src);
        if (safeSrc && getIframeProvider(container, safeSrc).id === providerId) {
            restoreIframePlaceholder(container);
        }
    });
}

function markInvalidEmbed(container) {
    container.innerHTML = "";
    const status = document.createElement("p");
    status.className = "dynamic-status dynamic-status--error";
    status.setAttribute("role", "alert");
    status.textContent = "Der externe Inhalt konnte aus Sicherheitsgründen nicht geladen werden.";
    container.appendChild(status);
}
