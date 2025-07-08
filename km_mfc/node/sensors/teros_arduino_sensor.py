"""Teros Arduino sensor implementation."""

import time
from .base_sensor import BaseSensor
from ..config import SensorReading
from ..drivers import SerialDriver, HardwareDriverError

class TerosArduinoSensor(BaseSensor):
    """Teros Arduino sensor via serial communication"""
    
    def __init__(self, name: str, config, port_detector_func=None):
        super().__init__(name, config)
        self.serial_driver = SerialDriver(config)
        self.port_detector = port_detector_func
        self._last_port = None
    
    def _verify_connection(self, port: str) -> bool:
        """Verify Arduino connection with handshake"""
        try:
            self.serial_driver.connect(port)
            response = self.serial_driver.send_command(b"S\n")
            return response == "U"
        except Exception as e:
            self.logger.warning(f"Connection verification failed: {e}")
            return False
    
    def _ensure_connection(self):
        """Ensure valid serial connection"""
        if self.port_detector:
            current_port = self.port_detector()
            
            if current_port != self._last_port or not self.serial_driver.is_connected:
                if self._verify_connection(current_port):
                    self._last_port = current_port
                    self.logger.info(f"Connected to Arduino on {current_port}")
                else:
                    raise HardwareDriverError("Arduino handshake failed")
    
    def read(self) -> SensorReading:
        """Read sensor data from Arduino"""
        timestamp = time.time()
        
        try:
            self._ensure_connection()
            
            if not self.serial_driver.is_connected:
                return SensorReading(
                    sensor_name=self.name,
                    timestamp=timestamp,
                    data={'status': 'not_connected'},
                    status="warning",
                    error_message="Serial connection not available"
                )
            
            response = self.serial_driver.send_command(b"R\n")
            
            if not response:
                return SensorReading(
                    sensor_name=self.name,
                    timestamp=timestamp,
                    data={'status': 'no_response'}
                )
            
            # Parse response: elapsed_time,volumetric_water_content,temperature,electric_conductivity
            parts = response.split(',')
            if len(parts) >= 4:
                data = {
                    'elapsed_time': int(parts[0]),
                    'volumetric_water_content': float(parts[1]),
                    'temperature': float(parts[2]),
                    'electric_conductivity': float(parts[3]),
                    'status': 'connected'
                }
            else:
                data = {'raw_response': response, 'status': 'parse_error'}
            
            return SensorReading(
                sensor_name=self.name,
                timestamp=timestamp,
                data=data
            )
        
        except Exception as e:
            return SensorReading(
                sensor_name=self.name,
                timestamp=timestamp,
                data={'status': 'error'},
                status="error",
                error_message=str(e)
            )
    
    def close(self):
        """Clean up resources"""
        self.serial_driver.close()
