"""Base adapter class."""

from abc import ABC, abstractmethod
from ..config import SensorReading

class SensorDataAdapter(ABC):
    """Abstract adapter for sensor data processing"""
    
    @abstractmethod
    def process_reading(self, reading: SensorReading):
        """Process a sensor reading"""
        pass
