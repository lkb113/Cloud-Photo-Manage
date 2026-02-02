from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from backend.database import conn, cursor
import boto3
import sys
import os

# Import database
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lambda_function.resize import resize_image
from backend.database import add_image, get_images, update_thumbnail

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# S3
s3_client = boto3.client(
    's3',
    endpoint_url='http://localhost:4566',
    aws_access_key_id='test',
    aws_secret_access_key='test',
    region_name='us-east-1'
)

BUCKET_NAME = 'cloud-photo-bucket'

# POST /upload
@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    contents = await file.read()
    s3_client.put_object(Bucket=BUCKET_NAME, Key=file.filename, Body=contents)
    url = f"http://localhost:4566/{BUCKET_NAME}/{file.filename}"
    add_image(file.filename, url, len(contents))
    thumbnail_url = resize_image(file.filename)
    if thumbnail_url:
        update_thumbnail(file.filename, thumbnail_url)
    return {"message": "uploaded", "filename": file.filename, "thumbnail_url": thumbnail_url}

# GET /images
@app.get("/images")
def list_images():
    return [dict(img) for img in get_images()]

# DELETE /images/{filename} - Supprimer une image
@app.delete("/images/{filename}")
def delete_image(filename: str):
    try:
        # Supprimer de S3
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=filename)
        
        # Supprimer de la BDD
        cursor.execute('DELETE FROM images WHERE filename = ?', (filename,))
        conn.commit()
        
        return {"message": "Image deleted", "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")
