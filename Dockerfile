# Étape 1 : Utiliser une image Python de base
FROM python:3.9-slim

# Installer les dépendances pour wkhtmltopdf
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    libfontconfig \
    && rm -rf /var/lib/apt/lists/*

# Étape 2 : Définir le répertoire de travail
WORKDIR /app

# Étape 3 : Copier le fichier requirements.txt dans le conteneur
COPY requirements.txt .

# Étape 4 : Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Étape 5 : Copier tout le projet dans le conteneur
COPY . .

# Étape 6 : Exposer le port utilisé par Django (8000)
EXPOSE 8000

# Étape 7 : Commande par défaut pour démarrer le serveur Django
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "TradeFlow.wsgi:application"]
