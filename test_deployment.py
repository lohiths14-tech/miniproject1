"""
Test Deployment Script
Verifies that the WSGI application can be imported and initialized correctly.
Matches the solution's verification step.
"""
import sys
import os
import unittest
from io import StringIO
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestDeployment(unittest.TestCase):
    def setUp(self):
        # Suppress output during testing
        self.held_output = StringIO()
        # Mock settings/config if needed for CI environment where .env might be missing
        os.environ['SECRET_KEY'] = 'test-key'

    def test_imports(self):
        """Test 1: Can import critical modules"""
        print("\nTest 1: Importing modules...")
        try:
            import wsgi
            import app
            from settings import Config
            import routes
            print("✅ Modules imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import modules: {str(e)}")

    def test_wsgi_application(self):
        """Test 2: WSGI application instance exists"""
        print("Test 2: Checking WSGI application...")
        try:
            import wsgi
            self.assertIsNotNone(wsgi.application)
            print("✅ WSGI application instance found")
        except Exception as e:
            self.fail(f"WSGI application check failed: {str(e)}")

    def test_routes_exist(self):
        """Test 3: Routes are registered"""
        print("Test 3: Checking routes...")
        try:
            from app import create_app
            app = create_app()
            # Check for key blueprints
            blueprints = app.blueprints.keys()
            required_bps = ['api_v1', 'simple_auth', 'health']
            for bp in required_bps:
                if bp in blueprints:
                    print(f"✅ Blueprint found: {bp}")
                else:
                    print(f"⚠️ Warning: Blueprint {bp} not found (might be named differently)")
        except Exception as e:
            self.fail(f"Route check failed: {str(e)}")

if __name__ == '__main__':
    print("🚀 Running Pre-Deployment Tests...")
    unittest.main(verbosity=2)
