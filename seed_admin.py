"""
Script para crear un usuario administrador temporal para pruebas.
Ejecutar: python seed_admin.py
Credenciales: admin@utoriental.edu.mx / Admin123!
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

# 1. Eliminar el administrador de prueba anterior si existe
cur.execute("DELETE FROM usuarios WHERE correo = %s", ("admin@utoriental.edu.mx",))
conn.commit()

# 2. Insertar o actualizar el administrador real
correo_admin = "bolsadetrabajo@utdeoriental.edu.mx"
hashed = generate_password_hash("UT_Oriental_2026!#")

cur.execute("SELECT id_usuario FROM usuarios WHERE correo = %s", (correo_admin,))
if cur.fetchone():
    # Si ya existe (por si acaso), actualizamos la contraseña y lo activamos
    cur.execute("""
        UPDATE usuarios 
        SET password = %s, activo = true, id_rol = 1 
        WHERE correo = %s
    """, (hashed, correo_admin))
    print("El usuario admin ya existía. Se actualizó la contraseña correctamente.")
else:
    # Si no existe, lo insertamos
    cur.execute("""
        INSERT INTO usuarios (id_rol, correo, password, activo)
        VALUES (1, %s, %s, true)
    """, (correo_admin, hashed))
    print("Usuario admin creado exitosamente.")

conn.commit()
print(f"Correo: {correo_admin}")
print("Contraseña: UT_Oriental_2026!#")

# Insertar carreras si no existen
cur.execute("SELECT COUNT(*) FROM carreras")
if cur.fetchone()[0] == 0:
    carreras = [
        ("Ingeniería en Sistemas Computacionales", "Desarrollo de software y sistemas"),
        ("Administración", "Gestión empresarial"),
        ("Contaduría Pública", "Contabilidad y finanzas"),
        ("Ingeniería Industrial", "Procesos y producción"),
        ("Diseño Gráfico", "Diseño visual y multimedia"),
    ]
    for nombre, desc in carreras:
        cur.execute("INSERT INTO carreras (nombre, descripcion) VALUES (%s, %s)", (nombre, desc))
    conn.commit()
    print("Carreras insertadas.")

cur.close()
conn.close()
