"""Tests for API authentication"""

import pytest
from src.api.auth import AuthManager
import jwt
from src.config import config


class TestAuthManager:
    """Test JWT authentication"""
    
    def test_generate_token(self):
        """Test token generation"""
        token = AuthManager.generate_token('testuser')
        assert token is not None
        assert isinstance(token, str)
    
    def test_verify_token(self):
        """Test token verification"""
        user_id = 'testuser'
        token = AuthManager.generate_token(user_id)
        payload = AuthManager.verify_token(token)
        
        assert payload['user_id'] == user_id
    
    def test_verify_invalid_token(self):
        """Test verification with invalid token"""
        with pytest.raises(jwt.InvalidTokenError):
            AuthManager.verify_token('invalid.token.here')
    
    def test_token_expiration(self):
        """Test token expiration"""
        # Generate token with 1 second expiration
        token = AuthManager.generate_token('testuser', expires_in=1)
        
        # Verify immediately
        payload = AuthManager.verify_token(token)
        assert payload['user_id'] == 'testuser'
        
        # Wait and verify expiration
        import time
        time.sleep(2)
        
        with pytest.raises(jwt.ExpiredSignatureError):
            AuthManager.verify_token(token)


class TestAuthRoutes:
    """Test authentication routes"""
    
    def test_login_success(self, client):
        """Test successful login"""
        response = client.post('/api/auth/login', json={
            'username': 'admin',
            'password': 'password123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'token' in data
        assert data['token_type'] == 'Bearer'
        assert data['expires_in'] == 3600
    
    def test_login_missing_credentials(self, client):
        """Test login with missing credentials"""
        response = client.post('/api/auth/login', json={})
        assert response.status_code == 400
        
        response = client.post('/api/auth/login', json={'username': 'admin'})
        assert response.status_code == 400
    
    def test_login_invalid_json(self, client):
        """Test login with invalid JSON"""
        response = client.post('/api/auth/login', 
                             data='invalid',
                             content_type='application/json')
        assert response.status_code in [400, 415]
