"""Resource quality and governance analysis for AAP instances."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DuplicateResource:
    """Represents a duplicate resource found within an organization."""

    name: str
    resource_type: str  # "job_template", "workflow_job_template", etc.
    count: int
    ids: list[int]
    severity: str  # "error", "warning", "info"
    impact: str  # Human-readable impact description
    recommendation: str  # Suggested fix
    details: list[dict[str, Any]] = field(default_factory=list)  # Full resource data

    @property
    def severity_emoji(self) -> str:
        """Get emoji for severity level."""
        return {
            "error": "🔴",
            "warning": "🟡",
            "info": "🔵",
        }.get(self.severity, "⚪")

    @property
    def resource_type_display(self) -> str:
        """Get display name for resource type."""
        type_map = {
            "job_templates": "Job Template",
            "workflow_job_templates": "Workflow",
            "inventories": "Inventory",
            "projects": "Project",
            "credentials": "Credential",
            "execution_environments": "Execution Environment",
            "credential_types": "Credential Type",
        }
        return type_map.get(self.resource_type, self.resource_type.replace("_", " ").title())


@dataclass
class QualityReport:
    """Quality analysis report for an organization."""

    org_name: str
    duplicate_count: int
    duplicates: list[DuplicateResource] = field(default_factory=list)
    quality_score: float = 100.0  # 0-100, decreases with issues

    def get_severity_counts(self) -> dict[str, int]:
        """Get count of duplicates by severity."""
        counts = {"error": 0, "warning": 0, "info": 0}
        for dup in self.duplicates:
            counts[dup.severity] = counts.get(dup.severity, 0) + 1
        return counts

    def get_duplicates_by_type(self) -> dict[str, list[DuplicateResource]]:
        """Group duplicates by resource type."""
        by_type: dict[str, list[DuplicateResource]] = {}
        for dup in self.duplicates:
            if dup.resource_type not in by_type:
                by_type[dup.resource_type] = []
            by_type[dup.resource_type].append(dup)
        return by_type


def detect_duplicates(
    resources: dict[str, list[dict[str, Any]]], org_name: str
) -> list[DuplicateResource]:
    """Detect duplicate resources within an organization.

    Args:
        resources: Resources grouped by type
        org_name: Organization name

    Returns:
        List of DuplicateResource objects
    """
    duplicates = []

    # Resource types to check for duplicates
    check_types = [
        "job_templates",
        "workflow_job_templates",
        "inventories",
        "projects",
        "credentials",
        "execution_environments",
    ]

    for resource_type in check_types:
        if resource_type not in resources:
            continue

        resource_list = resources[resource_type]

        # Group by name (case-insensitive)
        name_groups: dict[str, list[dict[str, Any]]] = {}
        for resource in resource_list:
            name = resource.get("name", "").lower().strip()
            if not name:
                continue

            if name not in name_groups:
                name_groups[name] = []
            name_groups[name].append(resource)

        # Find duplicates (same name appearing multiple times)
        for name, group in name_groups.items():
            if len(group) < 2:
                continue

            # Determine severity and recommendation
            count = len(group)
            if count >= 3:
                severity = "error"
                impact = f"HIGH - {count} copies will cause migration conflicts"
            elif count == 2:
                severity = "warning"
                impact = "MEDIUM - Creates confusion and potential conflicts"
            else:
                severity = "info"
                impact = "LOW - Informational"

            # Generate recommendation based on resource type
            original_name = group[0].get("name", name)
            if resource_type == "job_templates":
                recommendation = (
                    f"Consolidate or add environment prefix:\n"
                    f"  • prod-{original_name}\n"
                    f"  • dev-{original_name}\n"
                    f"  • test-{original_name}"
                )
            elif resource_type == "workflow_job_templates":
                recommendation = (
                    f"Add purpose or schedule identifier:\n"
                    f"  • {original_name}-nightly\n"
                    f"  • {original_name}-weekly\n"
                    f"  • {original_name}-ondemand"
                )
            elif resource_type == "inventories":
                recommendation = (
                    f"Add environment or datacenter prefix:\n"
                    f"  • prod-{original_name}\n"
                    f"  • staging-{original_name}\n"
                    f"  • us-east-{original_name}"
                )
            else:
                recommendation = "Consolidate duplicates or add differentiating prefix/suffix"

            duplicate = DuplicateResource(
                name=original_name,
                resource_type=resource_type,
                count=count,
                ids=[r.get("id") for r in group if r.get("id")],
                severity=severity,
                impact=impact,
                recommendation=recommendation,
                details=group,
            )
            duplicates.append(duplicate)

    return duplicates


def calculate_quality_score(duplicates: list[DuplicateResource]) -> float:
    """Calculate quality score based on duplicate issues.

    Args:
        duplicates: List of duplicate resources

    Returns:
        Quality score (0-100), where 100 is perfect
    """
    if not duplicates:
        return 100.0

    # Penalty by severity
    penalties = {"error": 10, "warning": 5, "info": 2}

    total_penalty = 0
    for dup in duplicates:
        penalty = penalties.get(dup.severity, 0)
        # Multiply by number of duplicates (more copies = worse)
        total_penalty += penalty * (dup.count - 1)

    # Score starts at 100, subtract penalties
    score = max(0.0, 100.0 - total_penalty)

    return round(score, 1)


def generate_quality_report(
    resources: dict[str, list[dict[str, Any]]], org_name: str
) -> QualityReport:
    """Generate quality report for an organization.

    Args:
        resources: Resources grouped by type
        org_name: Organization name

    Returns:
        QualityReport with duplicate detection results
    """
    duplicates = detect_duplicates(resources, org_name)
    quality_score = calculate_quality_score(duplicates)

    return QualityReport(
        org_name=org_name,
        duplicate_count=len(duplicates),
        duplicates=duplicates,
        quality_score=quality_score,
    )
