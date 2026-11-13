"""Lectura pública de ofertas con el identificador ya existente en PostgreSQL."""
from decimal import Decimal, InvalidOperation


def salary_value(value):
    """El salario es opcional y se guarda como NUMERIC(10,2), sin perder centavos."""
    value = str(value if value is not None else '').strip()
    if not value:
        return None
    try:
        amount = Decimal(value)
        if not amount.is_finite() or amount < 0 or amount > Decimal('99999999.99'):
            raise ValueError
        rounded = amount.quantize(Decimal('0.01'))
        if rounded != amount:
            raise ValueError
        return rounded
    except (InvalidOperation, ValueError):
        raise ValueError('Indica un salario entre 0 y 99,999,999.99, con hasta dos decimales, o déjalo en blanco.') from None


def salary_values(form):
    """Devuelve el importe fijo o los extremos de un rango mensual en MXN."""
    if hasattr(form, 'getlist') and len(set(form.getlist('salario'))) > 1:
        raise ValueError('El formulario tiene dos salarios distintos. Recarga esta página y vuelve a editar.')
    mode = form.get('salario_tipo')
    if mode is None:  # Formularios anteriores que solo enviaban salario.
        mode = 'fijo' if str(form.get('salario', '')).strip() else 'no_especificado'
    if mode == 'no_especificado':
        return None, None
    if mode == 'fijo':
        amount = salary_value(form.get('salario'))
        if amount is None:
            raise ValueError('Indica el salario fijo mensual.')
        return amount, None
    if mode == 'rango':
        minimum = salary_value(form.get('salario_min'))
        maximum = salary_value(form.get('salario_max'))
        if minimum is None or maximum is None:
            raise ValueError('Indica el salario mínimo y máximo del rango mensual.')
        if minimum >= maximum:
            raise ValueError('El salario máximo debe ser mayor que el mínimo.')
        return minimum, maximum
    raise ValueError('Selecciona una forma válida de indicar el salario.')


def salary_label(amount, maximum=None):
    """Texto compartido por vistas, API y exportaciones."""
    if amount is None:
        return 'No especificado'
    if maximum is not None:
        return f'Aprox. ${amount:,.2f} a ${maximum:,.2f} MXN mensuales'
    return f'${amount:,.2f} MXN mensuales'

PUBLIC_VACANCY_FIELDS = (
    'id', 'titulo', 'descripcion', 'salario', 'modalidad', 'horario', 'lugar',
    'publicada', 'empresa', 'escolaridad', 'experiencia', 'requisitos',
    'vencimiento', 'perfil', 'plazas', 'disponible', 'salario_max',
)


def public_vacancy(cur, vacancy_id):
    cur.execute("""
        SELECT v.id_vacante, v.titulo, v.descripcion, v.salario, v.modalidad,
               v.horario, v.lugar_trabajo, v.fecha_publicacion, e.nombre,
               r.escolaridad, r.experiencia, r.descripcion,
               v.fecha_vencimiento, v.perfil, v.num_vacantes,
               (v.fecha_vencimiento IS NULL OR v.fecha_vencimiento >= CURRENT_DATE),
               v.salario_max
        FROM vacantes v
        JOIN empresas e ON e.id_empresa=v.id_empresa
        LEFT JOIN requisitos_vacante r ON r.id_vacante=v.id_vacante
        WHERE v.id_vacante=%s AND v.estatus='activa' AND e.estatus='aprobada'
    """, (vacancy_id,))
    row = cur.fetchone()
    return dict(zip(PUBLIC_VACANCY_FIELDS, row)) if row else None


def vacancy_return_id(value):
    """Solo se admite el ID de una ruta local conocida, nunca una URL arbitraria."""
    value = str(value or '')
    if not value.isascii() or not value.isdigit() or len(value) > 10:
        return None
    number = int(value)
    return number if 0 < number <= 2147483647 else None
