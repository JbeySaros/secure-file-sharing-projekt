# secure-file-sharing-projekt [WIP]

## Présentation

**secure-file-sharing-projekt** est une application qui permet de partager des fichiers de manière sécurisée.  
L’objectif est de fournir un service simple pour les utilisateurs (upload et partage via un lien) tout en garantissant des mécanismes robustes côté technique : chiffrement, authentification et gestion fine des accès.  

---

## Architecture

- **Backend** : API REST en Python (FastAPI/Flask).  
- **Stockage** : fichiers chiffrés au repos.  
- **Authentification** : jetons sécurisés (JWT) ou sessions.  
- **Permissions** : gestion des droits, durée de validité, restrictions d’accès.  
- **Sécurité** : sandbox pour traitement des fichiers, validation stricte des entrées, journalisation centralisée.  

---

## Fonctionnement

 **Upload** : un utilisateur authentifié envoie un fichier via l’interface.  
 **Chiffrement** : le fichier est chiffré avant d’être stocké.  
 **Métadonnées** : enregistrement des informations (propriétaire, hash, droits d’accès, durée de validité).  
 **Partage** : l’utilisateur peut générer un lien sécurisé ou attribuer des permissions.  
 **Téléchargement** : le destinataire récupère le fichier, qui est déchiffré et vérifié.  

---

## Installation

```bash
git clone https://github.com/JbeySaros/secure-file-sharing-projekt.git
cd secure-file-sharing-projekt
pip install -r requirements.txt
```

**Déploiement**

Docker
```bash
docker build -t secure-file-sharing .
docker run -d -p 8000:8000 \
  -e SECRET_KEY="votre_cle_secrete" \
  -e STORAGE_PATH="/data/files" \
  secure-file-sharing
```
---

Variables d'environnement:
  - SECRET_KEY : clé de chiffrement.
  - STORAGE_PATH : chemin de stockage des fichiers.
  - TOKEN_EXPIRATION : durée de validité des jetons.
  - MAX_FILE_SIZE : limite de taille des fichiers.

---

## Test et Pipeline CI/CD Jenkins ##
Le projet est intégré dans un pipeline Jenkins pour automatiser la qualité et le déploiement.
Le pipeline type inclut :

  - **Checkout** : récupération du code source depuis GitHub.
  - **Build :** installation des dépendances.
  - **Tests :** exécution des tests unitaires et d’intégration (pytest).
  - **Analyse statique :** contrôle de style et sécurité (flake8, bandit).
  - **Build Docker :** construction de l’image du service.
  - **Push registry :** publication de l’image sur un registre Docker (DockerHub, ECR, GitHub Container Registry).
  - **Déploiement :** déploiement automatique sur un environnement cible (Kubernetes, VM, ou serveur).

## Licence ##

Ce projet est distribué sous licence MIT.
