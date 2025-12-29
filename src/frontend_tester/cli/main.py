"""Main CLI entry point for Frontend Tester."""

import typer
from typing_extensions import Annotated

from frontend_tester import __version__
from frontend_tester.cli.utils import console, print_header
from frontend_tester.cli.commands import init, config as config_cmd, run as run_cmd

# Create the main Typer app
app = typer.Typer(
    name="frontend-tester",
    help="AI-powered CLI tool for automated frontend regression testing",
    add_completion=False,
    no_args_is_help=True,
    rich_markup_mode="rich",
)


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"[bold cyan]Frontend Tester[/bold cyan] version [bold]{__version__}[/bold]")
        console.print("\nAI-powered blackbox regression testing for frontend applications")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-v",
            help="Show version and exit",
            callback=version_callback,
            is_eager=True,
        ),
    ] = False,
) -> None:
    """
    Frontend Tester - AI-powered frontend regression testing tool.

    A CLI tool for creating and running blackbox regression tests using:
    • Playwright for browser automation
    • Gherkin/Cucumber for BDD test scenarios
    • LiteLLM for AI-powered test generation
    • Docker for multi-browser/OS testing
    """
    pass


# Register subcommands
app.command(name="init")(init.init_command)
app.command(name="config")(config_cmd.config_command)
app.command(name="run")(run_cmd.run_command)


# Placeholder commands for future implementation
@app.command()
def generate(
    url: Annotated[str, typer.Argument(help="URL of the application to test")],
) -> None:
    """
    Generate tests from a URL using AI analysis.

    [yellow]Coming in Phase 3: AI Test Generation[/yellow]
    """
    console.print("[yellow]This command is not yet implemented.[/yellow]")
    console.print("It will be available in Phase 3: AI Test Generation")


@app.command()
def analyze(
    url: Annotated[str, typer.Argument(help="URL of the application to analyze")],
) -> None:
    """
    Analyze UI and suggest test scenarios.

    [yellow]Coming in Phase 3: AI Test Generation[/yellow]
    """
    console.print("[yellow]This command is not yet implemented.[/yellow]")
    console.print("It will be available in Phase 3: AI Test Generation")


if __name__ == "__main__":
    app()
