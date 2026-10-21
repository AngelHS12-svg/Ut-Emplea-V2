"""Cambio explícito de contraseña de una cuenta administrativa existente."""
import argparse
from getpass import getpass
import os

from app.config.database import get_connection
from app.utils.passwords import password_error
from werkzeug.security import generate_password_hash


def update_admin_password(email, password):
    error = password_error(password)
    if error:
        raise ValueError(error)
    hashed = generate_password_hash(password)
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE usuarios SET password=%s, reset_token=NULL, reset_expires=NULL,
                two_fa_code=NULL, two_fa_expires=NULL
            WHERE correo=%s AND id_rol IN (
                SELECT id_rol FROM roles WHERE nombre='Administrador'
            )
        """, (hashed, email))
        changed = cur.rowcount > 0
        conn.commit()
        return changed
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--email', required=True)
    args = parser.parse_args()
    password = os.environ.get('ADMIN_PASSWORD') or getpass('Nueva contraseña: ')
    if not os.environ.get('ADMIN_PASSWORD') and password != getpass('Confirma la contraseña: '):
        parser.error('Las contraseñas no coinciden.')
    try:
        changed = update_admin_password(args.email.strip(), password)
    except ValueError as exc:
        parser.error(str(exc))
    print('Contraseña actualizada.' if changed else 'No se encontró esa cuenta administrativa.')


if __name__ == '__main__':
    main()
