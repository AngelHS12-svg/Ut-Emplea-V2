"""Aislamiento obligatorio: las pruebas no pueden conectar a BD, SMTP ni red reales."""
import socket
import smtplib
import sys
import types
from unittest.mock import MagicMock

import pytest

# Disponible incluso al ejecutar un solo archivo de pruebas; nunca abre PostgreSQL.
_fake_psycopg2 = types.ModuleType('psycopg2')
_fake_psycopg2.connect = MagicMock()
sys.modules['psycopg2'] = _fake_psycopg2
for name in ('extras', 'extensions', 'pool'):
    module = types.ModuleType('psycopg2.' + name)
    setattr(_fake_psycopg2, name, module)
    sys.modules['psycopg2.' + name] = module
_fake_psycopg2.extras.RealDictCursor = MagicMock()
_fake_psycopg2.pool.ThreadedConnectionPool = MagicMock()


@pytest.fixture(autouse=True)
def isolate_services(monkeypatch):
    for key, value in {
        'SECRET_KEY': 'test-only-secret-with-more-than-32-characters',
        'FLASK_ENV': 'development', 'TRUST_PROXY': '0', 'DATABASE_URL': '',
        'DB_HOST': 'audit.invalid', 'DB_NAME': 'audit', 'DB_USER': 'audit',
        'DB_PASSWORD': 'audit', 'MAIL_USERNAME': 'audit@example.invalid',
        'MAIL_PASSWORD': 'audit',
    }.items():
        monkeypatch.setenv(key, value)

    def forbidden(*args, **kwargs):
        raise AssertionError('Una prueba intentó usar un servicio externo.')

    monkeypatch.setattr(socket.socket, 'connect', forbidden)
    monkeypatch.setattr(smtplib, 'SMTP_SSL', forbidden)
