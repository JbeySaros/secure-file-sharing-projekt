# Multi-stage build pour optimiser la taille
FROM python:3.11-slim as builder

# Variables de build
ARG BUILD_DATE
ARG VCS_REF  
ARG BUILD_NUMBER

# Métadonnées
LABEL org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.build-number=$BUILD_NUMBER \
      org.label-schema.name="Secure File Sharing API" \
      org.label-schema.description="API de partage de fichiers sécurisée avec chiffrement AES-256" \
      org.label-schema.version="3.0"

# Installer les dépendances de build
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copier et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage final - Image de production
FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MASTER_PASSWORD=secure_master_2024 \
    API_PASSWORD=secure_api_2024 \
    FLASK_ENV=production

# Copier les packages Python installés
COPY --from=builder /root/.local /root/.local

# Mettre à jour PATH pour utiliser les packages installés
ENV PATH=/root/.local/bin:$PATH

# Répertoire de travail
WORKDIR /app

# Créer utilisateur non-root
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Copier le code source
COPY --chown=appuser:appgroup . .

# Créer les dossiers nécessaires
RUN mkdir -p data/encrypted && \
    chown -R appuser:appgroup /app

# Exposer le port
EXPOSE 5000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Utiliser l'utilisateur non-root
USER appuser

# Commande de démarrage
CMD ["python", "app.py"]
