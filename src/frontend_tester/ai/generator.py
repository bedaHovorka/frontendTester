"""Test generation module for creating Gherkin scenarios and step definitions."""

import json
from pathlib import Path
from typing import Any

from frontend_tester.ai.client import LLMClient
from frontend_tester.ai.prompts.test_generation import (
    GENERATE_FEATURE_FILE_SYSTEM_PROMPT,
    GENERATE_FEATURE_FILE_USER_PROMPT,
    GENERATE_SCENARIOS_SYSTEM_PROMPT,
    GENERATE_SCENARIOS_USER_PROMPT,
    GENERATE_STEP_DEFINITIONS_SYSTEM_PROMPT,
    GENERATE_STEP_DEFINITIONS_USER_PROMPT,
)


class TestGenerator:
    """Generate BDD test scenarios and step definitions using LLM."""

    def __init__(self, llm_client: LLMClient):
        """
        Initialize test generator.

        Args:
            llm_client: LLM client for AI-powered generation
        """
        self.llm_client = llm_client

    async def generate_scenarios(
        self, url: str, title: str, analysis: dict[str, Any]
    ) -> str:
        """
        Generate Gherkin scenarios from UI analysis.

        Args:
            url: Page URL
            title: Page title
            analysis: UI analysis results

        Returns:
            Generated Gherkin scenarios as string
        """
        user_prompt = GENERATE_SCENARIOS_USER_PROMPT.format(
            url=url,
            title=title,
            analysis=json.dumps(analysis, indent=2),
        )

        scenarios = await self.llm_client.generate_with_system_prompt(
            system_prompt=GENERATE_SCENARIOS_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.7,
            max_tokens=4000,
        )

        return scenarios

    async def generate_feature_file(
        self,
        app_name: str,
        url: str,
        flow_name: str,
        elements: list[dict[str, Any]],
    ) -> str:
        """
        Generate complete Gherkin feature file.

        Args:
            app_name: Application name
            url: Page URL
            flow_name: User flow name
            elements: List of interactive elements

        Returns:
            Generated feature file content
        """
        user_prompt = GENERATE_FEATURE_FILE_USER_PROMPT.format(
            app_name=app_name,
            url=url,
            flow_name=flow_name,
            elements=json.dumps(elements, indent=2),
        )

        feature_content = await self.llm_client.generate_with_system_prompt(
            system_prompt=GENERATE_FEATURE_FILE_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.6,
            max_tokens=3000,
        )

        # Clean up markdown code fences if present
        return self._clean_code_response(feature_content)

    async def generate_step_definitions(
        self,
        gherkin_steps: list[str],
        url: str,
        elements: list[dict[str, Any]],
    ) -> str:
        """
        Generate Python step definitions for Gherkin steps.

        Args:
            gherkin_steps: List of Gherkin step strings
            url: Page URL
            elements: Available elements from analysis

        Returns:
            Generated Python code for step definitions
        """
        steps_text = "\n".join(gherkin_steps)

        user_prompt = GENERATE_STEP_DEFINITIONS_USER_PROMPT.format(
            gherkin_steps=steps_text,
            url=url,
            elements=json.dumps(elements, indent=2),
        )

        step_definitions = await self.llm_client.generate_with_system_prompt(
            system_prompt=GENERATE_STEP_DEFINITIONS_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.4,  # Lower temperature for code generation
            max_tokens=4000,
        )

        # Clean up markdown code fences if present
        return self._clean_code_response(step_definitions)

    async def generate_complete_test_suite(
        self,
        app_name: str,
        url: str,
        analysis: dict[str, Any],
        output_dir: Path,
    ) -> dict[str, Path]:
        """
        Generate complete test suite with feature files and step definitions.

        Args:
            app_name: Application name
            url: Page URL
            analysis: UI analysis results
            output_dir: Output directory for generated files

        Returns:
            Dict mapping file types to generated file paths
        """
        generated_files = {}

        # Create output directories
        features_dir = output_dir / "features"
        steps_dir = output_dir / "steps"
        features_dir.mkdir(parents=True, exist_ok=True)
        steps_dir.mkdir(parents=True, exist_ok=True)

        # Extract user flows from analysis
        ai_analysis = analysis.get("ai_analysis", {})
        user_flows = ai_analysis.get("user_flows", [])

        if not user_flows:
            # Generate generic scenarios if no flows detected
            scenarios = await self.generate_scenarios(
                url=url,
                title=analysis.get("title", ""),
                analysis=analysis,
            )

            # Clean markdown code fences
            scenarios_cleaned = self._clean_code_response(scenarios)

            # Generate feature filename from URL
            from urllib.parse import urlparse
            parsed = urlparse(url)
            feature_name = parsed.path.strip("/").replace("/", "_") or "index"
            if parsed.fragment:
                fragment_clean = parsed.fragment.replace("/", "_").replace("!", "").replace("#", "")
                if fragment_clean:
                    feature_name += "_" + fragment_clean

            # Save feature file
            feature_file = features_dir / f"{feature_name}.feature"
            with open(feature_file, "w") as f:
                f.write(scenarios_cleaned)

            generated_files["feature"] = feature_file

            # Extract steps and generate step definitions
            steps = self._extract_steps_from_feature(scenarios_cleaned)
            if steps:
                elements = analysis.get("basic_elements", {})
                step_definitions = await self.generate_step_definitions(
                    gherkin_steps=steps,
                    url=url,
                    elements=elements,
                )

                # Save step definitions
                steps_file = steps_dir / f"test_{feature_name}.py"
                with open(steps_file, "w") as f:
                    f.write(step_definitions)

                generated_files["steps"] = steps_file

        else:
            # Generate feature file for each flow
            for i, flow in enumerate(user_flows):
                flow_name = flow.get("name", f"Flow {i + 1}")
                elements = analysis.get("basic_elements", {})

                # Generate feature file
                feature_content = await self.generate_feature_file(
                    app_name=app_name,
                    url=url,
                    flow_name=flow_name,
                    elements=elements,
                )

                # Save feature file
                safe_flow_name = self._sanitize_filename(flow_name)
                feature_file = features_dir / f"{safe_flow_name}.feature"
                with open(feature_file, "w") as f:
                    f.write(feature_content)

                generated_files[f"feature_{safe_flow_name}"] = feature_file

                # Extract steps from feature content
                steps = self._extract_steps_from_feature(feature_content)

                # Generate step definitions
                if steps:
                    step_definitions = await self.generate_step_definitions(
                        gherkin_steps=steps,
                        url=url,
                        elements=elements,
                    )

                    # Save step definitions
                    steps_file = steps_dir / f"test_{safe_flow_name}.py"
                    with open(steps_file, "w") as f:
                        f.write(step_definitions)

                    generated_files[f"steps_{safe_flow_name}"] = steps_file

        return generated_files

    def _extract_steps_from_feature(self, feature_content: str) -> list[str]:
        """
        Extract Gherkin steps from feature file content.

        Args:
            feature_content: Feature file content

        Returns:
            List of unique step strings
        """
        steps = []
        lines = feature_content.split("\n")

        for line in lines:
            line = line.strip()
            if any(line.startswith(keyword) for keyword in ["Given", "When", "Then", "And", "But"]):
                steps.append(line)

        # Return unique steps
        return list(set(steps))

    def _sanitize_filename(self, name: str) -> str:
        """
        Sanitize string for use as filename.

        Args:
            name: Original name

        Returns:
            Sanitized filename
        """
        # Replace spaces and special characters
        safe_name = name.lower()
        safe_name = safe_name.replace(" ", "_")
        safe_name = "".join(c for c in safe_name if c.isalnum() or c == "_")

        return safe_name

    def _clean_code_response(self, response: str) -> str:
        """
        Clean LLM response by removing markdown code fences and preamble.

        Args:
            response: Raw LLM response

        Returns:
            Cleaned response
        """
        import re

        # Remove markdown code fences (```python, ```gherkin, etc.)
        cleaned = re.sub(r'^```[a-z]*\n', '', response, flags=re.MULTILINE)
        cleaned = re.sub(r'\n```$', '', cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r'^```[a-z]*$', '', cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r'^```$', '', cleaned, flags=re.MULTILINE)

        # Remove common preamble patterns
        # Match lines like "Here is..." or "Here's..." at the start
        cleaned = re.sub(r'^Here (is|are|\'s).*?:\s*\n+', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'^Below (is|are).*?:\s*\n+', '', cleaned, flags=re.IGNORECASE)

        # If the response starts with "Feature:" or "import", it's likely clean
        # Otherwise, try to find the actual code start
        if not (cleaned.strip().startswith(('Feature:', 'import', 'from', '@', 'def', 'class'))):
            # Try to find where actual code starts
            lines = cleaned.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith(('Feature:', 'import', 'from', '@', 'def', 'class')):
                    cleaned = '\n'.join(lines[i:])
                    break

        return cleaned.strip()

    async def save_feature_file(
        self, feature_content: str, output_path: Path
    ) -> None:
        """
        Save generated feature file.

        Args:
            feature_content: Feature file content
            output_path: Output file path
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            f.write(feature_content)

    async def save_step_definitions(
        self, step_definitions: str, output_path: Path
    ) -> None:
        """
        Save generated step definitions.

        Args:
            step_definitions: Step definitions code
            output_path: Output file path
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            f.write(step_definitions)
