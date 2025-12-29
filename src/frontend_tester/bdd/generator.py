"""Feature file generator using Jinja2 templates."""

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader


def get_template_env() -> Environment:
    """Get Jinja2 environment for BDD templates."""
    template_dir = Path(__file__).parent / "templates"
    return Environment(
        loader=FileSystemLoader(str(template_dir)),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def generate_feature_file(
    output_path: Path,
    feature_name: str,
    scenarios: list[dict[str, Any]],
    feature_description: str = "",
    background_steps: list[dict[str, str]] | None = None,
) -> None:
    """
    Generate a Gherkin feature file from template.

    Args:
        output_path: Path to write the feature file
        feature_name: Name of the feature
        scenarios: List of scenarios with steps
        feature_description: Optional feature description
        background_steps: Optional background steps
    """
    env = get_template_env()
    template = env.get_template("feature.jinja2")

    content = template.render(
        feature_name=feature_name,
        feature_description=feature_description,
        background_steps=background_steps or [],
        scenarios=scenarios,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content)


# This will be fully implemented in Phase 3 with AI integration
