"""
Unit tests for the CodeAgent class.
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.code_agent import CodeAgent

class TestCodeAgent(unittest.TestCase):
    """Test cases for the CodeAgent class."""
    
    @patch('agents.code_agent.get_api_key')
    @patch('agents.code_agent.os')
    @patch('agents.code_agent.ChatOpenAI')
    def setUp(self, mock_chat_genai, mock_os, mock_get_api_key):
        """Set up test cases with mocked dependencies."""
        mock_os.getenv.return_value = "fake_api_key"
        mock_get_api_key.return_value = "fake_api_key"
        self.mock_llm = MagicMock()
        mock_chat_genai.return_value = self.mock_llm
        self.agent = CodeAgent()
    
    def test_init(self):
        """Test initialization of CodeAgent."""
        self.assertEqual(self.agent.model_name, "gpt-4o")
        self.assertEqual(self.agent.api_key, "fake_api_key")
    
    def test_initialize_model(self):
        """Test model initialization."""
        # The model is already initialized in setUp, but we can test it again
        self.agent._initialize_model()
        # No need to check for genai.configure since we're using OpenAI now
    
    def test_detect_language_from_request(self):
        """Test language detection from user request."""
        # Test with Python mention
        request = "Can you explain this Python code: ```def hello(): pass```"
        self.assertEqual(self.agent._detect_language_from_request(request), "python")
        
        # Test with JavaScript mention
        request = "Generate JavaScript code for a simple calculator"
        self.assertEqual(self.agent._detect_language_from_request(request), "javascript")
        
        # Test with no language mention
        request = "Generate code for a simple calculator"
        self.assertIsNone(self.agent._detect_language_from_request(request))
    
    @patch('agents.code_agent.CodeAgent._generate_code')
    def test_process_request_generate_code(self, mock_generate_code):
        """Test processing a code generation request."""
        mock_generate_code.return_value = "Generated code here"
        
        result = self.agent.process_request("generate code for a calculator in Python")
        
        mock_generate_code.assert_called_once()
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["response"], "Generated code here")
    
    @patch('agents.code_agent.CodeAgent._explain_code')
    def test_process_request_explain_code(self, mock_explain_code):
        """Test processing a code explanation request."""
        mock_explain_code.return_value = "Code explanation here"
        
        request = """explain this code:
        ```python
        def add(a, b):
            return a + b
        ```"""
        
        result = self.agent.process_request(request)
        
        mock_explain_code.assert_called_once()
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["response"], "Code explanation here")
    
    @patch('agents.code_agent.CodeAgent._review_code')
    def test_process_request_review_code(self, mock_review_code):
        """Test processing a code review request."""
        mock_review_code.return_value = "Code review here"
        
        request = """review this code:
        ```python
        def add(a, b):
            return a + b
        ```"""
        
        result = self.agent.process_request(request)
        
        mock_review_code.assert_called_once()
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["response"], "Code review here")
    
    @patch('agents.code_agent.CodeAgent._refactor_code')
    def test_process_request_refactor_code(self, mock_refactor_code):
        """Test processing a code refactoring request."""
        mock_refactor_code.return_value = "Refactored code here"
        
        request = """refactor this code for better readability:
        ```python
        def add(a, b):
            return a + b
        ```"""
        
        result = self.agent.process_request(request)
        
        mock_refactor_code.assert_called_once()
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["response"], "Refactored code here")
    
    @patch('agents.code_agent.CodeAgent._fix_bug')
    def test_process_request_fix_bug(self, mock_fix_bug):
        """Test processing a bug fixing request."""
        mock_fix_bug.return_value = "Fixed code here"
        
        request = """fix bug in this code:
        ```python
        def divide(a, b):
            return a / b
        ```
        It crashes when b is zero."""
        
        result = self.agent.process_request(request)
        
        mock_fix_bug.assert_called_once()
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["response"], "Fixed code here")
    
    @patch('agents.code_agent.CodeAgent._complete_code')
    def test_process_request_complete_code(self, mock_complete_code):
        """Test processing a code completion request."""
        mock_complete_code.return_value = "Completed code here"
        
        request = """complete this code:
        ```python
        def factorial(n):
            # Implement factorial
        ```"""
        
        result = self.agent.process_request(request)
        
        mock_complete_code.assert_called_once()
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["response"], "Completed code here")

if __name__ == '__main__':
    unittest.main()
