# Frontend Tester

**AI-powered CLI tool for automated blackbox regression testing of frontend applications**

Frontend Tester is a specialized testing tool that combines the power of browser automation (Playwright), behavior-driven development (Gherkin/Cucumber), and AI (LiteLLM) to create and run comprehensive frontend regression tests.

## Features

### ✅ Phase 1: Project Structure + CLI (Complete)
- CLI framework with beautiful terminal output (Typer + Rich)
- Project initialization with `frontend-tester init`
- Configuration management (YAML + environment variables)
- BDD/Gherkin test structure setup
- Template system for test generation

### ✅ Phase 2: Playwright Integration (Complete)
- Multi-browser support (Chromium, Firefox, WebKit)
- Async browser automation with Playwright
- 40+ reusable BDD step definitions
- `frontend-tester run` command with:
  - Tag filtering (@smoke, @regression)
  - Parallel test execution
  - HTML report generation
  - Browser override options
- Docker support for containerized testing
- Pytest-bdd integration with async support

### ✅ Phase 3: AI-Powered Test Generation (Initial Implementation)
- LiteLLM integration with OpenAI and Anthropic support
- UI analysis and DOM extraction
- AI-powered test scenario generation
- `frontend-tester generate` command for creating test scenarios from URLs
- `frontend-tester analyze` command for UI component analysis
- Gherkin feature file generation from AI analysis

### Coming Soon
- **Phase 3 (Complete)**: Enhanced AI features and test maintenance
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

### 4. Generate Tests with AI (Phase 3)

```bash
# Analyze a URL and generate test scenarios
uv run frontend-tester generate https://example.com/login

# Analyze UI components
uv run frontend-tester analyze https://example.com/dashboard
```

### 5. Run Tests

```bash
# Run all tests
uv run frontend-tester run

# Run specific feature
uv run frontend-tester run --feature login.feature

# Run with tag filter
uv run frontend-tester run --tag smoke

# Run in parallel (4 workers)
uv run frontend-tester run --parallel 4

# Run with visible browser (headed mode)
uv run frontend-tester run --headed

# Run with specific browser
uv run frontend-tester run --browser firefox

# Generate HTML report
uv run frontend-tester run --html
```

### 6. Configuration Management

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

### `frontend-tester run [path]`
Run BDD tests using pytest-bdd and Playwright.

**Options:**
- `--feature, -f`: Run specific feature file
- `--tag, -t`: Run tests with specific tag (@smoke, @regression)
- `--browser, -b`: Override browser (chromium, firefox, webkit)
- `--headed`: Run with visible browser (default: headless)
- `--parallel, -n`: Number of parallel workers
- `--html`: Generate HTML report
- `--verbose, -v`: Verbose output

### `frontend-tester generate <url>`
Generate tests from URL using AI analysis.

**Options:**
- `--output, -o`: Output directory for generated tests
- `--provider`: LLM provider (openai, anthropic)
- `--model`: LLM model to use

### `frontend-tester analyze <url>`
Analyze UI and suggest test scenarios.

**Options:**
- `--depth`: Crawl depth for multi-page analysis
- `--output, -o`: Output file for analysis results

## Docker Support

Frontend Tester includes Docker configuration for consistent cross-browser testing.

### Using Docker

```bash
# Build the Docker image
docker build -t frontend-tester .

# Run tests in Docker
docker run -v $(pwd)/.frontend-tester:/app/.frontend-tester frontend-tester

# Run with specific browser
docker run -e FRONTEND_TESTER_BROWSER=firefox frontend-tester
```

### Using Docker Compose

```bash
# Run tests on all browsers in parallel
docker-compose up

# Run on specific browser
docker-compose up test-chromium
docker-compose up test-firefox
docker-compose up test-webkit
```

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

### Phase 2: Playwright Integration (Complete)
- Browser automation setup
- Docker integration
- Test execution engine
- `frontend-tester run` command

### Phase 3: AI Test Generation (In Progress)
- ✅ LiteLLM integration
- ✅ UI analysis and crawling
- ✅ Gherkin scenario generation
- ✅ `frontend-tester generate` command
- ✅ `frontend-tester analyze` command
- 🔜 Enhanced test maintenance features

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
