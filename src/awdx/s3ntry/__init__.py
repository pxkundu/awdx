"""
S3ntry - AWS S3 Security and Compliance Module

A comprehensive S3 security module for AWDX with real-world DevSecOps use cases.
Provides commands for S3 bucket security assessment, compliance validation, data protection,
access control analysis, and automated remediation with intelligent security insights.
"""

from .s3_commands import s3_app

__all__ = ["s3_app"]
