"""Data loading utilities for AAP analysis."""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from aap_migration_planner.analysis.analyzer import CrossOrgDependencyAnalyzer
from aap_migration_planner.client.aap_client import AAPClient
from aap_migration_planner.config import AAPInstanceConfig
from aap_migration_planner.database import DatabaseService


@st.cache_data(ttl=3600)
def load_from_file(file_path: str) -> dict[str, Any] | None:
    """Load analysis data from JSON file.

    Args:
        file_path: Path to JSON file

    Returns:
        Analysis data or None if file doesn't exist
    """
    path = Path(file_path)
    if not path.exists():
        return None

    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None


def save_to_file(data: dict[str, Any], file_path: str):
    """Save analysis data to JSON file.

    Args:
        data: Analysis data to save
        file_path: Path to save JSON file
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")


async def run_analysis_async(
    url: str,
    token: str,
    verify_ssl: bool,
    org_name: str | None = None,
    progress_callback: callable | None = None,
    max_concurrent_orgs: int = 5,
    max_concurrent_resources: int = 20,
) -> dict[str, Any] | None:
    """Run dependency analysis asynchronously with parallel processing.

    Args:
        url: AAP URL
        token: API token
        verify_ssl: Whether to verify SSL
        org_name: Optional specific organization to analyze
        progress_callback: Optional callback(current, total, message) for progress
        max_concurrent_orgs: Max orgs to analyze in parallel (default: 5)
        max_concurrent_resources: Max resource fetches in parallel (default: 20)

    Returns:
        Analysis results or None on error
    """
    try:
        # Create config
        config = AAPInstanceConfig(
            url=url,
            token=token,
            verify_ssl=verify_ssl,
        )

        # Initialize database service
        db_service = DatabaseService(db_path="data/aap_analysis.db")

        # Create client
        async with AAPClient(config) as client:
            analyzer = CrossOrgDependencyAnalyzer(
                client,
                max_concurrent_orgs=max_concurrent_orgs,
                max_concurrent_resources=max_concurrent_resources,
                progress_callback=progress_callback,
                db_service=db_service,
                use_cache=True,
                cache_ttl_hours=24,
            )

            if org_name:
                # Analyze single organization
                report = await analyzer.analyze_organization(org_name)
                return {
                    "type": "single_org",
                    "org_name": org_name,
                    "report": {
                        "org_name": report.org_name,
                        "org_id": report.org_id,
                        "resource_count": report.resource_count,
                        "has_cross_org_deps": report.has_cross_org_deps,
                        "dependencies": {
                            org: [
                                {
                                    "resource_type": dep.resource_type,
                                    "resource_id": dep.resource_id,
                                    "resource_name": dep.resource_name,
                                    "org_name": dep.org_name,
                                    "required_by": dep.required_by,
                                }
                                for dep in deps
                            ]
                            for org, deps in report.dependencies.items()
                        },
                        "can_migrate_standalone": report.can_migrate_standalone,
                        "required_migrations_before": report.required_migrations_before,
                    },
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                # Analyze all organizations
                global_report = await analyzer.analyze_all_organizations()
                return {
                    "type": "global",
                    "analysis_date": global_report.analysis_date.isoformat(),
                    "source_url": global_report.source_url,
                    "total_organizations": global_report.total_organizations,
                    "analyzed_organizations": global_report.analyzed_organizations,
                    "independent_orgs": global_report.independent_orgs,
                    "dependent_orgs": global_report.dependent_orgs,
                    "migration_order": global_report.migration_order,
                    "migration_phases": global_report.migration_phases,
                    "global_resources": global_report.global_resources,
                    "org_reports": {
                        org_name: {
                            "org_name": report.org_name,
                            "org_id": report.org_id,
                            "resource_count": report.resource_count,
                            "has_cross_org_deps": report.has_cross_org_deps,
                            "dependencies": {
                                org: [
                                    {
                                        "resource_type": dep.resource_type,
                                        "resource_id": dep.resource_id,
                                        "resource_name": dep.resource_name,
                                        "org_name": dep.org_name,
                                        "required_by": dep.required_by,
                                    }
                                    for dep in deps
                                ]
                                for org, deps in report.dependencies.items()
                            },
                            "resources": report.resources,  # All resources in this org
                            "can_migrate_standalone": report.can_migrate_standalone,
                            "required_migrations_before": report.required_migrations_before,
                        }
                        for org_name, report in global_report.org_reports.items()
                    },
                    "timestamp": datetime.now().isoformat(),
                }

    except Exception as e:
        st.error(f"Analysis failed: {str(e)}")
        import traceback

        st.code(traceback.format_exc())
        return None


def run_analysis(
    url: str, token: str, verify_ssl: bool, org_name: str | None = None
) -> dict[str, Any] | None:
    """Run dependency analysis (sync wrapper).

    Args:
        url: AAP URL
        token: API token
        verify_ssl: Whether to verify SSL
        org_name: Optional specific organization to analyze

    Returns:
        Analysis results or None on error
    """
    return asyncio.run(run_analysis_async(url, token, verify_ssl, org_name))


def get_sample_data() -> dict[str, Any]:
    """Get sample data for demo purposes.

    Returns:
        Sample analysis data
    """
    return {
        "type": "global",
        "analysis_date": datetime.now().isoformat(),
        "source_url": "https://aap-demo.example.com",
        "total_organizations": 5,
        "analyzed_organizations": [
            "Engineering",
            "Operations",
            "QA",
            "Production",
            "Shared Services",
        ],
        "independent_orgs": ["Shared Services"],
        "dependent_orgs": ["Engineering", "Operations", "QA", "Production"],
        "migration_order": ["Shared Services", "Engineering", "QA", "Operations", "Production"],
        "migration_phases": [
            {
                "phase": 1,
                "orgs": ["Shared Services"],
                "description": "Independent organizations (no dependencies)",
            },
            {
                "phase": 2,
                "orgs": ["Engineering", "Operations"],
                "description": "Organizations dependent on Phase 1 migrations",
            },
            {
                "phase": 3,
                "orgs": ["QA", "Production"],
                "description": "Organizations dependent on Phase 2 migrations",
            },
        ],
        "org_reports": {
            "Engineering": {
                "org_name": "Engineering",
                "org_id": 1,
                "resource_count": 150,
                "has_cross_org_deps": True,
                "dependencies": {
                    "Shared Services": [
                        {
                            "resource_type": "credentials",
                            "resource_id": 10,
                            "resource_name": "AWS Prod Credentials",
                            "org_name": "Shared Services",
                            "required_by": [
                                {"type": "job_templates", "id": 25, "name": "Deploy App"}
                            ],
                        }
                    ]
                },
                "can_migrate_standalone": False,
                "required_migrations_before": ["Shared Services"],
            }
        },
        "timestamp": datetime.now().isoformat(),
    }
