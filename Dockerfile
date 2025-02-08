# Imagen base con Python 3.9
FROM python:3.9

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos de requerimientos
COPY requirements.txt requirements.txt

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todos los archivos al contenedor
COPY . .

# Exponer el puerto 8080
EXPOSE 8080

# Ejecutar la aplicación con Gunicorn en producción
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
