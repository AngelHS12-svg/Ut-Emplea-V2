# Recuperar el acceso de una empresa cuando perdió su buzón

Usa este procedimiento para una empresa aprobada que ya tiene cuenta. Confirma
la solicitud por un canal corporativo conocido y verifica que la persona que la
hace esté autorizada para recibir el acceso. Es preferible un correo
institucional controlado por la empresa. No pidas contraseñas ni códigos.

La herramienta conserva el ID de usuario, la empresa y sus vacantes. Cambia
únicamente el correo de acceso y las credenciales de esa cuenta: invalida la
contraseña anterior, las sesiones, los códigos pendientes y los enlaces de
recuperación anteriores. La empresa elige su contraseña desde su nuevo buzón.
No se necesita reconstruir la imagen, reiniciar Docker ni ejecutar migraciones.

1. Sube a Git el archivo `maintenance/recuperar_acceso_empresa.py`. En el
   servidor, dentro de `~/mi-proyecto`, actualiza el repositorio con
   `git pull --ff-only origin main`.

2. Escribe los dos correos directamente en SSH y ejecuta la vista previa:

   ```bash
   read -r -p 'Correo de acceso anterior: ' correo_actual
   read -r -p 'Correo de acceso nuevo: ' correo_nuevo
   docker compose exec -T web python - --actual "$correo_actual" --nuevo "$correo_nuevo" < maintenance/recuperar_acceso_empresa.py
   ```

   La vista previa comprueba que existe la empresa aprobada y activa y que el
   nuevo correo está libre. Muestra el ID y el nombre sin guardar cambios.
   Comprueba que son los de la empresa que solicitó el cambio.

3. Si la vista previa coincide y la solicitud está autorizada, escribe el ID
   que mostró la herramienta y aplica el cambio:

   ```bash
   read -r -p 'ID de empresa confirmado: ' id_empresa
   docker compose exec -T web python - --actual "$correo_actual" --nuevo "$correo_nuevo" --empresa "$id_empresa" --aplicar < maintenance/recuperar_acceso_empresa.py
   unset correo_actual correo_nuevo id_empresa
   ```

   Si hay un error, revisa el resultado con la vista previa y en **Consultar
   empresas** antes de repetir la operación. Si el correo nuevo ya está en uso,
   solicita otro buzón autorizado; no elimines ni modifiques la otra cuenta.

4. La empresa abre **Olvidé mi contraseña** en TalentLink, solicita un enlace
   con el correo nuevo y crea su contraseña. Después elige **Empresa** al
   iniciar sesión. El código de verificación llegará a ese mismo buzón.
