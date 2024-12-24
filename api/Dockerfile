FROM python:3.10

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de requirements et installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --verbose

# Installer le modèle spaCy
RUN python -m spacy download en_core_web_sm

# Copier le code source uniquement, les models sont téléchargés à l'exécution
COPY app/ app/

# Variables d'environnement
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production
ENV DB_PORT=35836
ENV DB_USER=mailsmart
ENV DB_NAME=mailsmart


# Exposer le port
EXPOSE 80
# Lancer l'application avec uvicorn intégré à FastAPI
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]