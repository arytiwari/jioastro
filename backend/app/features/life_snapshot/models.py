"""
Database models for Life Snapshot feature.
"""

from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.database import Base


class LifeSnapshotData(Base):
    """
    Life Snapshot data model.

    Stores generated snapshot data including themes, risks, opportunities,
    and actions. Snapshots are cached to improve performance.

    Table: life_snapshot_data
    """

    __tablename__ = "life_snapshot_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=False, index=True)

    # Snapshot data (themes, risks, opportunities, actions)
    snapshot_data = Column(JSON, nullable=False)

    # Transit data used for calculation
    transits_data = Column(JSON, nullable=True)

    # AI-generated insights
    insights = Column(JSON, nullable=False)

    # Metadata
    generated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    cache_key = Column(String(255), unique=True, nullable=True, index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<LifeSnapshotData(id={self.id}, user_id={self.user_id}, profile_id={self.profile_id})>"

    def is_expired(self) -> bool:
        """Check if snapshot has expired."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) > self.expires_at


# Create indexes for efficient queries
Index('idx_life_snapshot_user_id', LifeSnapshotData.user_id)
Index('idx_life_snapshot_profile_id', LifeSnapshotData.profile_id)
Index('idx_life_snapshot_cache_key', LifeSnapshotData.cache_key)
Index('idx_life_snapshot_generated_at', LifeSnapshotData.generated_at)
Index('idx_life_snapshot_expires_at', LifeSnapshotData.expires_at)
