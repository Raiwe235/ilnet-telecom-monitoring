"""Main SNMP Collector module"""

import time
from datetime import datetime
from pathlib import Path
import structlog
from src.config import config
from src.snmp_collector.device_manager import DeviceManager
from src.snmp_collector.prometheus_exporter import PrometheusExporter

logger = structlog.get_logger(__name__)


class SNMPCollector:
    """Main SNMP collector for network device monitoring"""
    
    def __init__(self):
        """Initialize SNMP Collector"""
        self.device_manager = DeviceManager()
        self.prometheus_exporter = PrometheusExporter()
        self.is_running = False
        self.collection_count = 0
        self.error_count = 0
        
        logger.info(
            "collector_initialized",
            devices_count=len(self.device_manager.get_all_devices())
        )
    
    def collect_device_metrics(self, device_id: str) -> bool:
        """Collect metrics from a device
        
        Args:
            device_id: Device identifier
            
        Returns:
            True if successful, False otherwise
        """
        start_time = time.time()
        
        try:
            device = self.device_manager.get_device(device_id)
            if not device:
                logger.warning(
                    "device_not_found",
                    device_id=device_id
                )
                return False
            
            if not device.get('enabled', True):
                logger.debug(
                    "device_disabled",
                    device_id=device_id
                )
                return False
            
            manager = self.device_manager.get_snmp_manager(device_id)
            if not manager:
                logger.error(
                    "snmp_manager_not_found",
                    device_id=device_id
                )
                return False
            
            # Collect system information
            system_info = manager.get_system_info()
            if not system_info.get('hostname'):
                logger.warning(
                    "failed_to_collect_system_info",
                    device_id=device_id,
                    host=device['host']
                )
                return False
            
            # Update device metrics
            device_data = {
                'status': 'up',
                'uptime': system_info.get('uptime'),
            }
            self.prometheus_exporter.update_device_metrics(
                device_id=device_id,
                device_name=device['name'],
                host=device['host'],
                device_data=device_data
            )
            
            # Collect interface metrics
            interfaces = manager.get_interfaces()
            for if_index, if_data in interfaces.items():
                self.prometheus_exporter.update_interface_metrics(
                    device_id=device_id,
                    interface_index=if_index,
                    interface_data=if_data
                )
            
            # Record collection time
            duration = time.time() - start_time
            self.prometheus_exporter.record_collection_time(
                device_id=device_id,
                duration=duration
            )
            
            logger.debug(
                "device_metrics_collected",
                device_id=device_id,
                interfaces_count=len(interfaces),
                duration=duration
            )
            
            return True
        
        except Exception as e:
            self.error_count += 1
            logger.error(
                "collection_error",
                device_id=device_id,
                error=str(e)
            )
            return False
    
    def collect_all_metrics(self) -> int:
        """Collect metrics from all devices
        
        Returns:
            Number of successfully collected devices
        """
        devices = self.device_manager.get_all_devices()
        if not devices:
            logger.warning("no_devices_configured")
            return 0
        
        success_count = 0
        for device_id in devices.keys():
            if self.collect_device_metrics(device_id):
                success_count += 1
        
        self.collection_count += 1
        
        logger.info(
            "collection_cycle_complete",
            cycle=self.collection_count,
            devices_total=len(devices),
            devices_success=success_count,
            devices_failed=len(devices) - success_count
        )
        
        return success_count
    
    def get_metrics(self) -> bytes:
        """Get current metrics in Prometheus format
        
        Returns:
            Prometheus format metrics as bytes
        """
        return self.prometheus_exporter.get_metrics()
    
    def get_status(self) -> dict:
        """Get collector status
        
        Returns:
            Status dictionary
        """
        devices = self.device_manager.get_all_devices()
        return {
            'is_running': self.is_running,
            'devices_configured': len(devices),
            'collection_cycles': self.collection_count,
            'total_errors': self.error_count,
            'timestamp': datetime.utcnow().isoformat(),
        }
