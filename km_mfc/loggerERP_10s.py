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

"""This version of logger can switch between open and closed circuit based on
the two time interval constants below"""

# CIRCUIT CONTROLS
OPEN_CIRCUIT_INTERVAL = 10  # seconds
CLOSED_CIRCUIT_INTERVAL = 10  # seconds
ITERATIONS = 20  # number of open/closed cycles
current_mode = "open"  # Tracks the current mode for tagging

def set_open_circuit(gpio_pins):
    global current_mode
    for pin in gpio_pins:
        GPIO.output(pin, GPIO.LOW)  # LOW = open circuit
    current_mode = "open"
    print("Switched to OPEN circuit")


def set_closed_circuit(gpio_pins):
    global current_mode
    for pin in gpio_pins:
        GPIO.output(pin, GPIO.HIGH)  # HIGH = closed circuit
    current_mode = "closed"
    print("Switched to CLOSED circuit")


def data_processor(data_queue: queue.Queue):
    """Process sensor data from queue"""
    while True:
        try:
            reading = data_queue.get(timeout=1.0)

            # Add mode info to reading dictionary
            reading_dict = reading.to_dict()
            reading_dict["circuit_mode"] = current_mode

            # Process the reading (e.g., save to database, send to cloud, etc.)
            print(f"Processing: {reading.sensor_name} at {reading.timestamp} ({current_mode})")

            output_dir = "logs"
            os.makedirs(output_dir, exist_ok=True)

            filename = os.path.join(output_dir, f"KMM1_ERP_10s.json")
            with open(filename, "a") as f:
                json.dump(reading_dict, f)
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

    # Create data queue and adapters
    data_queue = queue.Queue(maxsize=1000)
    logger_adapter = LoggingAdapter()
    queue_adapter = QueueAdapter(data_queue)

    # Initialize sensors
    pcb_sensor = PCBSensor("pcb_main", config)
    arduino_sensor = TerosArduinoSensor("teros_main", config, get_current_serial_device)

    # Initialize sensor manager and add sensors
    manager = SensorManager()
    manager.add_sensor(pcb_sensor, interval=.1, adapters=[logger_adapter, queue_adapter])
    manager.add_sensor(arduino_sensor, interval=300, adapters=[logger_adapter, queue_adapter])

    try:
        # Start data processor thread
        from threading import Thread
        processor_thread = Thread(target=data_processor, args=(data_queue,))
        processor_thread.daemon = True
        processor_thread.start()

        # Start all sensors
        manager.start_all()

        # Set resistance BEFORE touching GPIO
        resistance = 4900
        pcb_sensor.set_resistance(DigitalPotChannel.AD0, resistance)
        print(f"Set resistance to {resistance}Ω")

        # Toggle GPIO Pins
        GPIO.setmode(GPIO.BCM)
        gpio_pins = [23, 24, 25, 5]
        for pin in gpio_pins:
            GPIO.setup(pin, GPIO.OUT)

        # Start in open circuit mode
        set_open_circuit(gpio_pins)

        # Toggle loop for a fixed number of iterations
        for i in range(ITERATIONS):
            print(f"--- Iteration {i+1}/{ITERATIONS} ---")
            time.sleep(OPEN_CIRCUIT_INTERVAL)
            set_closed_circuit(gpio_pins)
            time.sleep(CLOSED_CIRCUIT_INTERVAL)
            set_open_circuit(gpio_pins)

        print("Finished toggling. Final state: OPEN circuit.")

    except KeyboardInterrupt:
        print("Shutting down...")

    finally:
        manager.cleanup()
        GPIO.cleanup()


if __name__ == "__main__":
    main()
