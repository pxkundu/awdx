import typer
from awdx.profilyze.profile_commands import profile_app
from awdx.costlyzer.cost_commands import cost_app
from awdx.iamply.iam_commands import iam_app

app = typer.Typer(help="awdx: AWS DevOps X - Human-friendly AWS DevSecOps CLI tool.")

# Add subcommands
app.add_typer(profile_app, name="profile")
app.add_typer(cost_app, name="cost")
app.add_typer(iam_app, name="iam")

ASCII_ART = r"""
 █████╗ ██╗    ██╗█████╗ ██╗  ██╗
██╔══██╗██║    ██║██╔═██╗╚██╗██╔╝
███████║██║ █╗ ██║██║ ██║ ╚███╔╝
██╔══██║██║███╗██║██║ ██║ ██╔██╗
██║  ██║╚███╔███╔╝█████╔╝██╔╝ ██╗
╚═╝  ╚═╝ ╚══╝╚══╝ ╚════╝ ╚═╝  ╚═╝
"""

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        typer.echo(ASCII_ART)
        about_block = (
            "\u256D\u2500 About " + "\u2500" * 56 + "\u256E\n"
            "\u2502 Developed by: Partha Sarathi Kundu" + " " * 29 + "\u2502\n"
            "\u2502 Github: @pxkundu" + " " * 47 + "\u2502\n"
            "\u2570" + "\u2500" * 64 + "\u256F\n"
        )
        typer.echo(about_block)
        # Show help for the root app (this will include all subcommands)
        typer.echo(ctx.get_help())

if __name__ == "__main__":
    app() 