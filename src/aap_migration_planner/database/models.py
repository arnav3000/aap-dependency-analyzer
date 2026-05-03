"""SQLAlchemy database models for caching analysis data."""

from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Organization(Base):
    """Organization metadata and analysis status."""

    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True)
    aap_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    resource_count = Column(Integer, default=0)
    has_dependencies = Column(Boolean, default=False)
    can_migrate_standalone = Column(Boolean, default=True)
    last_analyzed_at = Column(DateTime, nullable=True, index=True)
    last_modified_at = Column(DateTime, nullable=True)  # From AAP
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    resources = relationship(
        "Resource", back_populates="organization", cascade="all, delete-orphan"
    )
    source_dependencies = relationship(
        "Dependency",
        foreign_keys="[Dependency.source_org_id]",
        back_populates="source_org",
        cascade="all, delete-orphan",
    )
    target_dependencies = relationship(
        "Dependency", foreign_keys="[Dependency.target_org_id]", back_populates="target_org"
    )


class Resource(Base):
    """Individual resources cached from AAP."""

    __tablename__ = "resources"

    id = Column(Integer, primary_key=True)
    aap_id = Column(Integer, nullable=False)
    resource_type = Column(String(50), nullable=False, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    name = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    data = Column(JSON, nullable=False)  # Full resource JSON from AAP
    checksum = Column(String(64), nullable=True)  # MD5 hash to detect changes
    last_modified = Column(DateTime, nullable=True)  # From AAP modified field
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="resources")

    # Composite indexes for common queries
    __table_args__ = (
        Index("idx_org_type", "organization_id", "resource_type"),
        Index("idx_type_aap_id", "resource_type", "aap_id"),
    )


class Dependency(Base):
    """Cross-organization dependency relationships."""

    __tablename__ = "dependencies"

    id = Column(Integer, primary_key=True)
    source_org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    source_resource_id = Column(Integer, ForeignKey("resources.id"), nullable=True)
    target_org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    target_resource_id = Column(Integer, ForeignKey("resources.id"), nullable=True)
    dependency_type = Column(String(100), nullable=False)  # e.g., "project", "inventory"
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    source_org = relationship(
        "Organization",
        foreign_keys="[Dependency.source_org_id]",
        back_populates="source_dependencies",
    )
    target_org = relationship(
        "Organization",
        foreign_keys="[Dependency.target_org_id]",
        back_populates="target_dependencies",
    )

    __table_args__ = (Index("idx_source_target", "source_org_id", "target_org_id"),)


class AnalysisJob(Base):
    """Track analysis job execution history."""

    __tablename__ = "analysis_jobs"

    id = Column(Integer, primary_key=True)
    status = Column(String(20), nullable=False, index=True)  # queued, running, completed, failed
    job_type = Column(String(50), default="full")  # full, incremental, single_org
    total_orgs = Column(Integer, default=0)
    processed_orgs = Column(Integer, default=0)
    total_resources = Column(Integer, default=0)
    total_dependencies = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    job_metadata = Column(JSON, nullable=True)  # Additional job info
    created_at = Column(DateTime, default=datetime.utcnow)


class GlobalResource(Base):
    """Global resources not tied to any organization."""

    __tablename__ = "global_resources"

    id = Column(Integer, primary_key=True)
    aap_id = Column(Integer, nullable=False)
    resource_type = Column(String(50), nullable=False, index=True)
    name = Column(String(500), nullable=False)
    data = Column(JSON, nullable=False)
    last_modified = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (Index("idx_type_aap_id_global", "resource_type", "aap_id"),)
