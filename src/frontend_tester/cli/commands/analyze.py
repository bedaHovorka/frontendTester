"""Analyze command for UI analysis."""

import asyncio
import json
from pathlib import Path

from typing_extensions import Annotated
import typer

from frontend_tester.ai.analyzer import UIAnalyzer
from frontend_tester.ai.client import LLMClient
from frontend_tester.cli.utils import console, print_error, print_info, print_success
from frontend_tester.core.config import load_config
from frontend_tester.playwright_runner.browser_manager import BrowserManager


async def analyze_page_async(
    url: str,
    output_file: Path | None,
    browser_type: str,
    headless: bool,
    crawl: bool,
    max_pages: int,
) -> None:
    """Async implementation of page analysis."""
    config = load_config()

    # Validate LLM configuration
    if not config.llm.api_key:
        print_error("LLM API key not configured. Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable.")
        raise typer.Exit(1)

    print_info(f"Analyzing page: {url}")
    print_info(f"Using LLM: {config.llm.provider}/{config.llm.model}")

    # Initialize components
    llm_client = LLMClient(config.llm)
    analyzer = UIAnalyzer(llm_client)

    # Launch browser
    print_info(f"Launching {browser_type} browser...")
    async with BrowserManager(config.browser) as manager:
        page = await manager.create_page(browser_type)

        if crawl:
            # Crawl and analyze multiple pages
            print_info(f"Crawling website (max {max_pages} pages)...")

            # Progress callback
            def progress_cb(current, total, page_url, title):
                console.print(f"  [{current}/{total}] {title[:50]} - {page_url}")

            analyses = await analyzer.crawl_and_analyze(
                page, url, max_pages=max_pages, progress_callback=progress_cb
            )

            console.print(f"\n[bold cyan]Crawl Results: {len(analyses)} pages analyzed[/bold cyan]")

            # Display summary
            for page_url, analysis in analyses.items():
                if "error" not in analysis:
                    console.print(f"  ✓ {analysis.get('title', 'Untitled')} - {page_url}")
                else:
                    console.print(f"  ✗ Error analyzing {page_url}")

            # Save analyses
            output_dir = output_file.parent if output_file else Path("analysis")
            output_dir.mkdir(parents=True, exist_ok=True)

            # Save individual page analyses
            for page_url, analysis in analyses.items():
                # Create safe filename from URL
                from urllib.parse import urlparse
                parsed = urlparse(page_url)
                filename = parsed.path.strip("/").replace("/", "_") or "index"
                if parsed.fragment:
                    filename += "_" + parsed.fragment.replace("/", "_").replace("!", "")
                filename = filename.replace("#", "") + ".json"

                page_output = output_dir / filename
                await analyzer.save_analysis(analysis, page_output)

            # Save combined analysis
            combined_output = output_dir / "all_pages.json"
            with open(combined_output, "w") as f:
                json.dump(analyses, f, indent=2)

            print_success(f"Analyses saved to: {output_dir}/")
            print_info(f"  • Individual pages: {len(analyses)} files")
            print_info(f"  • Combined analysis: all_pages.json")

        else:
            # Single page analysis
            print_info(f"Navigating to {url}...")
            await page.goto(url, wait_until="networkidle", timeout=60000)

            # Analyze page
            print_info("Analyzing page structure...")
            analysis = await analyzer.analyze_page(page)

            # Display results
            console.print("\n[bold cyan]Analysis Results:[/bold cyan]")
            console.print(f"[bold]URL:[/bold] {analysis['url']}")
            console.print(f"[bold]Title:[/bold] {analysis['title']}")

            # Display basic elements summary
            basic_elements = analysis.get("basic_elements", {})
            console.print("\n[bold green]Detected Elements:[/bold green]")
            for elem_type, elements in basic_elements.items():
                if elements:
                    console.print(f"  • {elem_type.capitalize()}: {len(elements)}")

            # Display AI analysis
            ai_analysis = analysis.get("ai_analysis", {})
            if ai_analysis and "error" not in ai_analysis:
                console.print("\n[bold green]AI Analysis:[/bold green]")

                # User flows
                user_flows = ai_analysis.get("user_flows", [])
                if user_flows:
                    console.print(f"  • User Flows: {len(user_flows)}")
                    for flow in user_flows[:3]:  # Show first 3
                        console.print(f"    - {flow.get('name', 'Unnamed flow')}")

                # Interactive elements
                interactive = ai_analysis.get("interactive_elements", [])
                if interactive:
                    console.print(f"  • Interactive Elements: {len(interactive)}")

                # Forms
                forms = ai_analysis.get("forms", [])
                if forms:
                    console.print(f"  • Forms: {len(forms)}")

            elif "error" in ai_analysis:
                print_error(f"AI analysis error: {ai_analysis['error']}")

            # Save to file
            if output_file:
                await analyzer.save_analysis(analysis, output_file)
                print_success(f"Analysis saved to: {output_file}")
            else:
                # Save to default location
                default_output = Path("analysis/analysis.json")
                await analyzer.save_analysis(analysis, default_output)
                print_success(f"Analysis saved to: {default_output}")

            # Display sample JSON
            console.print("\n[bold cyan]Sample Analysis (truncated):[/bold cyan]")
            sample_analysis = {
                "url": analysis["url"],
                "title": analysis["title"],
                "element_counts": {k: len(v) for k, v in basic_elements.items()},
            }
            console.print(json.dumps(sample_analysis, indent=2))

        await page.close()

    print_success("Analysis complete!")


def analyze_command(
    url: Annotated[str, typer.Argument(help="URL to analyze")],
    output: Annotated[
        Path | None, typer.Option("--output", "-o", help="Output file path or directory")
    ] = None,
    browser: Annotated[
        str, typer.Option("--browser", "-b", help="Browser to use")
    ] = "chromium",
    headed: Annotated[
        bool, typer.Option("--headed", help="Run browser in headed mode")
    ] = False,
    crawl: Annotated[
        bool, typer.Option("--crawl", "-c", help="Crawl and analyze all linked pages")
    ] = False,
    max_pages: Annotated[
        int, typer.Option("--max-pages", help="Maximum pages to crawl")
    ] = 50,
) -> None:
    """
    Analyze a web page and extract UI structure.

    This command uses Playwright to load the page and AI to analyze
    the structure and identify testable elements and user flows.

    Example:
        frontend-tester analyze http://localhost:3000
        frontend-tester analyze http://localhost:3000 --crawl --max-pages 20
        frontend-tester analyze http://localhost:3000 --output analysis.json
        frontend-tester analyze http://localhost:3000 --browser firefox --headed
    """
    try:
        asyncio.run(
            analyze_page_async(
                url=url,
                output_file=output,
                browser_type=browser,
                headless=not headed,
                crawl=crawl,
                max_pages=max_pages,
            )
        )
    except Exception as e:
        print_error(f"Analysis failed: {e}")
        raise typer.Exit(1)
