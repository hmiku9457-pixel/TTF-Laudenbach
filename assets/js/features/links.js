import { fetchJson } from "../core/http.js";
import { showContainerStatus } from "../core/status.js";
import { getSafeHttpUrl } from "../utils/safe-url.js";
import { initAnimations } from "./animations.js";

export async function loadLinks() {
    try {
        const data = await fetchJson("/assets/data/links.json");
        const tabellen = Array.isArray(data.tabellen) ? data.tabellen : [];
        const spielplaene = Array.isArray(data.spielplaene) ? data.spielplaene : [];
        const linkGruppen = Array.isArray(data.links) ? data.links : [];

        tabellen.forEach(entry => setLinkTarget(`link-${entry.id}`, entry.url));
        spielplaene.forEach(entry => setLinkTarget(`link-${entry.id}`, entry.url));

        linkGruppen.forEach(gruppe => {
            const container = document.getElementById(`gruppe-${gruppe.gruppe}`);
            if (!container) {
                return;
            }

            container.innerHTML = "";
            const links = Array.isArray(gruppe.links) ? gruppe.links : [];
            const validLinks = links
                .map(link => ({ ...link, safeUrl: getSafeHttpUrl(link.url) }))
                .filter(link => Boolean(link.safeUrl));

            if (validLinks.length === 0) {
                showContainerStatus(container, "Für diesen Bereich sind aktuell keine gültigen Links verfügbar.", "empty");
                return;
            }

            validLinks.forEach(link => {
                const anchor = document.createElement("a");
                anchor.href = link.safeUrl;
                anchor.target = "_blank";
                anchor.rel = "noopener noreferrer";
                anchor.className = "button button--card";
                anchor.textContent = link.name;
                anchor.id = `gruppe-link-${link.id}`;
                container.appendChild(anchor);
            });
        });

        const sponsorSlots = ["sponsor1", "sponsor2", "sponsor3", "sponsor4"];
        linkGruppen.forEach(gruppe => {
            const links = Array.isArray(gruppe.links) ? gruppe.links : [];
            links.forEach(link => {
                if (!sponsorSlots.includes(link.id)) {
                    return;
                }

                const safeUrl = getSafeHttpUrl(link.url);
                [`link-${link.id}`, `link-${link.id}-main`, `link-${link.id}-footer`]
                    .forEach(id => {
                        const element = document.getElementById(id);
                        if (!element) {
                            return;
                        }
                        element.textContent = link.name;
                        safeUrl
                            ? enableLink(element, safeUrl)
                            : disableLink(element, "Dieser Sponsor-Link ist ungültig.");
                    });
            });
        });

        initAnimations();
    } catch (error) {
        console.error("Fehler beim Laden der links.json:", error);
        showLinksError();
    }
}

function setLinkTarget(id, url) {
    const element = document.getElementById(id);
    if (!element) {
        return;
    }

    const safeUrl = getSafeHttpUrl(url);
    safeUrl
        ? enableLink(element, safeUrl)
        : disableLink(element, "Dieser Link ist ungültig.");
}

function enableLink(link, url) {
    link.href = url;
    link.removeAttribute("aria-disabled");
    link.classList.remove("is-disabled");
    link.removeAttribute("title");
}

function showLinksError() {
    document.querySelectorAll('[id^="gruppe-"]:not([id^="gruppe-link-"])')
        .forEach(container => showContainerStatus(container, "Die Linkliste konnte nicht geladen werden.", "error"));

    document.querySelectorAll('[id^="link-tabelle"], [id^="link-spiele"]')
        .forEach(link => disableLink(link, "Dieser Link ist momentan nicht verfügbar."));

    ["sponsor1", "sponsor2", "sponsor3", "sponsor4"].forEach(slot => {
        [`link-${slot}`, `link-${slot}-main`, `link-${slot}-footer`].forEach(id => {
            const link = document.getElementById(id);
            if (link) {
                const fallbackAvailable = disableLink(
                    link,
                    "Dieser Sponsor-Link ist momentan nicht verfügbar."
                );
                if (!fallbackAvailable) {
                    link.textContent = "Sponsor-Link nicht verfügbar";
                }
            }
        });
    });
}

function disableLink(link, title) {
    const fallbackUrl = getSafeHttpUrl(link.getAttribute("href"));

    if (fallbackUrl) {
        link.href = fallbackUrl;
        link.removeAttribute("aria-disabled");
        link.classList.remove("is-disabled");
        link.title = `${title} Der zuletzt hinterlegte Link bleibt verfügbar.`;
        return true;
    }

    link.removeAttribute("href");
    link.setAttribute("aria-disabled", "true");
    link.classList.add("is-disabled");
    link.title = title;
    return false;
}
