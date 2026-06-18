# Usar una imagen base ligera de Python
FROM python:3.11-slim

# Evitar que Python escriba archivos .pyc y habilitar modo sin búfer para logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para psycopg2 y compilación
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de dependencias e instalarlas
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código del proyecto
COPY . /app/

# Crear la carpeta de subidas si no existe y dar permisos
RUN mkdir -p /app/uploads && chmod 777 /app/uploads

# Exponer el puerto del servidor Flask
EXPOSE 5000

# Comando para ejecutar la aplicación con Gunicorn en producción
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "main:app"]
