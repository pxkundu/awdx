"""
AWDX MCP Server Implementation

This module implements the main MCP server for AWDX, providing a standardized
interface for AI assistants to interact with AWS DevSecOps capabilities.
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..ai_engine import get_nlp_processor, initialize_ai_engine
from ..ai_engine.config_manager import AIConfig
from .tools import AWDXToolRegistry

logger = logging.getLogger(__name__)
console = Console()


class AWDXMCPServer:
    """
    AWDX MCP Server for exposing AWS DevSecOps capabilities to AI assistants.
    
    This server implements the Model Context Protocol to allow AI assistants
    to interact with AWDX modules through a standardized interface.
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        enable_all_tools: bool = True,
        ai_enabled: bool = True,
        verbose: bool = False,
        **kwargs
    ):
        """
        Initialize the AWDX MCP server.

        Args:
            config_path: Path to AWDX configuration file
            enable_all_tools: Whether to enable all AWDX tools
            ai_enabled: Whether to enable AI capabilities
            **kwargs: Additional configuration options
        """
        self.config_path = config_path
        self.enable_all_tools = enable_all_tools
        self.ai_enabled = ai_enabled
        self.verbose = verbose
        
        # Set up logging level
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)
            logger.setLevel(logging.DEBUG)
        
        # Initialize tool registry
        self.tool_registry = AWDXToolRegistry()
        
        # AI components
        self.nlp_processor = None
        self.ai_config = None
        
        # Server state
        self.is_running = False
        self.clients: List[Dict[str, Any]] = []
        
        # Initialize components
        self._initialize_components()

    def _initialize_components(self) -> None:
        """Initialize server components."""
        try:
            # Load AI configuration if enabled
            if self.ai_enabled:
                self.ai_config = AIConfig.load_from_file(self.config_path)
                if initialize_ai_engine(self.config_path):
                    self.nlp_processor = get_nlp_processor()
                    logger.info("AI engine initialized for MCP server")
                else:
                    logger.warning("AI engine initialization failed, continuing without AI")
                    self.ai_enabled = False

            # Register AWDX tools
            self._register_tools()
            
            logger.info("AWDX MCP server components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP server components: {e}")
            raise

    def _register_tools(self) -> None:
        """Register AWDX tools with the MCP server."""
        try:
            # Register all AWDX module tools
            self.tool_registry.register_profile_tools()
            self.tool_registry.register_cost_tools()
            self.tool_registry.register_iam_tools()
            self.tool_registry.register_s3_tools()
            self.tool_registry.register_secret_tools()
            self.tool_registry.register_security_tools()
            
            # Register Phase 2 service-specific tools
            self.tool_registry.register_phase2_tools()
            
            # Register Phase 3 infrastructure automation tools
            self.tool_registry.register_phase3_tools()
            
            # Register AI-specific tools if available
            if self.ai_enabled and self.nlp_processor:
                self.tool_registry.register_ai_tools(self.nlp_processor)
            
            logger.info(f"Registered {len(self.tool_registry.get_tools())} MCP tools")
            
        except Exception as e:
            logger.error(f"Failed to register tools: {e}")
            raise

    async def handle_client_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """Handle client connection and MCP protocol communication."""
        client_id = id(writer)
        client_info = {
            "id": client_id,
            "reader": reader,
            "writer": writer,
            "address": writer.get_extra_info("peername")
        }
        
        self.clients.append(client_info)
        logger.info(f"New client connected: {client_info['address']}")
        
        try:
            await self._handle_mcp_protocol(reader, writer, client_id)
        except Exception as e:
            logger.error(f"Error handling client {client_id}: {e}")
        finally:
            self.clients = [c for c in self.clients if c["id"] != client_id]
            writer.close()
            await writer.wait_closed()
            logger.info(f"Client {client_id} disconnected")

    async def _handle_mcp_protocol(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, client_id: int) -> None:
        """Handle MCP protocol messages."""
        while True:
            try:
                # Read message length (4 bytes)
                length_bytes = await reader.read(4)
                if not length_bytes:
                    logger.debug("Client disconnected - no length bytes")
                    break
                
                message_length = int.from_bytes(length_bytes, byteorder="big")
                logger.debug(f"Received message of length: {message_length}")
                
                # Read message content
                message_data = await reader.read(message_length)
                if not message_data:
                    logger.debug("Client disconnected - no message data")
                    break
                
                # Decode message data
                message_text = message_data.decode("utf-8")
                if not message_text.strip():
                    logger.debug("Received empty message, skipping")
                    continue
                
                # Parse JSON message
                try:
                    message = json.loads(message_text)
                    logger.debug(f"Received MCP message: {message.get('method', 'unknown')}")
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON received: {e}")
                    logger.debug(f"Raw message: {repr(message_text)}")
                    continue
                
                # Handle MCP message
                response = await self._process_mcp_message(message, client_id)
                
                # Send response
                if response:
                    response_data = json.dumps(response).encode("utf-8")
                    response_length = len(response_data).to_bytes(4, byteorder="big")
                    writer.write(response_length + response_data)
                    await writer.drain()
                    logger.debug(f"Sent response for method: {message.get('method', 'unknown')}")
                    
            except asyncio.CancelledError:
                logger.debug("Connection cancelled")
                break
            except Exception as e:
                logger.error(f"Error processing MCP message: {e}")
                # Send error response
                try:
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": message.get("id") if "message" in locals() else None,
                        "error": {
                            "code": -32603,
                            "message": "Internal error",
                            "data": str(e)
                        }
                    }
                    response_data = json.dumps(error_response).encode("utf-8")
                    response_length = len(response_data).to_bytes(4, byteorder="big")
                    writer.write(response_length + response_data)
                    await writer.drain()
                except Exception as send_error:
                    logger.error(f"Failed to send error response: {send_error}")
                    break

    async def _process_mcp_message(self, message: Dict[str, Any], client_id: int) -> Optional[Dict[str, Any]]:
        """Process MCP protocol message and return response."""
        method = message.get("method")
        message_id = message.get("id")
        params = message.get("params", {})
        
        logger.debug(f"Processing MCP message: {method}")
        
        try:
            if method == "initialize":
                return await self._handle_initialize(params, message_id)
            elif method == "tools/list":
                return await self._handle_tools_list(params, message_id)
            elif method == "tools/call":
                return await self._handle_tools_call(params, message_id)
            elif method == "textDocument/read":
                return await self._handle_text_document_read(params, message_id)
            elif method == "textDocument/query":
                return await self._handle_text_document_query(params, message_id)
            elif method == "resources/list":
                return await self._handle_resources_list(params, message_id)
            elif method == "resources/read":
                return await self._handle_resources_read(params, message_id)
            else:
                logger.warning(f"Unknown MCP method: {method}")
                return {
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
                
        except Exception as e:
            logger.error(f"Error processing MCP method {method}: {e}")
            return {
                "jsonrpc": "2.0",
                "id": message_id,
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": str(e)
                }
            }

    async def _handle_initialize(self, params: Dict[str, Any], message_id: Any) -> Dict[str, Any]:
        """Handle MCP initialize request."""
        return {
            "jsonrpc": "2.0",
            "id": message_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {
                        "subscribes": True
                    },
                    "textDocument": {
                        "subscribes": True
                    }
                },
                "serverInfo": {
                    "name": "AWDX MCP Server",
                    "version": "1.0.0",
                    "description": "AWS DevSecOps tools for AI assistants"
                }
            }
        }

    async def _handle_tools_list(self, params: Dict[str, Any], message_id: Any) -> Dict[str, Any]:
        """Handle MCP tools/list request."""
        tools = self.tool_registry.get_tools()
        return {
            "jsonrpc": "2.0",
            "id": message_id,
            "result": {
                "tools": tools
            }
        }

    async def _handle_tools_call(self, params: Dict[str, Any], message_id: Any) -> Dict[str, Any]:
        """Handle MCP tools/call request."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        try:
            result = await self.tool_registry.call_tool(tool_name, arguments)
            return {
                "jsonrpc": "2.0",
                "id": message_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": message_id,
                "error": {
                    "code": -32603,
                    "message": f"Tool execution failed: {str(e)}"
                }
            }

    async def _handle_text_document_read(self, params: Dict[str, Any], message_id: Any) -> Dict[str, Any]:
        """Handle MCP textDocument/read request."""
        uri = params.get("uri")
        
        # For AWDX, this could return configuration files, logs, or reports
        try:
            content = await self._read_document_content(uri)
            return {
                "jsonrpc": "2.0",
                "id": message_id,
                "result": {
                    "contents": [
                        {
                            "uri": uri,
                            "text": content
                        }
                    ]
                }
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": message_id,
                "error": {
                    "code": -32603,
                    "message": f"Failed to read document: {str(e)}"
                }
            }

    async def _handle_text_document_query(self, params: Dict[str, Any], message_id: Any) -> Dict[str, Any]:
        """Handle MCP textDocument/query request."""
        # This could be used for querying AWS resources or AWDX data
        return {
            "jsonrpc": "2.0",
            "id": message_id,
            "result": {
                "items": []
            }
        }

    async def _handle_resources_list(self, params: Dict[str, Any], message_id: Any) -> Dict[str, Any]:
        """Handle MCP resources/list request."""
        # List available AWS resources or AWDX data sources
        resources = await self._list_available_resources()
        return {
            "jsonrpc": "2.0",
            "id": message_id,
            "result": {
                "resources": resources
            }
        }

    async def _handle_resources_read(self, params: Dict[str, Any], message_id: Any) -> Dict[str, Any]:
        """Handle MCP resources/read request."""
        uri = params.get("uri")
        
        try:
            content = await self._read_resource_content(uri)
            return {
                "jsonrpc": "2.0",
                "id": message_id,
                "result": {
                    "contents": [
                        {
                            "uri": uri,
                            "text": content
                        }
                    ]
                }
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": message_id,
                "error": {
                    "code": -32603,
                    "message": f"Failed to read resource: {str(e)}"
                }
            }

    async def _read_document_content(self, uri: str) -> str:
        """Read document content based on URI."""
        # Implementation for reading various document types
        if uri.startswith("awdx://config"):
            # Return AWDX configuration
            return "AWDX Configuration Content"
        elif uri.startswith("awdx://logs"):
            # Return AWDX logs
            return "AWDX Log Content"
        else:
            raise ValueError(f"Unsupported document URI: {uri}")

    async def _list_available_resources(self) -> List[Dict[str, Any]]:
        """List available resources."""
        return [
            {
                "uri": "awdx://config",
                "name": "AWDX Configuration",
                "description": "Current AWDX configuration"
            },
            {
                "uri": "awdx://logs",
                "name": "AWDX Logs", 
                "description": "AWDX application logs"
            }
        ]

    async def _read_resource_content(self, uri: str) -> str:
        """Read resource content based on URI."""
        return await self._read_document_content(uri)

    async def start_server(self, host: str = "localhost", port: int = 3000) -> None:
        """Start the MCP server."""
        server = await asyncio.start_server(
            self.handle_client_connection,
            host,
            port
        )
        
        self.is_running = True
        logger.info(f"AWDX MCP server started on {host}:{port}")
        
        async with server:
            await server.serve_forever()

    def run(self, host: str = "localhost", port: int = 3000) -> None:
        """Run the MCP server (blocking)."""
        try:
            asyncio.run(self.start_server(host, port))
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Server error: {e}")
        finally:
            self.is_running = False

    def get_status(self) -> Dict[str, Any]:
        """Get server status information."""
        return {
            "running": self.is_running,
            "ai_enabled": self.ai_enabled,
            "tools_registered": len(self.tool_registry.get_tools()),
            "connected_clients": len(self.clients),
            "version": "1.0.0"
        }


def main():
    """CLI entry point for the MCP server."""
    app = typer.Typer(help="AWDX MCP Server")
    
    @app.command()
    def start(
        host: str = typer.Option("localhost", "--host", "-h", help="Server host"),
        port: int = typer.Option(3000, "--port", "-p", help="Server port"),
        config: Optional[str] = typer.Option(None, "--config", "-c", help="Config file path"),
        no_ai: bool = typer.Option(False, "--no-ai", help="Disable AI features")
    ):
        """Start the AWDX MCP server."""
        console.print(Panel.fit(
            "[bold blue]AWDX MCP Server[/bold blue]\n"
            f"Host: {host}\n"
            f"Port: {port}\n"
            f"AI Enabled: {not no_ai}",
            title="🚀 Starting Server"
        ))
        
        server = AWDXMCPServer(
            config_path=config,
            ai_enabled=not no_ai
        )
        
        # Show server info
        status = server.get_status()
        table = Table(title="Server Status")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        for key, value in status.items():
            table.add_row(key.replace("_", " ").title(), str(value))
        
        console.print(table)
        console.print("\n[green]Server is ready to accept connections![/green]")
        
        server.run(host=host, port=port)
    
    @app.command()
    def status():
        """Show server status."""
        console.print("[yellow]MCP server is not running[/yellow]")
        console.print("Use 'awdx mcp start' to start the server")
    
    app()


if __name__ == "__main__":
    main() 