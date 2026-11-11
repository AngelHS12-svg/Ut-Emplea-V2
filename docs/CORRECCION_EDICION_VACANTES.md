# Datos que no aparecían después de editar una vacante

Se corrigieron tres defectos:

- El formulario de edición enviaba dos campos `salario`. Flask leía el primero,
  por lo que editar el segundo podía no tener efecto.
- No había un campo de modalidad aunque el servidor la actualizaba. Al guardar,
  podía sustituirse el valor anterior por NULL.
- Solo se ejecutaba UPDATE sobre requisitos: si una vacante antigua no tenía
  esa fila, no se guardaban sus requisitos, pero se mostraba éxito.

Ahora hay un salario y una modalidad en el formulario de edición. Publicar
vacantes también incluye la modalidad, separada de la ubicación. Los salarios
son importes mensuales opcionales en MXN y se validan sin descartar entradas
inválidas silenciosamente. Un salario cero se visualiza como cero; un dato
pendiente se muestra sin el signo de moneda.

Editar mantiene el ID de la vacante, su empresa y sus postulaciones. Los
requisitos faltantes se insertan al editar, dentro de la misma transacción y
bajo el bloqueo de la vacante cuya propiedad ya fue comprobada. Guardar por
segunda vez actualiza la fila en vez de duplicarla. Un formulario anterior que
no envíe modalidad conserva la existente. Los valores personalizados de
modalidad siguen disponibles al abrir la edición.

La confirmación de éxito solo aparece después del commit. Si el guardado falla,
se revierte toda la operación y el formulario mantiene los datos introducidos.

No requiere migraciones ni modificaciones masivas a las vacantes existentes.
Se publica reconstruyendo el servicio web mediante el procedimiento habitual;
se conserva el volumen de PostgreSQL y el archivo .env.

Las pruebas locales verifican guardar y volver a leer los datos desde el
formulario, el detalle empresarial y la URL pública, tanto con requisitos
anteriores como sin ellos. También cubren intentos de otra empresa, rollback
por fallo SQL, salario inválido, cero y campos duplicados. El recorrido se
comprobó adicionalmente con PostgreSQL temporal y navegador local usando
datos ficticios; no se modificaron vacantes en producción.
