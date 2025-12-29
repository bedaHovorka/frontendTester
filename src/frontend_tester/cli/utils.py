"""CLI utilities for pretty output and user interaction."""

from rich.console import Console
from rich.theme import Theme

# Custom theme for Frontend Tester
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "highlight": "bold magenta",
})

# Global console instance
console = Console(theme=custom_theme)


def print_info(message: str) -> None:
    """Print an info message."""
    console.print(f"[info]ℹ[/info] {message}")


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[success]✓[/success] {message}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"[warning]⚠[/warning] {message}")


def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"[error]✗[/error] {message}")


def print_header(title: str) -> None:
    """Print a section header."""
    console.print(f"\n[bold cyan]{title}[/bold cyan]")
    console.print("─" * len(title))
