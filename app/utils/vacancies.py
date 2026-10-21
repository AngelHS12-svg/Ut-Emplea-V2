"""Lectura pública de ofertas con el identificador ya existente en PostgreSQL."""

PUBLIC_VACANCY_FIELDS = (
    'id', 'titulo', 'descripcion', 'salario', 'modalidad', 'horario', 'lugar',
    'publicada', 'empresa', 'escolaridad', 'experiencia', 'requisitos',
    'vencimiento', 'perfil', 'plazas', 'disponible',
)


def public_vacancy(cur, vacancy_id):
    cur.execute("""
        SELECT v.id_vacante, v.titulo, v.descripcion, v.salario, v.modalidad,
               v.horario, v.lugar_trabajo, v.fecha_publicacion, e.nombre,
               r.escolaridad, r.experiencia, r.descripcion,
               v.fecha_vencimiento, v.perfil, v.num_vacantes,
               (v.fecha_vencimiento IS NULL OR v.fecha_vencimiento >= CURRENT_DATE)
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
