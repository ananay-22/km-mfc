"""Serial port utilities."""

import serial.tools.list_ports
from typing import Optional

def find_arduino_port() -> Optional[str]:
    """Find Arduino port automatically"""
    ports = serial.tools.list_ports.comports()
    
    for port in ports:
        if 'Arduino' in port.description or 'USB' in port.description:
            return port.device
    
    return None

def get_current_serial_device() -> Optional[str]:
    """Get current serial device - placeholder implementation"""
    return find_arduino_port()
