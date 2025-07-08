"""Sensor System Package."""

from .config import HardwareConfig, SensorReading, ADCChannel, DigitalPotChannel
from .sensors import BaseSensor, PCBSensor, TerosArduinoSensor
from .adapters import SensorDataAdapter, LoggingAdapter, QueueAdapter
from .management import SensorManager

__version__ = "1.0.0"
__all__ = [
    'HardwareConfig', 'SensorReading', 'ADCChannel', 'DigitalPotChannel',
    'BaseSensor', 'PCBSensor', 'TerosArduinoSensor',
    'SensorDataAdapter', 'LoggingAdapter', 'QueueAdapter',
    'SensorManager'
]
