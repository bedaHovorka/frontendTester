"""Config command implementation."""

from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated
from rich.table import Table

from frontend_tester.cli.utils import console, print_success, print_error, print_info
from frontend_tester.core.config import ProjectConfig, load_config


def config_command(
    action: Annotated[
        Optional[str],
        typer.Argument(help="Action: list, get, set"),
    ] = "list",
    key: Annotated[
        Optional[str],
        typer.Option("--key", "-k", help="Config key (e.g., 'llm.model')"),
    ] = None,
    value: Annotated[
        Optional[str],
        typer.Option("--value", "-v", help="Config value to set"),
    ] = None,
    global_config: Annotated[
        bool,
        typer.Option("--global", "-g", help="Use global config"),
    ] = False,
) -> None:
    """
    Manage Frontend Tester configuration.

    Examples:
      frontend-tester config list
      frontend-tester config get --key llm.model
      frontend-tester config set --key llm.model --value gpt-4
    """
    config_path = (
        ProjectConfig.get_global_config_path()
        if global_config
        else ProjectConfig.get_default_config_path()
    )

    if action == "list":
        _list_config(config_path)
    elif action == "get":
        if not key:
            print_error("--key is required for 'get' action")
            raise typer.Exit(1)
        _get_config(config_path, key)
    elif action == "set":
        if not key or not value:
            print_error("Both --key and --value are required for 'set' action")
            raise typer.Exit(1)
        _set_config(config_path, key, value)
    else:
        print_error(f"Unknown action: {action}. Use 'list', 'get', or 'set'")
        raise typer.Exit(1)


def _list_config(config_path: Path) -> None:
    """List all configuration values."""
    try:
        config = load_config(config_path if config_path.exists() else None)
    except FileNotFoundError:
        print_error(f"Config file not found: {config_path}")
        print_info("Run 'frontend-tester init' to create a project configuration")
        raise typer.Exit(1)

    console.print(f"\n[bold cyan]Configuration[/bold cyan] ({config_path})\n")

    # Create a table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Setting", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")

    # Project settings
    table.add_row("project.name", config.name)
    table.add_row("project.target_urls", ", ".join(config.target_urls))

    # Browser settings
    table.add_row("browser.browsers", ", ".join(config.browser.browsers))
    table.add_row("browser.headless", str(config.browser.headless))
    table.add_row("browser.timeout", f"{config.browser.timeout}ms")

    # Docker settings
    table.add_row("docker.enabled", str(config.docker.enabled))

    # LLM settings
    table.add_row("llm.provider", config.llm.provider)
    table.add_row("llm.model", config.llm.model)
    table.add_row("llm.api_key", "***" if config.llm.api_key else "(not set)")

    # Visual regression settings
    table.add_row("visual_regression.enabled", str(config.visual_regression.enabled))
    table.add_row("visual_regression.threshold", str(config.visual_regression.threshold))

    console.print(table)
    console.print()


def _get_config(config_path: Path, key: str) -> None:
    """Get a specific configuration value."""
    try:
        config = load_config(config_path if config_path.exists() else None)
    except FileNotFoundError:
        print_error(f"Config file not found: {config_path}")
        raise typer.Exit(1)

    # Parse nested key
    parts = key.split(".")
    value = config.model_dump()

    try:
        for part in parts:
            value = value[part]
        console.print(f"[cyan]{key}[/cyan] = [white]{value}[/white]")
    except (KeyError, TypeError):
        print_error(f"Config key not found: {key}")
        raise typer.Exit(1)


def _set_config(config_path: Path, key: str, value: str) -> None:
    """Set a configuration value."""
    try:
        config = load_config(config_path if config_path.exists() else None)
    except FileNotFoundError:
        print_error(f"Config file not found: {config_path}")
        print_info("Run 'frontend-tester init' to create a configuration")
        raise typer.Exit(1)

    # Parse nested key
    parts = key.split(".")
    config_dict = config.model_dump()

    # Navigate to the parent of the target key
    current = config_dict
    for part in parts[:-1]:
        if part not in current:
            print_error(f"Invalid config path: {key}")
            raise typer.Exit(1)
        current = current[part]

    # Set the value
    last_key = parts[-1]
    if last_key not in current:
        print_error(f"Config key not found: {key}")
        raise typer.Exit(1)

    # Try to convert value to the right type
    old_value = current[last_key]
    if isinstance(old_value, bool):
        value = value.lower() in ("true", "yes", "1")
    elif isinstance(old_value, int):
        value = int(value)
    elif isinstance(old_value, float):
        value = float(value)
    elif isinstance(old_value, list):
        value = [v.strip() for v in value.split(",")]

    current[last_key] = value

    # Save the updated config
    try:
        updated_config = ProjectConfig(**config_dict)
        updated_config.save_to_file(config_path)
        print_success(f"Updated {key} = {value}")
    except Exception as e:
        print_error(f"Failed to save config: {e}")
        raise typer.Exit(1)
