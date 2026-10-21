from app.config.database import get_connection
import psycopg2
import os

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
