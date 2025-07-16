"""Basic usage example."""

import logging
import time
from node.config import HardwareConfig, DigitalPotChannel
from node.sensors import PCBSensor, TerosArduinoSensor
from node.adapters import LoggingAdapter
from node.management import SensorManager
from node.utils import get_current_serial_device

def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create configuration
    config = HardwareConfig()
    
    # Create adapters
    logger_adapter = LoggingAdapter()
    
    # Create sensors
    pcb_sensor = PCBSensor("pcb_main", config)
    arduino_sensor = TerosArduinoSensor("teros_main", config, get_current_serial_device)
    
    # Create sensor manager
    manager = SensorManager()
    
    # Add sensors
    manager.add_sensor(pcb_sensor, interval=0.5, adapters=[logger_adapter])
    manager.add_sensor(arduino_sensor, interval=1.0, adapters=[logger_adapter])
    
    try:
        # Start all sensors
        manager.start_all()
        
        # Example: Set resistance on PCB sensor
        pcb_sensor.set_resistance(DigitalPotChannel.AD0, 50000.0)  # 50kΩ
        
        # Run for 30 seconds
        time.sleep(30)
        
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        manager.cleanup()

if __name__ == "__main__":
    main()
