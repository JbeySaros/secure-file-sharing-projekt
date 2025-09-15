from flask import Flask, request, jsonify, send_file
import os
import uuid
import json
from pathlib import Path

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'data/encrypted'
METADATA_FILE = 'data/metadata.json'

# Créer les dossiers si nécessaire
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('data', exist_ok=True)

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
    return jsonify({"message": "Secure File Sharing API", "status": "running"})

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    # Générer UUID pour le fichier
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_FOLDER, file_id)
    
    # Sauvegarder le fichier (temporairement sans chiffrement)
    file.save(file_path)
    
    # Mettre à jour les métadonnées
    metadata = load_metadata()
    metadata[file_id] = {
        'original_name': file.filename,
        'size': os.path.getsize(file_path)
    }
    save_metadata(metadata)
    
    return jsonify({
        "message": "File uploaded successfully",
        "file_id": file_id,
        "original_name": file.filename
    })

@app.route('/download/<file_id>')
def download_file(file_id):
    metadata = load_metadata()
    
    if file_id not in metadata:
        return jsonify({"error": "File not found"}), 404
    
    file_path = os.path.join(UPLOAD_FOLDER, file_id)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    
    return send_file(
        file_path,
        as_attachment=True,
        download_name=metadata[file_id]['original_name']
    )

@app.route('/files')
def list_files():
    metadata = load_metadata()
    return jsonify(metadata)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
