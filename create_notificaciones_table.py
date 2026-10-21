from app.config.database import get_connection
import psycopg2
import os

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
