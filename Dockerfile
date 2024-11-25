# Usa una imagen base de Python
FROM python:3.12-slim

# Instala dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev

# Establece el directorio de trabajo
WORKDIR /app

# Copia y instala las dependencias antes del código (para optimizar el cacheo)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Copia el código fuente
COPY . .



# Exponer el puerto en el que correrá la app (usualmente 8000 o configurado en gunicorn)
EXPOSE 8000

# Comando para correr gunicorn en producción
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "gestionAdministrativaCeprunsa.wsgi:application"]
