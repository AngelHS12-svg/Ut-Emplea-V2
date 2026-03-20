import re

def strip_tags(text):
    """Elimina etiquetas HTML para prevenir ataques XSS."""
    if not text: return ""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)
