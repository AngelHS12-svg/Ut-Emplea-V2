"""Configuración de sesiones y protección de solicitudes de modificación."""
import os
import secrets
import hashlib
import hmac
from datetime import timedelta
from urllib.parse import urlsplit

from flask import abort, current_app, request, session
from werkzeug.middleware.proxy_fix import ProxyFix


def credential_stamp(password_hash):
    """Revoca sesiones cuando cambia la contraseña, sin incluir su hash en la cookie."""
    return hmac.new(current_app.secret_key.encode(), password_hash.encode(), hashlib.sha256).hexdigest()


def configure_security(app):
    secret = os.environ.get('SECRET_KEY', '')
    if len(secret) < 32:
        raise RuntimeError('Configura SECRET_KEY con una clave aleatoria de al menos 32 caracteres.')
    environment = os.environ.get('FLASK_ENV', 'production')
    if environment not in ('production', 'development'):
        raise RuntimeError('FLASK_ENV debe ser production o development.')
    production = environment == 'production'
    public_url = os.environ.get('PUBLIC_BASE_URL', 'https://talentlink.duckdns.org').rstrip('/')
    parsed = urlsplit(public_url)
    if (parsed.scheme not in ('http', 'https') or not parsed.netloc
            or parsed.username or parsed.password or parsed.query or parsed.fragment
            or parsed.path not in ('', '/') or (production and parsed.scheme != 'https')):
        raise RuntimeError('PUBLIC_BASE_URL debe ser el origen público; usa HTTPS en producción.')
    app.config.update(
        SECRET_KEY=secret,
        SESSION_COOKIE_SECURE=production,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
        PUBLIC_BASE_URL=public_url,
        CSRF_ENABLED=True,
        TRUSTED_HOSTS=[parsed.hostname] if production else None,
    )
    if os.environ.get('TRUST_PROXY') == '1':
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

    def csrf_token():
        if '_csrf_token' not in session:
            session['_csrf_token'] = secrets.token_urlsafe(32)
        return session['_csrf_token']

    app.jinja_env.globals['csrf_token'] = csrf_token

    @app.before_request
    def protect_modifications():
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return
        if app.testing and not app.config['CSRF_ENABLED']:
            return
        expected = session.get('_csrf_token')
        supplied = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token')
        if (not isinstance(expected, str) or not isinstance(supplied, str)
                or not secrets.compare_digest(expected.encode(), supplied.encode())):
            abort(400, description='El formulario ha expirado. Recarga la página e inténtalo de nuevo.')
