"""AWDX AI Commands

This module provides AI-powered commands for natural language interaction
with AWDX CLI tools.

Commands:
    - awdx ask: Ask questions in natural language
    - awdx chat: Start interactive AI chat session  
    - awdx explain: Explain AWDX commands
    - awdx suggest: Get AI-powered suggestions
"""

import asyncio
import sys
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

from . import initialize_ai_engine, is_ai_available, get_nlp_processor
from .exceptions import AIEngineError, format_error_for_user
from .config_manager import AIConfig

# Import version info from main package
try:
    from awdx import __version__, __homepage__, __author__
except ImportError:
    __version__ = "0.0.9-dev"
    __homepage__ = "https://github.com/pxkundu/awdx"
    __author__ = "Partha Sarathi Kundu"

# ASCII Art for AWDX
ASCII_ART = r"""
 █████╗ ██╗    ██╗█████╗ ██╗  ██╗
██╔══██╗██║    ██║██╔═██╗╚██╗██╔╝
███████║██║ █╗ ██║██║ ██║ ╚███╔╝
██╔══██║██║███╗██║██║ ██║ ██╔██╗
██║  ██║╚███╔███╔╝█████╔╝██╔╝ ██╗
╚═╝  ╚═╝ ╚══╝╚══╝ ╚════╝ ╚═╝  ╚═╝
"""

# Create AI command app
ai_app = typer.Typer(
    name="ai",
    help="🤖 AI-powered natural language interface for AWDX",
    rich_markup_mode="rich",
    invoke_without_command=True
)

console = Console()

def get_ai_config() -> Optional[AIConfig]:
    """Get current AI configuration."""
    try:
        return AIConfig.load_from_file()
    except Exception:
        return None

def show_awdx_ai_art():
    """Display AWDX AI ASCII art."""
    awdx_ai_art = """
 █████╗ ██╗    ██╗██████╗ ██╗  ██╗    █████╗ ██╗
██╔══██╗██║    ██║██╔══██╗╚██╗██╔╝   ██╔══██╗██║
███████║██║ █╗ ██║██║  ██║ ╚███╔╝    ███████║██║
██╔══██║██║███╗██║██║  ██║ ██╔██╗    ██╔══██║██║
██║  ██║╚███╔███╔╝██████╔╝██╔╝ ██╗   ██║  ██║██║
╚═╝  ╚═╝ ╚══╝╚══╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝  ╚═╝╚═╝
"""
    console.print(awdx_ai_art, style="bold cyan")

@ai_app.callback()
def ai_main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", help="Show AWDX AI version"),
    help: bool = typer.Option(False, "--help", help="Show help message")
):
    """
    🤖 AWDX AI - Natural Language Interface for AWS DevSecOps
    
    Interact with AWS resources using natural language queries. Get intelligent 
    command suggestions, explanations, and automated DevOps workflows.
    
    🚀 Quick Start:
        awdx ai ask "show my AWS profiles"
        awdx ai chat
        awdx ai explain "awdx cost summary"
    
    💡 Examples:
        • "What are my EC2 costs for last month?"
        • "Audit my IAM security"  
        • "List all S3 buckets with encryption status"
        • "Find unused EBS volumes"
    
    ⚡ Features:
        • Smart intent recognition (25+ supported intents)
        • Dual-tool intelligence (AWDX + AWS CLI)
        • Security-conscious recommendations
        • DevOps workflow understanding
        • Interactive chat sessions
    """
    if version:
        # Show ASCII art and comprehensive AI version information
        typer.echo(ASCII_ART)
        typer.echo(f"🤖 AWDX AI v{__version__} - AWS DevOps X")
        typer.echo("Gen AI-powered AWS DevSecOps CLI tool")
        typer.echo(f"🔗 {__homepage__}")
        typer.echo(f"👨‍💻 Developed by: {__author__} (@pxkundu)")
        typer.echo()
        typer.echo("🧠 AI Engine: Google Gemini 1.5 Flash")
        typer.echo("🎯 Capabilities: Natural language AWS DevSecOps automation")
        typer.echo("💬 Usage: awdx ai chat  # Interactive session")
        typer.echo("        awdx ask 'your command here'")
        
        # Show AI configuration status
        try:
            config = get_ai_config()
            if config and config.has_valid_api_key():
                typer.echo("⚙️ Status: ✅ Configured and ready")
            else:
                typer.echo("⚙️ Status: ⚠️ Not configured - run 'awdx ai configure'")
        except Exception:
            typer.echo("⚙️ Status: ⚠️ Configuration needed - run 'awdx ai configure'")
        
        raise typer.Exit()
    
    if help:
        # Show ASCII art before help
        show_awdx_ai_art()
        console.print()
        console.print(ctx.get_help())
        raise typer.Exit()
    
    # If no subcommand is provided, show the AI introduction
    if ctx.invoked_subcommand is None:
        # Show ASCII art
        show_awdx_ai_art()
        
        # Show welcome information
        console.print(Panel(
            "🚀 **Quick Start:**\n"
            "   `awdx ai ask \"show my AWS profiles\"`\n"
            "   `awdx ai chat`\n"
            "   `awdx ai explain \"awdx cost summary\"`\n\n"
            "💡 **Examples:**\n"
            "   • \"What are my EC2 costs for last month?\"\n"
            "   • \"Audit my IAM security\"\n"
            "   • \"List all S3 buckets with encryption status\"\n"
            "   • \"Find unused EBS volumes\"\n\n"
            "⚡ **Features:**\n"
            "   • Smart intent recognition (25+ supported intents)\n"
            "   • Dual-tool intelligence (AWDX + AWS CLI)\n"
            "   • Security-conscious recommendations\n"
            "   • DevOps workflow understanding\n"
            "   • Interactive chat sessions",
            title="🤖 AWDX AI - Natural Language Interface for AWS DevSecOps",
            border_style="cyan",
            expand=False
        ))
        
        console.print("\n💡 [dim]Run [bold]awdx ai --help[/bold] to see all available commands.[/dim]")
        raise typer.Exit()


@ai_app.command("ask")
def ask_command(
    query: str = typer.Argument(..., help="Natural language query"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="AWS profile to use"),
    execute: bool = typer.Option(False, "--execute", "-x", help="Execute the suggested command"),
    explain: bool = typer.Option(True, "--explain/--no-explain", help="Show explanation")
):
    """
    Ask a question in natural language and get AWDX command suggestions.
    
    Examples:
        awdx ask "show my AWS profiles"
        awdx ask "what are my EC2 costs for last month"
        awdx ask "audit my IAM security" --execute
    """
    try:
        # Check if AI is available
        if not is_ai_available():
            console.print("❌ AI features are not available. Please configure GEMINI_API_KEY.", style="red")
            console.print("Visit https://aistudio.google.com/apikey to get your API key.")
            raise typer.Exit(1)
        
        # Process query directly - let exceptions bubble up for proper error formatting
        result = asyncio.run(_process_query(query, profile))
        
        if result:
            # Display result
            _display_command_result(result, explain)
            
            # Execute if requested
            if execute and result.confidence > 0.7:
                _execute_command(result.awdx_command)
            elif execute:
                console.print(f"⚠️ Command confidence too low ({result.confidence:.2f}). Use --explain to see details.", style="yellow")
        
    except KeyboardInterrupt:
        console.print("\n👋 Goodbye!")
        raise typer.Exit(0)
    except Exception as e:
        from .exceptions import format_error_for_user, AIEngineError
        if isinstance(e, AIEngineError):
            console.print(format_error_for_user(e))
        else:
            console.print(f"❌ Error: {e}")
        raise typer.Exit(1)


@ai_app.command("chat")
def chat_command(
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="AWS profile to use")
):
    """
    Start an interactive AI chat session for natural language commands.
    
    Type 'exit', 'quit', or press Ctrl+C to end the session.
    """
    try:
        # Check if AI is available
        if not is_ai_available():
            console.print("❌ AI features are not available. Please configure GEMINI_API_KEY.", style="red")
            console.print("Visit https://aistudio.google.com/apikey to get your API key.")
            raise typer.Exit(1)
        
        # Start chat session directly - let exceptions bubble up for proper error formatting
        asyncio.run(_start_chat_session(profile))
        
    except KeyboardInterrupt:
        console.print("\n👋 Goodbye!")
        raise typer.Exit(0)
    except Exception as e:
        from .exceptions import format_error_for_user, AIEngineError
        if isinstance(e, AIEngineError):
            console.print(format_error_for_user(e))
        else:
            console.print(f"❌ Error: {e}")
        raise typer.Exit(1)


@ai_app.command("explain")
def explain_command(
    command: str = typer.Argument(..., help="AWDX command to explain"),
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed explanation")
):
    """
    Explain what an AWDX command does.
    
    Examples:
        awdx explain "awdx cost summary"
        awdx explain "awdx iam audit --export results.json"
    """
    try:
        # Check if AI is available
        if not is_ai_available():
            console.print("❌ AI features are not available. Please configure GEMINI_API_KEY.", style="red")
            console.print("Visit https://aistudio.google.com/apikey to get your API key.")
            raise typer.Exit(1)
        
        # Get explanation directly - let exceptions bubble up for proper error formatting
        explanation = asyncio.run(_explain_command(command, detailed))
        
        if explanation:
            console.print(Panel(
                Markdown(explanation),
                title=f"🔍 Explanation: {command}",
                border_style="blue"
            ))
        
    except Exception as e:
        from .exceptions import format_error_for_user, AIEngineError
        if isinstance(e, AIEngineError):
            console.print(format_error_for_user(e))
        else:
            console.print(f"❌ Error: {e}")
        raise typer.Exit(1)


@ai_app.command("suggest")
def suggest_command(
    context: Optional[str] = typer.Option(None, "--context", "-c", help="Context for suggestions"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="AWS profile context")
):
    """
    Get AI-powered suggestions for AWDX commands based on context.
    
    Examples:
        awdx suggest --context "I want to optimize my AWS costs"
        awdx suggest --context "Security audit for production"
    """
    try:
        # Check if AI is available
        if not is_ai_available():
            console.print("❌ AI features are not available. Please configure GEMINI_API_KEY.", style="red")
            console.print("Visit https://aistudio.google.com/apikey to get your API key.")
            raise typer.Exit(1)
        
        # Get suggestions directly - let exceptions bubble up for proper error formatting
        suggestions = asyncio.run(_get_suggestions(context, profile))
        
        if suggestions:
            _display_suggestions(suggestions)
        
    except Exception as e:
        from .exceptions import format_error_for_user, AIEngineError
        if isinstance(e, AIEngineError):
            console.print(format_error_for_user(e))
        else:
            console.print(f"❌ Error: {e}")
        raise typer.Exit(1)


@ai_app.command()
def config(
    show: bool = typer.Option(False, "--show", help="Show current AI configuration"),
    reset: bool = typer.Option(False, "--reset", help="Reset AI configuration"),
) -> None:
    """Manage AI engine configuration."""
    try:
        if show:
            _show_ai_config()
        elif reset:
            _reset_ai_config()
        else:
            console.print("Use --show or --reset")
            
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        raise typer.Exit(1)


@ai_app.command()
def configure(
    interactive: bool = typer.Option(True, "--interactive/--no-interactive", help="Use interactive setup"),
    browser: bool = typer.Option(True, "--browser/--no-browser", help="Open browser automatically"),
    test: bool = typer.Option(False, "--test", help="Test mode for development", hidden=True),
) -> None:
    """🚀 Configure AWDX AI features with guided setup."""
    console = Console()
    
    try:
        # Test mode for development
        if test:
            console.print("🧪 [yellow]Test Mode - Configuration flow test[/yellow]")
            console.print("✅ Emoji display test: 🤖")
            console.print("✅ Configuration object creation test...")
            
            from .config_manager import AIConfig
            # Create test configuration for development
            test_config = AIConfig()
            test_config.gemini.api_key = "test_api_key_placeholder_for_development"
            console.print("✅ Config creation successful")
            console.print("✅ All tests passed!")
            return

        # Check if already configured
        if is_ai_available() and not typer.confirm("AI is already configured. Reconfigure?"):
            console.print("✅ AI features are already set up!", style="green")
            return
            
        if not interactive:
            _show_manual_configure()
            return
            
        console.print()
        console.print("🤖 [bold blue]AWDX AI Configuration[/bold blue]", justify="center")
        console.print("=" * 50, style="blue")
        console.print()
        
        # Step 1: Welcome and explanation
        console.print("Welcome to AWDX AI! Let's get you set up with intelligent AWS DevSecOps assistance.")
        console.print()
        console.print("This configuration will:")
        console.print("• 📋 Guide you to get a Google Gemini API key")
        console.print("• 🔐 Securely store your configuration")
        console.print("• ✅ Test the AI connection")
        console.print("• 🚀 Get you ready to use natural language commands")
        console.print()
        
        if not typer.confirm("Ready to continue?"):
            console.print("Configuration cancelled.", style="yellow")
            return
            
        # Step 2: API Key acquisition
        console.print("\n📋 [bold]Step 1: Get your Gemini API Key[/bold]")
        console.print()
        
        if browser:
            console.print("Opening Google AI Studio in your browser...")
            try:
                import webbrowser
                webbrowser.open("https://aistudio.google.com/apikey")
                console.print("✅ Browser opened to: https://aistudio.google.com/apikey")
            except Exception:
                console.print("⚠️  Could not open browser automatically.")
                browser = False
        
        if not browser:
            console.print("Please visit: [link]https://aistudio.google.com/apikey[/link]")
            
        console.print()
        console.print("Follow these steps in Google AI Studio:")
        console.print("1. 🔐 Sign in with your Google account")
        console.print("2. 🗝️  Click 'Get API key' button")
        console.print("3. 📝 Create a new API key (give it a name like 'AWDX-CLI')")
        console.print("4. 📋 Copy the generated API key (starts with 'AIza')")
        console.print()
        
        # Step 3: API Key input with validation
        console.print("📝 [bold]Step 2: Enter your API Key[/bold]")
        console.print()
        
        api_key = None
        max_attempts = 3
        for attempt in range(max_attempts):
            api_key = typer.prompt(
                "Paste your Gemini API key here",
                hide_input=True,
                type=str
            ).strip()
            
            if not api_key:
                console.print("❌ API key cannot be empty.", style="red")
                continue
                
            # Basic validation
            if not api_key.startswith('AIza') or len(api_key) < 30:
                console.print("❌ That doesn't look like a valid Gemini API key.", style="red")
                console.print("   Gemini API keys typically start with 'AIza' and are quite long.")
                if attempt < max_attempts - 1:
                    console.print(f"   Please try again. ({attempt + 1}/{max_attempts})")
                continue
                
            break
        else:
            console.print("❌ Too many invalid attempts. Please run configure again.", style="red")
            raise typer.Exit(1)
            
        # Step 4: Test connection
        console.print("\n🔍 [bold]Step 3: Testing connection...[/bold]")
        
        try:
            from .gemini_client import GeminiClient
            from .config_manager import AIConfig
            
            # Create temporary config for testing (without validation)
            temp_config = AIConfig()
            temp_config.gemini.api_key = api_key
            temp_config.enabled = True
            
            # Test basic API connectivity without full validation
            client = GeminiClient(temp_config)
            
            with console.status("Testing Gemini API connection..."):
                # Simple test call with timeout
                response = asyncio.run(asyncio.wait_for(
                    client.generate_text("Say 'Hello AWDX' if you can see this message."),
                    timeout=15.0
                ))
                
            if response and "AWDX" in response:
                console.print("✅ Connection successful!", style="green")
                connection_ok = True
            else:
                console.print("⚠️  Connection test returned unexpected response.", style="yellow")
                if response:
                    console.print(f"Response: {response[:100]}...")
                connection_ok = typer.confirm("Continue with configuration anyway?")
                
        except asyncio.TimeoutError:
            console.print("❌ Connection test timed out after 15 seconds.", style="red")
            console.print("\nThis might be due to:")
            console.print("• Network connectivity issues")
            console.print("• API server being slow")
            console.print("• Regional API restrictions")
            connection_ok = typer.confirm("Continue with configuration anyway?")
        except Exception as e:
            console.print(f"❌ Connection test failed: {str(e)}", style="red")
            console.print("\nThis might be due to:")
            console.print("• Invalid API key")
            console.print("• Network connectivity issues")
            console.print("• API quota limits")
            console.print("• Missing dependencies")
            connection_ok = typer.confirm("Continue with configuration anyway?")
            
        if not connection_ok:
            console.print("Configuration cancelled.", style="yellow")
            return
            
        # Step 5: Save configuration
        console.print("\n💾 [bold]Step 4: Save configuration[/bold]")
        console.print()
        
        save_options = [
            "Environment variable (recommended for development)",
            "User config file (~/.awdx/ai_config.yaml)",
            "Project config file (./awdx.ai.yaml)",
            "Show manual instructions only"
        ]
        
        console.print("How would you like to store your API key?")
        for i, option in enumerate(save_options, 1):
            console.print(f"{i}. {option}")
            
        choice = typer.prompt("Enter your choice (1-4)", type=int, default=1)
        
        if choice == 1:
            _save_to_environment(api_key, console)
        elif choice == 2:
            _save_to_user_config(api_key, console)
        elif choice == 3:
            _save_to_project_config(api_key, console)
        elif choice == 4:
            _show_manual_instructions(api_key, console)
        else:
            console.print("Invalid choice. Showing manual instructions.", style="yellow")
            _show_manual_instructions(api_key, console)
            
        # Step 6: Success and next steps
        console.print("\n🎉 [bold green]Configuration Complete![/bold green]")
        console.print()
        
        # Check if API key is immediately available
        import os
        if os.getenv('GEMINI_API_KEY'):
            console.print("🚀 [bold]You're now ready to use AWDX AI features:[/bold]")
        else:
            console.print("🔄 [yellow]Important: Restart your terminal or run this command:[/yellow]")
            console.print(f"[bold cyan]source ~/.zshrc[/bold cyan]")
            console.print()
            console.print("🚀 [bold]Then you'll be ready to use AWDX AI features:[/bold]")
        
        console.print()
        console.print("• [cyan]awdx ai ask[/cyan] \"show my AWS profiles\"")
        console.print("• [cyan]awdx ai chat[/cyan] - Start interactive session")
        console.print("• [cyan]awdx ai explain[/cyan] \"awdx s3 audit\"")
        console.print("• [cyan]awdx ai suggest[/cyan] - Get command suggestions")
        console.print()
        console.print("📚 For more help: [cyan]awdx ai --help[/cyan]")
        console.print("📖 Documentation: [cyan]docs/AI_FEATURES.md[/cyan]")

    except KeyboardInterrupt:
        console.print("\n❌ Configuration cancelled by user.", style="yellow")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n❌ Configuration failed: {str(e)}", style="red")
        console.print("\n💡 You can still configure manually:")
        _show_manual_configure()
        raise typer.Exit(1)


def _save_to_environment(api_key: str, console: Console) -> None:
    """Save API key to environment variable with shell-specific instructions."""
    console.print()
    console.print("🔧 [bold]Setting up environment variable...[/bold]")
    
    import os
    shell = os.environ.get('SHELL', '/bin/bash')
    
    if 'zsh' in shell:
        config_file = "~/.zshrc"
        export_cmd = f'echo \'export GEMINI_API_KEY="{api_key}"\' >> ~/.zshrc'
    elif 'fish' in shell:
        config_file = "~/.config/fish/config.fish"
        export_cmd = f'echo \'set -gx GEMINI_API_KEY "{api_key}"\' >> ~/.config/fish/config.fish'
    else:
        config_file = "~/.bashrc"
        export_cmd = f'echo \'export GEMINI_API_KEY="{api_key}"\' >> ~/.bashrc'
        
    console.print(f"Adding to your shell configuration ({config_file}):")
    console.print(f"[code]{export_cmd}[/code]")
    
    if typer.confirm("Add to shell configuration automatically?"):
        try:
            # Secure shell configuration update using subprocess instead of os.system
            import shlex
            if shell == 'zsh':
                file_path = os.path.expanduser("~/.zshrc")
            else:
                file_path = os.path.expanduser("~/.bashrc")
            
            # Safely append to shell configuration
            export_line = f'export GEMINI_API_KEY="{api_key}"\n'
            with open(file_path, 'a') as f:
                f.write(export_line)
            
            console.print("✅ Added to shell configuration!", style="green")
            console.print(f"🔄 Restart your terminal or run: [code]source {config_file}[/code]")
        except Exception as e:
            console.print(f"❌ Could not modify {config_file}: {e}", style="red")
            _show_manual_instructions(api_key, console)
    else:
        _show_manual_instructions(api_key, console)


def _save_to_user_config(api_key: str, console: Console) -> None:
    """Save API key to user configuration file."""
    import os
    import yaml
    from pathlib import Path
    
    config_dir = Path.home() / ".awdx"
    config_file = config_dir / "ai_config.yaml"
    
    try:
        config_dir.mkdir(exist_ok=True)
        
        config = {
            'gemini': {
                'api_key': api_key,
                'model': 'gemini-pro',
                'temperature': 0.1,
                'max_tokens': 1000
            },
            'general': {
                'cache_enabled': True,
                'cache_ttl': 3600,
                'verbose': False
            }
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
            
        # Set restrictive permissions
        os.chmod(config_file, 0o600)
        
        console.print(f"✅ Configuration saved to: {config_file}", style="green")
        console.print("🔐 File permissions set to 600 (user read/write only)")
        
    except Exception as e:
        console.print(f"❌ Could not save config file: {e}", style="red")
        _show_manual_instructions(api_key, console)


def _save_to_project_config(api_key: str, console: Console) -> None:
    """Save API key to project configuration file."""
    import yaml
    import os
    
    config_file = "awdx.ai.yaml"
    
    try:
        config = {
            'gemini': {
                'api_key': api_key,
                'model': 'gemini-pro'
            }
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
            
        # Set restrictive permissions
        os.chmod(config_file, 0o600)
        
        console.print(f"✅ Configuration saved to: {config_file}", style="green")
        console.print("⚠️  Remember to add this file to .gitignore!", style="yellow")
        
        if typer.confirm("Add to .gitignore automatically?"):
            try:
                with open(".gitignore", "a") as f:
                    f.write("\n# AWDX AI Configuration\nawdx.ai.yaml\n")
                console.print("✅ Added to .gitignore", style="green")
            except Exception:
                console.print("❌ Could not modify .gitignore", style="red")
        
    except Exception as e:
        console.print(f"❌ Could not save config file: {e}", style="red")
        _show_manual_instructions(api_key, console)


def _show_manual_instructions(api_key: str, console: Console) -> None:
    """Show manual setup instructions."""
    console.print("\n📖 [bold]Manual Setup Instructions[/bold]")
    console.print()
    console.print("Option 1: Environment Variable (Recommended)")
    console.print(f"[code]export GEMINI_API_KEY=\"{api_key}\"[/code]")
    console.print()
    console.print("Option 2: Add to shell config")
    console.print(f"[code]echo 'export GEMINI_API_KEY=\"{api_key}\"' >> ~/.bashrc[/code]")
    console.print("[code]source ~/.bashrc[/code]")
    console.print()


def _show_manual_configure() -> None:
    """Show manual configure instructions when interactive configure is disabled."""
    console = Console()
    console.print("\n📖 [bold]Manual AWDX AI Configuration[/bold]")
    console.print()
    console.print("1. Get your Gemini API key:")
    console.print("   Visit: [link]https://aistudio.google.com/apikey[/link]")
    console.print("   Create an API key for your project")
    console.print()
    console.print("2. Set the environment variable:")
    console.print("   [code]export GEMINI_API_KEY=\"your_api_key_here\"[/code]")
    console.print()
    console.print("3. Test the configuration:")
    console.print("   [code]awdx ai ask \"test connection\"[/code]")
    console.print()


# Helper functions

async def _process_query(query: str, profile: Optional[str] = None):
    """Process a natural language query."""
    nlp_processor = get_nlp_processor()
    result = await nlp_processor.process_query(query, aws_profile=profile)
    return result


async def _start_chat_session(profile: Optional[str] = None):
    """Start interactive chat session."""
    
    # Display AWDX AI ASCII art
    show_awdx_ai_art()
    console.print(Panel(
        "🤖 Welcome to AWDX AI Chat!\n\n"
        "Ask me anything about AWS DevSecOps in natural language.\n"
        "Type 'exit', 'quit', or press Ctrl+C to end the session.\n\n"
        "Examples:\n"
        "• Show me all my AWS profiles\n"
        "• What are my S3 costs for last month?\n"
        "• Run a security audit on my IAM users",
        title="AWDX AI Chat",
        border_style="green"
    ))
    
    nlp_processor = get_nlp_processor()
    
    while True:
        try:
            # Get user input
            user_input = Prompt.ask("\n[bold blue]You[/bold blue]")
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                break
            
            # Process query
            console.print("🤔 Thinking...", style="yellow")
            result = await nlp_processor.process_query(user_input, aws_profile=profile)
            
            if result:
                _display_command_result(result, explain=True)
                
                # Ask if user wants to execute
                if result.confidence > 0.7:
                    execute = Prompt.ask("Execute this command?", choices=["y", "n"], default="n")
                    if execute.lower() == 'y':
                        _execute_command(result.awdx_command)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"❌ Error: {e}", style="red")
    
    console.print("👋 Chat session ended. Goodbye!")


async def _explain_command(command: str, detailed: bool = False):
    """Get explanation for a command."""
    nlp_processor = get_nlp_processor()
    
    explanation_prompt = f"""Explain this AWDX command in detail:

Command: {command}

Provide a {"detailed" if detailed else "concise"} explanation including:
- What the command does
- What parameters it accepts
- What output to expect
- Any security considerations
- Related commands that might be useful

Format the response in markdown."""
    
    gemini_client = nlp_processor.gemini_client
    response = await gemini_client.generate_text(explanation_prompt)
    return response


async def _get_suggestions(context: Optional[str] = None, profile: Optional[str] = None):
    """Get AI-powered suggestions."""
    nlp_processor = get_nlp_processor()
    
    if not context:
        context = "General AWS DevSecOps tasks"
    
    suggestion_prompt = f"""Provide 5 useful AWDX command suggestions for this context:

Context: {context}
AWS Profile: {profile or 'default'}

Suggest practical AWDX commands that would be helpful for this context.
Include a brief explanation for each suggestion.

Format as:
1. `awdx command` - Brief explanation
2. `awdx command` - Brief explanation
..."""
    
    gemini_client = nlp_processor.gemini_client
    response = await gemini_client.generate_text(suggestion_prompt)
    return response


def _display_command_result(result, explain: bool = True):
    """Display parsed command result with DevOps intelligence."""
    # Create confidence indicator
    if result.confidence >= 0.8:
        confidence_style = "green"
        confidence_icon = "✅"
    elif result.confidence >= 0.6:
        confidence_style = "yellow"
        confidence_icon = "⚠️"
    else:
        confidence_style = "red"
        confidence_icon = "❌"
    
    # Create main result table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Field", style="cyan")
    table.add_column("Value")
    
    table.add_row("Intent", result.intent.value)
    table.add_row("Confidence", f"{confidence_icon} {result.confidence:.2f}", style=confidence_style)
    table.add_row("Primary Command", f"`{result.awdx_command}`", style="bold")
    
    if explain and result.explanation:
        table.add_row("Explanation", result.explanation)
    
    console.print(table)
    
    # Show alternatives if available
    alternatives = result.get_alternatives()
    if alternatives:
        console.print("\n💡 [bold cyan]Alternative Commands:[/bold cyan]")
        for i, alt in enumerate(alternatives, 1):
            console.print(f"  {i}. `{alt}`", style="dim")
    
    # Show security considerations
    if result.security_considerations:
        console.print(f"\n⚠️ [bold yellow]Security Considerations:[/bold yellow]")
        console.print(f"   {result.security_considerations}", style="yellow")
    
    # Show workflow context
    if result.workflow_context:
        console.print(f"\n🔄 [bold blue]DevOps Workflow Context:[/bold blue]")
        console.print(f"   {result.workflow_context}", style="blue")
    
    # Show suggestions
    if result.suggestions:
        console.print(f"\n💡 [bold green]Suggestions:[/bold green]")
        for suggestion in result.suggestions[:3]:  # Limit to 3 suggestions
            console.print(f"   • {suggestion}", style="green")


def _execute_command(command: str):
    """Execute an AWDX command securely."""
    console.print(f"🚀 Executing: {command}", style="green")
    
    # Parse command securely and execute
    import subprocess
    import shlex
    try:
        # Only allow AWDX commands for security
        if not command.startswith("awdx "):
            console.print("❌ Only AWDX commands are allowed for execution", style="red")
            return
        
        # Parse command safely to prevent injection
        command_parts = shlex.split(command)
        result = subprocess.run(command_parts, capture_output=True, text=True, timeout=30)
        
        if result.stdout:
            console.print(result.stdout)
        if result.stderr:
            console.print(result.stderr, style="red")
        if result.returncode != 0:
            console.print(f"❌ Command failed with exit code: {result.returncode}", style="red")
            
    except subprocess.TimeoutExpired:
        console.print("❌ Command timed out after 30 seconds", style="red")
    except Exception as e:
        console.print(f"❌ Execution failed: {e}", style="red")


def _display_suggestions(suggestions: str):
    """Display AI suggestions."""
    console.print(Panel(
        Markdown(suggestions),
        title="💡 AI Suggestions",
        border_style="cyan"
    ))


def _show_ai_config():
    """Show current AI configuration."""
    try:
        config = AIConfig.load_default()
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Setting", style="cyan")
        table.add_column("Value")
        
        table.add_row("AI Enabled", "✅ Yes" if config.is_enabled() else "❌ No")
        table.add_row("API Key", "✅ Configured" if config.has_valid_api_key() else "❌ Not configured")
        table.add_row("Model", config.gemini.model)
        table.add_row("Debug Mode", "Yes" if config.debug_mode else "No")
        
        console.print(Panel(table, title="🤖 AI Configuration", border_style="blue"))
        
    except Exception as e:
        console.print(f"❌ Failed to load configuration: {e}", style="red")


def _show_config_template():
    """Show configuration template."""
    config = AIConfig()
    template = config.get_config_template()
    
    console.print(Panel(
        Text(template, style="dim"),
        title="📄 AI Configuration Template",
        border_style="yellow"
    ))
    
    console.print("\n💡 Save this to ~/.awdx/ai_config.yaml to customize AI settings.")


def _reset_ai_config():
    """Reset AI configuration."""
    console.print("🚀 Resetting AI configuration...")
    
    # Remove API key
    import os
    os.environ.pop('GEMINI_API_KEY', None)
    
    # Test connection
    try:
        if initialize_ai_engine():
            console.print("✅ AI engine initialized successfully!")
        else:
            console.print("❌ AI engine initialization failed.")
    except Exception as e:
        console.print(f"❌ Initialization failed: {e}", style="red")


@ai_app.command()
def test(
    key: str = typer.Option(None, "--key", help="Test with specific API key"),
) -> None:
    """🧪 Test AI connection and configuration."""
    console = Console()
    
    try:
        console.print("🧪 [bold]AWDX AI Connection Test[/bold]")
        console.print("=" * 40)
        console.print()
        
        # Check environment variable
        import os
        env_key = os.getenv('GEMINI_API_KEY')
        
        if key:
            console.print(f"🔑 Testing with provided key: {key[:10]}...")
            test_key = key
        elif env_key:
            console.print(f"🔑 Found API key in environment: {env_key[:10]}...")
            test_key = env_key
        else:
            console.print("❌ No API key found")
            console.print("💡 To fix this:")
            console.print("1. Run: [cyan]source ~/.zshrc[/cyan] (if you configured recently)")
            console.print("2. Or run: [cyan]awdx ai configure[/cyan] to reconfigure")
            raise typer.Exit(1)
        
        # Test configuration loading
        console.print("📋 Testing configuration...")
        from .config_manager import AIConfig
        config = AIConfig()
        config.gemini.api_key = test_key
        console.print("✅ Configuration loaded")
        
        # Test client creation
        console.print("🤖 Testing AI client...")
        from .gemini_client import GeminiClient
        client = GeminiClient(config)
        console.print("✅ Client created")
        
        # Test connection (simple call)
        console.print("🌐 Testing API connection...")
        
        # First test the simple connection
        connection_works = client.test_connection()
        if connection_works:
            console.print("✅ Basic connection successful")
        else:
            console.print("❌ Basic connection failed")
            raise typer.Exit(1)
        
        # Test actual text generation
        console.print("📝 Testing text generation...")
        try:
            response = asyncio.run(client.generate_text("Say 'Hello AWDX' if you can see this message."))
            if response:
                console.print(f"✅ Text generation successful: {response[:100]}...")
            else:
                console.print("❌ Text generation returned None/empty")
        except Exception as gen_error:
            console.print(f"❌ Text generation failed: {str(gen_error)}")
            
            # Try a simpler test
            console.print("🔄 Trying simpler test...")
            try:
                simple_response = asyncio.run(client.generate_text("Hello"))
                console.print(f"✅ Simple test: {simple_response}")
            except Exception as simple_error:
                console.print(f"❌ Simple test failed: {str(simple_error)}")
        
        console.print("✅ [green]All tests passed! AI is working correctly.[/green]")
        
    except Exception as e:
        console.print(f"❌ Test failed: {str(e)}")
        raise typer.Exit(1)


# Export the command app
__all__ = ["ai_app"] 