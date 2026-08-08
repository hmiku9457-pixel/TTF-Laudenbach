const HTTP_PROTOCOLS = new Set(["https:", "http:"]);
const EMBED_HOSTS = new Set([
    "google.com",
    "www.google.com",
    "maps.google.com",
    "youtube.com",
    "www.youtube.com",
    "youtube-nocookie.com",
    "www.youtube-nocookie.com",
    "youtu.be"
]);

export function getSafeHttpUrl(value, { allowedHosts = null } = {}) {
    if (typeof value !== "string" || !value.trim()) {
        return null;
    }

    try {
        const url = new URL(value, window.location.origin);
        if (!HTTP_PROTOCOLS.has(url.protocol)) {
            return null;
        }

        if (allowedHosts && !hostIsAllowed(url.hostname, allowedHosts)) {
            return null;
        }

        return url.href;
    } catch {
        return null;
    }
}

export function getSafeEmbedUrl(value) {
    return getSafeHttpUrl(value, { allowedHosts: EMBED_HOSTS });
}

function hostIsAllowed(hostname, allowedHosts) {
    const normalized = hostname.toLowerCase();
    return Array.from(allowedHosts).some(host => normalized === host || normalized.endsWith(`.${host}`));
}
