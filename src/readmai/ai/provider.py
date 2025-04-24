from abc import ABC, abstractmethod

class AIProvider(ABC):
    """Abstract base class for AI providers"""
    
    @abstractmethod
    def initialize(self, api_key):
        """Initialize the AI provider with the given API key"""
        pass
    
    @abstractmethod
    def generate_content(self, prompt):
        """Generate content based on the given prompt
        
        Returns:
            str: The generated content
        """
        pass
    
    @property
    @abstractmethod
    def name(self):
        """Get the name of the AI provider"""
        pass