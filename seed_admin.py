"""
Script para crear un usuario administrador temporal para pruebas.
Ejecutar: python seed_admin.py
Credenciales: admin@utoriental.edu.mx / Admin123!
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

# Verificar si ya existe
cur.execute("SELECT id_usuario FROM usuarios WHERE correo = %s", ("admin@utoriental.edu.mx",))
if cur.fetchone():
    print("El usuario admin ya existe.")
else:
    hashed = generate_password_hash("Admin123!")
    cur.execute("""
        INSERT INTO usuarios (id_rol, correo, password)
        VALUES (1, %s, %s)
    """, ("admin@utoriental.edu.mx", hashed))
    conn.commit()
    print("Usuario admin creado exitosamente.")
    print("Correo: admin@utoriental.edu.mx")
    print("Contraseña: Admin123!")

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
