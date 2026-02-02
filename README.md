# S3tna - Cloud Photo Manager

Ce projet est un mini service cloud de gestion d’images, développé sans cloud public, mais en s’appuyant sur LocalStack pour simuler des services AWS localement.

## Description
Ce projet simule une architecture cloud moderne pour stocker et gérer des images :
- **Stockage S3** (LocalStack) pour les fichiers
- **API REST** (FastAPI) pour la gestion
- **Base de données SQLite** pour les métadonnées
- **Interface web** responsive avec mode sombre Installation

## Fonctionnalités
- Upload d'images via interface web
- Galerie d'images responsive
- Suppression d'images
- Mode sombre/clair avec sauvegarde de préférence
- Affichage des métadonnées (date, taille)
- API REST complète

## Installation

### Prérequis
- Docker & Docker Compose
- Python 3.x
- AWS CLI

1. **Cloner le projet**
```bash
git clone git@rendu-git.etna-alternance.net:module-10141/activity-54892/group-1070826.git
cd group-1070826
```

2. Lancer LocalStack
```bash
docker compose up -d
```

3. Créer le bucket S3
```bash
aws --endpoint-url=http://localhost:4566 s3 mb s3://cloud-photo-bucket
```

4. Installer les dépendances Python
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

5. Lancer l'API
```bash
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

6. **Lancer le serveur Frontend**
```bash
cd frontend
python3 -m http.server 5500
```

7. **Accéder à l'application**
   - Frontend : http://localhost:5500
   - API Documentation : http://localhost:8000/docs

## Endpoints

- `POST /upload` : Upload une image
- `GET /images` : Liste toutes les images
- `DELETE /images/{filename}` : Supprime une image

## Auteur

Projet réalisé dans le cadre de la formation ETNA.