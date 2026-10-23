"""Formación por nivel, con lectura compatible de perfiles anteriores."""
from datetime import date

from app.utils.security import strip_tags


def read_education(form):
    education = {}
    for key in ('tsu', 'superior'):
        program = strip_tags(form.get('programa_' + key)).strip()
        institution = strip_tags(form.get('institucion_' + key)).strip()
        year = (form.get('egreso_' + key) or '').strip()
        if len(program) > 255 or len(institution) > 255:
            raise ValueError('El programa y la institución admiten hasta 255 caracteres.')
        if key == 'tsu' and not program:
            raise ValueError('Indica tu programa educativo de Técnico Superior Universitario (TSU).')
        if year and (not year.isascii() or not year.isdigit() or not 1950 <= int(year) <= date.today().year):
            raise ValueError('El año de egreso debe ser válido y no puede ser futuro.')
        if key == 'superior' and not program:
            if year or institution:
                raise ValueError('Indica el programa de ingeniería o licenciatura, o deja ese nivel en blanco.')
            continue
        if key == 'tsu' and (not institution or not year):
            raise ValueError('Completa la institución y el año de egreso de tu TSU.')
        kind = 'TSU' if key == 'tsu' else (form.get('tipo_superior') or '')
        if key == 'superior' and kind not in ('Ingeniería', 'Licenciatura'):
            raise ValueError('Selecciona si tu segundo programa corresponde a ingeniería o licenciatura.')
        education[key] = {'tipo': kind, 'programa': program,
                          'institucion': institution, 'egreso': int(year) if year else None}
    if education.get('superior', {}).get('egreso') and education['superior']['egreso'] < education['tsu']['egreso']:
        raise ValueError('El egreso de ingeniería o licenciatura no puede ser anterior al de TSU.')
    return education


def legacy_education(education, degree, institution, program, year):
    """No asignar un TSU a alguien cuyo registro anterior solo indica otro grado."""
    if isinstance(education, dict) and education.get('tsu'):
        return education
    if not program:
        return {}
    record = {'tipo': degree or 'Formación registrada', 'programa': program,
              'institucion': institution or '', 'egreso': year}
    degree = (degree or '').strip().casefold()
    if degree in ('tsu', 'técnico superior universitario', 'tecnico superior universitario'):
        return {'tsu': record, '_legacy': True}
    if degree in ('ingeniería', 'ingenieria', 'licenciatura', 'ingeniería/licenciatura'):
        return {'superior': record, '_legacy': True}
    return {'anterior': record, '_legacy': True}


def highest_education(education):
    return education.get('superior') or education['tsu']
