const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

function setup(clipboardAllowed = true) {
    class Element {
        constructor(tag) { this.tag = tag; this.children = []; this.events = {}; this.attributes = {}; }
        appendChild(child) { this.children.push(child); }
        setAttribute(key, value) { this.attributes[key] = value; }
        addEventListener(key, callback) { this.events[key] = callback; }
        showModal() { this.open = true; }
        close() { this.open = false; this.events.close(); }
        remove() { this.removed = true; }
        focus() { this.focused = true; }
        select() { this.selected = true; }
        set innerHTML(_) { throw new Error('El enlace no debe interpretarse como HTML'); }
    }
    const listeners = {};
    const body = new Element('body');
    const calls = [];
    const context = {
        document: { body, createElement: tag => new Element(tag),
            addEventListener: (name, fn) => { listeners[name] = fn; } },
        window: { location: { origin: 'https://talentlink.example' } },
        navigator: { clipboard: { writeText: async text => {
            if (!clipboardAllowed) throw new Error('denied');
            calls.push(text);
        } } },
        URL, setTimeout: () => 1, clearTimeout: () => {},
    };
    vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../public/js/vacancy-share.js'), 'utf8'), context);
    listeners.DOMContentLoaded();
    const button = { dataset: { copyVacancy: 'https://talentlink.example/vacantes/42' } };
    return { body, calls, button, click: () => listeners.click({ target: { closest: () => button } }) };
}

test('copia el enlace de la vacante seleccionada y confirma el resultado', async () => {
    const { calls, button, click, body } = setup();
    await click();
    button.dataset.copyVacancy = 'https://talentlink.example/vacantes/87';
    await click();
    assert.deepEqual(calls, ['https://talentlink.example/vacantes/42', 'https://talentlink.example/vacantes/87']);
    assert.equal(body.children[0].attributes.role, 'status');
    assert.equal(body.children[0].textContent, 'Enlace de la vacante copiado');
});

test('si el navegador impide copiar permite seleccionar el enlace manualmente', async () => {
    const { body, calls, click } = setup(false);
    await click();
    assert.equal(calls.length, 0);
    const dialog = body.children[0];
    assert.equal(dialog.open, true);
    const input = dialog.children[0].children[0];
    assert.equal(input.readOnly, true);
    assert.equal(input.value, 'https://talentlink.example/vacantes/42');
    assert.equal(input.selected, true);
    dialog.children[1].events.click();
    assert.equal(dialog.removed, true);
});

test('no copia destinos ajenos, ejecutables ni rutas que no correspondan a una vacante', async () => {
    const { body, calls, button, click } = setup();
    for (const value of ['https://attacker.example/vacantes/42', 'javascript:alert(1)',
        'https://talentlink.example/admin', 'https://talentlink.example/vacantes/0',
        'https://talentlink.example/vacantes/42?next=evil', 'https://talentlink.example/vacantes/42#bad']) {
        button.dataset.copyVacancy = value;
        await click();
    }
    assert.equal(calls.length, 0);
    assert.equal(body.children.length, 0);
});
