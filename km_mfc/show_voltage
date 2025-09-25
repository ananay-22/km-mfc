import logging
import time
import RPi.GPIO as GPIO
from node.config import HardwareConfig, DigitalPotChannel
from node.sensors import PCBSensor, TerosArduinoSensor
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

    # Initialize sensors
    pcb_sensor = PCBSensor("pcb_main", config)
    arduino_sensor = TerosArduinoSensor("teros_main", config, get_current_serial_device)

    # Initialize sensor manager and add sensors
    manager = SensorManager()
    manager.add_sensor(pcb_sensor, interval=300.0, adapters=[])
    manager.add_sensor(arduino_sensor, interval=300.0, adapters=[])

    try:
        # Start all sensors
        manager.start_all()

        # Set resistance BEFORE touching GPIO
        resistance = 24900
        pcb_sensor.set_resistance(DigitalPotChannel.AD0, resistance)
        print(f"Set resistance to {resistance}Ω (open circuit)")

        # Now safely toggle GPIO pins
        GPIO.setmode(GPIO.BCM)
        gpio_pins = [23, 24, 25, 5]

        for pin in gpio_pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
            print(f"GPIO {pin} set to LOW")

        # --- Show one snapshot of PCB data ---
        reading = pcb_sensor.read()
        print(f"Voltage: {reading.voltage:.3f} V | Current: {reading.current:.6f} A")

    except KeyboardInterrupt:
        print("Shutting down...")

    finally:
        manager.cleanup()
        GPIO.cleanup()


if __name__ == "__main__":

    main()
