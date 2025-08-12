"""
Unit tests for config module.
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.config import get_api_key, get_model_config

class TestConfig(unittest.TestCase):
    """Test cases for configuration functions."""
    
    @patch('utils.config.os')
    def test_get_api_key(self, mock_os):
        """Test retrieving API key from environment variables."""
        # Test when API key exists
        mock_os.getenv.return_value = "test_api_key"
        self.assertEqual(get_api_key(), "test_api_key")
        mock_os.getenv.assert_called_with("OPENAI_API_KEY")
        
        # Test with different provider
        mock_os.getenv.return_value = "google_api_key"
        self.assertEqual(get_api_key("google"), "google_api_key")
        mock_os.getenv.assert_called_with("GOOGLE_API_KEY")
        
        # Test when API key doesn't exist
        mock_os.getenv.return_value = None
        self.assertIsNone(get_api_key())
    
    def test_get_model_config(self):
        """Test retrieving model configuration."""
        # Test with default model name (gpt-4o)
        config = get_model_config()
        self.assertEqual(config["provider"], "openai")
        self.assertEqual(config["temperature"], 0.7)
        self.assertEqual(config["max_tokens"], 2048)
        
        # Test with specific model name (gpt-4o)
        config = get_model_config("gpt-4o")
        self.assertEqual(config["provider"], "openai")
        self.assertEqual(config["temperature"], 0.7)
        self.assertEqual(config["max_tokens"], 2048)
        
        # Test with unknown model name (should return default config)
        config = get_model_config("unknown-model")
        self.assertEqual(config["provider"], "openai")
        self.assertEqual(config["temperature"], 0.7)
        self.assertEqual(config["max_tokens"], 1024)

if __name__ == '__main__':
    unittest.main()
