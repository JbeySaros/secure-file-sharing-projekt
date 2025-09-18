import os
import io
import pytest

from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_home_endpoint(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome" in response.data or b"OK" in response.data


def test_upload_without_auth(client):
    test_content = b"Hello World"
    data = {
        'file': (io.BytesIO(test_content), 'test.txt')
    }

    response = client.post('/upload', data=data, content_type='multipart/form-data')
    # Pas de token → doit être refusé
    assert response.status_code == 401


def test_upload_with_auth(client):
    test_content = b"Hello Auth World"
    data = {
        'file': (io.BytesIO(test_content), 'test.txt')
    }

    api_password = os.getenv("API_PASSWORD", "jenkins_test_api_2024")

    response = client.post(
        '/upload',
        data=data,
        content_type='multipart/form-data',
        headers={"Authorization": f"Bearer {api_password}"}
    )

    # Upload doit réussir avec le bon token
    assert response.status_code == 200, f"Upload failed: {response.data}"
    assert b"file_id" in response.data or b"success" in response.data


def test_list_files(client):
    api_password = os.getenv("API_PASSWORD", "jenkins_test_api_2024")

    response = client.get(
        '/files',
        headers={"Authorization": f"Bearer {api_password}"}
    )

    # La route /files est protégée → doit passer avec le bon token
    assert response.status_code == 200, f"List files unauthorized: {response.data}"
    assert isinstance(response.json, list)
