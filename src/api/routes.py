"""API Routes for ILNET monitoring platform"""

from flask import Blueprint, request, jsonify
import structlog
from src.api.auth import token_required, AuthManager
from src.snmp_collector.device_manager import DeviceManager
from src.snmp_collector.collector import SNMPCollector

logger = structlog.get_logger(__name__)

# Create blueprints
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
health_bp = Blueprint('health', __name__, url_prefix='/api')
devices_bp = Blueprint('devices', __name__, url_prefix='/api/devices')
collector_bp = Blueprint('collector', __name__, url_prefix='/api/collector')

# Global instances
device_manager = None
snmp_collector = None


def init_routes(app, _device_manager, _snmp_collector):
    """Initialize routes with dependencies
    
    Args:
        app: Flask application
        _device_manager: DeviceManager instance
        _snmp_collector: SNMPCollector instance
    """
    global device_manager, snmp_collector
    device_manager = _device_manager
    snmp_collector = _snmp_collector
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(devices_bp)
    app.register_blueprint(collector_bp)


# === AUTH ROUTES ===

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login and get JWT token
    
    Request JSON:
        {
            "username": "admin",
            "password": "password123"
        }
    """
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing credentials'}), 400
    
    # TODO: Implement proper authentication against user database
    # For now, accept any username/password (insecure - for demo only)
    username = data['username']
    
    try:
        token = AuthManager.generate_token(
            user_id=username,
            expires_in=3600
        )
        return jsonify({
            'token': token,
            'expires_in': 3600,
            'token_type': 'Bearer'
        }), 200
    except Exception as e:
        logger.error("login_error", error=str(e))
        return jsonify({'error': 'Login failed'}), 500


# === HEALTH ROUTES ===

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'service': 'ilnet-collector'
    }), 200


@health_bp.route('/status', methods=['GET'])
def status():
    """Get collector status"""
    if not snmp_collector:
        return jsonify({'error': 'Collector not initialized'}), 500
    
    status_data = snmp_collector.get_status()
    return jsonify(status_data), 200


# === DEVICE ROUTES ===

@devices_bp.route('/', methods=['GET'])
@token_required
def list_devices():
    """List all configured devices"""
    if not device_manager:
        return jsonify({'error': 'Device manager not initialized'}), 500
    
    devices = device_manager.get_all_devices()
    return jsonify({
        'count': len(devices),
        'devices': devices
    }), 200


@devices_bp.route('/<device_id>', methods=['GET'])
@token_required
def get_device(device_id):
    """Get specific device information"""
    if not device_manager:
        return jsonify({'error': 'Device manager not initialized'}), 500
    
    device = device_manager.get_device(device_id)
    if not device:
        return jsonify({'error': 'Device not found'}), 404
    
    return jsonify(device), 200


@devices_bp.route('/', methods=['POST'])
@token_required
def add_device():
    """Add a new device
    
    Request JSON:
        {
            "device_id": "router_main",
            "host": "192.168.1.1",
            "name": "Main Router",
            "community": "public",
            "device_type": "router",
            "tags": ["core", "production"]
        }
    """
    if not device_manager:
        return jsonify({'error': 'Device manager not initialized'}), 500
    
    data = request.get_json()
    required_fields = ['device_id', 'host', 'name']
    
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    success = device_manager.add_device(
        device_id=data['device_id'],
        host=data['host'],
        name=data['name'],
        community=data.get('community', 'public'),
        device_type=data.get('device_type', 'router'),
        tags=data.get('tags', [])
    )
    
    if success:
        return jsonify({
            'message': 'Device added successfully',
            'device_id': data['device_id']
        }), 201
    else:
        return jsonify({'error': 'Failed to add device'}), 400


@devices_bp.route('/<device_id>', methods=['DELETE'])
@token_required
def remove_device(device_id):
    """Remove a device"""
    if not device_manager:
        return jsonify({'error': 'Device manager not initialized'}), 500
    
    success = device_manager.remove_device(device_id)
    
    if success:
        return jsonify({'message': 'Device removed successfully'}), 200
    else:
        return jsonify({'error': 'Device not found'}), 404


@devices_bp.route('/test/<device_id>', methods=['POST'])
@token_required
def test_device_connection(device_id):
    """Test connection to a device"""
    if not device_manager:
        return jsonify({'error': 'Device manager not initialized'}), 500
    
    is_connected = device_manager.test_device_connection(device_id)
    
    return jsonify({
        'device_id': device_id,
        'connected': is_connected
    }), 200


@devices_bp.route('/test', methods=['POST'])
@token_required
def test_all_connections():
    """Test connection to all devices"""
    if not device_manager:
        return jsonify({'error': 'Device manager not initialized'}), 500
    
    results = device_manager.test_all_connections()
    
    return jsonify({
        'total': len(results),
        'results': results
    }), 200


# === COLLECTOR ROUTES ===

@collector_bp.route('/collect', methods=['POST'])
@token_required
def collect_metrics():
    """Trigger metric collection from all devices"""
    if not snmp_collector:
        return jsonify({'error': 'Collector not initialized'}), 500
    
    success_count = snmp_collector.collect_all_metrics()
    
    return jsonify({
        'message': 'Metrics collected',
        'devices_success': success_count,
        'status': snmp_collector.get_status()
    }), 200


@collector_bp.route('/collect/<device_id>', methods=['POST'])
@token_required
def collect_device_metrics(device_id):
    """Trigger metric collection from specific device"""
    if not snmp_collector:
        return jsonify({'error': 'Collector not initialized'}), 500
    
    success = snmp_collector.collect_device_metrics(device_id)
    
    return jsonify({
        'device_id': device_id,
        'success': success,
        'status': snmp_collector.get_status()
    }), 200


@collector_bp.route('/status', methods=['GET'])
def get_collector_status():
    """Get collector status"""
    if not snmp_collector:
        return jsonify({'error': 'Collector not initialized'}), 500
    
    return jsonify(snmp_collector.get_status()), 200
