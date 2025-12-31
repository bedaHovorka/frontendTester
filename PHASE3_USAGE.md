# Phase 3: AI Test Generation - Usage Guide

This guide explains how to use the AI-powered test generation features added in Phase 3.

## Prerequisites

1. **LLM API Key** - You need an API key from one of the supported providers:
   - OpenAI (recommended): Set `OPENAI_API_KEY` environment variable
   - Anthropic: Set `ANTHROPIC_API_KEY` environment variable

2. **Running Application** - The application you want to test must be running and accessible

3. **Dependencies Installed**:
   ```bash
   uv sync  # Installs AI dependencies automatically
   ```

## Quick Start

### 1. Set Up API Key

```bash
# For OpenAI (recommended)
export OPENAI_API_KEY="sk-..."

# OR for Anthropic/Claude
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 2. Analyze Your Application

The `analyze` command inspects your web application and extracts UI structure:

```bash
# Basic analysis
uv run frontend-tester analyze http://localhost:3000

# Save to custom location
uv run frontend-tester analyze http://localhost:3000 --output analysis.json

# Use different browser
uv run frontend-tester analyze http://localhost:3000 --browser firefox

# Run in headed mode (see the browser)
uv run frontend-tester analyze http://localhost:3000 --headed
```

**What it does:**
- Launches Playwright browser
- Navigates to the URL
- Extracts interactive elements (buttons, links, forms, inputs)
- Uses AI to identify user flows and test scenarios
- Saves analysis to JSON file

**Output:**
```
Analyzing page: http://localhost:3000
Using LLM: openai/gpt-4
Launching chromium browser...
Navigating to http://localhost:3000...
Analyzing page structure...

Analysis Results:
URL: http://localhost:3000
Title: My Application

Detected Elements:
  • buttons: 15
  • links: 23
  • inputs: 8
  • forms: 2

AI Analysis:
  • User Flows: 3
    - Login Flow
    - Registration Flow
    - Dashboard Navigation
  • Interactive Elements: 46
  • Forms: 2

Analysis saved to: .frontend-tester/analysis/analysis.json
```

### 3. Generate Tests

The `generate` command creates complete BDD test suites from your application:

```bash
# Basic generation
uv run frontend-tester generate http://localhost:3000

# Specify output directory
uv run frontend-tester generate http://localhost:3000 --output-dir /tmp/tests

# Use existing analysis
uv run frontend-tester generate http://localhost:3000 --analysis analysis.json

# Customize app name
uv run frontend-tester generate http://localhost:3000 --app-name "My App"
```

**What it does:**
- Analyzes page (or uses existing analysis)
- Generates Gherkin feature files for each user flow
- Generates Python step definitions using Playwright
- Saves to organized directory structure

**Output:**
```
Generating tests for: http://localhost:3000
Using LLM: openai/gpt-4
Output directory: .frontend-tester
Analyzing page structure...
Generating test scenarios...

Generated Files:
  • feature_login_flow: .frontend-tester/features/login_flow.feature
  • steps_login_flow: .frontend-tester/steps/test_login_flow.py
  • feature_registration_flow: .frontend-tester/features/registration_flow.feature
  • steps_registration_flow: .frontend-tester/steps/test_registration_flow.py

Test generation complete! Generated 4 files.

Next steps:
  1. Review generated files in: .frontend-tester
  2. Customize scenarios as needed
  3. Run tests with: frontend-tester run
```

### 4. Review Generated Tests

**Feature File** (`.frontend-tester/features/login_flow.feature`):
```gherkin
Feature: User Login
  As a user
  I want to log into the application
  So that I can access my account

  @smoke @critical
  Scenario: Successful login with valid credentials
    Given I am on the login page
    When I enter "user@example.com" in the email field
    And I enter "password123" in the password field
    And I click the "Login" button
    Then I should see the dashboard
    And I should see "Welcome back" message

  @regression
  Scenario: Login fails with invalid credentials
    Given I am on the login page
    When I enter "invalid@example.com" in the email field
    And I enter "wrongpassword" in the password field
    And I click the "Login" button
    Then I should see "Invalid credentials" error message
```

**Step Definitions** (`.frontend-tester/steps/test_login_flow.py`):
```python
from pytest_bdd import given, when, then, scenario
from playwright.async_api import Page, expect

@given('I am on the login page')
async def go_to_login_page(page: Page, base_url: str):
    await page.goto(f"{base_url}/login")

@when('I enter "{email}" in the email field')
async def enter_email(page: Page, email: str):
    await page.fill('#email', email)

# ... more steps
```

### 5. Run Generated Tests

```bash
# Run all generated tests
uv run frontend-tester run

# Run specific feature
uv run frontend-tester run .frontend-tester/features/login_flow.feature

# Run with tags
uv run frontend-tester run --tags smoke
```

## Using Docker

### Build Image

```bash
docker build -t frontend-tester .
```

### Run Analysis in Container

```bash
# Set API key
export OPENAI_API_KEY="sk-..."

# Run analysis
docker-compose up analyze
```

### Generate Tests in Container

```bash
# Generate tests and save to TEST_REPO
docker-compose up generate
```

The docker-compose.yml is configured to:
- Mount APP_REPO as read-only at `/app_repo`
- Mount TEST_REPO as read-write at `/test_repo`
- Pass LLM API keys via environment variables
- Access the app at `http://angularjs-demo-app:3000` (via Docker network)

## Configuration

### LLM Settings

Edit `.frontend-tester/config.yaml`:

```yaml
llm:
  provider: openai  # or anthropic, ollama, gemini
  model: gpt-4      # or gpt-3.5-turbo, claude-3-opus-20240229, etc.
  temperature: 0.7
  max_tokens: 2000
```

### Repository Paths

```yaml
app_repo: /home/user/my-app        # Application repo (read-only)
test_repo: /tmp/my-app-tests       # Test repo (generated tests)
```

### Browser Settings

```yaml
browser:
  browsers: [chromium]
  headless: true
  timeout: 30000
```

## Advanced Usage

### Analyze Multiple Pages

```bash
# Analyze different pages/flows
uv run frontend-tester analyze http://localhost:3000/
uv run frontend-tester analyze http://localhost:3000/login
uv run frontend-tester analyze http://localhost:3000/dashboard
```

### Use Different LLM Providers

```bash
# Configure provider in config.yaml or use env vars
export ANTHROPIC_API_KEY="sk-ant-..."

# Edit config.yaml
llm:
  provider: anthropic
  model: claude-3-opus-20240229
```

### Customize Temperature

Higher temperature = more creative/varied scenarios
Lower temperature = more consistent/predictable scenarios

```yaml
llm:
  temperature: 0.3  # More deterministic (recommended for code generation)
```

## Workflow: APP_REPO and TEST_REPO

### Architecture

```
APP_REPO (Application)          TEST_REPO (Tests)
├── src/                        ├── features/
├── public/                     │   ├── login_flow.feature
├── package.json                │   └── registration_flow.feature
└── ...                         ├── steps/
    (DO NOT MODIFY)             │   ├── test_login_flow.py
                                │   └── test_registration_flow.py
                                ├── support/
                                ├── analysis/
                                └── .git/
                                    (Generated & Modified)
```

### Best Practices

1. **APP_REPO** - Keep application code separate
   - Never modify during test generation
   - Mount as read-only in Docker
   - Use only for reference if needed

2. **TEST_REPO** - Dedicated test repository
   - All generated tests go here
   - Commit generated tests to version control
   - Customize and maintain separately from app

3. **Git Workflow**
   ```bash
   # In TEST_REPO
   cd /tmp/dummy_fe_app
   git add features/ steps/
   git commit -m "Generated tests for login flow"
   git push
   ```

## Troubleshooting

### "LLM API key not configured"

**Solution**: Set the appropriate environment variable:
```bash
export OPENAI_API_KEY="sk-..."
# OR
export ANTHROPIC_API_KEY="sk-ant-..."
```

### "Failed to parse JSON" in analysis

**Issue**: LLM returned invalid JSON

**Solution**:
- Try again (LLM responses can vary)
- Lower the temperature in config
- Use a more capable model (e.g., gpt-4 instead of gpt-3.5-turbo)

### Browser timeout during analysis

**Solution**:
- Increase timeout in config: `browser.timeout: 60000`
- Check if application is running
- Use `--headed` flag to see what's happening

### Generated tests don't work

**Solution**:
1. Review generated step definitions
2. Customize selectors if needed
3. Ensure application structure matches analysis
4. Re-run analyze if application changed

## Tips

1. **Start Small** - Analyze individual pages/flows before the entire app
2. **Review Before Running** - Always review generated tests before execution
3. **Customize Selectors** - Update selectors to use stable identifiers (data-testid)
4. **Iterate** - Regenerate and refine based on results
5. **Version Control** - Commit generated tests to track changes

## Next Steps

After generating tests:
1. Review and customize generated scenarios
2. Update selectors to use stable identifiers
3. Add assertions and validations
4. Run tests: `frontend-tester run`
5. Configure CI/CD integration
6. Wait for Phase 4: Visual Regression Testing!

## Resources

- [LiteLLM Documentation](https://docs.litellm.ai/)
- [Playwright Documentation](https://playwright.dev/python/)
- [pytest-bdd Documentation](https://pytest-bdd.readthedocs.io/)
- [Gherkin Syntax](https://cucumber.io/docs/gherkin/)
