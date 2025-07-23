"""
AWDX MCP Server CLI

This module provides CLI commands for managing the AWDX MCP server.
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .server import AWDXMCPServer

console = Console()

# Create MCP command app
mcp_app = typer.Typer(
    name="mcp",
    help="🔌 MCP Server - Model Context Protocol integration for AI assistants",
    rich_markup_mode="rich",
)

@mcp_app.command()
def start(
    host: str = typer.Option("localhost", "--host", "-h", help="Server host address"),
    port: int = typer.Option(3000, "--port", "-p", help="Server port number"),
    config: str = typer.Option(None, "--config", "-c", help="AWDX configuration file path"),
    no_ai: bool = typer.Option(False, "--no-ai", help="Disable AI features"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging")
):
    """Start the AWDX MCP server."""
    
    # Display startup information
    console.print(Panel.fit(
        "[bold blue]AWDX MCP Server[/bold blue]\n"
        f"Host: {host}\n"
        f"Port: {port}\n"
        f"AI Enabled: {not no_ai}\n"
        f"Config: {config or 'Default'}",
        title="🚀 Starting MCP Server"
    ))
    
    # Create and start server
    try:
        server = AWDXMCPServer(
            config_path=config,
            ai_enabled=not no_ai,
            verbose=verbose
        )
        
        # Show server status
        status = server.get_status()
        table = Table(title="Server Status")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        for key, value in status.items():
            table.add_row(key.replace("_", " ").title(), str(value))
        
        console.print(table)
        console.print("\n[green]MCP server is ready to accept connections![/green]")
        console.print(f"[dim]Connect your AI assistant to: {host}:{port}[/dim]")
        
        # Start the server
        server.run(host=host, port=port)
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error starting server: {e}[/red]")
        raise typer.Exit(1)

@mcp_app.command()
def status():
    """Show MCP server status and information."""
    
    console.print(Panel.fit(
        "[bold blue]AWDX MCP Server Status[/bold blue]\n"
        "The MCP server is not currently running.\n"
        "Use 'awdx mcp start' to start the server.",
        title="📊 Server Status"
    ))
    
    # Show available tools
    try:
        server = AWDXMCPServer(enable_all_tools=True)
        tools = server.tool_registry.get_tools()
        
        if tools:
            table = Table(title="Available MCP Tools")
            table.add_column("Tool Name", style="cyan")
            table.add_column("Description", style="green")
            
            for tool in tools:
                table.add_row(tool["name"], tool["description"])
            
            console.print(table)
        else:
            console.print("[yellow]No tools available[/yellow]")
            
    except Exception as e:
        console.print(f"[red]Error getting tool information: {e}[/red]")

@mcp_app.command()
def tools():
    """List all available MCP tools."""
    
    try:
        server = AWDXMCPServer(enable_all_tools=True)
        tools = server.tool_registry.get_tools()
        
        if not tools:
            console.print("[yellow]No tools available[/yellow]")
            return
        
        # Group tools by category
        categories = {
            "Profile Management": [],
            "Cost Analysis": [],
            "IAM Security": [],
            "S3 Security": [],
            "Secret Management": [],
            "Security Assessment": [],
            "AI Features": []
        }
        
        for tool in tools:
            name = tool["name"]
            if name.startswith("awdx_profile"):
                categories["Profile Management"].append(tool)
            elif name.startswith("awdx_cost"):
                categories["Cost Analysis"].append(tool)
            elif name.startswith("awdx_iam"):
                categories["IAM Security"].append(tool)
            elif name.startswith("awdx_s3"):
                categories["S3 Security"].append(tool)
            elif name.startswith("awdx_secret"):
                categories["Secret Management"].append(tool)
            elif name.startswith("awdx_security"):
                categories["Security Assessment"].append(tool)
            elif name.startswith("awdx_ai"):
                categories["AI Features"].append(tool)
        
        # Display tools by category
        for category, category_tools in categories.items():
            if category_tools:
                console.print(f"\n[bold]{category}[/bold]")
                table = Table(show_header=False, box=None)
                table.add_column("Tool", style="cyan")
                table.add_column("Description", style="green")
                
                for tool in category_tools:
                    table.add_row(tool["name"], tool["description"])
                
                console.print(table)
                
    except Exception as e:
        console.print(f"[red]Error listing tools: {e}[/red]")

@mcp_app.command()
def test(
    host: str = typer.Option("localhost", "--host", "-h", help="Server host"),
    port: int = typer.Option(3000, "--port", "-p", help="Server port")
):
    """Test MCP server connection and basic functionality."""
    
    console.print(Panel.fit(
        f"[bold blue]Testing MCP Server Connection[/bold blue]\n"
        f"Host: {host}\n"
        f"Port: {port}",
        title="🧪 Connection Test"
    ))
    
    try:
        import asyncio
        import json
        
        async def test_connection():
            try:
                reader, writer = await asyncio.open_connection(host, port)
                
                # Send initialize request
                init_request = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {
                            "name": "AWDX Test Client",
                            "version": "1.0.0"
                        }
                    }
                }
                
                request_data = json.dumps(init_request).encode("utf-8")
                request_length = len(request_data).to_bytes(4, byteorder="big")
                writer.write(request_length + request_data)
                await writer.drain()
                
                # Read response
                length_bytes = await reader.read(4)
                if length_bytes:
                    message_length = int.from_bytes(length_bytes, byteorder="big")
                    response_data = await reader.read(message_length)
                    response = json.loads(response_data.decode("utf-8"))
                    
                    if "result" in response:
                        console.print("[green]✓ Connection successful![/green]")
                        console.print(f"[dim]Server: {response['result']['serverInfo']['name']} v{response['result']['serverInfo']['version']}[/dim]")
                    else:
                        console.print("[red]✗ Connection failed[/red]")
                        console.print(f"[red]Error: {response.get('error', {}).get('message', 'Unknown error')}[/red]")
                
                writer.close()
                await writer.wait_closed()
                
            except Exception as e:
                console.print(f"[red]✗ Connection failed: {e}[/red]")
        
        asyncio.run(test_connection())
        
    except ImportError:
        console.print("[red]asyncio not available for testing[/red]")
    except Exception as e:
        console.print(f"[red]Test failed: {e}[/red]")

@mcp_app.command()
def docs():
    """Show MCP server documentation and usage examples."""
    
    console.print(Panel.fit(
        "[bold blue]AWDX MCP Server Documentation[/bold blue]\n"
        "The AWDX MCP server exposes AWS DevSecOps capabilities\n"
        "to AI assistants through the Model Context Protocol.\n\n"
        "For detailed documentation, visit:\n"
        "https://github.com/pxkundu/awdx/docs/MCP_INTEGRATION.md",
        title="📚 Documentation"
    ))
    
    # Show usage examples
    examples = [
        ("Start server", "awdx mcp start"),
        ("Start with custom port", "awdx mcp start --port 3001"),
        ("Start without AI", "awdx mcp start --no-ai"),
        ("List tools", "awdx mcp tools"),
        ("Test connection", "awdx mcp test"),
        ("Show status", "awdx mcp status")
    ]
    
    table = Table(title="Usage Examples")
    table.add_column("Action", style="cyan")
    table.add_column("Command", style="green")
    
    for action, command in examples:
        table.add_row(action, command)
    
    console.print(table)
    
    console.print("\n[bold]Integration Examples:[/bold]")
    console.print("• Connect Claude Desktop to AWDX MCP server")
    console.print("• Use AWDX tools in ChatGPT with MCP plugin")
    console.print("• Integrate with custom AI assistants")
    console.print("• Build automated DevSecOps workflows")

if __name__ == "__main__":
    mcp_app() 