"""
Authentication Service

Handles user authentication and password verification.
"""

import hashlib
from typing import Optional, Dict


class AuthService:
    """Service for handling authentication"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return AuthService.hash_password(plain_password) == hashed_password
    
    @staticmethod
    def generate_token(user_id: str, user_type: str) -> str:
        """Generate a simple token (in production, use JWT)"""
        # This is a simple token for development
        # In production, use proper JWT tokens with expiration
        token_string = f"{user_id}:{user_type}"
        return hashlib.sha256(token_string.encode()).hexdigest()


# Global instance
auth_service = AuthService()
