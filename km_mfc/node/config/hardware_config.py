"""Hardware configuration management for sensor system."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any
import json

class ADCChannel(Enum):
    """ADC channel enumeration"""
    ADC0 = 0
    ADC1 = 1

class DigitalPotChannel(Enum):
    """Digital potentiometer channel enumeration"""
    AD0 = 0
    AD1 = 1
    AD2 = 2
    AD3 = 3

@dataclass
class HardwareConfig:
    """Centralized hardware configuration"""
    # I2C Configuration
    i2c_bus: int = 1
    tca_address: int = 0x70
    ad5272_address: int = 0x2c
    
    # SPI Configuration
    spi_bus: int = 0
    spi_max_speed: int = 1000000
    
    # AD5272 Digital Potentiometer
    ad5272_max_resistance: float = 100000.0
    ad5272_max_steps: int = 1023
    
    # MCP3564 ADC
    mcp3564_vref: float = 3.32
    mcp3564_timeout: float = 0.01
    
    # Serial Configuration
    serial_baudrate: int = 9600
    serial_timeout: float = 1.0
    
    @classmethod
    def from_json(cls, json_path: str) -> 'HardwareConfig':
        """Load configuration from JSON file"""
        with open(json_path, 'r') as f:
            data = json.load(f)
        return cls(**data)
    
    def to_json(self, json_path: str):
        """Save configuration to JSON file"""
        with open(json_path, 'w') as f:
            json.dump(self.__dict__, f, indent=2)

@dataclass
class SensorReading:
    """Standardized sensor reading format"""
    sensor_name: str
    timestamp: float
    data: Dict[str, Any]
    status: str = "success"
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'sensor_name': self.sensor_name,
            'timestamp': self.timestamp,
            'data': self.data,
            'status': self.status,
            'error_message': self.error_message
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SensorReading':
        """Create from dictionary"""
        return cls(**data)
