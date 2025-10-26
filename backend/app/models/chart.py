"""Birth Chart Model"""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

from app.db.database import Base


class Chart(Base):
    """Cached birth chart calculations"""

    __tablename__ = "charts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=False)
    chart_type = Column(String(10), nullable=False)  # 'D1' or 'D9'
    chart_data = Column(JSONB, nullable=False)  # All planets, houses, aspects
    chart_svg = Column(Text)  # Rendered SVG chart
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('profile_id', 'chart_type', name='uq_profile_chart_type'),
    )

    def __repr__(self):
        return f"<Chart {self.chart_type} for Profile {self.profile_id}>"
