# Frontend Tester Docker Image
# Multi-stage build for optimized image size

# Stage 1: Build stage - install dependencies and build the package
FROM mcr.microsoft.com/playwright/python:v1.57.0-jammy AS builder

WORKDIR /app

# Install uv for package management
RUN pip install --no-cache-dir uv

# Copy project files
COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/
COPY tests/ ./tests/

# Install project dependencies (creates .venv with all packages)
RUN uv sync --extra dev

# Install Playwright browser dependencies in builder stage
RUN uv run playwright install-deps

# Stage 2: Runtime stage - copy everything from builder
FROM mcr.microsoft.com/playwright/python:v1.57.0-jammy AS runtime

WORKDIR /app

# Install uv (lightweight, needed for uv run)
RUN pip install --no-cache-dir uv

# Copy everything from builder (project files + venv + installed browsers)
COPY --from=builder /app /app

# Set environment variables
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
ENV FRONTEND_TESTER_HEADLESS=true
ENV PATH="/app/.venv/bin:$PATH"

# Default command: run tests
CMD ["uv", "run", "frontend-tester", "run"]

# Usage:
# Build: docker build -t frontend-tester .
# Run tests: docker run -v $(pwd)/.frontend-tester:/app/.frontend-tester frontend-tester
# Run with custom command: docker run frontend-tester uv run frontend-tester --help
# Run specific browser: docker run -e FRONTEND_TESTER_BROWSER=firefox frontend-tester
