from flask import Flask, request, jsonify, send_file
import os
import uuid
import json
import tempfile
from pathlib import Path

# Import nos modules
from src.crypto_utils import CryptoManager
from src.hash_utils import HashManager  
from src.auth import auth_manager

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'data/encrypted'
METADATA_FILE = 'data/metadata.json'

# Créer les dossiers si nécessaire
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('data', exist_ok=True)

# Instances des gestionnaires
crypto = CryptoManager()
hash_manager = HashManager()

def load_metadata():
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_metadata(metadata):
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=2)

@app.route('/')
def home():
    return jsonify({
        "message": "Secure File Sharing API v2.0", 
        "status": "running",
        "features": ["encryption", "integrity_check", "authentication"]
    })

@app.route('/upload', methods=['POST'])
@auth_manager.require_auth
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    # Générer UUID pour le fichier
    file_id = str(uuid.uuid4())
    
    # Sauvegarder temporairement le fichier original
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        file.save(temp_file.name)
        temp_path = temp_file.name
    
    # Calculer le hash du fichier original
    original_hash = hash_manager.calculate_file_hash(temp_path)
    
    # Chiffrer le fichier
    encrypted_path = os.path.join(UPLOAD_FOLDER, file_id)
    crypto.encrypt_file(temp_path, encrypted_path)
    
    # Nettoyer le fichier temporaire
    os.unlink(temp_path)
    
    # Mettre à jour les métadonnées
    metadata = load_metadata()
    metadata[file_id] = {
        'original_name': file.filename,
        'size': os.path.getsize(encrypted_path),
        'original_hash': original_hash,
        'encrypted': True
    }
    save_metadata(metadata)
    
    return jsonify({
        "message": "File uploaded and encrypted successfully",
        "file_id": file_id,
        "original_name": file.filename,
        "original_hash": original_hash
    })

@app.route('/download/<file_id>')
@auth_manager.require_auth  
def download_file(file_id):
    metadata = load_metadata()
    
    if file_id not in metadata:
        return jsonify({"error": "File not found"}), 404
    
    encrypted_path = os.path.join(UPLOAD_FOLDER, file_id)
    if not os.path.exists(encrypted_path):
        return jsonify({"error": "File not found"}), 404
    
    # Déchiffrer le fichier temporairement
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = temp_file.name
    
    crypto.decrypt_file(encrypted_path, temp_path)
    
    # Vérifier l'intégrité
    decrypted_hash = hash_manager.calculate_file_hash(temp_path)
    expected_hash = metadata[file_id]['original_hash']
    
    if decrypted_hash != expected_hash:
        os.unlink(temp_path)
        return jsonify({"error": "File integrity check failed"}), 500
    
    # Le fichier temporaire sera supprimé après l'envoi par Flask
    return send_file(
        temp_path,
        as_attachment=True,
        download_name=metadata[file_id]['original_name']
    )

@app.route('/files')
@auth_manager.require_auth
def list_files():
    metadata = load_metadata()
    return jsonify(metadata)

@app.route('/verify/<file_id>')
@auth_manager.require_auth
def verify_file(file_id):
    """Vérifie l'intégrité d'un fichier sans le télécharger"""
    metadata = load_metadata()
    
    if file_id not in metadata:
        return jsonify({"error": "File not found"}), 404
    
    encrypted_path = os.path.join(UPLOAD_FOLDER, file_id)
    if not os.path.exists(encrypted_path):
        return jsonify({"error": "File not found"}), 404
    
    # Déchiffrer temporairement pour vérifier
    with tempfile.NamedTemporaryFile() as temp_file:
        crypto.decrypt_file(encrypted_path, temp_file.name)
        decrypted_hash = hash_manager.calculate_file_hash(temp_file.name)
    
    expected_hash = metadata[file_id]['original_hash']
    is_valid = decrypted_hash == expected_hash
    
    return jsonify({
        "file_id": file_id,
        "original_name": metadata[file_id]['original_name'],
        "integrity_valid": is_valid,
        "expected_hash": expected_hash,
        "actual_hash": decrypted_hash
    })

if __name__ == '__main__':
    print("🔐 Secure File Sharing API v2.0")
    print("🔑 Default password: secure_api_2024")
    print("📡 Starting server...")
    app.run(debug=True, host='0.0.0.0', port=5000)
