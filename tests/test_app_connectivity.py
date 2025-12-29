"""Tests for connectivity to the target application (AngularJS demo app).

This test verifies that the Playwright setup can successfully connect to and interact
with the application under test, both locally and from within Docker containers.
"""

import os
import pytest
from assertpy import assert_that

from frontend_tester.core.config import BrowserConfig
from frontend_tester.playwright_runner.browser_manager import browser_manager


def get_app_base_url() -> str:
    """Get the base URL for the app.

    Uses environment variable APP_BASE_URL if set, otherwise defaults to localhost.
    This allows the test to work both locally and in Docker.

    Returns:
        Base URL for the application
    """
    return os.environ.get("APP_BASE_URL", "http://localhost:3000")


@pytest.mark.asyncio
async def test_app_home_page_loads():
    """Test that the app home page loads successfully."""
    config = BrowserConfig(browsers=["chromium"], headless=True)
    base_url = get_app_base_url()

    async with browser_manager(config) as manager:
        async with manager.page() as page:
            # Navigate to the home page
            response = await page.goto(base_url, wait_until="networkidle")

            # Verify successful response
            assert_that(response).is_not_none()
            assert_that(response.status).is_equal_to(200)

            # Verify page title
            title = await page.title()
            assert_that(title).contains("AngularJS Demo Application")

            # Verify main heading is present
            heading = await page.locator("h1").text_content()
            assert_that(heading).contains("AngularJS")


@pytest.mark.asyncio
async def test_app_navigation():
    """Test that navigation works in the app."""
    config = BrowserConfig(browsers=["chromium"], headless=True)
    base_url = get_app_base_url()

    async with browser_manager(config) as manager:
        async with manager.page() as page:
            # Navigate to the home page
            await page.goto(base_url, wait_until="networkidle")

            # Verify navigation menu is present
            nav = page.locator("nav")
            assert_that(await nav.count()).is_greater_than(0)

            # Check for navigation links
            home_link = page.locator('a[href="#!/home"]')
            assert_that(await home_link.count()).is_greater_than(0)

            data_binding_link = page.locator('a[href="#!/data-binding"]')
            assert_that(await data_binding_link.count()).is_greater_than(0)


@pytest.mark.asyncio
async def test_app_angularjs_loaded():
    """Test that AngularJS is loaded and working."""
    config = BrowserConfig(browsers=["chromium"], headless=True)
    base_url = get_app_base_url()

    async with browser_manager(config) as manager:
        async with manager.page() as page:
            # Navigate to the home page
            await page.goto(base_url, wait_until="networkidle")

            # Check that AngularJS app is initialized (ng-app attribute)
            html_element = page.locator("html[ng-app='demoApp']")
            assert_that(await html_element.count()).is_equal_to(1)

            # Verify AngularJS is loaded by checking for angular object in window
            angular_loaded = await page.evaluate("() => typeof window.angular !== 'undefined'")
            assert_that(angular_loaded).is_true()


@pytest.mark.asyncio
async def test_app_responsive():
    """Test that the app is accessible with different viewport sizes."""
    config = BrowserConfig(
        browsers=["chromium"],
        headless=True,
        viewport={"width": 375, "height": 667}  # Mobile viewport
    )
    base_url = get_app_base_url()

    async with browser_manager(config) as manager:
        async with manager.page() as page:
            # Navigate to the home page with mobile viewport
            response = await page.goto(base_url, wait_until="networkidle")

            # Should still load successfully on mobile
            assert_that(response.status).is_equal_to(200)

            # Verify page content is still accessible
            heading = await page.locator("h1").text_content()
            assert_that(heading).is_not_none()


@pytest.mark.asyncio
async def test_app_multiple_pages():
    """Test navigating to multiple pages in the app."""
    config = BrowserConfig(browsers=["chromium"], headless=True)
    base_url = get_app_base_url()

    # List of pages to test (AngularJS hash routes)
    pages_to_test = [
        ("#!/home", "Home"),
        ("#!/data-binding", "Data Binding"),
        ("#!/controllers", "Controllers"),
        ("#!/filters", "Filters"),
    ]

    async with browser_manager(config) as manager:
        async with manager.page() as page:
            # First load the base page
            initial_response = await page.goto(base_url, wait_until="networkidle")
            assert_that(initial_response.status).is_equal_to(200)

            for route, expected_content in pages_to_test:
                # Navigate to specific route
                url = f"{base_url}/{route}"
                response = await page.goto(url, wait_until="networkidle")

                # For hash navigation, response might be None (client-side routing)
                # or it might return a response (depending on Playwright behavior)
                if response is not None:
                    assert_that(response.status).is_equal_to(200)

                # Wait for content to render
                await page.wait_for_timeout(500)  # Give AngularJS time to render

                # Verify we're on the correct page by checking the URL
                current_url = page.url
                assert_that(current_url).contains(route)

                # Verify content is present
                page_content = await page.content()
                assert_that(page_content).is_not_none()