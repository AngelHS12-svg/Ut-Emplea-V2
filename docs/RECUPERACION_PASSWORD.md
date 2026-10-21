# Recuperación de contraseña de Talent Link

El registro de PostgreSQL compartido por el operador mostró `column "reset_token" of relation "usuarios" does not exist`. El flujo anterior dependía de `reset_token` y `reset_expires`, que tampoco figuran en el esquema versionado. La interfaz existía, pero faltaba manejar estos errores y estados del proceso.

La solicitud ahora genera un enlace firmado con ItsDangerous (dependencia existente), vigente por una hora, asociado al identificador del usuario y a una huella HMAC de su contraseña actual. No escribe tokens en la BD ni requiere una migración. El cambio de contraseña verifica usuario activo y hash anterior en el mismo UPDATE, evitando que el enlace vuelva a cambiarla, incluso ante solicitudes concurrentes. El inicio de sesión continúa exigiendo 2FA.

La ruta `/auth/forgot-password` tiene una pantalla propia, accesible desde el login compartido por empresa y candidato. Incluye confirmación de solicitud, errores de validación, formulario de nueva contraseña y estados de enlace inválido, servicio no disponible y cambio completado. Usa verde, dorado, vino, tipografías e identidad de UT de Oriental. Las respuestas no confirman si existe una cuenta. Una falla de SMTP se registra internamente y mantiene esa misma respuesta; la pantalla no garantiza la entrega.

No se modifican cuentas, archivos, roles ni la clave de sesión del servidor. Solo al completar la recuperación se cambia la contraseña de esa cuenta y se invalidan sus sesiones y códigos 2FA pendientes. Solicitar un enlace no cierra sesiones. Los enlaces del mecanismo anterior deberán solicitarse nuevamente.

## Publicar sobre la instalación actual

Conservar el `.env` actual, especialmente `SECRET_KEY`, y los respaldos existentes. Después de subir esta revisión al repositorio, ejecutar mediante SSH desde `~/mi-proyecto`, deteniéndose si falla un paso:

```bash
git status --short
git pull --ff-only origin main

# Nginx necesita leer los archivos estáticos creados por Git.
# Un umask 077 durante el respaldo también afecta a archivos nuevos del pull.
chmod 755 public
find public/css public/js -type d -exec chmod 755 {} +
find public/css public/js -type f -exec chmod 644 {} +

docker compose config --quiet
docker compose build web
docker compose run --rm --no-deps web python -c "from main import app; print('Configuración de Flask correcta')"
docker compose up -d --no-deps --no-build web
docker compose up -d --no-deps --force-recreate nginx
docker compose ps
docker compose logs --tail=40 web nginx
```

Los permisos se aplican solo a código CSS/JS público; no afectan `.env`, respaldos ni uploads. La corrección también resuelve el `403 Permission denied` reportado para `public/js/security.js`. No se recrea PostgreSQL ni se cambian sus volúmenes. Mantener `SECRET_KEY` conserva las sesiones actuales de las cuentas que no cambien su contraseña.

La comprobación completa de recuperación se hace en local con BD y correo simulados. Las pruebas bloquean conexiones externas y no crean cuentas ni envían mensajes reales. Para repetirlas: `python -m pytest tests/test_password_recovery.py tests/test_security.py tests/test_templates.py` con las dependencias de desarrollo instaladas.
