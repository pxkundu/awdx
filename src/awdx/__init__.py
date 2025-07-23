"""
AWDX - AWS DevOps X
Gen AI-powered AWS DevSecOps CLI tool with natural language interface.

Copyright (c) 2024 Partha Sarathi Kundu

Licensed under the MIT License. See LICENSE file in the project root for details.
Author: Partha Sarathi Kundu <inboxkundu@gmail.com>
GitHub: https://github.com/pxkundu/awdx

This software is developed independently and is not affiliated with any organization.
"""

import sys
import traceback
from typing import Any, Dict, Optional

import typer
from botocore.exceptions import ClientError, NoCredentialsError, ProfileNotFound

# Version information
try:
    import importlib.metadata
    __version__ = importlib.metadata.version("awdx")
except ImportError:
    __version__ = "0.0.15"  # Fallback version
__author__ = "AWDX Team"
__description__ = "AWS DevSecOps CLI Tool for Security, Cost, and Compliance Management"
__homepage__ = "https://github.com/pxkundu/awdx"


# Error handling and user feedback system
class AWDXErrorHandler:
    """Centralized error handling and user feedback system."""

    @staticmethod
    def handle_aws_error(
        error: Exception, context: str = "", profile: Optional[str] = None
    ) -> None:
        """Handle AWS-specific errors with user-friendly messages and suggestions."""

        if isinstance(error, NoCredentialsError):
            typer.echo(f"❌ No AWS credentials found!")
            typer.echo(
                f"💡 Please configure your AWS credentials using one of these methods:"
            )
            typer.echo(f"   • AWS CLI: aws configure")
            typer.echo(
                f"   • Environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY"
            )
            typer.echo(f"   • IAM roles (if running on EC2)")
            typer.echo(f"   • AWS SSO: aws configure sso")

        elif isinstance(error, ProfileNotFound):
            typer.echo(f"❌ AWS profile '{profile}' not found!")
            typer.echo(f"💡 Available profiles:")
            try:
                import boto3

                session = boto3.Session()
                profiles = session.available_profiles
                for prof in profiles:
                    typer.echo(f"   • {prof}")
            except:
                typer.echo(f"   • default")
            typer.echo(
                f"💡 Use 'aws configure --profile <name>' to create a new profile"
            )

        elif isinstance(error, ClientError):
            error_code = error.response["Error"]["Code"]
            error_message = error.response["Error"]["Message"]

            typer.echo(f"❌ AWS API Error ({error_code}): {error_message}")

            # Provide specific guidance based on error codes
            if error_code == "AccessDeniedException":
                typer.echo(f"💡 This appears to be a permissions issue. Please check:")
                typer.echo(f"   • Your IAM user/role has the necessary permissions")
                typer.echo(f"   • The service is enabled in your AWS account")
                typer.echo(f"   • You're using the correct AWS profile/region")

            elif error_code == "InvalidParameterValue":
                typer.echo(f"💡 Parameter validation failed. Please check:")
                typer.echo(f"   • Required parameters are provided")
                typer.echo(f"   • Parameter values are in the correct format")
                typer.echo(f"   • Parameter values are within valid ranges")

            elif error_code == "ValidationException":
                typer.echo(f"💡 Request validation failed. Please check:")
                typer.echo(f"   • All required fields are provided")
                typer.echo(f"   • Field values meet AWS requirements")
                typer.echo(f"   • Resource names follow AWS naming conventions")

            elif error_code == "ServiceUnavailable":
                typer.echo(f"💡 AWS service is temporarily unavailable. Please:")
                typer.echo(f"   • Try again in a few minutes")
                typer.echo(f"   • Check AWS Service Health Dashboard")
                typer.echo(f"   • Contact AWS Support if the issue persists")

            elif error_code == "ThrottlingException":
                typer.echo(f"💡 Request rate limit exceeded. Please:")
                typer.echo(f"   • Wait a moment and try again")
                typer.echo(f"   • Reduce the frequency of requests")
                typer.echo(f"   • Consider using pagination for large datasets")

            else:
                typer.echo(f"💡 For more help, check:")
                typer.echo(f"   • AWS documentation for {error_code}")
                typer.echo(f"   • AWS Support if this is a persistent issue")
                typer.echo(f"   • AWDX documentation and examples")

        elif "sso-session does not exist" in str(error):
            # Handle SSO session errors specifically
            typer.echo(f"❌ AWS SSO Session Error: {str(error)}")
            typer.echo(f"💡 This is a configuration issue. Please check:")
            typer.echo(f"   • Your AWS SSO session is properly configured")
            typer.echo(f"   • Run 'aws configure sso' to set up SSO")
            typer.echo(f"   • Check your ~/.aws/config file for SSO session settings")
            typer.echo(f"   • Try 'aws sso login' to refresh your SSO session")
            typer.echo(
                f"   • Use a different AWS profile: awdx cost trends --profile default"
            )

        elif "NoCredentialsError" in str(
            error
        ) or "Unable to locate credentials" in str(error):
            typer.echo(f"❌ No AWS credentials found!")
            typer.echo(
                f"💡 Please configure your AWS credentials using one of these methods:"
            )
            typer.echo(f"   • AWS CLI: aws configure")
            typer.echo(
                f"   • Environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY"
            )
            typer.echo(f"   • IAM roles (if running on EC2)")
            typer.echo(f"   • AWS SSO: aws configure sso")
            typer.echo(f"   • Use a different profile: --profile <profile-name>")

        else:
            # Generic error handling
            typer.echo(f"❌ Unexpected error: {str(error)}")
            typer.echo(f"💡 This might be a bug in AWDX. Please:")
            typer.echo(f"   • Check if you're using the latest version")
            typer.echo(f"   • Report this issue to the AWDX developers")
            typer.echo(f"   • Include the full error message and context")

    @staticmethod
    def suggest_github_issue(error: Exception, context: str = "") -> None:
        """Suggest creating a GitHub issue for bugs."""
        typer.echo()
        typer.echo(f"🐛 This appears to be a bug in AWDX.")
        typer.echo(f"💡 Would you like to report this issue to help improve AWDX?")

        if typer.confirm("Create GitHub issue for this bug?"):
            typer.echo(
                f"📝 Please create an issue at: https://github.com/awdx/awdx/issues"
            )
            typer.echo(f"📋 Include the following information:")
            typer.echo(f"   • AWDX version: {__version__}")
            typer.echo(f"   • Command that caused the error")
            typer.echo(f"   • Full error message")
            typer.echo(f"   • Your AWS region and profile (if applicable)")
            typer.echo(f"   • Steps to reproduce the issue")

    @staticmethod
    def handle_configuration_error(error: str, suggestion: str = "") -> None:
        """Handle configuration-related errors."""
        typer.echo(f"⚙️ Configuration Error: {error}")
        if suggestion:
            typer.echo(f"💡 {suggestion}")

    @staticmethod
    def handle_network_error(error: Exception) -> None:
        """Handle network-related errors."""
        typer.echo(f"🌐 Network Error: Unable to connect to AWS services")
        typer.echo(f"💡 Please check:")
        typer.echo(f"   • Your internet connection")
        typer.echo(f"   • AWS service availability")
        typer.echo(f"   • Firewall/proxy settings")
        typer.echo(f"   • VPN connection (if applicable)")


def handle_exceptions(func):
    """Decorator to handle exceptions gracefully."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            AWDXErrorHandler.handle_aws_error(e)
            AWDXErrorHandler.suggest_github_issue(e)
            raise typer.Exit(1)

    return wrapper


# Export the error handler for use in other modules
__all__ = [
    "AWDXErrorHandler",
    "handle_exceptions",
    "__version__",
    "__author__",
    "__description__",
    "__homepage__",
]
