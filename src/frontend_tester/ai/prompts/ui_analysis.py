"""Prompt templates for UI analysis."""

ANALYZE_UI_SYSTEM_PROMPT = """You are an expert frontend QA engineer specializing in blackbox testing.
Your task is to analyze web page HTML and identify testable elements and user flows.

Focus on:
1. Interactive elements (buttons, links, forms, inputs)
2. Navigation patterns
3. User workflows and common scenarios
4. Form validations
5. Dynamic content

Provide structured analysis that can be used to generate automated tests."""

ANALYZE_UI_USER_PROMPT = """Analyze the following HTML from a web page:

URL: {url}
Page Title: {title}

HTML Content:
{html}

Please provide:
1. List of all interactive elements (buttons, links, inputs, selects, etc.) with their:
   - Type (button, link, input, etc.)
   - Identifier (id, name, or unique selector)
   - Label/text
   - Purpose

2. Identified user flows/scenarios (e.g., "Login flow", "Registration flow")

3. Forms on the page with their fields

4. Navigation elements (menus, breadcrumbs, etc.)

Format your response as JSON with this structure:
{{
  "interactive_elements": [
    {{
      "type": "button",
      "identifier": "submit-btn",
      "label": "Submit",
      "purpose": "Submit form"
    }}
  ],
  "user_flows": [
    {{
      "name": "Login Flow",
      "steps": ["Navigate to login", "Enter credentials", "Click submit", "Verify success"]
    }}
  ],
  "forms": [
    {{
      "name": "Login Form",
      "fields": [
        {{"type": "email", "identifier": "email", "label": "Email"}}
      ]
    }}
  ],
  "navigation": [
    {{"type": "link", "identifier": "home-link", "label": "Home"}}
  ]
}}
"""

EXTRACT_ELEMENTS_SYSTEM_PROMPT = """You are a web scraping expert.
Extract all interactive elements from the HTML that can be used for automated testing.
Focus on elements users can interact with: buttons, links, inputs, selects, textareas."""

EXTRACT_ELEMENTS_USER_PROMPT = """Extract all interactive elements from this HTML:

{html}

For each element, provide:
- Element type (button, link, input, select, etc.)
- Unique selector (prefer: id > data-testid > name > unique class > xpath)
- Text/label
- Attributes (name, placeholder, type, etc.)

Return as JSON array."""
