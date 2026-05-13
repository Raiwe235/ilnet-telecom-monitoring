"""Test configuration and fixtures"""

import pytest
import json
from pathlib import Path
from src.config import TestingConfig
from src.api.app import create_app
from src.snmp_collector.device_manager import DeviceManager
from src.snmp_collector.collector import SNMPCollector


@pytest.fixture
def app():
    """Create Flask app for testing"""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def temp_device_config(tmp_path):
    """Create temporary device configuration file"""
    config_file = tmp_path / 'devices.json'
    config_file.write_text(json.dumps({
        'devices': {
            'test_router': {
                'host': '192.168.1.1',
                'name': 'Test Router',
                'community': 'public',
                'version': '2c',
                'device_type': 'router',
                'tags': ['test'],
                'enabled': True
            }
        }
    }))
    return config_file


@pytest.fixture
def device_manager(temp_device_config):
    """Create DeviceManager instance with test config"""
    return DeviceManager(config_file=temp_device_config)


@pytest.fixture
def snmp_collector():
    """Create SNMPCollector instance"""
    return SNMPCollector()
