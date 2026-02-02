// Configuration de l'API
const API_URL = 'http://localhost:8000';

// Éléments du DOM
const uploadForm = document.getElementById('uploadForm');
const fileInput = document.getElementById('fileInput');
const uploadStatus = document.getElementById('uploadStatus');
const gallery = document.getElementById('gallery');
const refreshBtn = document.getElementById('refreshBtn');

// Fonction pour uploader une image
uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault(); // Empêche le rechargement de la page
    
    const file = fileInput.files[0];
    
    if (!file) {
        showStatus('Veuillez sélectionner un fichier', 'error');
        return;
    }
    
    // Créer un FormData pour envoyer le fichier
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        showStatus('Upload en cours...', '');
        
        // Envoyer le fichier à l'API
        const response = await fetch(`${API_URL}/upload`, {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const data = await response.json();
            showStatus(` Image "${data.filename}" uploadée avec succès !`, 'success');
            fileInput.value = ''; // Réinitialiser le champ
            loadImages(); // Recharger la galerie
        } else {
            showStatus(' Erreur lors de l\'upload', 'error');
        }
    } catch (error) {
        showStatus(' Erreur de connexion à l\'API', 'error');
        console.error('Erreur:', error);
    }
});

// Fonction pour afficher les messages de statut
function showStatus(message, type) {
    uploadStatus.textContent = message;
    uploadStatus.className = type;
}

// Fonction pour charger et afficher les images
async function loadImages() {
    try {
        const response = await fetch(`${API_URL}/images`);
        const images = await response.json();
        
        if (images.length === 0) {
            gallery.innerHTML = '<p class="empty-message">Aucune image pour le moment.</p>';
            return;
        }
        
        // Vider la galerie
        gallery.innerHTML = '';
        
        // Créer une carte pour chaque image
        images.forEach(img => {
            const card = document.createElement('div');
            card.className = 'image-card';
            
            // Formater la date
            const date = new Date(img.upload_date).toLocaleDateString('fr-FR', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
            
            // Formater la taille (bytes → KB ou MB)
            const size = img.size < 1024 * 1024 
                ? `${(img.size / 1024).toFixed(2)} KB`
                : `${(img.size / (1024 * 1024)).toFixed(2)} MB`;
            
            card.innerHTML = `
                <img src="${img.original_url}" alt="${img.filename}" onclick="window.open('${img.original_url}', '_blank')">
                <div class="image-info">
                    <p class="image-filename">${img.filename}</p>
                    <p>${date}</p>
                    <p>${size}</p>
                    <button class="delete-btn" onclick="deleteImage('${img.filename}')">Supprimer</button>
                </div>
            `;
            
            gallery.appendChild(card);
        });
    } catch (error) {
        gallery.innerHTML = '<p class="empty-message">Erreur lors du chargement des images</p>';
        console.error('Erreur:', error);
    }
}

// Fonction pour supprimer une image
async function deleteImage(filename) {
    if (!confirm(`Voulez-vous vraiment supprimer "${filename}" ?`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/images/${filename}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            alert(`Image "${filename}" supprimée`);
            loadImages(); // Recharger la galerie
        } else {
            alert('Erreur lors de la suppression');
        }
    } catch (error) {
        alert('Erreur de connexion');
        console.error('Erreur:', error);
    }
}

// Mode nuit
const darkModeToggle = document.getElementById('darkModeToggle');

// Charger la préférence sauvegardée
if (localStorage.getItem('darkMode') === 'enabled') {
    document.body.classList.add('dark-mode');
    darkModeToggle.textContent = 'Mode Jour';
}

// Toggle mode nuit
darkModeToggle.addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
    
    if (document.body.classList.contains('dark-mode')) {
        darkModeToggle.textContent = 'Mode Jour';
        localStorage.setItem('darkMode', 'enabled');
    } else {
        darkModeToggle.textContent = 'Mode Nuit';
        localStorage.setItem('darkMode', 'disabled');
    }
});

// Bouton rafraîchir
refreshBtn.addEventListener('click', loadImages);

// Charger les images au démarrage de la page
loadImages();
