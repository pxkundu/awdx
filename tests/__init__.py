"""
AWDX Testing Suite
==================

Comprehensive testing suite for AWDX including:
- Unit tests
- Integration tests 
- Security tests
- Performance tests

Run with: pytest tests/
Security scan: python tests/security_scanner.py
"""

# Import version from main package
try:
    from awdx import __version__, __author__
except ImportError:
    __version__ = "0.0.9-dev"
    __author__ = "Partha Sarathi Kundu" 