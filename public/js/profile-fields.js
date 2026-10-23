document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-education-fields]').forEach(section => {
        const program = section.querySelector('[name="programa_superior"]');
        const kind = section.querySelector('[name="tipo_superior"]');
        const tsuYear = section.querySelector('[name="egreso_tsu"]');
        const year = section.querySelector('[name="egreso_superior"]');
        const institution = section.querySelector('[name="institucion_superior"]');
        const synchronize = () => {
            kind.required = Boolean(program.value.trim());
            kind.dataset.required = kind.required ? 'true' : 'false';
            program.setCustomValidity(!program.value.trim() && (institution.value.trim() || year.value)
                ? 'Indica el programa de ingeniería o licenciatura, o deja este nivel en blanco.' : '');
            year.setCustomValidity(year.value && tsuYear.value && Number(year.value) < Number(tsuYear.value)
                ? 'El egreso de este título no puede ser anterior al del TSU.' : '');
        };
        [program, institution, year, tsuYear].forEach(field => field.addEventListener('input', synchronize));
        synchronize();
    });

    document.querySelectorAll('[data-postal-fields]').forEach(section => {
        const fields = Object.fromEntries(['codigo_postal', 'estado', 'municipio', 'ciudad', 'colonia']
            .map(key => [key, section.querySelector('[name="' + key + '"]')]));
        const status = section.querySelector('[role="status"]');
        let places = [];
        let requestVersion = 0;
        let timer;
        let previousCP = fields.codigo_postal.value;
        const message = (text, error = false) => {
            status.textContent = text;
            status.dataset.error = String(error);
        };
        const options = (name, values) => {
            const list = section.querySelector('#postal-' + name);
            list.replaceChildren(...[...new Set(values.filter(Boolean))].map(value => {
                const option = document.createElement('option');
                option.value = value;
                return option;
            }));
        };
        const unique = (rows, key) => [...new Set(rows.map(row => row[key]).filter(Boolean))];
        const fillUnique = (rows, keys) => keys.forEach(key => {
            const values = unique(rows, key);
            fields[key].value = values.length === 1 ? values[0] : '';
        });
        const load = async path => {
            const controller = new AbortController();
            const timeout = setTimeout(() => controller.abort(), 5000);
            try {
                const response = await fetch('/api/catalogos/' + path, { signal: controller.signal });
                const data = await response.json();
                if (!response.ok) throw new Error(data.error || 'No se pudo consultar el catálogo.');
                return data;
            } finally {
                clearTimeout(timeout);
            }
        };
        const loadMunicipalities = async () => {
            const state = fields.estado.value;
            options('municipios', []);
            if (!state) return;
            try {
                const data = await load('municipios?estado=' + encodeURIComponent(state));
                if (state === fields.estado.value) options('municipios', data.municipios);
            } catch (_) { /* La captura manual sigue disponible. */ }
        };
        const loadCities = async () => {
            const state = fields.estado.value;
            const municipality = fields.municipio.value;
            options('ciudades', []);
            if (!state || !municipality) return;
            try {
                const params = new URLSearchParams({ estado: state, municipio: municipality });
                const data = await load('ciudades?' + params);
                if (state === fields.estado.value && municipality === fields.municipio.value) {
                    options('ciudades', data.ciudades);
                }
            } catch (_) { /* Algunas localidades rurales no tienen ciudad postal. */ }
        };
        const relevantPlaces = () => places.filter(row =>
            (!fields.estado.value || row.estado === fields.estado.value) &&
            (!fields.municipio.value || row.municipio === fields.municipio.value));
        const lookup = async () => {
            clearTimeout(timer);
            const cp = fields.codigo_postal.value.trim();
            const version = ++requestVersion;
            if (!/^[0-9]{5}$/.test(cp)) {
                message('Escribe un código postal de 5 dígitos.', true);
                return;
            }
            message('Consultando código postal…');
            try {
                const data = await load('codigos-postales/' + cp);
                if (version !== requestVersion || cp !== fields.codigo_postal.value.trim()) return;
                places = data.asentamientos;
                fillUnique(places, ['estado', 'municipio', 'ciudad', 'colonia']);
                options('municipios', unique(places, 'municipio'));
                options('ciudades', unique(places, 'ciudad'));
                options('colonias', unique(places, 'colonia'));
                message(places.length > 1
                    ? 'Ubicación encontrada. Selecciona tu colonia en las opciones y revisa los datos.'
                    : 'Ubicación completada. Revisa los datos y añade tu calle y número.');
                loadMunicipalities();
                loadCities();
            } catch (error) {
                if (version !== requestVersion) return;
                places = [];
                message(error.message && !['AbortError', 'TypeError', 'SyntaxError'].includes(error.name)
                    ? error.message + ' Puedes capturar los datos manualmente.'
                    : 'No fue posible consultar el catálogo. Puedes capturar los datos manualmente.', true);
            }
        };
        fields.codigo_postal.addEventListener('input', () => {
            clearTimeout(timer);
            ++requestVersion;
            if (fields.codigo_postal.value !== previousCP) {
                previousCP = fields.codigo_postal.value;
                places = [];
                ['estado', 'municipio', 'ciudad', 'colonia'].forEach(key => { fields[key].value = ''; });
                ['municipios', 'ciudades', 'colonias'].forEach(name => options(name, []));
                message('');
            }
            if (/^[0-9]{5}$/.test(fields.codigo_postal.value)) timer = setTimeout(lookup, 350);
        });
        section.querySelector('[data-postal-search]').addEventListener('click', lookup);
        fields.estado.addEventListener('change', () => {
            ['municipio', 'ciudad', 'colonia'].forEach(key => { fields[key].value = ''; });
            options('ciudades', []);
            options('colonias', unique(relevantPlaces(), 'colonia'));
            loadMunicipalities();
        });
        fields.municipio.addEventListener('change', () => {
            fields.colonia.value = '';
            fillUnique(relevantPlaces(), ['ciudad']);
            options('colonias', unique(relevantPlaces(), 'colonia'));
            loadCities();
        });
        fields.colonia.addEventListener('change', () => {
            const rows = relevantPlaces().filter(row => row.colonia === fields.colonia.value);
            if (rows.length) {
                fillUnique(rows, ['estado', 'municipio', 'ciudad']);
                loadCities();
            }
        });
        loadMunicipalities();
        loadCities();
    });
});
