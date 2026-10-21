document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-password-toggle]').forEach(button => {
        const input = document.getElementById(button.dataset.passwordToggle);
        const label = button.getAttribute('aria-label');
        button.addEventListener('click', () => {
            const visible = input.type === 'password';
            input.type = visible ? 'text' : 'password';
            button.textContent = visible ? 'Ocultar' : 'Ver';
            button.setAttribute('aria-pressed', String(visible));
            button.setAttribute('aria-label', visible ? label.replace('Mostrar', 'Ocultar') : label);
        });
    });
    document.querySelectorAll('[data-recovery-form]').forEach(form => {
        const button = form.querySelector('[type="submit"]');
        const content = Array.from(button.childNodes, node => node.cloneNode(true));
        form.addEventListener('submit', () => {
            button.disabled = true;
            button.textContent = button.dataset.busyText;
        });
        window.addEventListener('pageshow', () => {
            button.disabled = false;
            button.replaceChildren(...content.map(node => node.cloneNode(true)));
        });
    });
});
