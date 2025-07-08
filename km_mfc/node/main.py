"""Main entry point for the sensor system."""

import argparse
import logging
import sys
from sensor_system.examples.basic_usage import main as basic_main
from sensor_system.examples.advanced_usage import main as advanced_main

def main():
    parser = argparse.ArgumentParser(description="Sensor System")
    parser.add_argument(
        "--mode", 
        choices=["basic", "advanced"], 
        default="basic",
        help="Run mode (basic or advanced)"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        if args.mode == "basic":
            basic_main()
        else:
            advanced_main()
    except Exception as e:
        logging.error(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
