"""Birth Profile Model"""

from sqlalchemy import Column, String, Date, Time, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.database import Base


class Profile(Base):
    """Birth profile for astrological calculations"""

    __tablename__ = "profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    birth_date = Column(Date, nullable=False)
    birth_time = Column(Time, nullable=False)
    birth_lat = Column(Numeric(9, 6), nullable=False)
    birth_lon = Column(Numeric(9, 6), nullable=False)
    birth_city = Column(String(100))
    birth_timezone = Column(String(50))
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Profile {self.name} ({self.id})>"
