"""
Script to run all tests for the AI Code Helper project.
"""
import sys
import unittest
import pytest

if __name__ == '__main__':
    print("Running unit tests for AI Code Helper...")
    
    # Option 1: Run tests with unittest
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Exit with proper code based on test results
    sys.exit(not result.wasSuccessful())
    
    # Option 2: Uncomment to run tests with pytest instead
    # sys.exit(pytest.main(['-v', 'tests']))
