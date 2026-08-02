/**
 * Semantische Seitenstruktur und Navigationszustände.
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

    const pathname = normalizePagePath(window.location.pathname);
    const firstHeading = main.querySelector("h2, h3");
    const headingText = pathname === "/"
        ? "Tischtennis-Freunde Laudenbach"
        : firstHeading?.textContent?.trim() || document.title || "TTF Laudenbach";

    const heading = document.createElement("h1");
    heading.className = "visually-hidden page-heading";
    heading.textContent = headingText;
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
            const linkPath = normalizePagePath(
                new URL(link.href, window.location.origin).pathname
            );

            if (linkPath === currentPath) {
                link.setAttribute("aria-current", "page");
            }
        } catch {
            // Ungültige Links werden hier lediglich ignoriert.
        }
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

    Array.from(element.attributes).forEach(attribute => {
        replacement.setAttribute(attribute.name, attribute.value);
    });

    while (element.firstChild) {
        replacement.appendChild(element.firstChild);
    }

    element.replaceWith(replacement);
    return replacement;
}
