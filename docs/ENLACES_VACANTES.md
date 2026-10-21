# Enlaces individuales de vacantes

Cada vacante se consulta en `/vacantes/<id_vacante>`. Por ejemplo, el registro con `id_vacante=42` se comparte como `https://talentlink.duckdns.org/vacantes/42`. El número visible coincide con el de PostgreSQL: no se inventan identificadores, no se renumeran los existentes y no cambia el enlace al editar el título.

No se requieren migraciones, columnas nuevas ni volver a publicar las vacantes actuales. Abrir el enlace solo ejecuta consultas SELECT. Se conservan los registros de las ofertas, sus requisitos, archivos, postulaciones y vacantes guardadas. Las nuevas ofertas reciben automáticamente su enlace mediante el ID que ya asigna PostgreSQL.

## Uso

- Empresa: en **Mis Vacantes** aparecen el ID, **Ver enlace público** y **Copiar enlace**.
- Administrador: las tarjetas muestran el ID y las mismas opciones de compartir, además de sus controles privados existentes.
- Candidato: **Todas las Vacantes** y **Buscar Vacantes** muestran el ID y opciones para abrir/copiar la URL. Cambiar la selección actualiza el enlace correspondiente.
- El visitante puede leer la oferta sin cuenta. Para postularse inicia sesión como candidato y verifica su código 2FA; después vuelve a la oferta compartida. La postulación siempre requiere una acción POST explícita con CSRF.
- El botón copia al portapapeles. Si el navegador lo impide, abre un cuadro con el enlace seleccionado para copiarlo manualmente.

## Visibilidad y compatibilidad

Se muestran públicamente solo las vacantes con estado `activa` de empresas `aprobada`, siguiendo el criterio de los listados de candidatos. No se muestran datos privados de contacto, candidatos, postulaciones ni controles de edición. Si una oferta activa superó su fecha de vencimiento, su URL conserva la información y señala **Convocatoria finalizada**, sin permitir postularse o guardarla. La vigencia se calcula con `CURRENT_DATE` de PostgreSQL; se admite el día de cierre completo.

Una vacante eliminada, inactiva, de empresa no aprobada o inexistente devuelve una página 404 sin detalles privados. Sus IDs no se reasignan. Los controles de empresa y administrador siguen usando sus rutas privadas autorizadas; la página pública no da permisos de administración.

Las direcciones anteriores `/candidato/detalle-vacante/<id>` redirigen permanentemente a `/vacantes/<id>`, por lo que las notificaciones y enlaces anteriores siguen funcionando. Las nuevas notificaciones ya usan la ruta pública. El dominio de los enlaces se toma de `PUBLIC_BASE_URL`, sin confiar en el Host enviado por el visitante.

## Despliegue y comprobación

Se usa el mismo procedimiento de [RECUPERACION_PASSWORD.md](RECUPERACION_PASSWORD.md): subir el código, mantener `.env` y `SECRET_KEY`, incorporar con `git pull`, ajustar lectura de CSS/JS y reconstruir/recrear web y Nginx. No recrear la base de datos ni ejecutar scripts de limpieza o reinicialización. Las sesiones actuales se conservan mientras se mantenga `SECRET_KEY`.

Las pruebas locales usan servicios simulados y cubren IDs existentes sin escrituras, enlaces anteriores, ofertas inexistentes/no públicas, vigencia, escape de texto, permisos para acciones de candidato, CSRF, regreso tras login y 2FA, URLs de compartir y portapapeles con alternativa manual. No se accedió ni se crearon registros en producción.

```shell
python -m pytest tests/test_vacancy_links.py
node --test tests/vacancy_share.test.js
```
