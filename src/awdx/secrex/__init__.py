"""
Secrex - AWS Secret Management and Rotation Module

A comprehensive secret management module for AWDX with real-world DevSecOps use cases.
Provides commands for secret discovery, rotation, monitoring, and automated management
with intelligent security insights and compliance features.
"""

from .secret_commands import secret_app

__all__ = ["secret_app"]
