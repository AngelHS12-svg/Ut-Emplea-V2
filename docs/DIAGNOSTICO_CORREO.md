# Diagnóstico de correo de TalentLink

Los códigos de verificación y los enlaces de recuperación usan el mismo
servidor SMTP. La aplicación reintenta una vez los fallos temporales de DNS,
conexión y los rechazos SMTP de clase 4xx. Una desconexión durante la entrega
puede ocurrir después de que el proveedor recibió el mensaje, por lo que ese
caso no se reintenta automáticamente.

Los logs de envío del servicio `web` muestran el tipo de correo, la fase y, si
está disponible, el código de error. No incluyen el correo del destinatario,
códigos de verificación ni enlaces de recuperación. «Correo enviado» indica
aceptación por SMTP; no garantiza que el mensaje aparezca en la bandeja de
entrada.

Desde `~/mi-proyecto`, consulta los eventos recientes:

```bash
docker compose logs --timestamps --since=2h web 2>&1 \
  | grep -E 'Correo enviado:|tipo=.*fase=.*intento=|SMTP aceptó el correo|No se pudo enviar un correo de recuperación' \
  | tail -30
```

Si vuelve a fallar, compara la resolución en el servidor y en el contenedor.
Estos comandos no solicitan códigos, no inician sesión en SMTP y no envían correo:

```bash
getent ahosts smtp.gmail.com
docker compose exec -T web getent ahosts smtp.gmail.com
docker compose exec -T web python -c 'import socket; socket.create_connection(("smtp.gmail.com", 465), timeout=5).close(); print("Puerto SMTP accesible desde web")'
```

- Si falla DNS en ambos entornos, revisa el resolvedor y la conexión del servidor.
- Si el servidor resuelve y el contenedor no, revisa el DNS de la red de Docker.
- Si el contenedor resuelve pero no conecta, revisa la salida al puerto 465 y
  las rutas o el firewall con quien administra la red.
- Si el proveedor devuelve 535, revisa la configuración SMTP de forma privada.

El reintento ayuda cuando el corte dura poco. Si DNS o la ruta siguen caídos,
se necesita corregir la red del servidor o del contenedor.
