# Frontend Tester

**AI-powered CLI tool for automated blackbox regression testing of frontend applications**

Frontend Tester is a specialized testing tool that combines the power of browser automation (Playwright), behavior-driven development (Gherkin/Cucumber), and AI (LiteLLM) to create and run comprehensive frontend regression tests.

## Features

### Current (Phase 1)
- CLI framework with beautiful terminal output (Typer + Rich)
- Project initialization with `frontend-tester init`
- Configuration management (YAML + environment variables)
- BDD/Gherkin test structure setup
- Template system for test generation

### Coming Soon
- **Phase 2**: Playwright integration with Docker for multi-browser testing
- **Phase 3**: AI-powered test generation using LiteLLM (OpenAI + Anthropic)
- **Phase 4**: Visual regression testing with screenshot comparison
- **Phase 5**: Self-healing tests and auto-fix capabilities

## Installation

### Prerequisites
- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Install with UV

```bash
# Clone the repository
git clone https://github.com/yourusername/frontend-tester.git
cd frontend-tester

# Install dependencies
uv sync

# Verify installation
uv run frontend-tester --version
```

## Quick Start

### 1. Initialize a New Project

```bash
# Interactive setup
uv run frontend-tester init

# Or with options
uv run frontend-tester init --name my-app-tests --url http://localhost:3000
```

This creates a `.frontend-tester/` directory with:
- `config.yaml` - Project configuration
- `features/` - Gherkin feature files
- `steps/` - Python step definitions
- `support/` - Browser fixtures and utilities
- `baselines/` - Visual regression baselines
- `reports/` - Test execution reports

### 2. Configure API Keys

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

Edit `.env`:
```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### 3. Write Test Scenarios

Edit `.frontend-tester/features/example.feature`:

```gherkin
Feature: User Login
  As a user
  I want to log into the application
  So that I can access my account

  Scenario: Successful login
    Given I am on the login page
    When I enter "user@example.com" in the email field
    And I enter "password123" in the password field
    And I click the "Login" button
    Then I should see the dashboard page
    And I should see "Welcome back" message
```

### 4. Configuration Management

```bash
# List all configuration
uv run frontend-tester config list

# Get specific value
uv run frontend-tester config get --key llm.model

# Set configuration
uv run frontend-tester config set --key llm.model --value gpt-4
```

## CLI Commands

### `frontend-tester init [path]`
Initialize a new test project with interactive prompts.

**Options:**
- `--name, -n`: Project name
- `--url, -u`: Target URL to test
- `--yes, -y`: Skip prompts, use defaults

### `frontend-tester config [action]`
Manage configuration (list, get, set).

**Options:**
- `--key, -k`: Configuration key (e.g., `llm.model`)
- `--value, -v`: Value to set
- `--global, -g`: Use global config

### `frontend-tester generate <url>` (Phase 3)
Generate tests from URL using AI analysis.

### `frontend-tester run [path]` (Phase 2)
Run tests using pytest-bdd.

### `frontend-tester analyze <url>` (Phase 3)
Analyze UI and suggest test scenarios.

## Project Structure

```
frontendTester/
├── src/
│   └── frontend_tester/
│       ├── cli/           # CLI interface
│       ├── core/          # Configuration & project management
│       ├── bdd/           # Gherkin/BDD support
│       ├── playwright_runner/  # Browser automation (Phase 2)
│       ├── ai/            # LLM integration (Phase 3)
│       └── visual/        # Visual regression (Phase 4)
├── tests/                 # Unit tests
├── pyproject.toml         # Project configuration
└── README.md
```

## Architecture

### Test Format: Gherkin/Cucumber
Tests are written in Gherkin syntax for readability:
- **Feature files** (`.feature`) - Human-readable test scenarios
- **Step definitions** (`.py`) - Python implementation
- **Support files** - Browser fixtures and utilities

### Browser Automation: Playwright
- Cross-browser support (Chrome, Firefox, Safari)
- Docker support for consistent environments
- Parallel test execution
- Auto-wait and retry logic

### AI Integration: LiteLLM
- Unified interface for OpenAI and Anthropic
- UI analysis and test generation
- Self-healing test maintenance
- Natural language test creation

## Configuration

### Project Config (`.frontend-tester/config.yaml`)

```yaml
name: my-tests
target_urls:
  - http://localhost:3000

browser:
  browsers:
    - chromium
  headless: true
  timeout: 30000

docker:
  enabled: false

llm:
  provider: openai
  model: gpt-4
  temperature: 0.7

visual_regression:
  enabled: false
  threshold: 0.01
```

### Environment Variables (`.env`)

```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

## Development

### Running Tests

```bash
# Run unit tests
uv run pytest

# Run with coverage
uv run pytest --cov=frontend_tester
```

### Linting

```bash
# Run ruff
uv run ruff check src/

# Auto-fix
uv run ruff check --fix src/
```

## Roadmap

### Phase 1: Project Structure + CLI (Complete)
- Project initialization
- Configuration management
- BDD template system
- CLI framework

### Phase 2: Playwright Integration (Next)
- Browser automation setup
- Docker integration
- Test execution engine
- `frontend-tester run` command

### Phase 3: AI Test Generation
- LiteLLM integration
- UI analysis and crawling
- Gherkin scenario generation
- `frontend-tester generate` command

### Phase 4: Visual Regression
- Screenshot capture
- Image comparison
- Baseline management
- Diff reporting

### Phase 5: Fix/Autofix
- Self-healing tests
- Selector maintenance
- AI-suggested fixes
- Automatic test updates

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)

## Support

- Issues: https://github.com/bedaHovorka/frontend-tester/issues
- Discussions: https://github.com/bedaHovorka/frontend-tester/discussions

## Acknowledgments

Built with:
- [Playwright](https://playwright.dev) - Browser automation
- [pytest-bdd](https://pytest-bdd.readthedocs.io/) - BDD testing
- [LiteLLM](https://github.com/BerriAI/litellm) - LLM proxy
- [Typer](https://typer.tiangolo.com/) - CLI framework
- [Rich](https://rich.readthedocs.io/) - Terminal formatting
