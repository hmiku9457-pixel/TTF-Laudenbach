import { fetchJson } from "../core/http.js";
import { showTableStatus } from "../core/status.js";
import { spieleConfigs, tabellenConfigs } from "../config/table-configs.js";
import { initAnimations } from "./animations.js";

export function initTableScrollContainers(root = document) {
    root.querySelectorAll("table").forEach(table => {
        if (table.parentElement?.classList.contains("table-scroll")) {
            return;
        }

        if (table.classList.contains("table-ewigeRangliste")) {
            return;
        }

        const wrapper = document.createElement("div");
        wrapper.className = "table-scroll";
        const headerCells = table.tHead?.rows?.[0]?.cells?.length || 0;

        if (headerCells >= 5) {
            wrapper.classList.add("table-scroll--wide");
            wrapper.tabIndex = 0;
            wrapper.setAttribute("aria-label", "Tabelle kann horizontal gescrollt werden");
        }

        table.parentNode.insertBefore(wrapper, table);
        wrapper.appendChild(table);
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

export async function loadAllTables() {
    const configs = [...spieleConfigs, ...tabellenConfigs];
    await Promise.allSettled(configs.map(config => loadTable(config)));
}
