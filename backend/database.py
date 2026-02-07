"""
Module de gestion de la base de données SQLite.

Ce module gère les métadonnées des images uploadées :
création de table, ajout, récupération et mise à jour.
"""

import sqlite3
from datetime import datetime

# Connexion à la base de données
conn = sqlite3.connect('images.db', check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Créer la table images
cursor.execute('''
CREATE TABLE IF NOT EXISTS images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT UNIQUE NOT NULL,
    original_url TEXT NOT NULL,
    thumbnail_url TEXT,
    upload_date TEXT NOT NULL,
    size INTEGER NOT NULL
)
''')
conn.commit()


def add_image(filename, url, size):
    """
    Ajoute une nouvelle image dans la base de données.

    Args:
        filename (str): Nom du fichier image
        url (str): URL de l'image dans S3
        size (int): Taille du fichier en bytes

    Returns:
        int: ID de l'image insérée
    """
    cursor.execute('''
    INSERT INTO images (filename, original_url, upload_date, size)
    VALUES (?, ?, ?, ?)
    ''', (filename, url, datetime.utcnow().isoformat(), size))
    conn.commit()


def get_images():
    """
    Récupère toutes les images de la base de données.

    Returns:
        list: Liste des images (Row objects) triées par date décroissante
    """
    cursor.execute('SELECT * FROM images')
    return cursor.fetchall()


def update_thumbnail(filename, thumbnail_url):
    """
    Met à jour l'URL de la miniature pour une image.

    Args:
        filename (str): Nom du fichier image
        thumbnail_url (str): URL de la miniature dans S3
    """
    cursor.execute('''
    UPDATE images
    SET thumbnail_url = ?
    WHERE filename = ?
    ''', (thumbnail_url, filename))
    conn.commit()
