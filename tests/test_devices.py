"""Tests for device management"""

import pytest
from src.snmp_collector.device_manager import DeviceManager


class TestDeviceManager:
    """Test device management functionality"""
    
    def test_load_devices(self, device_manager):
        """Test loading devices from config"""
        devices = device_manager.get_all_devices()
        assert len(devices) > 0
        assert 'test_router' in devices
    
    def test_get_device(self, device_manager):
        """Test retrieving specific device"""
        device = device_manager.get_device('test_router')
        assert device is not None
        assert device['host'] == '192.168.1.1'
        assert device['name'] == 'Test Router'
    
    def test_get_nonexistent_device(self, device_manager):
        """Test retrieving non-existent device"""
        device = device_manager.get_device('nonexistent')
        assert device is None
    
    def test_add_device(self, device_manager):
        """Test adding a new device"""
        success = device_manager.add_device(
            device_id='new_switch',
            host='192.168.1.100',
            name='New Switch',
            community='public',
            device_type='switch',
            tags=['test', 'new']
        )
        
        assert success is True
        device = device_manager.get_device('new_switch')
        assert device is not None
        assert device['host'] == '192.168.1.100'
    
    def test_add_duplicate_device(self, device_manager):
        """Test adding duplicate device ID"""
        success = device_manager.add_device(
            device_id='test_router',
            host='192.168.1.200',
            name='Duplicate Router'
        )
        assert success is False
    
    def test_remove_device(self, device_manager):
        """Test removing a device"""
        # Add device first
        device_manager.add_device(
            device_id='device_to_remove',
            host='192.168.1.50',
            name='Device to Remove'
        )
        
        # Remove it
        success = device_manager.remove_device('device_to_remove')
        assert success is True
        
        # Verify it's gone
        device = device_manager.get_device('device_to_remove')
        assert device is None
    
    def test_remove_nonexistent_device(self, device_manager):
        """Test removing non-existent device"""
        success = device_manager.remove_device('nonexistent')
        assert success is False
    
    def test_get_snmp_manager(self, device_manager):
        """Test getting SNMP manager for device"""
        manager = device_manager.get_snmp_manager('test_router')
        assert manager is not None


class TestDeviceRoutes:
    """Test device API routes"""
    
    @pytest.fixture
    def auth_token(self, client):
        """Get authentication token"""
        response = client.post('/api/auth/login', json={
            'username': 'admin',
            'password': 'password'
        })
        data = response.get_json()
        return data['token']
    
    def test_list_devices(self, client, auth_token):
        """Test listing all devices"""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.get('/api/devices/', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'devices' in data
        assert 'count' in data
    
    def test_list_devices_no_auth(self, client):
        """Test listing devices without authentication"""
        response = client.get('/api/devices/')
        assert response.status_code == 401
    
    def test_add_device_via_api(self, client, auth_token):
        """Test adding device via API"""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.post('/api/devices/', 
                             headers=headers,
                             json={
                                 'device_id': 'api_router',
                                 'host': '192.168.1.200',
                                 'name': 'API Router',
                                 'device_type': 'router'
                             })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['device_id'] == 'api_router'
    
    def test_add_device_missing_fields(self, client, auth_token):
        """Test adding device with missing required fields"""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.post('/api/devices/',
                             headers=headers,
                             json={'device_id': 'incomplete'})
        
        assert response.status_code == 400
