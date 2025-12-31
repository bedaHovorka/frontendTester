"""Browser management for Playwright."""

from typing import Any
from contextlib import asynccontextmanager

from playwright.async_api import (
    async_playwright,
    Browser,
    BrowserContext,
    Page,
    Playwright,
)

from frontend_tester.core.config import BrowserConfig


class BrowserManager:
    """Manages Playwright browser instances and contexts."""

    def __init__(self, config: BrowserConfig):
        """Initialize browser manager.

        Args:
            config: Browser configuration
        """
        self.config = config
        self._playwright: Playwright | None = None
        self._browsers: dict[str, Browser] = {}

    async def start(self) -> None:
        """Start Playwright and launch browsers."""
        self._playwright = await async_playwright().start()

        # Launch configured browsers
        for browser_name in self.config.browsers:
            browser = await self._launch_browser(browser_name)
            self._browsers[browser_name] = browser

    async def stop(self) -> None:
        """Stop all browsers and Playwright."""
        # Close all browsers
        for browser in self._browsers.values():
            await browser.close()
        self._browsers.clear()

        # Stop Playwright
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None

    async def __aenter__(self) -> "BrowserManager":
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.stop()

    async def _launch_browser(self, browser_name: str) -> Browser:
        """Launch a specific browser.

        Args:
            browser_name: Browser name (chromium, firefox, webkit)

        Returns:
            Browser instance

        Raises:
            ValueError: If browser name is invalid
        """
        if not self._playwright:
            raise RuntimeError("Playwright not started. Call start() first.")

        launch_options = {
            "headless": self.config.headless,
            "args": self.config.args or [],
            "slow_mo": self.config.slow_mo,
        }

        if browser_name == "chromium":
            return await self._playwright.chromium.launch(**launch_options)
        elif browser_name == "firefox":
            return await self._playwright.firefox.launch(**launch_options)
        elif browser_name == "webkit":
            return await self._playwright.webkit.launch(**launch_options)
        else:
            raise ValueError(f"Invalid browser: {browser_name}")

    def get_browser(self, browser_name: str | None = None) -> Browser:
        """Get a browser instance.

        Args:
            browser_name: Browser name, or None for the first configured browser

        Returns:
            Browser instance

        Raises:
            ValueError: If browser not found
        """
        if browser_name is None:
            # Return first browser
            if not self._browsers:
                raise ValueError("No browsers launched")
            return next(iter(self._browsers.values()))

        if browser_name not in self._browsers:
            raise ValueError(f"Browser not launched: {browser_name}")

        return self._browsers[browser_name]

    async def create_context(
        self, browser_name: str | None = None, **options: Any
    ) -> BrowserContext:
        """Create a new browser context.

        Args:
            browser_name: Browser name, or None for the first configured browser
            **options: Context options (viewport, locale, etc.)

        Returns:
            Browser context
        """
        browser = self.get_browser(browser_name)

        # Apply default viewport if not specified
        if "viewport" not in options and self.config.viewport:
            options["viewport"] = self.config.viewport

        # Apply locale if configured
        if "locale" not in options and self.config.locale:
            options["locale"] = self.config.locale

        # Apply timezone if configured
        if "timezone_id" not in options and self.config.timezone:
            options["timezone_id"] = self.config.timezone

        return await browser.new_context(**options)

    async def create_page(self, browser_name: str | None = None, **context_options: Any) -> Page:
        """Create a new page in a new context.

        Args:
            browser_name: Browser name, or None for the first configured browser
            **context_options: Context options

        Returns:
            Page instance
        """
        context = await self.create_context(browser_name, **context_options)
        return await context.new_page()

    @asynccontextmanager
    async def page(
        self, browser_name: str | None = None, **context_options: Any
    ) -> Page:
        """Context manager for creating a page.

        Args:
            browser_name: Browser name, or None for the first configured browser
            **context_options: Context options

        Yields:
            Page instance

        Example:
            async with browser_manager.page() as page:
                await page.goto("https://example.com")
                # ... perform actions
        """
        context = await self.create_context(browser_name, **context_options)
        page = await context.new_page()
        try:
            yield page
        finally:
            await context.close()


@asynccontextmanager
async def browser_manager(config: BrowserConfig) -> BrowserManager:
    """Context manager for browser manager lifecycle.

    Args:
        config: Browser configuration

    Yields:
        BrowserManager instance

    Example:
        async with browser_manager(config) as manager:
            async with manager.page() as page:
                await page.goto("https://example.com")
    """
    manager = BrowserManager(config)
    await manager.start()
    try:
        yield manager
    finally:
        await manager.stop()
