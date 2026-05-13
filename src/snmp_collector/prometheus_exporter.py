"""Prometheus metrics exporter for network devices"""

from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    Summary,
    CollectorRegistry,
    generate_latest,
    REGISTRY,
)
from typing import Dict, Any
import structlog

logger = structlog.get_logger(__name__)


class PrometheusExporter:
    """Export network metrics to Prometheus format"""
    
    def __init__(self, registry=None):
        """Initialize Prometheus Exporter
        
        Args:
            registry: CollectorRegistry instance (uses default if None)
        """
        self.registry = registry or REGISTRY
        self._init_metrics()
    
    def _init_metrics(self):
        """Initialize all metrics"""
        
        # Device metrics
        self.device_up = Gauge(
            'ilnet_device_up',
            'Device is up (1) or down (0)',
            ['device_id', 'device_name', 'host'],
            registry=self.registry
        )
        
        self.device_uptime = Gauge(
            'ilnet_device_uptime_seconds',
            'Device uptime in seconds',
            ['device_id', 'device_name'],
            registry=self.registry
        )
        
        # Interface metrics
        self.interface_up = Gauge(
            'ilnet_interface_up',
            'Interface status (1=up, 0=down)',
            ['device_id', 'interface_name', 'interface_index'],
            registry=self.registry
        )
        
        self.interface_speed = Gauge(
            'ilnet_interface_speed_bps',
            'Interface speed in bits per second',
            ['device_id', 'interface_name', 'interface_index'],
            registry=self.registry
        )
        
        self.interface_in_octets = Counter(
            'ilnet_interface_in_octets_total',
            'Total inbound octets',
            ['device_id', 'interface_name', 'interface_index'],
            registry=self.registry
        )
        
        self.interface_out_octets = Counter(
            'ilnet_interface_out_octets_total',
            'Total outbound octets',
            ['device_id', 'interface_name', 'interface_index'],
            registry=self.registry
        )
        
        self.interface_in_errors = Counter(
            'ilnet_interface_in_errors_total',
            'Total inbound errors',
            ['device_id', 'interface_name', 'interface_index'],
            registry=self.registry
        )
        
        self.interface_out_errors = Counter(
            'ilnet_interface_out_errors_total',
            'Total outbound errors',
            ['device_id', 'interface_name', 'interface_index'],
            registry=self.registry
        )
        
        self.interface_in_discards = Counter(
            'ilnet_interface_in_discards_total',
            'Total inbound discards',
            ['device_id', 'interface_name', 'interface_index'],
            registry=self.registry
        )
        
        self.interface_out_discards = Counter(
            'ilnet_interface_out_discards_total',
            'Total outbound discards',
            ['device_id', 'interface_name', 'interface_index'],
            registry=self.registry
        )
        
        # Collection metrics
        self.collection_duration_seconds = Histogram(
            'ilnet_collection_duration_seconds',
            'Time taken to collect metrics from device',
            ['device_id'],
            registry=self.registry
        )
        
        self.collection_errors = Counter(
            'ilnet_collection_errors_total',
            'Total collection errors',
            ['device_id', 'error_type'],
            registry=self.registry
        )
        
        logger.info("prometheus_metrics_initialized")
    
    def update_device_metrics(self, device_id: str, device_name: str,
                            host: str, device_data: Dict[str, Any]) -> None:
        """Update device metrics
        
        Args:
            device_id: Device identifier
            device_name: Device name
            host: Device IP/hostname
            device_data: Dictionary with device metrics
        """
        try:
            # Device status
            is_up = 1 if device_data.get('status') == 'up' else 0
            self.device_up.labels(
                device_id=device_id,
                device_name=device_name,
                host=host
            ).set(is_up)
            
            # Device uptime
            if 'uptime' in device_data and device_data['uptime']:
                try:
                    uptime = int(device_data['uptime']) // 100  # Convert to seconds
                    self.device_uptime.labels(
                        device_id=device_id,
                        device_name=device_name
                    ).set(uptime)
                except (ValueError, TypeError):
                    pass
        
        except Exception as e:
            logger.error(
                "update_device_metrics_error",
                device_id=device_id,
                error=str(e)
            )
            self.collection_errors.labels(
                device_id=device_id,
                error_type='device_metrics'
            ).inc()
    
    def update_interface_metrics(self, device_id: str, interface_index: str,
                                interface_data: Dict[str, Any]) -> None:
        """Update interface metrics
        
        Args:
            device_id: Device identifier
            interface_index: Interface index number
            interface_data: Dictionary with interface metrics
        """
        try:
            interface_name = interface_data.get('name', f'eth{interface_index}')
            
            # Interface status
            status = interface_data.get('status', '2')
            is_up = 1 if status == '1' else 0
            self.interface_up.labels(
                device_id=device_id,
                interface_name=interface_name,
                interface_index=interface_index
            ).set(is_up)
            
            # Interface speed
            if 'speed' in interface_data and interface_data['speed']:
                try:
                    speed = int(interface_data['speed'])
                    self.interface_speed.labels(
                        device_id=device_id,
                        interface_name=interface_name,
                        interface_index=interface_index
                    ).set(speed)
                except (ValueError, TypeError):
                    pass
            
            # Traffic metrics
            labels = dict(
                device_id=device_id,
                interface_name=interface_name,
                interface_index=interface_index
            )
            
            try:
                if 'in_octets' in interface_data:
                    self.interface_in_octets.labels(**labels)._value.set(
                        int(interface_data['in_octets'])
                    )
            except (ValueError, TypeError, AttributeError):
                pass
            
            try:
                if 'out_octets' in interface_data:
                    self.interface_out_octets.labels(**labels)._value.set(
                        int(interface_data['out_octets'])
                    )
            except (ValueError, TypeError, AttributeError):
                pass
            
            # Error metrics
            for metric_name in ['in_errors', 'out_errors', 'in_discards', 'out_discards']:
                if metric_name in interface_data and interface_data[metric_name]:
                    try:
                        value = int(interface_data[metric_name])
                        metric = getattr(self, f'interface_{metric_name}')
                        metric.labels(**labels)._value.set(value)
                    except (ValueError, TypeError, AttributeError):
                        pass
        
        except Exception as e:
            logger.error(
                "update_interface_metrics_error",
                device_id=device_id,
                interface_index=interface_index,
                error=str(e)
            )
            self.collection_errors.labels(
                device_id=device_id,
                error_type='interface_metrics'
            ).inc()
    
    def record_collection_time(self, device_id: str, duration: float) -> None:
        """Record metric collection duration
        
        Args:
            device_id: Device identifier
            duration: Time taken in seconds
        """
        self.collection_duration_seconds.labels(
            device_id=device_id
        ).observe(duration)
    
    def get_metrics(self) -> bytes:
        """Get all metrics in Prometheus format
        
        Returns:
            Prometheus format metrics as bytes
        """
        return generate_latest(self.registry)
