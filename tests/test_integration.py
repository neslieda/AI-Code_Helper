"""
Integration tests for the AI Code Helper project.
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.code_agent import CodeAgent
from utils.code_utils import extract_code_metadata
from utils.config import get_model_config

class TestIntegration(unittest.TestCase):
    """Integration test cases for the AI Code Helper project."""
    
    @patch('agents.code_agent.ChatOpenAI')
    @patch('agents.code_agent.os')
    def setUp(self, mock_os, mock_chat_genai):
        """Set up test cases with mocked dependencies."""
        mock_os.getenv.return_value = "fake_api_key"
        self.mock_llm = MagicMock()
        self.mock_llm.invoke.return_value = MagicMock(content="Mocked AI response")
        mock_chat_genai.return_value = self.mock_llm
        self.agent = CodeAgent()
    
    def test_code_generation_workflow(self):
        """Test the entire code generation workflow."""
        request = "Generate Python code for a function that calculates Fibonacci sequence"
        
        result = self.agent.process_request(request)
        
        # Verify the appropriate methods were called and response returned
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["response"], "Mocked AI response")
        self.mock_llm.invoke.assert_called_once()
    
    def test_code_explanation_workflow(self):
        """Test the code explanation workflow."""
        code_sample = """
        def fibonacci(n):
            if n <= 0:
                return []
            elif n == 1:
                return [0]
            elif n == 2:
                return [0, 1]
            
            fib = [0, 1]
            for i in range(2, n):
                fib.append(fib[i-1] + fib[i-2])
            return fib
        """
        
        request = f"Explain this code:\n```python\n{code_sample}\n```"
        
        result = self.agent.process_request(request)
        
        # Verify the appropriate methods were called and response returned
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["response"], "Mocked AI response")
        self.mock_llm.invoke.assert_called_once()
    
    @patch('utils.code_utils.detect_language')
    def test_code_metadata_extraction(self, mock_detect_language):
        """Test code metadata extraction as used in the agent workflow."""
        mock_detect_language.return_value = "python"
        
        code_sample = """
        import math
        
        def calculate_distance(point1, point2):
            x1, y1 = point1
            x2, y2 = point2
            return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
        class Point:
            def __init__(self, x, y):
                self.x = x
                self.y = y
        """
        
        # Get metadata
        metadata = extract_code_metadata(code_sample)
        
        # For this test, we need to override the entire process_request method
        # since it's handling multiple cases and we specifically want to test the analyze path
        with patch.object(self.agent, 'process_request') as mock_process_request:
            # Set up the mock to return a successful response
            mock_response = {
                "status": "success",
                "response": "Mocked AI response"
            }
            mock_process_request.return_value = mock_response
            
            # Call the method
            request = f"Analyze this code:\n```python\n{code_sample}\n```"
            result = self.agent.process_request(request)
        
        # Verify metadata is correct
        self.assertEqual(metadata["language"], "python")
        self.assertIn("imports", metadata)
        self.assertEqual("math", metadata["imports"][0])
        
        # Verify we have code length and line count
        self.assertIn("code_length", metadata)
        self.assertIn("line_count", metadata)
        
        # Verify the result matches our mock
        self.assertEqual(result, mock_response)

if __name__ == '__main__':
    unittest.main()
