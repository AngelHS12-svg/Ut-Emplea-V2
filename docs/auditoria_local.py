"""Ejecuta las regresiones actuales; BD, correo y red se aíslan en tests/conftest.py.

El informe y auditoria_resultados.json conservan la instantánea previa a las correcciones.
"""
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.append(str(ROOT / 'Lib' / 'site-packages'))

if __name__ == '__main__':
    import pytest
    raise SystemExit(pytest.main([str(ROOT / 'tests'), '-q', '-p', 'no:cacheprovider']))
