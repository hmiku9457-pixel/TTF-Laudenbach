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

/**
 * Dropdown-Navigation mit kombiniertem Link und Pfeil.
 * Erster Klick öffnet das Untermenü, ein zweiter Klick auf denselben Link
 * öffnet die zugehörige Übersichtsseite.
 */
export function initDropdownNavigation(navigation = document) {
    const dropdowns = Array.from(navigation.querySelectorAll(".dropdown"));

    const closeDropdown = (dropdown, { focus = false } = {}) => {
        const link = dropdown.querySelector(":scope > a");
        dropdown.classList.remove("is-open");
        dropdown.dataset.navigationArmed = "false";
        link?.setAttribute("aria-expanded", "false");
        if (focus) {
            link?.focus();
        }
    };

    const openDropdown = dropdown => {
        dropdowns.forEach(other => {
            if (other !== dropdown) {
                closeDropdown(other);
            }
        });

        const link = dropdown.querySelector(":scope > a");
        dropdown.classList.add("is-open");
        dropdown.dataset.navigationArmed = "true";
        link?.setAttribute("aria-expanded", "true");
    };

    dropdowns.forEach((dropdown, index) => {
        const submenu = dropdown.querySelector(":scope > .submenu");
        const link = dropdown.querySelector(":scope > a");
        if (!submenu || !link) {
            return;
        }

        // Entfernt den in einer früheren Version separat erzeugten Button.
        dropdown.querySelector(":scope > .submenu-toggle")?.remove();

        submenu.id ||= `submenu-${index + 1}`;
        link.classList.add("dropdown-link");
        link.setAttribute("aria-haspopup", "true");
        link.setAttribute("aria-controls", submenu.id);
        link.setAttribute("aria-expanded", "false");
        dropdown.dataset.navigationArmed = "false";

        if (!link.querySelector(".dropdown-link__indicator")) {
            const indicator = document.createElement("span");
            indicator.className = "dropdown-link__indicator";
            indicator.setAttribute("aria-hidden", "true");
            indicator.textContent = "▾";
            link.appendChild(indicator);
        }

        link.addEventListener("click", event => {
            const isOpen = dropdown.classList.contains("is-open");
            const isArmed = dropdown.dataset.navigationArmed === "true";

            if (!isOpen || !isArmed) {
                event.preventDefault();
                openDropdown(dropdown);
            }
            // Ist das Menü bereits durch einen ersten Klick geöffnet, darf der
            // zweite Klick regulär zur Übersichtsseite navigieren.
        });

        link.addEventListener("keydown", event => {
            if (event.key === "ArrowDown") {
                event.preventDefault();
                openDropdown(dropdown);
                submenu.querySelector("a")?.focus();
            }
        });

        dropdown.addEventListener("keydown", event => {
            if (event.key === "Escape") {
                event.preventDefault();
                closeDropdown(dropdown, { focus: true });
            }
        });

        submenu.addEventListener("click", event => {
            if (event.target.closest("a")) {
                closeDropdown(dropdown);
            }
        });
    });

    document.addEventListener("click", event => {
        dropdowns.forEach(dropdown => {
            if (!dropdown.contains(event.target)) {
                closeDropdown(dropdown);
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
