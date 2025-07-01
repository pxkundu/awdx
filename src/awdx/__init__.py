"""
AWDX - AWS DevOps X
Gen AI-powered AWS DevSecOps CLI tool with natural language interface.

Copyright (c) 2024 Partha Sarathi Kundu

Licensed under the MIT License. See LICENSE file in the project root for details.
Author: Partha Sarathi Kundu <pxkundu2@shockers.wichita.edu>
GitHub: https://github.com/pxkundu/awdx
"""

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    # Python < 3.8 fallback
    from importlib_metadata import version, PackageNotFoundError

def get_version() -> str:
    """
    Get the current AWDX version dynamically from package metadata.
    
    Returns:
        str: Version string (e.g., "0.0.9")
    """
    try:
        return version("awdx")
    except PackageNotFoundError:
        # Fallback for development/testing when package isn't installed
        return "0.0.9-dev"

__version__ = get_version()
__author__ = "Partha Sarathi Kundu"
__email__ = "pxkundu2@shockers.wichita.edu"
__homepage__ = "https://github.com/pxkundu/awdx" 