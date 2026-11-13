# Arranque local de TalentLink

## Configuración privada

En la raíz de TalentLink, copia `.env.example` a `.env` y completa las credenciales de una base PostgreSQL **de desarrollo**, la cuenta de correo de prueba y una `SECRET_KEY` aleatoria de al menos 32 caracteres. `.env` está ignorado por Git. No uses la base de producción para probar publicaciones o registros.

Para HTTP local configura `FLASK_ENV=development`, `TRUST_PROXY=0` y `PUBLIC_BASE_URL=http://127.0.0.1:5001`. `python main.py` no lee `.env` por sí solo: exporta esas variables al proceso antes de ejecutarlo, o usa Docker como sigue.

## Docker en Windows

Desde la carpeta de TalentLink:

```powershell
docker build -f Dockerfile.local -t talentlink-local:dev .
docker run --rm --name talentlink-web-dev --env-file .env -p 127.0.0.1:5001:5000 talentlink-local:dev
```

Abre `http://127.0.0.1:5001/`. Si PostgreSQL está instalado en Windows, usa `DB_HOST=host.docker.internal` en `.env`. Si está en otro contenedor, conecta ambos a una misma red Docker y usa el nombre de ese contenedor como `DB_HOST`. La base debe tener el esquema actual; el volcado `database/bd_ut.sql` es anterior a algunas funciones y no reproduce por sí solo la instalación desplegada.

Para detener el servidor iniciado con `docker run`, presiona Ctrl+C. Reconstruye la imagen después de cambiar código. El inicio de sesión usa códigos por correo, así que requiere una cuenta SMTP válida en `MAIL_USERNAME` y `MAIL_PASSWORD`.

Para iniciar sesión y publicar vacantes se necesitan una base de desarrollo con el esquema actual y una cuenta SMTP válida. Para la función de rangos salariales, aplica también [su migración](SALARIO_RANGO.md) en la base de desarrollo antes de probar el formulario.
