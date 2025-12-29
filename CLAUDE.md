# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with the Frontend Tester project.

## Project Overview

**Frontend Tester** is an AI-powered CLI tool for automated blackbox regression testing of frontend applications. It combines:
- **Playwright** for browser automation
- **Gherkin/Cucumber (pytest-bdd)** for BDD test scenarios
- **LiteLLM** for AI-powered test generation
- **Docker** for consistent cross-browser testing

## Development Commands

### Package Management
This project uses **uv** as the Python package manager.

```bash
# Install dependencies (creates/updates .venv and uv.lock)
uv sync

# Run the CLI tool
uv run frontend-tester --help

# Run with specific command
uv run frontend-tester init
uv run frontend-tester config list

# Run tests
uv run pytest
uv run pytest -v  # verbose
uv run pytest tests/test_cli.py  # specific file
uv run pytest --cov=frontend_tester  # with coverage

# Linting (optional)
uv run ruff check src/
uv run ruff check --fix src/
```

### Environment Setup
For AI features (Phase 3+):
```bash
# Copy example and edit
cp .env.example .env

# Add your API keys
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
```

## Project Architecture

### Directory Structure
```
frontend-tester/
├── src/frontend_tester/       # Main package
│   ├── cli/                   # CLI interface (Typer + Rich)
│   │   ├── main.py            # Entry point
│   │   ├── commands/          # Command implementations
│   │   │   ├── init.py        # Project initialization
│   │   │   └── config.py      # Configuration management
│   │   └── utils.py           # CLI utilities (console, printing)
│   ├── core/                  # Core functionality
│   │   ├── config.py          # Pydantic configuration models
│   │   └── project.py         # Project structure management
│   ├── bdd/                   # BDD/Gherkin support
│   │   ├── generator.py       # Feature file generation
│   │   ├── step_generator.py  # Step definition generation
│   │   └── templates/         # Jinja2 templates
│   ├── playwright_runner/     # Phase 2: Browser automation
│   ├── ai/                    # Phase 3: LLM integration
│   └── visual/                # Phase 4: Visual regression
├── tests/                     # Unit tests (pytest)
├── pyproject.toml             # Project configuration
├── README.md                  # User documentation
├── PLAN.md                    # Development roadmap
├── DONE.md                    # Completed work log
└── CLAUDE.md                  # This file
```

### Key Patterns

#### CLI Framework (Typer + Rich)
```python
# Command structure in cli/commands/
from typer import Typer
from rich.console import Console

from frontend_tester.cli.utils import console, print_success

def my_command():
    """Command implementation."""
    print_success("Operation completed!")
```

Commands are registered in `cli/main.py`:
```python
from frontend_tester.cli.commands import init, config

app.command(name="init")(init.init_command)
app.command(name="config")(config.config_command)
```

#### Configuration System (Pydantic)
Configuration uses Pydantic models with YAML + environment variable support:

```python
from frontend_tester.core.config import ProjectConfig, load_config

# Load config (searches: specified path → ./.frontend-tester/config.yaml → ~/.frontend-tester/config.yaml → defaults)
config = load_config()

# Access settings
config.browser.browsers  # ["chromium", "firefox"]
config.llm.provider      # "openai"

# Save config
config.save_to_file(Path(".frontend-tester/config.yaml"))
```

Priority: Environment variables > YAML file > Defaults

#### Project Structure Management
```python
from frontend_tester.core.project import create_project_structure, find_project_root

# Create .frontend-tester/ directory with all subdirectories
create_project_structure(Path("."), config)

# Find project root (looks for .frontend-tester/ directory)
root = find_project_root()  # Returns Path or None
```

#### BDD Template System (Phase 1)
Uses Jinja2 for generating feature files and step definitions:

```python
from frontend_tester.bdd.generator import generate_feature_file

generate_feature_file(
    output_path=Path(".frontend-tester/features/login.feature"),
    feature_name="User Login",
    scenarios=[{
        "name": "Successful login",
        "steps": [
            {"keyword": "Given", "text": "I am on the login page"},
            {"keyword": "When", "text": 'I enter "user@example.com" in the email field'},
            {"keyword": "Then", "text": "I should see the dashboard"},
        ]
    }]
)
```

Templates are in `src/frontend_tester/bdd/templates/`.

### Testing Strategy

#### Unit Tests
Tests use pytest and are in `tests/` directory:

- `test_cli.py` - CLI command tests (using Typer's CliRunner)
- `test_config.py` - Configuration loading/saving
- `test_project.py` - Project structure creation

Run tests: `uv run pytest -v`

**IMPORTANT: Use assertpy for assertions**
- All tests use `assertpy` for fluent, readable assertions
- Import: `from assertpy import assert_that`
- Examples:
  - `assert_that(value).is_equal_to(expected)`
  - `assert_that(result).contains("text")`
  - `assert_that(path.exists()).is_true()`
  - `assert_that(list).is_length(3)`
- For Path objects, call `.exists()` method first: `assert_that(path.exists()).is_true()`
- Never use standard `assert` statements - always use assertpy

#### Test Fixtures
Use `tempfile.TemporaryDirectory()` for isolated test environments:

```python
from assertpy import assert_that

def test_something():
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        # Test in isolated directory
        create_project_structure(project_path, config)
        assert_that((project_path / ".frontend-tester").exists()).is_true()
```

## Development Phases

### Phase 1: Project Structure + CLI (COMPLETED)
**Status**: ✅ Complete
**Files**: All current files

Key accomplishments:
- CLI framework with Typer + Rich
- Configuration system with Pydantic
- `init` and `config` commands
- BDD template system
- Unit tests (11 passing)

### Phase 2: Playwright Integration (NEXT)
**Status**: 🔜 Planned
**Files to create/modify**:
- `src/frontend_tester/playwright_runner/` - Browser management
- `.frontend-tester/support/browser.py` - Pytest fixtures
- `.frontend-tester/support/conftest.py` - Pytest configuration
- `src/frontend_tester/cli/commands/run.py` - Run command

Key tasks:
- Add Playwright to dependencies
- Implement browser fixtures
- Create step definitions with Playwright
- Docker integration for multi-browser testing
- Implement `frontend-tester run` command

### Phase 3: AI Test Generation (FUTURE)
**Status**: 📋 Planned
**Files to create**:
- `src/frontend_tester/ai/client.py` - LiteLLM wrapper
- `src/frontend_tester/ai/prompts/` - Prompt templates
- `src/frontend_tester/cli/commands/generate.py` - Generate command
- `src/frontend_tester/cli/commands/analyze.py` - Analyze command

Key tasks:
- Integrate LiteLLM
- UI analysis (DOM extraction, element identification)
- Gherkin scenario generation from analysis
- Step definition generation

### Phase 4: Visual Regression (FUTURE)
**Status**: 📋 Planned

### Phase 5: Fix/Autofix System (FUTURE)
**Status**: 📋 Planned (details TBD)

## Common Development Tasks

### Adding a New CLI Command

1. Create command file in `src/frontend_tester/cli/commands/`:
```python
# src/frontend_tester/cli/commands/my_command.py
from typer import Argument
from typing_extensions import Annotated

from frontend_tester.cli.utils import print_success

def my_command(
    arg: Annotated[str, Argument(help="Description")],
) -> None:
    """Command description."""
    # Implementation
    print_success("Done!")
```

2. Register in `src/frontend_tester/cli/main.py`:
```python
from frontend_tester.cli.commands import my_command

app.command(name="my-command")(my_command.my_command)
```

3. Add tests in `tests/test_cli.py`

### Modifying Configuration

1. Update Pydantic models in `src/frontend_tester/core/config.py`
2. Add validators if needed
3. Update tests in `tests/test_config.py`
4. Document in README.md

### Adding New Templates

1. Create Jinja2 template in `src/frontend_tester/bdd/templates/`
2. Add generator function in `bdd/generator.py` or `bdd/step_generator.py`
3. Use in command implementations

## Code Style and Best Practices

### Type Hints
Use type hints everywhere (Python 3.11+ syntax):
```python
def my_function(path: Path, config: ProjectConfig) -> None:
    """Function with type hints."""
    pass
```

### Error Handling
Use Rich console for user-facing errors:
```python
from frontend_tester.cli.utils import print_error

try:
    # Operation
    pass
except Exception as e:
    print_error(f"Failed: {e}")
    raise typer.Exit(1)
```

### Async/Await
Prepare for async operations (Phase 2+):
```python
async def async_function():
    """Use async for IO-bound operations."""
    pass
```

### Testing
- Write tests for all new functionality
- Use descriptive test names: `test_<what>_<scenario>`
- Keep tests isolated (use temp directories)
- Aim for high coverage

## Common Issues and Solutions

### Issue: CLI command not found
**Solution**: Run `uv sync` to reinstall package after adding new commands

### Issue: Import errors
**Solution**: Ensure `__init__.py` files exist in all package directories

### Issue: Config not loading
**Solution**: Check config file exists at correct path, verify YAML syntax

### Issue: Tests failing
**Solution**:
1. Check if dependencies are installed: `uv sync`
2. Run tests with verbose output: `uv run pytest -v`
3. Check temporary directory cleanup in tests

## Documentation

- **README.md** - User-facing documentation, installation, quick start
- **PLAN.md** - Development roadmap, task breakdown, timeline
- **DONE.md** - Completed work log, changelog
- **CLAUDE.md** - This file, development guide for Claude Code

## Workflow Tips

### Starting Work on a Phase
1. Review PLAN.md for tasks
2. Update DONE.md with progress
3. Create/modify files as needed
4. Write tests
5. Run `uv run pytest` to validate
6. Update documentation

### Before Committing
1. Run tests: `uv run pytest`
2. Run linting: `uv run ruff check src/`
3. Update DONE.md with completed work
4. Update PLAN.md if tasks change

### User Interaction
- Use Rich console utilities from `cli/utils.py`
- Provide clear, actionable error messages
- Use progress indicators for long operations
- Show helpful next steps after operations

## References

- **Typer**: https://typer.tiangolo.com/
- **Rich**: https://rich.readthedocs.io/
- **Pydantic**: https://docs.pydantic.dev/
- **pytest-bdd**: https://pytest-bdd.readthedocs.io/
- **Playwright**: https://playwright.dev/python/
- **LiteLLM**: https://docs.litellm.ai/

## Notes for Claude Code

- This is an incremental project - work is done phase by phase
- Current focus: Complete Phase 1, then move to Phase 2 (Playwright)
- User wants tracking files (PLAN.md, DONE.md) updated frequently
- BDD/Gherkin format is core to the project - maintain this approach
- AI features (Phase 3) will use LiteLLM for unified LLM access
- Keep CLI user experience high priority - use Rich for beautiful output
