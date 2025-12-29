"""Tests for browser manager."""

import pytest
from assertpy import assert_that

from frontend_tester.core.config import BrowserConfig
from frontend_tester.playwright_runner.browser_manager import BrowserManager, browser_manager


@pytest.mark.asyncio
async def test_browser_manager_lifecycle():
    """Test browser manager start/stop."""
    config = BrowserConfig(browsers=["chromium"], headless=True)
    manager = BrowserManager(config)

    # Start should initialize Playwright
    await manager.start()
    assert_that(manager._playwright).is_not_none()
    assert_that(manager._browsers).is_not_empty()
    assert_that(manager._browsers).contains_key("chromium")

    # Stop should clean up
    await manager.stop()
    assert_that(manager._browsers).is_empty()
    assert_that(manager._playwright).is_none()


@pytest.mark.asyncio
async def test_browser_manager_get_browser():
    """Test getting browser instances."""
    config = BrowserConfig(browsers=["chromium"], headless=True)
    manager = BrowserManager(config)

    await manager.start()

    # Get default browser (first in list)
    browser = manager.get_browser()
    assert_that(browser).is_not_none()

    # Get specific browser
    browser2 = manager.get_browser("chromium")
    assert_that(browser2).is_equal_to(browser)

    # Invalid browser should raise error
    with pytest.raises(ValueError, match="not launched"):
        manager.get_browser("firefox")

    await manager.stop()


@pytest.mark.asyncio
async def test_browser_manager_context_manager():
    """Test browser manager as context manager."""
    config = BrowserConfig(browsers=["chromium"], headless=True)

    async with browser_manager(config) as manager:
        assert_that(manager._playwright).is_not_none()
        assert_that(manager._browsers).is_not_empty()

    # After context exit, should be cleaned up
    # (can't check manager state as it's out of scope, but no errors means success)


@pytest.mark.asyncio
async def test_browser_manager_page_context_manager():
    """Test creating a page with context manager."""
    config = BrowserConfig(browsers=["chromium"], headless=True)

    async with browser_manager(config) as manager:
        async with manager.page() as page:
            assert_that(page).is_not_none()
            # Simple navigation test
            await page.goto("about:blank")
            assert_that(page.url).is_equal_to("about:blank")


@pytest.mark.asyncio
async def test_browser_manager_invalid_browser():
    """Test launching invalid browser (bypassing validation for testing)."""
    # Create config with valid browser first, then manually set invalid browser
    config = BrowserConfig(browsers=["chromium"], headless=True)
    manager = BrowserManager(config)

    # Manually set invalid browser to test launch logic
    manager.config.browsers = ["invalid"]

    with pytest.raises(ValueError, match="Invalid browser"):
        await manager.start()


@pytest.mark.asyncio
async def test_browser_manager_no_browsers():
    """Test getting browser when none launched."""
    config = BrowserConfig(browsers=[], headless=True)
    manager = BrowserManager(config)

    await manager.start()

    with pytest.raises(ValueError, match="No browsers launched"):
        manager.get_browser()

    await manager.stop()


@pytest.mark.asyncio
async def test_browser_manager_create_context():
    """Test creating browser context with options."""
    config = BrowserConfig(
        browsers=["chromium"],
        headless=True,
        viewport={"width": 1280, "height": 720},
    )

    async with browser_manager(config) as manager:
        # Create context with default viewport
        context = await manager.create_context()
        assert_that(context).is_not_none()

        # Context should use configured viewport
        page = await context.new_page()
        viewport = page.viewport_size
        assert_that(viewport["width"]).is_equal_to(1280)
        assert_that(viewport["height"]).is_equal_to(720)

        await page.close()
        await context.close()
