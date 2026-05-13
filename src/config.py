"""Configuration management for ILNET monitoring platform"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_file = Path(__file__).parent.parent / '.env'
if env_file.exists():
    load_dotenv(env_file)
else:
    load_dotenv(Path(__file__).parent.parent / '.env.example')


class Config:
    """Base configuration"""
    DEBUG = False
    TESTING = False
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # SNMP Configuration
    SNMP_VERSION = os.getenv('SNMP_VERSION', '2c')
    SNMP_COMMUNITY = os.getenv('SNMP_COMMUNITY', 'public')
    SNMP_TIMEOUT = int(os.getenv('SNMP_TIMEOUT', '5'))
    SNMP_RETRIES = int(os.getenv('SNMP_RETRIES', '3'))
    SNMP_PORT = int(os.getenv('SNMP_PORT', '161'))
    
    # Collector Configuration
    COLLECTOR_PORT = int(os.getenv('COLLECTOR_PORT', '8000'))
    COLLECTOR_HOST = os.getenv('COLLECTOR_HOST', '0.0.0.0')
    COLLECTOR_INTERVAL = int(os.getenv('COLLECTOR_INTERVAL', '30'))
    
    # Prometheus Configuration
    PROMETHEUS_PUSHGATEWAY = os.getenv('PROMETHEUS_PUSHGATEWAY', 'http://prometheus:9091')
    PROMETHEUS_PORT = int(os.getenv('PROMETHEUS_PORT', '9090'))
    
    # Redis Configuration
    REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
    REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', 'redispassword')
    REDIS_DB = int(os.getenv('REDIS_DB', '0'))
    
    # Security
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-this')
    TLS_ENABLED = os.getenv('TLS_ENABLED', 'false').lower() == 'true'
    TLS_CERT_PATH = os.getenv('TLS_CERT_PATH', '/app/certs/server.crt')
    TLS_KEY_PATH = os.getenv('TLS_KEY_PATH', '/app/certs/server.key')
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    CONFIG_DIR = BASE_DIR / 'config'
    LOGS_DIR = Path('/var/log/ilnet')
    DEVICES_CONFIG = CONFIG_DIR / 'snmp_devices.json'


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = 'INFO'


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    LOG_LEVEL = 'DEBUG'
    SNMP_COMMUNITY = 'test'


# Select configuration based on environment
env = os.getenv('FLASK_ENV', 'development')
if env == 'production':
    config = ProductionConfig()
elif env == 'testing':
    config = TestingConfig()
else:
    config = DevelopmentConfig()
