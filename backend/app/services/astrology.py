"""
Vedic Astrology Calculation Service
Using accurate Swiss Ephemeris implementation for professional-grade Vedic calculations
"""

from typing import Dict, List, Any
from datetime import datetime, date, time
from app.services.vedic_astrology_accurate import accurate_vedic_astrology


class VedicAstrologyService:
    """Service for Vedic astrology calculations - delegates to accurate Swiss Ephemeris implementation"""

    def __init__(self):
        """Initialize astrology service"""
        pass

    def calculate_birth_chart(
        self,
        name: str,
        birth_date: date,
        birth_time: time,
        latitude: float,
        longitude: float,
        timezone_str: str = "UTC",
        city: str = "Unknown"
    ) -> Dict[str, Any]:
        """
        Calculate Vedic birth chart (D1 - Rashi chart) using accurate Swiss Ephemeris

        Args:
            name: Person's name
            birth_date: Date of birth
            birth_time: Time of birth
            latitude: Birth location latitude
            longitude: Birth location longitude
            timezone_str: Timezone string (e.g., 'Asia/Kolkata')
            city: Birth city name

        Returns:
            Complete birth chart data including planets, houses, yogas, and dashas
        """

        # Delegate to accurate Swiss Ephemeris implementation
        return accurate_vedic_astrology.calculate_birth_chart(
            name=name,
            birth_date=birth_date,
            birth_time=birth_time,
            latitude=latitude,
            longitude=longitude,
            timezone_str=timezone_str,
            city=city
        )

    def calculate_navamsa_chart(
        self,
        name: str,
        birth_date: date,
        birth_time: time,
        latitude: float,
        longitude: float,
        timezone_str: str = "UTC",
        city: str = "Unknown"
    ) -> Dict[str, Any]:
        """
        Calculate Navamsa chart (D9) using accurate Swiss Ephemeris
        Navamsa is the 9th divisional chart showing marriage, dharma, and spiritual potential
        """

        # Delegate to accurate Swiss Ephemeris implementation
        return accurate_vedic_astrology.calculate_navamsa(
            name=name,
            birth_date=birth_date,
            birth_time=birth_time,
            latitude=latitude,
            longitude=longitude,
            timezone_str=timezone_str,
            city=city
        )

    def calculate_moon_chart(
        self,
        name: str,
        birth_date: date,
        birth_time: time,
        latitude: float,
        longitude: float,
        timezone_str: str = "UTC",
        city: str = "Unknown"
    ) -> Dict[str, Any]:
        """
        Calculate Moon chart (Chandra Kundali) using accurate Swiss Ephemeris
        Moon chart shows life from the Moon's perspective - emotions, mind, mother
        """

        # Delegate to accurate Swiss Ephemeris implementation
        return accurate_vedic_astrology.calculate_moon_chart(
            name=name,
            birth_date=birth_date,
            birth_time=birth_time,
            latitude=latitude,
            longitude=longitude,
            timezone_str=timezone_str,
            city=city
        )


# Singleton instance
astrology_service = VedicAstrologyService()
