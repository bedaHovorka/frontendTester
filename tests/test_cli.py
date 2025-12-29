"""Tests for CLI functionality."""

from typer.testing import CliRunner
from assertpy import assert_that

from frontend_tester.cli.main import app
from frontend_tester import __version__

runner = CliRunner()


def test_version():
    """Test --version flag."""
    result = runner.invoke(app, ["--version"])
    assert_that(result.exit_code).is_equal_to(0)
    assert_that(result.stdout).contains("Frontend Tester")
    assert_that(result.stdout).contains(__version__)


def test_help():
    """Test --help flag."""
    result = runner.invoke(app, ["--help"])
    assert_that(result.exit_code).is_equal_to(0)
    assert_that(result.stdout).contains("frontend-tester")
    assert_that(result.stdout).contains("AI-powered")


def test_no_args():
    """Test running with no arguments shows help."""
    result = runner.invoke(app, [])
    # Typer returns exit code 2 when no_args_is_help=True
    assert_that(result.exit_code).is_equal_to(2)
    assert_that(result.stdout).contains("Usage:")


def test_init_help():
    """Test init command help."""
    result = runner.invoke(app, ["init", "--help"])
    assert_that(result.exit_code).is_equal_to(0)
    assert_that(result.stdout).contains("Initialize")


def test_config_help():
    """Test config command help."""
    result = runner.invoke(app, ["config", "--help"])
    assert_that(result.exit_code).is_equal_to(0)
    assert_that(result.stdout).contains("Manage")
