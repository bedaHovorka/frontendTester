"""Project structure management."""

from pathlib import Path
from typing import Optional

from frontend_tester.core.config import ProjectConfig


def create_project_structure(path: Path, config: ProjectConfig) -> None:
    """
    Create the Frontend Tester project structure.

    Structure:
        .frontend-tester/
        ├── config.yaml
        ├── features/
        │   └── example.feature
        ├── steps/
        │   ├── __init__.py
        │   └── common_steps.py
        ├── support/
        │   ├── __init__.py
        │   ├── browser.py
        │   └── conftest.py
        ├── baselines/
        └── reports/
    """
    # Create main directory
    project_dir = path / ".frontend-tester"
    project_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectories
    (project_dir / "features").mkdir(exist_ok=True)
    (project_dir / "steps").mkdir(exist_ok=True)
    (project_dir / "support").mkdir(exist_ok=True)
    (project_dir / "baselines").mkdir(exist_ok=True)
    (project_dir / "reports").mkdir(exist_ok=True)

    # Save configuration
    config.save_to_file(project_dir / "config.yaml")

    # Create example feature file
    _create_example_feature(project_dir / "features" / "example.feature", config)

    # Create step definitions
    _create_step_init(project_dir / "steps" / "__init__.py")
    _create_common_steps(project_dir / "steps" / "common_steps.py")

    # Create support files
    _create_support_init(project_dir / "support" / "__init__.py")
    _create_browser_fixture(project_dir / "support" / "browser.py")
    _create_conftest(project_dir / "support" / "conftest.py")

    # Create README in project dir
    _create_project_readme(project_dir / "README.md", config)


def _create_example_feature(path: Path, config: ProjectConfig) -> None:
    """Create an example feature file."""
    content = f"""Feature: Example Web Application Test
  As a tester
  I want to verify the web application works correctly
  So that users have a good experience

  Background:
    Given I am on the homepage

  Scenario: Homepage loads successfully
    When I navigate to "{config.target_urls[0] if config.target_urls else 'http://localhost:3000'}"
    Then the page should load
    And the page title should be visible

  Scenario: Visual regression check
    Given I am on the homepage
    When the page has loaded completely
    Then the page should match the baseline "homepage"

  # TODO: Add more scenarios here
  # Use 'frontend-tester generate <url>' to auto-generate tests
"""
    path.write_text(content)


def _create_step_init(path: Path) -> None:
    """Create __init__.py for steps."""
    content = '''"""Step definitions for BDD tests."""
'''
    path.write_text(content)


def _create_common_steps(path: Path) -> None:
    """Create common step definitions."""
    content = '''"""Common step definitions used across features."""

from pytest_bdd import given, when, then, parsers

# NOTE: These are placeholder implementations
# Actual Playwright integration will be added in Phase 2


@given("I am on the homepage")
def on_homepage(browser):
    """Navigate to homepage - placeholder."""
    # TODO: Implement with Playwright in Phase 2
    pass


@when(parsers.parse('I navigate to "{url}"'))
def navigate_to_url(browser, url: str):
    """Navigate to a specific URL - placeholder."""
    # TODO: Implement with Playwright in Phase 2
    pass


@then("the page should load")
def page_loads(browser):
    """Verify page loads - placeholder."""
    # TODO: Implement with Playwright in Phase 2
    pass


@then("the page title should be visible")
def title_visible(browser):
    """Verify title is visible - placeholder."""
    # TODO: Implement with Playwright in Phase 2
    pass


@when("the page has loaded completely")
def page_loaded_completely(browser):
    """Wait for page to load completely - placeholder."""
    # TODO: Implement with Playwright in Phase 2
    pass


@then(parsers.parse('the page should match the baseline "{baseline_name}"'))
def visual_regression_check(browser, baseline_name: str):
    """Visual regression check - placeholder."""
    # TODO: Implement visual regression in Phase 4
    pass
'''
    path.write_text(content)


def _create_support_init(path: Path) -> None:
    """Create __init__.py for support."""
    content = '''"""Support utilities for tests."""
'''
    path.write_text(content)


def _create_browser_fixture(path: Path) -> None:
    """Create browser fixture placeholder."""
    content = '''"""Browser management for tests."""

# NOTE: This is a placeholder
# Actual Playwright browser fixtures will be added in Phase 2

import pytest


@pytest.fixture
def browser():
    """Browser fixture - placeholder."""
    # TODO: Implement Playwright browser setup in Phase 2
    # Will include:
    # - Browser launch (headless/headed)
    # - Context creation
    # - Page creation
    # - Cleanup
    yield None  # Placeholder
'''
    path.write_text(content)


def _create_conftest(path: Path) -> None:
    """Create pytest-bdd configuration."""
    content = '''"""pytest-bdd configuration for Frontend Tester."""

import pytest
from pathlib import Path

# Configure pytest-bdd to find features
pytest_plugins = ["pytest_bdd.plugin"]


def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Set features directory
    features_dir = Path(__file__).parent.parent / "features"
    config.option.features_base_dir = str(features_dir)


# Import fixtures from browser.py
from .browser import browser  # noqa: F401, E402
'''
    path.write_text(content)


def _create_project_readme(path: Path, config: ProjectConfig) -> None:
    """Create README in project directory."""
    content = f"""# Frontend Tester Project: {config.name}

This directory contains your Frontend Tester configuration and test files.

## Structure

- `config.yaml` - Project configuration
- `features/` - Gherkin feature files (.feature)
- `steps/` - Python step definitions
- `support/` - Browser fixtures and utilities
- `baselines/` - Visual regression baseline images
- `reports/` - Test execution reports

## Getting Started

### Run Tests (Phase 2+)
```bash
frontend-tester run
```

### Generate Tests with AI (Phase 3+)
```bash
frontend-tester generate {config.target_urls[0] if config.target_urls else "http://localhost:3000"}
```

### Update Configuration
```bash
frontend-tester config list
frontend-tester config set --key llm.model --value gpt-4
```

## Writing Tests

Feature files use Gherkin syntax. Example:

```gherkin
Feature: User Login
  Scenario: Successful login
    Given I am on the login page
    When I enter "user@example.com" in the email field
    And I click the "Login" button
    Then I should see the dashboard
```

Step definitions are in `steps/` directory.

## Next Steps

1. Edit `config.yaml` to configure your browsers, URLs, and LLM settings
2. Write feature files in `features/` directory
3. Run tests with `frontend-tester run` (coming in Phase 2)
4. Use AI to generate tests with `frontend-tester generate` (coming in Phase 3)

## Documentation

For full documentation, see: https://github.com/yourusername/frontend-tester
"""
    path.write_text(content)


def find_project_root(start_path: Optional[Path] = None) -> Optional[Path]:
    """
    Find the Frontend Tester project root by looking for .frontend-tester directory.

    Args:
        start_path: Starting directory (defaults to cwd)

    Returns:
        Path to project root or None if not found
    """
    current = start_path or Path.cwd()

    # Check current directory and all parents
    for directory in [current] + list(current.parents):
        if (directory / ".frontend-tester").is_dir():
            return directory

    return None
