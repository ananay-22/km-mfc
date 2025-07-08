"""AD5272 Digital Potentiometer Driver."""

import smbus2
from contextlib import contextmanager
from .base_driver import BaseDriver, HardwareDriverError
from ..config import DigitalPotChannel

class AD5272Driver(BaseDriver):
    """Driver for AD5272 digital potentiometer"""
    
    def __init__(self, config):
        super().__init__(config)
        self._bus = None
    
    @contextmanager
    def _get_bus(self):
        """Context manager for I2C bus access"""
        if self._bus is None:
            self._bus = smbus2.SMBus(self.config.i2c_bus)
        try:
            yield self._bus
        except Exception as e:
            raise HardwareDriverError(f"I2C communication error: {e}")
    
    def select_channel(self, channel: DigitalPotChannel):
        """Select TCA multiplexer channel"""
        chip_address = 2 ** channel.value
        with self._get_bus() as bus:
            bus.write_byte_data(self.config.tca_address, 0, chip_address)
    
    def set_wiper_position(self, position: int):
        """Set the wiper position (0-1023)"""
        if not (0 <= position <= self.config.ad5272_max_steps):
            raise ValueError(f"Position must be between 0 and {self.config.ad5272_max_steps}")
        
        with self._get_bus() as bus:
            # Unlock the resistor
            bus.write_i2c_block_data(self.config.ad5272_address, 0x1c, [0x02])
            
            # Set wiper position
            command_number = 1
            command = [
                (command_number << 2) | ((position >> 8) & 0x03),
                position & 0xff
            ]
            bus.write_i2c_block_data(self.config.ad5272_address, command[0], command[1:])
    
    def read_wiper_position(self) -> int:
        """Read current wiper position"""
        with self._get_bus() as bus:
            wr_msg = smbus2.i2c_msg.write(self.config.ad5272_address, [(0b0010 << 2) | 0, 0])
            rd_msg = smbus2.i2c_msg.read(self.config.ad5272_address, 2)
            bus.i2c_rdwr(wr_msg)
            bus.i2c_rdwr(rd_msg)
            
            data = list(rd_msg)
            return (int(data[0]) << 8) | int(data[1])
    
    def resistance_to_position(self, resistance: float) -> int:
        """Convert resistance value to wiper position"""
        resistance = max(0.0, min(resistance, self.config.ad5272_max_resistance))
        return int(round(self.config.ad5272_max_steps * (resistance / self.config.ad5272_max_resistance)))
    
    def position_to_resistance(self, position: int) -> float:
        """Convert wiper position to resistance value"""
        return (position / self.config.ad5272_max_steps) * self.config.ad5272_max_resistance
    
    def close(self):
        """Clean up resources"""
        if self._bus:
            self._bus.close()
            self._bus = None
