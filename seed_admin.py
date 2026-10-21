"""Alta explícita de administrador. Nunca elimina ni reemplaza cuentas existentes."""
import argparse
from getpass import getpass
import os

from app.config.database import get_connection
from app.utils.passwords import password_error
from werkzeug.security import generate_password_hash


def create_admin(email, password):
    error = password_error(password)
    if error:
        raise ValueError(error)
    if not email or "@" not in email:
        raise ValueError("Indica un correo válido.")
    hashed = generate_password_hash(password)
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO usuarios (id_rol, correo, password, activo)
            SELECT id_rol, %s, %s, true FROM roles WHERE nombre='Administrador'
            ON CONFLICT (correo) DO NOTHING RETURNING id_usuario
        """, (email, hashed))
        created = cur.fetchone() is not None
        conn.commit()
        return created
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
        created = create_admin(args.email.strip(), password)
    except ValueError as exc:
        parser.error(str(exc))
    print('Administrador creado.' if created else 'No se creó: el correo ya existe o falta el rol Administrador.')


if __name__ == '__main__':
    main()
