document.querySelectorAll('[data-salary-form]').forEach((root) => {
    const selector = root.querySelector('[name="salario_tipo"]');
    const sync = () => {
        root.querySelectorAll('[data-salary-fields]').forEach((group) => {
            const active = group.dataset.salaryFields === selector.value;
            group.hidden = !active;
            group.style.display = active ? '' : 'none';
            group.querySelectorAll('input').forEach((input) => {
                input.disabled = !active;
                input.required = active;
            });
        });
    };
    selector.addEventListener('change', sync);
    sync();
});
