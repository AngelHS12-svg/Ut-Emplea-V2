"""Crear el catálogo SQLite a partir del TXT SEPOMEX delimitado por |.

Uso: python maintenance/import_postal_catalog.py archivo.txt [--encoding utf-8]
Acepta exportaciones con/sin cabecera. No conecta a la base de producción.
"""
import argparse
import csv
import sqlite3
from pathlib import Path


def build(source, destination, encoding='utf-8'):
    destination = Path(destination)
    temporary = destination.with_suffix('.building')
    destination.parent.mkdir(parents=True, exist_ok=True)
    if temporary.exists():
        temporary.unlink()
    conn = sqlite3.connect(temporary)
    try:
        conn.executescript('''
            CREATE TABLE asentamientos (
                cp TEXT NOT NULL, colonia TEXT NOT NULL, municipio TEXT NOT NULL,
                estado TEXT NOT NULL, ciudad TEXT NOT NULL
            );
        ''')
        count = 0
        with open(source, encoding=encoding, newline='') as stream:
            for row in csv.reader(stream, delimiter='|'):
                if len(row) < 6 or len(row[0]) != 5 or not row[0].isascii() or not row[0].isdigit():
                    continue
                fields = [v.strip() for v in row[:6]]
                if '\ufffd' in ''.join(fields):
                    raise ValueError('El catálogo contiene caracteres dañados; revisa la codificación.')
                conn.execute('INSERT INTO asentamientos VALUES (?, ?, ?, ?, ?)',
                             (fields[0], fields[1], fields[3], fields[4], fields[5]))
                count += 1
        if count < 100000:
            raise ValueError('La importación no contiene un catálogo nacional completo.')
        conn.executescript('''
            CREATE INDEX postal_cp ON asentamientos(cp);
            CREATE INDEX postal_estado ON asentamientos(estado, municipio, ciudad);
        ''')
        conn.commit()
        if conn.execute('SELECT COUNT(DISTINCT estado) FROM asentamientos').fetchone()[0] != 32:
            raise ValueError('Se esperaban las 32 entidades federativas.')
        if conn.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise ValueError('El catálogo SQLite no superó la revisión de integridad.')
        conn.close()
        temporary.replace(destination)
        return count
    finally:
        conn.close()
        if temporary.exists():
            temporary.unlink()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source')
    parser.add_argument('--encoding', default='utf-8')
    parser.add_argument('--output', default=str(Path(__file__).resolve().parents[1] / 'app/data/sepomex.sqlite3'))
    args = parser.parse_args()
    print(f'{build(args.source, args.output, args.encoding)} asentamientos importados.')
