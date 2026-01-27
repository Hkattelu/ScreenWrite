import unittest
import sys
import os
import socket
from unittest.mock import patch

def run_tests():
    """Run all tests in the tests directory."""
    # Ensure project root is in path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    
    # Define a guard function to prevent network access
    def network_guard(*args, **kwargs):
        raise RuntimeError("Network access is disabled during tests. Please mock all network calls.")
    
    # Patch socket to prevent any network calls
    with patch('socket.socket', side_effect=network_guard):
        # Discover and run tests
        loader = unittest.TestLoader()
        start_dir = os.path.dirname(__file__)
        suite = loader.discover(start_dir, pattern='test_*.py')
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        sys.exit(not result.wasSuccessful())

if __name__ == '__main__':
    run_tests()
