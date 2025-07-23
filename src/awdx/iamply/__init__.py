"""
IAMply - AWS IAM Management Module

A comprehensive IAM management module for AWDX with real-world DevSecOps use cases.
Provides commands for IAM user, role, policy, and access management with security best practices.
"""

from .iam_commands import iam_app

__all__ = ["iam_app"]
