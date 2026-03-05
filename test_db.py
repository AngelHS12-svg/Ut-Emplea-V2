from app.config.database import get_connection

conn = get_connection()

if conn:
    print("Conexion exitosa a PostgreSQL")
else:
    print("Error de conexion")