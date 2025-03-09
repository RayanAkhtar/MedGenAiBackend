import os
import sys
import pytest

def run_tests():
    """Run all tests and report results."""
    print("Running backend API tests...")
    
    # Run tests and capture the result
    result = pytest.main(['-v', 'tests/test_routes.py'])
    
    if result == 0:
        print("\n✅ All tests passed successfully!")
    else:
        print("\n❌ Some tests failed. See details above.")
    
    return result

if __name__ == "__main__":
    sys.exit(run_tests()) 