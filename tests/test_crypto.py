import pytest
import tempfile
import os
from src.crypto_utils import CryptoManager
from src.hash_utils import HashManager

def test_crypto_encrypt_decrypt():
    """Test chiffrement/déchiffrement de données"""
    crypto = CryptoManager("test_password")
    
    original_data = b"Secret message for testing"
    encrypted_data = crypto.encrypt_data(original_data)
    decrypted_data = crypto.decrypt_data(encrypted_data)
    
    assert original_data == decrypted_data
    assert original_data != encrypted_data  # Vérifier que c'est bien chiffré

def test_crypto_file_operations():
    """Test chiffrement/déchiffrement de fichiers"""
    crypto = CryptoManager("test_password")
    
    # Créer un fichier de test
    test_content = b"File content for encryption test"
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(test_content)
        original_path = temp_file.name
    
    # Chemins pour fichiers chiffré et déchiffré
    encrypted_path = original_path + ".encrypted"
    decrypted_path = original_path + ".decrypted"
    
    try:
        # Chiffrer
        crypto.encrypt_file(original_path, encrypted_path)
        assert os.path.exists(encrypted_path)
        
        # Déchiffrer
        crypto.decrypt_file(encrypted_path, decrypted_path)
        assert os.path.exists(decrypted_path)
        
        # Vérifier le contenu
        with open(decrypted_path, 'rb') as f:
            decrypted_content = f.read()
        
        assert test_content == decrypted_content
        
    finally:
        # Nettoyer
        for path in [original_path, encrypted_path, decrypted_path]:
            if os.path.exists(path):
                os.unlink(path)

def test_hash_calculation():
    """Test calcul de hash"""
    test_content = b"Content for hashing"
    
    # Hash de données
    hash1 = HashManager.calculate_data_hash(test_content)
    hash2 = HashManager.calculate_data_hash(test_content)
    assert hash1 == hash2  # Même contenu = même hash
    
    # Hash de fichier
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(test_content)
        temp_path = temp_file.name
    
    try:
        file_hash = HashManager.calculate_file_hash(temp_path)
        data_hash = HashManager.calculate_data_hash(test_content)
        assert file_hash == data_hash  # Même contenu = même hash
        
        # Test vérification d'intégrité
        assert HashManager.verify_file_integrity(temp_path, file_hash) == True
        assert HashManager.verify_file_integrity(temp_path, "wrong_hash") == False
        
    finally:
        os.unlink(temp_path)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
