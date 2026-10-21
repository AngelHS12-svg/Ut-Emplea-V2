# Primera entrega de seguridad — 21 de octubre de 2026

Los cambios están preparados en la carpeta local. No se accedió al servidor por SSH, se enviaron correos, se registraron cuentas ni se modificó producción. El informe de análisis y su JSON describen el estado anterior a esta entrega y se conservan localmente.

## Cambios implementados

- Se retiró la clave fija de sesión. La aplicación exige `SECRET_KEY` de entorno de al menos 32 caracteres, sin valor predeterminado. Cookies `HttpOnly`, `SameSite=Lax`, `Secure` en producción y sesiones limitadas a ocho horas.
- Las sesiones se invalidan al cambiar la contraseña. La cookie guarda una comprobación HMAC de la credencial; no contiene su contraseña ni el hash almacenado en BD. Las cuentas inactivas dejan de cargarse.
- Administración completa ahora el mismo segundo factor que empresas y candidatos. Los códigos usan `secrets`, y verificación, vigencia, estado activo y consumo se resuelven con una sola operación SQL. Desafíos ausentes y fallos de envío se manejan sin autenticar al usuario.
- Se protegieron todas las solicitudes de modificación con un token CSRF vinculado a la sesión, incluidos formularios anónimos, uploads y acciones de notificaciones. El cierre de sesión requiere POST.
- Edición, eliminación y decisión de postulaciones comprueban propietario. Se aplican consultas por usuario y bloqueo de las filas involucradas antes de modificar; una solicitud a un recurso ajeno responde 404 y no escribe ni notifica.
- Notificaciones y requisitos se construyen con nodos de texto. Los nombres de candidatos ya no se interpolan dentro de código JavaScript. Se restringen los destinos de notificaciones al mismo origen.
- El registro antiguo de empresas redirige con 307 al registro principal, conservando los datos y sus validaciones. Se mantiene la protección CSRF en ambas rutas.
- Se preservan idiomas y certificaciones al guardar un perfil cuyo formulario no envía esos campos.
- Todas las rutas usan el mismo proveedor de conexiones, con pool por worker, sin conexiones adicionales ilimitadas. Se devuelven al terminar cada solicitud y se descartarán si falla su recuperación. Se corrigieron además cierres explícitos en las operaciones afectadas.
- Recuperación de contraseña usa el dominio configurado, sin confiar en el encabezado Host. Los enlaces firmados con ItsDangerous caducan en una hora y están ligados a la contraseña actual mediante HMAC; no contienen la contraseña ni su hash. El cambio compara el hash anterior en el UPDATE para evitar reutilización concurrente y anula códigos 2FA pendientes. No necesita las columnas `reset_token` ni `reset_expires`, ausentes en la instalación que reportó el error. Registro y recuperación comparten la política de contraseña. Los errores técnicos revisados dejan de enviarse al usuario.
- Los scripts administrativos ya no incluyen contraseñas predeterminadas ni se ejecutan al importarlos. Crear administrador es idempotente y no elimina usuarios. La contraseña se pide sin mostrarla o se recibe mediante entorno para uso controlado.
- Compose deja de publicar el puerto 5000; Nginx sigue siendo la entrada pública. Se prepararon límites por IP para `/auth/`, respuesta 429 y un healthcheck de BD que usa las variables correctas. Se agregó `.dockerignore` para excluir secretos, documentos de usuarios y dependencias locales del contexto de construcción.

No se cambió el proveedor Gmail ni su contraseña de aplicación. Se conserva «Talent Link» en los correos de código inicial y reenvío.

## Configuración necesaria

Antes de iniciar esta versión normalmente, agrega estas variables a tu configuración privada. No copies una clave de ejemplo:

```dotenv
SECRET_KEY=<clave aleatoria propia de al menos 32 caracteres>
FLASK_ENV=production
PUBLIC_BASE_URL=https://talentlink.duckdns.org
TRUST_PROXY=1
DB_POOL_MAX=10
```

Para generar una clave, en una terminal de confianza:

```shell
python -c "import secrets; print(secrets.token_hex(32))"
```

Guárdala únicamente en el entorno privado correspondiente. No la pegues en Git ni en el chat. Debe ser estable entre reinicios y compartida por los workers. Al desplegar con una clave nueva, las sesiones anteriores dejan de ser válidas y los usuarios vuelven a entrar con su correo, contraseña y código 2FA. La rotación de esta clave no modifica cuentas, contraseñas ni registros de la base de datos.

### Rotación directa elegida

Se utilizará únicamente la clave nueva, sin aceptar firmas de la clave expuesta. Se retiró la compatibilidad temporal de sesiones antiguas. Los usuarios con sesión abierta tendrán que autenticarse otra vez; las cuentas, empresas, candidatos, vacantes, postulaciones y archivos se conservan. El administrador también utiliza 2FA para iniciar sesión.

Este cambio no requiere borrar ni reinicializar la BD o los volúmenes. Se debe mantener el respaldo previsto para cualquier despliegue y conservar los volúmenes existentes.

En ejecución directa local por HTTP utiliza `FLASK_ENV=development`, `TRUST_PROXY=0` y una clave local distinta. Las variables se deben establecer en el entorno: `python main.py` no carga automáticamente `.env`. Compose sí utiliza `.env` para interpolar su configuración. El servidor directo escucha solo en `127.0.0.1:5001`; debug requiere además `FLASK_DEBUG=1` y entorno de desarrollo.

`TRUST_PROXY=1` corresponde al único Nginx controlado de este Compose. Si cambia la cadena de proxies se debe revisar esa confianza. En producción, `TRUSTED_HOSTS` se deriva del dominio de `PUBLIC_BASE_URL`.

`DB_POOL_MAX` es por proceso. Con cuatro workers y valor 10, los pools pueden utilizar hasta 40 conexiones en total. Ajustarlo según el límite real de PostgreSQL y otros consumidores.

## Preparación para un despliegue posterior

La secuencia de comandos está en [ACTUALIZAR_SERVIDOR.md](ACTUALIZAR_SERVIDOR.md).

Esta sección documenta pasos futuros; no se ejecutaron contra el servidor.

1. Verificar que el código e imagen en ejecución corresponden a la revisión esperada, respaldar la BD y uploads y comprobar una restauración en una copia separada.
2. Configurar una clave nueva y el dominio público. Avisar a los usuarios de que tendrán que iniciar sesión otra vez tras la actualización. Confirmar que el correo del administrador recibe mensajes antes de activar esta versión: también necesitará código para entrar.
3. Rotar las contraseñas administrativas y de BD que estuvieron escritas en el repositorio, si siguen en uso. Retirarlas de los archivos actuales no las borra del historial. Actualizar también la configuración privada correspondiente. En una BD ya creada, cambiar únicamente `POSTGRES_PASSWORD` en Compose no cambia la contraseña del rol existente.
4. Revisar configuración e imagen en un entorno de prueba y comprobar Nginx con los certificados y la red apropiados. No publicar la salida completa de `docker compose config`, porque incluye secretos; usar `docker compose config --quiet` para validar.
5. Recrear los servicios al desplegar para aplicar variables y puertos; un simple reinicio no aplica todas estas modificaciones. Verificar HTTPS, acceso por los tres roles con 2FA, CSRF, uploads y operaciones permitidas y rechazadas entre dos empresas.
6. Confirmar que 5000 ya no está publicado y conservar una forma documentada de volver a la imagen y configuración anteriores. Las sesiones anteriores quedan invalidadas; los usuarios recargan la página e inician sesión otra vez. Sus cuentas y registros se conservan.

Esta entrega no introduce tablas ni columnas. Se apoya en las de autenticación que ya utiliza el código desplegado; la reproducción completa y las migraciones del esquema siguen siendo una entrega separada.

## Comprobaciones locales

Con las dependencias de desarrollo instaladas en un entorno aislado:

```shell
python -m pip install -r requirements-dev.txt
python -m pytest
node --test tests/security_ui.test.js tests/vacancy_share.test.js
```

También se puede lanzar Python desde la raíz con `python -B docs/auditoria_local.py`. Los fixtures fuerzan valores ficticios de entorno y bloquean red y SMTP durante las pruebas. Las operaciones administrativas se prueban con mocks; no crean cuentas reales.

Resultado de esta revisión: **134 pruebas Python y 6 pruebas JavaScript aprobadas**, sin saltos. Incluyen sesiones con otra firma, revocación tras cambio de contraseña, CSRF ausente/incorrecto/de otra sesión, autorización positiva y negativa, 2FA, recuperación, recursos de BD, plantillas y salida HTML segura. Las regresiones de recuperación cubren correo → enlace → formulario → contraseña, para empresa y candidato, en otra sesión del navegador; firma alterada, caducidad, uso previo, cuenta inactiva, carrera entre cambios, contraseña inválida y fallos de BD/SMTP.

La ejecución principal utilizó Python 3.12, Flask 3.1.3, Flask-Login 0.6.3, Jinja2 3.1.6, Werkzeug 3.1.6 y pytest 9.0.2 disponibles localmente. `requirements.txt` fija Werkzeug 3.1.8: no se instaló ni construyó una imagen desde cero en esta máquina. Los mocks no sustituyen una prueba de SQL, concurrencia, restricciones o rendimiento con PostgreSQL real. Docker, Nginx y PostgreSQL no están disponibles como ejecutables locales; queda pendiente validar la imagen y el despliegue en un entorno separado. No se usó producción como entorno de prueba.

## Trabajo que sigue pendiente

- Rotación efectiva de credenciales y revisión del acceso al historial y a los documentos personales rastreados por Git. No se borraron CV, fotografías ni historial para evitar pérdida de datos.
- Migraciones completas, respaldo y restauración de BD y uploads con evidencia de ejecución.
- Validación real de los límites por IP de Nginx. El límite actual de autenticación es 10 solicitudes por minuto, con ráfaga de 5, e incluye GET de `/auth/`. Debe ajustarse a la carga y a usuarios que compartan una IP de salida de la universidad. No constituye un límite por cuenta ni frena por sí solo ataques distribuidos.
- Retirar gradualmente los scripts inline y habilitar una CSP con nonces. La entrega corrige los puntos de inyección identificados, pero conserva `unsafe-inline` por la estructura actual de las plantillas.
- Contenedor con usuario sin privilegios, después de preparar y comprobar permisos de los volúmenes. La imagen actual conserva su usuario y permisos existentes.
- Validación profunda de documentos subidos, dependencias/CVE, registros de auditoría y reglas completas de vencimiento/duplicados/colocación. Los controles por firma binaria existentes no equivalen a un análisis antivirus.

## Referencias

- [Seguridad de Flask](https://flask.palletsprojects.com/en/stable/web-security/).
- [Confianza del proxy en Flask](https://flask.palletsprojects.com/en/stable/deploying/proxy_fix/).
- [Límites de solicitudes en Nginx](https://nginx.org/en/docs/http/ngx_http_limit_req_module.html).
- [UPDATE y RETURNING en PostgreSQL 15](https://www.postgresql.org/docs/15/sql-update.html).
