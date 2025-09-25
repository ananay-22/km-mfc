"""Used for experiments to see if pcb current data is accurate"""

import os
import logging
import queue
import time
import json
import RPi.GPIO as GPIO
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

    # Create data queue and adapters
    data_queue = queue.Queue(maxsize=1000)
    logger_adapter = LoggingAdapter()
    queue_adapter = QueueAdapter(data_queue)

    # Initialize sensors
    pcb_sensor = PCBSensor("pcb_main", config)
    arduino_sensor = TerosArduinoSensor("teros_main", config, get_current_serial_device)

    # Initialize sensor manager and add sensors
    manager = SensorManager()
    manager.add_sensor(pcb_sensor, interval=300.0, adapters=[logger_adapter, queue_adapter])
    manager.add_sensor(arduino_sensor, interval=300.0, adapters=[logger_adapter, queue_adapter])

    try:
        # Start data processor thread
        from threading import Thread
        processor_thread = Thread(target=data_processor, args=(data_queue,))
        processor_thread.daemon = True
        processor_thread.start()

        # Start all sensors
        manager.start_all()

        # Set resistance BEFORE touching GPIO
        resistance = 24900
        pcb_sensor.set_resistance(DigitalPotChannel.AD0, resistance)
        print(f"Set resistance to {resistance}Ω")

        # Now safely toggle GPIO pins
        GPIO.setmode(GPIO.BCM)
        gpio_pins = [23, 24, 25, 5]

        for pin in gpio_pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
            print(f"GPIO {pin} set to LOW")

        # Keep running
        while False:
            time.sleep(1)

    except KeyboardInterrupt:
        print("Shutting down...")

    finally:
        manager.cleanup()
        GPIO.cleanup()



if __name__ == "__main__":

    main()


if __name__ == "__main__":

    main()
