// ==========================================
// ===== INHALTSVERZEICHNIS =================
// ==========================================
//
// 01 - DOM READY & INITIALISIERUNG
// 02 - FETCH-HILFSFUNKTIONEN
// 03 - HEADER & FOOTER
// 04 - SEITENSTRUKTUR & SEMANTIK
// 04A - STATUSMELDUNGEN
// 05 - NEWS-SLIDER
// 06 - ANIMATIONEN
// 07 - TABELLEN-SCROLL & SUCHE
// 08 - THEME SWITCHER
// 09 - iFRAME CONSENT (DSGVO)
// 10 - GENERISCHER TABLE LOADER
// 11 - SPIELE KONFIG
// 12 - TABELLEN KONFIG
// 13 - HILFSFUNKTIONEN
// 14 - LINKS LOADER
// 15 - KONTAKTFORMULAR
// 16 - HISTORISCHE FOTOS
// 17 - SPIELERLISTEN
//
// ==========================================

// ==========================================
// ===== 01 - DOM READY & INITIALISIERUNG ===
// ==========================================

document.addEventListener("DOMContentLoaded", () => {

    async function initializePage() {
        // Statische Inhalte sofort initialisieren.
        initPageStructure();
        initTableSemantics();
        initTableScrollContainers();
        initTableSearch();
        initIframeConsent();
        initContactForm();
        initAnimations();
        initAnimationObserver();

        // Header und Footer parallel laden.
        // Die Links werden bewusst erst danach geladen, damit die Sponsor-Ziele
        // im Footer garantiert bereits im DOM vorhanden sind.
        const [headerLoaded] = await Promise.all([
            loadComponent(
                "header-container",
                "/components/header.html",
                "Die Navigation konnte nicht geladen werden."
            ),
            loadComponent(
                "footer-container",
                "/components/footer.html",
                "Der Seitenfuß konnte nicht geladen werden."
            )
        ]);

        if (headerLoaded) {
            initThemeSwitcher();
            initHeaderAccessibility();
        }

        await loadLinks();

        // Die übrigen Inhalte dürfen unabhängig voneinander laden.
        // Ein einzelner Fehler blockiert dadurch nicht die komplette Seite.
        await Promise.allSettled([
            initNewsSlider(),
            loadAllTables(),
            initHistoricalImages(),
            initSpielerliste()
        ]);

        // Falls später doch Inhalte dynamisch ergänzt wurden.
        initTableSemantics();
        initTableScrollContainers();
        initAnimations();
    }


    // ==========================================
    // ===== 02 - FETCH-HILFSFUNKTIONEN =========
    // ==========================================

    async function fetchText(url, options = {}) {
        const response = await fetch(url, options);

        if (!response.ok) {
            throw new Error(
                `HTTP ${response.status} (${response.statusText || "Unbekannter Fehler"}) bei ${url}`
            );
        }

        return response.text();
    }

    async function fetchJson(url, options = {}) {
        const response = await fetch(url, options);

        if (!response.ok) {
            throw new Error(
                `HTTP ${response.status} (${response.statusText || "Unbekannter Fehler"}) bei ${url}`
            );
        }

        try {
            return await response.json();
        } catch (error) {
            throw new Error(`Ungültiges JSON in ${url}: ${error.message}`);
        }
    }


    // ==========================================
    // ===== 03 - HEADER & FOOTER ===============
    // ==========================================

    async function loadComponent(containerId, url, errorMessage) {
        const container = document.getElementById(containerId);

        if (!container) {
            return false;
        }

        try {
            container.innerHTML = await fetchText(url);
            return true;
        } catch (error) {
            console.error(`Fehler beim Laden von ${url}:`, error);
            showContainerStatus(container, errorMessage, "error");
            return false;
        }
    }


    // ==========================================
    // ===== 04 - SEITENSTRUKTUR & SEMANTIK =====
    // ==========================================

    function initPageStructure() {
        ensureMainLandmark();
        ensureSkipLink();
        ensurePageHeading();
    }

    function ensureMainLandmark() {
        const existingMain = document.querySelector("main");

        if (existingMain) {
            if (!existingMain.id) {
                existingMain.id = "main-content";
            }

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

    function ensureSkipLink() {
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

    function ensurePageHeading() {
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

    function initHeaderAccessibility() {
        const navigation = document.querySelector("#header-container nav");

        if (!navigation) {
            return;
        }

        const currentPath = normalizePagePath(window.location.pathname);

        navigation.querySelectorAll('a[href]').forEach(link => {
            link.removeAttribute("aria-current");

            let linkPath;

            try {
                linkPath = normalizePagePath(
                    new URL(link.href, window.location.origin).pathname
                );
            } catch (error) {
                return;
            }

            if (linkPath === currentPath) {
                link.setAttribute("aria-current", "page");
            }
        });
    }

    function normalizePagePath(pathname) {
        const normalized = String(pathname || "/")
            .replace(/\/index\.html$/i, "/")
            .replace(/\/+$/, "");

        return normalized || "/";
    }

    function initTableSemantics(root = document) {
        const tables = root.querySelectorAll("table");

        tables.forEach(table => {
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


    // ==========================================
    // ===== 04A - STATUSMELDUNGEN ==============
    // ==========================================

    function showContainerStatus(container, message, type = "error") {
        container.innerHTML = "";

        const status = document.createElement("p");
        status.className = `dynamic-status dynamic-status--${type}`;
        status.textContent = message;

        if (type === "error") {
            status.setAttribute("role", "alert");
        } else {
            status.setAttribute("role", "status");
        }

        container.appendChild(status);
    }

    function getTableColumnCount(tbody) {
        const table = tbody.closest("table");

        if (!table) {
            return 1;
        }

        const headerRow = table.tHead?.rows?.[table.tHead.rows.length - 1];

        if (headerRow?.cells?.length) {
            return headerRow.cells.length;
        }

        const firstRow = table.rows?.[0];
        return firstRow?.cells?.length || 1;
    }

    function showTableStatus(tbody, message, type = "error") {
        tbody.innerHTML = "";

        const row = document.createElement("tr");
        row.className = `table-status-row table-status-row--${type}`;

        const cell = document.createElement("td");
        cell.colSpan = getTableColumnCount(tbody);
        cell.textContent = message;

        if (type === "error") {
            cell.setAttribute("role", "alert");
        }

        row.appendChild(cell);
        tbody.appendChild(row);
    }


    // ==========================================
    // ===== 05 - NEWS-SLIDER ===================
    // ==========================================

    async function initNewsSlider() {
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
                showContainerStatus(
                    newsContainer,
                    "Aktuell sind keine Neuigkeiten vorhanden.",
                    "empty"
                );
                return;
            }

            data.forEach((item, index) => {
                const slide = document.createElement("article");
                slide.className = "news-slide";

                if (index === 0) {
                    slide.classList.add("active");
                }

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
            showContainerStatus(
                newsContainer,
                "Die Neuigkeiten konnten nicht geladen werden.",
                "error"
            );
        }
    }

    function startSlider(newsContainer) {
        const slides = Array.from(
            newsContainer.querySelectorAll(".news-slide")
        );

        if (slides.length === 0) {
            return;
        }

        newsContainer.setAttribute("role", "region");
        newsContainer.setAttribute("aria-roledescription", "Karussell");
        newsContainer.setAttribute("aria-label", "Neuigkeiten");

        slides.forEach((slide, slideIndex) => {
            slide.setAttribute("role", "group");
            slide.setAttribute("aria-roledescription", "Folie");
            slide.setAttribute(
                "aria-label",
                `${slideIndex + 1} von ${slides.length}`
            );
        });

        // Bei einem Eintrag sind keine Steuerelemente nötig.
        if (slides.length === 1) {
            setSlideAccessibility(slides[0], true);
            return;
        }

        newsContainer.classList.add("news-slider--controlled");

        const controls = document.createElement("div");
        controls.className = "news-slider__controls";
        controls.setAttribute("aria-label", "Neuigkeiten steuern");

        const previousButton = createSliderButton(
            "‹",
            "Vorherige Neuigkeit",
            "news-slider__button news-slider__button--previous"
        );
        const toggleButton = createSliderButton(
            "Pause",
            "Automatischen Wechsel pausieren",
            "news-slider__button news-slider__button--toggle"
        );
        const status = document.createElement("span");
        status.className = "news-slider__status";
        status.setAttribute("aria-live", "off");
        status.setAttribute("aria-atomic", "true");

        const nextButton = createSliderButton(
            "›",
            "Nächste Neuigkeit",
            "news-slider__button news-slider__button--next"
        );

        controls.append(previousButton, toggleButton, status, nextButton);
        newsContainer.appendChild(controls);

        const reducedMotionQuery = window.matchMedia(
            "(prefers-reduced-motion: reduce)"
        );

        let index = 0;
        let intervalId = null;
        let userPaused = reducedMotionQuery.matches;
        let temporarilyPaused = false;

        function setSlideAccessibility(slide, isActive) {
            slide.classList.toggle("active", isActive);
            slide.setAttribute("aria-hidden", String(!isActive));
            slide.toggleAttribute("inert", !isActive);
        }

        function showSlide(nextIndex, announce = false) {
            index = (nextIndex + slides.length) % slides.length;

            slides.forEach((slide, slideIndex) => {
                setSlideAccessibility(slide, slideIndex === index);
            });

            status.setAttribute("aria-live", announce ? "polite" : "off");
            status.textContent = `${index + 1} / ${slides.length}`;

            if (announce) {
                window.setTimeout(() => {
                    status.setAttribute("aria-live", "off");
                }, 250);
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

                showSlide(index + 1, false);
            }, 10000);
        }

        function updateToggleButton() {
            toggleButton.textContent = userPaused ? "Abspielen" : "Pause";
            toggleButton.setAttribute(
                "aria-label",
                userPaused
                    ? "Automatischen Wechsel starten"
                    : "Automatischen Wechsel pausieren"
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

        showSlide(0, false);
        updateToggleButton();
        syncAutomaticChange();
    }

    function createSliderButton(text, label, className) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = className;
        button.textContent = text;
        button.setAttribute("aria-label", label);
        return button;
    }


    // ==========================================
    // ===== 06 - ANIMATIONEN ===================
    // ==========================================

    function initAnimations(root = document) {
        const scope = root instanceof Element || root instanceof Document
            ? root
            : document;

        const selector =
            ".box:not(.animate), " +
            ".team-box:not(.animate), " +
            ".news-slider:not(.animate), " +
            ".button:not(.animate)";

        const elements = Array.from(scope.querySelectorAll(selector));

        if (scope instanceof Element && scope.matches(selector)) {
            elements.unshift(scope);
        }

        elements.forEach((element, index) => {
            element.style.animationDelay = `${index * 0.2}s`;
            element.classList.add("animate");
        });

        const rows = scope.querySelectorAll(
            ".table-ewigeRangliste tbody tr:not(.animate)"
        );

        rows.forEach((row, index) => {
            row.style.animationDelay = `${index * 0.08}s`;
            row.classList.add("animate");
        });
    }

    function initAnimationObserver() {
        const observer = new MutationObserver(mutations => {
            mutations.forEach(mutation => {
                mutation.addedNodes.forEach(node => {
                    if (!(node instanceof Element)) {
                        return;
                    }

                    initAnimations(node);
                    initTableSemantics(node);
                    initTableScrollContainers(node);
                });
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }


    // ==========================================
    // ===== 07 - TABELLEN-SCROLL & SUCHE =======
    // ==========================================

    function initTableScrollContainers(root = document) {
        const tables = root.querySelectorAll("table");

        tables.forEach(table => {
            if (table.parentElement?.classList.contains("table-scroll")) {
                return;
            }

            // Die Ewige Rangliste ist bereits auf 600 px begrenzt und benötigt
            // keinen zusätzlichen Wrapper.
            if (table.classList.contains("table-ewigeRangliste")) {
                return;
            }

            const wrapper = document.createElement("div");
            wrapper.className = "table-scroll";

            const headerCells = table.tHead?.rows?.[0]?.cells?.length || 0;

            if (headerCells >= 5) {
                wrapper.classList.add("table-scroll--wide");
                wrapper.tabIndex = 0;
                wrapper.setAttribute(
                    "aria-label",
                    "Tabelle kann horizontal gescrollt werden"
                );
            }

            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        });
    }

    function initTableSearch() {
        const input = document.getElementById("searchInput");

        if (!input || input.dataset.searchInitialized === "true") {
            return;
        }

        input.dataset.searchInitialized = "true";

        input.addEventListener("input", () => {
            const search = input.value.trim().toLowerCase();
            const rows = document.querySelectorAll(
                ".table-ewigeRangliste tbody tr"
            );

            rows.forEach(row => {
                const nameCell = row.children[1];

                if (!nameCell) {
                    return;
                }

                const name = nameCell.textContent.toLowerCase();
                row.style.display = name.includes(search) ? "" : "none";
            });
        });
    }


    // ==========================================
    // ===== 08 - THEME SWITCHER ================
    // ==========================================

    function initThemeSwitcher() {
        const switcher = document.getElementById("themeSwitcher");

        if (!switcher || switcher.dataset.themeInitialized === "true") {
            return;
        }

        switcher.dataset.themeInitialized = "true";

        switcher.addEventListener("change", event => {
            document.body.classList.remove("theme-red", "theme-dark");
            document.body.classList.add(`theme-${event.target.value}`);
        });
    }


    // ==========================================
    // ===== 09 - iFRAME CONSENT ================
    // ==========================================

    const iframePlaceholders = new WeakMap();

    function rememberIframePlaceholder(container) {
        if (!iframePlaceholders.has(container)) {
            iframePlaceholders.set(container, container.innerHTML);
        }
    }

    function getIframeProvider(container, src) {
        let hostname = "externer-inhalt";

        try {
            hostname = new URL(src, window.location.href).hostname.toLowerCase();
        } catch (error) {
            console.warn("Die Iframe-URL konnte nicht ausgewertet werden:", src);
        }

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

        return context
            ? `${provider.name} – ${context}`
            : `${provider.name} – externer Inhalt`;
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
        iframe.referrerPolicy = "no-referrer-when-downgrade";
        iframe.allowFullscreen = true;

        const controls = document.createElement("div");
        controls.className = "iframe-embed__controls";

        const status = document.createElement("span");
        status.textContent = `Externer Inhalt von ${provider.name} ist aktiviert.`;

        const revokeButton = document.createElement("button");
        revokeButton.type = "button";
        revokeButton.className = "iframe-revoke-button";
        revokeButton.textContent = "Externe Inhalte deaktivieren";
        revokeButton.addEventListener("click", () => {
            revokeIframeConsent(provider.id);
        });

        controls.append(status, revokeButton);

        container.innerHTML = "";
        container.dataset.providerId = provider.id;
        container.dataset.iframeLoaded = "true";
        container.append(iframe, controls);
    }

    function restoreIframePlaceholder(container) {
        const placeholderHtml = iframePlaceholders.get(container);

        if (typeof placeholderHtml !== "string") {
            return;
        }

        container.innerHTML = placeholderHtml;
        delete container.dataset.iframeLoaded;
    }

    function loadAcceptedIframes(providerId) {
        document.querySelectorAll(".iframe-consent").forEach(container => {
            const src = container.dataset.src;

            if (!src) {
                return;
            }

            const provider = getIframeProvider(container, src);

            if (provider.id === providerId) {
                createIframe(container, src);
            }
        });
    }

    function revokeIframeConsent(providerId) {
        removeStorageValue(getIframeStorageKey(providerId));

        document.querySelectorAll(".iframe-consent").forEach(container => {
            const src = container.dataset.src;

            if (!src) {
                return;
            }

            const provider = getIframeProvider(container, src);

            if (provider.id === providerId) {
                restoreIframePlaceholder(container);
            }
        });
    }

    function initIframeConsent() {
        const containers = Array.from(
            document.querySelectorAll(".iframe-consent")
        );

        if (containers.length === 0) {
            return;
        }

        const legacyConsent = getStorageValue("externalContentAccepted") === "true";

        containers.forEach(container => {
            rememberIframePlaceholder(container);

            const src = container.dataset.src;

            if (!src) {
                return;
            }

            const provider = getIframeProvider(container, src);
            container.dataset.providerId = provider.id;

            if (legacyConsent) {
                setStorageValue(getIframeStorageKey(provider.id), "true");
            }

            if (getStorageValue(getIframeStorageKey(provider.id)) === "true") {
                createIframe(container, src);
            }
        });

        if (legacyConsent) {
            removeStorageValue("externalContentAccepted");
        }

        window.loadIframe = function loadIframe(button) {
            const container = button.closest(".iframe-consent");
            const src = container?.dataset.src;

            if (!container || !src) {
                return;
            }

            const provider = getIframeProvider(container, src);
            setStorageValue(getIframeStorageKey(provider.id), "true");
            loadAcceptedIframes(provider.id);
        };
    }

    function getStorageValue(key) {
        try {
            return window.localStorage.getItem(key);
        } catch (error) {
            console.warn("Local Storage ist nicht verfügbar:", error);
            return null;
        }
    }

    function setStorageValue(key, value) {
        try {
            window.localStorage.setItem(key, value);
        } catch (error) {
            console.warn("Local Storage ist nicht verfügbar:", error);
        }
    }

    function removeStorageValue(key) {
        try {
            window.localStorage.removeItem(key);
        } catch (error) {
            console.warn("Local Storage ist nicht verfügbar:", error);
        }
    }


    // ==========================================
    // ===== 10 - GENERISCHER TABLE LOADER ======
    // ==========================================

    async function loadTable(config) {
        const tbody = document.getElementById(config.targetId);

        if (!tbody) {
            return;
        }

        try {
            const data = await fetchJson(config.url);

            if (!Array.isArray(data)) {
                throw new Error(`${config.url} enthält keine Liste.`);
            }

            tbody.innerHTML = "";

            if (data.length === 0) {
                showTableStatus(
                    tbody,
                    config.emptyMessage || "Aktuell sind keine Daten verfügbar.",
                    "empty"
                );
                return;
            }

            data.forEach(item => {
                const row = document.createElement("tr");
                row.innerHTML = config.render(item);
                tbody.appendChild(row);
            });

            initTableSearch();
            initAnimations(tbody.closest("table") || document);

        } catch (error) {
            console.error(`Fehler bei ${config.url}:`, error);
            showTableStatus(
                tbody,
                config.errorMessage || "Die Daten konnten nicht geladen werden.",
                "error"
            );
        }
    }

    async function loadAllTables() {
        const configs = [...spieleConfigs, ...tabellenConfigs];
        await Promise.allSettled(configs.map(config => loadTable(config)));
    }


    // ==========================================
    // ===== 11 - SPIELE KONFIG =================
    // ==========================================

    const spieleConfigs = [
        {
            targetId: "spiele-startseite",
            url: "/assets/data/spieleStartseite.json",
            emptyMessage: "Aktuell stehen keine Spiele an.",
            errorMessage: "Die nächsten Spiele konnten nicht geladen werden.",
            render: spiel => {
                const istHeimspiel = spiel.heim.includes("Laudenbach");
                const gegner = istHeimspiel ? spiel.gast : spiel.heim;

                return `
                    <td>${spiel.datum}</td>
                    <td>${formatUhrzeit(spiel.uhrzeit)}</td>
                    <td>${getMannschaft(spiel.heim, spiel.gast, spiel.klasse)}</td>
                    <td>${gegner}</td>
                    <td>${getSpielort(spiel.spielort, istHeimspiel)}</td>
                    <td>${getErgebnis(spiel)}</td>
                `;
            }
        },
        createGameConfig("spiele-herren1", "/assets/data/spieleHerren1.json"),
        createGameConfig("spiele-herren2", "/assets/data/spieleHerren2.json"),
        createGameConfig("spiele-herren3", "/assets/data/spieleHerren3.json"),
        createGameConfig("spiele-herren4", "/assets/data/spieleHerren4.json"),
        createGameConfig("spiele-herren5", "/assets/data/spieleHerren5.json"),
        createGameConfig("spiele-jugend1", "/assets/data/spieleJugend1.json"),
        createGameConfig("spiele-jugend2", "/assets/data/spieleJugend2.json")
    ];

    function createGameConfig(targetId, url) {
        return {
            targetId,
            url,
            render: renderStandardSpiele,
            emptyMessage: "Für diese Mannschaft sind aktuell keine Spiele eingetragen.",
            errorMessage: "Der Spielplan konnte nicht geladen werden."
        };
    }

    function renderStandardSpiele(row) {
        const istHeimspiel = row.heim.includes("Laudenbach");
        const gegner = istHeimspiel ? row.gast : row.heim;

        return `
            <td>${row.datum}</td>
            <td>${formatUhrzeit(row.uhrzeit)}</td>
            <td>${getSpielort(row.spielort, istHeimspiel)}</td>
            <td>${gegner}</td>
            <td>${formatErgebnis(row.heim, row.gast, row.ergebnis)}</td>
        `;
    }


    // ==========================================
    // ===== 12 - TABELLEN KONFIG ===============
    // ==========================================

    const tabellenConfigs = [
        createLeagueTableConfig("tabelle-herren1", "/assets/data/tabelleHerren1.json"),
        createLeagueTableConfig("tabelle-herren2", "/assets/data/tabelleHerren2.json"),
        createLeagueTableConfig("tabelle-herren3", "/assets/data/tabelleHerren3.json"),
        createLeagueTableConfig("tabelle-herren4", "/assets/data/tabelleHerren4.json"),
        createLeagueTableConfig("tabelle-herren5", "/assets/data/tabelleHerren5.json"),
        createLeagueTableConfig("tabelle-jugend1", "/assets/data/tabelleJugend1.json"),
        createLeagueTableConfig("tabelle-jugend2", "/assets/data/tabelleJugend2.json")
    ];

    function createLeagueTableConfig(targetId, url) {
        return {
            targetId,
            url,
            render: renderStandardTabelle,
            emptyMessage: "Für diese Liga sind aktuell keine Tabellendaten vorhanden.",
            errorMessage: "Die Ligatabelle konnte nicht geladen werden."
        };
    }

    function renderStandardTabelle(row) {
        return `
            <td>${row.rang}</td>
            <td>${row.mannschaft}</td>
            <td>${row.partien}</td>
            <td>${row.siege}</td>
            <td>${row.unentschieden}</td>
            <td>${row.niederlagen}</td>
            <td>${row.spiele}</td>
            <td>${row.spieleDifferenz}</td>
            <td>${row.punkte}</td>
        `;
    }


    // ==========================================
    // ===== 13 - HILFSFUNKTIONEN ===============
    // ==========================================

    function getMannschaft(heim, gast, klasse) {
        let team = "";

        if (heim.includes("Laudenbach")) {
            team = heim;
        } else if (gast.includes("Laudenbach")) {
            team = gast;
        } else {
            return "-";
        }

        const match = team.match(/(I|II|III|IV|V)$/);
        const nummer = match ? match[0] : "I";

        if (klasse.startsWith("J")) {
            return `Jugend ${nummer}`;
        }

        if (klasse.startsWith("E")) {
            return `Herren ${nummer}`;
        }

        return nummer;
    }

    function getSpielort(code, istHeimspiel) {
        if (!istHeimspiel) {
            return "Auswärtsspiel";
        }

        switch (code) {
            case "1":
                return "Großsporthalle Weikersheim";
            case "2":
                return "Zehntscheune Laudenbach";
            case "3":
                return "Ausweichhalle";
            default:
                return "Unbekannt";
        }
    }

    function formatUhrzeit(uhrzeit) {
        if (!uhrzeit) {
            return "–";
        }

        return String(uhrzeit)
            .replace("\n", " ")
            .replace(/\s+v$/, " v");
    }

    function getErgebnis(spiel) {
        if (spiel.status === "geplant") {
            return "-:-";
        }

        return spiel.ergebnis || "-:-";
    }

    function formatErgebnis(heim, gast, ergebnis) {
        if (!ergebnis) {
            return "-:-";
        }

        const [heimPunkte, gastPunkte] = ergebnis.split(":").map(Number);

        if (!Number.isFinite(heimPunkte) || !Number.isFinite(gastPunkte)) {
            return ergebnis;
        }

        const istHeimspiel = heim.includes("TTF Laudenbach");

        if (istHeimspiel) {
            return `${heimPunkte}:${gastPunkte}`;
        }

        return `${gastPunkte}:${heimPunkte}`;
    }


    // ==========================================
    // ===== 14 - LINKS LOADER ==================
    // ==========================================

    async function loadLinks() {
        try {
            const data = await fetchJson("/assets/data/links.json");

            const tabellen = Array.isArray(data.tabellen) ? data.tabellen : [];
            const spielplaene = Array.isArray(data.spielplaene)
                ? data.spielplaene
                : [];
            const linkGruppen = Array.isArray(data.links) ? data.links : [];

            tabellen.forEach(entry => {
                setLinkTarget(`link-${entry.id}`, entry.url);
            });

            spielplaene.forEach(entry => {
                setLinkTarget(`link-${entry.id}`, entry.url);
            });

            linkGruppen.forEach(gruppe => {
                const container = document.getElementById(
                    `gruppe-${gruppe.gruppe}`
                );

                if (!container) {
                    return;
                }

                container.innerHTML = "";

                const links = Array.isArray(gruppe.links) ? gruppe.links : [];

                if (links.length === 0) {
                    showContainerStatus(
                        container,
                        "Für diesen Bereich sind aktuell keine Links verfügbar.",
                        "empty"
                    );
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

            const sponsorSlots = [
                "sponsor1",
                "sponsor2",
                "sponsor3",
                "sponsor4"
            ];

            linkGruppen.forEach(gruppe => {
                const links = Array.isArray(gruppe.links) ? gruppe.links : [];

                links.forEach(link => {
                    if (!sponsorSlots.includes(link.id)) {
                        return;
                    }

                    [
                        `link-${link.id}`,
                        `link-${link.id}-main`,
                        `link-${link.id}-footer`
                    ].forEach(id => {
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

        if (!element) {
            return;
        }

        element.href = url;
        element.removeAttribute("aria-disabled");
        element.classList.remove("is-disabled");
    }

    function showLinksError() {
        document.querySelectorAll(
            '[id^="gruppe-"]:not([id^="gruppe-link-"])'
        ).forEach(container => {
            showContainerStatus(
                container,
                "Die Linkliste konnte nicht geladen werden.",
                "error"
            );
        });

        document.querySelectorAll(
            '[id^="link-tabelle"], [id^="link-spiele"]'
        ).forEach(link => {
            link.removeAttribute("href");
            link.setAttribute("aria-disabled", "true");
            link.classList.add("is-disabled");
            link.title = "Dieser Link ist momentan nicht verfügbar.";
        });

        ["sponsor1", "sponsor2", "sponsor3", "sponsor4"].forEach(slot => {
            [
                `link-${slot}`,
                `link-${slot}-main`,
                `link-${slot}-footer`
            ].forEach(id => {
                const link = document.getElementById(id);

                if (link) {
                    link.removeAttribute("href");
                    link.setAttribute("aria-disabled", "true");
                    link.classList.add("is-disabled");
                    link.textContent = "Sponsor-Link nicht verfügbar";
                }
            });
        });
    }


    // ==========================================
    // ===== 15 - KONTAKTFORMULAR ===============
    // ==========================================

    function initContactForm() {
        const contactForm = document.getElementById("contactForm");
        const submitButton = document.getElementById("contactSubmitButton");

        if (!contactForm || !submitButton) {
            return;
        }

        function isMobileView() {
            return window.matchMedia("(max-width: 768px)").matches;
        }

        function resetContactForm() {
            contactForm.reset();
            submitButton.classList.remove(
                "is-sending",
                "is-success",
                "is-error"
            );
            submitButton.textContent = "Nachricht senden";
            submitButton.disabled = false;
        }

        contactForm.addEventListener("submit", async event => {
            event.preventDefault();

            if (submitButton.classList.contains("is-success")) {
                resetContactForm();
                return;
            }

            if (submitButton.classList.contains("is-error")) {
                submitButton.classList.remove("is-error");
                submitButton.textContent = "Nachricht senden";
            }

            const formData = new FormData(contactForm);

            submitButton.disabled = true;
            submitButton.classList.remove("is-success", "is-error");
            submitButton.classList.add("is-sending");
            submitButton.textContent = "Wird gesendet...";

            try {
                const response = await fetch(contactForm.action, {
                    method: contactForm.method,
                    body: formData,
                    headers: {
                        Accept: "application/json"
                    }
                });

                submitButton.classList.remove("is-sending");

                if (response.ok) {
                    if (isMobileView()) {
                        alert("Vielen Dank! Ihre Nachricht wurde erfolgreich gesendet.");
                        resetContactForm();
                    } else {
                        submitButton.classList.add("is-success");
                        submitButton.textContent = "✓ Gesendet – Weitere Nachricht senden?";
                        submitButton.disabled = false;
                    }
                } else if (isMobileView()) {
                    alert("Beim Senden ist ein Fehler aufgetreten.");
                    submitButton.textContent = "Nachricht senden";
                    submitButton.disabled = false;
                } else {
                    submitButton.classList.add("is-error");
                    submitButton.textContent = "✗ Fehler – Erneut versuchen?";
                    submitButton.disabled = false;
                }

            } catch (error) {
                console.error("Fehler beim Senden des Kontaktformulars:", error);
                submitButton.classList.remove("is-sending");

                if (isMobileView()) {
                    alert("Es konnte keine Verbindung hergestellt werden.");
                    submitButton.textContent = "Nachricht senden";
                    submitButton.disabled = false;
                } else {
                    submitButton.classList.add("is-error");
                    submitButton.textContent = "✗ Verbindungsfehler – Erneut versuchen?";
                    submitButton.disabled = false;
                }
            }
        });
    }


    // ==========================================
    // ===== 16 - HISTORISCHE FOTOS =============
    // ==========================================

    async function initHistoricalImages() {
        const galleryContainer = document.getElementById(
            "images-gallery-container"
        );
        const eventList = document.getElementById("images-event-list");
        const loadingBox = document.getElementById("images-loading");

        if (!galleryContainer || !eventList) {
            return;
        }

        try {
            const data = await fetchJson("/assets/data/gallerie.json");
            const galleries = Array.isArray(data.galleries)
                ? data.galleries
                : [];
            const defaultGalleryId = data.defaultGallery || "general";

            if (galleries.length === 0) {
                showContainerStatus(
                    galleryContainer,
                    "Keine Bilder gefunden.",
                    "empty"
                );
                eventList.innerHTML = "";
                hideLoadingBox(loadingBox);
                return;
            }

            function renderGallery(galleryId) {
                const gallery = galleries.find(item => item.id === galleryId);

                if (!gallery) {
                    showContainerStatus(
                        galleryContainer,
                        "Die ausgewählte Galerie wurde nicht gefunden.",
                        "error"
                    );
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

                const images = Array.isArray(gallery.images)
                    ? gallery.images
                    : [];

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

                document
                    .querySelectorAll(".images-event-button")
                    .forEach(button => {
                        button.classList.toggle(
                            "is-active",
                            button.dataset.target === gallery.id
                        );
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

                if (gallery.id === defaultGalleryId) {
                    button.classList.add("is-active");
                }

                button.addEventListener("click", () => {
                    renderGallery(gallery.id);
                });

                eventList.appendChild(button);
            });

            const initialGallery = galleries.some(
                gallery => gallery.id === defaultGalleryId
            )
                ? defaultGalleryId
                : galleries[0].id;

            renderGallery(initialGallery);

        } catch (error) {
            console.error("Fehler beim Laden der gallerie.json:", error);
            showContainerStatus(
                galleryContainer,
                "Die Bilder konnten nicht geladen werden.",
                "error"
            );
            eventList.innerHTML = "";
            hideLoadingBox(loadingBox);
        }
    }

    function hideLoadingBox(loadingBox) {
        if (loadingBox) {
            loadingBox.style.display = "none";
        }
    }


    // ==========================================
    // ===== 17 - SPIELERLISTEN =================
    // ==========================================

    async function initSpielerliste() {
        const tbody = document.getElementById("spieler-mannschaft");

        if (!tbody) {
            return;
        }

        const datei = tbody.dataset.datei;
        const mannschaft = tbody.dataset.mannschaft;

        if (!datei || !mannschaft) {
            console.error(
                "Spielerliste kann nicht geladen werden: " +
                "data-datei oder data-mannschaft fehlt."
            );
            showSpielerlisteError(
                tbody,
                "Die Spielerliste ist nicht korrekt konfiguriert."
            );
            return;
        }

        try {
            const spielerlisten = await fetchJson(datei);
            const spieler = spielerlisten[mannschaft];

            if (!Array.isArray(spieler)) {
                throw new Error(
                    `Mannschaft "${mannschaft}" wurde in ${datei} nicht gefunden.`
                );
            }

            renderSpielerliste(tbody, spieler);

        } catch (error) {
            console.error(
                `Fehler beim Laden der Spielerliste "${mannschaft}":`,
                error
            );
            showSpielerlisteError(
                tbody,
                "Die Spielerliste konnte nicht geladen werden."
            );
        }
    }

    function renderSpielerliste(tbody, spieler) {
        tbody.innerHTML = "";

        if (spieler.length === 0) {
            showTableStatus(
                tbody,
                "Für diese Mannschaft sind aktuell keine Spieler eingetragen.",
                "empty"
            );
            return;
        }

        const sortierteSpieler = [...spieler].sort((a, b) => {
            return Number(a.position) - Number(b.position);
        });

        sortierteSpieler.forEach(eintrag => {
            const row = document.createElement("tr");
            const positionCell = document.createElement("td");
            const nameCell = document.createElement("td");
            const qttrCell = document.createElement("td");

            positionCell.textContent = eintrag.position
                ? `${eintrag.position}.`
                : "–";
            nameCell.textContent = eintrag.name || "Unbekannt";
            qttrCell.textContent = eintrag.qttr || "–";

            row.append(positionCell, nameCell, qttrCell);
            tbody.appendChild(row);
        });
    }

    function showSpielerlisteError(tbody, message) {
        showTableStatus(tbody, message, "error");
    }


    initializePage().catch(error => {
        console.error("Unerwarteter Fehler bei der Seiteninitialisierung:", error);
    });
});
