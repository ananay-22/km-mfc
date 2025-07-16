"""Advanced usage example with data processing."""

import logging
import queue
import time
import json
from node.config import HardwareConfig, DigitalPotChannel
from node.sensors import PCBSensor, TerosArduinoSensor
from node.adapters import LoggingAdapter, QueueAdapter
from node.management import SensorManager
from node.utils import get_current_serial_device

def data_processor(data_queue: queue.Queue):
    """Process sensor data from queue"""
    while True:
        try:
            reading = data_queue.get(timeout=1.0)
            
            # Process the reading (e.g., save to database, send to cloud, etc.)
            print(f"Processing: {reading.sensor_name} at {reading.timestamp}")
            
            # Example processing - save to file
            with open(f"sensor_data_{reading.sensor_name}.json", "a") as f:
                json.dump(reading.to_dict(), f)
                f.write('\n')
                
        except queue.Empty:
            continue
        except Exception as e:
            print(f"Data processing error: {e}")

def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create configuration
    config = HardwareConfig()
    
    # Create data queue
    data_queue = queue.Queue(maxsize=1000)
    
    # Create adapters
    logger_adapter = LoggingAdapter()
    queue_adapter = QueueAdapter(data_queue)
    
    # Create sensors
    pcb_sensor = PCBSensor("pcb_main", config)
    arduino_sensor = TerosArduinoSensor("teros_main", config, get_current_serial_device)
    
    # Create sensor manager
    manager = SensorManager()
    
    # Add sensors with multiple adapters
    manager.add_sensor(pcb_sensor, interval=0.5, adapters=[logger_adapter, queue_adapter])
    manager.add_sensor(arduino_sensor, interval=1.0, adapters=[logger_adapter])
    
    try:
        # Start data processor in separate thread
        from threading import Thread
        processor_thread = Thread(target=data_processor, args=(data_queue,))
        processor_thread.daemon = True
        processor_thread.start()
        
        # Start all sensors
        manager.start_all()
        
        # Example: Set different resistances over time
        resistances = [10000, 25000, 50000, 75000, 100000]  # Different resistance values
        
        for i, resistance in enumerate(resistances):
            pcb_sensor.set_resistance(DigitalPotChannel.AD0, resistance)
            print(f"Set resistance to {resistance}Ω")
            time.sleep(10)  # Wait 10 seconds between changes
        
        # Continue running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        manager.cleanup()

if __name__ == "__main__":
    main()
