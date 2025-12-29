"""Run command for executing tests."""

import sys
import subprocess
from pathlib import Path
from typing import Optional

from typer import Argument, Option
from typing_extensions import Annotated

from frontend_tester.cli.utils import print_error, print_info, print_success, print_header
from frontend_tester.core.project import find_project_root


def run_command(
    path: Annotated[
        Optional[Path],
        Argument(help="Path to project (default: current directory)"),
    ] = None,
    feature: Annotated[
        Optional[str],
        Option("--feature", "-f", help="Run specific feature file"),
    ] = None,
    tag: Annotated[
        Optional[str],
        Option("--tag", "-t", help="Run tests with specific tag (e.g., @smoke)"),
    ] = None,
    browser: Annotated[
        Optional[str],
        Option("--browser", "-b", help="Override browser (chromium, firefox, webkit)"),
    ] = None,
    headed: Annotated[
        bool,
        Option("--headed", help="Run in headed mode (show browser window)"),
    ] = False,
    parallel: Annotated[
        Optional[int],
        Option("--parallel", "-n", help="Run tests in parallel (number of workers)"),
    ] = None,
    verbose: Annotated[
        bool,
        Option("--verbose", "-v", help="Verbose output"),
    ] = False,
    html_report: Annotated[
        bool,
        Option("--html", help="Generate HTML report"),
    ] = False,
) -> None:
    """Run tests using pytest-bdd.

    Executes BDD tests from the .frontend-tester/features directory using Playwright.

    Examples:
        # Run all tests
        frontend-tester run

        # Run specific feature
        frontend-tester run --feature login.feature

        # Run with tag
        frontend-tester run --tag smoke

        # Run in parallel
        frontend-tester run --parallel 4

        # Run with visible browser
        frontend-tester run --headed
    """
    print_header("Running Frontend Tests")

    # Find project root
    project_root = find_project_root(path or Path.cwd())
    if not project_root:
        print_error("Not in a Frontend Tester project. Run 'frontend-tester init' first.")
        raise SystemExit(1)

    frontend_tester_dir = project_root / ".frontend-tester"
    features_dir = frontend_tester_dir / "features"
    support_dir = frontend_tester_dir / "support"

    # Check if features exist
    if not features_dir.exists() or not any(features_dir.glob("*.feature")):
        print_error("No feature files found in .frontend-tester/features/")
        print_info("Create feature files or use 'frontend-tester generate' to create them.")
        raise SystemExit(1)

    # Build pytest command
    pytest_args = ["pytest"]

    # Add features directory (relative to .frontend-tester/)
    # Note: pytest will automatically discover conftest.py in support/ subdirectory
    pytest_args.append("features")

    # Add feature filter
    if feature:
        feature_path = features_dir / feature
        if not feature_path.exists():
            print_error(f"Feature file not found: {feature}")
            raise SystemExit(1)
        pytest_args[-1] = f"features/{feature}"

    # Add tag filter
    if tag:
        # Ensure tag starts with @
        if not tag.startswith("@"):
            tag = f"@{tag}"
        pytest_args.extend(["-m", tag.lstrip("@")])

    # Add verbosity
    if verbose:
        pytest_args.append("-vv")
    else:
        pytest_args.append("-v")

    # Add parallel execution
    if parallel:
        pytest_args.extend(["-n", str(parallel)])

    # Add HTML report
    if html_report:
        report_path = frontend_tester_dir / "reports" / "report.html"
        pytest_args.extend(["--html", "reports/report.html", "--self-contained-html"])
        print_info(f"HTML report will be saved to: {report_path}")

    # Set environment variables for overrides
    env = {}
    if browser:
        env["FRONTEND_TESTER_BROWSER"] = browser
    if headed:
        env["FRONTEND_TESTER_HEADLESS"] = "false"

    # Display command
    print_info(f"Running: {' '.join(pytest_args)}")
    if env:
        print_info(f"Environment overrides: {env}")

    print()  # Empty line

    # Run pytest
    try:
        import os

        # Merge with current environment
        full_env = os.environ.copy()
        full_env.update(env)

        result = subprocess.run(
            pytest_args,
            cwd=frontend_tester_dir,  # Run from .frontend-tester/ so pytest finds support/conftest.py
            env=full_env,
        )

        print()  # Empty line after output

        if result.returncode == 0:
            print_success("✓ All tests passed!")
            if html_report:
                print_info(f"View report: {report_path}")
        else:
            print_error(f"✗ Tests failed with exit code {result.returncode}")
            raise SystemExit(result.returncode)

    except FileNotFoundError:
        print_error("pytest not found. Make sure it's installed:")
        print_info("  uv sync --extra dev")
        raise SystemExit(1)
    except KeyboardInterrupt:
        print()  # New line after ^C
        print_info("Test run interrupted by user")
        raise SystemExit(130)
