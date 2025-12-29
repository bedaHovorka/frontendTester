"""Project structure management."""

from pathlib import Path
from typing import Optional

from jinja2 import Environment, PackageLoader

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

    # Create test file to register scenarios
    _create_test_file(project_dir / "features" / "test_features.py")

    # Create step definitions
    _create_step_init(project_dir / "steps" / "__init__.py")
    _create_common_steps(project_dir / "steps" / "test_common_steps.py")

    # Create support files
    _create_support_init(project_dir / "support" / "__init__.py")
    _create_browser_fixture(project_dir / "support" / "browser.py")
    _create_conftest(project_dir / "support" / "conftest.py")

    # Create root conftest.py that imports everything
    _create_root_conftest(project_dir / "conftest.py")

    # Create README in project dir
    _create_project_readme(project_dir / "README.md", config)


def _create_example_feature(path: Path, config: ProjectConfig) -> None:
    """Create an example feature file."""
    target_url = config.target_urls[0] if config.target_urls else "https://example.com"

    content = f"""Feature: Example Web Application Test
  As a tester
  I want to verify the web application works correctly
  So that users have a good experience

  @smoke
  Scenario: Homepage loads successfully
    Given I am on "{target_url}"
    Then I should see "Example Domain"
    And the page title should be "Example Domain"

  @smoke
  Scenario: Page title verification
    Given I am on "{target_url}"
    Then the URL should be "{target_url}"
    And the page title should contain "Example"

  @regression
  Scenario: Content verification
    Given I am on "{target_url}"
    Then I should see "This domain is for use in illustrative examples"
    And I should see "More information"

  # TODO: Add more scenarios here
  # Use 'frontend-tester generate <url>' to auto-generate tests
"""
    path.write_text(content)


def _create_test_file(path: Path) -> None:
    """Create test file to register scenarios."""
    content = '''"""Auto-generated test file for BDD scenarios.

This file registers all scenarios from feature files so pytest can discover them.
pytest-bdd requires test files (test_*.py) to link feature files to test execution.
"""

import sys
from pathlib import Path
from pytest_bdd import scenarios

# Get the directory containing this file (features/)
FEATURES_DIR = Path(__file__).parent

# Add parent directory to path so we can import from steps/
sys.path.insert(0, str(FEATURES_DIR.parent))

# Import step definitions so they get registered with pytest-bdd
from steps import common_steps  # noqa: F401, E402

# Register all scenarios from all .feature files in this directory
# This creates a pytest test for each scenario in each feature file
for feature_file in FEATURES_DIR.glob("*.feature"):
    scenarios(feature_file.name)
'''
    path.write_text(content)


def _create_step_init(path: Path) -> None:
    """Create __init__.py for steps."""
    content = '''"""Step definitions for BDD tests."""
'''
    path.write_text(content)


def _create_common_steps(path: Path) -> None:
    """Create common step definitions."""
    # Copy common steps from the bdd module
    import importlib.resources

    # Read the common_steps.py from the bdd package
    from frontend_tester.bdd import common_steps
    import inspect

    content = inspect.getsource(common_steps)
    path.write_text(content)


def _create_support_init(path: Path) -> None:
    """Create __init__.py for support."""
    content = '''"""Support utilities for tests."""
'''
    path.write_text(content)


def _create_browser_fixture(path: Path) -> None:
    """Create browser fixture with Playwright."""
    # Use Jinja2 template for browser fixtures
    env = Environment(loader=PackageLoader("frontend_tester", "bdd/templates"))
    template = env.get_template("browser.jinja2")
    content = template.render()
    path.write_text(content)


def _create_conftest(path: Path) -> None:
    """Create pytest-bdd configuration."""
    # NOTE: This creates conftest.py in support/ directory
    # The root conftest.py is created separately below
    env = Environment(loader=PackageLoader("frontend_tester", "bdd/templates"))
    template = env.get_template("conftest.jinja2")
    content = template.render()
    path.write_text(content)


def _create_root_conftest(path: Path) -> None:
    """Create root conftest.py that imports fixtures and step definitions."""
    content = '''"""Root conftest.py for pytest configuration and fixture discovery.

This file ensures pytest discovers:
- Fixtures from support/browser.py
- Configuration from support/conftest.py
- Step definitions (imported directly here)
"""

import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import fixtures and configuration from support
from support.conftest import *  # noqa: F403, F401

# Import ALL step definitions directly
# NOTE: pytest-bdd 8.x requires step definitions to be in conftest.py or test files
# Simply importing from another module doesn't work
from steps.test_common_steps import *  # noqa: F403, F401
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
