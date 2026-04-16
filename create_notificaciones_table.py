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

def create_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notificaciones (
            id_notificacion SERIAL PRIMARY KEY,
            id_usuario INTEGER NOT NULL REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
            tipo VARCHAR(50) NOT NULL,
            mensaje TEXT NOT NULL,
            url VARCHAR(255),
            leida BOOLEAN DEFAULT FALSE,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("Tabla notificaciones creada exitosamente.")

if __name__ == "__main__":
    create_table()
