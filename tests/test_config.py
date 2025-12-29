"""Tests for configuration system."""

from pathlib import Path
import tempfile
import pytest
from assertpy import assert_that

from frontend_tester.core.config import (
    ProjectConfig,
    BrowserConfig,
    LLMConfig,
)


def test_default_config():
    """Test default configuration."""
    config = ProjectConfig()
    assert_that(config.name).is_equal_to("my-tests")
    assert_that(config.browser.browsers).is_equal_to(["chromium"])
    assert_that(config.browser.headless).is_true()
    assert_that(config.llm.provider).is_equal_to("openai")


def test_config_validation():
    """Test configuration validation."""
    # Valid config
    config = ProjectConfig(
        name="test",
        target_urls=["http://localhost:3000"],
        browser=BrowserConfig(browsers=["chromium", "firefox"]),
    )
    assert_that(config.browser.browsers).is_length(2)

    # Invalid browser
    with pytest.raises(ValueError, match="Invalid browser"):
        BrowserConfig(browsers=["invalid"])


def test_config_save_load():
    """Test saving and loading configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.yaml"

        # Create and save config
        config = ProjectConfig(
            name="test-project",
            target_urls=["http://example.com"],
            llm=LLMConfig(provider="anthropic", model="claude-sonnet-4"),
        )
        config.save_to_file(config_path)

        # Load config
        loaded_config = ProjectConfig.load_from_file(config_path)
        assert_that(loaded_config.name).is_equal_to("test-project")
        assert_that(loaded_config.target_urls).is_equal_to(["http://example.com"])
        assert_that(loaded_config.llm.provider).is_equal_to("anthropic")


def test_config_no_api_key_in_file():
    """Test that API keys are not saved to file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.yaml"

        # Create config with API key
        config = ProjectConfig(
            name="test",
            llm=LLMConfig(api_key="sk-secret123"),
        )
        config.save_to_file(config_path)

        # Verify API key is not in file
        content = config_path.read_text()
        assert_that(content).does_not_contain("sk-secret123")
        assert_that(content).contains_ignoring_case("api_key").matches(r"api_key:\s*['\"]?\s*['\"]?")
