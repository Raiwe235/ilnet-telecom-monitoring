"""Flask application factory for ILNET monitoring platform"""

from flask import Flask
from flask_cors import CORS
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import structlog
from src.config import config
from src.snmp_collector.device_manager import DeviceManager
from src.snmp_collector.collector import SNMPCollector
from src.api.routes import init_routes

logger = structlog.get_logger(__name__)


def create_app():
    """Create and configure Flask application
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Configuration
    app.config['JSON_SORT_KEYS'] = False
    
    # CORS
    CORS(app)
    
    # Initialize dependencies
    device_manager = DeviceManager()
    snmp_collector = SNMPCollector()
    
    # Initialize routes
    init_routes(app, device_manager, snmp_collector)
    
    # Metrics endpoint
    @app.route('/metrics')
    def metrics():
        """Prometheus metrics endpoint"""
        return snmp_collector.get_metrics(), 200, {'Content-Type': 'text/plain'}
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error("internal_server_error", error=str(error))
        return {'error': 'Internal server error'}, 500
    
    logger.info(
        "flask_app_created",
        debug=app.debug,
        host=config.COLLECTOR_HOST,
        port=config.COLLECTOR_PORT
    )
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(
        host=config.COLLECTOR_HOST,
        port=config.COLLECTOR_PORT,
        debug=config.DEBUG
    )
