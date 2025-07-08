"""Serial communication driver."""

import serial
import time
from .base_driver import BaseDriver, HardwareDriverError

class SerialDriver(BaseDriver):
    """Driver for serial communication"""
    
    def __init__(self, config):
        super().__init__(config)
        self._connection = None
        self._port = None
    
    def connect(self, port: str):
        """Connect to serial port"""
        if self._port == port and self._connection and self._connection.is_open:
            return
        
        self.disconnect()
        
        try:
            self._connection = serial.Serial(
                port, 
                self.config.serial_baudrate, 
                timeout=self.config.serial_timeout
            )
            time.sleep(2)  # Allow time for connection
            self._connection.reset_input_buffer()
            self._connection.reset_output_buffer()
            self._port = port
        except Exception as e:
            raise HardwareDriverError(f"Serial connection error: {e}")
    
    def send_command(self, command: bytes) -> str:
        """Send command and read response"""
        if not self._connection or not self._connection.is_open:
            raise HardwareDriverError("Serial connection not established")
        
        self._connection.write(command)
        response = self._connection.readline().decode('utf-8').strip()
        return response
    
    def disconnect(self):
        """Disconnect from serial port"""
        if self._connection and self._connection.is_open:
            self._connection.close()
        self._connection = None
        self._port = None
    
    @property
    def is_connected(self) -> bool:
        """Check if serial connection is active"""
        return self._connection and self._connection.is_open
    
    def close(self):
        """Clean up resources"""
        self.disconnect()
