/**
 * Einheitliche Status- und Fehlermeldungen für dynamische Inhalte.
 */
export function showContainerStatus(container, message, type = "error") {
    container.innerHTML = "";

    const status = document.createElement("p");
    status.className = `dynamic-status dynamic-status--${type}`;
    status.textContent = message;
    status.setAttribute("role", type === "error" ? "alert" : "status");

    container.appendChild(status);
}

export function getTableColumnCount(tbody) {
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

export function showTableStatus(tbody, message, type = "error") {
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
