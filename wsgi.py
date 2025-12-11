"""
WSGI Entry Point for Render Deployment
Matches the solution pattern to ensure proper path resolution
"""
import os
import sys

# Add the project directory to the Python path
project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Print for debugging in logs
print(f"WSGI: Updated sys.path: {sys.path[0]}")

# Import the application factory
from app import create_app

# Create the application instance
application = create_app()

if __name__ == "__main__":
    application.run()
