import re


def password_error(password):
    if not isinstance(password, str) or len(password) < 12:
        return 'La contraseña debe tener al menos 12 caracteres.'
    if len(password) > 256:
        return 'La contraseña es demasiado larga.'
    if (not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password)
            or not re.search(r'\d', password) or not re.search(r'[^A-Za-z0-9]', password)):
        return 'La contraseña debe incluir mayúscula, minúscula, número y símbolo especial.'
    sequences = ('012', '123', '234', '345', '456', '567', '678', '789', '890',
                 '098', '987', '876', '765', '654', '543', '432', '321', '210', '109')
    if any(sequence in password for sequence in sequences):
        return 'La contraseña no debe tener números consecutivos (ej. 123 o 321).'
    return None
