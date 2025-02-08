FROM python:3.9

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ejecuta Gunicorn con 4 workers
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
