import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection():
    connection = psycopg2.connect(
        host="localhost",
        database="bolsa_trabajo_uto",
        user="postgres",
        password="angel123",
        port="5432"
    )
    return connection

def verificar_usuarios():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Consultar todos los usuarios
    cur.execute("""
        SELECT u.id_usuario, u.correo, u.password, r.nombre AS rol
        FROM usuarios u
        JOIN roles r ON u.id_rol = r.id_rol
        ORDER BY u.id_usuario;
    """)
    
    usuarios = cur.fetchall()
    
    for usuario in usuarios:
        print(f"ID: {usuario['id_usuario']}, Correo: {usuario['correo']}, Contraseña: {usuario['password']}, Rol: {usuario['rol']}")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    verificar_usuarios()