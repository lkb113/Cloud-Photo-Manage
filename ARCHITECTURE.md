# Architecture du Projet
![Diagramme](screenshots/Diagramme%20d'architecture%20S3TNA.png)
## Vue d'ensemble
```
┌─────────────────────────────────────────────────────────────┐
│                        UTILISATEUR                           │
│                      (Navigateur Web)                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │      FRONTEND        │
              │   HTML/CSS/JS        │
              │   Port: 5500         │
              └──────────┬───────────┘
                         │
                         │ HTTP REST
                         ▼
              ┌──────────────────────┐
              │     API BACKEND      │
              │      FastAPI         │
              │     Port: 8000       │
              └─┬────────┬─────────┬─┘
                │        │         │
       ┌────────┘        │         └─────────┐
       │                 │                   │
       ▼                 ▼                   ▼
┌─────────────┐   ┌────────────┐    ┌──────────────┐
│  LocalStack │   │  SQLite    │    │   Lambda     │
│     S3      │   │  Database  │    │   Resize     │
│  Port: 4566 │   │ images.db  │    │  (Python)    │
└─────────────┘   └────────────┘    └──────────────┘
       │
       │ Stockage images
       │ + miniatures
       ▼
┌─────────────────┐
│  cloud-photo-   │
│     bucket      │
└─────────────────┘
```

## Monitoring
```
┌──────────────────────┐
│    API Backend       │
│   /metrics endpoint  │
└──────────┬───────────┘
           │
           │ Scraping (15s)
           ▼
    ┌─────────────┐
    │ Prometheus  │
    │  Port: 9090 │
    └──────┬──────┘
           │
           │ Queries
           ▼
    ┌─────────────┐
    │   Grafana   │
    │  Port: 3000 │
    └─────────────┘
```

## Flux de données

### Upload d'une image

1. Utilisateur sélectionne une image dans le frontend
2. Frontend envoie POST /upload à l'API
3. API upload l'image dans S3 (LocalStack)
4. API sauvegarde métadonnées en SQLite
5. API appelle Lambda pour redimensionner
6. Lambda crée miniature 300x300
7. Lambda upload miniature dans S3
8. API met à jour SQLite avec URL miniature
9. API enregistre métriques Prometheus
10. API retourne succès au frontend

### Visualisation des images

1. Frontend demande GET /images
2. API récupère données depuis SQLite
3. API retourne liste JSON
4. Frontend affiche miniatures
5. Clic sur miniature → ouvre originale

### Monitoring

1. Prometheus scrappe /metrics toutes les 15s
2. Prometheus stocke métriques
3. Grafana query Prometheus
4. Grafana affiche graphiques temps réel