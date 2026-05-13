"""Device Manager for managing SNMP devices"""

import json
from pathlib import Path
from typing import List, Dict, Optional
import structlog
from src.config import config
from src.snmp_collector.snmp_manager import SNMPManager

logger = structlog.get_logger(__name__)


class DeviceManager:
    """Manage network devices configuration and communication"""
    
    def __init__(self, config_file: Path = None):
        """Initialize Device Manager
        
        Args:
            config_file: Path to devices configuration JSON file
        """
        self.config_file = config_file or config.DEVICES_CONFIG
        self.devices = {}
        self.snmp_managers = {}
        self.load_devices()
    
    def load_devices(self) -> None:
        """Load devices from configuration file"""
        if not self.config_file.exists():
            logger.warning(
                "device_config_not_found",
                path=str(self.config_file)
            )
            return
        
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                self.devices = data.get('devices', {})
            
            logger.info(
                "devices_loaded",
                count=len(self.devices)
            )
            
            # Initialize SNMP managers for each device
            for device_id, device_info in self.devices.items():
                self.snmp_managers[device_id] = SNMPManager(
                    host=device_info.get('host'),
                    community=device_info.get('community'),
                    version=device_info.get('version')
                )
        
        except Exception as e:
            logger.error(
                "device_config_error",
                path=str(self.config_file),
                error=str(e)
            )
    
    def save_devices(self) -> None:
        """Save devices to configuration file"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump({'devices': self.devices}, f, indent=2)
            logger.info("devices_saved", count=len(self.devices))
        except Exception as e:
            logger.error(
                "device_save_error",
                path=str(self.config_file),
                error=str(e)
            )
    
    def add_device(self, device_id: str, host: str, name: str,
                   community: str = 'public', device_type: str = 'router',
                   tags: List[str] = None) -> bool:
        """Add a new device
        
        Args:
            device_id: Unique device identifier
            host: Device IP address or hostname
            name: Device name/description
            community: SNMP community string
            device_type: Type of device (router, switch, etc.)
            tags: List of tags for the device
            
        Returns:
            True if successful, False otherwise
        """
        if device_id in self.devices:
            logger.warning(
                "device_already_exists",
                device_id=device_id
            )
            return False
        
        self.devices[device_id] = {
            'host': host,
            'name': name,
            'community': community,
            'version': '2c',
            'device_type': device_type,
            'tags': tags or [],
            'enabled': True,
        }
        
        # Initialize SNMP manager
        self.snmp_managers[device_id] = SNMPManager(
            host=host,
            community=community
        )
        
        self.save_devices()
        logger.info(
            "device_added",
            device_id=device_id,
            host=host
        )
        return True
    
    def remove_device(self, device_id: str) -> bool:
        """Remove a device
        
        Args:
            device_id: Device identifier
            
        Returns:
            True if successful, False otherwise
        """
        if device_id not in self.devices:
            logger.warning(
                "device_not_found",
                device_id=device_id
            )
            return False
        
        del self.devices[device_id]
        if device_id in self.snmp_managers:
            del self.snmp_managers[device_id]
        
        self.save_devices()
        logger.info("device_removed", device_id=device_id)
        return True
    
    def get_device(self, device_id: str) -> Optional[Dict]:
        """Get device information
        
        Args:
            device_id: Device identifier
            
        Returns:
            Device configuration dictionary or None
        """
        return self.devices.get(device_id)
    
    def get_all_devices(self) -> Dict:
        """Get all devices
        
        Returns:
            Dictionary of all devices
        """
        return self.devices
    
    def get_snmp_manager(self, device_id: str) -> Optional[SNMPManager]:
        """Get SNMP manager for device
        
        Args:
            device_id: Device identifier
            
        Returns:
            SNMPManager instance or None
        """
        return self.snmp_managers.get(device_id)
    
    def test_device_connection(self, device_id: str) -> bool:
        """Test connection to a device
        
        Args:
            device_id: Device identifier
            
        Returns:
            True if connection successful, False otherwise
        """
        manager = self.get_snmp_manager(device_id)
        if not manager:
            logger.warning(
                "device_not_found",
                device_id=device_id
            )
            return False
        
        return manager.test_connection()
    
    def test_all_connections(self) -> Dict[str, bool]:
        """Test connection to all devices
        
        Returns:
            Dictionary of device_id -> connection_status
        """
        results = {}
        for device_id in self.devices.keys():
            results[device_id] = self.test_device_connection(device_id)
        return results
