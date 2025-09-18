import hashlib
import os

class HashManager:
    @staticmethod
    def calculate_file_hash(file_path: str) -> str:
        """Calcule le hash SHA-256 d'un fichier"""
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            # Lire le fichier par chunks pour économiser la mémoire
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    @staticmethod
    def calculate_data_hash(data: bytes) -> str:
        """Calcule le hash SHA-256 de données en mémoire"""
        return hashlib.sha256(data).hexdigest()
    
    @staticmethod
    def verify_file_integrity(file_path: str, expected_hash: str) -> bool:
        """Vérifie l'intégrité d'un fichier"""
        if not os.path.exists(file_path):
            return False
        
        actual_hash = HashManager.calculate_file_hash(file_path)
        return actual_hash == expected_hash

# Test rapide
if __name__ == "__main__":
    # Créer un fichier de test
    test_content = b"Test file content for hashing"
    with open("temp_test.txt", "wb") as f:
        f.write(test_content)
    
    # Calculer hash
    hash_value = HashManager.calculate_file_hash("temp_test.txt")
    print(f"File hash: {hash_value}")
    
    # Vérifier intégrité
    is_valid = HashManager.verify_file_integrity("temp_test.txt", hash_value)
    print(f"Integrity check: {is_valid}")
    
    # Nettoyer
    os.remove("temp_test.txt")
