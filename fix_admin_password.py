"""
Script para actualizar la contraseña del admin.
"""
import os
import psycopg2
from werkzeug.security import generate_password_hash

if os.getenv("DATABASE_URL"):
    conn = psycopg2.connect(dsn=os.getenv("DATABASE_URL"))
else:
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "bolsa_trabajo_uto"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASS", "angel123"),
        port=os.getenv("DB_PORT", "5432")
    )
cur = conn.cursor()

hashed = generate_password_hash("Admin123!")
cur.execute("UPDATE usuarios SET password = %s WHERE correo = %s", (hashed, "admin@utoriental.edu.mx"))

if cur.rowcount > 0:
    conn.commit()
    print("Contraseña del admin actualizada exitosamente.")
    print("Correo: admin@utoriental.edu.mx")
    print("Contraseña: Admin123!")
else:
    print("No se encontró el usuario admin.")

cur.close()
conn.close()
