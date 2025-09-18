from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

class CryptoManager:
    def __init__(self, password: str = None):
        """Initialise le gestionnaire de chiffrement avec un mot de passe maître"""
        if password is None:
            password = os.environ.get('MASTER_PASSWORD', 'default_secure_password_2024')
        
        self.password = password.encode()
        self._key = None
    
    def _get_key(self, salt: bytes = None) -> bytes:
        """Génère ou récupère la clé de chiffrement"""
        if salt is None:
            salt = b'stable_salt_for_demo'  # En production, utiliser un salt aléatoire par fichier
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password))
        return key
    
    def encrypt_data(self, data: bytes) -> bytes:
        """Chiffre des données"""
        key = self._get_key()
        f = Fernet(key)
        encrypted_data = f.encrypt(data)
        return encrypted_data
    
    def decrypt_data(self, encrypted_data: bytes) -> bytes:
        """Déchiffre des données"""
        key = self._get_key()
        f = Fernet(key)
        decrypted_data = f.decrypt(encrypted_data)
        return decrypted_data
    
    def encrypt_file(self, input_path: str, output_path: str):
        """Chiffre un fichier"""
        with open(input_path, 'rb') as file:
            file_data = file.read()
        
        encrypted_data = self.encrypt_data(file_data)
        
        with open(output_path, 'wb') as encrypted_file:
            encrypted_file.write(encrypted_data)
    
    def decrypt_file(self, encrypted_path: str, output_path: str):
        """Déchiffre un fichier"""
        with open(encrypted_path, 'rb') as encrypted_file:
            encrypted_data = encrypted_file.read()
        
        decrypted_data = self.decrypt_data(encrypted_data)
        
        with open(output_path, 'wb') as file:
            file.write(decrypted_data)

# Test rapide
if __name__ == "__main__":
    crypto = CryptoManager("test_password")
    
    # Test avec des données
    test_data = b"Hello World - Secret Message!"
    encrypted = crypto.encrypt_data(test_data)
    decrypted = crypto.decrypt_data(encrypted)
    
    print(f"Original: {test_data}")
    print(f"Encrypted: {encrypted[:50]}...")  # Affiche juste le début
    print(f"Decrypted: {decrypted}")
    print(f"Success: {test_data == decrypted}")
