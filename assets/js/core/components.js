import { fetchText } from "./http.js";
import { showContainerStatus } from "./status.js";

/**
 * Lädt eine gemeinsame HTML-Komponente in einen vorhandenen Container.
 */
export async function loadComponent(containerId, url, errorMessage) {
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
