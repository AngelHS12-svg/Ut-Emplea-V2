import psycopg2
import os

def check_and_create_schema():
    print("Connecting to database...")
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "bolsa_trabajo_uto"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASS", "angel123"),
        port=os.getenv("DB_PORT", "5432")
    )
    cur = conn.cursor()
    
    try:
        print("Creating vacantes_guardadas table if it doesn't exist...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS vacantes_guardadas (
                id_guardada SERIAL PRIMARY KEY,
                id_candidato INTEGER NOT NULL REFERENCES candidatos(id_candidato) ON DELETE CASCADE,
                id_vacante INTEGER NOT NULL REFERENCES vacantes(id_vacante) ON DELETE CASCADE,
                fecha_guardado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(id_candidato, id_vacante)
            )
        """)
        
        conn.commit()
        print("Success! Table vacantes_guardadas is ready.")
        
    except Exception as e:
        print(f"Error executing schema update: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()
        print("Connection closed.")

if __name__ == "__main__":
    check_and_create_schema()
