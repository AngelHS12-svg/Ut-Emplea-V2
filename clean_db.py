import psycopg2
import os

def get_connection():
    if os.getenv("DATABASE_URL"):
        return psycopg2.connect(dsn=os.getenv("DATABASE_URL"))
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "bolsa_trabajo_uto"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASS", "angel123"),
        port=os.getenv("DB_PORT", "5432")
    )

def clean_db():
    conn = get_connection()
    cur = conn.cursor()
    try:
        print("Eliminando candidatos...")
        cur.execute("DELETE FROM candidatos")
        print("Eliminando empresas...")
        cur.execute("DELETE FROM empresas")
        print("Eliminando notificaciones...")
        cur.execute("DELETE FROM notificaciones")
        print("Eliminando vacantes...")
        cur.execute("DELETE FROM vacantes")
        print("Eliminando usuarios que no sean Admi...")
        cur.execute("DELETE FROM usuarios WHERE id_rol != 1")
        conn.commit()
        print("Base de datos limpiada. Solo quedan administradores.")
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    clean_db()
