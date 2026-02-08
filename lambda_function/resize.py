from PIL import Image
import io
import boto3
import os

# Client S3
s3_client = boto3.client(
    's3',
    endpoint_url=os.getenv('LOCALSTACK_ENDPOINT', 'http://localhost:4566'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'test'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'test'),
    region_name=os.getenv('AWS_REGION', 'us-east-1')
)

BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'cloud-photo-bucket')
THUMBNAIL_SIZE = (300, 300)


def resize_image(filename):
    """
    Redimensionne une image en miniature 300x300 pixels.

    Télécharge l'image depuis S3, la redimensionne en conservant
    les proportions, puis upload la miniature dans S3.

    Args:
        filename (str): Nom du fichier image à redimensionner

    Returns:
        str: URL de la miniature créée, ou None en cas d'erreur

    Example:
        >>> resize_image('photo.jpg')
        'http://localhost:4566/cloud-photo-bucket/photo_thumb.jpg'
    """
    try:
        # Télécharger l'image
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=filename)
        image_data = response['Body'].read()

        # Ouvrir l'image
        image = Image.open(io.BytesIO(image_data))

        # Redimensionner
        image.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)

        # Convertir en bytes
        output = io.BytesIO()
        image_format = image.format if image.format else 'JPEG'
        image.save(output, format=image_format)
        output.seek(0)

        # Nom de la miniature
        name, ext = os.path.splitext(filename)
        thumbnail_filename = f"{name}_thumb{ext}"

        # Uploader la miniature
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=thumbnail_filename,
            Body=output.getvalue(),
            ContentType=f'image/{image_format.lower()}'
        )

        # URL de la miniature
        thumbnail_url = (
            f"http://localhost:4566/{BUCKET_NAME}/"
            f"{thumbnail_filename}"
            )

        print(f"Miniature créée : {thumbnail_filename}")
        return thumbnail_url

    except Exception as e:
        print(f"Erreur lors du redimensionnement : {str(e)}")
        return None


if __name__ == "__main__":
    """Point d'entrée pour tester la fonction directement."""
    result = resize_image("test.jpg")
    print(f"Résultat : {result}")
