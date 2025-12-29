"""Common BDD step definitions using Playwright."""

import re
from typing import Any

from playwright.async_api import Page, expect
from pytest_bdd import given, when, then, parsers


# Navigation Steps


@given(parsers.parse('I am on "{url}"'))
@given(parsers.parse("I am on {url}"))
async def navigate_to_url(page: Page, url: str) -> None:
    """Navigate to a URL.

    Args:
        page: Playwright page instance
        url: URL to navigate to
    """
    await page.goto(url)


@given("I am on the homepage")
@given("I visit the homepage")
async def navigate_to_homepage(page: Page, base_url: str) -> None:
    """Navigate to the homepage.

    Args:
        page: Playwright page instance
        base_url: Base URL from config
    """
    await page.goto(base_url)


@when(parsers.parse('I navigate to "{url}"'))
@when(parsers.parse("I navigate to {url}"))
async def navigate_to(page: Page, url: str) -> None:
    """Navigate to a URL.

    Args:
        page: Playwright page instance
        url: URL to navigate to
    """
    await page.goto(url)


@when("I go back")
async def go_back(page: Page) -> None:
    """Navigate back in browser history.

    Args:
        page: Playwright page instance
    """
    await page.go_back()


@when("I go forward")
async def go_forward(page: Page) -> None:
    """Navigate forward in browser history.

    Args:
        page: Playwright page instance
    """
    await page.go_forward()


@when("I reload the page")
@when("I refresh the page")
async def reload_page(page: Page) -> None:
    """Reload the current page.

    Args:
        page: Playwright page instance
    """
    await page.reload()


# Click Actions


@when(parsers.parse('I click on "{selector}"'))
@when(parsers.parse("I click on {selector}"))
async def click_element(page: Page, selector: str) -> None:
    """Click on an element.

    Args:
        page: Playwright page instance
        selector: CSS selector or text selector
    """
    await page.click(selector)


@when(parsers.parse('I click the button "{text}"'))
async def click_button_by_text(page: Page, text: str) -> None:
    """Click a button by its text.

    Args:
        page: Playwright page instance
        text: Button text
    """
    await page.get_by_role("button", name=text).click()


@when(parsers.parse('I click the link "{text}"'))
async def click_link_by_text(page: Page, text: str) -> None:
    """Click a link by its text.

    Args:
        page: Playwright page instance
        text: Link text
    """
    await page.get_by_role("link", name=text).click()


# Form Interactions


@when(parsers.parse('I type "{text}" into "{selector}"'))
@when(parsers.parse("I type {text} into {selector}"))
async def type_into_field(page: Page, text: str, selector: str) -> None:
    """Type text into an input field.

    Args:
        page: Playwright page instance
        text: Text to type
        selector: CSS selector
    """
    await page.fill(selector, text)


@when(parsers.parse('I fill "{field}" with "{value}"'))
async def fill_field(page: Page, field: str, value: str) -> None:
    """Fill a form field by label or placeholder.

    Args:
        page: Playwright page instance
        field: Field label or placeholder
        value: Value to fill
    """
    # Try by label first
    try:
        await page.get_by_label(field).fill(value)
    except Exception:
        # Fall back to placeholder
        await page.get_by_placeholder(field).fill(value)


@when(parsers.parse('I select "{option}" from "{selector}"'))
async def select_option(page: Page, option: str, selector: str) -> None:
    """Select an option from a dropdown.

    Args:
        page: Playwright page instance
        option: Option text or value
        selector: CSS selector
    """
    await page.select_option(selector, option)


@when(parsers.parse('I check "{selector}"'))
async def check_checkbox(page: Page, selector: str) -> None:
    """Check a checkbox.

    Args:
        page: Playwright page instance
        selector: CSS selector
    """
    await page.check(selector)


@when(parsers.parse('I uncheck "{selector}"'))
async def uncheck_checkbox(page: Page, selector: str) -> None:
    """Uncheck a checkbox.

    Args:
        page: Playwright page instance
        selector: CSS selector
    """
    await page.uncheck(selector)


@when(parsers.parse('I press "{key}"'))
async def press_key(page: Page, key: str) -> None:
    """Press a keyboard key.

    Args:
        page: Playwright page instance
        key: Key name (Enter, Escape, etc.)
    """
    await page.keyboard.press(key)


# Assertions


@then(parsers.parse('I should see "{text}"'))
async def should_see_text(page: Page, text: str) -> None:
    """Assert that text is visible on the page.

    Args:
        page: Playwright page instance
        text: Text to find
    """
    await expect(page.get_by_text(text)).to_be_visible()


@then(parsers.parse('I should not see "{text}"'))
async def should_not_see_text(page: Page, text: str) -> None:
    """Assert that text is not visible on the page.

    Args:
        page: Playwright page instance
        text: Text that should not be visible
    """
    await expect(page.get_by_text(text)).not_to_be_visible()


@then(parsers.parse('I should see the heading "{text}"'))
async def should_see_heading(page: Page, text: str) -> None:
    """Assert that a heading with text is visible.

    Args:
        page: Playwright page instance
        text: Heading text
    """
    await expect(page.get_by_role("heading", name=text)).to_be_visible()


@then(parsers.parse('the page title should be "{title}"'))
async def page_title_should_be(page: Page, title: str) -> None:
    """Assert the page title.

    Args:
        page: Playwright page instance
        title: Expected page title
    """
    await expect(page).to_have_title(title)


@then(parsers.parse('the page title should contain "{text}"'))
async def page_title_should_contain(page: Page, text: str) -> None:
    """Assert the page title contains text.

    Args:
        page: Playwright page instance
        text: Text that should be in the title
    """
    await expect(page).to_have_title(re.compile(re.escape(text)))


@then(parsers.parse('the URL should be "{url}"'))
async def url_should_be(page: Page, url: str) -> None:
    """Assert the current URL.

    Args:
        page: Playwright page instance
        url: Expected URL
    """
    await expect(page).to_have_url(url)


@then(parsers.parse('the URL should contain "{text}"'))
async def url_should_contain(page: Page, text: str) -> None:
    """Assert the URL contains text.

    Args:
        page: Playwright page instance
        text: Text that should be in the URL
    """
    await expect(page).to_have_url(re.compile(re.escape(text)))


@then(parsers.parse('"{selector}" should be visible'))
async def element_should_be_visible(page: Page, selector: str) -> None:
    """Assert an element is visible.

    Args:
        page: Playwright page instance
        selector: CSS selector
    """
    await expect(page.locator(selector)).to_be_visible()


@then(parsers.parse('"{selector}" should not be visible'))
@then(parsers.parse('"{selector}" should be hidden'))
async def element_should_not_be_visible(page: Page, selector: str) -> None:
    """Assert an element is not visible.

    Args:
        page: Playwright page instance
        selector: CSS selector
    """
    await expect(page.locator(selector)).not_to_be_visible()


@then(parsers.parse('"{selector}" should be enabled'))
async def element_should_be_enabled(page: Page, selector: str) -> None:
    """Assert an element is enabled.

    Args:
        page: Playwright page instance
        selector: CSS selector
    """
    await expect(page.locator(selector)).to_be_enabled()


@then(parsers.parse('"{selector}" should be disabled'))
async def element_should_be_disabled(page: Page, selector: str) -> None:
    """Assert an element is disabled.

    Args:
        page: Playwright page instance
        selector: CSS selector
    """
    await expect(page.locator(selector)).to_be_disabled()


@then(parsers.parse('"{selector}" should contain "{text}"'))
async def element_should_contain_text(page: Page, selector: str, text: str) -> None:
    """Assert an element contains text.

    Args:
        page: Playwright page instance
        selector: CSS selector
        text: Text that should be in the element
    """
    await expect(page.locator(selector)).to_contain_text(text)


@then(parsers.parse('"{selector}" should have value "{value}"'))
async def element_should_have_value(page: Page, selector: str, value: str) -> None:
    """Assert an input element has a specific value.

    Args:
        page: Playwright page instance
        selector: CSS selector
        value: Expected value
    """
    await expect(page.locator(selector)).to_have_value(value)


@then(parsers.parse('"{selector}" should be checked'))
async def checkbox_should_be_checked(page: Page, selector: str) -> None:
    """Assert a checkbox is checked.

    Args:
        page: Playwright page instance
        selector: CSS selector
    """
    await expect(page.locator(selector)).to_be_checked()


@then(parsers.parse('"{selector}" should not be checked'))
@then(parsers.parse('"{selector}" should be unchecked'))
async def checkbox_should_not_be_checked(page: Page, selector: str) -> None:
    """Assert a checkbox is not checked.

    Args:
        page: Playwright page instance
        selector: CSS selector
    """
    await expect(page.locator(selector)).not_to_be_checked()


# Wait Steps


@when(parsers.parse("I wait for {seconds:d} seconds"))
async def wait_for_seconds(page: Page, seconds: int) -> None:
    """Wait for a specified number of seconds.

    Args:
        page: Playwright page instance
        seconds: Number of seconds to wait
    """
    await page.wait_for_timeout(seconds * 1000)


@when(parsers.parse('I wait for "{selector}" to be visible'))
async def wait_for_element_visible(page: Page, selector: str) -> None:
    """Wait for an element to be visible.

    Args:
        page: Playwright page instance
        selector: CSS selector
    """
    await page.wait_for_selector(selector, state="visible")


@when(parsers.parse('I wait for "{selector}" to be hidden'))
async def wait_for_element_hidden(page: Page, selector: str) -> None:
    """Wait for an element to be hidden.

    Args:
        page: Playwright page instance
        selector: CSS selector
    """
    await page.wait_for_selector(selector, state="hidden")


@when("I wait for the page to load")
async def wait_for_page_load(page: Page) -> None:
    """Wait for the page to finish loading.

    Args:
        page: Playwright page instance
    """
    await page.wait_for_load_state("networkidle")
