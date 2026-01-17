#!/usr/bin/env python3
"""
Test runner for vid-orchestrator end-to-end integration tests.

This script runs the comprehensive end-to-end integration test suite
that validates the complete workflow from markdown script to FCPXML output.
"""

import sys
import unittest
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_tests():
    """Run the end-to-end integration tests."""
    # Discover and run tests
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code based on test results
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_tests())