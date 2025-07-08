"""Base sensor class."""

from abc import ABC, abstractmethod
import logging
from ..config import HardwareConfig, SensorReading

class BaseSensor(ABC):
    """Abstract base class for all sensors"""
    
    def __init__(self, name: str, config: HardwareConfig):
        self.name = name
        self.config = config
        self.logger = logging.getLogger(f"{self.__class__.__name__}.{name}")
    
    @abstractmethod
    def read(self) -> SensorReading:
        """Read sensor data"""
        pass
    
    @abstractmethod
    def close(self):
        """Clean up resources"""
        pass
