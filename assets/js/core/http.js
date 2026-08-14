/**
 * Gemeinsame HTTP-Hilfsfunktionen.
 */
export async function fetchJson(url, options = {}) {
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
