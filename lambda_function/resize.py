from PIL import Image
import io
import boto3
import os

# Client S3
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
    result = resize_image("test.jpg")
    print(f"Résultat : {result}")
