const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

test('el formulario solo envía los importes del modo seleccionado', () => {
    const selector = {
        value: 'no_especificado',
        addEventListener(_event, callback) { this.onChange = callback; },
    };
    const fixed = { disabled: false, required: false };
    const minimum = { disabled: false, required: false };
    const maximum = { disabled: false, required: false };
    const groups = [
        { dataset: { salaryFields: 'fijo' }, style: {}, querySelectorAll: () => [fixed] },
        { dataset: { salaryFields: 'rango' }, style: {}, querySelectorAll: () => [minimum, maximum] },
    ];
    const root = { querySelector: () => selector, querySelectorAll: () => groups };
    const document = { querySelectorAll: () => [root] };
    const source = fs.readFileSync(path.join(__dirname, '../public/js/salary-fields.js'), 'utf8');
    vm.runInNewContext(source, { document });

    assert.deepEqual([fixed.disabled, minimum.disabled, maximum.disabled], [true, true, true]);
    selector.value = 'rango';
    selector.onChange();
    assert.deepEqual([fixed.disabled, minimum.disabled, maximum.disabled], [true, false, false]);
    assert.deepEqual([fixed.required, minimum.required, maximum.required], [false, true, true]);
    selector.value = 'fijo';
    selector.onChange();
    assert.deepEqual([fixed.disabled, minimum.disabled, maximum.disabled], [false, true, true]);
});
