"""Init command implementation."""

from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated
from rich.prompt import Prompt, Confirm

from frontend_tester.cli.utils import (
    console,
    print_success,
    print_error,
    print_info,
    print_header,
)
from frontend_tester.core.config import ProjectConfig, BrowserConfig, LLMConfig
from frontend_tester.core.project import create_project_structure


def init_command(
    path: Annotated[
        Optional[Path],
        typer.Argument(help="Path to initialize project (default: current directory)"),
    ] = None,
    name: Annotated[
        Optional[str],
        typer.Option("--name", "-n", help="Project name"),
    ] = None,
    url: Annotated[
        Optional[str],
        typer.Option("--url", "-u", help="Target URL to test"),
    ] = None,
    non_interactive: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Skip prompts, use defaults"),
    ] = False,
) -> None:
    """
    Initialize a new Frontend Tester test repository.

    Creates test directory structure with:
    • config.yaml - Configuration
    • features/ - Test features (example + AI-generated)
    • steps/ - Step definitions
    • support/ - Browser fixtures and pytest config
    """
    target_path = path or Path.cwd()

    # Check if project already exists
    config_file = target_path / "config.yaml"
    if config_file.exists():
        print_error(f"Frontend Tester project already exists at {target_path}")
        print_info("Run 'frontend-tester config' to view/edit configuration")
        raise typer.Exit(1)

    print_header("Frontend Tester - Test Repository Initialization")
    console.print("\nThis wizard will help you set up a new test repository.\n")

    # Get project configuration
    if non_interactive:
        config = _get_default_config(name, url)
    else:
        config = _get_config_interactive(name, url)

    # Create project structure
    try:
        print_info("Creating test repository structure...")
        create_project_structure(target_path, config)
        print_success("Test repository created")

        # Display summary
        _display_summary(target_path, config)

    except Exception as e:
        print_error(f"Failed to create test repository: {e}")
        raise typer.Exit(1)


def _get_default_config(
    name: Optional[str] = None, url: Optional[str] = None
) -> ProjectConfig:
    """Get default configuration."""
    return ProjectConfig(
        name=name or "my-tests",
        target_urls=[url] if url else ["http://localhost:3000"],
        browser=BrowserConfig(browsers=["chromium"], headless=True),
        llm=LLMConfig(provider="openai", model="gpt-4"),
    )


def _get_config_interactive(
    name: Optional[str] = None, url: Optional[str] = None
) -> ProjectConfig:
    """Get configuration through interactive prompts."""
    # Project name
    project_name = name or Prompt.ask(
        "[cyan]Project name[/cyan]", default="my-tests"
    )

    # Target URL(s)
    if url:
        target_urls = [url]
    else:
        url_input = Prompt.ask(
            "[cyan]Target URL to test[/cyan]", default="http://localhost:3000"
        )
        target_urls = [url_input]

    # Browser selection
    console.print("\n[cyan]Select browsers to test:[/cyan]")
    console.print("  1. Chromium (Chrome/Edge) - Recommended")
    console.print("  2. Firefox")
    console.print("  3. WebKit (Safari)")
    console.print("  4. All browsers")

    browser_choice = Prompt.ask("Choice", choices=["1", "2", "3", "4"], default="1")

    browser_map = {
        "1": ["chromium"],
        "2": ["firefox"],
        "3": ["webkit"],
        "4": ["chromium", "firefox", "webkit"],
    }
    browsers = browser_map[browser_choice]

    # Headless mode
    headless = Confirm.ask(
        "[cyan]Run browsers in headless mode?[/cyan]", default=True
    )

    # Docker usage
    use_docker = Confirm.ask(
        "[cyan]Use Docker for browser testing?[/cyan] (recommended for CI/CD)",
        default=False,
    )

    # LLM provider
    console.print("\n[cyan]Select LLM provider for AI features:[/cyan]")
    console.print("  1. OpenAI (GPT-4)")
    console.print("  2. Anthropic (Claude)")

    llm_choice = Prompt.ask("Choice", choices=["1", "2"], default="1")

    llm_provider = "openai" if llm_choice == "1" else "anthropic"
    llm_model = "gpt-4" if llm_choice == "1" else "claude-sonnet-4"

    return ProjectConfig(
        name=project_name,
        target_urls=target_urls,
        browser=BrowserConfig(
            browsers=browsers,
            headless=headless,
        ),
        docker={"enabled": use_docker},
        llm=LLMConfig(
            provider=llm_provider,
            model=llm_model,
        ),
    )


def _display_summary(path: Path, config: ProjectConfig) -> None:
    """Display project creation summary."""
    console.print("\n[bold green]✓ Test repository initialized successfully![/bold green]\n")

    console.print("[bold cyan]Repository Details:[/bold cyan]")
    console.print(f"  Name: {config.name}")
    console.print(f"  Location: {path.absolute()}")
    console.print(f"  Config: {path / 'config.yaml'}")
    console.print(f"  Target URLs: {', '.join(config.target_urls)}")
    console.print(f"  Browsers: {', '.join(config.browser.browsers)}")
    console.print(f"  LLM: {config.llm.provider} ({config.llm.model})")

    console.print("\n[bold cyan]Structure Created:[/bold cyan]")
    console.print("  [cyan]config.yaml[/cyan] - Configuration file")
    console.print("  [cyan]features/[/cyan] - Gherkin feature files (example + AI-generated)")
    console.print("  [cyan]steps/[/cyan] - Python step definitions")
    console.print("  [cyan]support/[/cyan] - Browser fixtures and pytest config")
    console.print("  [cyan]analysis/[/cyan] - UI analysis JSON files")
    console.print("  [cyan]baselines/[/cyan] - Visual regression baselines")
    console.print("  [cyan]reports/[/cyan] - Test execution reports")

    console.print("\n[bold cyan]Next Steps:[/bold cyan]")
    console.print("  1. Check the README:")
    console.print("     [dim]$ cat README.md[/dim]")
    console.print("\n  2. Run the example tests:")
    console.print("     [dim]$ pytest -v[/dim]")
    console.print("\n  3. Set your API keys in .env file:")
    console.print("     [dim]OPENAI_API_KEY=sk-...[/dim]")
    console.print("     [dim]ANTHROPIC_API_KEY=sk-ant-...[/dim]")
    console.print("\n  4. Generate tests with AI:")
    console.print(f"     [dim]$ frontend-tester generate {config.target_urls[0]}[/dim]")
    console.print("\n  5. View/edit configuration:")
    console.print("     [dim]$ frontend-tester config list[/dim]")

    console.print(
        "\n[dim]For more information, see README.md in this directory[/dim]\n"
    )
