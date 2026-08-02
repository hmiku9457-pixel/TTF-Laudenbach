/**
 * Fehlertoleranter Zugriff auf Local Storage.
 */
export function getStorageValue(key) {
    try {
        return window.localStorage.getItem(key);
    } catch (error) {
        console.warn("Local Storage ist nicht verfügbar:", error);
        return null;
    }
}

export function setStorageValue(key, value) {
    try {
        window.localStorage.setItem(key, value);
    } catch (error) {
        console.warn("Local Storage ist nicht verfügbar:", error);
    }
}

export function removeStorageValue(key) {
    try {
        window.localStorage.removeItem(key);
    } catch (error) {
        console.warn("Local Storage ist nicht verfügbar:", error);
    }
}
