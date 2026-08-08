export function initAnimations(root = document) {
    const scope = root instanceof Element || root instanceof Document ? root : document;
    const selector = [
        ".box:not(.animate)",
        ".team-box:not(.animate)",
        ".news-slider:not(.animate)",
        ".button:not(.animate)"
    ].join(", ");

    const elements = Array.from(scope.querySelectorAll(selector));
    if (scope instanceof Element && scope.matches(selector)) {
        elements.unshift(scope);
    }

    elements.forEach((element, index) => {
        element.style.animationDelay = `${index * 0.2}s`;
        element.classList.add("animate");
    });

    scope.querySelectorAll(".table-ewigeRangliste tbody tr:not(.animate)")
        .forEach((row, index) => {
            row.style.animationDelay = `${index * 0.08}s`;
            row.classList.add("will-animate");
            requestAnimationFrame(() => row.classList.add("animate"));
        });
}

export function initAnimationObserver(onElementAdded = []) {
    const callbacks = Array.isArray(onElementAdded) ? onElementAdded : [onElementAdded];
    const observer = new MutationObserver(mutations => {
        mutations.forEach(mutation => {
            mutation.addedNodes.forEach(node => {
                if (!(node instanceof Element)) {
                    return;
                }
                initAnimations(node);
                callbacks.forEach(callback => callback?.(node));
            });
        });
    });

    observer.observe(document.body, { childList: true, subtree: true });
    return observer;
}
