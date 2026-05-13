"""Tests for health checks"""

import pytest


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_health_endpoint(self, client):
        """Test /health endpoint"""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'version' in data
        assert 'service' in data
    
    def test_status_endpoint(self, client):
        """Test /api/status endpoint"""
        response = client.get('/api/status')
        assert response.status_code == 200
        data = response.get_json()
        assert 'is_running' in data
        assert 'devices_configured' in data


class TestErrorHandling:
    """Test error handling"""
    
    def test_404_not_found(self, client):
        """Test 404 error handling"""
        response = client.get('/nonexistent')
        assert response.status_code == 404
    
    def test_invalid_json(self, client):
        """Test invalid JSON handling"""
        response = client.post('/api/auth/login',
                             data='invalid',
                             content_type='application/json')
        assert response.status_code in [400, 415]
