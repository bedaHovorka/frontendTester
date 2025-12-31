"""Project structure management."""

from pathlib import Path
from typing import Optional

from jinja2 import Environment, PackageLoader

from frontend_tester.core.config import ProjectConfig


def create_project_structure(path: Path, config: ProjectConfig) -> None:
    """
    Create the Frontend Tester project structure with two directories:

    1. .frontend-tester/ - Configuration and AI-generated tests (empty initially)
    2. TEST_DIR/ - Visible example tests for learning

    Structure:
        .frontend-tester/           # Hidden directory for config and generated content
        ├── config.yaml             # Configuration
        ├── features/               # AI-generated test features (empty initially)
        ├── steps/                  # AI-generated step definitions (empty initially)
        ├── support/                # Support utilities (empty initially)
        ├── baselines/              # Visual regression baselines
        ├── reports/                # Test execution reports
        └── README.md               # Configuration documentation

        TEST_DIR/                   # Visible example tests
        ├── features/               # Example feature files
        │   ├── example.feature
        │   └── test_features.py
        ├── steps/                  # Example step definitions
        │   ├── __init__.py
        │   └── test_common_steps.py
        ├── support/                # Test support utilities
        │   ├── __init__.py
        │   ├── browser.py
        │   └── conftest.py
        ├── conftest.py             # Root pytest configuration
        └── README.md               # Getting started guide
    """
    # Create .frontend-tester/ directory structure (for config and generated content)
    frontend_tester_dir = path / ".frontend-tester"
    frontend_tester_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectories in .frontend-tester/ (empty, for generated content)
    (frontend_tester_dir / "features").mkdir(exist_ok=True)
    (frontend_tester_dir / "steps").mkdir(exist_ok=True)
    (frontend_tester_dir / "support").mkdir(exist_ok=True)
    (frontend_tester_dir / "baselines").mkdir(exist_ok=True)
    (frontend_tester_dir / "reports").mkdir(exist_ok=True)

    # Save configuration to .frontend-tester/
    config.save_to_file(frontend_tester_dir / "config.yaml")

    # Create README in .frontend-tester/
    _create_project_readme(frontend_tester_dir / "README.md", config)

    # Create TEST_DIR/ directory structure (with examples)
    test_dir = path / "TEST_DIR"
    test_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectories in TEST_DIR/
    (test_dir / "features").mkdir(exist_ok=True)
    (test_dir / "steps").mkdir(exist_ok=True)
    (test_dir / "support").mkdir(exist_ok=True)

    # Create example feature file in TEST_DIR/
    _create_example_feature(test_dir / "features" / "example.feature", config)

    # Create test file to register scenarios in TEST_DIR/
    _create_test_file(test_dir / "features" / "test_features.py")

    # Create step definitions in TEST_DIR/
    _create_step_init(test_dir / "steps" / "__init__.py")
    _create_common_steps(test_dir / "steps" / "test_common_steps.py")

    # Create support files in TEST_DIR/
    _create_support_init(test_dir / "support" / "__init__.py")
    _create_browser_fixture(test_dir / "support" / "browser.py")
    _create_conftest(test_dir / "support" / "conftest.py")

    # Create root conftest.py in TEST_DIR/
    _create_root_conftest(test_dir / "conftest.py")

    # Create README in TEST_DIR/
    _create_test_dir_readme(test_dir / "README.md", config)


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
    """Create README in .frontend-tester/ directory."""
    content = f"""# Frontend Tester Configuration: {config.name}

This directory (`.frontend-tester/`) contains project **configuration** and **AI-generated test content**.

## Structure

- `config.yaml` - Project configuration (browsers, LLM settings, etc.)
- `features/` - AI-generated Gherkin feature files (empty initially)
- `steps/` - AI-generated step definitions (empty initially)
- `support/` - Support utilities (empty initially)
- `baselines/` - Visual regression baseline images
- `reports/` - Test execution reports

## Configuration

Edit `config.yaml` to configure:
- Target URLs for testing
- Browser settings (chromium, firefox, webkit)
- LLM provider and model for AI generation
- Visual regression settings

View current configuration:
```bash
frontend-tester config list
```

Update settings:
```bash
frontend-tester config set --key llm.model --value gpt-4
frontend-tester config set --key browser.headless --value false
```

## Generating Tests

Generate tests from a URL:
```bash
frontend-tester generate {config.target_urls[0] if config.target_urls else "http://localhost:3000"}
```

Generated tests will be placed in this directory's subdirectories.

## Example Tests

For learning and reference, check out the `TEST_DIR/` directory which contains:
- Example feature files
- Example step definitions
- Working pytest configuration
- Ready-to-run tests

## Documentation

For full documentation, see: https://github.com/yourusername/frontend-tester
"""
    path.write_text(content)


def _create_test_dir_readme(path: Path, config: ProjectConfig) -> None:
    """Create README in TEST_DIR/ directory."""
    content = f"""# Frontend Tester Example Tests: {config.name}

This directory (`TEST_DIR/`) contains **example tests** to help you learn how to use Frontend Tester.

## Quick Start

Run the example tests:
```bash
cd TEST_DIR
pytest -v
```

Run with a specific browser:
```bash
pytest -v --browser chromium
pytest -v --browser firefox
```

Run specific test tags:
```bash
pytest -v -m smoke         # Run smoke tests only
pytest -v -m regression    # Run regression tests only
```

## Structure

- `features/` - Example Gherkin feature files
  - `example.feature` - Example scenarios for {config.target_urls[0] if config.target_urls else "https://example.com"}
  - `test_features.py` - Test file to register scenarios
- `steps/` - Example step definitions with Playwright
  - `test_common_steps.py` - Common steps (Given, When, Then)
- `support/` - Browser fixtures and pytest configuration
  - `browser.py` - Playwright browser fixtures
  - `conftest.py` - pytest configuration
- `conftest.py` - Root pytest configuration

## Learning Path

1. **Read `features/example.feature`** - See how Gherkin scenarios are written
2. **Explore `steps/test_common_steps.py`** - Understand step definitions and Playwright usage
3. **Check `support/browser.py`** - Learn about browser fixtures
4. **Run tests** - Execute `pytest -v` to see everything in action
5. **Modify examples** - Try changing scenarios or adding new steps

## Configuration

This test directory uses configuration from `../.frontend-tester/config.yaml`.

View configuration:
```bash
cd ..
frontend-tester config list
```

## AI-Generated Tests

Once you're comfortable with the examples, generate tests for your application:

```bash
cd ..
frontend-tester generate {config.target_urls[0] if config.target_urls else "http://localhost:3000"}
```

Generated tests will be placed in `../.frontend-tester/features/` and `../.frontend-tester/steps/`.

## Next Steps

- Customize `features/example.feature` for your use case
- Add new step definitions in `steps/`
- Run tests in CI/CD pipelines
- Explore visual regression testing (Phase 4)

## Documentation

For full documentation, see: https://github.com/yourusername/frontend-tester
"""
    path.write_text(content)


def find_project_root(start_path: Optional[Path] = None) -> Optional[Path]:
    """
    Find the Frontend Tester project root by looking for .frontend-tester/ directory.

    Args:
        start_path: Starting directory (defaults to cwd)

    Returns:
        Path to project root or None if not found
    """
    current = start_path or Path.cwd()

    # Check current directory and all parents
    for directory in [current] + list(current.parents):
        # Look for .frontend-tester/ directory
        if (directory / ".frontend-tester").is_dir():
            return directory

    return None
