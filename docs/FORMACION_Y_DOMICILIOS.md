# Formación académica y domicilios de México

El registro de candidatos solicita el programa TSU, la institución y su año de
egreso. Ingeniería o licenciatura constituye un segundo nivel opcional, con
programa, tipo de título y, si se conocen, institución y año propios.

Desde **Mi perfil → Editar perfil** se puede añadir ese segundo título después.
**Generar CV** lee los datos actuales y muestra los dos programas por separado.
Un PDF subido por el usuario es un archivo independiente: para cambiar su
contenido debe subir una versión nueva.

Los registros antiguos se leen usando los campos previos, sin suponer un TSU
cuando solo indicaban ingeniería/licenciatura u otro grado. Al editar, el
candidato revisa y completa su TSU. Otros grados antiguos (por ejemplo, maestría)
se conservan además de los dos niveles nuevos.

## Catálogo de domicilios

Ambos registros y ambos perfiles incluyen país (México), C.P., estado, municipio
o alcaldía, ciudad/localidad, colonia/asentamiento y calle/número. Al completar
cinco dígitos se consulta la API **local** `/api/catalogos/codigos-postales/<cp>`.
Si hay varias colonias se muestran todas y el usuario elige. Una ciudad postal
ausente se deja en blanco; no se confunde municipio con ciudad.

El catálogo SEPOMEX incluido funciona sin claves, sin pagos y sin conexión a un
proveedor externo. Procedencia, revisión y actualización en `app/data/README.md`.
Los catálogos de municipios y ciudades se filtran por estado/municipio. Los
campos de localidad y colonia permiten captura manual, incluyendo códigos
recientes que aún no aparezcan en la copia local.

## Actualización del servidor

**Esta versión requiere una migración antes de iniciar el nuevo contenedor web.**
No se debe restaurar `database/bd_ut.sql` ni recrear el volumen de PostgreSQL.
La migración solo añade cinco columnas opcionales a candidatos y una a
direcciones de empresas. No ejecuta actualizaciones ni borrados de registros.
Es transaccional, tiene un límite de espera de bloqueo de cinco segundos y
puede ejecutarse nuevamente.

Después del push, desde `~/mi-proyecto` por SSH:

```bash
git status --short

# Respaldo nuevo de la base actual; conserva también tus respaldos de archivos y .env.
umask 077
backup_dir="$HOME/respaldos-ut-emplea/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$backup_dir"
chmod 700 "$backup_dir"
docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom' > "$backup_dir/database.dump"
chmod 600 "$backup_dir/database.dump"
docker compose exec -T db pg_restore --list < "$backup_dir/database.dump" > /dev/null
tar -czf "$backup_dir/archivos.tar.gz" uploads public/uploads
cp .env "$backup_dir/env.anterior"
git rev-parse HEAD > "$backup_dir/revision-anterior.txt"
ls -lh "$backup_dir"

umask 022
git pull --ff-only origin main

docker compose config --quiet
docker compose build web
docker compose run --rm --no-deps web python maintenance/migrate_formacion_domicilio.py
docker compose run --rm --no-deps web python -c "from main import app; from app.utils.postal import postal_places; assert postal_places('75020'); print('Flask y catálogo postal correctos')"

find public/css public/js -type d -exec chmod 755 {} +
find public/css public/js -type f -exec chmod 644 {} +
docker compose up -d --no-deps --no-build web
docker compose exec nginx nginx -t
docker compose exec nginx nginx -s reload
docker compose ps
docker compose logs --tail=40 web
```

Ejecuta cada bloque solo si el anterior terminó correctamente. Si la migración
falla o agota la espera de bloqueo, conserva el contenedor actual, revisa el
mensaje y vuelve a ejecutar la migración cuando se libere el bloqueo.

Mantén el `.env` y su `SECRET_KEY` actual. Esta actualización no cambia las
credenciales ni invalida las sesiones existentes. PostgreSQL y sus volúmenes
continúan en uso; no se ejecuta `docker compose down -v`.

## Verificación local

Las pruebas de registro/edición/CV usan conexiones y correo simulados. El
catálogo postal sí se consulta realmente desde su SQLite incluido. La
migración se verificó adicionalmente dos veces sobre PostgreSQL 16 temporal
local, comprobando que permanecen los valores anteriores y se guarda JSONB.
La imagen de producción usa PostgreSQL 15; la migración utiliza sintaxis
compatible (columnas opcionales, `IF NOT EXISTS` y JSONB).
