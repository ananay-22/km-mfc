"""Sensor management system."""

from threading import Thread, Event
from typing import Dict, List
import logging
from ..sensors import BaseSensor
from ..adapters import SensorDataAdapter

class SensorManager:
    """Manages multiple sensors with scheduled reading"""
    
    def __init__(self):
        self.sensors: Dict[str, BaseSensor] = {}
        self.adapters: Dict[str, List[SensorDataAdapter]] = {}
        self.intervals: Dict[str, float] = {}
        self.threads: Dict[str, Thread] = {}
        self.stop_events: Dict[str, Event] = {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def add_sensor(self, sensor: BaseSensor, interval: float, adapters: List[SensorDataAdapter]):
        """Add a sensor with reading interval and data adapters"""
        self.sensors[sensor.name] = sensor
        self.adapters[sensor.name] = adapters
        self.intervals[sensor.name] = interval
        self.logger.info(f"Added sensor '{sensor.name}' with {interval}s interval")
    
    def start_sensor(self, sensor_name: str):
        """Start reading from a specific sensor"""
        if sensor_name not in self.sensors:
            raise ValueError(f"Sensor '{sensor_name}' not found")
        
        if sensor_name in self.threads and self.threads[sensor_name].is_alive():
            self.logger.warning(f"Sensor '{sensor_name}' already running")
            return
        
        stop_event = Event()
        thread = Thread(target=self._sensor_loop, args=(sensor_name, stop_event))
        
        self.stop_events[sensor_name] = stop_event
        self.threads[sensor_name] = thread
        thread.start()
        
        self.logger.info(f"Started reading from sensor '{sensor_name}'")
    
    def stop_sensor(self, sensor_name: str):
        """Stop reading from a specific sensor"""
        if sensor_name in self.stop_events:
            self.stop_events[sensor_name].set()
        
        if sensor_name in self.threads:
            self.threads[sensor_name].join(timeout=5.0)
            del self.threads[sensor_name]
        
        self.logger.info(f"Stopped sensor '{sensor_name}'")
    
    def start_all(self):
        """Start all registered sensors"""
        for sensor_name in self.sensors:
            self.start_sensor(sensor_name)
    
    def stop_all(self):
        """Stop all running sensors"""
        for sensor_name in list(self.threads.keys()):
            self.stop_sensor(sensor_name)
    
    def _sensor_loop(self, sensor_name: str, stop_event: Event):
        """Main sensor reading loop"""
        sensor = self.sensors[sensor_name]
        interval = self.intervals[sensor_name]
        adapters = self.adapters[sensor_name]
        
        while not stop_event.wait(interval):
            try:
                reading = sensor.read()
                
                for adapter in adapters:
                    try:
                        adapter.process_reading(reading)
                    except Exception as e:
                        self.logger.error(f"Adapter error for {sensor_name}: {e}")
                        
            except Exception as e:
                self.logger.error(f"Sensor reading error for {sensor_name}: {e}")
    
    def cleanup(self):
        """Clean up all resources"""
        self.stop_all()
        for sensor in self.sensors.values():
            sensor.close()
        self.sensors.clear()
