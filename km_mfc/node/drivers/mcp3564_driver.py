"""MCP3564 ADC Driver."""

import spidev
import time
from contextlib import contextmanager
from typing import Optional
from .base_driver import BaseDriver, HardwareDriverError

class MCP3564Driver(BaseDriver):
    """Driver for MCP3564 ADC"""
    
    # Register definitions
    REGISTERS = {
        'ADCDATA': 0x00, 'CONFIG0': 0x01, 'CONFIG1': 0x02, 'CONFIG2': 0x03,
        'CONFIG3': 0x04, 'IRQ': 0x05, 'MUX': 0x06, 'SCAN': 0x07,
        'TIMER': 0x08, 'OFFSETCAL': 0x09, 'GAINCAL': 0x0a, 'LOCK': 0x0d,
        'CRCCFG': 0x0f
    }
    
    def __init__(self, config):
        super().__init__(config)
        self._spi = None
        self._current_cs = None
        self._initialized = False
    
    def _make_command(self, addr: int, rw: str) -> int:
        """Create SPI command byte"""
        chip_addr = 1
        rw_bits = {'r': 3, 'w': 2}.get(rw, 1)
        return ((chip_addr << 6) | (addr & 0x0f) << 2) | rw_bits
    
    @contextmanager
    def _get_spi(self, cs_pin: int):
        """Context manager for SPI access"""
        if self._spi is None or self._current_cs != cs_pin:
            if self._spi:
                self._spi.close()
            
            self._spi = spidev.SpiDev()
            self._spi.open(self.config.spi_bus, cs_pin)
            self._spi.max_speed_hz = self.config.spi_max_speed
            self._spi.mode = 0
            self._current_cs = cs_pin
            self._initialized = False
        
        if not self._initialized:
            self._initialize_adc()
            self._initialized = True
        
        try:
            yield self._spi
        except Exception as e:
            raise HardwareDriverError(f"SPI communication error: {e}")
    
    def _initialize_adc(self):
        """Initialize the MCP3564 ADC"""
        if not self._spi:
            return
        
        # Read LOCK register for sanity check
        self._spi.xfer([self._make_command(self.REGISTERS['LOCK'], 'r'), 0])
        
        # Configure ADC
        configs = [
            # CONFIG0: internal oscillator, no current bias, ADC in standby
            (self.REGISTERS['CONFIG0'], (0b10 << 4) | (0b10 << 0)),
            # CONFIG1: AMCLK = MCLK/2, oversample = 1024
            (self.REGISTERS['CONFIG1'], (0b01 << 6) | (0b0101 << 2)),
            # CONFIG3: one-shot mode, 24-bit format, offset/gaincal enabled
            (self.REGISTERS['CONFIG3'], (0b10 << 6) | (0b00 << 4) | (1 << 0)),
            # IRQ: enable IRQ pin
            (self.REGISTERS['IRQ'], (0b01 << 2) | (1 << 1) | (1 << 0))
        ]
        
        for reg, value in configs:
            self._spi.xfer([self._make_command(reg, 'w'), value])
        
        # Set gain calibration
        self._spi.xfer([self._make_command(self.REGISTERS['GAINCAL'], 'w'), 0x7c, 0xab, 0xd8])
    
    def read_channel_raw(self, cs_pin: int, channel: int) -> Optional[bytes]:
        """Read raw ADC data from specified channel"""
        with self._get_spi(cs_pin) as spi:
            # Setup MUX
            chan_p = (2 * channel) & 0x0f
            chan_n = (chan_p + 1) & 0x0f
            spi.xfer([self._make_command(self.REGISTERS['MUX'], 'w'), (chan_p << 4) | chan_n])
            
            # Start conversion
            spi.xfer([(1 << 6) | (0b1010 << 2)])
            
            # Poll for completion
            start_time = time.monotonic()
            while True:
                result = spi.xfer([self._make_command(self.REGISTERS['IRQ'], 'r'), 0])
                if not (result[1] & (1 << 6)):
                    break
                
                if (time.monotonic() - start_time) > self.config.mcp3564_timeout:
                    return None
                
                time.sleep(0.001)
            
            # Read data
            result = spi.xfer([self._make_command(self.REGISTERS['ADCDATA'], 'r'), 0, 0, 0])
            return bytes(result[1:])
    
    def raw_to_voltage(self, raw_data: bytes, gain: float = 1.0, vref: Optional[float] = None) -> float:
        """Convert raw ADC data to voltage"""
        if vref is None:
            vref = self.config.mcp3564_vref
        
        # Convert 24-bit two's complement
        value = int.from_bytes(raw_data, byteorder='big', signed=False)
        if value & 0x800000:  # Sign bit set
            value -= 0x1000000
        
        return vref * (value / 8388608) / gain
    
    def close(self):
        """Clean up resources"""
        if self._spi:
            self._spi.close()
            self._spi = None
