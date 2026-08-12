import { fetchJson } from "../core/http.js";
import { showTableStatus } from "../core/status.js";
import { spieleConfigs, tabellenConfigs } from "../config/table-configs.js";
import {
    initTableScrollContainers as initResponsiveTableScrollContainers,
    refreshResponsiveTable
} from "./table-responsive.js";

const TABLE_CONFIGS = [...spieleConfigs, ...tabellenConfigs];

export function initTableScrollContainers(root = document) {
    initResponsiveTableScrollContainers(TABLE_CONFIGS, root);
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

    const table = tbody.closest("table");

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
    } catch (error) {
        console.error(`Fehler bei ${config.url}:`, error);
        showTableStatus(
            tbody,
            config.errorMessage || "Die Daten konnten nicht geladen werden.",
            "error"
        );
    } finally {
        refreshResponsiveTable(table, config.responsiveType);
    }
}

export async function loadAllTables() {
    await Promise.allSettled(TABLE_CONFIGS.map(config => loadTable(config)));
}
