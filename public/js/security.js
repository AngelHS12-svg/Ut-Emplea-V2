'use strict';

window.TalentLinkUI = (() => {
    function safePath(value) {
        if (typeof value !== 'string' || !value.startsWith('/') || value.startsWith('//') || value.includes('\\')) {
            return null;
        }
        try {
            const target = new URL(value, window.location.origin);
            return target.origin === window.location.origin ? target.pathname + target.search + target.hash : null;
        } catch (_) {
            return null;
        }
    }

    function csrfFetch(path, options = {}) {
        const target = safePath(path);
        if (!target) throw new Error('Destino de solicitud no permitido.');
        const headers = new Headers(options.headers);
        headers.set('X-CSRF-Token', document.querySelector('meta[name="csrf-token"]').content);
        return fetch(target, { ...options, headers, credentials: 'same-origin' }).then(response => {
            if (!response.ok) throw new Error('No se pudo completar la solicitud. Recarga la página.');
            return response;
        });
    }

    function renderNotifications(menu, notifications, onSelect) {
        menu.replaceChildren();
        if (!notifications.length) {
            const empty = document.createElement('div');
            empty.className = 'notif-item last';
            empty.textContent = 'No tienes notificaciones nuevas.';
            menu.appendChild(empty);
            return;
        }
        notifications.forEach(notification => {
            if (!Number.isSafeInteger(notification.id) || notification.id < 1) return;
            const item = document.createElement('div');
            item.className = 'notif-item';
            item.tabIndex = 0;
            item.setAttribute('role', 'button');
            const path = safePath(notification.url);
            const select = () => onSelect(notification.id, path);
            item.addEventListener('click', select);
            item.addEventListener('keydown', event => {
                if (event.key === 'Enter' || event.key === ' ') {
                    event.preventDefault();
                    select();
                }
            });
            [['notif-title', String(notification.tipo || '').toUpperCase()],
             ['notif-msg', notification.mensaje], ['notif-date', notification.fecha]].forEach(([className, value]) => {
                const field = document.createElement('div');
                field.className = className;
                field.textContent = String(value || '');
                item.appendChild(field);
            });
            menu.appendChild(item);
        });
    }
    return { safePath, csrfFetch, renderNotifications };
})();
