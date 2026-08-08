import { fetchJson } from "../core/http.js";
import { showTableStatus } from "../core/status.js";
import { spieleConfigs, tabellenConfigs } from "../config/table-configs.js";
import { initAnimations } from "./animations.js";

export function initTableScrollContainers(root = document) {
    root.querySelectorAll("table").forEach(table => {
        configureResponsiveTable(table);

        if (table.parentElement?.classList.contains("table-scroll")) {
            syncTableWrapper(table.parentElement, table);
            return;
        }
        if (table.classList.contains("table-ewigeRangliste")) {
            return;
        }

        const wrapper = document.createElement("div");
        wrapper.className = "table-scroll";
        table.parentNode.insertBefore(wrapper, table);
        wrapper.appendChild(table);
        syncTableWrapper(wrapper, table);
    });
}

function syncTableWrapper(wrapper, table) {
    const headerCells = table.tHead?.rows?.[0]?.cells?.length || 0;
    const isCardTable = table.classList.contains("table-mobile-cards");

    wrapper.classList.toggle("table-scroll--wide", headerCells >= 5);
    wrapper.classList.toggle("table-scroll--cards", isCardTable);

    if (headerCells >= 5 && !isCardTable) {
        wrapper.tabIndex = 0;
        wrapper.setAttribute("aria-label", "Tabelle kann horizontal gescrollt werden");
    } else {
        wrapper.removeAttribute("tabindex");
        wrapper.removeAttribute("aria-label");
    }
}

function configureResponsiveTable(table) {
    if (!table) {
        return;
    }

    const targetId = table.tBodies?.[0]?.id || "";
    const tableType = getResponsiveTableType(targetId);
    if (!tableType) {
        return;
    }

    table.classList.add("table-mobile-cards", `table-mobile-cards--${tableType}`);
    decorateTableCells(table);
}

function getResponsiveTableType(targetId) {
    if (targetId === "spiele-startseite") {
        return "next-games";
    }
    if (/^spiele-(?:herren|jugend)\d+$/i.test(targetId)) {
        return "schedule";
    }
    if (/^tabelle-(?:herren|jugend)\d+$/i.test(targetId)) {
        return "league";
    }
    return null;
}

function decorateTableCells(table) {
    const labels = Array.from(table.tHead?.rows?.[0]?.cells || [])
        .map(cell => cell.textContent.trim().replace(/:$/, ""));

    table.tBodies[0]?.querySelectorAll("tr:not(.table-status-row)").forEach(row => {
        Array.from(row.cells).forEach((cell, index) => {
            cell.dataset.label = labels[index] || `Spalte ${index + 1}`;
        });
    });
}

export function initTableSearch() {
    const input = document.getElementById("searchInput");
    if (!input || input.dataset.searchInitialized === "true") {
        return;
    }

    input.dataset.searchInitialized = "true";
    input.addEventListener("input", () => {
        const search = input.value.trim().toLowerCase();
        document.querySelectorAll(".table-ewigeRangliste tbody tr")
            .forEach(row => {
                const nameCell = row.children[1];
                if (nameCell) {
                    row.style.display = nameCell.textContent.toLowerCase().includes(search)
                        ? ""
                        : "none";
                }
            });
    });
}

export async function loadTable(config) {
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
            configureResponsiveTable(tbody.closest("table"));
            return;
        }

        data.forEach(item => {
            const row = document.createElement("tr");
            const cells = config.cells(item);

            cells.forEach(value => {
                const cell = document.createElement("td");
                cell.textContent = value ?? "–";
                row.appendChild(cell);
            });
            tbody.appendChild(row);
        });

        const table = tbody.closest("table");
        configureResponsiveTable(table);
        if (table?.parentElement?.classList.contains("table-scroll")) {
            syncTableWrapper(table.parentElement, table);
        }

        initTableSearch();
        initAnimations(table || document);
    } catch (error) {
        console.error(`Fehler bei ${config.url}:`, error);
        showTableStatus(
            tbody,
            config.errorMessage || "Die Daten konnten nicht geladen werden.",
            "error"
        );
        configureResponsiveTable(tbody.closest("table"));
    }
}

export async function loadAllTables() {
    const configs = [...spieleConfigs, ...tabellenConfigs];
    await Promise.allSettled(configs.map(config => loadTable(config)));
}
