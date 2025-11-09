"""Prashna (Horary Astrology) Model"""

from sqlalchemy import Column, String, Text, DateTime, Float, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.database import Base


class Prashna(Base):
    """Saved Prashna (Horary) questions and analyses"""

    __tablename__ = "prashnas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Question details
    question = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False, index=True)  # career, relationship, health, etc.

    # Query moment (when question was asked)
    query_datetime = Column(DateTime(timezone=True), nullable=False)

    # Location where question was asked
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timezone = Column(String(50), nullable=False)

    # Prashna chart and analysis (stored as JSON)
    prashna_chart = Column(JSON, nullable=False)  # Complete chart data
    analysis = Column(JSON, nullable=False)  # Analysis and answer

    # Optional notes
    notes = Column(Text)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Prashna {self.id} - {self.question_type}>"
