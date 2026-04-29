"""Main CLI entry point for AAP Migration Planner."""

import asyncio
import sys
from pathlib import Path

import click
from dotenv import load_dotenv

from aap_migration_planner import __version__
from aap_migration_planner.utils.logging import configure_logging, get_logger

# Load environment variables
load_dotenv()

logger = get_logger(__name__)


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name="aap-planner")
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    default="INFO",
    help="Logging level",
    envvar="LOG_LEVEL",
)
@click.pass_context
def cli(ctx, log_level):
    """AAP Migration Planner - Plan your AAP migrations with confidence.

    Analyze dependencies, detect risks, and get recommended migration sequences
    for Ansible Automation Platform instances.

    Examples:

        # Analyze single organization
        aap-planner analyze --organization "Engineering"

        # Analyze all organizations
        aap-planner analyze --all

        # Generate HTML report
        aap-planner report --format html --output plan.html
    """
    # Configure logging
    configure_logging(level=log_level)

    # If no subcommand, show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command(name="analyze")
@click.option(
    "-o",
    "--organization",
    multiple=True,
    help="Organization name(s) to analyze. Can specify multiple times.",
)
@click.option(
    "--all",
    "analyze_all",
    is_flag=True,
    help="Analyze all organizations in source AAP.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output file for analysis results (JSON format)",
)
def analyze(organization, analyze_all, output):
    """Analyze AAP instance for cross-organization dependencies.

    This command analyzes your AAP instance to discover dependencies
    between organizations, detect potential migration risks, and
    recommend migration sequences.

    Examples:

        # Analyze single organization
        aap-planner analyze --organization "Engineering"

        # Analyze multiple organizations
        aap-planner analyze --organization "Eng" --organization "Ops"

        # Analyze all organizations
        aap-planner analyze --all

        # Save results to file
        aap-planner analyze --all --output analysis.json
    """
    click.echo("🔍 AAP Migration Planner - Dependency Analysis")
    click.echo()

    if not analyze_all and not organization:
        click.echo("❌ Error: Must specify --organization or --all")
        click.echo()
        click.echo("Examples:")
        click.echo('  aap-planner analyze --organization "Engineering"')
        click.echo('  aap-planner analyze --all')
        sys.exit(1)

    # TODO: Implement analysis logic
    click.echo("✅ Analysis feature coming soon!")
    click.echo()
    click.echo("This will analyze:")
    if analyze_all:
        click.echo("  - All organizations in your AAP instance")
    else:
        for org in organization:
            click.echo(f'  - Organization: "{org}"')

    if output:
        click.echo(f"  - Results will be saved to: {output}")

    click.echo()
    click.echo("📊 Stay tuned for the complete analysis implementation!")


@cli.command(name="report")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["html", "text", "json"], case_sensitive=False),
    default="html",
    help="Report output format",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output file path",
)
def report(output_format, output):
    """Generate migration planning report.

    Generates a comprehensive report from previous analysis results,
    including dependency graphs, risk assessments, and recommended
    migration sequences.

    Examples:

        # Generate HTML report
        aap-planner report --format html --output plan.html

        # Generate text report
        aap-planner report --format text

        # Generate JSON export
        aap-planner report --format json --output plan.json
    """
    click.echo("📊 AAP Migration Planner - Report Generation")
    click.echo()
    click.echo(f"Format: {output_format}")

    if output:
        click.echo(f"Output: {output}")

    click.echo()
    click.echo("✅ Report generation feature coming soon!")


@cli.command(name="validate")
def validate():
    """Validate AAP connection and configuration.

    Tests connectivity to AAP instance and validates credentials.

    Example:

        aap-planner validate
    """
    click.echo("🔐 AAP Migration Planner - Configuration Validation")
    click.echo()
    click.echo("✅ Validation feature coming soon!")
    click.echo()
    click.echo("This will validate:")
    click.echo("  - AAP connection")
    click.echo("  - API credentials")
    click.echo("  - Required permissions")


if __name__ == "__main__":
    cli()
