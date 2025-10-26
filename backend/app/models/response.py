"""AI Response Model"""

from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.database import Base


class Response(Base):
    """AI-generated astrological interpretations"""

    __tablename__ = "responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_id = Column(UUID(as_uuid=True), ForeignKey("queries.id"), nullable=False, index=True)
    interpretation = Column(Text, nullable=False)
    ai_model = Column(String(50))
    tokens_used = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Response {self.id} for Query {self.query_id}>"
