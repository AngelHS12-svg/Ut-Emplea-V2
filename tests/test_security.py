"""Regresiones de seguridad con servicios externos bloqueados por conftest."""
from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask
from werkzeug.security import generate_password_hash


@pytest.fixture
def secure_app():
    import main
    saved = dict(main.app.config)
    main.app.config.update(TESTING=True, CSRF_ENABLED=True, SESSION_COOKIE_SECURE=False)
    yield main.app
    main.app.config.clear()
    main.app.config.update(saved)


@pytest.fixture
def client(secure_app):
    return secure_app.test_client()


def token(client):
    client.get('/')
    with client.session_transaction() as session:
        return session['_csrf_token']


def authenticate(client, role='Empresa', user_id=200):
    import main
    with client.session_transaction() as session:
        session['_user_id'] = str(user_id)
        session['_fresh'] = True
    return patch.object(main.login_manager, '_user_callback', return_value=main.User(
        user_id, 'user@example.invalid', 2, role))


@pytest.mark.parametrize('secret', ['', 'short'])
def test_missing_or_short_secret_refuses_startup(monkeypatch, secret):
    from app.config.security import configure_security
    monkeypatch.setenv('SECRET_KEY', secret)
    with pytest.raises(RuntimeError, match='SECRET_KEY'):
        configure_security(Flask('test'))


def test_production_cookie_settings(monkeypatch):
    from app.config.security import configure_security
    monkeypatch.setenv('FLASK_ENV', 'production')
    app = Flask('test')
    configure_security(app)
    assert app.config['SESSION_COOKIE_SECURE'] is True
    assert app.config['SESSION_COOKIE_HTTPONLY'] is True
    assert app.config['SESSION_COOKIE_SAMESITE'] == 'Lax'


def test_different_key_cannot_fabricate_admin_session(client, secure_app):
    other = Flask('other')
    other.secret_key = 'a-different-secret-with-at-least-32-characters'
    cookie = other.session_interface.get_signing_serializer(other).dumps({'_user_id': '1'})
    client.set_cookie(secure_app.config['SESSION_COOKIE_NAME'], cookie)
    with patch('main.get_connection') as database:
        assert client.get('/admin').status_code == 302
        database.assert_not_called()


@pytest.mark.parametrize('bad_token', [None, 'wrong', 'á' * 12])
def test_csrf_rejects_before_database(client, bad_token):
    token(client)
    data = {} if bad_token is None else {'csrf_token': bad_token}
    with patch('main.get_connection') as database:
        assert client.post('/auth/login', data=data).status_code == 400
        database.assert_not_called()


def test_csrf_is_bound_to_session(client, secure_app):
    first = token(client)
    other = secure_app.test_client()
    token(other)
    assert other.post('/auth/login', data={'csrf_token': first}).status_code == 400


def test_csrf_header_for_notification(client):
    csrf = token(client)
    conn = MagicMock()
    with authenticate(client), patch('main.get_connection', return_value=conn):
        response = client.post('/api/notificaciones/leer/5', headers={'X-CSRF-Token': csrf})
    assert response.status_code == 200
    assert conn.cursor.return_value.execute.call_args.args[1] == (5, 200)


@pytest.mark.parametrize('action', ['editar', 'eliminar', 'aceptar', 'rechazar'])
@pytest.mark.parametrize('owned', [False, True])
def test_company_mutations_require_owner(client, action, owned):
    csrf = token(client)
    conn = MagicMock()
    cur = conn.cursor.return_value
    vacancy = (900, 'Vacante', 'Descripción', 10000, 'Presencial', '9-6', 'Puebla',
               date(2027, 1, 1), 1, 'Perfil', 'Ingeniería', '1 año', 'Python')
    cur.fetchone.return_value = ((900, 300) if action in ('aceptar', 'rechazar') else vacancy) if owned else None
    path = (f'/empresa/vacante/900/{action}' if action in ('editar', 'eliminar')
            else f'/empresa/postulacion/901/{action}')
    with authenticate(client), patch('main.get_connection', return_value=conn), \
            patch('main.crear_notificacion') as notify, patch('main.notificar_admins') as admins:
        response = client.post(path, data={
            'csrf_token': csrf, 'titulo': 'Cambio', 'num_vacantes': '1', 'salario': '10000'})
    assert response.status_code == (302 if owned else 404)
    first_query, first_params = cur.execute.call_args_list[0].args
    assert 'e.id_usuario' in first_query
    assert first_params[-1] == 200
    if owned:
        conn.commit.assert_called_once()
    else:
        conn.commit.assert_not_called()
        notify.assert_not_called()
        admins.assert_not_called()
        assert cur.execute.call_count == 1
    conn.close.assert_called_once()


def test_edit_cannot_read_other_company_vacancy(client):
    token(client)
    conn = MagicMock()
    conn.cursor.return_value.fetchone.return_value = None
    with authenticate(client), patch('main.get_connection', return_value=conn):
        assert client.get('/empresa/vacante/900/editar').status_code == 404
    conn.close.assert_called_once()


@pytest.mark.parametrize('role', ['Administrador', 'Candidato'])
def test_other_roles_cannot_mutate_company_data(client, role):
    csrf = token(client)
    with authenticate(client, role=role), patch('main.get_connection') as database:
        assert client.post('/empresa/vacante/900/eliminar', data={'csrf_token': csrf}).status_code == 403
        database.assert_not_called()


def test_admin_password_starts_2fa_and_does_not_log_in(client):
    csrf = token(client)
    conn = MagicMock()
    conn.cursor.return_value.fetchone.return_value = (
        1, 'admin@example.invalid', generate_password_hash('SafePass8!xQ4'), 'Administrador', 1, True)
    with patch('main.get_connection', return_value=conn), \
            patch('main._enviar_codigo_verificacion', return_value=True) as send:
        response = client.post('/auth/login', data={
            'csrf_token': csrf, 'correo': 'admin@example.invalid', 'password': 'SafePass8!xQ4', 'rol': 'admin'})
    assert response.location.endswith('/auth/verify-2fa')
    with client.session_transaction() as session:
        assert session['2fa_user_id'] == 1
        assert '_user_id' not in session
    send.assert_called_once_with(1)


def test_failed_email_does_not_create_challenge(client):
    csrf = token(client)
    conn = MagicMock()
    conn.cursor.return_value.fetchone.return_value = (
        1, 'admin@example.invalid', generate_password_hash('SafePass8!xQ4'), 'Administrador', 1, True)
    with patch('main.get_connection', return_value=conn), patch('main._enviar_codigo_verificacion', return_value=False):
        client.post('/auth/login', data={
            'csrf_token': csrf, 'correo': 'admin@example.invalid', 'password': 'SafePass8!xQ4', 'rol': 'admin'})
    with client.session_transaction() as session:
        assert '2fa_user_id' not in session and '_user_id' not in session


def test_2fa_without_challenge_is_handled(client):
    csrf = token(client)
    with patch('main.get_connection') as database:
        assert client.post('/auth/verify-2fa', data={'csrf_token': csrf, 'codigo': '000000'}).status_code == 302
        database.assert_not_called()


@pytest.mark.parametrize('valid', [False, True])
def test_2fa_consumes_code_atomically_and_checks_active(client, valid):
    csrf = token(client)
    with client.session_transaction() as session:
        session['2fa_user_id'] = 1
    conn = MagicMock()
    conn.cursor.return_value.fetchone.return_value = (1, 'admin@example.invalid', 1, 'Administrador', 'stored-hash') if valid else None
    with patch('main.get_connection', return_value=conn):
        response = client.post('/auth/verify-2fa', data={'csrf_token': csrf, 'codigo': '000000'})
    query = conn.cursor.return_value.execute.call_args.args[0]
    assert 'activo IS TRUE' in query and 'two_fa_expires>CURRENT_TIMESTAMP' in query
    assert 'two_fa_code=NULL' in query and 'RETURNING' in query
    with client.session_transaction() as session:
        assert ('_user_id' in session) == valid
        if valid:
            assert '2fa_user_id' not in session
    assert response.location.endswith('/admin' if valid else '/auth/verify-2fa')


def test_inactive_account_not_loaded(client):
    import main
    conn = MagicMock()
    conn.cursor.return_value.fetchone.return_value = None
    with main.app.test_request_context('/'), patch('main.get_connection', return_value=conn):
        assert main.load_user('1') is None
    assert 'activo IS TRUE' in conn.cursor.return_value.execute.call_args.args[0]


def test_compat_registration_uses_canonical_route(client):
    csrf = token(client)
    with patch('app.routes.empresa_routes.get_connection') as database:
        response = client.post('/empresa/registro-empresa', data={'csrf_token': csrf, 'password': 'x'})
        assert response.status_code == 307 and response.location.endswith('/registro-empresa')
        database.assert_not_called()


def test_profile_preserves_omitted_languages(client):
    csrf = token(client)
    conn = MagicMock()
    with authenticate(client, role='Candidato'), patch('main.get_connection', return_value=conn):
        response = client.post('/candidato/actualizar-perfil', data={'csrf_token': csrf, 'nombre': 'Cambio'})
    assert response.status_code == 302
    query, params = conn.cursor.return_value.execute.call_args.args
    assert 'COALESCE(%s, idiomas)' in query and params[-3:-1] == (None, None)
    conn.close.assert_called_once()


def test_logout_requires_post_and_csrf(client):
    csrf = token(client)
    with authenticate(client):
        assert client.get('/logout').status_code == 405
        assert client.post('/logout').status_code == 400
        assert client.post('/logout', data={'csrf_token': csrf}).status_code == 302
    with client.session_transaction() as session:
        assert '_user_id' not in session


def test_connection_returned_once_at_teardown(secure_app, monkeypatch):
    import app.config.database as database
    pool = MagicMock()
    pool.getconn.return_value.closed = False
    monkeypatch.setattr(database, '_pool', pool)
    with secure_app.test_request_context('/'):
        connection = database.get_connection()
        connection.close()
        database.close_request_connections()
    pool.putconn.assert_called_once_with(pool.getconn.return_value, close=False)


def test_pool_exhaustion_does_not_open_unbounded_connections(monkeypatch, secure_app):
    import app.config.database as database
    pool = MagicMock()
    pool.getconn.side_effect = RuntimeError('pool exhausted')
    monkeypatch.setattr(database, '_pool', pool)
    with pytest.raises(RuntimeError, match='exhausted'):
        database.get_connection()


def test_admin_seed_is_idempotent_and_never_deletes():
    import seed_admin
    conn = MagicMock()
    conn.cursor.return_value.fetchone.return_value = None
    with patch('seed_admin.get_connection', return_value=conn):
        assert seed_admin.create_admin('admin@example.invalid', 'SafePass8!xQ4') is False
    query = conn.cursor.return_value.execute.call_args.args[0]
    assert 'ON CONFLICT' in query and 'DELETE' not in query.upper()
    conn.close.assert_called_once()


def test_password_change_revokes_existing_session(client):
    import main
    conn = MagicMock()
    conn.cursor.return_value.fetchone.return_value = (200, 'user@example.invalid', 2, 'Empresa', 'new-hash')
    with main.app.app_context(), client.session_transaction() as session:
        session['_user_id'] = '200'
        session['_credential_stamp'] = main.credential_stamp('old-hash')
    with patch('main.get_connection', return_value=conn):
        assert client.get('/empresa/').status_code == 302


def test_unchanged_password_keeps_session(client):
    import main
    conn = MagicMock()
    conn.cursor.return_value.fetchone.return_value = (200, 'user@example.invalid', 2, 'Empresa', 'same-hash')
    with main.app.test_request_context('/'):
        from flask import session
        session['_credential_stamp'] = main.credential_stamp('same-hash')
        with patch('main.get_connection', return_value=conn):
            assert main.load_user('200').id == 200


def test_reset_consumes_valid_token_in_single_update(client):
    csrf = token(client)
    conn = MagicMock()
    conn.cursor.return_value.fetchone.return_value = (1,)
    with patch('main.get_connection', return_value=conn):
        response = client.post('/auth/reset-password/local-token', data={
            'csrf_token': csrf, 'password': 'SafePass8!xQ4', 'confirm_password': 'SafePass8!xQ4'})
    assert response.status_code == 302
    conn.cursor.return_value.execute.assert_called_once()
    query, params = conn.cursor.return_value.execute.call_args.args
    assert 'reset_expires>CURRENT_TIMESTAMP' in query and 'reset_token=NULL' in query
    assert params[1] == 'local-token'
    assert params[0] != 'SafePass8!xQ4'
    conn.close.assert_called_once()


def test_reset_email_uses_configured_origin_instead_of_host_header(client, secure_app):
    csrf = token(client)
    conn = MagicMock()
    conn.cursor.return_value.fetchone.return_value = (1,)
    with patch('main.get_connection', return_value=conn), patch('main.enviar_email') as mail:
        client.post('/auth/forgot-password', headers={'Host': 'attacker.example'},
                    data={'csrf_token': csrf, 'correo': 'user@example.invalid'})
    # Una cookie de otro host no pasa CSRF, por lo que tampoco envía correo.
    mail.assert_not_called()
    with patch('main.get_connection', return_value=conn), patch('main.enviar_email') as mail:
        client.post('/auth/forgot-password', data={'csrf_token': csrf, 'correo': 'user@example.invalid'})
    assert secure_app.config['PUBLIC_BASE_URL'] + '/auth/reset-password/' in mail.call_args.args[2]


def test_request_teardown_releases_connection_on_error(secure_app, monkeypatch):
    import app.config.database as database
    pool = MagicMock()
    pool.getconn.return_value.closed = False
    monkeypatch.setattr(database, '_pool', pool)
    with pytest.raises(ValueError):
        with secure_app.test_request_context('/'):
            database.get_connection()
            raise ValueError('simulated handler error')
    pool.putconn.assert_called_once()
