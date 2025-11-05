"""City Model for Indian Cities"""

from sqlalchemy import Column, String, Numeric, Integer
from app.db.database import Base


class City(Base):
    """Indian cities with coordinates for astrology calculations"""

    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    state = Column(String(100), nullable=False, index=True)
    latitude = Column(Numeric(9, 6), nullable=False)
    longitude = Column(Numeric(9, 6), nullable=False)
    display_name = Column(String(200), nullable=False)  # "City, State" format

    def __repr__(self):
        return f"<City {self.display_name} ({self.latitude}, {self.longitude})>"
