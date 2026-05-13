"""SNMP Manager for device communication"""

import json
from typing import Dict, List, Optional, Tuple, Any
from pysnmp.hlapi import (
    getCmd,
    nextCmd,
    SnmpEngine,
    CommunityData,
    UdpTransportTarget,
    ObjectType,
    ObjectIdentity,
    ContextData,
)
from pysnmp.proto import rfc1155
import structlog
from src.config import config
from pathlib import Path

logger = structlog.get_logger(__name__)


class SNMPManager:
    """Manager for SNMP device communication"""
    
    # Common OIDs
    OID_SYSUPTIME = '1.3.6.1.2.1.1.3.0'  # System uptime
    OID_SYSNAME = '1.3.6.1.2.1.1.5.0'    # System name
    OID_SYSDESCR = '1.3.6.1.2.1.1.1.0'   # System description
    OID_IFNAME = '1.3.6.1.2.1.2.2.1.2'   # Interface name
    OID_IFTYPE = '1.3.6.1.2.1.2.2.1.3'   # Interface type
    OID_IFSPEED = '1.3.6.1.2.1.2.2.1.5'  # Interface speed
    OID_IFSTATUS = '1.3.6.1.2.1.2.2.1.8' # Interface status (1=up, 2=down)
    OID_IFINOCTETS = '1.3.6.1.2.1.2.2.1.10'      # Inbound octets
    OID_IFOUTOCTETS = '1.3.6.1.2.1.2.2.1.16'     # Outbound octets
    OID_IFINERRORS = '1.3.6.1.2.1.2.2.1.14'      # Inbound errors
    OID_IFOUTERRORS = '1.3.6.1.2.1.2.2.1.20'     # Outbound errors
    OID_IFINDISCARDS = '1.3.6.1.2.1.2.2.1.13'    # Inbound discards
    OID_IFOUTDISCARDS = '1.3.6.1.2.1.2.2.1.19'   # Outbound discards
    
    def __init__(self, host: str, community: str = None, version: str = None,
                 timeout: int = None, retries: int = None):
        """Initialize SNMP Manager
        
        Args:
            host: Device hostname or IP
            community: SNMP community string
            version: SNMP version (2c or 3)
            timeout: SNMP timeout in seconds
            retries: Number of retries
        """
        self.host = host
        self.community = community or config.SNMP_COMMUNITY
        self.version = version or config.SNMP_VERSION
        self.timeout = timeout or config.SNMP_TIMEOUT
        self.retries = retries or config.SNMP_RETRIES
        self.port = config.SNMP_PORT
        self.engine = SnmpEngine()
        
    def get(self, oid: str) -> Optional[Any]:
        """Get a single OID value
        
        Args:
            oid: Object Identifier
            
        Returns:
            Value of the OID or None if error
        """
        try:
            error_indication, error_status, error_index, var_binds = next(
                getCmd(
                    self.engine,
                    CommunityData(self.community, mpModel=1),
                    UdpTransportTarget(
                        (self.host, self.port),
                        timeout=self.timeout,
                        retries=self.retries
                    ),
                    ContextData(),
                    ObjectType(ObjectIdentity(oid))
                )
            )
            
            if error_indication:
                logger.error(
                    "snmp_get_error",
                    host=self.host,
                    oid=oid,
                    error=str(error_indication)
                )
                return None
                
            if error_status:
                logger.warning(
                    "snmp_error_status",
                    host=self.host,
                    oid=oid,
                    status=error_status.prettyPrint()
                )
                return None
                
            if var_binds:
                return var_binds[0][1].prettyPrint()
                
        except Exception as e:
            logger.error(
                "snmp_get_exception",
                host=self.host,
                oid=oid,
                error=str(e)
            )
        return None
    
    def walk(self, oid: str) -> List[Tuple[str, str]]:
        """Walk an OID tree
        
        Args:
            oid: Starting OID
            
        Returns:
            List of (OID, value) tuples
        """
        results = []
        try:
            for error_indication, error_status, error_index, var_binds in nextCmd(
                self.engine,
                CommunityData(self.community, mpModel=1),
                UdpTransportTarget(
                    (self.host, self.port),
                    timeout=self.timeout,
                    retries=self.retries
                ),
                ContextData(),
                ObjectType(ObjectIdentity(oid))
            ):
                if error_indication:
                    logger.error(
                        "snmp_walk_error",
                        host=self.host,
                        oid=oid,
                        error=str(error_indication)
                    )
                    break
                    
                if error_status:
                    logger.warning(
                        "snmp_walk_status",
                        host=self.host,
                        status=error_status.prettyPrint()
                    )
                    break
                    
                for obj_name, obj_val in var_binds:
                    results.append((
                        str(obj_name),
                        obj_val.prettyPrint()
                    ))
                    
        except Exception as e:
            logger.error(
                "snmp_walk_exception",
                host=self.host,
                oid=oid,
                error=str(e)
            )
        
        return results
    
    def get_system_info(self) -> Dict[str, str]:
        """Get system information
        
        Returns:
            Dictionary with system info
        """
        return {
            'hostname': self.get(self.OID_SYSNAME),
            'description': self.get(self.OID_SYSDESCR),
            'uptime': self.get(self.OID_SYSUPTIME),
        }
    
    def get_interfaces(self) -> Dict[str, Dict]:
        """Get interface information
        
        Returns:
            Dictionary of interfaces with their details
        """
        interfaces = {}
        
        # Get interface names
        if_names = self.walk(self.OID_IFNAME)
        
        for oid, name in if_names:
            # Extract interface index from OID
            if_index = oid.split('.')[-1]
            
            interfaces[if_index] = {
                'name': name,
                'type': self.get(f'{self.OID_IFTYPE}.{if_index}'),
                'speed': self.get(f'{self.OID_IFSPEED}.{if_index}'),
                'status': self.get(f'{self.OID_IFSTATUS}.{if_index}'),
                'in_octets': self.get(f'{self.OID_IFINOCTETS}.{if_index}'),
                'out_octets': self.get(f'{self.OID_IFOUTOCTETS}.{if_index}'),
                'in_errors': self.get(f'{self.OID_IFINERRORS}.{if_index}'),
                'out_errors': self.get(f'{self.OID_IFOUTERRORS}.{if_index}'),
                'in_discards': self.get(f'{self.OID_IFINDISCARDS}.{if_index}'),
                'out_discards': self.get(f'{self.OID_IFOUTDISCARDS}.{if_index}'),
            }
        
        return interfaces
    
    def test_connection(self) -> bool:
        """Test SNMP connectivity
        
        Returns:
            True if connection successful, False otherwise
        """
        sysname = self.get(self.OID_SYSNAME)
        is_connected = sysname is not None
        
        if is_connected:
            logger.info(
                "snmp_connection_success",
                host=self.host,
                sysname=sysname
            )
        else:
            logger.warning(
                "snmp_connection_failed",
                host=self.host
            )
        
        return is_connected
