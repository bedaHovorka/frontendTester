"""Generate command for test generation."""

import asyncio
import json
from pathlib import Path

from typing_extensions import Annotated
import typer

from frontend_tester.ai.analyzer import UIAnalyzer
from frontend_tester.ai.client import LLMClient
from frontend_tester.ai.generator import TestGenerator
from frontend_tester.cli.utils import console, print_error, print_info, print_success
from frontend_tester.core.config import load_config
from frontend_tester.playwright_runner.browser_manager import BrowserManager


async def generate_tests_async(
    url: str,
    output_dir: Path,
    app_name: str,
    browser_type: str,
    headless: bool,
    analysis_file: Path | None,
) -> None:
    """Async implementation of test generation."""
    config = load_config()

    # Validate LLM configuration
    if not config.llm.api_key:
        print_error("LLM API key not configured. Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable.")
        raise typer.Exit(1)

    print_info(f"Generating tests for: {url}")
    print_info(f"Using LLM: {config.llm.provider}/{config.llm.model}")
    print_info(f"Output directory: {output_dir}")

    # Initialize components
    llm_client = LLMClient(config.llm)
    analyzer = UIAnalyzer(llm_client)
    generator = TestGenerator(llm_client)

    # Get analysis
    if analysis_file and analysis_file.exists():
        print_info(f"Loading existing analysis from: {analysis_file}")
        with open(analysis_file, "r") as f:
            analysis = json.load(f)
    else:
        print_info("No existing analysis found. Analyzing page...")
        # Launch browser and analyze
        async with BrowserManager(config.browser) as manager:
            page = await manager.create_page(browser_type)

            # Navigate to URL
            print_info(f"Navigating to {url}...")
            await page.goto(url, wait_until="networkidle", timeout=60000)

            # Analyze page
            print_info("Analyzing page structure...")
            analysis = await analyzer.analyze_page(page)

            # Save analysis
            analysis_output = output_dir / "analysis" / "analysis.json"
            await analyzer.save_analysis(analysis, analysis_output)
            print_success(f"Analysis saved to: {analysis_output}")

            await page.close()

    # Generate tests
    print_info("Generating test scenarios...")
    generated_files = await generator.generate_complete_test_suite(
        app_name=app_name,
        url=url,
        analysis=analysis,
        output_dir=output_dir,
    )

    # Display results
    console.print("\n[bold green]Generated Files:[/bold green]")
    for file_type, file_path in generated_files.items():
        console.print(f"  • {file_type}: {file_path}")

    print_success(f"\nTest generation complete! Generated {len(generated_files)} files.")
    print_info(f"\nNext steps:")
    print_info(f"  1. Review generated files in: {output_dir}")
    print_info(f"  2. Customize scenarios as needed")
    print_info(f"  3. Run tests with: frontend-tester run")


def generate_command(
    url: Annotated[str, typer.Argument(help="URL to generate tests for")],
    output_dir: Annotated[
        Path, typer.Option("--output-dir", "-o", help="Output directory for generated tests")
    ] = Path("."),
    app_name: Annotated[
        str, typer.Option("--app-name", "-n", help="Application name")
    ] = "My App",
    browser: Annotated[
        str, typer.Option("--browser", "-b", help="Browser to use")
    ] = "chromium",
    headed: Annotated[
        bool, typer.Option("--headed", help="Run browser in headed mode")
    ] = False,
    analysis_file: Annotated[
        Path | None, typer.Option("--analysis", "-a", help="Existing analysis file to use")
    ] = None,
) -> None:
    """
    Generate BDD test scenarios from a web page.

    This command analyzes the page (or uses existing analysis) and generates
    Gherkin feature files and pytest-bdd step definitions.

    Example:
        frontend-tester generate http://localhost:3000
        frontend-tester generate http://localhost:3000 --output-dir /tmp/tests
        frontend-tester generate http://localhost:3000 --analysis analysis.json
        frontend-tester generate http://localhost:3000 --app-name "My App" --browser firefox
    """
    try:
        asyncio.run(
            generate_tests_async(
                url=url,
                output_dir=output_dir,
                app_name=app_name,
                browser_type=browser,
                headless=not headed,
                analysis_file=analysis_file,
            )
        )
    except Exception as e:
        print_error(f"Test generation failed: {e}")
        raise typer.Exit(1)
