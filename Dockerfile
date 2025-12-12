# On utilise une version légère de Python
FROM python:3.10-slim

# On définit le dossier de travail dans le conteneur
WORKDIR /app

# On copie les fichiers de votre projet dans le conteneur
COPY . .

# On installe les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Google Cloud attend que l'on écoute sur le port 8080 par défaut
ENV PORT 8080

# Commande de démarrage (Serveur Gunicorn robuste)
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app