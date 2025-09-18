from functools import wraps
from flask import request, jsonify
import os
import hashlib

class AuthManager:
    def __init__(self):
        # Mot de passe maître hashé (en production, utiliser bcrypt)
        self.master_password_hash = self._hash_password(
            os.environ.get('API_PASSWORD', 'secure_api_2024')
        )
    
    def _hash_password(self, password: str) -> str:
        """Hash un mot de passe avec SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str) -> bool:
        """Vérifie si le mot de passe est correct"""
        return self._hash_password(password) == self.master_password_hash
    
    def require_auth(self, f):
        """Décorateur pour protéger les routes"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Vérifier le header Authorization
            auth_header = request.headers.get('Authorization')
            
            if not auth_header:
                return jsonify({'error': 'Authorization header required'}), 401
            
            # Format attendu: "Bearer password"
            try:
                auth_type, password = auth_header.split(' ', 1)
                if auth_type.lower() != 'bearer':
                    return jsonify({'error': 'Invalid authorization type'}), 401
            except ValueError:
                return jsonify({'error': 'Invalid authorization format'}), 401
            
            if not self.verify_password(password):
                return jsonify({'error': 'Invalid credentials'}), 401
            
            return f(*args, **kwargs)
        return decorated_function

# Instance globale
auth_manager = AuthManager()

# Test rapide
if __name__ == "__main__":
    auth = AuthManager()
    
    # Test avec bon mot de passe
    print(f"Good password: {auth.verify_password('secure_api_2024')}")
    
    # Test avec mauvais mot de passe  
    print(f"Bad password: {auth.verify_password('wrong_password')}")
