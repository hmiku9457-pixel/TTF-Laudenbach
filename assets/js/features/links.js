import { fetchJson } from "../core/http.js";
import { showContainerStatus } from "../core/status.js";
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

            if (links.length === 0) {
                showContainerStatus(container, "Für diesen Bereich sind aktuell keine Links verfügbar.", "empty");
                return;
            }

            links.forEach(link => {
                const anchor = document.createElement("a");
                anchor.href = link.url;
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

                [`link-${link.id}`, `link-${link.id}-main`, `link-${link.id}-footer`]
                    .forEach(id => {
                        const element = document.getElementById(id);

                        if (element) {
                            element.href = link.url;
                            element.textContent = link.name;
                        }
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

    if (element) {
        element.href = url;
        element.removeAttribute("aria-disabled");
        element.classList.remove("is-disabled");
    }
}

function showLinksError() {
    document.querySelectorAll('[id^="gruppe-"]:not([id^="gruppe-link-"])')
        .forEach(container => {
            showContainerStatus(container, "Die Linkliste konnte nicht geladen werden.", "error");
        });

    document.querySelectorAll('[id^="link-tabelle"], [id^="link-spiele"]')
        .forEach(link => disableLink(link, "Dieser Link ist momentan nicht verfügbar."));

    ["sponsor1", "sponsor2", "sponsor3", "sponsor4"].forEach(slot => {
        [`link-${slot}`, `link-${slot}-main`, `link-${slot}-footer`]
            .forEach(id => {
                const link = document.getElementById(id);

                if (link) {
                    disableLink(link, "Dieser Sponsor-Link ist momentan nicht verfügbar.");
                    link.textContent = "Sponsor-Link nicht verfügbar";
                }
            });
    });
}

function disableLink(link, title) {
    link.removeAttribute("href");
    link.setAttribute("aria-disabled", "true");
    link.classList.add("is-disabled");
    link.title = title;
}
