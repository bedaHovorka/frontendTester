# Frontend Tester - Development Plan

## Current Status
**Phase 3: AI Test Generation - ✅ COMPLETE**

Last updated: 2025-12-31

## Milestones

### Phase 1: Project Structure + Basic CLI (✅ Complete)
**Status**: Complete
**Goal**: Create foundational CLI tool with project initialization and configuration management

- [x] Create `pyproject.toml` with dependencies
- [x] Set up project structure
- [x] Implement CLI framework (Typer + Rich)
- [x] Create configuration system (Pydantic)
- [x] Implement `init` command
- [x] Implement `config` command
- [x] Create BDD templates (Jinja2)
- [x] Create documentation (README.md, .gitignore, .env.example)
- [x] Write unit tests (11 tests, all passing)
- [x] Validate with `uv sync` and manual testing

**Completed**: 2025-12-29

### Phase 2: Playwright Integration (✅ Complete)
**Status**: Complete
**Goal**: Browser automation with multi-browser/OS support via Docker

Tasks:
- [x] Add Playwright dependencies to pyproject.toml
- [x] Create Docker configuration for browser images
- [x] Implement browser management (`playwright_runner/`)
- [x] Create pytest-bdd step implementations with Playwright
- [x] Implement `frontend-tester run` command
- [x] Add parallel test execution support
- [x] Create example tests with real browser interaction
- [x] Test across Chromium, Firefox, and WebKit
- [x] Write unit tests (7 additional tests, all passing)
- [x] Document Playwright setup

**Completed**: 2025-12-29

### Phase 3: AI Test Generation (✅ Complete)
**Status**: Complete
**Goal**: LLM-powered test generation and UI analysis

Tasks:
- [x] Create/update/maintain tests, using git to manage two repos
- [x] APP_REPO when is tested app (in any technology), this code should not be touched during test generation
- [x] TEST_REPO (different from APP_REPO) where generated tests are stored, this code is created/updated during test generation
- [x] into TEST_REPO will be generated only black-box tests, access to APP_REPO in case of necessary
- [x] white-box tests exists in APP_REPO and are maintained by developer/tester manually, not by this tool
- [x] Dependencies to run test should be installed to separate docker container when tests are executed (multi-stage)
- [x] Integrate LiteLLM for unified LLM access
- [x] Create LLM client wrapper (`ai/client.py`)
- [x] Implement UI analysis:
  - [x] DOM structure extraction
  - [x] Interactive element identification
  - [x] Form field detection
  - [x] Navigation flow mapping
- [x] Implement Gherkin scenario generation
- [x] Implement Python step definition generation
- [x] Create `frontend-tester generate` command
- [x] Create `frontend-tester analyze` command
- [x] Add prompt templates for different test types
- [ ] Generated tests (TEST_REPO) must be without compile errors (see PHASE3*.md files)
- [ ] Generated test (TEST_REPO) must work in own prepared container with sample applications launched in other container
- [ ] Deep testing and validation of generated tests (see PHASE3*.md files for found issues and improvements)

**Estimated Duration**: 2-3 weeks

### Phase 4: Visual Regression (Planned)
**Status**: Not Started
**Goal**: Screenshot-based visual regression testing

Tasks:
- [ ] Test process workflow:
  - REFERENTIAL and CHANGED state switching by git in APP_REPO and run both in different Docker containers
  - using git worktree to manage REFERENTIAL (in temp? folder)
  - for CHANGED is default actual working state
  - for REFERENTIAL is default last committed state
  - three modes of type of changes to detect or specified by user: "functional" or "visual" or "refactor"
- [ ] Implement screenshot capture with Playwright
- [ ] Integrate image comparison library (pixelmatch)
- [ ] Create baseline management system
- [ ] Implement visual diff reporting (HTML)
- [ ] Add Gherkin step: "Then the page should match baseline"
- [ ] Create visual regression configuration options
- [ ] Add threshold tuning capabilities
- [ ] Document visual regression workflow

**Estimated Duration**: 1-2 weeks

### Phase 5: Fix/Autofix System (Planned)
**Status**: Not Started
**Goal**: Self-healing tests and automatic maintenance

Tasks:
- [ ] TBD - Awaiting detailed requirements from user
- [ ] Handling modes of type of changes from previous phase to apply different strategies of fixing tests
  - "refactor" - focus on code structure changes without UI changes, zero tolerance for visual diffs. No fix of test code possible.
  - "functional" or "visual" - focus on fixing functional test failures.
    Before change mustn't be on REFERENTIAL any failures, only on CHANGED. After change is possible fix of test code.
  - user (tester) must approve suggested fixes before applying them.
- [ ] Potential features:
  - Selector auto-update when elements change
  - AI-suggested fixes for broken tests
  - Test maintenance recommendations
  - Automatic baseline updates
  - Code review of test after autofix

**Estimated Duration**: TBD

## Upcoming Decisions

1. **Docker Images**: Official Playwright images vs custom builds?
2. **CI/CD Integration**: Priority platform (GitHub Actions, GitLab CI, Jenkins)?
3. **Test Report Format**: HTML, JSON, JUnit XML, or Allure?
4. **Selector Strategy**: CSS, XPath, data-testid, or AI-powered semantic selectors?

## Technical Debt

- None currently (Phase 1 is foundational)

## Future Enhancements

- Plugin system for custom step definitions
- Record-and-replay functionality
- Performance testing integration
- Accessibility testing integration
- Mobile device emulation
- API testing integration
- Multi-language support (feature files in different languages)

## Notes

- Following Python 3.11+ best practices
- Using UV for package management (as per CLAUDE.md)
- Async/await throughout for performance
- Type hints everywhere for maintainability
- Rich terminal output for UX
