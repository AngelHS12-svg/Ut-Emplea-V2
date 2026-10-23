"""Aplicar solo la migración aditiva de formación y domicilios (sin importar main)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.config.database import get_connection


def migrate():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute((ROOT / 'database/migrations/20261022_formacion_domicilio.sql').read_text(encoding='utf-8'))
        print('Migración de formación y domicilios completada. Registros existentes conservados.')
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == '__main__':
    migrate()
