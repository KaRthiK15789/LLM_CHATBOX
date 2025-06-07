import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class Config:
    """Central configuration management"""
    
    # Application settings
    MAX_FILE_SIZE_MB = 5
    ALLOWED_FILE_TYPES = ['.xlsx', '.xls']
    DEFAULT_CHART_THEME = 'plotly_white'
    
    # OpenAI settings
    OPENAI_SETTINGS = {
        'api_key': os.getenv('OPENAI_API_KEY'),
        'model': 'gpt-3.5-turbo',
        'temperature': 0.3,
        'max_tokens': 500
    }
    
    # Visualization settings
    CHART_CONFIG = {
        'colors': {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'background': '#f8f9fa'
        },
        'font': {
            'family': 'Arial',
            'size': 12,
            'color': '#333333'
        }
    }
    
    @classmethod
    def validate(cls):
        """Validate critical configurations"""
        if not cls.OPENAI_SETTINGS['api_key']:
            print("Warning: OpenAI API key not found. Some features may be limited.")
        
        if cls.MAX_FILE_SIZE_MB > 10:
            raise ValueError("MAX_FILE_SIZE_MB exceeds safety limit")

    @classmethod
    def get_logging_config(cls):
        """Return logging configuration"""
        return {
            'level': os.getenv('LOG_LEVEL', 'INFO'),
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }

# Validate configurations on load
Config.validate()
