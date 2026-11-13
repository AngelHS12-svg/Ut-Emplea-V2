from decimal import Decimal

import pytest

from app.utils.vacancies import salary_label, salary_values


@pytest.mark.parametrize(('form', 'expected'), [
    ({'salario_tipo': 'no_especificado'}, (None, None)),
    ({'salario_tipo': 'fijo', 'salario': '10000.50'}, (Decimal('10000.50'), None)),
    ({'salario_tipo': 'rango', 'salario_min': '8000', 'salario_max': '10000'},
     (Decimal('8000.00'), Decimal('10000.00'))),
    ({'salario': '8000'}, (Decimal('8000.00'), None)),
])
def test_salary_values(form, expected):
    assert salary_values(form) == expected


@pytest.mark.parametrize('form', [
    {'salario_tipo': 'fijo'},
    {'salario_tipo': 'rango', 'salario_min': '8000'},
    {'salario_tipo': 'rango', 'salario_min': '10000', 'salario_max': '8000'},
    {'salario_tipo': 'rango', 'salario_min': '-1', 'salario_max': '8000'},
    {'salario_tipo': 'texto', 'salario': '10000'},
])
def test_salary_rejects_invalid_forms(form):
    with pytest.raises(ValueError):
        salary_values(form)


def test_salary_label_covers_all_modes_including_zero():
    assert salary_label(None) == 'No especificado'
    assert salary_label(Decimal('0')) == '$0.00 MXN mensuales'
    assert salary_label(Decimal('8000'), Decimal('10000')) == (
        'Aprox. $8,000.00 a $10,000.00 MXN mensuales')
