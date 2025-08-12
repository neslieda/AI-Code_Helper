"""
Configuration utilities for the AI Code Helper.
"""
import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# Load environment variables from .env file
load_dotenv()

def get_api_key(provider: str = "openai") -> Optional[str]:
    """
    Get the API key for the specified provider.
    
    Args:
        provider: The name of the API provider (e.g., 'openai', 'anthropic')
        
    Returns:
        The API key if found, None otherwise
    """
    provider = provider.upper()
    api_key = os.getenv(f"{provider}_API_KEY")
    return api_key

def get_model_config(model_name: str = "gpt-4o") -> Dict[str, Any]:
    """
    Get the configuration for the specified model.
    
    Args:
        model_name: The name of the model to configure
        
    Returns:
        A dictionary containing the model configuration
    """
    # Default configurations for different models
    configs = {
        "gpt-3.5-turbo": {
            "provider": "openai",
            "temperature": 0.7,
            "max_tokens": 1024,
        },
        "gpt-4": {
            "provider": "openai",
            "temperature": 0.7,
            "max_tokens": 2048,
        },
        "gpt-4o": {
            "provider": "openai",
            "temperature": 0.7,
            "max_tokens": 2048,
        },
        # Add configurations for other models as needed
    }
    
    return configs.get(model_name, configs["gpt-3.5-turbo"])
