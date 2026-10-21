from app.config.database import get_connection
import psycopg2
import os

def migrate():
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        print("Iniciando migración de la tabla 'candidatos'...")
        
        # Nuevas columnas
        alter_queries = [
            "ALTER TABLE candidatos ADD COLUMN IF NOT EXISTS codigo_postal VARCHAR(10)",
            "ALTER TABLE candidatos ADD COLUMN IF NOT EXISTS ubicacion VARCHAR(255)",
            "ALTER TABLE candidatos ADD COLUMN IF NOT EXISTS carrera TEXT",
            "ALTER TABLE candidatos ADD COLUMN IF NOT EXISTS ultimo_grado_estudios VARCHAR(100)",
            "ALTER TABLE candidatos ADD COLUMN IF NOT EXISTS institucion_estudios VARCHAR(255)",
            "ALTER TABLE candidatos ADD COLUMN IF NOT EXISTS carrera_estudios VARCHAR(255)",
            "ALTER TABLE candidatos ADD COLUMN IF NOT EXISTS ultimo_puesto VARCHAR(100)",
            "ALTER TABLE candidatos ADD COLUMN IF NOT EXISTS ultima_empresa VARCHAR(100)",
            "ALTER TABLE candidatos ADD COLUMN IF NOT EXISTS fecha_inicio_laboral VARCHAR(50)",
            "ALTER TABLE candidatos ADD COLUMN IF NOT EXISTS fecha_fin_laboral VARCHAR(50)",
            "ALTER TABLE candidatos ADD COLUMN IF NOT EXISTS actividades_logros TEXT",
            "ALTER TABLE candidatos ADD COLUMN IF NOT EXISTS puesto_deseado VARCHAR(100)",
            "ALTER TABLE candidatos ADD COLUMN IF NOT EXISTS sueldo_deseado DECIMAL(12,2)",
            "ALTER TABLE candidatos ADD COLUMN IF NOT EXISTS area_trabajo VARCHAR(100)",
            "ALTER TABLE candidatos ADD COLUMN IF NOT EXISTS especialidad VARCHAR(100)",
            "ALTER TABLE candidatos ADD COLUMN IF NOT EXISTS tags_especialidad TEXT",
            "ALTER TABLE candidatos ADD COLUMN IF NOT EXISTS idiomas TEXT",
            "ALTER TABLE candidatos ADD COLUMN IF NOT EXISTS cursos_certificaciones TEXT",
            "ALTER TABLE candidatos ADD COLUMN IF NOT EXISTS foto_perfil_url TEXT"
        ]
        
        for query in alter_queries:
            try:
                cur.execute(query)
                print(f"Ejecutado: {query}")
            except Exception as e:
                print(f"Error en query '{query}': {e}")
                conn.rollback()
        
        conn.commit()
        print("✅ Migración completada exitosamente.")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error de conexión: {e}")

if __name__ == "__main__":
    migrate()
