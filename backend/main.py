from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from backend.database import conn, cursor, add_image, get_images, update_thumbnail
import boto3
import sys
import os
from prometheus_client import Counter, generate_latest, Histogram, Gauge, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import time

# Import database
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Import de la fonction de redimensionnement
from lambda_function.resize import resize_image
from backend.database import add_image, get_images, update_thumbnail


# Métriques Prometheus
images_uploaded = Counter('images_uploaded_total', 'Nombre total d\'images uploadées')
thumbnails_created = Counter('thumbnails_created_total', 'Nombre total de miniatures créées')
images_deleted = Counter('images_deleted_total', 'Nombre total d\'images supprimées')
upload_size_bytes = Histogram('upload_size_bytes', 'Taille des images uploadées en bytes', buckets=[1024, 10240, 102400, 1048576, 10485760])
api_latency = Histogram('api_request_duration_seconds', 'Latence des requêtes API en secondes', buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0])
total_images = Gauge('total_images_stored', 'Nombre total d\'images stockées dans la base de données') 

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint métriques
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Client S3
s3_client = boto3.client(
    's3',
    endpoint_url='http://localhost:4566',
    aws_access_key_id='test',
    aws_secret_access_key='test',
    region_name='us-east-1'
)

# Nom du bucket
BUCKET_NAME = 'cloud-photo-bucket'

# Upload image
@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    start_time = time.time()
    try:
        # Lecture du fichier
        contents = await file.read()
        file_size = len(contents)
        # Upload vers S3
        s3_client.put_object(Bucket=BUCKET_NAME, Key=file.filename, Body=contents)
        # Ajouter à la BDD
        url = f"http://localhost:4566/{BUCKET_NAME}/{file.filename}"
        add_image(file.filename, url, len(contents))
        # Création de la miniature
        thumbnail_url = resize_image(file.filename)

        # Mettre à jour la BDD et les métriques
        if thumbnail_url:
            update_thumbnail(file.filename, thumbnail_url)
            thumbnails_created.inc()
            images_uploaded.inc()
            upload_size_bytes.observe(file_size)
            total_images.set(len(get_images()))
            duration = time.time() - start_time
            api_latency.observe(duration)

        return {"message": "uploaded", "filename": file.filename, "thumbnail_url": thumbnail_url}
    
    except Exception as e:
        duration = time.time() - start_time
        api_latency.observe(duration)
        raise e

# Liste images
@app.get("/images")
def list_images():
    start_time = time.time()
    try:
        result = [dict(img) for img in get_images()]
        total_images.set(len(result))
        duration = time.time() - start_time
        api_latency.observe(duration)
        return result
    except Exception as e:
        duration = time.time() - start_time
        api_latency.observe(duration)
        raise e

# Supprimer une image
@app.delete("/images/{filename}")
def delete_image(filename: str):
    start_time = time.time()
    try:
        # Supprimer de S3
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=filename)
        
        # Suppprimer la miniature
        name, ext = os.path.splitext(filename)
        thumbnail_filename = f"{name}_thumbnail{ext}"
        try: 
            s3_client.delete_object(Bucket=BUCKET_NAME, Key=thumbnail_filename)
        except:
            pass

        # Supprimer de la BDD
        cursor.execute('DELETE FROM images WHERE filename = ?', (filename,))
        conn.commit()

        # Mettre à jour les métriques
        images_deleted.inc()
        total_images.set(len(get_images()))
        duration = time.time() - start_time
        api_latency.observe(duration)
        return {"message": "Image deleted", "filename": filename}
    except Exception as e:
        duration = time.time() - start_time
        api_latency.observe(duration)
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")
