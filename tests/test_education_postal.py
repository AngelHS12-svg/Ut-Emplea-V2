"""Registros, títulos y CV con PostgreSQL/correo simulados; catálogo local real."""
import json
import re
from datetime import date
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def app():
    import main
    saved = dict(main.app.config)
    main.app.config.update(TESTING=True, CSRF_ENABLED=True, SESSION_COOKIE_SECURE=False)
    yield main.app
    main.app.config.clear()
    main.app.config.update(saved)


@pytest.fixture
def client(app):
    return app.test_client()


def csrf(client):
    client.get('/')
    with client.session_transaction() as session:
        return session['_csrf_token']


def authenticated(client, role='Candidato'):
    import main
    with client.session_transaction() as session:
        session['_user_id'] = '42'
        session['_fresh'] = True
    return patch.object(main.login_manager, '_user_callback', return_value=main.User(42, 'prueba@example.invalid', 3, role))


def data():
    return {'nombre': 'Prueba', 'apellido_paterno': 'Local', 'sexo': 'Otro',
            'correo': 'prueba@example.invalid', 'password': 'SafePass8!xQ4', 'telefono': '5559876540',
            'programa_tsu': 'Tecnologías de la Información', 'institucion_tsu': 'UT de Oriental',
            'egreso_tsu': '2020', 'codigo_postal': '75020', 'estado': 'Puebla',
            'municipio': 'Oriental', 'colonia': 'Oriental', 'ciudad': '', 'ubicacion': 'Calle de prueba 10'}


def with_degree(payload, degree='Ingeniería'):
    return dict(payload, programa_superior='Desarrollo y Gestión de Software', tipo_superior=degree,
                institucion_superior='UT de Oriental', egreso_superior='2024')


def sql_call(cursor, prefix):
    return next(call.args for call in cursor.execute.call_args_list if call.args[0].strip().startswith(prefix))


def update_values(sql, params):
    return dict(zip(re.findall(r'\b([a-z_]+)\s*=', sql), params))


@pytest.mark.parametrize('kind', [None, 'Ingeniería', 'Licenciatura'])
def test_register_requires_tsu_and_saves_each_title_separately(client, kind):
    token = csrf(client)
    payload = data() if kind is None else with_degree(data(), kind)
    conn = MagicMock()
    cur = conn.cursor.return_value
    cur.fetchone.return_value = (91,)
    with patch('main.get_connection', return_value=conn), patch('main.notificar_admins') as notify:
        response = client.post('/registro-candidato', data=dict(payload, csrf_token=token))
    assert response.status_code == 302 and response.location.endswith('/')
    sql, params = sql_call(cur, 'INSERT INTO candidatos')
    assert sql.count('%s') == len(params)
    education = json.loads(params[25])
    assert education['tsu']['programa'] == payload['programa_tsu']
    assert education['tsu']['egreso'] == 2020
    assert ('superior' in education) == bool(kind)
    assert params[8] == (payload['programa_superior'] if kind else payload['programa_tsu'])
    assert params[9] == (kind or 'TSU')
    assert params[-4:] == ('Puebla', 'Oriental', '', 'Oriental')
    conn.commit.assert_called_once()
    notify.assert_called_once()


@pytest.mark.parametrize('changes', [
    {'programa_tsu': ''}, {'institucion_tsu': ''}, {'egreso_tsu': ''},
    {'egreso_tsu': str(date.today().year + 1)}, {'egreso_tsu': 'abc'},
    {'programa_superior': 'Software', 'tipo_superior': ''},
    {'programa_superior': 'Software', 'tipo_superior': 'Maestría'},
    {'programa_superior': 'Software', 'tipo_superior': 'Ingeniería', 'egreso_superior': '2019'},
    {'institucion_superior': 'UT', 'programa_superior': ''},
    {'programa_tsu': 'x' * 256}, {'estado': ''}, {'municipio': ''}, {'colonia': ''},
    {'codigo_postal': '1234'}, {'pais': 'Otro país'},
])
def test_invalid_registration_is_rejected_before_creating_account(client, changes):
    token = csrf(client)
    with patch('main.get_connection') as database:
        result = client.post('/registro-candidato', data=dict(data(), csrf_token=token, **changes))
    assert result.status_code == 302 and result.location.endswith('/registro-candidato')
    database.assert_not_called()


def cv_row(education):
    row = [None] * 32
    row[0:3] = ['Prueba', 'Local', '']
    row[4:13] = ['5559876540', 2024, 'Desarrollo y Gestión de Software', 'prueba@example.invalid',
                '75020', 'Calle de prueba 10', 'Ingeniería', 'UT de Oriental', 'Desarrollo y Gestión de Software']
    row[18] = 'Desarrollador'
    row[24] = 91
    row[27:32] = [education, 'Puebla', 'Oriental', '', 'Oriental']
    return row


def test_add_degree_later_updates_same_candidate_and_live_cv(client):
    token = csrf(client)
    from app.utils.education import read_education
    old_education = read_education(data())
    conn = MagicMock()
    cur = conn.cursor.return_value
    cur.fetchone.return_value = (old_education, 'TSU', 'UT de Oriental', 'Tecnologías de la Información', 2020)
    with authenticated(client), patch('main.get_connection', return_value=conn):
        result = client.post('/candidato/actualizar-perfil', data=dict(with_degree(data()), csrf_token=token))
        assert result.status_code == 302
        sql, params = sql_call(cur, 'UPDATE candidatos SET')
        assert 'WHERE id_usuario = %s' in sql and params[-1] == 42
        assert sql.count('%s') == len(params)
        education = json.loads(update_values(sql, params)['formacion_academica'])
        assert education['tsu'] == old_education['tsu']
        assert education['superior']['tipo'] == 'Ingeniería'
        cur.fetchone.return_value = cv_row(education)
        cv = client.get('/candidato/generar-cv')
    assert cv.status_code == 200
    assert 'TSU · Tecnologías de la Información' in cv.text
    assert 'Ingeniería · Desarrollo y Gestión de Software' in cv.text
    assert 'Egreso 2020' in cv.text and 'Egreso 2024' in cv.text
    assert 'Calle de prueba 10, Oriental, Puebla' in cv.text
    assert not any(call.args[0].strip().startswith(('DELETE', 'INSERT', 'ALTER')) for call in cur.execute.call_args_list)


@pytest.mark.parametrize('degree', ['TSU', 'Ingeniería/Licenciatura', 'Maestría'])
def test_old_cv_preserves_real_degree_without_inventing_tsu(client, degree):
    token = csrf(client)
    row = cv_row(None)
    row[10] = degree
    row[12] = row[6] = 'Programa anterior'
    conn = MagicMock()
    conn.cursor.return_value.fetchone.return_value = row
    with authenticated(client), patch('main.get_connection', return_value=conn):
        response = client.get('/candidato/generar-cv')
    assert response.status_code == 200
    assert degree + ' · Programa anterior' in response.text
    if degree != 'TSU':
        assert 'TSU ·' not in response.text
    conn.commit.assert_not_called()


def test_other_existing_degree_is_retained_when_profile_gains_tsu(client):
    token = csrf(client)
    conn = MagicMock()
    cur = conn.cursor.return_value
    cur.fetchone.return_value = (None, 'Maestría', 'Institución anterior', 'Calidad', 2025)
    with authenticated(client), patch('main.get_connection', return_value=conn):
        response = client.post('/candidato/actualizar-perfil', data=dict(data(), csrf_token=token))
    assert response.status_code == 302
    sql, params = sql_call(cur, 'UPDATE candidatos SET')
    education = json.loads(update_values(sql, params)['formacion_academica'])
    assert education['anterior']['programa'] == 'Calidad'
    assert education['anterior']['egreso'] == 2025


def test_tsu_only_cv_omits_empty_degree(client):
    from app.utils.education import read_education
    csrf(client)
    conn = MagicMock()
    conn.cursor.return_value.fetchone.return_value = cv_row(read_education(data()))
    with authenticated(client), patch('main.get_connection', return_value=conn):
        response = client.get('/candidato/generar-cv')
    assert 'TSU · Tecnologías de la Información' in response.text
    assert 'Ingeniería ·' not in response.text and 'Egreso None' not in response.text


def test_company_registration_persists_structured_address(client):
    token = csrf(client)
    conn = MagicMock()
    conn.cursor.return_value.fetchone.side_effect = [(21,), (87,)]
    payload = dict(data(), empresa='Empresa de prueba', direccion='Calle de prueba 10')
    with patch('main.get_connection', return_value=conn), patch('main.notificar_admins'):
        response = client.post('/registro-empresa', data=dict(payload, csrf_token=token))
    assert response.status_code == 302 and response.location.endswith('/')
    sql, params = sql_call(conn.cursor.return_value, 'INSERT INTO direcciones_empresa')
    assert sql.count('%s') == len(params)
    assert params == (87, 'Calle de prueba 10', '75020', 'Puebla', 'Oriental', '', 'Oriental')


def test_catalog_is_local_and_preserves_zeros_and_all_colonies(client):
    with patch('main.get_connection') as database:
        places = client.get('/api/catalogos/codigos-postales/75020').get_json()['asentamientos']
        zero = client.get('/api/catalogos/codigos-postales/01000').get_json()
    assert {p['colonia'] for p in places} == {'Oriental', 'Miravalles'}
    assert all(p['estado'] == 'Puebla' and p['municipio'] == 'Oriental' for p in places)
    assert all(p['ciudad'] == '' for p in places)  # No inventar ciudad en zonas sin ciudad postal.
    assert zero['codigo_postal'] == '01000'
    assert zero['asentamientos'][0]['colonia'] == 'San Ángel'
    database.assert_not_called()


def test_states_municipalities_and_cities_catalogs(client):
    assert len(client.get('/api/catalogos/estados').get_json()['estados']) == 32
    assert 'Oriental' in client.get('/api/catalogos/municipios?estado=Puebla').get_json()['municipios']
    assert client.get('/api/catalogos/ciudades?estado=Puebla&municipio=Oriental').get_json()['ciudades'] == []
    assert client.get('/api/catalogos/municipios?estado=NoExiste').status_code == 400
    assert client.get('/api/catalogos/municipios?estado=Puebla%27%20OR%201=1').status_code == 400


@pytest.mark.parametrize('cp,status', [('99999', 404), ('abcde', 400), ('1234', 400), ('123456', 400)])
def test_unknown_or_invalid_postcode_allows_manual_entry(client, cp, status):
    response = client.get('/api/catalogos/codigos-postales/' + cp)
    assert response.status_code == status
    assert 'error' in response.get_json()


def test_unknown_postcode_can_be_saved_manually():
    from app.utils.postal import read_address
    assert read_address(dict(data(), codigo_postal='99999'))['municipio'] == 'Oriental'


def test_catalog_file_cannot_be_written_through_connection():
    import sqlite3
    from app.utils.postal import query
    with pytest.raises(sqlite3.OperationalError, match='readonly'):
        query('DELETE FROM asentamientos')


def test_profile_update_requires_csrf_and_candidate_role(client):
    with patch('main.get_connection') as database:
        assert client.post('/candidato/actualizar-perfil', data=data()).status_code == 400
        token = csrf(client)
        with authenticated(client, 'Empresa'):
            assert client.post('/candidato/actualizar-perfil', data=dict(data(), csrf_token=token)).status_code == 302
        database.assert_not_called()


def test_company_profile_saves_new_address_and_preserves_omitted_legacy_fields(client):
    token = csrf(client)
    conn = MagicMock()
    cur = conn.cursor.return_value
    payload = dict(data(), nombre='Empresa de prueba', calle='Calle de prueba 10')
    cur.fetchone.side_effect = [(87,), (1,), (1,)]
    with authenticated(client, 'Empresa'), patch('app.routes.empresa_routes.get_connection', return_value=conn):
        response = client.post('/empresa/perfil', data=dict(payload, csrf_token=token))
    assert response.status_code == 302
    sql, params = sql_call(cur, 'UPDATE direcciones_empresa')
    assert sql.count('%s') == len(params)
    assert params == ('Calle de prueba 10', '75020', 'Puebla', 'Oriental', '', 'Oriental', 87)
    # Un formulario abierto antes de la actualización no enviaba los campos nuevos.
    cur.reset_mock()
    cur.fetchone.side_effect = [(87,), (1,), (1,)]
    with authenticated(client, 'Empresa'), patch('app.routes.empresa_routes.get_connection', return_value=conn):
        response = client.post('/empresa/perfil', data={'csrf_token': token, 'calle': 'Otra calle 12'})
    assert response.status_code == 302
    sql, params = sql_call(cur, 'UPDATE direcciones_empresa')
    assert 'codigo_postal = COALESCE(%s, codigo_postal)' in sql
    assert params[1:6] == (None, None, None, None, None)


def test_candidate_profile_uses_both_levels_and_keeps_old_engineering_unclassified_as_tsu(client):
    from app.utils.education import read_education
    csrf(client)
    row = [None] * 31
    row[:8] = [91, 'Prueba', 'Local', '', 'O', '5559876540', 2024, 'Software']
    row[8] = 'prueba@example.invalid'
    row[10:15] = ['75020', 'Calle de prueba 10', 'Ingeniería', 'UT de Oriental', 'Software']
    row[26:31] = [read_education(with_degree(data())), 'Puebla', 'Oriental', '', 'Oriental']
    conn = MagicMock()
    cur = conn.cursor.return_value
    cur.fetchone.return_value = row
    with authenticated(client), patch('main.get_connection', return_value=conn):
        response = client.get('/candidato/perfil')
        assert response.status_code == 200
        assert 'value="Tecnologías de la Información"' in response.text
        assert 'value="Desarrollo y Gestión de Software"' in response.text
        row[26] = None
        old = client.get('/candidato/perfil')
    assert old.status_code == 200
    assert re.search(r'id="programa-tsu"[^>]*value=""', old.text)
    assert re.search(r'id="programa-superior"[^>]*value="Software"', old.text)
    assert 'Conservamos tu formación anterior' in old.text


def test_unavailable_postal_file_does_not_block_form_or_manual_registration(client, monkeypatch, tmp_path):
    import app.utils.postal as postal
    postal.states.cache_clear()
    postal.postal_places.cache_clear()
    monkeypatch.setattr(postal, 'CATALOG', tmp_path / 'inexistente.sqlite3')
    try:
        assert client.get('/api/catalogos/codigos-postales/01010').status_code == 503
        assert client.get('/registro-candidato').status_code == 200
        token = csrf(client)
        conn = MagicMock()
        conn.cursor.return_value.fetchone.return_value = (91,)
        with patch('main.get_connection', return_value=conn), patch('main.notificar_admins'):
            response = client.post('/registro-candidato', data=dict(data(), csrf_token=token))
        assert response.status_code == 302 and response.location.endswith('/')
        conn.commit.assert_called_once()
    finally:
        postal.states.cache_clear()
        postal.postal_places.cache_clear()
