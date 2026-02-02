from PIL import Image
import io
import boto3
import os

# Configuration S3
s3_client = boto3.client(
    's3',
    endpoint_url='http://localhost:4566',
    aws_access_key_id='test',
    aws_secret_access_key='test',
    region_name='us-east-1'
)

BUCKET_NAME = 'cloud-photo-bucket'
THUMBNAIL_SIZE = (300, 300)

def resize_image(filename):
    """
    Redimensionne une image et sauvegarde la miniature dans S3
    Args:
        filename: Nom du fichier à redimensionner
    Returns:
        URL de la miniature ou None en cas d'erreur
    """
    try:
        # 1. Télécharger l'image originale depuis S3
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=filename)
        image_data = response['Body'].read()
        
        # 2. Ouvrir l'image avec Pillow
        image = Image.open(io.BytesIO(image_data))
        
        # 3. Redimensionner en gardant les proportions
        image.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
        
        # 4. Convertir en bytes
        output = io.BytesIO()
        # Sauvegarder dans le format original (ou JPEG par défaut)
        image_format = image.format if image.format else 'JPEG'
        image.save(output, format=image_format)
        output.seek(0)
        
        # 5. Générer le nom de la miniature
        name, ext = os.path.splitext(filename)
        thumbnail_filename = f"{name}_thumb{ext}"
        
        # 6. Uploader la miniature dans S3
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=thumbnail_filename,
            Body=output.getvalue(),
            ContentType=f'image/{image_format.lower()}'
        )
        
        # 7. Retourner l'URL de la miniature
        thumbnail_url = f"http://localhost:4566/{BUCKET_NAME}/{thumbnail_filename}"
        
        print(f"Miniature créée : {thumbnail_filename}")
        return thumbnail_url
        
    except Exception as e:
        print(f"Erreur lors du redimensionnement : {str(e)}")
        return None

# Pour tester la fonction directement
if __name__ == "__main__":
    # Test
    result = resize_image("test.jpg")
    print(f"Résultat : {result}")