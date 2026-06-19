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
# 1. Eliminar absolutamente TODOS los usuarios de la base de datos
cur.execute("DELETE FROM usuarios")
conn.commit()
print("Todas las cuentas anteriores han sido eliminadas.")

# 2. Insertar el administrador real
correo_admin = "bolsadetrabajo@utdeoriental.edu.mx"
hashed = generate_password_hash("UT_Oriental_2026!#")

cur.execute("""
    INSERT INTO usuarios (id_rol, correo, password, activo)
    VALUES (1, %s, %s, true)
""", (correo_admin, hashed))

conn.commit()
print("Usuario admin creado exitosamente.")
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
