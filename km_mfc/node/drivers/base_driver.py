"""Base driver classes and exceptions."""

from abc import ABC, abstractmethod

class HardwareDriverError(Exception):
    """Base exception for hardware driver errors"""
    pass

class BaseDriver(ABC):
    """Abstract base class for hardware drivers"""
    
    def __init__(self, config):
        self.config = config
    
    @abstractmethod
    def close(self):
        """Clean up resources"""
        pass
