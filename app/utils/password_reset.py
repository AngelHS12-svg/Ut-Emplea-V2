"""Enlaces de recuperación ligados a la contraseña actual, sin columnas adicionales."""
import secrets

from flask import current_app
from itsdangerous import BadData, URLSafeTimedSerializer

from app.config.security import credential_stamp

RESET_MAX_AGE = 60 * 60


def _serializer():
    return URLSafeTimedSerializer(current_app.secret_key, salt='talentlink-password-reset-v1')


def create_reset_token(user_id, password_hash):
    return _serializer().dumps({'uid': user_id, 'stamp': credential_stamp(password_hash)})


def read_reset_token(token):
    if not isinstance(token, str) or len(token) > 1024:
        return None
    try:
        data = _serializer().loads(token, max_age=RESET_MAX_AGE)
    except BadData:
        return None
    if (not isinstance(data, dict) or type(data.get('uid')) is not int
            or data['uid'] < 1 or not isinstance(data.get('stamp'), str)
            or len(data['stamp']) != 64 or not data['stamp'].isascii()):
        return None
    return data


def matches_current_password(data, password_hash):
    return secrets.compare_digest(data['stamp'], credential_stamp(password_hash))
