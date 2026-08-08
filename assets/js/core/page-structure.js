/**
 * Semantische Seitenstruktur und Navigationszustände.
 * Die Struktur wird statisch ausgeliefert; die ensure-Funktionen sind Fallbacks.
 */
export function initPageStructure() {
    ensureMainLandmark();
    ensureSkipLink();
    ensurePageHeading();
}

export function ensureMainLandmark() {
    const existingMain = document.querySelector("main");

    if (existingMain) {
        existingMain.id ||= "main-content";
        if (!existingMain.hasAttribute("tabindex")) {
            existingMain.tabIndex = -1;
        }
        return existingMain;
    }

    const headerContainer = document.getElementById("header-container");
    const footerContainer = document.getElementById("footer-container");

    if (!headerContainer || !footerContainer) {
        return null;
    }

    const main = document.createElement("main");
    main.id = "main-content";
    main.tabIndex = -1;
    headerContainer.insertAdjacentElement("afterend", main);

    let currentNode = main.nextSibling;
    while (currentNode && currentNode !== footerContainer) {
        const nextNode = currentNode.nextSibling;
        main.appendChild(currentNode);
        currentNode = nextNode;
    }

    return main;
}

export function ensureSkipLink() {
    const main = document.getElementById("main-content");
    if (!main || document.querySelector(".skip-link")) {
        return;
    }

    const skipLink = document.createElement("a");
    skipLink.className = "skip-link";
    skipLink.href = "#main-content";
    skipLink.textContent = "Direkt zum Inhalt";
    document.body.insertBefore(skipLink, document.body.firstChild);
}

export function ensurePageHeading() {
    const main = document.getElementById("main-content");
    if (!main || main.querySelector("h1")) {
        return;
    }

    const firstHeading = main.querySelector("h2, h3");
    const heading = document.createElement("h1");
    heading.className = "visually-hidden page-heading";
    heading.textContent = firstHeading?.textContent?.trim() || document.title || "TTF Laudenbach";
    main.insertBefore(heading, main.firstChild);
}

export function initHeaderAccessibility() {
    const navigation = document.querySelector("#header-container nav");
    if (!navigation) {
        return;
    }

    const currentPath = normalizePagePath(window.location.pathname);
    navigation.querySelectorAll("a[href]").forEach(link => {
        link.removeAttribute("aria-current");
        try {
            const linkPath = normalizePagePath(new URL(link.href, window.location.origin).pathname);
            if (linkPath === currentPath) {
                link.setAttribute("aria-current", "page");
            }
        } catch {
            // Ungültige Links werden von der Qualitätsprüfung abgefangen.
        }
    });

    initDropdownNavigation(navigation);
}

export function initDropdownNavigation(navigation = document) {
    const dropdowns = Array.from(navigation.querySelectorAll(".dropdown"));

    dropdowns.forEach((dropdown, index) => {
        const submenu = dropdown.querySelector(":scope > .submenu");
        const link = dropdown.querySelector(":scope > a");
        if (!submenu || !link) {
            return;
        }

        submenu.id ||= `submenu-${index + 1}`;
        let toggle = dropdown.querySelector(":scope > .submenu-toggle");

        if (!toggle) {
            toggle = document.createElement("button");
            toggle.type = "button";
            toggle.className = "submenu-toggle";
            toggle.innerHTML = '<span aria-hidden="true">▾</span>';
            link.insertAdjacentElement("afterend", toggle);
        }

        toggle.setAttribute("aria-controls", submenu.id);
        toggle.setAttribute("aria-expanded", "false");
        toggle.setAttribute("aria-label", `Untermenü ${link.textContent.trim()} öffnen`);

        const close = ({ focus = false } = {}) => {
            dropdown.classList.remove("is-open");
            toggle.setAttribute("aria-expanded", "false");
            toggle.setAttribute("aria-label", `Untermenü ${link.textContent.trim()} öffnen`);
            if (focus) {
                toggle.focus();
            }
        };

        const open = () => {
            dropdowns.forEach(other => {
                if (other !== dropdown) {
                    other.classList.remove("is-open");
                    other.querySelector(":scope > .submenu-toggle")?.setAttribute("aria-expanded", "false");
                }
            });
            dropdown.classList.add("is-open");
            toggle.setAttribute("aria-expanded", "true");
            toggle.setAttribute("aria-label", `Untermenü ${link.textContent.trim()} schließen`);
        };

        toggle.addEventListener("click", event => {
            event.preventDefault();
            const isOpen = toggle.getAttribute("aria-expanded") === "true";
            isOpen ? close() : open();
        });

        dropdown.addEventListener("keydown", event => {
            if (event.key === "Escape") {
                close({ focus: true });
            }
        });
    });

    document.addEventListener("click", event => {
        dropdowns.forEach(dropdown => {
            if (!dropdown.contains(event.target)) {
                dropdown.classList.remove("is-open");
                dropdown.querySelector(":scope > .submenu-toggle")?.setAttribute("aria-expanded", "false");
            }
        });
    });
}

export function normalizePagePath(pathname) {
    const normalized = String(pathname || "/")
        .replace(/\/index\.html$/i, "/")
        .replace(/\/+$/, "");
    return normalized || "/";
}

export function initTableSemantics(root = document) {
    root.querySelectorAll("table").forEach(table => {
        table.querySelectorAll("thead tr").forEach(row => {
            Array.from(row.children).forEach(cell => {
                let headerCell = cell;
                if (cell.tagName === "TD") {
                    headerCell = replaceElementTag(cell, "th");
                }
                if (headerCell.tagName === "TH" && !headerCell.hasAttribute("scope")) {
                    headerCell.setAttribute("scope", "col");
                }
            });
        });
    });
}

function replaceElementTag(element, tagName) {
    const replacement = document.createElement(tagName);
    Array.from(element.attributes).forEach(attribute => replacement.setAttribute(attribute.name, attribute.value));
    while (element.firstChild) {
        replacement.appendChild(element.firstChild);
    }
    element.replaceWith(replacement);
    return replacement;
}
