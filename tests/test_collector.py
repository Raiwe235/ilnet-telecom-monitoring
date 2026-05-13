"""Tests for SNMP collector"""

import pytest
from src.snmp_collector.collector import SNMPCollector


class TestSNMPCollector:
    """Test SNMP collector functionality"""
    
    def test_collector_initialization(self, snmp_collector):
        """Test collector initialization"""
        assert snmp_collector is not None
        assert snmp_collector.collection_count == 0
        assert snmp_collector.error_count == 0
    
    def test_get_status(self, snmp_collector):
        """Test getting collector status"""
        status = snmp_collector.get_status()
        
        assert 'is_running' in status
        assert 'devices_configured' in status
        assert 'collection_cycles' in status
        assert 'total_errors' in status
        assert 'timestamp' in status
    
    def test_get_metrics(self, snmp_collector):
        """Test getting metrics"""
        metrics = snmp_collector.get_metrics()
        
        assert isinstance(metrics, bytes)
        assert b'ilnet_device_up' in metrics or len(metrics) > 0


class TestCollectorRoutes:
    """Test collector API routes"""
    
    @pytest.fixture
    def auth_token(self, client):
        """Get authentication token"""
        response = client.post('/api/auth/login', json={
            'username': 'admin',
            'password': 'password'
        })
        data = response.get_json()
        return data['token']
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
    
    def test_collector_status(self, client):
        """Test getting collector status"""
        response = client.get('/api/collector/status')
        assert response.status_code == 200
        data = response.get_json()
        assert 'is_running' in data
    
    def test_collect_metrics(self, client, auth_token):
        """Test triggering metrics collection"""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.post('/api/collector/collect', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'devices_success' in data
    
    def test_collect_metrics_no_auth(self, client):
        """Test metrics collection without auth"""
        response = client.post('/api/collector/collect')
        assert response.status_code == 401
