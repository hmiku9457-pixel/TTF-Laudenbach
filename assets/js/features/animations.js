export function initAnimations(root = document) {
    const scope = root instanceof Element || root instanceof Document
        ? root
        : document;

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

    initRankingFade(scope);
}

function initRankingFade(scope) {
    const rows = Array.from(
        scope.querySelectorAll(
            ".table-ewigeRangliste tbody tr:not(.ranking-fade-ready)"
        )
    );

    if (rows.length === 0) {
        return;
    }

    const lastIndex = Math.max(rows.length - 1, 1);

    rows.forEach((row, index) => {
        const reverseRatio = (rows.length - 1 - index) / lastIndex;
        const delay = Math.round(reverseRatio * 60);

        row.classList.remove("animate", "will-animate");
        row.style.animationDelay = "";
        row.style.setProperty("--ranking-fade-delay", `${delay}ms`);
        row.classList.add("ranking-fade-ready");
    });
}

export function initAnimationObserver(onElementAdded = []) {
    const callbacks = Array.isArray(onElementAdded)
        ? onElementAdded
        : [onElementAdded];

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

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    return observer;
}
