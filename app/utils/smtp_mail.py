"""Envío SMTP a un destinatario con un reintento de fallos transitorios."""

import errno
import smtplib
import socket
from time import sleep


SMTP_TIMEOUT = 8
RETRY_DELAY = 1
TRANSIENT_ERRNOS = {
    errno.ENETUNREACH, errno.ENETDOWN, errno.EHOSTUNREACH, errno.ECONNREFUSED,
    errno.ECONNRESET, errno.ECONNABORTED, errno.ETIMEDOUT, errno.EPIPE,
}


def _can_retry(error, sending):
    # Un rechazo explícito no implica que el proveedor haya aceptado el mensaje.
    if isinstance(error, smtplib.SMTPRecipientsRefused):
        return bool(error.recipients) and all(400 <= reply[0] < 500 for reply in error.recipients.values())
    if isinstance(error, smtplib.SMTPResponseException):
        return 400 <= error.smtp_code < 500
    if sending:
        # Si se perdió la conexión al entregar, no sabemos si SMTP lo recibió.
        return False
    if isinstance(error, socket.gaierror):
        return error.errno == socket.EAI_AGAIN
    return (isinstance(error, (TimeoutError, smtplib.SMTPServerDisconnected))
            or getattr(error, "errno", None) in TRANSIENT_ERRNOS)


def send_smtp_message(config, recipient, message, *, category, logger):
    sender = config["MAIL_USERNAME"]
    for attempt in (1, 2):
        stage = "conexión"
        accepted = False
        try:
            with smtplib.SMTP_SSL(config["MAIL_SERVER"], config["MAIL_PORT"], timeout=SMTP_TIMEOUT) as server:
                stage = "autenticación"
                server.login(sender, config["MAIL_PASSWORD"])
                stage = "entrega"
                server.sendmail(sender, recipient, message)
                accepted = True
            return True
        except (OSError, smtplib.SMTPException) as error:
            if accepted:
                logger.warning("SMTP aceptó el correo de %s; falló el cierre de conexión (%s)",
                               category, type(error).__name__)
                return True

            retry = attempt == 1 and _can_retry(error, stage == "entrega")
            report = logger.warning if retry else logger.error
            report(
                "Error al enviar correo | tipo=%s fase=%s intento=%d/2 causa=%s errno=%s smtp=%s reintento=%s",
                category, stage, attempt, type(error).__name__,
                getattr(error, "errno", None), getattr(error, "smtp_code", None), "sí" if retry else "no",
            )
            if not retry:
                return False
            sleep(RETRY_DELAY)
