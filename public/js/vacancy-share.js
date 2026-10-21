'use strict';

document.addEventListener('DOMContentLoaded', () => {
    let feedback;
    let feedbackTimeout;
    function notify(message) {
        if (!feedback) {
            feedback = document.createElement('div');
            feedback.className = 'tl-share-feedback';
            feedback.setAttribute('role', 'status');
            document.body.appendChild(feedback);
        }
        feedback.hidden = false;
        feedback.textContent = message;
        clearTimeout(feedbackTimeout);
        feedbackTimeout = setTimeout(() => { feedback.hidden = true; }, 4000);
    }

    function showLink(url) {
        const dialog = document.createElement('dialog');
        dialog.className = 'tl-share-dialog';
        dialog.setAttribute('aria-label', 'Copiar enlace de la vacante');
        const label = document.createElement('label');
        const input = document.createElement('input');
        label.textContent = 'Selecciona y copia el enlace para compartirlo:';
        input.type = 'text';
        input.readOnly = true;
        input.value = url;
        input.setAttribute('aria-label', 'Enlace de la vacante');
        label.appendChild(input);
        const close = document.createElement('button');
        close.type = 'button';
        close.className = 'tl-copy-link';
        close.textContent = 'Cerrar';
        close.addEventListener('click', () => dialog.close());
        dialog.addEventListener('close', () => dialog.remove());
        dialog.appendChild(label);
        dialog.appendChild(close);
        document.body.appendChild(dialog);
        dialog.showModal();
        input.focus();
        input.select();
    }

    document.addEventListener('click', async event => {
        const button = event.target.closest('[data-copy-vacancy]');
        if (!button) return;
        let url;
        try {
            url = new URL(button.dataset.copyVacancy);
            if (!['http:', 'https:'].includes(url.protocol) || url.origin !== window.location.origin
                || !/^\/vacantes\/[1-9][0-9]*$/.test(url.pathname) || url.search || url.hash) return;
        } catch (_) { return; }
        try {
            await navigator.clipboard.writeText(url.href);
            notify('Enlace de la vacante copiado');
        } catch (_) {
            showLink(url.href);
        }
    });
});
