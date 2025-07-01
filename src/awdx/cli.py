#!/usr/bin/env python3
"""
AWDX CLI - Main Command Line Interface

Copyright (c) 2024 Partha Sarathi Kundu
Licensed under the MIT License.
Author: Partha Sarathi Kundu <inboxkundu@gmail.com>

This software is developed independently and is not affiliated with any organization.
"""

import typer
from awdx import __version__, __homepage__, __author__
from awdx.profilyze.profile_commands import profile_app
from awdx.costlyzer.cost_commands import cost_app
from awdx.iamply.iam_commands import iam_app
from awdx.s3ntry.s3_commands import s3_app
from awdx.secrex.secret_commands import secret_app
from awdx.secutide.security_commands import security_app

# Import AI commands (with fallback if not available)
try:
    from awdx.ai_engine.ai_commands import ai_app
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    ai_app = None

app = typer.Typer(help="awdx: AWS DevOps X - Gen AI-powered AWS DevSecOps CLI tool.")

# Add subcommands
app.add_typer(profile_app, name="profile")
app.add_typer(cost_app, name="cost")
app.add_typer(iam_app, name="iam")
app.add_typer(s3_app, name="s3")
app.add_typer(secret_app, name="secret")
app.add_typer(security_app, name="security")

# Add AI commands if available
if AI_AVAILABLE and ai_app:
    app.add_typer(ai_app, name="ai")

ASCII_ART = r"""
 █████╗ ██╗    ██╗█████╗ ██╗  ██╗
██╔══██╗██║    ██║██╔═██╗╚██╗██╔╝
███████║██║ █╗ ██║██║ ██║ ╚███╔╝
██╔══██║██║███╗██║██║ ██║ ██╔██╗
██║  ██║╚███╔███╔╝█████╔╝██╔╝ ██╗
╚═╝  ╚═╝ ╚══╝╚══╝ ╚════╝ ╚═╝  ╚═╝
"""

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", help="Show AWDX version")
):
    if version:
        typer.echo(ASCII_ART)
        typer.echo(f"🚀 AWDX v{__version__} - AWS DevOps X")
        typer.echo("Gen AI-powered AWS DevSecOps CLI tool")
        typer.echo(f"🔗 {__homepage__}")
        typer.echo(f"👨‍💻 Developed by: {__author__} (@pxkundu)")
        
        # Show AI status if available
        if AI_AVAILABLE:
            try:
                from awdx.ai_engine import is_ai_available
                ai_status = "✅ Ready" if is_ai_available() else "⚙️ Configure needed"
                typer.echo(f"🤖 AI Engine: {ai_status}")
            except:
                typer.echo("🤖 AI Engine: ⚠️ Available but not configured")
        else:
            typer.echo("🤖 AI Engine: ❌ Not available")
        
        raise typer.Exit()
    
    if ctx.invoked_subcommand is None:
        typer.echo(ASCII_ART)
        about_block = (
            "\u256D\u2500 About " + "\u2500" * 56 + "\u256E\n"
            "\u2502 Developed by: Partha Sarathi Kundu" + " " * 29 + "\u2502\n"
            "\u2502 Github: @pxkundu" + " " * 47 + "\u2502\n"
            "\u2570" + "\u2500" * 64 + "\u256F\n"
        )
        typer.echo(about_block)
        
        # Show AI status if available
        if AI_AVAILABLE:
            try:
                from awdx.ai_engine import is_ai_available
                ai_status = "🤖 AI: ✅ Ready" if is_ai_available() else "🤖 AI: ⚙️ Configure needed (run: awdx ai configure)"
                typer.echo(f"\n{ai_status}")
                typer.echo("Try: awdx ask 'show me all my AWS profiles'")
                typer.echo("     awdx chat  # Interactive AI session")
            except:
                typer.echo("\n🤖 AI: ⚠️ Available but not configured")
        else:
            typer.echo("\n🤖 AI: ❌ Not available (install google-generativeai)")
        
        typer.echo()
        # Show help for the root app (this will include all subcommands)
        typer.echo(ctx.get_help())

if __name__ == "__main__":
    app() 