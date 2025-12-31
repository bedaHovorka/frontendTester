"""UI analysis module for extracting page structure and elements."""

import json
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from playwright.async_api import Page

from frontend_tester.ai.client import LLMClient
from frontend_tester.ai.prompts.ui_analysis import (
    ANALYZE_UI_SYSTEM_PROMPT,
    ANALYZE_UI_USER_PROMPT,
    EXTRACT_ELEMENTS_SYSTEM_PROMPT,
    EXTRACT_ELEMENTS_USER_PROMPT,
)


class UIAnalyzer:
    """Analyze web page UI and extract testable elements."""

    def __init__(self, llm_client: LLMClient):
        """
        Initialize UI analyzer.

        Args:
            llm_client: LLM client for AI-powered analysis
        """
        self.llm_client = llm_client

    async def analyze_page(self, page: Page) -> dict[str, Any]:
        """
        Analyze a web page and extract UI structure.

        Args:
            page: Playwright page instance

        Returns:
            Analysis results dict with elements, flows, forms, navigation
        """
        # Get page content
        url = page.url
        title = await page.title()
        html = await page.content()

        # Extract basic elements with BeautifulSoup
        basic_elements = self._extract_basic_elements(html)

        # Use LLM for advanced analysis
        analysis = await self._llm_analyze(url, title, html)

        return {
            "url": url,
            "title": title,
            "basic_elements": basic_elements,
            "ai_analysis": analysis,
        }

    def _extract_basic_elements(self, html: str) -> dict[str, list[dict[str, Any]]]:
        """
        Extract basic interactive elements using BeautifulSoup.

        Args:
            html: Page HTML content

        Returns:
            Dict with categorized elements
        """
        soup = BeautifulSoup(html, "lxml")

        elements = {
            "buttons": [],
            "links": [],
            "inputs": [],
            "selects": [],
            "textareas": [],
            "forms": [],
        }

        # Extract buttons
        for button in soup.find_all(["button", "input"], type=["button", "submit", "reset"]):
            elements["buttons"].append(self._extract_element_info(button))

        # Extract links
        for link in soup.find_all("a", href=True):
            elements["links"].append(self._extract_element_info(link))

        # Extract inputs
        for input_elem in soup.find_all("input"):
            if input_elem.get("type") not in ["button", "submit", "reset"]:
                elements["inputs"].append(self._extract_element_info(input_elem))

        # Extract selects
        for select in soup.find_all("select"):
            elem_info = self._extract_element_info(select)
            # Add options
            elem_info["options"] = [
                {"value": opt.get("value", ""), "text": opt.get_text(strip=True)}
                for opt in select.find_all("option")
            ]
            elements["selects"].append(elem_info)

        # Extract textareas
        for textarea in soup.find_all("textarea"):
            elements["textareas"].append(self._extract_element_info(textarea))

        # Extract forms
        for form in soup.find_all("form"):
            elements["forms"].append(self._extract_element_info(form))

        return elements

    def _extract_element_info(self, element: Any) -> dict[str, Any]:
        """
        Extract information from a BeautifulSoup element.

        Args:
            element: BeautifulSoup element

        Returns:
            Dict with element information
        """
        return {
            "tag": element.name,
            "id": element.get("id", ""),
            "name": element.get("name", ""),
            "class": element.get("class", []),
            "type": element.get("type", ""),
            "text": element.get_text(strip=True),
            "placeholder": element.get("placeholder", ""),
            "aria_label": element.get("aria-label", ""),
            "data_testid": element.get("data-testid", ""),
            "href": element.get("href", ""),
            "value": element.get("value", ""),
        }

    async def _llm_analyze(self, url: str, title: str, html: str) -> dict[str, Any]:
        """
        Use LLM to analyze page structure and identify test scenarios.

        Args:
            url: Page URL
            title: Page title
            html: Page HTML

        Returns:
            AI analysis results
        """
        # Simplify HTML for LLM (remove scripts, styles, etc.)
        simplified_html = self._simplify_html(html)

        # Generate prompt
        user_prompt = ANALYZE_UI_USER_PROMPT.format(
            url=url, title=title, html=simplified_html
        )

        try:
            # Get LLM response
            response = await self.llm_client.generate_with_system_prompt(
                system_prompt=ANALYZE_UI_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=0.3,  # Lower temperature for more consistent output
            )

            # Parse JSON response
            analysis = json.loads(response)
            return analysis

        except json.JSONDecodeError:
            # If LLM doesn't return valid JSON, return raw response
            return {"raw_response": response, "error": "Failed to parse JSON"}
        except Exception as e:
            return {"error": str(e)}

    def _simplify_html(self, html: str, max_length: int = 8000) -> str:
        """
        Simplify HTML for LLM processing.

        Args:
            html: Original HTML
            max_length: Maximum length of simplified HTML

        Returns:
            Simplified HTML
        """
        soup = BeautifulSoup(html, "lxml")

        # Remove scripts, styles, comments
        for element in soup(["script", "style", "noscript"]):
            element.decompose()

        # Remove comments
        for comment in soup.find_all(string=lambda text: isinstance(text, str) and text.strip().startswith("<!--")):
            comment.extract()

        # Get text representation with some structure
        simplified = str(soup)

        # Truncate if too long
        if len(simplified) > max_length:
            simplified = simplified[:max_length] + "\n... (truncated)"

        return simplified

    async def extract_elements_for_selector(
        self, page: Page, selector_type: str = "all"
    ) -> list[dict[str, Any]]:
        """
        Extract elements suitable for creating selectors.

        Args:
            page: Playwright page instance
            selector_type: Type of elements to extract (all, interactive, forms)

        Returns:
            List of elements with selector information
        """
        html = await page.content()
        soup = BeautifulSoup(html, "lxml")

        elements = []

        if selector_type in ["all", "interactive"]:
            # Interactive elements
            for elem in soup.find_all(["button", "a", "input", "select", "textarea"]):
                elements.append(self._create_selector_info(elem))

        if selector_type in ["all", "forms"]:
            # Form elements
            for elem in soup.find_all("form"):
                elements.append(self._create_selector_info(elem))

        return elements

    def _create_selector_info(self, element: Any) -> dict[str, Any]:
        """
        Create selector information for an element.

        Args:
            element: BeautifulSoup element

        Returns:
            Dict with selector options
        """
        selectors = []

        # ID selector (highest priority)
        if element.get("id"):
            selectors.append({"type": "id", "value": f"#{element['id']}"})

        # Data-testid
        if element.get("data-testid"):
            selectors.append(
                {"type": "data-testid", "value": f"[data-testid='{element['data-testid']}']"}
            )

        # Name
        if element.get("name"):
            selectors.append({"type": "name", "value": f"[name='{element['name']}']"})

        # Type + placeholder (for inputs)
        if element.name == "input" and element.get("placeholder"):
            selectors.append(
                {
                    "type": "placeholder",
                    "value": f"input[placeholder='{element['placeholder']}']",
                }
            )

        # Text content (for buttons and links)
        text = element.get_text(strip=True)
        if text and element.name in ["button", "a"]:
            selectors.append({"type": "text", "value": f"text='{text}'"})

        # ARIA label
        if element.get("aria-label"):
            selectors.append(
                {"type": "aria-label", "value": f"[aria-label='{element['aria-label']}']"}
            )

        return {
            "tag": element.name,
            "text": text,
            "selectors": selectors,
            "attributes": self._extract_element_info(element),
        }

    async def save_analysis(self, analysis: dict[str, Any], output_path: Path) -> None:
        """
        Save analysis results to JSON file.

        Args:
            analysis: Analysis results
            output_path: Output file path
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(analysis, f, indent=2)

    async def discover_urls(
        self,
        page: Page,
        start_url: str,
        max_pages: int = 50,
        same_origin_only: bool = True
    ) -> list[str]:
        """
        Discover all URLs from a website by crawling links.

        Args:
            page: Playwright page instance
            start_url: Starting URL to crawl from
            max_pages: Maximum number of pages to discover
            same_origin_only: Only crawl pages from the same origin

        Returns:
            List of discovered URLs
        """
        visited_urls = set()
        to_visit = {start_url}
        discovered = []

        start_origin = self._get_origin(start_url)

        while to_visit and len(visited_urls) < max_pages:
            url = to_visit.pop()

            # Skip if already visited
            if url in visited_urls:
                continue

            # Skip if different origin and same_origin_only
            if same_origin_only and self._get_origin(url) != start_origin:
                continue

            try:
                # Navigate to page
                await page.goto(url, wait_until="networkidle", timeout=30000)
                discovered.append(url)
                visited_urls.add(url)

                # Extract links (without full analysis)
                html = await page.content()
                basic_elements = self._extract_basic_elements(html)
                links = basic_elements.get("links", [])

                for link in links:
                    href = link.get("href", "")
                    if href and not href.startswith(("javascript:", "mailto:")):
                        # Handle hash-based routing (e.g., #!/page)
                        if href.startswith("#!"):
                            # Hash route - construct full URL
                            base_url = url.split("#")[0]  # Remove any existing hash
                            absolute_url = base_url + href
                            if absolute_url not in visited_urls:
                                to_visit.add(absolute_url)
                        elif href.startswith("#"):
                            # Regular anchor link - skip
                            continue
                        else:
                            # Regular URL or relative path
                            absolute_url = urljoin(url, href)
                            if absolute_url not in visited_urls:
                                to_visit.add(absolute_url)

            except Exception:
                # Skip pages that fail to load
                visited_urls.add(url)

        return discovered

    async def crawl_and_analyze(
        self,
        page: Page,
        start_url: str,
        max_pages: int = 50,
        same_origin_only: bool = True,
        progress_callback = None
    ) -> dict[str, dict[str, Any]]:
        """
        Crawl website starting from URL and analyze all discovered pages.

        Args:
            page: Playwright page instance
            start_url: Starting URL to crawl from
            max_pages: Maximum number of pages to analyze
            same_origin_only: Only crawl pages from the same origin
            progress_callback: Optional callback function called after each page analysis

        Returns:
            Dict mapping URLs to their analysis results
        """
        # First, discover all URLs (fast)
        urls = await self.discover_urls(page, start_url, max_pages, same_origin_only)

        # Then analyze each URL (slow, with progress updates)
        analyses = {}
        for i, url in enumerate(urls):
            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
                analysis = await self.analyze_page(page)
                analyses[url] = analysis

                if progress_callback:
                    progress_callback(i + 1, len(urls), url, analysis.get("title", ""))

            except Exception as e:
                # Log error but continue
                analyses[url] = {
                    "url": url,
                    "error": str(e),
                    "title": "",
                    "basic_elements": {},
                    "ai_analysis": {"error": str(e)}
                }
                if progress_callback:
                    progress_callback(i + 1, len(urls), url, f"Error: {e}")

        return analyses

    def _get_origin(self, url: str) -> str:
        """
        Extract origin (scheme + netloc) from URL.

        Args:
            url: URL to parse

        Returns:
            Origin string (e.g., "http://localhost:3000")
        """
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
