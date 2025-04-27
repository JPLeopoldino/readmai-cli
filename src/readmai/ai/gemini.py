import google.generativeai as genai
from .provider import AIProvider

class GeminiProvider(AIProvider):
    """AI provider implementation for Google's Gemini"""
    
    def __init__(self, model="gemini-2.0-flash"):
        self.model_name = model
        self.model = None
        
    def initialize(self, api_key):
        """Initialize the Gemini API with the given API key"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(self.model_name)
        return True
        
    def generate_content(self, prompt):
        """Generate content using Gemini API"""
        if not self.model:
            raise RuntimeError("Gemini provider not initialized. Call initialize() first.")
            
        response = self.model.generate_content(prompt)
        
        if not response.parts:
            return None
            
        return response.text
    
    @property
    def name(self):
        return f"Gemini ({self.model_name})"