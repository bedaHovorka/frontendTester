"""Step definition generator using Jinja2 templates."""

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


def generate_step_definitions(
    output_path: Path,
    feature_name: str,
    steps: list[dict[str, Any]],
) -> None:
    """
    Generate Python step definitions from template.

    Args:
        output_path: Path to write the steps file
        feature_name: Name of the feature
        steps: List of step definitions with implementation
    """
    env = get_template_env()
    template = env.get_template("steps.jinja2")

    content = template.render(
        feature_name=feature_name,
        steps=steps,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content)


# This will be fully implemented in Phase 3 with AI integration
