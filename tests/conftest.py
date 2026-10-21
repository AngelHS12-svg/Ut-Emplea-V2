"""Aislamiento obligatorio: las pruebas no pueden conectar a BD, SMTP ni red reales."""
import socket
import smtplib

import pytest


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
