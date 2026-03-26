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
