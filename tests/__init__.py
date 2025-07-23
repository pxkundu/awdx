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
    from awdx import __author__, __version__
except ImportError:
    __version__ = "0.0.11-dev"
    __author__ = "Partha Sarathi Kundu"
