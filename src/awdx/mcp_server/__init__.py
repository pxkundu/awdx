"""
AWDX MCP Server - Model Context Protocol Integration

This module provides MCP server capabilities for AWDX, enabling AI assistants
to interact with AWS DevSecOps tools through a standardized protocol.

Key Features:
    - Expose AWDX modules as MCP tools
    - Real-time AWS data access
    - Integration with external AI assistants
    - Standardized tool calling interface
    - Security and authentication handling

Version: 1.0.0
Author: AWDX Team
License: MIT
"""

import logging
from typing import Optional

# Package version
__version__ = "1.0.0"

# Setup module-level logger
logger = logging.getLogger(__name__)

# MCP server components
from .server import AWDXMCPServer
from .tools import (
    AWDXToolRegistry,
    ProfileTool,
    CostTool,
    IAMTool,
    S3Tool,
    SecretTool,
    SecurityTool,
)

# Public API exports
__all__ = [
    "AWDXMCPServer",
    "AWDXToolRegistry",
    "ProfileTool",
    "CostTool", 
    "IAMTool",
    "S3Tool",
    "SecretTool",
    "SecurityTool",
    "__version__",
]


def create_mcp_server(
    config_path: Optional[str] = None,
    enable_all_tools: bool = True,
    **kwargs
) -> AWDXMCPServer:
    """
    Factory function to create a configured MCP server instance.

    Args:
        config_path: Optional path to AWDX configuration file
        enable_all_tools: Whether to enable all AWDX tools by default
        **kwargs: Additional server configuration options

    Returns:
        AWDXMCPServer: Configured MCP server instance
    """
    return AWDXMCPServer(
        config_path=config_path,
        enable_all_tools=enable_all_tools,
        **kwargs
    )


def run_mcp_server(
    host: str = "localhost",
    port: int = 3000,
    config_path: Optional[str] = None,
    **kwargs
) -> None:
    """
    Run the AWDX MCP server.

    Args:
        host: Server host address
        port: Server port number
        config_path: Optional path to configuration file
        **kwargs: Additional server options
    """
    server = create_mcp_server(config_path=config_path, **kwargs)
    server.run(host=host, port=port) 