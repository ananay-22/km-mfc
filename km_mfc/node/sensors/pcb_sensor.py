"""PCB sensor implementation."""

import time
from typing import Dict, Any, Optional
from .base_sensor import BaseSensor
from ..config import SensorReading, ADCChannel, DigitalPotChannel
from ..drivers import MCP3564Driver, AD5272Driver

class PCBSensor(BaseSensor):
    """PCB sensor with ADC and digital potentiometer control"""
    
    def __init__(self, name: str, config):
        super().__init__(name, config)
        self.adc_driver = MCP3564Driver(config)
        self.pot_driver = AD5272Driver(config)
        self._last_adc_channel = None
    
    def set_resistance(self, channel: DigitalPotChannel, resistance: float):
        """Set digital potentiometer resistance"""
        try:
            self.pot_driver.select_channel(channel)
            position = self.pot_driver.resistance_to_position(resistance)
            self.pot_driver.set_wiper_position(position)
            self.logger.info(f"Set channel {channel.name} to {resistance}Ω (position {position})")
        except Exception as e:
            self.logger.error(f"Failed to set resistance: {e}")
            raise
    
    def read_adc_channel(self, adc_channel: ADCChannel, channel_num: int) -> Optional[Dict[str, Any]]:
        """Read specific ADC channel"""
        try:
            cs_pin = adc_channel.value
            raw_data = self.adc_driver.read_channel_raw(cs_pin, channel_num)
            
            if raw_data is None:
                return None
            
            voltage = self.adc_driver.raw_to_voltage(raw_data, vref=5.3)  # Custom VREF
            raw_int = int.from_bytes(raw_data, byteorder='big')
            
            return {
                'voltage': voltage,
                'raw_value': raw_int,
                'channel': channel_num,
                'adc': adc_channel.name
            }
        except Exception as e:
            self.logger.error(f"ADC read error: {e}")
            return None
    
    def read(self) -> SensorReading:
        """Read all sensor data"""
        timestamp = time.time()
        data = {}
        
        try:
            # Read voltage and current from both ADC channels
            for adc_channel in ADCChannel:
                adc_data = {}
                
                # Read voltage (channel 1) and current (channel 0)
                voltage_data = self.read_adc_channel(adc_channel, 1)
                current_data = self.read_adc_channel(adc_channel, 0)
                
                voltage_data2 = self.read_adc_channel(adc_channel, 3)
                current_data2 = self.read_adc_channel(adc_channel, 2)
                
                if voltage_data:
                    adc_data['voltage 1'] = voltage_data
                if current_data:
                    adc_data['current 1'] = current_data
                    
                if voltage_data2:
                    adc_data['voltage 2'] = voltage_data2
                if current_data2:
                    adc_data['current 2'] = current_data2
                
                data[adc_channel.name] = adc_data
            
            return SensorReading(
                sensor_name=self.name,
                timestamp=timestamp,
                data=data
            )
        
        except Exception as e:
            return SensorReading(
                sensor_name=self.name,
                timestamp=timestamp,
                data={},
                status="error",
                error_message=str(e)
            )
    
    def close(self):
        """Clean up resources"""
        self.adc_driver.close()
        self.pot_driver.close()
