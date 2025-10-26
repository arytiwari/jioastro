"""User Feedback Model"""

from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.database import Base


class Feedback(Base):
    """User feedback on AI interpretations"""

    __tablename__ = "feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    response_id = Column(UUID(as_uuid=True), ForeignKey("responses.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    rating = Column(Integer, CheckConstraint('rating >= 1 AND rating <= 5'), nullable=False)
    comment = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Feedback {self.rating}⭐ for Response {self.response_id}>"
