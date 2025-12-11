"""
Hypothesis configuration for property-based testing
**Validates: Requirements 5.9**
"""

from hypothesis import settings, Verbosity

# Define profiles for different environments
settings.register_profile("dev", max_examples=20, deadline=None)
settings.register_profile("ci", max_examples=100, deadline=5000, verbosity=Verbosity.verbose)
settings.register_profile("debug", max_examples=10, verbosity=Verbosity.verbose, print_blob=True)

# Load profile from environment or use dev as default
import os
profile = os.getenv("HYPOTHESIS_PROFILE", "dev")
settings.load_profile(profile)
