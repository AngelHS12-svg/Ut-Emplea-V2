"""Recuperación administrativa de una empresa ya aprobada. Vista previa por defecto."""

import argparse
import re
import secrets
import sys
from pathlib import Path

from werkzeug.security import generate_password_hash


class RecoveryError(Exception):
    pass


def recover(conn, current_email, new_email, company_id=None, apply=False):
    if any(len(email) > 150 or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email)
           for email in (current_email, new_email)):
        raise RecoveryError("Revisa el formato de los correos.")
    if current_email.casefold() == new_email.casefold():
        raise RecoveryError("El correo nuevo debe ser distinto del anterior.")
    if apply and (company_id is None or company_id < 1):
        raise RecoveryError("Indica el ID de empresa de la vista previa para aplicar el cambio.")

    try:
        with conn.cursor() as cur:
            if apply:
                cur.execute("SET LOCAL lock_timeout = '5s'")
            query = """
                SELECT e.id_empresa, e.nombre, e.estatus, u.id_usuario, u.activo
                FROM empresas e
                JOIN usuarios u ON u.id_usuario = e.id_usuario
                JOIN roles r ON r.id_rol = u.id_rol
                WHERE u.correo = %s AND r.nombre = 'Empresa'
            """
            params = [current_email]
            if company_id is not None:
                query += " AND e.id_empresa = %s"
                params.append(company_id)
            if apply:
                query += " FOR UPDATE OF e, u"
            cur.execute(query, params)
            company = cur.fetchone()
            if not company:
                raise RecoveryError("No encontré una cuenta de empresa con ese correo e ID.")
            found_id, name, status, user_id, active = company
            if not active or status != "aprobada":
                raise RecoveryError(f"Empresa #{found_id}: {name}. La cuenta debe estar activa y aprobada.")

            cur.execute("SELECT 1 FROM usuarios WHERE lower(correo) = lower(%s) LIMIT 1", (new_email,))
            if cur.fetchone():
                raise RecoveryError("El correo nuevo ya pertenece a una cuenta. No se cambió ningún registro.")

            if apply:
                # La clave aleatoria no se muestra. El nuevo titular elige la suya mediante recuperación.
                replacement_hash = generate_password_hash(secrets.token_urlsafe(48))
                cur.execute("""
                    UPDATE usuarios
                    SET correo = %s, password = %s, two_fa_code = NULL, two_fa_expires = NULL
                    WHERE id_usuario = %s AND correo = %s AND activo IS TRUE
                    RETURNING id_usuario
                """, (new_email, replacement_hash, user_id, current_email))
                if cur.fetchone() != (user_id,):
                    raise RecoveryError("La cuenta cambió durante la operación. Vuelve a revisar los datos.")
        if apply:
            conn.commit()
        else:
            conn.rollback()
        return found_id, name
    except Exception:
        conn.rollback()
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--actual", required=True, help="Correo de acceso que figura en la cuenta")
    parser.add_argument("--nuevo", required=True, help="Correo autorizado por la empresa")
    parser.add_argument("--empresa", type=int, help="ID de la empresa confirmado en la vista previa")
    parser.add_argument("--aplicar", action="store_true", help="Guardar el cambio (requiere --empresa)")
    args = parser.parse_args()
    if args.aplicar and (args.empresa is None or args.empresa < 1):
        parser.error("--aplicar requiere el ID positivo de --empresa")

    if __file__ != "<stdin>":
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from app.config.database import get_connection

    conn = None
    try:
        conn = get_connection()
        company_id, name = recover(conn, args.actual.strip(), args.nuevo.strip(), args.empresa, args.aplicar)
    except RecoveryError as error:
        print(f"No se aplicó el cambio: {error}", file=sys.stderr)
        return 1
    except Exception as error:
        sqlstate = getattr(error, "pgcode", None)
        print(f"No se confirmó el cambio. Error: {type(error).__name__}"
              + (f" ({sqlstate})" if sqlstate else ""), file=sys.stderr)
        return 1
    finally:
        if conn is not None:
            conn.close()
    print(f"Empresa #{company_id}: {name}")
    if args.aplicar:
        print("Correo actualizado. La empresa ya puede usar «Olvidé mi contraseña» con su nuevo correo.")
    else:
        print(f"Vista previa: {args.actual.strip()} -> {args.nuevo.strip()}. No se guardó ningún cambio.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
