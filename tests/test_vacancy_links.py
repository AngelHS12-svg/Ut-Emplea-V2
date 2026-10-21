"""URLs de vacantes existentes, lectura pública y retorno después de 2FA."""
from datetime import date, datetime
from unittest.mock import MagicMock, patch

import pytest
from werkzeug.security import generate_password_hash


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


def vacancy(vacancy_id=42, available=True):
    return (vacancy_id, 'Analista de calidad', 'Descripción oficial de la oferta', 14000,
            'Presencial', 'Lunes a viernes', 'Oriental, Puebla', datetime(2026, 10, 20),
            'Empresa de ejemplo', 'Ingeniería', 'Un año', 'Análisis de procesos',
            date(2026, 12, 31), 'Perfil profesional', 2, available)


def authenticated(role='Candidato'):
    import main
    return patch.object(main.login_manager, '_user_callback',
                        return_value=main.User(3, 'local@example.invalid', 3, role))


@pytest.mark.parametrize('vacancy_id', [1, 42, 120053])
def test_existing_id_has_public_url_without_writing_or_renumbering(client, app, vacancy_id):
    conn = MagicMock()
    conn.cursor.return_value.fetchone.return_value = vacancy(vacancy_id)
    with patch('main.get_connection', return_value=conn), patch('main.enviar_email') as mail:
        response = client.get('/vacantes/' + str(vacancy_id))
    assert response.status_code == 200
    assert f'VACANTE #{vacancy_id}' in response.text
    assert f'data-copy-vacancy="{app.config["PUBLIC_BASE_URL"]}/vacantes/{vacancy_id}"' in response.text
    assert 'Iniciar sesión para postularme' in response.text
    assert f'vacante={vacancy_id}' in response.text
    conn.cursor.return_value.execute.assert_called_once()
    query, params = conn.cursor.return_value.execute.call_args.args
    assert params == (vacancy_id,)
    assert query.strip().startswith('SELECT')
    assert "v.estatus='activa'" in query and "e.estatus='aprobada'" in query
    assert 'correo' not in query and 'password' not in query
    conn.commit.assert_not_called()
    conn.close.assert_called_once()
    mail.assert_not_called()


@pytest.mark.parametrize('id_path', ['0', '2147483648', '999999999999999999999999999', 'no-es-id', '-1'])
def test_invalid_id_does_not_reach_database(client, id_path):
    with patch('main.get_connection') as database:
        assert client.get('/vacantes/' + id_path).status_code == 404
        database.assert_not_called()


def test_missing_or_unpublished_offer_has_friendly_404(client):
    conn = MagicMock()
    conn.cursor.return_value.fetchone.return_value = None
    with patch('main.get_connection', return_value=conn):
        response = client.get('/vacantes/42')
    assert response.status_code == 404
    assert 'Vacante no disponible' in response.text
    assert 'data-copy-vacancy' not in response.text
    conn.close.assert_called_once()


def test_expired_offer_keeps_url_and_description_but_has_no_application_form(client):
    conn = MagicMock()
    conn.cursor.return_value.fetchone.return_value = vacancy(available=False)
    with patch('main.get_connection', return_value=conn):
        response = client.get('/vacantes/42')
    assert response.status_code == 200
    assert 'Descripción oficial' in response.text
    assert 'Convocatoria finalizada' in response.text
    assert '/candidato/postularse/' not in response.text
    assert 'Iniciar sesión para postularme' not in response.text


def test_old_detail_url_redirects_without_login_or_database(client):
    with patch('main.get_connection') as database:
        response = client.get('/candidato/detalle-vacante/42')
    assert response.status_code == 301
    assert response.location == '/vacantes/42'
    database.assert_not_called()


def test_vacancy_text_is_escaped_and_canonical_does_not_use_host(client, app):
    row = list(vacancy())
    row[1] = '<script>alert("title")</script>'
    row[2] = '<img src=x onerror="alert(1)">'
    conn = MagicMock()
    conn.cursor.return_value.fetchone.return_value = row
    with patch('main.get_connection', return_value=conn):
        response = client.get('/vacantes/42', headers={'Host': 'attacker.example'})
    assert response.status_code == 200
    assert '<script>alert' not in response.text and '<img src=x' not in response.text
    assert '&lt;script&gt;' in response.text
    assert f'<link rel="canonical" href="{app.config["PUBLIC_BASE_URL"]}/vacantes/42">' in response.text
    assert 'attacker.example' not in response.text


@pytest.mark.parametrize('already_applied,already_saved', [(False, False), (True, True)])
def test_candidate_actions_reflect_existing_records(client, already_applied, already_saved):
    with client.session_transaction() as session:
        session['_user_id'] = '3'
    conn = MagicMock()
    conn.cursor.return_value.fetchone.side_effect = [vacancy(), (5,),
        (10,) if already_applied else None, (20,) if already_saved else None]
    with authenticated(), patch('main.get_connection', return_value=conn):
        response = client.get('/vacantes/42')
    assert response.status_code == 200
    assert ('action="/candidato/postularse/42"' in response.text) is not already_applied
    assert ('action="/candidato/guardar-vacante/42"' in response.text) is not already_saved
    if already_applied:
        assert 'Ya te postulaste' in response.text
    else:
        assert 'name="csrf_token"' in response.text
    conn.commit.assert_not_called()


@pytest.mark.parametrize('role', ['Empresa', 'Administrador'])
def test_other_roles_can_share_without_candidate_actions(client, role):
    with client.session_transaction() as session:
        session['_user_id'] = '3'
    conn = MagicMock()
    conn.cursor.return_value.fetchone.return_value = vacancy()
    with authenticated(role), patch('main.get_connection', return_value=conn):
        response = client.get('/vacantes/42')
    assert response.status_code == 200
    assert 'data-copy-vacancy' in response.text
    assert 'action="/candidato/postularse/' not in response.text
    conn.cursor.return_value.execute.assert_called_once()


@pytest.mark.parametrize('action', ['postularse', 'guardar-vacante'])
def test_mutations_check_visibility_deadline_and_existing_records(client, action):
    token = csrf(client)
    with client.session_transaction() as session:
        session['_user_id'] = '3'
    conn = MagicMock()
    conn.cursor.return_value.fetchone.side_effect = [(5,), None]
    with authenticated(), patch('main.get_connection', return_value=conn), \
            patch('main.crear_notificacion') as notify, patch('main.notificar_admins') as admins:
        response = client.post(f'/candidato/{action}/42', data={'csrf_token': token})
    assert response.status_code == 302 and response.location == '/vacantes/42'
    query, params = conn.cursor.return_value.execute.call_args.args
    assert "v.estatus='activa'" in query and "e.estatus='aprobada'" in query
    assert 'v.fecha_vencimiento >= CURRENT_DATE' in query
    assert 'NOT EXISTS' in query
    assert params == (5, 42, 5)
    conn.commit.assert_not_called()
    notify.assert_not_called()
    admins.assert_not_called()
    conn.close.assert_called_once()


@pytest.mark.parametrize('action', ['postularse', 'guardar-vacante'])
def test_applying_and_saving_still_require_login_and_csrf(client, action):
    with patch('main.get_connection') as database:
        assert client.post(f'/candidato/{action}/42').status_code == 400
        token = csrf(client)
        assert client.post(f'/candidato/{action}/42', data={'csrf_token': token}).status_code == 302
        database.assert_not_called()


@pytest.mark.parametrize('action', ['postularse', 'guardar-vacante'])
def test_valid_candidate_can_apply_or_save_and_return_to_the_same_vacancy(client, action):
    token = csrf(client)
    with client.session_transaction() as session:
        session['_user_id'] = '3'
    conn = MagicMock()
    conn.cursor.return_value.fetchone.side_effect = [(5,), (71,), (8,)]
    with authenticated(), patch('main.get_connection', return_value=conn), \
            patch('main.crear_notificacion') as notify, patch('main.notificar_admins'):
        response = client.post(f'/candidato/{action}/42', data={'csrf_token': token})
    assert response.location == '/vacantes/42'
    conn.commit.assert_called_once()
    notify.assert_called_once()
    conn.close.assert_called_once()


def test_shared_vacancy_returns_after_successful_login_and_2fa(client):
    token = csrf(client)
    conn = MagicMock()
    conn.cursor.return_value.fetchone.return_value = (
        3, 'local@example.invalid', generate_password_hash('SafePass8!xQ4'), 'Candidato', 3, True)
    with patch('main.get_connection', return_value=conn), patch('main._enviar_codigo_verificacion', return_value=True):
        response = client.post('/auth/login', data={'csrf_token': token, 'rol': 'candidato',
            'correo': 'local@example.invalid', 'password': 'SafePass8!xQ4', 'vacante_id': '42'})
    assert response.location == '/auth/verify-2fa'
    with client.session_transaction() as session:
        assert '_user_id' not in session
        assert session['2fa_vacante_id'] == 42
    assert client.get('/auth/verify-2fa').status_code == 200
    with client.session_transaction() as session:
        token = session['_csrf_token']
    conn.cursor.return_value.fetchone.return_value = (3, 'local@example.invalid', 3, 'Candidato', 'stored-hash')
    with patch('main.get_connection', return_value=conn):
        response = client.post('/auth/verify-2fa', data={'csrf_token': token, 'codigo': '654987'})
    assert response.location == '/vacantes/42'
    with client.session_transaction() as session:
        assert session['_user_id'] == '3'
        assert '2fa_vacante_id' not in session


@pytest.mark.parametrize('value', ['https://attacker.example', '//attacker.example', '-1', '0', '2147483648', '１２'])
def test_return_destination_cannot_be_external_or_invalid(value):
    from app.utils.vacancies import vacancy_return_id
    assert vacancy_return_id(value) is None


def test_company_and_candidate_lists_show_database_id_and_sharing(client, app):
    import main
    with main.app.test_request_context('/'):
        from flask import render_template
        from flask_login import login_user
        login_user(main.User(3, 'local@example.invalid', 2, 'Empresa'))
        company = render_template('empresa/empresa-consultar.html', vacantes=[(42, 'Oferta', datetime.now(), 'activa', 0)], page=1, total_pages=1)
        candidate = render_template('vacantes/ver-vacantes.html', vacantes=[(42, 'Oferta', 'Empresa', 'Puebla', 'Presencial', datetime.now(), 'activa')])
    for markup in [company, candidate]:
        assert 'Vacante #42' in markup
        assert f'data-copy-vacancy="{app.config["PUBLIC_BASE_URL"]}/vacantes/42"' in markup
