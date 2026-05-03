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
    "--organization",
    "-o",
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
        click.echo("  aap-planner analyze --all")
        sys.exit(1)

    # Import dependencies
    from aap_migration_planner.analysis.analyzer import CrossOrgDependencyAnalyzer
    from aap_migration_planner.client.aap_client import AAPClient
    from aap_migration_planner.config import AAPInstanceConfig

    try:
        # Load configuration from environment
        click.echo("📡 Connecting to AAP instance...")
        config = AAPInstanceConfig.from_env()
        click.echo(f"   URL: {config.url}")
        click.echo()

        # Run analysis
        async def run():
            async with AAPClient(config) as client:
                analyzer = CrossOrgDependencyAnalyzer(client)

                if analyze_all:
                    click.echo("🔎 Analyzing all organizations...")
                    report = await analyzer.analyze_all_organizations()

                    click.echo()
                    click.echo("✅ Analysis complete!")
                    click.echo()
                    click.echo("📊 Summary:")
                    click.echo(f"   Total organizations: {report.total_organizations}")
                    click.echo(f"   Independent orgs:    {len(report.independent_orgs)}")
                    click.echo(f"   Dependent orgs:      {len(report.dependent_orgs)}")
                    click.echo()

                    if report.migration_phases:
                        click.echo(f"🗓️  Migration Phases: {len(report.migration_phases)}")
                        for phase in report.migration_phases:
                            click.echo(f"   Phase {phase['phase']}: {', '.join(phase['orgs'])}")

                    return report
                else:
                    # Analyze specific organizations
                    reports = []
                    for org_name in organization:
                        click.echo(f"🔎 Analyzing organization: {org_name}...")
                        org_report = await analyzer.analyze_organization(org_name)
                        reports.append(org_report)

                        click.echo(f"   Resources: {org_report.resource_count}")
                        click.echo(f"   Dependencies: {len(org_report.dependencies)} org(s)")
                        standalone = "✅" if org_report.can_migrate_standalone else "❌"
                        click.echo(f"   Can migrate standalone: {standalone}")
                        click.echo()

                    return reports[0] if len(reports) == 1 else reports

        # Execute async analysis
        result = asyncio.run(run())

        # Save to file if requested
        if output:
            import json
            from datetime import datetime

            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Convert to dict
            def to_dict(obj):
                if hasattr(obj, "__dict__"):
                    return {k: to_dict(v) for k, v in obj.__dict__.items() if not k.startswith("_")}
                elif isinstance(obj, list):
                    return [to_dict(item) for item in obj]
                elif isinstance(obj, dict):
                    return {k: to_dict(v) for k, v in obj.items()}
                elif isinstance(obj, datetime):
                    return obj.isoformat()
                else:
                    return obj

            data = to_dict(result)

            with open(output_path, "w") as f:
                json.dump(data, f, indent=2, default=str)

            click.echo(f"💾 Results saved to: {output}")
            click.echo()

    except ValueError as e:
        click.echo(f"❌ Configuration Error: {str(e)}")
        click.echo()
        click.echo("Make sure you have set the following environment variables:")
        click.echo("  AAP_URL=https://your-aap-instance.com")
        click.echo("  AAP_TOKEN=your_api_token")
        click.echo()
        click.echo("Or create a .env file with these values.")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Analysis failed: {str(e)}")
        logger.exception("analysis_failed", error=str(e))
        sys.exit(1)


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
@click.option(
    "--input",
    "-i",
    type=click.Path(exists=True, path_type=Path),
    help="Input analysis JSON file (if not provided, will run fresh analysis)",
)
def report(output_format, output, input):
    """Generate migration planning report.

    Generates a comprehensive report from previous analysis results,
    including dependency graphs, risk assessments, and recommended
    migration sequences.

    Examples:

        # Generate HTML report from analysis file
        aap-planner report --input analysis.json --format html --output plan.html

        # Generate text report (fresh analysis)
        aap-planner report --format text

        # Generate JSON export
        aap-planner report --format json --output plan.json
    """
    click.echo("📊 AAP Migration Planner - Report Generation")
    click.echo()

    import json
    from datetime import datetime

    from aap_migration_planner.analysis.analyzer import (
        CrossOrgDependencyAnalyzer,
    )
    from aap_migration_planner.client.aap_client import AAPClient
    from aap_migration_planner.config import AAPInstanceConfig
    from aap_migration_planner.reporting import html_report, text_report

    try:
        # Load or generate analysis data
        if input:
            click.echo(f"📂 Loading analysis from: {input}")
            with open(input) as f:
                data = json.load(f)
            report_data = data
        else:
            click.echo("🔍 Running fresh analysis...")
            config = AAPInstanceConfig.from_env()

            async def run():
                async with AAPClient(config) as client:
                    analyzer = CrossOrgDependencyAnalyzer(client)
                    return await analyzer.analyze_all_organizations()

            result = asyncio.run(run())

            # Convert to dict
            def to_dict(obj):
                if hasattr(obj, "__dict__"):
                    return {k: to_dict(v) for k, v in obj.__dict__.items() if not k.startswith("_")}
                elif isinstance(obj, list):
                    return [to_dict(item) for item in obj]
                elif isinstance(obj, dict):
                    return {k: to_dict(v) for k, v in obj.items()}
                elif isinstance(obj, datetime):
                    return obj.isoformat()
                else:
                    return obj

            report_data = to_dict(result)

        # Generate report based on format
        if output_format == "html":
            click.echo("🌐 Generating HTML report...")
            html_content = html_report.generate_html_report(report_data)

            if output:
                output_path = Path(output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "w") as f:
                    f.write(html_content)
                click.echo(f"✅ HTML report saved to: {output}")
            else:
                click.echo(html_content)

        elif output_format == "text":
            click.echo("📝 Generating text report...")
            text_content = text_report.generate_text_report(report_data)

            if output:
                output_path = Path(output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "w") as f:
                    f.write(text_content)
                click.echo(f"✅ Text report saved to: {output}")
            else:
                click.echo(text_content)

        elif output_format == "json":
            click.echo("📋 Generating JSON export...")

            if output:
                output_path = Path(output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "w") as f:
                    json.dump(report_data, f, indent=2, default=str)
                click.echo(f"✅ JSON export saved to: {output}")
            else:
                click.echo(json.dumps(report_data, indent=2, default=str))

        click.echo()
        click.echo("✅ Report generation complete!")

    except FileNotFoundError:
        click.echo(f"❌ Input file not found: {input}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Report generation failed: {str(e)}")
        logger.exception("report_generation_failed", error=str(e))
        sys.exit(1)


@cli.command(name="validate")
def validate():
    """Validate AAP connection and configuration.

    Tests connectivity to AAP instance and validates credentials.

    Example:

        aap-planner validate
    """
    click.echo("🔐 AAP Migration Planner - Configuration Validation")
    click.echo()

    from aap_migration_planner.client.aap_client import AAPClient
    from aap_migration_planner.config import AAPInstanceConfig

    try:
        # Load configuration
        click.echo("📋 Loading configuration...")
        config = AAPInstanceConfig.from_env()
        click.echo(f"   URL: {config.url}")
        click.echo(f"   SSL Verify: {config.verify_ssl}")
        click.echo(f"   Timeout: {config.timeout}s")
        click.echo()

        # Test connection
        click.echo("🔌 Testing AAP connection...")

        async def test_connection():
            async with AAPClient(config) as client:
                # Get version
                version = await client.get_version()
                click.echo("   ✅ Connected successfully!")
                click.echo(f"   AAP Version: {version}")
                click.echo()

                # Get organization count
                click.echo("📊 Checking permissions...")
                orgs = await client.get_organizations()
                click.echo("   ✅ API credentials valid")
                click.echo(f"   Organizations accessible: {len(orgs)}")

                if orgs:
                    click.echo()
                    click.echo("   Organizations:")
                    for org in orgs[:10]:  # Show first 10
                        click.echo(f"     - {org.get('name')} (ID: {org.get('id')})")

                    if len(orgs) > 10:
                        click.echo(f"     ... and {len(orgs) - 10} more")

                click.echo()
                click.echo("✅ Validation successful! Ready to run analysis.")
                return True

        asyncio.run(test_connection())

    except ValueError as e:
        click.echo(f"❌ Configuration Error: {str(e)}")
        click.echo()
        click.echo("Required environment variables:")
        click.echo("  AAP_URL=https://your-aap-instance.com")
        click.echo("  AAP_TOKEN=your_api_token")
        click.echo()
        click.echo("Optional:")
        click.echo("  AAP_VERIFY_SSL=true|false  (default: true)")
        click.echo("  AAP_TIMEOUT=30  (default: 30 seconds)")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Connection failed: {str(e)}")
        click.echo()
        click.echo("Please check:")
        click.echo("  - AAP URL is correct and accessible")
        click.echo("  - API token is valid")
        click.echo("  - Network connectivity to AAP instance")
        click.echo("  - SSL certificate if verify_ssl is enabled")
        logger.exception("validation_failed", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    cli()
