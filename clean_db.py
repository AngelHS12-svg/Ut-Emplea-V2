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
        tables = [
            "postulaciones",
            "requisitos_vacante",
            "vacantes_guardadas",
            "vacantes",
            "recursos_humanos",
            "direcciones_empresa",
            "validacion_empresas",
            "validacion_candidatos",
            "empresas",
            "candidatos",
            "notificaciones"
        ]
        for table in tables:
            print(f"Eliminando {table}...")
            cur.execute(f"DELETE FROM {table}")
            
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
