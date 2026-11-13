# Salario fijo, rango o no especificado

Las empresas pueden publicar y editar una vacante con una cantidad fija, un rango aproximado mensual en MXN o sin importe. Las vacantes existentes conservan su salario; un valor nulo sigue apareciendo como «No especificado». La columna `salario` almacena el importe fijo o el límite inferior. La nueva columna `salario_max` almacena únicamente el límite superior de un rango.

## Actualización del servidor

Antes de iniciar el código nuevo, respalda la base de datos y los archivos siguiendo [ACTUALIZAR_SERVIDOR.md](ACTUALIZAR_SERVIDOR.md). Después de descargar el código y antes de sustituir `web`, ejecuta una vez (se puede repetir sin duplicar cambios):

```bash
docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < database/migrations/20261113_salario_rango.sql
```

La migración agrega una columna opcional y una restricción para impedir rangos incompletos o invertidos. No reescribe las vacantes existentes. Si la migración falla, conserva el contenedor web anterior y revisa el error antes de continuar.

La aplicación sigue necesitando las variables privadas del servidor (`SECRET_KEY`, base de datos y correo). No copies esos valores al repositorio.
