# Actualizar la instalación existente mediante SSH

Estos pasos se ejecutan manualmente en el servidor de la universidad, dentro de la carpeta donde ya está funcionando este proyecto. No se ejecutaron desde Codex. La actualización cambia web y Nginx; conserva el contenedor de BD y los volúmenes existentes. Las sesiones anteriores dejarán de ser válidas y los usuarios entrarán de nuevo con sus cuentas y código 2FA.

## 1. Identificar la instalación y respaldar antes de actualizar

```bash
git status --short
git branch --show-current
docker compose ps
```

Confirma que es la instalación correcta y que la rama es `main`. Revisa y conserva cualquier cambio local del servidor antes de incorporar los cambios remotos. Detén el procedimiento si falla alguno de los pasos siguientes.

Ejecuta el respaldo usando el Compose que actualmente funciona, antes del `git pull`:

```bash
umask 077
backup_dir="$HOME/respaldos-ut-emplea/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$backup_dir"
docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom' > "$backup_dir/database.dump"
docker compose exec -T db pg_restore --list < "$backup_dir/database.dump" > /dev/null
tar -czf "$backup_dir/archivos.tar.gz" uploads public/uploads
cp .env "$backup_dir/env.anterior"
git rev-parse HEAD > "$backup_dir/revision-anterior.txt"
docker inspect --format '{{.Image}}' ut_emplea_web > "$backup_dir/imagen-web-anterior.txt"
```

El respaldo de configuración contiene secretos y debe conservarse en ese directorio privado. La comprobación con `pg_restore --list` valida que se puede leer el archivo; la restauración completa se debe ensayar en un entorno separado. Para consistencia exacta entre BD y archivos, planifica una ventana sin escrituras al tomar el respaldo.

## 2. Preparar la nueva clave de sesión

Con el contenedor web actual todavía en funcionamiento, genera una clave privada:

```bash
docker compose exec -T web python -c "import secrets; print(secrets.token_hex(32))"
```

Agrega su resultado al `.env` del servidor como `SECRET_KEY=...`. Mantén los valores actuales de BD y Gmail. Esta clave debe ser nueva y permanecer estable después del despliegue; guárdala solo en el entorno privado. El archivo `.env.example` muestra las variables adicionales y sus valores predeterminados.

La clave de sesión no modifica contraseñas ni registros de usuarios. El administrador también necesitará código por correo en su próximo inicio de sesión. La rotación de las contraseñas administrativas y de BD expuestas es una operación distinta, documentada en [SEGURIDAD.md](SEGURIDAD.md).

## 3. Descargar, validar y construir

```bash
git pull --ff-only origin main
docker compose config --quiet
docker compose build web
docker compose run --rm --no-deps nginx nginx -t
```

La comprobación de Nginx utiliza los certificados montados y la red de la instalación existente. Todos los pasos deben terminar correctamente antes de reemplazar servicios. El código, las pruebas y los archivos de configuración se revisaron en local; la imagen y estas comprobaciones requieren Docker y se validan en el entorno de despliegue o una copia separada.

## 4. Reemplazar únicamente los servicios de aplicación

```bash
docker compose up -d --no-deps --no-build web
docker compose up -d --no-deps --force-recreate nginx
docker compose ps
docker compose logs --tail=40 web nginx
```

Nginx se recrea para cargar la configuración y resolver la dirección del contenedor web actualizado. La sustitución puede producir una interrupción breve. El volumen `postgres_data`, los uploads y los registros de la BD se conservan. No se ejecutan scripts de limpieza ni inicialización de usuarios en este procedimiento.

Comprueba HTTPS y el acceso con tus cuentas existentes. Los formularios abiertos antes de la actualización requieren recarga. El puerto 5000 queda disponible solo dentro de la red de Compose. Conserva los respaldos, la revisión y la imagen anteriores para una recuperación si hiciera falta.
