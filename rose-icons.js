/** Lightweight SVG icons — replaces Font Awesome (PageSpeed). */
(function () {
    'use strict';

    const SPRITE = 'assets/icons.svg';

    function icon(name, className) {
        const extra = className ? ` ${className}` : '';
        return `<svg class="ico${extra}" viewBox="0 0 24 24" width="1em" height="1em" aria-hidden="true"><use href="${SPRITE}#${name}"></use></svg>`;
    }

    window.RoseIcon = icon;
})();
