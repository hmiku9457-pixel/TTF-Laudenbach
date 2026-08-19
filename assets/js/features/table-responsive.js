const SUPPORTED_TABLE_TYPES = new Set(["next-games", "league", "schedule"]);

const LEAGUE_COLUMN_NAMES = [
    "rank",
    "team",
    "matches",
    "wins",
    "draws",
    "losses",
    "games",
    "difference",
    "points"
];
const NEXT_GAMES_COLUMN_NAMES = [
    "date",
    "time",
    "team",
    "opponent",
    "venue",
    "result"
];
const SCHEDULE_COLUMN_NAMES = [
    "date",
    "time",
    "venue",
    "opponent",
    "result"
];

export function initTableScrollContainers(configs, root = document) {
    const responsiveTypes = new Map(
        configs.map(config => [config.targetId, config.responsiveType])
    );

    root.querySelectorAll("table").forEach(table => {
        const targetId = table.tBodies?.[0]?.id || "";
        const tableType = responsiveTypes.get(targetId) || null;

        configureResponsiveTable(table, tableType);

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

export function refreshResponsiveTable(table, tableType) {
    configureResponsiveTable(table, tableType);

    if (table?.parentElement?.classList.contains("table-scroll")) {
        syncTableWrapper(table.parentElement, table);
    }
}

function syncTableWrapper(wrapper, table) {
    const headerCells = table.tHead?.rows?.[0]?.cells?.length || 0;
    const isCompactTable = table.classList.contains("table-compact-mobile");

    wrapper.classList.toggle(
        "table-scroll--wide",
        headerCells >= 5 && !isCompactTable
    );
    wrapper.classList.toggle("table-scroll--compact", isCompactTable);

    if (headerCells >= 5 && !isCompactTable) {
        wrapper.tabIndex = 0;
        wrapper.setAttribute("aria-label", "Tabelle kann horizontal gescrollt werden");
    } else {
        wrapper.removeAttribute("tabindex");
        wrapper.removeAttribute("aria-label");
    }
}

function configureResponsiveTable(table, tableType) {
    if (!table || !SUPPORTED_TABLE_TYPES.has(tableType)) {
        return;
    }

    resetResponsiveClasses(table);
    table.classList.add(
        "table-compact-mobile",
        `table-compact-mobile--${tableType}`
    );

    if (tableType === "next-games") {
        prepareNextGamesTable(table);
    } else if (tableType === "league") {
        prepareLeagueTable(table);
    } else if (tableType === "schedule") {
        prepareScheduleTable(table);
    }

    syncStatusRowColspan(table);
    initVenueTooltipInteractions();
}

function resetResponsiveClasses(table) {
    [
        "table-compact-mobile",
        "table-compact-mobile--next-games",
        "table-compact-mobile--league",
        "table-compact-mobile--schedule"
    ].forEach(className => table.classList.remove(className));
}

function prepareLeagueTable(table) {
    const headerRow = table.tHead?.rows?.[0];
    if (!headerRow) {
        return;
    }

    const desktopHeaders = Array.from(headerRow.cells)
        .filter(cell => !cell.classList.contains("table-mobile-only"));
    if (desktopHeaders.length < LEAGUE_COLUMN_NAMES.length) {
        return;
    }

    applyColumnClasses(desktopHeaders, LEAGUE_COLUMN_NAMES);
    ensureDualHeaderLabel(desktopHeaders[1], "Team");

    let recordHeader = headerRow.querySelector(".table-mobile-only--record");
    if (!recordHeader) {
        recordHeader = document.createElement("th");
        recordHeader.scope = "col";
        recordHeader.className = "table-mobile-only table-mobile-only--record table-col--record";
        recordHeader.textContent = "S-U-N";
        headerRow.insertBefore(recordHeader, headerRow.cells[2] || null);
    }

    table.tBodies[0]?.querySelectorAll("tr:not(.table-status-row)").forEach(row => {
        const originalCells = Array.from(row.cells)
            .filter(cell => !cell.classList.contains("table-mobile-only"));
        if (originalCells.length < LEAGUE_COLUMN_NAMES.length) {
            return;
        }

        applyColumnClasses(originalCells, LEAGUE_COLUMN_NAMES);

        let recordCell = row.querySelector(".table-mobile-only--record");
        if (!recordCell) {
            recordCell = document.createElement("td");
            recordCell.className =
                "table-mobile-only table-mobile-only--record table-col--record";
            recordCell.textContent = [
                normalizedCellText(originalCells[3]),
                normalizedCellText(originalCells[4]),
                normalizedCellText(originalCells[5])
            ].join("-");
            row.insertBefore(recordCell, originalCells[2] || null);
        } else {
            recordCell.classList.add("table-col--record");
        }
    });
}

function prepareNextGamesTable(table) {
    const headerRow = table.tHead?.rows?.[0];
    if (headerRow) {
        ensureDualHeaderLabel(headerRow.cells[0], "Dat.");
        ensureDualHeaderLabel(headerRow.cells[1], "Zeit");
        ensureDualHeaderLabel(headerRow.cells[2], "Team");
        ensureDualHeaderLabel(headerRow.cells[3], "Geg.");
        ensureDualHeaderLabel(headerRow.cells[4], "H/A");
        ensureDualHeaderLabel(headerRow.cells[5], "Erg.");
        applyColumnClasses(Array.from(headerRow.cells), NEXT_GAMES_COLUMN_NAMES);
    }

    const targetId = table.tBodies?.[0]?.id || "next-games";
    table.tBodies[0]?.querySelectorAll("tr:not(.table-status-row)")
        .forEach((row, rowIndex) => {
            const cells = Array.from(row.cells);
            if (cells.length < 5) {
                return;
            }

            applyColumnClasses(cells, NEXT_GAMES_COLUMN_NAMES);

            ensureDualValue(
                cells[0],
                compactDate(normalizedCellText(cells[0]))
            );
            ensureDualValue(
                cells[2],
                abbreviateTeam(normalizedCellText(cells[2]))
            );
            ensureVenueCell(cells[4], targetId, rowIndex);
        });
}

function prepareScheduleTable(table) {
    const headerRow = table.tHead?.rows?.[0];
    if (!headerRow) {
        return;
    }

    const desktopHeaders = Array.from(headerRow.cells)
        .filter(cell => !cell.classList.contains("table-mobile-only"));
    if (desktopHeaders.length < SCHEDULE_COLUMN_NAMES.length) {
        return;
    }

    applyColumnClasses(desktopHeaders, SCHEDULE_COLUMN_NAMES);
    ensureDualHeaderLabel(desktopHeaders[0], "Dat.");
    ensureDualHeaderLabel(desktopHeaders[1], "Zeit");
    ensureDualHeaderLabel(desktopHeaders[4], "Erg.");

    let opponentHeader = headerRow.querySelector(
        ".table-mobile-only--schedule-opponent"
    );
    let venueHeader = headerRow.querySelector(
        ".table-mobile-only--schedule-venue"
    );

    if (!opponentHeader) {
        opponentHeader = document.createElement("th");
        opponentHeader.scope = "col";
        opponentHeader.className =
            "table-mobile-only table-mobile-only--schedule-opponent table-col--opponent";
        opponentHeader.textContent = "Geg.";
        headerRow.insertBefore(opponentHeader, desktopHeaders[2]);
    }

    if (!venueHeader) {
        venueHeader = document.createElement("th");
        venueHeader.scope = "col";
        venueHeader.className =
            "table-mobile-only table-mobile-only--schedule-venue table-col--venue";
        venueHeader.textContent = "H/A";
        headerRow.insertBefore(venueHeader, desktopHeaders[2]);
    }

    const targetId = table.tBodies?.[0]?.id || "schedule";
    table.tBodies[0]?.querySelectorAll("tr:not(.table-status-row)")
        .forEach((row, rowIndex) => {
            const desktopCells = Array.from(row.cells)
                .filter(cell => !cell.classList.contains("table-mobile-only"));
            if (desktopCells.length < SCHEDULE_COLUMN_NAMES.length) {
                return;
            }

            applyColumnClasses(desktopCells, SCHEDULE_COLUMN_NAMES);

            ensureDualValue(
                desktopCells[0],
                compactDate(normalizedCellText(desktopCells[0]))
            );

            let opponentCell = row.querySelector(
                ".table-mobile-only--schedule-opponent"
            );
            let venueCell = row.querySelector(
                ".table-mobile-only--schedule-venue"
            );

            if (!opponentCell) {
                opponentCell = document.createElement("td");
                opponentCell.className =
                    "table-mobile-only table-mobile-only--schedule-opponent table-col--opponent";
                opponentCell.textContent = normalizedCellText(desktopCells[3]);
                row.insertBefore(opponentCell, desktopCells[2]);
            }

            if (!venueCell) {
                venueCell = document.createElement("td");
                venueCell.className =
                    "table-mobile-only table-mobile-only--schedule-venue table-col--venue";
                venueCell.textContent = normalizedCellText(desktopCells[2]);
                row.insertBefore(venueCell, desktopCells[2]);
            }

            ensureVenueCell(venueCell, targetId, rowIndex);
        });
}

function ensureDualHeaderLabel(cell, mobileText) {
    if (!cell || cell.querySelector(".responsive-label--mobile")) {
        return;
    }

    const desktopText = cell.textContent.trim();
    cell.textContent = "";

    const desktop = document.createElement("span");
    desktop.className = "responsive-label responsive-label--desktop";
    desktop.textContent = desktopText;

    const mobile = document.createElement("span");
    mobile.className = "responsive-label responsive-label--mobile";
    mobile.textContent = mobileText;

    cell.append(desktop, mobile);
}

function ensureDualValue(cell, mobileText) {
    if (!cell || cell.querySelector(".responsive-value--mobile")) {
        return;
    }

    const desktopText = normalizedCellText(cell);
    cell.textContent = "";

    const desktop = document.createElement("span");
    desktop.className = "responsive-value responsive-value--desktop";
    desktop.textContent = desktopText;

    const mobile = document.createElement("span");
    mobile.className = "responsive-value responsive-value--mobile";
    mobile.textContent = mobileText || desktopText;

    cell.append(desktop, mobile);
}

function ensureVenueCell(cell, tableId, rowIndex) {
    if (!cell || cell.querySelector(".venue-compact")) {
        return;
    }

    const fullLocation = normalizedCellText(cell);
    const isAway = /auswärt/i.test(fullLocation);
    const badgeText = isAway ? "A" : "H";
    const badgeLabel = isAway ? "A – Auswärtsspiel" : "H – Heimspiel";
    const tooltipText = isAway
        ? "Spielort beim gegnerischen Verein"
        : fullLocation || "Spielort noch nicht bekannt";
    const tooltipId = `venue-tooltip-${sanitizeId(tableId)}-${rowIndex + 1}`;

    cell.textContent = "";

    const desktop = document.createElement("span");
    desktop.className = "venue-full";
    desktop.textContent = fullLocation || "–";

    const compact = document.createElement("span");
    compact.className = "venue-compact";

    const badge = document.createElement("button");
    badge.type = "button";
    badge.className = `venue-badge venue-badge--${isAway ? "away" : "home"}`;
    badge.textContent = badgeText;
    badge.setAttribute("aria-label", badgeLabel);
    badge.setAttribute("aria-describedby", tooltipId);
    badge.setAttribute("aria-expanded", "false");

    const tooltip = document.createElement("span");
    tooltip.id = tooltipId;
    tooltip.className = "venue-tooltip";
    tooltip.setAttribute("role", "tooltip");
    tooltip.textContent = tooltipText;

    compact.append(badge, tooltip);
    cell.append(desktop, compact);
}

function initVenueTooltipInteractions() {
    if (document.documentElement.dataset.venueTooltipsInitialized === "true") {
        return;
    }

    document.documentElement.dataset.venueTooltipsInitialized = "true";

    document.addEventListener("click", event => {
        const badge = event.target.closest(".venue-badge");
        const currentWrapper = badge?.closest(".venue-compact") || null;
        const shouldOpen = currentWrapper && !currentWrapper.classList.contains("is-open");

        closeVenueTooltips();

        if (shouldOpen) {
            currentWrapper.classList.add("is-open");
            badge.setAttribute("aria-expanded", "true");
        }
    });

    document.addEventListener("keydown", event => {
        if (event.key !== "Escape") {
            return;
        }

        const openBadge = document.querySelector(".venue-compact.is-open .venue-badge");
        closeVenueTooltips();
        openBadge?.focus();
    });
}

function closeVenueTooltips() {
    document.querySelectorAll(".venue-compact.is-open").forEach(wrapper => {
        wrapper.classList.remove("is-open");
        wrapper.querySelector(".venue-badge")?.setAttribute("aria-expanded", "false");
    });
}

function syncStatusRowColspan(table) {
    const headerCount = table.tHead?.rows?.[0]?.cells?.length || 1;
    table.querySelectorAll(".table-status-row td").forEach(cell => {
        cell.colSpan = headerCount;
    });
}

function applyColumnClasses(cells, columnNames) {
    cells.forEach((cell, index) => {
        Array.from(cell.classList)
            .filter(className => className.startsWith("table-col--"))
            .forEach(className => cell.classList.remove(className));

        const columnName = columnNames[index];
        if (columnName) {
            cell.classList.add(`table-col--${columnName}`);
        }
    });
}

function normalizedCellText(cell) {
    return String(cell?.textContent || "").replace(/\s+/g, " ").trim();
}

function compactDate(value) {
    return String(value || "")
        .replace(/(\d{2}\.\d{2}\.)\d{4}/, "$1")
        .replace(/\s+/g, " ")
        .trim();
}

function abbreviateTeam(value) {
    const normalized = String(value || "").trim();
    const numberMap = {
        "1": "I",
        "2": "II",
        "3": "III",
        "4": "IV",
        "5": "V"
    };
    const match = normalized.match(/^(Herren|Jugend)\s+([IVX]+|\d+)$/i);
    if (!match) {
        return normalized;
    }

    const prefix = /^herren$/i.test(match[1]) ? "H" : "J";
    const number = numberMap[match[2]] || match[2].toUpperCase();
    return `${prefix} ${number}`;
}

function sanitizeId(value) {
    return String(value || "table")
        .toLowerCase()
        .replace(/[^a-z0-9_-]+/g, "-")
        .replace(/^-+|-+$/g, "") || "table";
}
