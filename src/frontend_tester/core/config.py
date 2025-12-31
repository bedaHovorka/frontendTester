"""Configuration management for Frontend Tester."""

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class BrowserConfig(BaseModel):
    """Browser configuration."""

    browsers: list[str] = Field(
        default=["chromium"],
        description="List of browsers to test (chromium, firefox, webkit)",
    )
    headless: bool = Field(default=True, description="Run browsers in headless mode")
    timeout: int = Field(default=30000, description="Default timeout in milliseconds")
    viewport_width: int = Field(default=1280, description="Viewport width in pixels")
    viewport_height: int = Field(default=720, description="Viewport height in pixels")
    args: list[str] | None = Field(default=None, description="Additional browser arguments")
    slow_mo: int = Field(default=0, description="Slow down operations by milliseconds")
    locale: str | None = Field(default=None, description="Locale for browser (e.g., 'en-US')")
    timezone: str | None = Field(default=None, description="Timezone for browser (e.g., 'America/New_York')")

    @property
    def viewport(self) -> dict[str, int]:
        """Get viewport as dict."""
        return {"width": self.viewport_width, "height": self.viewport_height}

    @field_validator("browsers")
    @classmethod
    def validate_browsers(cls, v: list[str]) -> list[str]:
        """Validate browser names."""
        valid_browsers = {"chromium", "firefox", "webkit", "chrome", "edge", "safari"}
        for browser in v:
            if browser.lower() not in valid_browsers:
                raise ValueError(
                    f"Invalid browser: {browser}. "
                    f"Valid options: {', '.join(valid_browsers)}"
                )
        return v


class DockerConfig(BaseModel):
    """Docker configuration for cross-browser testing."""

    enabled: bool = Field(default=False, description="Use Docker for browser testing")
    images: dict[str, str] = Field(
        default={
            "chromium": "mcr.microsoft.com/playwright:v1.40.0-jammy",
            "firefox": "mcr.microsoft.com/playwright:v1.40.0-jammy",
            "webkit": "mcr.microsoft.com/playwright:v1.40.0-jammy",
        },
        description="Docker images for different browsers",
    )


class LLMConfig(BaseModel):
    """LLM configuration for AI-powered features."""

    provider: str = Field(default="openai", description="LLM provider (openai, anthropic)")
    model: str = Field(default="gpt-4", description="Model name to use")
    api_key: str = Field(default="", description="API key (prefer environment variables)")
    temperature: float = Field(default=0.7, description="Sampling temperature")
    max_tokens: int = Field(default=2000, description="Maximum tokens in response")

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        """Validate LLM provider."""
        valid_providers = {"openai", "anthropic", "ollama", "gemini"}
        if v.lower() not in valid_providers:
            raise ValueError(
                f"Invalid provider: {v}. Valid options: {', '.join(valid_providers)}"
            )
        return v.lower()


class VisualRegressionConfig(BaseModel):
    """Visual regression testing configuration."""

    enabled: bool = Field(default=False, description="Enable visual regression testing")
    threshold: float = Field(
        default=0.01, description="Difference threshold (0-1)", ge=0.0, le=1.0
    )
    update_baselines: bool = Field(
        default=False, description="Update baselines on test run"
    )


class ProjectConfig(BaseModel):
    """Main project configuration."""

    name: str = Field(default="my-tests", description="Project name")
    target_urls: list[str] = Field(
        default=["http://localhost:3000"], description="Target URLs to test"
    )
    app_repo: str | None = Field(
        default=None, description="Path to application repository (read-only, for reference)"
    )
    test_repo: str | None = Field(
        default=None, description="Path to test repository (where tests are generated)"
    )
    browser: BrowserConfig = Field(default_factory=BrowserConfig)
    docker: DockerConfig = Field(default_factory=DockerConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    visual_regression: VisualRegressionConfig = Field(default_factory=VisualRegressionConfig)

    @classmethod
    def load_from_file(cls, config_path: Path) -> "ProjectConfig":
        """Load configuration from YAML file."""
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r") as f:
            data = yaml.safe_load(f) or {}

        # Override with environment variables
        if os.getenv("OPENAI_API_KEY"):
            if "llm" not in data:
                data["llm"] = {}
            data["llm"]["api_key"] = os.getenv("OPENAI_API_KEY", "")
        if os.getenv("ANTHROPIC_API_KEY") and data.get("llm", {}).get("provider") == "anthropic":
            data["llm"]["api_key"] = os.getenv("ANTHROPIC_API_KEY", "")

        return cls(**data)

    def save_to_file(self, config_path: Path) -> None:
        """Save configuration to YAML file."""
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Don't save API keys to file
        data = self.model_dump()
        if "llm" in data and "api_key" in data["llm"]:
            data["llm"]["api_key"] = ""

        with open(config_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    @classmethod
    def get_default_config_path(cls) -> Path:
        """Get default config path for the current directory."""
        return Path.cwd() / "config.yaml"

    @classmethod
    def get_global_config_path(cls) -> Path:
        """Get global config path."""
        return Path.home() / ".config" / "frontend-tester" / "config.yaml"


def load_config(config_path: Path | None = None) -> ProjectConfig:
    """
    Load configuration with fallback chain.

    Priority:
    1. Specified config_path
    2. config.yaml in current directory
    3. ~/.config/frontend-tester/config.yaml (global)
    4. Default configuration
    """
    if config_path and config_path.exists():
        return ProjectConfig.load_from_file(config_path)

    # Try local config
    local_config = ProjectConfig.get_default_config_path()
    if local_config.exists():
        return ProjectConfig.load_from_file(local_config)

    # Try global config
    global_config = ProjectConfig.get_global_config_path()
    if global_config.exists():
        return ProjectConfig.load_from_file(global_config)

    # Return default config
    return ProjectConfig()
