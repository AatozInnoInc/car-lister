window.modalPortal = (function () {
    function ensureContainer() {
        let container = document.getElementById('modal-portal-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'modal-portal-container';
            container.style.position = 'relative';
            document.body.appendChild(container);
        }
        return container;
    }

    function attach(root) {
        const container = ensureContainer();
        if (!root) return;
        const el = root instanceof HTMLElement ? root : root.closest && root.closest('.modal-portal-root');
        if (!el) return;
        if (el.parentElement !== container) {
            container.appendChild(el);
        }
    }

    function detach(root) {
        const container = document.getElementById('modal-portal-container');
        if (!container || !root) return;
        const el = root instanceof HTMLElement ? root : root.closest && root.closest('.modal-portal-root');
        if (!el) return;
        if (el.parentElement === container) {
            document.body.appendChild(el); // fallback: move back near end of body
        }
    }

    return { attach, detach };
})();


