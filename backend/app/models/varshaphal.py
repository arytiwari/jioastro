"""
Database models for Varshaphal (Annual Predictions) data.
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.db.database import Base


class VarshapalData(Base):
    """
    Stores Varshaphal (Annual Predictions) calculations.

    Each record represents one year's solar return chart and predictions
    for a specific profile. Cached for performance.
    """

    __tablename__ = "varshaphal_data"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Foreign keys
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # Supabase Auth user ID
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)

    # Varshaphal metadata
    target_year = Column(Integer, nullable=False, index=True)
    solar_return_time = Column(DateTime(timezone=True), nullable=False)
    natal_sun_longitude = Column(String(50), nullable=False)

    # Solar Return Chart data
    solar_return_chart = Column(JSONB, nullable=False)
    # Stores: {
    #   "varsha_lagna": {...},
    #   "muntha": {...},
    #   "planets": {...},
    #   "houses": {...},
    #   "yogas": [...]
    # }

    # Patyayini Dasha periods
    patyayini_dasha = Column(JSONB, nullable=False)
    # Stores: [
    #   {"planet": "Jupiter", "start_date": "...", "end_date": "...", ...},
    #   ...
    # ]

    # Sahams (Sensitive Points)
    sahams = Column(JSONB, nullable=False)
    # Stores: {
    #   "Punya Saham": {...},
    #   "Vidya Saham": {...},
    #   ...
    # }

    # Annual Interpretation
    annual_interpretation = Column(JSONB, nullable=False)
    # Stores: {
    #   "overall_quality": "Excellent",
    #   "year_summary": "...",
    #   "monthly_predictions": [...],
    #   "best_periods": [...],
    #   "worst_periods": [...],
    #   "key_opportunities": [...],
    #   "key_challenges": [...],
    #   "recommended_remedies": [...],
    #   "important_sahams": [...]
    # }

    # Cache management
    generated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=False)
    cache_key = Column(String(255), unique=True, nullable=False, index=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    profile = relationship("Profile", back_populates="varshaphals")

    # Indexes for performance
    __table_args__ = (
        Index("idx_varshaphal_user_year", "user_id", "target_year"),
        Index("idx_varshaphal_profile_year", "profile_id", "target_year"),
        Index("idx_varshaphal_expires_at", "expires_at"),
    )

    def is_expired(self) -> bool:
        """Check if cache has expired."""
        return datetime.now(timezone.utc) > self.expires_at

    def __repr__(self):
        return f"<VarshapalData(id={self.id}, profile_id={self.profile_id}, year={self.target_year})>"
