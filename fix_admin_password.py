"""
Script para actualizar la contraseña del admin.
"""
import psycopg2
from werkzeug.security import generate_password_hash

conn = psycopg2.connect(
    host="localhost",
    database="bolsa_trabajo_uto",
    user="postgres",
    password="angel123",
    port="5432"
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
