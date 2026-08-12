/**
 * Lädt die globalen Seitenteile aus /components.
 *
 * Header und Footer sind damit echte Single Sources of Truth und müssen nicht
 * mehr in jede HTML-Datei kopiert werden.
 */
const SITE_COMPONENTS = [
    {
        selector: "#header-container",
        url: "/components/header.html",
        name: "Header"
    },
    {
        selector: "#footer-container",
        url: "/components/footer.html",
        name: "Footer"
    }
];

async function loadSiteComponent({ selector, url, name }) {
    const container = document.querySelector(selector);
    if (!container) {
        return { name, status: "missing-container" };
    }

    if (container.dataset.componentLoaded === "true") {
        return { name, status: "already-loaded" };
    }

    const response = await fetch(url, { cache: "no-cache" });
    if (!response.ok) {
        throw new Error(`${name} konnte nicht geladen werden (${response.status}).`);
    }

    container.innerHTML = await response.text();
    container.dataset.componentLoaded = "true";
    return { name, status: "loaded" };
}

export async function initSiteComponents() {
    const results = await Promise.allSettled(
        SITE_COMPONENTS.map(component => loadSiteComponent(component))
    );

    results.forEach((result, index) => {
        if (result.status === "rejected") {
            console.error(
                `${SITE_COMPONENTS[index].name} konnte nicht initialisiert werden:`,
                result.reason
            );
        }
    });

    return results;
}
