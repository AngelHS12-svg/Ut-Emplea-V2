import re

def strip_tags(text):
    """Elimina etiquetas HTML para prevenir ataques XSS."""
    if not text: return ""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def detectar_script(text):
    """Detecta patrones de inyección de scripts maliciosos. Retorna True si se encuentra uno."""
    if not text:
        return False
    patrones = [
        r'<\s*script',
        r'javascript\s*:',
        r'on(error|load|click|mouseover|focus|blur|submit|change)\s*=',
        r'eval\s*\(',
        r'document\.(cookie|write|location)',
        r'<\s*iframe',
        r'<\s*object',
        r'<\s*embed',
        r'<\s*svg.*?on',
    ]
    texto_lower = text.lower()
    for patron in patrones:
        if re.search(patron, texto_lower):
            return True
    return False

def detectar_sqli(text):
    """Detecta patrones de inyección SQL comunes. Retorna True si se encuentra uno."""
    if not text:
        return False
    # Patrones SQL sospechosos
    patrones = [
        r'--\s',
        r'/\*',
        r'union\s+select',
        r'insert\s+into',
        r'delete\s+from',
        r'drop\s+table',
        r'update\s+\w+\s+set',
        r'or\s+1=1',
        r'or\s+\'1\'=\'1\'',
        r'waitfor\s+delay',
        r'pg_sleep\s*\('
    ]
    texto_lower = text.lower()
    for patron in patrones:
        if re.search(patron, texto_lower):
            return True
    return False

def validar_archivo(file, allowed_extensions, max_size_mb=5):
    """
    Valida un archivo por extensión, tamaño y firma (magic numbers).
    Retorna (True, None) si es válido, o (False, mensaje) si no.
    """
    if not file:
        return False, "No se recibió ningún archivo."
    
    # 1. Validar Extensión
    filename = file.filename
    if '.' not in filename:
        return False, "El archivo no tiene extensión válida."
    
    ext = filename.rsplit('.', 1)[1].lower()
    if ext not in allowed_extensions:
        return False, f"Extensión .{ext} no permitida. Permitidas: {', '.join(allowed_extensions)}"
    
    # 2. Validar Tamaño
    file.seek(0, 2) # Ir al final
    size = file.tell()
    file.seek(0) # Regresar al inicio
    
    if size > max_size_mb * 1024 * 1024:
        return False, f"El archivo excede el límite de {max_size_mb}MB."
    
    # 3. Validar Firma (Magic Numbers)
    header = file.read(16)
    file.seek(0) # Resetear para que pueda ser guardado después
    
    if ext == 'pdf':
        if not header.startswith(b'%PDF'):
            return False, "El contenido del archivo no coincide con el formato PDF real."
    elif ext in ['jpg', 'jpeg']:
        if not header.startswith(b'\xff\xd8\xff'):
            return False, "El contenido del archivo no coincide con el formato JPG real."
    elif ext == 'png':
        if not header.startswith(b'\x89PNG'):
            return False, "El contenido del archivo no coincide con el formato PNG real."
    elif ext == 'docx':
        if not header.startswith(b'PK\x03\x04'):
            return False, "El contenido del archivo no coincide con el formato DOCX real."
    elif ext == 'doc':
        if not header.startswith(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'):
            return False, "El contenido del archivo no coincide con el formato DOC real."
            
    return True, None
