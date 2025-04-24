import os
from openai import OpenAI
from .provider import AIProvider

class OpenAIProvider(AIProvider):
    """AI provider implementation for OpenAI"""
    
    def __init__(self, model="gpt-4o"):
        self.model_name = model
        self.client = None
        
    def initialize(self, api_key):
        """Initialize the OpenAI client with the given API key"""
        self.client = OpenAI(api_key=api_key)
        return True
        
    def generate_content(self, prompt):
        """Generate content using OpenAI API"""
        if not self.client:
            raise RuntimeError("OpenAI provider not initialized. Call initialize() first.")
            
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        
        if not response.choices:
            return None
            
        return response.choices[0].message.content
    
    @property
    def name(self):
        return f"OpenAI ({self.model_name})"