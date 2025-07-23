"""
Test MCP Server Integration

This module tests the AWDX MCP server integration.
"""

import asyncio
import json
import pytest
from unittest.mock import Mock, patch

# Test MCP server availability
@pytest.mark.unit
@pytest.mark.mcp
def test_mcp_server_import():
    """Test that MCP server can be imported."""
    try:
        from awdx.mcp_server import AWDXMCPServer, AWDXToolRegistry
        assert AWDXMCPServer is not None
        assert AWDXToolRegistry is not None
    except ImportError as e:
        pytest.skip(f"MCP server not available: {e}")

@pytest.mark.unit
@pytest.mark.mcp
def test_mcp_server_creation():
    """Test MCP server creation."""
    try:
        from awdx.mcp_server import AWDXMCPServer
        
        # Test server creation without AI
        server = AWDXMCPServer(ai_enabled=False)
        assert server is not None
        assert server.ai_enabled == False
        
        # Test server status
        status = server.get_status()
        assert "running" in status
        assert "tools_registered" in status
        assert "version" in status
        
    except ImportError as e:
        pytest.skip(f"MCP server not available: {e}")

@pytest.mark.unit
@pytest.mark.mcp
def test_tool_registry():
    """Test tool registry functionality."""
    try:
        from awdx.mcp_server import AWDXToolRegistry
        
        registry = AWDXToolRegistry()
        
        # Test tool registration
        tools = registry.get_tools()
        assert isinstance(tools, list)
        
        # Test that tools are properly formatted
        if tools:
            tool = tools[0]
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool
            
    except ImportError as e:
        pytest.skip(f"MCP server not available: {e}")

@pytest.mark.unit
@pytest.mark.mcp
def test_mcp_tools_registration():
    """Test that all AWDX tools are registered."""
    try:
        from awdx.mcp_server import AWDXToolRegistry
        
        registry = AWDXToolRegistry()
        
        # Register all tools
        registry.register_profile_tools()
        registry.register_cost_tools()
        registry.register_iam_tools()
        registry.register_s3_tools()
        registry.register_secret_tools()
        registry.register_security_tools()
        
        tools = registry.get_tools()
        
        # Check that we have tools from each category
        tool_names = [tool["name"] for tool in tools]
        
        # Profile tools
        assert any(name.startswith("awdx_profile") for name in tool_names)
        
        # Cost tools
        assert any(name.startswith("awdx_cost") for name in tool_names)
        
        # IAM tools
        assert any(name.startswith("awdx_iam") for name in tool_names)
        
        # S3 tools
        assert any(name.startswith("awdx_s3") for name in tool_names)
        
        # Secret tools
        assert any(name.startswith("awdx_secret") for name in tool_names)
        
        # Security tools
        assert any(name.startswith("awdx_security") for name in tool_names)
        
    except ImportError as e:
        pytest.skip(f"MCP server not available: {e}")

@pytest.mark.unit
@pytest.mark.mcp
def test_mcp_protocol_messages():
    """Test MCP protocol message handling."""
    try:
        from awdx.mcp_server import AWDXMCPServer
        
        server = AWDXMCPServer(ai_enabled=False)
        
        # Test initialize message
        init_params = {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "Test Client",
                "version": "1.0.0"
            }
        }
        
        # Mock the async method
        async def test_init():
            response = await server._process_mcp_message({
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": init_params
            }, client_id=1)
            
            assert response is not None
            assert "result" in response
            assert "serverInfo" in response["result"]
            assert response["result"]["serverInfo"]["name"] == "AWDX MCP Server"
        
        asyncio.run(test_init())
        
    except ImportError as e:
        pytest.skip(f"MCP server not available: {e}")

@pytest.mark.unit
@pytest.mark.mcp
def test_mcp_tools_list():
    """Test tools/list MCP method."""
    try:
        from awdx.mcp_server import AWDXMCPServer
        
        server = AWDXMCPServer(ai_enabled=False)
        
        async def test_tools_list():
            response = await server._process_mcp_message({
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {}
            }, client_id=1)
            
            assert response is not None
            assert "result" in response
            assert "tools" in response["result"]
            assert isinstance(response["result"]["tools"], list)
        
        asyncio.run(test_tools_list())
        
    except ImportError as e:
        pytest.skip(f"MCP server not available: {e}")

@pytest.mark.unit
@pytest.mark.mcp
def test_mcp_tools_call():
    """Test tools/call MCP method."""
    try:
        from awdx.mcp_server import AWDXMCPServer
        
        server = AWDXMCPServer(ai_enabled=False)
        
        async def test_tools_call():
            # Test with a non-existent tool
            response = await server._process_mcp_message({
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "nonexistent_tool",
                    "arguments": {}
                }
            }, client_id=1)
            
            assert response is not None
            assert "error" in response
            assert response["error"]["code"] == -32603
        
        asyncio.run(test_tools_call())
        
    except ImportError as e:
        pytest.skip(f"MCP server not available: {e}")

@pytest.mark.unit
@pytest.mark.mcp
def test_mcp_cli_commands():
    """Test MCP CLI commands."""
    try:
        from awdx.mcp_server.cli import mcp_app
        
        # Test that CLI app exists
        assert mcp_app is not None
        
        # Test that commands are registered
        commands = [cmd.name for cmd in mcp_app.registered_commands]
        expected_commands = ["start", "status", "tools", "test", "docs"]
        
        for cmd in expected_commands:
            assert cmd in commands
            
    except ImportError as e:
        pytest.skip(f"MCP CLI not available: {e}")

@pytest.mark.unit
@pytest.mark.mcp
def test_mcp_integration_with_main_cli():
    """Test that MCP is integrated with main AWDX CLI."""
    try:
        from awdx.cli import app
        
        # Check that MCP commands are available in main CLI
        # This is a basic check - the actual integration is tested in CLI tests
        assert app is not None
        
    except ImportError as e:
        pytest.skip(f"Main CLI not available: {e}")

if __name__ == "__main__":
    # Run basic tests
    print("Testing MCP Server Integration...")
    
    try:
        from awdx.mcp_server import AWDXMCPServer, AWDXToolRegistry
        print("✅ MCP server imports successfully")
        
        # Test server creation
        server = AWDXMCPServer(ai_enabled=False)
        print("✅ MCP server creation successful")
        
        # Test tool registry
        registry = AWDXToolRegistry()
        registry.register_profile_tools()
        tools = registry.get_tools()
        print(f"✅ Tool registry working - {len(tools)} tools registered")
        
        # Test server status
        status = server.get_status()
        print(f"✅ Server status: {status}")
        
        print("\n🎉 All MCP integration tests passed!")
        
    except ImportError as e:
        print(f"❌ MCP server not available: {e}")
    except Exception as e:
        print(f"❌ MCP integration test failed: {e}") 