"""Flujo de recuperación completo con BD y correo simulados, sin servicios externos."""
import re
from unittest.mock import MagicMock, patch

import pytest
from werkzeug.security import check_password_hash


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
    assert client.get('/auth/forgot-password').status_code == 200
    with client.session_transaction() as session:
        return session['_csrf_token']


def reset_token(app, user_id=2, password_hash='old-hash'):
    from app.utils.password_reset import create_reset_token
    with app.app_context():
        return create_reset_token(user_id, password_hash)


@pytest.mark.parametrize('user_id,correo', [(2, 'empresa@example.invalid'), (3, 'candidato@example.invalid')])
def test_email_link_opens_form_and_updates_existing_account(client, app, user_id, correo):
    token = csrf(client)
    conn = MagicMock()
    cur = conn.cursor.return_value
    cur.fetchone.return_value = (user_id, 'old-hash')
    with patch('main.get_connection', return_value=conn), patch('main.enviar_email', return_value=True) as mail:
        response = client.post('/auth/forgot-password', data={'csrf_token': token, 'correo': correo})
        assert response.status_code == 303
        assert client.get(response.location).status_code == 200
        recipient, subject, body = mail.call_args.args
        assert recipient == correo
        assert 'Talent Link' in subject and 'Talent Link' in body
        assert 'UT Oriental Emplea' not in body + subject
        link = re.search(r'https?://\S+/auth/reset-password/\S+', body).group()
        assert link.startswith(app.config['PUBLIC_BASE_URL'] + '/')
        path = '/auth/reset-password/' + link.rsplit('/', 1)[1]
        # El enlace funciona también en otro navegador/sesión de correo.
        browser = app.test_client()
        form = browser.get(path)
        assert form.status_code == 200
        assert 'name="confirm_password"' in form.text
        with browser.session_transaction() as session:
            browser_csrf = session['_csrf_token']
        cur.fetchone.side_effect = [(user_id, 'old-hash'), (user_id,)]
        response = browser.post(path, data={'csrf_token': browser_csrf,
            'password': 'SafePass8!xQ4', 'confirm_password': 'SafePass8!xQ4'})
        assert response.status_code == 303
        assert 'Tu contraseña se actualizó correctamente' in browser.get(response.location).text
    query, params = cur.execute.call_args.args
    assert check_password_hash(params[0], 'SafePass8!xQ4')
    assert params[1:] == (user_id, 'old-hash')
    assert 'AND password=%s AND activo IS TRUE' in query
    assert 'two_fa_code=NULL' in query
    for call in cur.execute.call_args_list:
        assert 'reset_token' not in call.args[0] and 'reset_expires' not in call.args[0]
        assert not any(sql in call.args[0] for sql in ('DELETE ', 'INSERT ', 'ALTER '))
    with browser.session_transaction() as session:
        assert '_user_id' not in session


@pytest.mark.parametrize('record,mail_ok', [(None, True), ((2, 'old-hash'), True), ((2, 'old-hash'), False)])
def test_same_confirmation_for_unknown_email_or_smtp_failure(client, record, mail_ok):
    token = csrf(client)
    conn = MagicMock()
    conn.cursor.return_value.fetchone.return_value = record
    with patch('main.get_connection', return_value=conn), patch('main.enviar_email', return_value=mail_ok) as mail:
        response = client.post('/auth/forgot-password', data={'csrf_token': token, 'correo': 'user@example.invalid'})
        assert response.status_code == 303
        assert response.location == '/auth/forgot-password?sent=1'
        assert 'Si tu correo está asociado' in client.get(response.location).text
    assert mail.call_count == int(record is not None)
    assert 'activo IS TRUE' in conn.cursor.return_value.execute.call_args.args[0]
    conn.commit.assert_not_called()
    conn.close.assert_called_once()


@pytest.mark.parametrize('correo', ['', 'no-es-correo', 'x\r\nBcc:bad@example.invalid', 'a' * 151 + '@example.invalid'])
def test_invalid_email_does_not_query_database(client, correo):
    token = csrf(client)
    with patch('main.get_connection') as db:
        response = client.post('/auth/forgot-password', data={'csrf_token': token, 'correo': correo})
        assert response.status_code == 400
        assert 'Ingresa un correo electrónico válido' in response.text
        db.assert_not_called()


@pytest.mark.parametrize('method', ['get', 'post'])
def test_tampered_and_expired_links_show_recovery_page_without_query(client, app, method):
    token = csrf(client)
    valid = reset_token(app)
    with patch('itsdangerous.timed.TimestampSigner.get_timestamp', return_value=1):
        expired = reset_token(app)
    with patch('main.get_connection') as db:
        for invalid in ['not-a-token', valid + 'x', expired]:
            response = getattr(client, method)('/auth/reset-password/' + invalid,
                **({'data': {'csrf_token': token, 'password': 'SafePass8!xQ4',
                             'confirm_password': 'SafePass8!xQ4'}} if method == 'post' else {}))
            assert response.status_code == 400
            assert 'Solicitar otro enlace' in response.text
        db.assert_not_called()


@pytest.mark.parametrize('method', ['get', 'post'])
@pytest.mark.parametrize('record', [None, (2, 'changed-hash')])
def test_used_link_or_inactive_account_cannot_reset(client, app, method, record):
    token = csrf(client)
    valid = reset_token(app)
    conn = MagicMock()
    conn.cursor.return_value.fetchone.return_value = record
    with patch('main.get_connection', return_value=conn):
        response = getattr(client, method)('/auth/reset-password/' + valid,
            **({'data': {'csrf_token': token, 'password': 'SafePass8!xQ4',
                         'confirm_password': 'SafePass8!xQ4'}} if method == 'post' else {}))
    assert response.status_code == 400
    conn.cursor.return_value.execute.assert_called_once()
    conn.commit.assert_not_called()
    conn.close.assert_called_once()


def test_concurrent_reset_cannot_report_success_if_password_already_changed(client, app):
    token = csrf(client)
    conn = MagicMock()
    conn.cursor.return_value.fetchone.side_effect = [(2, 'old-hash'), None]
    with patch('main.get_connection', return_value=conn):
        response = client.post('/auth/reset-password/' + reset_token(app), data={
            'csrf_token': token, 'password': 'SafePass8!xQ4', 'confirm_password': 'SafePass8!xQ4'})
    assert response.status_code == 400
    assert 'Solicitar otro enlace' in response.text


@pytest.mark.parametrize('password,confirmation', [('short', 'short'), ('SafePass8!xQ4', 'different')])
def test_invalid_password_stays_on_form_without_writing(client, app, password, confirmation):
    token = csrf(client)
    with patch('main.get_connection') as db:
        response = client.post('/auth/reset-password/' + reset_token(app), data={
            'csrf_token': token, 'password': password, 'confirm_password': confirmation})
    assert response.status_code == 400
    assert 'role="alert"' in response.text
    db.assert_not_called()


@pytest.mark.parametrize('stage', ['request', 'open', 'save'])
def test_database_outage_has_friendly_page(client, app, stage):
    token = csrf(client)
    valid = reset_token(app)
    with patch('main.get_connection', side_effect=RuntimeError('simulated DB failure')):
        if stage == 'request':
            response = client.post('/auth/forgot-password', data={'csrf_token': token, 'correo': 'user@example.invalid'})
        elif stage == 'open':
            response = client.get('/auth/reset-password/' + valid)
        else:
            response = client.post('/auth/reset-password/' + valid, data={
                'csrf_token': token, 'password': 'SafePass8!xQ4', 'confirm_password': 'SafePass8!xQ4'})
    assert response.status_code == 503
    assert 'simulated DB failure' not in response.text


def test_recovery_forms_require_csrf(client, app):
    with patch('main.get_connection') as db:
        assert client.post('/auth/forgot-password', data={'correo': 'user@example.invalid'}).status_code == 400
        assert client.post('/auth/reset-password/' + reset_token(app), data={
            'password': 'SafePass8!xQ4', 'confirm_password': 'SafePass8!xQ4'}).status_code == 400
        db.assert_not_called()
