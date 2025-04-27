import os
from openai import OpenAI
from .provider import AIProvider

class OpenAIProvider(AIProvider):
    """AI provider implementation for OpenAI"""
    
    def __init__(self, model="gpt-4.1-mini"):
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
        
        try:    
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            
            if not response.choices:
                return None
                
            return response.choices[0].message.content
            
        except Exception as e:
            error_message = str(e).lower()
            
            # Handle quota or rate limit errors
            if 'rate limit' in error_message or 'too many requests' in error_message:
                error_msg = (
                    f"OpenAI rate limit reached. Please try again later or use a different "
                    f"provider with the --provider flag. Details: {str(e)}"
                )
                raise RuntimeError(error_msg) from e
                
            # Handle quota errors
            elif 'quota' in error_message or 'insufficient_quota' in error_message:
                error_msg = (
                    "OpenAI API quota exceeded. Please check your billing details at "
                    "https://platform.openai.com/account/billing or use a different provider "
                    "with the --provider flag."
                )
                raise RuntimeError(error_msg) from e
                
            # Handle authentication errors
            elif 'auth' in error_message or 'api key' in error_message:
                error_msg = "Invalid OpenAI API key. Please check your API key and try again."
                raise RuntimeError(error_msg) from e
                
            # Handle connection errors
            elif 'connection' in error_message or 'network' in error_message:
                error_msg = (
                    "Connection to OpenAI failed. Please check your internet connection "
                    "or try again later."
                )
                raise RuntimeError(error_msg) from e
                
            # General error handling
            else:
                error_msg = f"OpenAI API error: {str(e)}. Try using a different model or provider."
                raise RuntimeError(error_msg) from e
    
    @property
    def name(self):
        return f"OpenAI ({self.model_name})"