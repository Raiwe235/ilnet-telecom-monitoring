"""JWT Authentication for ILNET API"""

from functools import wraps
from datetime import datetime, timedelta
import jwt
from flask import request, jsonify, current_app
import structlog
from src.config import config

logger = structlog.get_logger(__name__)


class AuthManager:
    """Manage JWT authentication"""
    
    @staticmethod
    def generate_token(user_id: str, expires_in: int = 3600) -> str:
        """Generate JWT token
        
        Args:
            user_id: User identifier
            expires_in: Token expiration time in seconds
            
        Returns:
            JWT token string
        """
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(seconds=expires_in),
            'iat': datetime.utcnow(),
        }
        token = jwt.encode(
            payload,
            config.JWT_SECRET_KEY,
            algorithm='HS256'
        )
        logger.info(
            "token_generated",
            user_id=user_id,
            expires_in=expires_in
        )
        return token
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload
            
        Raises:
            jwt.InvalidTokenError: If token is invalid
        """
        try:
            payload = jwt.decode(
                token,
                config.JWT_SECRET_KEY,
                algorithms=['HS256']
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("token_expired")
            raise
        except jwt.InvalidTokenError as e:
            logger.warning("invalid_token", error=str(e))
            raise


def token_required(f):
    """Decorator to require JWT token for route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            payload = AuthManager.verify_token(token)
            request.user_id = payload.get('user_id')
        except Exception as e:
            logger.warning(
                "token_verification_failed",
                error=str(e)
            )
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function
