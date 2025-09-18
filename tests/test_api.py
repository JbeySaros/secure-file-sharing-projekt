import pytest
import tempfile
import json
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture  
def auth_headers():
    return {'Authorization': 'Bearer secure_api_2024'}

def test_home_endpoint(client):
    """Test de l'endpoint home"""
    response = client.get('/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'Secure File Sharing API' in data['message']

def test_upload_without_auth(client):
    """Test upload sans authentification"""
    response = client.post('/upload')
    assert response.status_code == 401

def test_upload_with_auth(client, auth_headers):
    """Test upload avec authentification"""
    # Créer un fichier de test
    test_content = b"Test file content for upload"
    
    data = {
        'file': (tempfile.BytesIO(test_content), 'test.txt')
    }
    
    response = client.post('/upload', data=data, headers=auth_headers)
    assert response.status_code == 200
    
    response_data = json.loads(response.data)
    assert 'file_id' in response_data
    assert response_data['original_name'] == 'test.txt'

def test_list_files(client, auth_headers):
    """Test listage des fichiers"""
    response = client.get('/files', headers=auth_headers)
    assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
