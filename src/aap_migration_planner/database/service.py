"""Database service for managing analysis data cache."""

import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy import create_engine, func, text
from sqlalchemy.orm import Session, sessionmaker

from aap_migration_planner.database.models import (
    AnalysisJob,
    Base,
    Dependency,
    Organization,
    Resource,
)
from aap_migration_planner.utils.logging import get_logger

logger = get_logger(__name__)


class DatabaseService:
    """Service for managing SQLite database operations."""

    def __init__(self, db_path: str = "data/aap_analysis.db"):
        """Initialize database service.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path

        # Create data directory if it doesn't exist
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        # Create engine with SQLite optimizations
        self.engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
            echo=False,
        )

        # Enable WAL mode for better concurrency
        with self.engine.connect() as conn:
            conn.execute(text("PRAGMA journal_mode=WAL"))
            conn.execute(text("PRAGMA synchronous=NORMAL"))
            conn.execute(text("PRAGMA cache_size=10000"))
            conn.execute(text("PRAGMA temp_store=MEMORY"))
            conn.commit()

        # Create tables
        Base.metadata.create_all(self.engine)

        # Session factory
        self.SessionLocal = sessionmaker(bind=self.engine)

        logger.info("database_initialized", db_path=db_path)

    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()

    def create_analysis_job(self, job_type: str = "full", total_orgs: int = 0) -> int:
        """Create a new analysis job.

        Args:
            job_type: Type of analysis (full, incremental, single_org)
            total_orgs: Total organizations to analyze

        Returns:
            Job ID
        """
        with self.get_session() as session:
            job = AnalysisJob(
                status="running",
                job_type=job_type,
                total_orgs=total_orgs,
                processed_orgs=0,
            )
            session.add(job)
            session.commit()
            return job.id

    def update_job_progress(
        self,
        job_id: int,
        processed_orgs: int | None = None,
        total_resources: int | None = None,
        total_dependencies: int | None = None,
    ):
        """Update job progress."""
        with self.get_session() as session:
            job = session.query(AnalysisJob).filter_by(id=job_id).first()
            if job:
                if processed_orgs is not None:
                    job.processed_orgs = processed_orgs
                if total_resources is not None:
                    job.total_resources = total_resources
                if total_dependencies is not None:
                    job.total_dependencies = total_dependencies
                session.commit()

    def complete_job(self, job_id: int, error_message: str | None = None):
        """Mark job as completed or failed."""
        with self.get_session() as session:
            job = session.query(AnalysisJob).filter_by(id=job_id).first()
            if job:
                job.status = "failed" if error_message else "completed"
                job.completed_at = datetime.utcnow()
                if error_message:
                    job.error_message = error_message
                session.commit()

    def upsert_organization(
        self,
        aap_id: int,
        name: str,
        resource_count: int = 0,
        has_dependencies: bool = False,
        can_migrate_standalone: bool = True,
        last_modified_at: datetime | None = None,
    ) -> Organization:
        """Insert or update organization.

        Args:
            aap_id: AAP organization ID
            name: Organization name
            resource_count: Total resource count
            has_dependencies: Whether org has cross-org dependencies
            can_migrate_standalone: Whether can migrate standalone
            last_modified_at: Last modification time from AAP

        Returns:
            Organization model
        """
        with self.get_session() as session:
            org = session.query(Organization).filter_by(aap_id=aap_id).first()

            if org:
                # Update existing
                org.name = name
                org.resource_count = resource_count
                org.has_dependencies = has_dependencies
                org.can_migrate_standalone = can_migrate_standalone
                org.last_analyzed_at = datetime.utcnow()
                if last_modified_at:
                    org.last_modified_at = last_modified_at
            else:
                # Create new
                org = Organization(
                    aap_id=aap_id,
                    name=name,
                    resource_count=resource_count,
                    has_dependencies=has_dependencies,
                    can_migrate_standalone=can_migrate_standalone,
                    last_analyzed_at=datetime.utcnow(),
                    last_modified_at=last_modified_at,
                )
                session.add(org)

            session.commit()
            session.refresh(org)
            return org

    def upsert_resource(
        self,
        org_id: int,
        aap_id: int,
        resource_type: str,
        name: str,
        data: dict,
        description: str | None = None,
        last_modified: datetime | None = None,
    ) -> Resource:
        """Insert or update resource.

        Args:
            org_id: Database organization ID
            aap_id: AAP resource ID
            resource_type: Resource type (e.g., projects, job_templates)
            name: Resource name
            data: Full resource JSON
            description: Resource description
            last_modified: Last modification time from AAP

        Returns:
            Resource model
        """
        with self.get_session() as session:
            # Calculate checksum
            checksum = hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()

            resource = (
                session.query(Resource)
                .filter_by(organization_id=org_id, resource_type=resource_type, aap_id=aap_id)
                .first()
            )

            if resource:
                # Update existing
                resource.name = name
                resource.description = description
                resource.data = data
                resource.checksum = checksum
                if last_modified:
                    resource.last_modified = last_modified
            else:
                # Create new
                resource = Resource(
                    organization_id=org_id,
                    aap_id=aap_id,
                    resource_type=resource_type,
                    name=name,
                    description=description,
                    data=data,
                    checksum=checksum,
                    last_modified=last_modified,
                )
                session.add(resource)

            session.commit()
            session.refresh(resource)
            return resource

    def bulk_upsert_resources(
        self,
        org_id: int,
        resource_type: str,
        resources: list[dict],
    ):
        """Bulk insert/update resources for performance.

        Args:
            org_id: Database organization ID
            resource_type: Resource type
            resources: List of resource dicts from AAP
        """
        with self.get_session() as session:
            for res_data in resources:
                checksum = hashlib.md5(json.dumps(res_data, sort_keys=True).encode()).hexdigest()

                resource = (
                    session.query(Resource)
                    .filter_by(
                        organization_id=org_id,
                        resource_type=resource_type,
                        aap_id=res_data.get("id"),
                    )
                    .first()
                )

                if resource:
                    # Update
                    resource.name = res_data.get("name", "")
                    resource.description = res_data.get("description")
                    resource.data = res_data
                    resource.checksum = checksum
                    resource.last_modified = res_data.get("modified")
                else:
                    # Insert
                    resource = Resource(
                        organization_id=org_id,
                        aap_id=res_data.get("id"),
                        resource_type=resource_type,
                        name=res_data.get("name", ""),
                        description=res_data.get("description"),
                        data=res_data,
                        checksum=checksum,
                        last_modified=res_data.get("modified"),
                    )
                    session.add(resource)

            session.commit()

    def get_organization(self, name: str) -> Organization | None:
        """Get organization by name."""
        with self.get_session() as session:
            return session.query(Organization).filter_by(name=name).first()

    def get_organization_by_aap_id(self, aap_id: int) -> Organization | None:
        """Get organization by AAP ID."""
        with self.get_session() as session:
            return session.query(Organization).filter_by(aap_id=aap_id).first()

    def get_all_organizations(self) -> list[Organization]:
        """Get all organizations."""
        with self.get_session() as session:
            return session.query(Organization).all()

    def get_resources_by_org(self, org_id: int, resource_type: str | None = None) -> list[Resource]:
        """Get all resources for an organization.

        Args:
            org_id: Database organization ID
            resource_type: Optional filter by resource type

        Returns:
            List of resources
        """
        with self.get_session() as session:
            query = session.query(Resource).filter_by(organization_id=org_id)
            if resource_type:
                query = query.filter_by(resource_type=resource_type)
            return query.all()

    def needs_analysis(self, org_name: str, max_age_hours: int = 24) -> bool:
        """Check if organization needs re-analysis.

        Args:
            org_name: Organization name
            max_age_hours: Maximum age of cached data in hours

        Returns:
            True if needs analysis, False if cache is fresh
        """
        with self.get_session() as session:
            org = session.query(Organization).filter_by(name=org_name).first()

            if not org:
                return True  # Never analyzed

            if not org.last_analyzed_at:
                return True  # No analysis timestamp

            # Check if cache is stale
            age = datetime.utcnow() - org.last_analyzed_at
            if age > timedelta(hours=max_age_hours):
                logger.info(
                    "cache_stale",
                    org_name=org_name,
                    age_hours=age.total_seconds() / 3600,
                    max_age_hours=max_age_hours,
                )
                return True

            return False

    def get_cached_analysis(self, org_name: str) -> dict | None:
        """Get cached analysis results for an organization.

        Args:
            org_name: Organization name

        Returns:
            Dict with organization data and resources, or None if not cached
        """
        with self.get_session() as session:
            org = session.query(Organization).filter_by(name=org_name).first()

            if not org:
                return None

            # Get all resources grouped by type
            resources = session.query(Resource).filter_by(organization_id=org.id).all()

            resources_by_type = {}
            for resource in resources:
                if resource.resource_type not in resources_by_type:
                    resources_by_type[resource.resource_type] = []
                resources_by_type[resource.resource_type].append(resource.data)

            return {
                "org_name": org.name,
                "org_id": org.aap_id,
                "resource_count": org.resource_count,
                "resources": resources_by_type,
                "last_analyzed_at": org.last_analyzed_at.isoformat()
                if org.last_analyzed_at
                else None,
                "cached": True,
            }

    def clear_organization(self, org_name: str):
        """Clear all cached data for an organization."""
        with self.get_session() as session:
            org = session.query(Organization).filter_by(name=org_name).first()
            if org:
                session.delete(org)
                session.commit()
                logger.info("cache_cleared", org_name=org_name)

    def get_stats(self) -> dict:
        """Get database statistics."""
        with self.get_session() as session:
            stats = {
                "total_orgs": session.query(func.count(Organization.id)).scalar(),
                "total_resources": session.query(func.count(Resource.id)).scalar(),
                "total_dependencies": session.query(func.count(Dependency.id)).scalar(),
                "total_jobs": session.query(func.count(AnalysisJob.id)).scalar(),
                "last_analysis": session.query(func.max(Organization.last_analyzed_at)).scalar(),
            }
            return stats
