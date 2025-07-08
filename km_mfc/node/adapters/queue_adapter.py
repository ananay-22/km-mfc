"""Queue adapter for sensor data."""

import queue
import logging
from .base_adapter import SensorDataAdapter
from ..config import SensorReading

class QueueAdapter(SensorDataAdapter):
    """Queue-based adapter for async processing"""
    
    def __init__(self, data_queue: queue.Queue):
        self.queue = data_queue
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def process_reading(self, reading: SensorReading):
        try:
            self.queue.put_nowait(reading)
        except queue.Full:
            self.logger.warning(f"Data queue full, dropping reading from {reading.sensor_name}")
