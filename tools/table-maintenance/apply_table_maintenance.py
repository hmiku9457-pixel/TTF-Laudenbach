#!/usr/bin/env python3
"""Wartbarkeits-Cleanup für den Tabellenbereich der TTF-Laudenbach-Webseite.

Das Script ist absichtlich dauerhaft und idempotent. Es löscht sich nicht selbst.
Es setzt den geprüften Zielzustand für Priorität 1 + 2 des Tabellen-Cleanups um.

Aufruf:
    python tools/table-maintenance/apply_table_maintenance.py
    python tools/table-maintenance/apply_table_maintenance.py --check
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]

TARGETS = {
    'assets/js/features/tables.js': 'import { fetchJson } from "../core/http.js";\nimport { showTableStatus } from "../core/status.js";\nimport { spieleConfigs, tabellenConfigs } from "../config/table-configs.js";\nimport {\n    initTableScrollContainers as initResponsiveTableScrollContainers,\n    refreshResponsiveTable\n} from "./table-responsive.js";\n\nconst TABLE_CONFIGS = [...spieleConfigs, ...tabellenConfigs];\n\nexport function initTableScrollContainers(root = document) {\n    initResponsiveTableScrollContainers(TABLE_CONFIGS, root);\n}\n\nexport function initTableSearch() {\n    const input = document.getElementById("searchInput");\n    if (!input || input.dataset.searchInitialized === "true") {\n        return;\n    }\n\n    input.dataset.searchInitialized = "true";\n    input.addEventListener("input", () => {\n        const search = input.value.trim().toLowerCase();\n        document.querySelectorAll(".table-ewigeRangliste tbody tr")\n            .forEach(row => {\n                const nameCell = row.children[1];\n                if (nameCell) {\n                    row.style.display = nameCell.textContent.toLowerCase().includes(search)\n                        ? ""\n                        : "none";\n                }\n            });\n    });\n}\n\nexport async function loadTable(config) {\n    const tbody = document.getElementById(config.targetId);\n    if (!tbody) {\n        return;\n    }\n\n    const table = tbody.closest("table");\n\n    try {\n        const data = await fetchJson(config.url);\n        if (!Array.isArray(data)) {\n            throw new Error(`${config.url} enthält keine Liste.`);\n        }\n\n        tbody.innerHTML = "";\n        if (data.length === 0) {\n            showTableStatus(\n                tbody,\n                config.emptyMessage || "Aktuell sind keine Daten verfügbar.",\n                "empty"\n            );\n            return;\n        }\n\n        data.forEach(item => {\n            const row = document.createElement("tr");\n            const cells = config.cells(item);\n            cells.forEach(value => {\n                const cell = document.createElement("td");\n                cell.textContent = value ?? "–";\n                row.appendChild(cell);\n            });\n\n            tbody.appendChild(row);\n        });\n    } catch (error) {\n        console.error(`Fehler bei ${config.url}:`, error);\n        showTableStatus(\n            tbody,\n            config.errorMessage || "Die Daten konnten nicht geladen werden.",\n            "error"\n        );\n    } finally {\n        refreshResponsiveTable(table, config.responsiveType);\n    }\n}\n\nexport async function loadAllTables() {\n    await Promise.allSettled(TABLE_CONFIGS.map(config => loadTable(config)));\n}\n',
    'assets/js/features/table-responsive.js': 'const SUPPORTED_TABLE_TYPES = new Set(["next-games", "league", "schedule"]);\n\nexport function initTableScrollContainers(configs, root = document) {\n    const responsiveTypes = new Map(\n        configs.map(config => [config.targetId, config.responsiveType])\n    );\n\n    root.querySelectorAll("table").forEach(table => {\n        const targetId = table.tBodies?.[0]?.id || "";\n        const tableType = responsiveTypes.get(targetId) || null;\n\n        configureResponsiveTable(table, tableType);\n\n        if (table.parentElement?.classList.contains("table-scroll")) {\n            syncTableWrapper(table.parentElement, table);\n            return;\n        }\n\n        if (table.classList.contains("table-ewigeRangliste")) {\n            return;\n        }\n\n        const wrapper = document.createElement("div");\n        wrapper.className = "table-scroll";\n        table.parentNode.insertBefore(wrapper, table);\n        wrapper.appendChild(table);\n        syncTableWrapper(wrapper, table);\n    });\n}\n\nexport function refreshResponsiveTable(table, tableType) {\n    configureResponsiveTable(table, tableType);\n\n    if (table?.parentElement?.classList.contains("table-scroll")) {\n        syncTableWrapper(table.parentElement, table);\n    }\n}\n\nfunction syncTableWrapper(wrapper, table) {\n    const headerCells = table.tHead?.rows?.[0]?.cells?.length || 0;\n    const isCompactTable = table.classList.contains("table-compact-mobile");\n\n    wrapper.classList.toggle(\n        "table-scroll--wide",\n        headerCells >= 5 && !isCompactTable\n    );\n    wrapper.classList.toggle("table-scroll--compact", isCompactTable);\n\n    if (headerCells >= 5 && !isCompactTable) {\n        wrapper.tabIndex = 0;\n        wrapper.setAttribute("aria-label", "Tabelle kann horizontal gescrollt werden");\n    } else {\n        wrapper.removeAttribute("tabindex");\n        wrapper.removeAttribute("aria-label");\n    }\n}\n\nfunction configureResponsiveTable(table, tableType) {\n    if (!table || !SUPPORTED_TABLE_TYPES.has(tableType)) {\n        return;\n    }\n\n    resetResponsiveClasses(table);\n    table.classList.add(\n        "table-compact-mobile",\n        `table-compact-mobile--${tableType}`\n    );\n\n    if (tableType === "next-games") {\n        prepareNextGamesTable(table);\n    } else if (tableType === "league") {\n        prepareLeagueTable(table);\n    } else if (tableType === "schedule") {\n        prepareScheduleTable(table);\n    }\n\n    syncStatusRowColspan(table);\n    initVenueTooltipInteractions();\n}\n\nfunction resetResponsiveClasses(table) {\n    [\n        "table-compact-mobile",\n        "table-compact-mobile--next-games",\n        "table-compact-mobile--league",\n        "table-compact-mobile--schedule"\n    ].forEach(className => table.classList.remove(className));\n}\n\nfunction prepareLeagueTable(table) {\n    const headerRow = table.tHead?.rows?.[0];\n    if (!headerRow) {\n        return;\n    }\n\n    ensureDualHeaderLabel(headerRow.cells[1], "Team");\n\n    let recordHeader = headerRow.querySelector(".table-mobile-only--record");\n    if (!recordHeader) {\n        recordHeader = document.createElement("th");\n        recordHeader.scope = "col";\n        recordHeader.className = "table-mobile-only table-mobile-only--record";\n        recordHeader.textContent = "S-U-N";\n        headerRow.insertBefore(recordHeader, headerRow.cells[2] || null);\n    }\n\n    table.tBodies[0]?.querySelectorAll("tr:not(.table-status-row)").forEach(row => {\n        if (row.querySelector(".table-mobile-only--record")) {\n            return;\n        }\n\n        const originalCells = Array.from(row.cells);\n        if (originalCells.length < 9) {\n            return;\n        }\n\n        const recordCell = document.createElement("td");\n        recordCell.className = "table-mobile-only table-mobile-only--record";\n        recordCell.textContent = [\n            normalizedCellText(originalCells[3]),\n            normalizedCellText(originalCells[4]),\n            normalizedCellText(originalCells[5])\n        ].join("-");\n\n        row.insertBefore(recordCell, originalCells[2] || null);\n    });\n}\n\nfunction prepareNextGamesTable(table) {\n    const headerRow = table.tHead?.rows?.[0];\n    if (headerRow) {\n        ensureDualHeaderLabel(headerRow.cells[0], "Dat.");\n        ensureDualHeaderLabel(headerRow.cells[1], "Zeit");\n        ensureDualHeaderLabel(headerRow.cells[2], "Team");\n        ensureDualHeaderLabel(headerRow.cells[3], "Geg.");\n        ensureDualHeaderLabel(headerRow.cells[4], "H/A");\n        ensureDualHeaderLabel(headerRow.cells[5], "Erg.");\n    }\n\n    const targetId = table.tBodies?.[0]?.id || "next-games";\n    table.tBodies[0]?.querySelectorAll("tr:not(.table-status-row)")\n        .forEach((row, rowIndex) => {\n            const cells = Array.from(row.cells);\n            if (cells.length < 6) {\n                return;\n            }\n\n            ensureDualValue(\n                cells[0],\n                compactDate(normalizedCellText(cells[0]))\n            );\n            ensureDualValue(\n                cells[2],\n                abbreviateTeam(normalizedCellText(cells[2]))\n            );\n            ensureVenueCell(cells[4], targetId, rowIndex);\n        });\n}\n\nfunction prepareScheduleTable(table) {\n    const headerRow = table.tHead?.rows?.[0];\n    if (!headerRow) {\n        return;\n    }\n\n    const desktopHeaders = Array.from(headerRow.cells)\n        .filter(cell => !cell.classList.contains("table-mobile-only"));\n    if (desktopHeaders.length < 5) {\n        return;\n    }\n\n    ensureDualHeaderLabel(desktopHeaders[0], "Dat.");\n    ensureDualHeaderLabel(desktopHeaders[1], "Zeit");\n    ensureDualHeaderLabel(desktopHeaders[4], "Erg.");\n\n    let opponentHeader = headerRow.querySelector(\n        ".table-mobile-only--schedule-opponent"\n    );\n    let venueHeader = headerRow.querySelector(\n        ".table-mobile-only--schedule-venue"\n    );\n\n    if (!opponentHeader) {\n        opponentHeader = document.createElement("th");\n        opponentHeader.scope = "col";\n        opponentHeader.className =\n            "table-mobile-only table-mobile-only--schedule-opponent";\n        opponentHeader.textContent = "Geg.";\n        headerRow.insertBefore(opponentHeader, desktopHeaders[2]);\n    }\n\n    if (!venueHeader) {\n        venueHeader = document.createElement("th");\n        venueHeader.scope = "col";\n        venueHeader.className =\n            "table-mobile-only table-mobile-only--schedule-venue";\n        venueHeader.textContent = "H/A";\n        headerRow.insertBefore(venueHeader, desktopHeaders[2]);\n    }\n\n    const targetId = table.tBodies?.[0]?.id || "schedule";\n    table.tBodies[0]?.querySelectorAll("tr:not(.table-status-row)")\n        .forEach((row, rowIndex) => {\n            const desktopCells = Array.from(row.cells)\n                .filter(cell => !cell.classList.contains("table-mobile-only"));\n            if (desktopCells.length < 5) {\n                return;\n            }\n\n            ensureDualValue(\n                desktopCells[0],\n                compactDate(normalizedCellText(desktopCells[0]))\n            );\n\n            let opponentCell = row.querySelector(\n                ".table-mobile-only--schedule-opponent"\n            );\n            let venueCell = row.querySelector(\n                ".table-mobile-only--schedule-venue"\n            );\n\n            if (!opponentCell) {\n                opponentCell = document.createElement("td");\n                opponentCell.className =\n                    "table-mobile-only table-mobile-only--schedule-opponent";\n                opponentCell.textContent = normalizedCellText(desktopCells[3]);\n                row.insertBefore(opponentCell, desktopCells[2]);\n            }\n\n            if (!venueCell) {\n                venueCell = document.createElement("td");\n                venueCell.className =\n                    "table-mobile-only table-mobile-only--schedule-venue";\n                venueCell.textContent = normalizedCellText(desktopCells[2]);\n                row.insertBefore(venueCell, desktopCells[2]);\n            }\n\n            ensureVenueCell(venueCell, targetId, rowIndex);\n        });\n}\n\nfunction ensureDualHeaderLabel(cell, mobileText) {\n    if (!cell || cell.querySelector(".responsive-label--mobile")) {\n        return;\n    }\n\n    const desktopText = cell.textContent.trim();\n    cell.textContent = "";\n\n    const desktop = document.createElement("span");\n    desktop.className = "responsive-label responsive-label--desktop";\n    desktop.textContent = desktopText;\n\n    const mobile = document.createElement("span");\n    mobile.className = "responsive-label responsive-label--mobile";\n    mobile.textContent = mobileText;\n\n    cell.append(desktop, mobile);\n}\n\nfunction ensureDualValue(cell, mobileText) {\n    if (!cell || cell.querySelector(".responsive-value--mobile")) {\n        return;\n    }\n\n    const desktopText = normalizedCellText(cell);\n    cell.textContent = "";\n\n    const desktop = document.createElement("span");\n    desktop.className = "responsive-value responsive-value--desktop";\n    desktop.textContent = desktopText;\n\n    const mobile = document.createElement("span");\n    mobile.className = "responsive-value responsive-value--mobile";\n    mobile.textContent = mobileText || desktopText;\n\n    cell.append(desktop, mobile);\n}\n\nfunction ensureVenueCell(cell, tableId, rowIndex) {\n    if (!cell || cell.querySelector(".venue-compact")) {\n        return;\n    }\n\n    const fullLocation = normalizedCellText(cell);\n    const isAway = /auswärt/i.test(fullLocation);\n    const badgeText = isAway ? "A" : "H";\n    const detailText = isAway\n        ? "Auswärtsspiel – Spielort beim gegnerischen Verein"\n        : `Heimspiel – ${fullLocation || "Spielort noch nicht bekannt"}`;\n    const tooltipId = `venue-tooltip-${sanitizeId(tableId)}-${rowIndex + 1}`;\n\n    cell.textContent = "";\n\n    const desktop = document.createElement("span");\n    desktop.className = "venue-full";\n    desktop.textContent = fullLocation || "–";\n\n    const compact = document.createElement("span");\n    compact.className = "venue-compact";\n\n    const badge = document.createElement("button");\n    badge.type = "button";\n    badge.className = `venue-badge venue-badge--${isAway ? "away" : "home"}`;\n    badge.textContent = badgeText;\n    badge.setAttribute("aria-label", detailText);\n    badge.setAttribute("aria-describedby", tooltipId);\n    badge.setAttribute("aria-expanded", "false");\n\n    const tooltip = document.createElement("span");\n    tooltip.id = tooltipId;\n    tooltip.className = "venue-tooltip";\n    tooltip.setAttribute("role", "tooltip");\n    tooltip.textContent = detailText;\n\n    compact.append(badge, tooltip);\n    cell.append(desktop, compact);\n}\n\nfunction initVenueTooltipInteractions() {\n    if (document.documentElement.dataset.venueTooltipsInitialized === "true") {\n        return;\n    }\n\n    document.documentElement.dataset.venueTooltipsInitialized = "true";\n\n    document.addEventListener("click", event => {\n        const badge = event.target.closest(".venue-badge");\n        const currentWrapper = badge?.closest(".venue-compact") || null;\n        const shouldOpen = currentWrapper && !currentWrapper.classList.contains("is-open");\n\n        closeVenueTooltips();\n\n        if (shouldOpen) {\n            currentWrapper.classList.add("is-open");\n            badge.setAttribute("aria-expanded", "true");\n        }\n    });\n\n    document.addEventListener("keydown", event => {\n        if (event.key !== "Escape") {\n            return;\n        }\n\n        const openBadge = document.querySelector(".venue-compact.is-open .venue-badge");\n        closeVenueTooltips();\n        openBadge?.focus();\n    });\n}\n\nfunction closeVenueTooltips() {\n    document.querySelectorAll(".venue-compact.is-open").forEach(wrapper => {\n        wrapper.classList.remove("is-open");\n        wrapper.querySelector(".venue-badge")?.setAttribute("aria-expanded", "false");\n    });\n}\n\nfunction syncStatusRowColspan(table) {\n    const headerCount = table.tHead?.rows?.[0]?.cells?.length || 1;\n    table.querySelectorAll(".table-status-row td").forEach(cell => {\n        cell.colSpan = headerCount;\n    });\n}\n\nfunction normalizedCellText(cell) {\n    return String(cell?.textContent || "").replace(/\\s+/g, " ").trim();\n}\n\nfunction compactDate(value) {\n    return String(value || "")\n        .replace(/(\\d{2}\\.\\d{2}\\.)\\d{4}/, "$1")\n        .replace(/\\s+/g, " ")\n        .trim();\n}\n\nfunction abbreviateTeam(value) {\n    const normalized = String(value || "").trim();\n    const numberMap = {\n        "1": "I",\n        "2": "II",\n        "3": "III",\n        "4": "IV",\n        "5": "V"\n    };\n    const match = normalized.match(/^(Herren|Jugend)\\s+([IVX]+|\\d+)$/i);\n    if (!match) {\n        return normalized;\n    }\n\n    const prefix = /^herren$/i.test(match[1]) ? "H" : "J";\n    const number = numberMap[match[2]] || match[2].toUpperCase();\n    return `${prefix} ${number}`;\n}\n\nfunction sanitizeId(value) {\n    return String(value || "table")\n        .toLowerCase()\n        .replace(/[^a-z0-9_-]+/g, "-")\n        .replace(/^-+|-+$/g, "") || "table";\n}\n',
    'assets/js/config/table-configs.js': 'import {\n    formatErgebnis,\n    formatUhrzeit,\n    getErgebnis,\n    getMannschaft,\n    getSpielort\n} from "../utils/game-formatters.js";\n\nconst text = value => value == null ? "" : String(value);\n\nfunction createGameConfig(targetId, url) {\n    return {\n        targetId,\n        url,\n        responsiveType: "schedule",\n        cells: row => {\n            const heim = text(row?.heim);\n            const gast = text(row?.gast);\n            const istHeimspiel = heim.includes("Laudenbach");\n            const gegner = istHeimspiel ? gast : heim;\n            return [\n                text(row?.datum),\n                formatUhrzeit(text(row?.uhrzeit)),\n                getSpielort(text(row?.spielort), istHeimspiel),\n                gegner,\n                formatErgebnis(heim, gast, text(row?.ergebnis))\n            ];\n        },\n        emptyMessage: "Für diese Mannschaft sind aktuell keine Spiele eingetragen.",\n        errorMessage: "Der Spielplan konnte nicht geladen werden."\n    };\n}\n\nfunction createLeagueTableConfig(targetId, url) {\n    return {\n        targetId,\n        url,\n        responsiveType: "league",\n        cells: row => [\n            text(row?.rang),\n            text(row?.mannschaft),\n            text(row?.partien),\n            text(row?.siege),\n            text(row?.unentschieden),\n            text(row?.niederlagen),\n            text(row?.spiele),\n            text(row?.spieleDifferenz),\n            text(row?.punkte)\n        ],\n        emptyMessage: "Für diese Liga sind aktuell keine Tabellendaten vorhanden.",\n        errorMessage: "Die Ligatabelle konnte nicht geladen werden."\n    };\n}\n\nexport const spieleConfigs = [\n    {\n        targetId: "spiele-startseite",\n        url: "/assets/data/spieleStartseite.json",\n        responsiveType: "next-games",\n        cells: spiel => {\n            const heim = text(spiel?.heim);\n            const gast = text(spiel?.gast);\n            const istHeimspiel = heim.includes("Laudenbach");\n            const gegner = istHeimspiel ? gast : heim;\n            return [\n                text(spiel?.datum),\n                formatUhrzeit(text(spiel?.uhrzeit)),\n                getMannschaft(heim, gast, text(spiel?.klasse)),\n                gegner,\n                getSpielort(text(spiel?.spielort), istHeimspiel),\n                getErgebnis({ ...spiel, heim, gast })\n            ];\n        },\n        emptyMessage: "Aktuell stehen keine Spiele an.",\n        errorMessage: "Die nächsten Spiele konnten nicht geladen werden."\n    },\n    createGameConfig("spiele-herren1", "/assets/data/spieleHerren1.json"),\n    createGameConfig("spiele-herren2", "/assets/data/spieleHerren2.json"),\n    createGameConfig("spiele-herren3", "/assets/data/spieleHerren3.json"),\n    createGameConfig("spiele-herren4", "/assets/data/spieleHerren4.json"),\n    createGameConfig("spiele-herren5", "/assets/data/spieleHerren5.json"),\n    createGameConfig("spiele-jugend1", "/assets/data/spieleJugend1.json"),\n    createGameConfig("spiele-jugend2", "/assets/data/spieleJugend2.json")\n];\n\nexport const tabellenConfigs = [\n    createLeagueTableConfig("tabelle-herren1", "/assets/data/tabelleHerren1.json"),\n    createLeagueTableConfig("tabelle-herren2", "/assets/data/tabelleHerren2.json"),\n    createLeagueTableConfig("tabelle-herren3", "/assets/data/tabelleHerren3.json"),\n    createLeagueTableConfig("tabelle-herren4", "/assets/data/tabelleHerren4.json"),\n    createLeagueTableConfig("tabelle-herren5", "/assets/data/tabelleHerren5.json"),\n    createLeagueTableConfig("tabelle-jugend1", "/assets/data/tabelleJugend1.json"),\n    createLeagueTableConfig("tabelle-jugend2", "/assets/data/tabelleJugend2.json")\n];\n',
    'assets/css/components/tables.css': '/* Tabellen, responsive Spieltabellen und ewige Rangliste. */\n\n/* =========================================\n   ===== TABELLEN: BASIS ====================\n   ========================================= */\n\ntable {\n    width: 100%;\n    border-collapse: collapse;\n    margin-top: var(--space-m);\n}\n\ntd,\nth {\n    padding: var(--space-m);\n    text-align: left;\n    border-bottom: 1px solid #334155;\n}\n\ntable thead th {\n    color: var(--accent);\n}\n\ntable tbody th {\n    color: var(--text-main);\n    font-weight: 400;\n}\n\ntable.table--emphasis-first-column tbody th {\n    color: var(--text-main);\n    font-weight: 600;\n}\n\ntable tr:hover {\n    background: rgba(56, 189, 248, 0.1);\n}\n\n/* Lade-, Leer- und Fehlerzustände innerhalb dynamischer Tabellen. */\n.table-status-row td {\n    text-align: center;\n    font-weight: 500;\n}\n\n.table-status-row--error td {\n    color: var(--text-main);\n    background: rgba(198, 40, 40, 0.18);\n}\n\n.table-status-row--empty td {\n    color: var(--text-muted);\n}\n\n/* =========================================\n   ===== TABELLEN: SCROLL-CONTAINER =========\n   ========================================= */\n\n.table-scroll {\n    width: 100%;\n    max-width: 100%;\n    margin-top: var(--space-m);\n    overflow-x: auto;\n    overscroll-behavior-inline: contain;\n    -webkit-overflow-scrolling: touch;\n}\n\n.table-scroll > table {\n    margin-top: 0;\n}\n\n.table-scroll--wide > table {\n    min-width: 700px;\n}\n\n.table-scroll--wide:focus-visible {\n    outline: 2px solid var(--accent);\n    outline-offset: 3px;\n    border-radius: var(--space-s);\n}\n\n/* =========================================\n   ===== SPIELTABELLEN: RESPONSIVE HILFEN ===\n   ========================================= */\n\n.responsive-label--mobile,\n.responsive-value--mobile,\n.table-mobile-only,\n.venue-compact {\n    display: none;\n}\n\n.venue-compact {\n    position: relative;\n    align-items: center;\n    justify-content: center;\n}\n\n.venue-badge {\n    display: inline-grid;\n    place-items: center;\n    width: 1.75rem;\n    height: 1.75rem;\n    padding: 0;\n    border: 1px solid var(--accent);\n    border-radius: 999px;\n    background: rgba(56, 189, 248, 0.12);\n    color: var(--accent);\n    font: inherit;\n    font-size: 0.78rem;\n    font-weight: 800;\n    line-height: 1;\n    cursor: help;\n}\n\n.venue-badge--away {\n    border-color: #94a3b8;\n    background: rgba(148, 163, 184, 0.12);\n    color: #cbd5e1;\n}\n\n.venue-tooltip {\n    position: absolute;\n    z-index: 4300;\n    right: 0;\n    bottom: calc(100% + 0.5rem);\n    width: max-content;\n    max-width: min(250px, 76vw);\n    padding: 0.55rem 0.7rem;\n    border: 1px solid #475569;\n    border-radius: 0.5rem;\n    background: #020617;\n    color: #e2e8f0;\n    box-shadow: var(--shadow-light);\n    font-size: 0.8rem;\n    font-weight: 400;\n    line-height: 1.35;\n    text-align: left;\n    white-space: normal;\n    opacity: 0;\n    visibility: hidden;\n    pointer-events: none;\n    transform: translateY(0.25rem);\n    transition:\n        opacity 0.16s ease,\n        transform 0.16s ease,\n        visibility 0.16s ease;\n}\n\n.venue-compact:hover .venue-tooltip,\n.venue-compact:focus-within .venue-tooltip,\n.venue-compact.is-open .venue-tooltip {\n    opacity: 1;\n    visibility: visible;\n    transform: translateY(0);\n}\n\n/* =========================================\n   ===== EWIGE RANGLISTE ====================\n   ========================================= */\n\n.table-ewigeRangliste {\n    width: 100%;\n    max-width: 680px;\n    margin: 2rem auto;\n    border: 1px solid #334155;\n    border-collapse: separate;\n    border-spacing: 0;\n    border-radius: var(--space-m);\n    overflow: hidden;\n    background: rgba(15, 23, 42, 0.52);\n    box-shadow: var(--shadow-light);\n    font-family: Arial, sans-serif;\n    font-size: 0.95rem;\n}\n\n.table-ewigeRangliste thead {\n    background: rgba(56, 189, 248, 0.12);\n}\n\n.table-ewigeRangliste thead th {\n    padding: 0.7rem 0.75rem;\n    border-bottom: 1px solid #475569;\n    color: var(--accent);\n    font-weight: 700;\n    letter-spacing: 0.01em;\n    text-align: left;\n}\n\n.table-ewigeRangliste tbody tr {\n    background: rgba(15, 23, 42, 0.36);\n    opacity: 1;\n    transform: none;\n}\n\n.table-ewigeRangliste tbody th[scope="row"],\n.table-ewigeRangliste tbody td {\n    padding: 0.62rem 0.75rem;\n    border-bottom: 1px solid rgba(71, 85, 105, 0.72);\n    background: transparent;\n    color: var(--text-main);\n    line-height: 1.3;\n}\n\n.table-ewigeRangliste tbody th[scope="row"] {\n    width: 16%;\n    text-align: left;\n    font-weight: 700;\n}\n\n/* Fallback für ältere Ranglisten-Zeilen ohne semantisches Zeilen-TH. */\n.table-ewigeRangliste tbody td:first-child {\n    width: 70px;\n    text-align: center;\n    font-weight: 700;\n}\n\n.table-ewigeRangliste tbody td:nth-child(2) {\n    width: 64%;\n    text-align: left;\n}\n\n.table-ewigeRangliste tbody td:last-child {\n    width: 20%;\n    text-align: right;\n    font-weight: 600;\n}\n\n.table-ewigeRangliste tbody tr:last-child > * {\n    border-bottom: 0;\n}\n\n.table-ewigeRangliste tbody tr:hover {\n    background: rgba(56, 189, 248, 0.09);\n    transition: background-color 0.2s ease;\n}\n\n.table-search {\n    display: block;\n    width: 100%;\n    max-width: 680px;\n    margin: 1rem auto;\n    padding: 0.5rem;\n    border: 1px solid #475569;\n    border-radius: var(--space-s);\n    background: #f8fafc;\n    color: #0f172a;\n    font-size: 1rem;\n}\n\n.table-ewigeRangliste tbody tr.ranking-fade-ready {\n    animation: rankingReverseFade 0.16s ease-out both;\n    animation-delay: var(--ranking-fade-delay, 0ms);\n}\n\n@keyframes rankingReverseFade {\n    from {\n        opacity: 0.72;\n        transform: translateY(2px);\n    }\n    to {\n        opacity: 1;\n        transform: translateY(0);\n    }\n}\n\n/* =========================================\n   ===== KOMPAKTE TABELLEN BIS 768 PX =======\n   ========================================= */\n\n@media (max-width: 768px) {\n    .table-scroll--compact {\n        width: 100%;\n        max-width: 100%;\n        overflow: visible;\n        overscroll-behavior: auto;\n    }\n\n    .table-scroll--compact > table.table-compact-mobile {\n        width: 100%;\n        max-width: 100%;\n        min-width: 0;\n    }\n\n    table.table-compact-mobile {\n        display: table;\n        width: 100%;\n        min-width: 0;\n        table-layout: fixed;\n        font-size: clamp(0.68rem, 2.25vw, 0.82rem);\n    }\n\n    table.table-compact-mobile > thead {\n        display: table-header-group;\n        position: static;\n        width: auto;\n        height: auto;\n        margin: 0;\n        overflow: visible;\n        clip: auto;\n        white-space: normal;\n    }\n\n    table.table-compact-mobile > thead > tr {\n        display: table-row;\n        width: auto;\n    }\n\n    table.table-compact-mobile > tbody {\n        display: table-row-group;\n        width: auto;\n    }\n\n    table.table-compact-mobile > tbody > tr {\n        display: table-row;\n        width: auto;\n        padding: 0;\n        border: 0;\n        border-radius: 0;\n        background: transparent;\n        box-shadow: none;\n    }\n\n    table.table-compact-mobile > thead th,\n    table.table-compact-mobile > tbody td {\n        display: table-cell;\n        min-width: 0;\n        box-sizing: border-box;\n        padding: 0.55rem 0.25rem;\n        overflow-wrap: anywhere;\n        hyphens: auto;\n        vertical-align: middle;\n    }\n\n    table.table-compact-mobile > thead th {\n        overflow-wrap: normal;\n        word-break: normal;\n        hyphens: none;\n        white-space: nowrap;\n        line-height: 1.2;\n    }\n\n    table.table-compact-mobile > tbody td::before {\n        content: none;\n    }\n\n    table.table-compact-mobile .responsive-label--desktop,\n    table.table-compact-mobile .responsive-value--desktop,\n    table.table-compact-mobile .venue-full {\n        display: none;\n    }\n\n    table.table-compact-mobile .responsive-label--mobile,\n    table.table-compact-mobile .responsive-value--mobile {\n        display: inline;\n    }\n\n    table.table-compact-mobile .venue-compact {\n        display: inline-flex;\n    }\n\n    /* Ligatabelle: Rang | Team | S-U-N | Spiele | +/- | Punkte */\n    table.table-compact-mobile--league .table-mobile-only {\n        display: table-cell;\n    }\n\n    table.table-compact-mobile--league :is(th, td):nth-child(4),\n    table.table-compact-mobile--league :is(th, td):nth-child(5),\n    table.table-compact-mobile--league :is(th, td):nth-child(6),\n    table.table-compact-mobile--league :is(th, td):nth-child(7) {\n        display: none;\n    }\n\n    table.table-compact-mobile--league :is(th, td):nth-child(1) {\n        width: 8%;\n        text-align: left;\n    }\n\n    table.table-compact-mobile--league :is(th, td):nth-child(2) {\n        width: 35%;\n        text-align: left;\n    }\n\n    table.table-compact-mobile--league :is(th, td):nth-child(3) {\n        width: 14%;\n        text-align: center;\n        white-space: nowrap;\n    }\n\n    table.table-compact-mobile--league :is(th, td):nth-child(8) {\n        width: 16%;\n        text-align: center;\n        white-space: nowrap;\n    }\n\n    table.table-compact-mobile--league :is(th, td):nth-child(9) {\n        width: 11%;\n        text-align: center;\n        white-space: nowrap;\n    }\n\n    table.table-compact-mobile--league :is(th, td):nth-child(10) {\n        width: 16%;\n        text-align: right;\n        white-space: nowrap;\n    }\n\n    /* Startseite: Dat. | Zeit | Team | Geg. | H/A | Erg. */\n    table.table-compact-mobile--next-games :is(th, td):nth-child(1) {\n        width: 18%;\n        text-align: left;\n    }\n\n    table.table-compact-mobile--next-games :is(th, td):nth-child(2) {\n        width: 14%;\n        text-align: center;\n        white-space: nowrap;\n    }\n\n    table.table-compact-mobile--next-games :is(th, td):nth-child(3) {\n        width: 13%;\n        text-align: left;\n        white-space: nowrap;\n    }\n\n    table.table-compact-mobile--next-games :is(th, td):nth-child(4) {\n        width: 31%;\n        text-align: left;\n    }\n\n    table.table-compact-mobile--next-games :is(th, td):nth-child(5) {\n        width: 10%;\n        overflow: visible;\n        text-align: center;\n    }\n\n    table.table-compact-mobile--next-games :is(th, td):nth-child(6) {\n        width: 14%;\n        text-align: right;\n        white-space: nowrap;\n    }\n\n    /* Mannschaftsspielplan: Dat. | Zeit | Geg. | H/A | Erg. */\n    table.table-compact-mobile--schedule .table-mobile-only {\n        display: table-cell;\n    }\n\n    table.table-compact-mobile--schedule :is(th, td):nth-child(5),\n    table.table-compact-mobile--schedule :is(th, td):nth-child(6) {\n        display: none;\n    }\n\n    table.table-compact-mobile--schedule :is(th, td):nth-child(1) {\n        width: 19%;\n        text-align: left;\n    }\n\n    table.table-compact-mobile--schedule :is(th, td):nth-child(2) {\n        width: 15%;\n        text-align: center;\n        white-space: nowrap;\n    }\n\n    table.table-compact-mobile--schedule :is(th, td):nth-child(3) {\n        width: 38%;\n        text-align: left;\n    }\n\n    table.table-compact-mobile--schedule :is(th, td):nth-child(4) {\n        width: 11%;\n        overflow: visible;\n        text-align: center;\n    }\n\n    table.table-compact-mobile--schedule :is(th, td):nth-child(7) {\n        width: 17%;\n        text-align: right;\n        white-space: nowrap;\n    }\n\n    table.table-compact-mobile .table-status-row {\n        display: table-row;\n    }\n\n    table.table-compact-mobile .table-status-row td {\n        display: table-cell;\n        text-align: center;\n    }\n}\n\n/* =========================================\n   ===== WEITERE MOBILE ANPASSUNGEN =========\n   ========================================= */\n\n@media (max-width: 600px) {\n    .table-search {\n        max-width: 100%;\n    }\n}\n\n@media (max-width: 480px) {\n    table {\n        font-size: 0.85rem;\n    }\n\n    td,\n    th {\n        padding: var(--space-s);\n    }\n\n    table.table-compact-mobile {\n        font-size: clamp(0.63rem, 2.6vw, 0.76rem);\n    }\n\n    table.table-compact-mobile > thead th {\n        font-size: clamp(0.64rem, 2.65vw, 0.74rem);\n        letter-spacing: 0;\n    }\n\n    table.table-compact-mobile > tbody td,\n    table.table-compact-mobile > thead th {\n        padding: 0.5rem 0.16rem;\n    }\n\n    table.table-compact-mobile--next-games :is(th, td),\n    table.table-compact-mobile--schedule :is(th, td) {\n        padding-inline: 0.12rem;\n    }\n\n    .venue-badge {\n        width: 1.55rem;\n        height: 1.55rem;\n        font-size: 0.7rem;\n    }\n\n    .venue-tooltip {\n        right: -1rem;\n        max-width: min(220px, 82vw);\n    }\n}\n\n@media (prefers-reduced-motion: reduce) {\n    .venue-tooltip {\n        transition: none;\n    }\n\n    .table-ewigeRangliste tbody tr.ranking-fade-ready {\n        animation: none;\n    }\n}\n',
    'assets/css/components/page-content.css': '/* Seitenüberschriften, Seiteneinstieg und allgemeine Inhaltsregeln. */\n\n:root {\n    --link-visited: #a5b4fc;\n    --link-visited-hover: #c7d2fe;\n}\n\nhtml,\nbody {\n    max-width: 100%;\n}\n\nmain :where(p, li, dd, figcaption, label) a:not(.button):not(.read-more):visited {\n    color: var(--link-visited);\n}\n\nmain :where(p, li, dd, figcaption, label) a:not(.button):not(.read-more):visited:hover,\nmain :where(p, li, dd, figcaption, label) a:not(.button):not(.read-more):visited:focus-visible {\n    color: var(--link-visited-hover);\n}\n\n/* Sichtbarer, klar priorisierter Seiteneinstieg. */\n.page-heading {\n    margin: 0 0 var(--space-l);\n    text-align: center;\n    text-wrap: balance;\n}\n\n.home-intro {\n    margin: var(--space-l) var(--space-xl) 0;\n    padding: clamp(var(--space-l), 3vw, var(--space-xxl));\n    border: 1px solid rgba(56, 189, 248, 0.28);\n    border-radius: var(--space-m);\n    background: linear-gradient(135deg, rgba(56, 189, 248, 0.12), rgba(15, 23, 42, 0.38));\n    box-shadow: var(--shadow-light);\n    text-align: center;\n}\n\n.home-intro .page-heading {\n    margin-bottom: var(--space-s);\n}\n\n.home-intro__lead {\n    max-width: 68ch;\n    margin: 0 auto var(--space-l);\n    color: var(--text-muted);\n    font-size: clamp(1rem, 1.5vw, 1.15rem);\n}\n\n.home-intro__actions {\n    display: flex;\n    flex-wrap: wrap;\n    justify-content: center;\n    gap: var(--space-m);\n}\n\n@media (max-width: 768px) {\n    .home-intro {\n        margin: var(--space-m) var(--space-m) 0;\n    }\n\n    .home-intro__actions > * {\n        width: 100%;\n    }\n}\n',
    'assets/css/components/robustness.css': '/* Einheitliche Status- und Fallback-Zustände für dynamische Inhalte. */\n\n.dynamic-status {\n    width: 100%;\n    padding: var(--space-l);\n    border-radius: var(--space-m);\n    text-align: center;\n}\n\n.dynamic-status--error {\n    color: var(--text-main);\n    background: rgba(198, 40, 40, 0.18);\n    border: 1px solid var(--error);\n}\n\n.dynamic-status--empty {\n    color: var(--text-main);\n    background: rgba(100, 116, 139, 0.18);\n    border: 1px solid var(--text-muted);\n}\n\n.news-slider > .dynamic-status {\n    min-height: 250px;\n    display: grid;\n    place-items: center;\n}\n\n/* Nicht verfügbare dynamische Links */\na.is-disabled {\n    opacity: 0.65;\n    cursor: not-allowed;\n    pointer-events: none;\n}\n',
    'assets/css/responsive.css': '/* Responsive Anpassungen für das allgemeine Seitenlayout. */\n\n/* =========================================\n   ===== 17. RESPONSIVE / MOBILE ===========\n   ========================================= */\n\n/* Große Tablets / kleinere Laptops */\n@media (max-width: 1024px) {\n    .grid-home-firstLine,\n    .grid-home-secondLine {\n        grid-template-columns: 1fr;\n    }\n\n    .menu {\n        gap: var(--space-m);\n    }\n\n    .menu a {\n        font-size: 0.95rem;\n    }\n}\n\n/* Tablet / kleine Bildschirme */\n@media (max-width: 768px) {\n    #header-container,\n    header {\n        padding: var(--space-l) var(--space-m);\n    }\n\n    .logo {\n        position: static;\n        transform: none;\n        height: 60px;\n        margin-bottom: var(--space-s);\n    }\n\n    .menu {\n        flex-direction: row;\n        flex-wrap: wrap;\n        align-items: center;\n        justify-content: center;\n        gap: var(--space-s) var(--space-m);\n    }\n\n    .submenu {\n        position: absolute;\n        top: 100%;\n        left: 50%;\n        transform: translateX(-50%) translateY(-10px);\n        white-space: nowrap;\n        box-shadow: var(--shadow-heavy);\n        z-index: 2000;\n    }\n\n    .dropdown:hover .submenu,\n    .dropdown:focus-within .submenu {\n        transform: translateX(-50%) translateY(0);\n    }\n\n    .grid,\n    .grid-home-firstLine,\n    .grid-home-secondLine,\n    .full-width,\n    .grid-button,\n    .teams-grid {\n        grid-template-columns: 1fr;\n        padding-left: var(--space-m);\n        padding-right: var(--space-m);\n    }\n\n    .news-slider {\n        min-height: 320px;\n    }\n\n    .footer {\n        grid-template-columns: 1fr;\n        gap: var(--space-m);\n    }\n\n    .footer-links {\n        flex-wrap: wrap;\n    }\n\n    .content.images-page {\n        grid-template-columns: 1fr;\n    }\n\n    .images-event-list {\n        position: static;\n        order: -1;\n    }\n\n    .masonry-gallery {\n        column-count: 2;\n    }\n}\n\n/* Sehr kleine Handys */\n@media (max-width: 480px) {\n    .box,\n    .team-box,\n    .contact-form {\n        padding: var(--space-l);\n    }\n\n    .grid-button {\n        grid-template-columns: 1fr;\n    }\n\n    .button--card {\n        padding: var(--space-l);\n    }\n\n    .map-container iframe {\n        height: 220px;\n    }\n\n    .masonry-gallery {\n        column-count: 1;\n    }\n}\n',
}

OLD_STATE_MARKERS = {
    "assets/js/features/tables.js": [
        "const CARD_TABLE_TYPES = new Set();",
        "function decorateTableCells(table)",
        'import { initAnimations } from "./animations.js";',
    ],
    "assets/css/components/tables.css": [
        "table.table-mobile-cards",
        "TTF:INTEGRATED:tables",
        "TTF:MOBILE-TABLE-VISIBILITY",
    ],
    "assets/css/components/page-content.css": [
        "@keyframes rankingReverseFade",
        ".responsive-label--mobile",
    ],
    "assets/css/components/robustness.css": [
        ".table-scroll",
        ".table-status-row",
    ],
    "assets/css/responsive.css": [
        ".table-ewigeRangliste",
        ".table-search",
    ],
}


def read(path: str) -> str:
    file_path = ROOT / path
    return file_path.read_text(encoding="utf-8") if file_path.exists() else ""


def is_fully_applied() -> bool:
    return all(read(path) == content for path, content in TARGETS.items())


def validate_source_state() -> None:
    """Verhindert ein blindes Überschreiben eines unbekannten Tabellenstands."""
    if is_fully_applied():
        return

    problems: list[str] = []
    required_existing = [
        "assets/js/features/tables.js",
        "assets/js/config/table-configs.js",
        "assets/css/components/tables.css",
        "assets/css/components/page-content.css",
        "assets/css/components/robustness.css",
        "assets/css/responsive.css",
    ]

    for path in required_existing:
        if not (ROOT / path).exists():
            problems.append(f"Fehlt: {path}")

    for path, markers in OLD_STATE_MARKERS.items():
        source = read(path)
        if source == TARGETS.get(path, ""):
            continue
        missing = [marker for marker in markers if marker not in source]
        if missing:
            problems.append(
                f"{path}: erwartete Altstand-Marker fehlen: {', '.join(missing)}"
            )

    responsive_path = ROOT / "assets/js/features/table-responsive.js"
    if responsive_path.exists() and read("assets/js/features/table-responsive.js") != TARGETS[
        "assets/js/features/table-responsive.js"
    ]:
        problems.append(
            "assets/js/features/table-responsive.js existiert bereits mit unbekanntem Inhalt."
        )

    if problems:
        print("Der Repository-Stand passt nicht sicher zum erwarteten Ausgangszustand:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        print(
            "Abbruch ohne Änderungen. Bitte den aktuellen Tabellenstand zuerst prüfen.",
            file=sys.stderr,
        )
        raise SystemExit(2)


def write_target(path: str, content: str) -> bool:
    file_path = ROOT / path
    old = file_path.read_text(encoding="utf-8") if file_path.exists() else None
    if old == content:
        return False
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8", newline="\n")
    return True


def validate_final_state() -> None:
    problems: list[str] = []

    for path, expected in TARGETS.items():
        actual = read(path)
        if actual != expected:
            problems.append(f"{path}: entspricht nicht dem geprüften Zielzustand")

    tables_js = read("assets/js/features/tables.js")
    responsive_js = read("assets/js/features/table-responsive.js")
    config_js = read("assets/js/config/table-configs.js")
    tables_css = read("assets/css/components/tables.css")
    page_css = read("assets/css/components/page-content.css")
    robustness_css = read("assets/css/components/robustness.css")
    responsive_css = read("assets/css/responsive.css")

    forbidden = {
        "assets/js/features/tables.js": [
            "CARD_TABLE_TYPES",
            "decorateTableCells",
            "initAnimations",
            "getResponsiveTableType",
        ],
        "assets/js/features/table-responsive.js": [
            "table-mobile-cards",
            "CARD_TABLE_TYPES",
        ],
        "assets/css/components/tables.css": [
            "table-mobile-cards",
            "TTF:INTEGRATED",
            "TTF:MOBILE-TABLE-VISIBILITY",
            "will-animate",
            "!important",
        ],
        "assets/css/components/page-content.css": [
            "responsive-label--mobile",
            "rankingReverseFade",
        ],
        "assets/css/components/robustness.css": [
            ".table-scroll",
            ".table-status-row",
        ],
        "assets/css/responsive.css": [
            ".table-ewigeRangliste",
            ".table-search",
        ],
    }

    lookup = {
        "assets/js/features/tables.js": tables_js,
        "assets/js/features/table-responsive.js": responsive_js,
        "assets/css/components/tables.css": tables_css,
        "assets/css/components/page-content.css": page_css,
        "assets/css/components/robustness.css": robustness_css,
        "assets/css/responsive.css": responsive_css,
    }

    for path, tokens in forbidden.items():
        for token in tokens:
            if token in lookup[path]:
                problems.append(f"{path}: Altlast noch vorhanden: {token}")

    required = {
        "assets/js/features/tables.js": [
            'from "./table-responsive.js"',
            "refreshResponsiveTable(table, config.responsiveType)",
            "finally {",
        ],
        "assets/js/features/table-responsive.js": [
            "SUPPORTED_TABLE_TYPES",
            "prepareLeagueTable",
            "prepareNextGamesTable",
            "prepareScheduleTable",
            "initVenueTooltipInteractions",
        ],
        "assets/js/config/table-configs.js": [
            'responsiveType: "schedule"',
            'responsiveType: "league"',
            'responsiveType: "next-games"',
        ],
        "assets/css/components/tables.css": [
            ".table-scroll",
            ".table-status-row",
            "@keyframes rankingReverseFade",
            "table.table-compact-mobile--league",
            "table.table-compact-mobile--next-games",
            "table.table-compact-mobile--schedule",
        ],
    }

    lookup_required = {
        "assets/js/features/tables.js": tables_js,
        "assets/js/features/table-responsive.js": responsive_js,
        "assets/js/config/table-configs.js": config_js,
        "assets/css/components/tables.css": tables_css,
    }

    for path, tokens in required.items():
        for token in tokens:
            if token not in lookup_required[path]:
                problems.append(f"{path}: erwarteter Zielbestandteil fehlt: {token}")

    for path in [
        "assets/css/components/tables.css",
        "assets/css/components/page-content.css",
        "assets/css/components/robustness.css",
        "assets/css/responsive.css",
    ]:
        css = read(path)
        if css.count("{") != css.count("}"):
            problems.append(f"{path}: Anzahl öffnender/schließender CSS-Klammern stimmt nicht")

    if problems:
        print("Tabellen-Cleanup-Prüfung fehlgeschlagen:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        raise SystemExit(1)


def apply() -> None:
    validate_source_state()
    changed: list[str] = []
    for path, content in TARGETS.items():
        if write_target(path, content):
            changed.append(path)

    validate_final_state()

    if changed:
        print("Tabellen-Cleanup angewendet:")
        for path in changed:
            print(f"  - {path}")
    else:
        print("Tabellen-Cleanup ist bereits vollständig angewendet.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Nur den bereits angewendeten Zielzustand prüfen.",
    )
    args = parser.parse_args()

    if args.check:
        validate_final_state()
        print("Tabellen-Cleanup: Zielzustand ist vollständig und konsistent.")
        return

    apply()


if __name__ == "__main__":
    main()
