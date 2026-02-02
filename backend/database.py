import sqlite3
from datetime import datetime

# Connexion
conn = sqlite3.connect('images.db', check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Créer la table
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

# Ajouter une image
def add_image(filename, url, size):
    cursor.execute('''
    INSERT INTO images (filename, original_url, upload_date, size)
    VALUES (?, ?, ?, ?)
    ''', (filename, url, datetime.utcnow().isoformat(), size))
    conn.commit()

# Lister les images
def get_images():
    cursor.execute('SELECT * FROM images')
    return cursor.fetchall()

# Mettre à jour l'URL de la miniature
def update_thumbnail(filename, thumbnail_url):
    cursor.execute('''
    UPDATE images
    SET thumbnail_url = ?
    WHERE filename = ?
    ''', (thumbnail_url, filename))
    conn.commit()