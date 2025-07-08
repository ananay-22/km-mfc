"""Logging adapter for sensor data."""

import logging
import json
from typing import Optional
from .base_adapter import SensorDataAdapter
from ..config import SensorReading

class LoggingAdapter(SensorDataAdapter):
    """Simple logging adapter"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(self.__class__.__name__)
    
    def process_reading(self, reading: SensorReading):
        if reading.status == "success":
            self.logger.info(f"{reading.sensor_name}: {json.dumps(reading.data, indent=2)}")
        else:
            self.logger.error(f"{reading.sensor_name} error: {reading.error_message}")
