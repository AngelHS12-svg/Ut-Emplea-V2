"""Consultas de solo lectura sobre el catálogo SEPOMEX incluido en la imagen."""
from contextlib import closing
from functools import lru_cache
from pathlib import Path
import re
import sqlite3

from app.utils.security import strip_tags

CATALOG = Path(__file__).resolve().parents[1] / 'data/sepomex.sqlite3'
FALLBACK_STATES = (
    'Aguascalientes', 'Baja California', 'Baja California Sur', 'Campeche', 'Chiapas',
    'Chihuahua', 'Ciudad de México', 'Coahuila de Zaragoza', 'Colima', 'Durango',
    'Guanajuato', 'Guerrero', 'Hidalgo', 'Jalisco', 'Michoacán de Ocampo', 'Morelos',
    'México', 'Nayarit', 'Nuevo León', 'Oaxaca', 'Puebla', 'Querétaro', 'Quintana Roo',
    'San Luis Potosí', 'Sinaloa', 'Sonora', 'Tabasco', 'Tamaulipas', 'Tlaxcala',
    'Veracruz de Ignacio de la Llave', 'Yucatán', 'Zacatecas',
)


def query(sql, values=()):
    with closing(sqlite3.connect(CATALOG.as_uri() + '?mode=ro', uri=True)) as conn:
        return conn.execute(sql, values).fetchall()


@lru_cache(maxsize=512)
def postal_places(cp):
    if not re.fullmatch(r'[0-9]{5}', cp):
        return []
    return [dict(zip(('colonia', 'municipio', 'estado', 'ciudad'), row)) for row in query(
        'SELECT DISTINCT colonia, municipio, estado, ciudad FROM asentamientos WHERE cp = ? ORDER BY colonia, municipio', (cp,))]


@lru_cache(maxsize=1)
def states():
    try:
        return [row[0] for row in query('SELECT DISTINCT estado FROM asentamientos ORDER BY estado')]
    except sqlite3.Error:
        # El formulario y la captura manual siguen disponibles si falta el catálogo.
        return list(FALLBACK_STATES)


@lru_cache(maxsize=512)
def municipalities(state):
    return [row[0] for row in query('SELECT DISTINCT municipio FROM asentamientos WHERE estado = ? ORDER BY municipio', (state,))]


@lru_cache(maxsize=512)
def cities(state, municipality):
    return [row[0] for row in query('''SELECT DISTINCT ciudad FROM asentamientos
        WHERE estado = ? AND municipio = ? AND ciudad != '' ORDER BY ciudad''', (state, municipality))]


def read_address(form, required=True):
    address = {key: strip_tags(form.get(key)).strip() for key in ('estado', 'municipio', 'ciudad', 'colonia')}
    cp = strip_tags(form.get('codigo_postal')).strip()
    if (required or cp) and not re.fullmatch(r'[0-9]{5}', cp):
        raise ValueError('El código postal debe tener 5 dígitos.')
    if form.get('pais', 'México') != 'México':
        raise ValueError('El domicilio debe estar en México.')
    if any(len(value) > 150 for value in address.values()):
        raise ValueError('Cada dato del domicilio admite hasta 150 caracteres.')
    if required or any(address.values()):
        if not all(address[key] for key in ('estado', 'municipio', 'colonia')):
            raise ValueError('Completa el estado, municipio y colonia del domicilio.')
        if address['estado'] not in states():
            raise ValueError('Selecciona un estado del catálogo de México.')
    return address


def address_text(street, address):
    parts = [street] + [address.get(k) for k in ('colonia', 'ciudad', 'municipio', 'estado')]
    return ', '.join(dict.fromkeys(value for value in parts if value))
