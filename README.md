# S3tna - Cloud Photo Manager

## Présentation du projet
Ce projet est un mini service cloud de gestion d’images, développé sans cloud public, mais en s’appuyant sur LocalStack pour simuler des services AWS localement.

Il permet de :      
- téléverser des images via une interface web,
- stocker les images dans un stockage objet S3 simulé,
- sauvegarder les métadonnées en base de données,
- générer automatiquement des miniatures via une fonction Lambda,
- surveiller l’activité avec Prometheus & Grafana.

## Installation

### Prérequis
- Docker & Docker Compose
- Python 3.x
- AWS CLI

### Démarrage

1. Lancer LocalStack
```bash
docker compose up -d
```

2. Créer le bucket S3
```bash
aws --endpoint-url=http://localhost:4566 s3 mb s3://cloud-photo-bucket
```

3. Installer les dépendances Python
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. Lancer l'API
```bash
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints

- `POST /upload` : Upload une image
- `GET /images` : Liste toutes les images