"""Configuration package for AI Grading System"""

# Import Config from the main settings.py file at root level
import sys
import os
# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import Config class - note this imports from the settings.py file in root
# Users should use: from settings import Config
try:
    # Try importing from parent's settings.py
    import importlib.util
    spec = importlib.util.spec_from_file_location("root_config",
                                                    os.path.join(os.path.dirname(__file__), "..", "settings.py"))
    if spec and spec.loader:
        root_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(root_config)
        Config = root_config.Config
except Exception:
    # Fallback: Config might not be available in test environment
    Config = None

# This allows imports like: from config.security_config import ...
# Without conflicting with pytest's config module
__all__ = ['Config', 'logging_config', 'rate_limit_config', 'security_config']


