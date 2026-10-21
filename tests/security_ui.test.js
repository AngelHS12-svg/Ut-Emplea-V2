const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

function setup() {
    class Element {
        constructor() { this.children = []; this.events = {}; this.attributes = {}; }
        appendChild(child) { this.children.push(child); }
        replaceChildren() { this.children = []; }
        setAttribute(key, value) { this.attributes[key] = value; }
        addEventListener(key, callback) { this.events[key] = callback; }
        set innerHTML(_) { throw new Error('El contenido de usuario no debe interpretarse como HTML'); }
    }
    const calls = [];
    const context = {
        window: { location: { origin: 'https://talentlink.example' } },
        document: { createElement: () => new Element(), querySelector: () => ({ content: 'local-csrf-token' }) },
        URL, Headers,
        fetch: (...args) => { calls.push(args); return Promise.resolve({ ok: true }); },
    };
    vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../public/js/security.js'), 'utf8'), context);
    return { ui: context.window.TalentLinkUI, menu: new Element(), calls };
}

test('las notificaciones maliciosas se conservan como texto y no crean HTML', () => {
    const { ui, menu } = setup();
    let selected;
    const message = '<img src=x onerror="alert(1)">';
    ui.renderNotifications(menu, [{ id: 7, tipo: '<b>tipo</b>', mensaje: message, fecha: 'Hoy', url: '/candidato/postulaciones' }],
        (...args) => { selected = args; });
    assert.equal(menu.children[0].children[1].textContent, message);
    assert.equal(menu.children[0].children[1].children.length, 0);
    menu.children[0].events.click();
    assert.deepEqual(selected, [7, '/candidato/postulaciones']);
});

test('los enlaces externos o ejecutables no se usan como destinos', () => {
    const { ui } = setup();
    for (const value of ['javascript:alert(1)', '//evil.example', '/\\evil.example', 'https://evil.example', null]) {
        assert.equal(ui.safePath(value), null);
    }
    assert.equal(ui.safePath('/admin?tab=1'), '/admin?tab=1');
});

test('el token CSRF solo se transmite a solicitudes del mismo origen', async () => {
    const { ui, calls } = setup();
    assert.throws(() => ui.csrfFetch('//evil.example', { method: 'POST' }));
    assert.equal(calls.length, 0);
    await ui.csrfFetch('/api/notificaciones/leer/7', { method: 'POST' });
    assert.equal(calls[0][1].headers.get('X-CSRF-Token'), 'local-csrf-token');
    assert.equal(calls[0][1].credentials, 'same-origin');
});
