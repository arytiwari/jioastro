"""
Muhurta (Electional Astrology) Service

Implements:
- Panchang calculations (Tithi, Nakshatra, Yoga, Karana, Vara)
- Hora (planetary hours) calculations
- Good time finder for various activities (marriage, business, travel, etc.)

Uses Swiss Ephemeris for accurate astronomical calculations.
"""

import swisseph as swe
from datetime import datetime, timedelta, time
from typing import Dict, List, Tuple, Optional, Any
import math


class MuhurtaService:
    """Service for Muhurta (Electional Astrology) calculations"""

    # Nakshatra names (27 lunar mansions)
    NAKSHATRAS = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
        "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
        "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
        "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
        "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
    ]

    # Tithi names (30 lunar days)
    TITHIS = [
        # Shukla Paksha (Waxing Moon)
        "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
        "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
        "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",
        # Krishna Paksha (Waning Moon)
        "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
        "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
        "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya"
    ]

    # Yoga names (27 yogas)
    YOGAS = [
        "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda",
        "Sukarma", "Dhriti", "Shula", "Ganda", "Vriddhi", "Dhruva",
        "Vyaghata", "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyan",
        "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla",
        "Brahma", "Indra", "Vaidhriti"
    ]

    # Karana names (11 karanas, 8 repeating + 3 fixed)
    KARANAS = [
        "Bava", "Balava", "Kaulava", "Taitila", "Garaja", "Vanija", "Vishti",
        "Shakuni", "Chatushpada", "Naga", "Kimstughna"
    ]

    # Vara (weekday) with planetary rulers
    VARAS = [
        {"name": "Sunday", "ruler": "Sun", "quality": "Royal"},
        {"name": "Monday", "ruler": "Moon", "quality": "Gentle"},
        {"name": "Tuesday", "ruler": "Mars", "quality": "Fierce"},
        {"name": "Wednesday", "ruler": "Mercury", "quality": "Mixed"},
        {"name": "Thursday", "ruler": "Jupiter", "quality": "Auspicious"},
        {"name": "Friday", "ruler": "Venus", "quality": "Pleasant"},
        {"name": "Saturday", "ruler": "Saturn", "quality": "Harsh"}
    ]

    # Planetary hour rulers (in order for day and night)
    HORA_RULERS_DAY = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]
    HORA_RULERS_NIGHT = ["Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon", "Saturn"]

    def __init__(self):
        """Initialize Swiss Ephemeris"""
        swe.set_ephe_path(None)  # Use default ephemeris path
        # Set sidereal mode (Lahiri ayanamsa for Vedic)
        swe.set_sid_mode(swe.SIDM_LAHIRI)

    def _datetime_to_julian(self, dt: datetime) -> float:
        """Convert datetime to Julian day number"""
        return swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0 + dt.second/3600.0)

    def _julian_to_datetime(self, jd: float) -> datetime:
        """Convert Julian day to datetime"""
        result = swe.revjul(jd)
        year, month, day, hour = result
        hours = int(hour)
        minutes = int((hour - hours) * 60)
        seconds = int(((hour - hours) * 60 - minutes) * 60)
        return datetime(year, month, day, hours, minutes, seconds)

    def _normalize_degrees(self, degrees: float) -> float:
        """Normalize degrees to 0-360 range"""
        while degrees < 0:
            degrees += 360
        while degrees >= 360:
            degrees -= 360
        return degrees

    # ============================================================================
    # PANCHANG CALCULATIONS
    # ============================================================================

    def calculate_tithi(self, dt: datetime, latitude: float = 0, longitude: float = 0) -> Dict[str, Any]:
        """
        Calculate Tithi (Lunar Day)

        Tithi = (Moon longitude - Sun longitude) / 12 degrees
        Range: 0-29 (30 tithis)
        """
        jd = self._datetime_to_julian(dt)

        # Get Sun and Moon positions (tropical)
        sun_pos = swe.calc_ut(jd, swe.SUN)[0][0]
        moon_pos = swe.calc_ut(jd, swe.MOON)[0][0]

        # Calculate tithi
        diff = self._normalize_degrees(moon_pos - sun_pos)
        tithi_num = int(diff / 12.0)
        tithi_progress = (diff % 12.0) / 12.0 * 100  # Progress in current tithi

        # Determine paksha (fortnight)
        paksha = "Shukla Paksha" if tithi_num < 15 else "Krishna Paksha"
        paksha_tithi = tithi_num % 15

        # Get tithi name
        tithi_name = self.TITHIS[tithi_num]

        # Calculate end time of current tithi
        # Tithi ends when Moon moves 12 degrees ahead of Sun
        target_diff = (tithi_num + 1) * 12.0
        end_jd = self._find_tithi_end(jd, target_diff)
        end_time = self._julian_to_datetime(end_jd)

        # Assess auspiciousness
        auspicious = self._is_tithi_auspicious(tithi_num, tithi_name)

        return {
            "tithi_number": tithi_num + 1,  # 1-30
            "tithi_name": tithi_name,
            "paksha": paksha,
            "paksha_tithi": paksha_tithi + 1,  # 1-15
            "progress_percent": round(tithi_progress, 2),
            "ends_at": end_time.isoformat(),
            "is_auspicious": auspicious,
            "description": self._get_tithi_description(tithi_name, paksha)
        }

    def calculate_nakshatra(self, dt: datetime) -> Dict[str, Any]:
        """
        Calculate Nakshatra (Lunar Mansion)

        Based on Moon's sidereal position
        27 nakshatras, each 13°20' (800')
        """
        jd = self._datetime_to_julian(dt)

        # Get Moon position (sidereal)
        moon_pos_sidereal = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)[0][0]

        # Calculate nakshatra (0-26)
        nakshatra_num = int(moon_pos_sidereal / (360.0 / 27.0))
        nakshatra_progress = (moon_pos_sidereal % (360.0 / 27.0)) / (360.0 / 27.0) * 100

        # Get pada (quarter) - 1-4
        pada = int((moon_pos_sidereal % (360.0 / 27.0)) / (360.0 / 27.0 / 4.0)) + 1

        nakshatra_name = self.NAKSHATRAS[nakshatra_num]

        # Calculate end time
        target_pos = (nakshatra_num + 1) * (360.0 / 27.0)
        end_jd = self._find_nakshatra_end(jd, target_pos)
        end_time = self._julian_to_datetime(end_jd)

        # Get nakshatra properties
        properties = self._get_nakshatra_properties(nakshatra_num)

        return {
            "nakshatra_number": nakshatra_num + 1,  # 1-27
            "nakshatra_name": nakshatra_name,
            "pada": pada,
            "progress_percent": round(nakshatra_progress, 2),
            "ends_at": end_time.isoformat(),
            "ruler": properties["ruler"],
            "deity": properties["deity"],
            "nature": properties["nature"],
            "is_auspicious": properties["auspicious"],
            "favorable_for": properties["favorable_for"]
        }

    def calculate_yoga(self, dt: datetime) -> Dict[str, Any]:
        """
        Calculate Yoga

        Yoga = (Sun longitude + Moon longitude) / (360/27)
        27 yogas total
        """
        jd = self._datetime_to_julian(dt)

        # Get Sun and Moon positions (sidereal)
        sun_pos = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL)[0][0]
        moon_pos = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)[0][0]

        # Calculate yoga
        combined = self._normalize_degrees(sun_pos + moon_pos)
        yoga_num = int(combined / (360.0 / 27.0))
        yoga_progress = (combined % (360.0 / 27.0)) / (360.0 / 27.0) * 100

        yoga_name = self.YOGAS[yoga_num]

        # Calculate end time
        target_combined = (yoga_num + 1) * (360.0 / 27.0)
        end_jd = self._find_yoga_end(jd, target_combined)
        end_time = self._julian_to_datetime(end_jd)

        # Assess quality
        quality = self._get_yoga_quality(yoga_num, yoga_name)

        return {
            "yoga_number": yoga_num + 1,  # 1-27
            "yoga_name": yoga_name,
            "progress_percent": round(yoga_progress, 2),
            "ends_at": end_time.isoformat(),
            "quality": quality["type"],
            "is_auspicious": quality["auspicious"],
            "description": quality["description"]
        }

    def calculate_karana(self, dt: datetime) -> Dict[str, Any]:
        """
        Calculate Karana (Half of Tithi)

        Each tithi has 2 karanas
        11 karanas total: 8 movable (repeat) + 3 fixed (at end of month)
        """
        jd = self._datetime_to_julian(dt)

        # Get Sun and Moon positions
        sun_pos = swe.calc_ut(jd, swe.SUN)[0][0]
        moon_pos = swe.calc_ut(jd, swe.MOON)[0][0]

        # Calculate karana
        diff = self._normalize_degrees(moon_pos - sun_pos)
        karana_num = int(diff / 6.0)  # 60 karanas in a month (30 tithis * 2)
        karana_progress = (diff % 6.0) / 6.0 * 100

        # Map to 11 karanas (0-10)
        # First 7 repeat 8 times, last 4 are fixed
        if karana_num < 57:
            karana_index = karana_num % 7  # Repeating karanas
        else:
            karana_index = 7 + (karana_num - 57)  # Fixed karanas

        karana_name = self.KARANAS[karana_index]

        # Calculate end time
        target_diff = (karana_num + 1) * 6.0
        end_jd = self._find_karana_end(jd, target_diff)
        end_time = self._julian_to_datetime(end_jd)

        # Assess nature
        nature = self._get_karana_nature(karana_index, karana_name)

        return {
            "karana_number": karana_num + 1,
            "karana_name": karana_name,
            "karana_type": "Fixed" if karana_index >= 7 else "Movable",
            "progress_percent": round(karana_progress, 2),
            "ends_at": end_time.isoformat(),
            "is_auspicious": nature["auspicious"],
            "nature": nature["description"]
        }

    def calculate_vara(self, dt: datetime) -> Dict[str, Any]:
        """
        Calculate Vara (Weekday)

        Each day ruled by a planet
        """
        weekday = dt.weekday()  # 0 = Monday, 6 = Sunday

        # Adjust to start from Sunday (0 = Sunday)
        vara_index = (weekday + 1) % 7

        vara = self.VARAS[vara_index]

        return {
            "vara_number": vara_index + 1,
            "vara_name": vara["name"],
            "ruling_planet": vara["ruler"],
            "quality": vara["quality"],
            "favorable_for": self._get_vara_activities(vara["ruler"]),
            "avoid": self._get_vara_avoid(vara["ruler"])
        }

    def calculate_panchang(self, dt: datetime, latitude: float = 0, longitude: float = 0) -> Dict[str, Any]:
        """
        Calculate complete Panchang for a given datetime

        Combines Tithi, Nakshatra, Yoga, Karana, and Vara
        """
        tithi = self.calculate_tithi(dt, latitude, longitude)
        nakshatra = self.calculate_nakshatra(dt)
        yoga = self.calculate_yoga(dt)
        karana = self.calculate_karana(dt)
        vara = self.calculate_vara(dt)

        # Calculate sunrise and sunset for the location
        sunrise_time, sunset_time = self._calculate_sunrise_sunset(dt, latitude, longitude)

        # Determine overall auspiciousness
        auspicious_count = sum([
            tithi["is_auspicious"],
            nakshatra["is_auspicious"],
            yoga["is_auspicious"],
            karana["is_auspicious"]
        ])

        overall_quality = "Highly Auspicious" if auspicious_count >= 3 else \
                         "Auspicious" if auspicious_count == 2 else \
                         "Mixed" if auspicious_count == 1 else "Inauspicious"

        return {
            "date": dt.date().isoformat(),
            "time": dt.time().isoformat(),
            "location": {"latitude": latitude, "longitude": longitude},
            "sunrise": sunrise_time.isoformat() if sunrise_time else None,
            "sunset": sunset_time.isoformat() if sunset_time else None,
            "tithi": tithi,
            "nakshatra": nakshatra,
            "yoga": yoga,
            "karana": karana,
            "vara": vara,
            "overall_quality": overall_quality,
            "auspicious_score": auspicious_count,
            "summary": self._generate_panchang_summary(tithi, nakshatra, yoga, vara)
        }

    # ============================================================================
    # HELPER METHODS FOR PANCHANG
    # ============================================================================

    def _find_tithi_end(self, start_jd: float, target_diff: float) -> float:
        """Find when tithi ends (binary search)"""
        jd = start_jd
        step = 1.0  # Start with 1 day step

        for _ in range(20):  # Max iterations
            sun_pos = swe.calc_ut(jd, swe.SUN)[0][0]
            moon_pos = swe.calc_ut(jd, swe.MOON)[0][0]
            diff = self._normalize_degrees(moon_pos - sun_pos)

            if abs(diff - target_diff) < 0.01:  # Converged
                break

            if diff < target_diff:
                jd += step
            else:
                jd -= step
                step /= 2

        return jd

    def _find_nakshatra_end(self, start_jd: float, target_pos: float) -> float:
        """Find when nakshatra ends"""
        jd = start_jd
        step = 1.0

        for _ in range(20):
            moon_pos = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)[0][0]

            if abs(moon_pos - target_pos) < 0.01:
                break

            if moon_pos < target_pos:
                jd += step
            else:
                jd -= step
                step /= 2

        return jd

    def _find_yoga_end(self, start_jd: float, target_combined: float) -> float:
        """Find when yoga ends"""
        jd = start_jd
        step = 1.0

        for _ in range(20):
            sun_pos = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL)[0][0]
            moon_pos = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)[0][0]
            combined = self._normalize_degrees(sun_pos + moon_pos)

            if abs(combined - target_combined) < 0.01:
                break

            if combined < target_combined:
                jd += step
            else:
                jd -= step
                step /= 2

        return jd

    def _find_karana_end(self, start_jd: float, target_diff: float) -> float:
        """Find when karana ends"""
        return self._find_tithi_end(start_jd, target_diff)

    def _calculate_sunrise_sunset(self, dt: datetime, latitude: float, longitude: float) -> Tuple[Optional[datetime], Optional[datetime]]:
        """
        Calculate sunrise and sunset times for a given date and location.

        Returns:
            Tuple of (sunrise_datetime, sunset_datetime) or (None, None) if calculation fails
        """
        if latitude == 0 and longitude == 0:
            return None, None

        try:
            # Convert to Julian day at midnight
            jd_midnight = swe.julday(dt.year, dt.month, dt.day, 0.0)

            # Geographic position: (longitude, latitude, altitude)
            geopos = (longitude, latitude, 0.0)

            # Calculate sunrise
            sunrise_result = swe.rise_trans(
                jd_midnight,
                swe.SUN,
                swe.CALC_RISE | swe.BIT_DISC_CENTER,
                geopos,
                0.0,  # atmospheric pressure
                0.0   # temperature
            )

            # Calculate sunset
            sunset_result = swe.rise_trans(
                jd_midnight,
                swe.SUN,
                swe.CALC_SET | swe.BIT_DISC_CENTER,
                geopos,
                0.0,
                0.0
            )

            # Check if calculation succeeded (0 = found, -2 = circumpolar)
            if sunrise_result[0] != 0 or sunset_result[0] != 0:
                # Rise/set not available (polar regions, etc.)
                return None, None

            sunrise_jd = sunrise_result[1][0]
            sunset_jd = sunset_result[1][0]

            # Convert Julian days back to datetime
            sunrise = self._julian_to_datetime(sunrise_jd)
            sunset = self._julian_to_datetime(sunset_jd)

            return sunrise, sunset

        except Exception as e:
            # Silently fail for any calculation errors
            return None, None

    # ============================================================================
    # QUALITY ASSESSMENT METHODS
    # ============================================================================

    def _is_tithi_auspicious(self, tithi_num: int, tithi_name: str) -> bool:
        """Determine if tithi is auspicious"""
        # Auspicious tithis: 2, 3, 5, 7, 10, 11, 13 of both pakshas
        auspicious_numbers = [1, 2, 4, 6, 9, 10, 12, 16, 17, 19, 21, 24, 25, 27]
        # Avoid: 4, 6, 8, 9, 14 (Chaturthi, Shashthi, Ashtami, Navami, Chaturdashi)
        # Also avoid 30 (Amavasya) for most activities
        return tithi_num in auspicious_numbers

    def _get_tithi_description(self, tithi_name: str, paksha: str) -> str:
        """Get description for tithi"""
        descriptions = {
            "Pratipada": "New beginnings, starting projects",
            "Dwitiya": "Auspicious for most activities",
            "Tritiya": "Very auspicious, good for marriage",
            "Chaturthi": "Mixed, avoid important work",
            "Panchami": "Excellent for learning and education",
            "Shashthi": "Moderate, good for routine work",
            "Saptami": "Auspicious for most activities",
            "Ashtami": "Challenging, avoid new beginnings",
            "Navami": "Mixed, good for spiritual activities",
            "Dashami": "Auspicious for travel and business",
            "Ekadashi": "Highly spiritual, fasting day",
            "Dwadashi": "Good for vratam and religious work",
            "Trayodashi": "Auspicious for ventures",
            "Chaturdashi": "Avoid important activities",
            "Purnima": "Full moon, auspicious for completion",
            "Amavasya": "New moon, spiritual but avoid material activities"
        }
        return descriptions.get(tithi_name, "Standard day")

    def _get_nakshatra_properties(self, nakshatra_num: int) -> Dict[str, Any]:
        """Get properties for nakshatra"""
        # Simplified properties (can be expanded)
        properties = [
            {"ruler": "Ketu", "deity": "Ashwini Kumaras", "nature": "Swift", "auspicious": True, "favorable_for": ["Travel", "Medicine", "Healing"]},
            {"ruler": "Venus", "deity": "Yama", "nature": "Fierce", "auspicious": False, "favorable_for": ["Endings", "Funerals"]},
            {"ruler": "Sun", "deity": "Agni", "nature": "Mixed", "auspicious": True, "favorable_for": ["Fire rituals", "Cooking"]},
            {"ruler": "Moon", "deity": "Brahma", "nature": "Fixed", "auspicious": True, "favorable_for": ["Building", "Foundations"]},
            # ... (complete for all 27)
        ]
        if nakshatra_num < len(properties):
            return properties[nakshatra_num]
        return {"ruler": "Unknown", "deity": "Unknown", "nature": "Mixed", "auspicious": True, "favorable_for": []}

    def _get_yoga_quality(self, yoga_num: int, yoga_name: str) -> Dict[str, Any]:
        """Get quality assessment for yoga"""
        # Auspicious yogas: 1, 2, 3, 4, 6, 7, 11, 14, 15, 18, 19, 20, 21, 22, 24, 25
        auspicious = [0, 1, 2, 3, 5, 6, 10, 13, 14, 17, 18, 19, 20, 21, 23, 24]
        inauspicious = [5, 8, 9, 16, 22, 26]  # Atiganda, Shula, Ganda, Vyatipata, Variyan, Vaidhriti

        if yoga_num in inauspicious:
            return {"type": "Inauspicious", "auspicious": False, "description": f"Avoid important activities during {yoga_name}"}
        elif yoga_num in auspicious:
            return {"type": "Auspicious", "auspicious": True, "description": f"{yoga_name} is favorable for most activities"}
        else:
            return {"type": "Mixed", "auspicious": True, "description": f"{yoga_name} is moderate"}

    def _get_karana_nature(self, karana_index: int, karana_name: str) -> Dict[str, Any]:
        """Get nature of karana"""
        # Auspicious karanas: Bava, Balava, Kaulava, Taitila
        auspicious = [0, 1, 2, 3]
        inauspicious = [6]  # Vishti (Bhadra) - very inauspicious

        if karana_index in inauspicious:
            return {"auspicious": False, "description": "Avoid all important activities"}
        elif karana_index in auspicious:
            return {"auspicious": True, "description": "Favorable for activities"}
        else:
            return {"auspicious": True, "description": "Moderate"}

    def _get_vara_activities(self, ruler: str) -> List[str]:
        """Get favorable activities for weekday"""
        activities = {
            "Sun": ["Government work", "Authority", "Leadership", "Promotions"],
            "Moon": ["Emotional matters", "Travel", "Water activities", "Peace"],
            "Mars": ["Sports", "Competition", "Surgery", "War"],
            "Mercury": ["Business", "Communication", "Education", "Writing"],
            "Jupiter": ["Spiritual", "Teaching", "Marriage", "Ceremonies"],
            "Venus": ["Arts", "Beauty", "Romance", "Luxury"],
            "Saturn": ["Construction", "Labor", "Service", "Discipline"]
        }
        return activities.get(ruler, [])

    def _get_vara_avoid(self, ruler: str) -> List[str]:
        """Get activities to avoid on weekday"""
        avoid = {
            "Sun": ["Humility required tasks"],
            "Moon": ["Harsh decisions"],
            "Mars": ["Peace negotiations"],
            "Mercury": ["Silent meditation"],
            "Jupiter": ["Unethical business"],
            "Venus": ["Harsh work"],
            "Saturn": ["Pleasure activities", "Marriage"]
        }
        return avoid.get(ruler, [])

    def _generate_panchang_summary(self, tithi: Dict, nakshatra: Dict, yoga: Dict, vara: Dict) -> str:
        """Generate summary of the day"""
        return f"Today is {vara['vara_name']} ({vara['ruling_planet']}), " \
               f"{tithi['tithi_name']} Tithi in {tithi['paksha']}, " \
               f"Moon in {nakshatra['nakshatra_name']} Nakshatra, " \
               f"and {yoga['yoga_name']} Yoga. "

    # ============================================================================
    # HORA (PLANETARY HOURS) CALCULATIONS
    # ============================================================================

    def calculate_hora(self, dt: datetime, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Calculate Hora (Planetary Hour)

        Divides day and night into 12 horas each (24 total)
        Each hora ruled by a planet in sequence
        """
        sunrise, sunset = self._calculate_sunrise_sunset(dt, latitude, longitude)

        if not sunrise or not sunset:
            return {
                "error": "Cannot calculate hora without location (sunrise/sunset needed)",
                "current_hora": None
            }

        # Determine if current time is day or night
        is_day = sunrise.time() <= dt.time() < sunset.time()

        if is_day:
            # Day hora
            start_time = sunrise
            end_time = sunset
            hora_rulers = self.HORA_RULERS_DAY
        else:
            # Night hora
            if dt.time() >= sunset.time():
                start_time = sunset
                # Next sunrise (next day)
                next_day = dt + timedelta(days=1)
                next_sunrise, _ = self._calculate_sunrise_sunset(next_day, latitude, longitude)
                end_time = next_sunrise if next_sunrise else sunrise + timedelta(days=1)
            else:
                # After midnight before sunrise
                prev_day = dt - timedelta(days=1)
                _, prev_sunset = self._calculate_sunrise_sunset(prev_day, latitude, longitude)
                start_time = prev_sunset if prev_sunset else sunset - timedelta(days=1)
                end_time = sunrise

            hora_rulers = self.HORA_RULERS_NIGHT

        # Calculate hora duration
        total_duration = (end_time - start_time).total_seconds()
        hora_duration = total_duration / 12.0  # 12 horas in day/night

        # Find current hora
        elapsed = (dt - start_time).total_seconds()
        current_hora_index = int(elapsed / hora_duration)

        if current_hora_index >= 12:
            current_hora_index = 11  # Safety check

        # Get ruler (cycles through 7 planets)
        ruler_index = current_hora_index % 7
        current_ruler = hora_rulers[ruler_index]

        # Calculate hora timing
        hora_start = start_time + timedelta(seconds=current_hora_index * hora_duration)
        hora_end = hora_start + timedelta(seconds=hora_duration)
        hora_progress = ((elapsed % hora_duration) / hora_duration) * 100

        # Get next favorable hora for specific activities
        next_favorable = self._get_next_favorable_hora(dt, latitude, longitude)

        return {
            "current_time": dt.isoformat(),
            "is_day": is_day,
            "hora_number": current_hora_index + 1,
            "ruling_planet": current_ruler,
            "hora_starts": hora_start.isoformat(),
            "hora_ends": hora_end.isoformat(),
            "progress_percent": round(hora_progress, 2),
            "favorable_for": self._get_hora_activities(current_ruler),
            "unfavorable_for": self._get_hora_avoid(current_ruler),
            "strength": self._get_hora_strength(current_ruler, is_day, dt),
            "next_favorable": next_favorable
        }

    def get_daily_hora_table(self, date: datetime, latitude: float, longitude: float) -> List[Dict[str, Any]]:
        """
        Get complete hora table for a day (all 24 horas)
        """
        sunrise, sunset = self._calculate_sunrise_sunset(date, latitude, longitude)

        if not sunrise or not sunset:
            return []

        horas = []

        # Day horas (sunrise to sunset)
        day_duration = (sunset - sunrise).total_seconds()
        day_hora_duration = day_duration / 12.0

        for i in range(12):
            hora_start = sunrise + timedelta(seconds=i * day_hora_duration)
            hora_end = hora_start + timedelta(seconds=day_hora_duration)
            ruler = self.HORA_RULERS_DAY[i % 7]

            horas.append({
                "hora_number": i + 1,
                "period": "Day",
                "ruling_planet": ruler,
                "starts_at": hora_start.isoformat(),
                "ends_at": hora_end.isoformat(),
                "favorable_for": self._get_hora_activities(ruler),
                "strength": self._get_hora_strength(ruler, True, hora_start)
            })

        # Night horas (sunset to next sunrise)
        next_day = date + timedelta(days=1)
        next_sunrise, _ = self._calculate_sunrise_sunset(next_day, latitude, longitude)

        if next_sunrise:
            night_duration = (next_sunrise - sunset).total_seconds()
            night_hora_duration = night_duration / 12.0

            for i in range(12):
                hora_start = sunset + timedelta(seconds=i * night_hora_duration)
                hora_end = hora_start + timedelta(seconds=night_hora_duration)
                ruler = self.HORA_RULERS_NIGHT[i % 7]

                horas.append({
                    "hora_number": i + 13,
                    "period": "Night",
                    "ruling_planet": ruler,
                    "starts_at": hora_start.isoformat(),
                    "ends_at": hora_end.isoformat(),
                    "favorable_for": self._get_hora_activities(ruler),
                    "strength": self._get_hora_strength(ruler, False, hora_start)
                })

        return horas

    def _get_hora_activities(self, ruler: str) -> List[str]:
        """Get favorable activities for hora"""
        activities = {
            "Sun": ["Government work", "Leadership", "Authority", "Meeting officials"],
            "Moon": ["Emotional work", "Home matters", "Travel", "Water activities"],
            "Mars": ["Sports", "Competition", "Physical work", "Surgery"],
            "Mercury": ["Business", "Communication", "Education", "Writing", "Trading"],
            "Jupiter": ["Spiritual work", "Teaching", "Religious ceremonies", "Charity"],
            "Venus": ["Arts", "Beauty", "Romance", "Luxury", "Creativity"],
            "Saturn": ["Construction", "Long-term planning", "Hard work", "Service"]
        }
        return activities.get(ruler, [])

    def _get_hora_avoid(self, ruler: str) -> List[str]:
        """Get activities to avoid during hora"""
        avoid = {
            "Sun": ["Humility required work"],
            "Moon": ["Harsh decisions", "Confrontations"],
            "Mars": ["Peace negotiations", "Delicate work"],
            "Mercury": ["Silent retreat"],
            "Jupiter": ["Unethical activities"],
            "Venus": ["Harsh labor"],
            "Saturn": ["Marriage", "Pleasure", "Quick gains"]
        }
        return avoid.get(ruler, [])

    def _get_hora_strength(self, ruler: str, is_day: bool, dt: datetime) -> str:
        """Assess hora strength"""
        # Day planets: Sun, Jupiter, Saturn (stronger during day)
        # Night planets: Moon, Venus (stronger during night)
        # Mercury: Strong both day and night
        # Mars: Neutral

        day_planets = ["Sun", "Jupiter", "Saturn"]
        night_planets = ["Moon", "Venus"]

        if ruler in day_planets and is_day:
            return "Strong"
        elif ruler in night_planets and not is_day:
            return "Strong"
        elif ruler == "Mercury":
            return "Strong"
        elif ruler == "Mars":
            return "Moderate"
        else:
            return "Weak"

    def _get_next_favorable_hora(self, dt: datetime, latitude: float, longitude: float, activity_type: str = "general") -> Dict[str, Any]:
        """Find next favorable hora for specific activity"""
        # For simplicity, return next Jupiter or Venus hora (generally favorable)
        favorable_planets = ["Jupiter", "Venus", "Mercury"]

        # Check next 24 horas
        for hours_ahead in range(24):
            check_time = dt + timedelta(hours=hours_ahead)
            hora_info = self.calculate_hora(check_time, latitude, longitude)

            if hora_info.get("ruling_planet") in favorable_planets:
                return {
                    "planet": hora_info["ruling_planet"],
                    "starts_at": hora_info["hora_starts"],
                    "hours_from_now": hours_ahead
                }

        return {"planet": None, "starts_at": None, "hours_from_now": None}

    # ============================================================================
    # GOOD TIME FINDER (MUHURTA FINDER)
    # ============================================================================

    def find_marriage_muhurta(
        self,
        start_date: datetime,
        end_date: datetime,
        latitude: float,
        longitude: float,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find auspicious times for marriage

        Criteria:
        - Favorable Tithis: 2, 3, 5, 7, 10, 11, 13 (both pakshas)
        - Favorable Nakshatras: Rohini, Mrigashira, Magha, Uttara Phalguni, Hasta, Swati, Anuradha, Uttara Ashadha, Uttara Bhadrapada, Revati
        - Avoid: Ashtami, Navami, Chaturdashi, Amavasya
        - Avoid: Vishti Karana
        - Favorable Varas: Wednesday (Mercury), Thursday (Jupiter), Friday (Venus)
        - Avoid: Tuesday (Mars - war), Saturday (Saturn - delays)
        """
        favorable_tithis = [1, 2, 4, 6, 9, 10, 12, 16, 17, 19, 21, 24, 25, 27]
        favorable_nakshatras = [3, 4, 9, 11, 12, 14, 16, 20, 25, 26]  # Indices
        avoid_varas = [2, 6]  # Tuesday, Saturday
        favorable_varas = [3, 4, 5]  # Wednesday, Thursday, Friday

        return self._find_muhurta_generic(
            start_date, end_date, latitude, longitude, max_results,
            activity_type="marriage",
            favorable_tithis=favorable_tithis,
            favorable_nakshatras=favorable_nakshatras,
            avoid_varas=avoid_varas,
            favorable_varas=favorable_varas,
            min_score=70
        )

    def find_business_start_muhurta(
        self,
        start_date: datetime,
        end_date: datetime,
        latitude: float,
        longitude: float,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find auspicious times for starting a business

        Criteria:
        - Favorable Tithis: 2, 3, 5, 10, 11, 13 (growth-oriented)
        - Favorable Nakshatras: Ashwini, Rohini, Pushya, Hasta, Chitra, Swati, Anuradha, Shravana, Revati
        - Favorable Varas: Wednesday (Mercury - commerce), Thursday (Jupiter - prosperity)
        - Favorable Horas: Mercury, Jupiter
        - Avoid: Amavasya, Chaturdashi
        """
        favorable_tithis = [1, 2, 4, 9, 10, 12, 16, 17, 19, 24, 25, 27]
        favorable_nakshatras = [0, 3, 7, 12, 13, 14, 16, 21, 26]
        favorable_varas = [3, 4]  # Wednesday, Thursday
        favorable_horas = ["Mercury", "Jupiter"]

        return self._find_muhurta_generic(
            start_date, end_date, latitude, longitude, max_results,
            activity_type="business_start",
            favorable_tithis=favorable_tithis,
            favorable_nakshatras=favorable_nakshatras,
            favorable_varas=favorable_varas,
            favorable_horas=favorable_horas,
            min_score=65
        )

    def find_travel_muhurta(
        self,
        start_date: datetime,
        end_date: datetime,
        latitude: float,
        longitude: float,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find auspicious times for travel

        Criteria:
        - Favorable Tithis: 2, 3, 5, 7, 10, 11, 13
        - Favorable Nakshatras: Ashwini (swift), Punarvasu, Pushya, Hasta, Anuradha, Shravana, Dhanishtha
        - Favorable Varas: Monday (Moon - travel), Wednesday (Mercury - short trips)
        - Avoid: 8th house afflictions (check separately in chart)
        - Avoid: Vishti Karana
        """
        favorable_tithis = [1, 2, 4, 6, 9, 10, 12, 16, 17, 19, 21, 24, 25]
        favorable_nakshatras = [0, 6, 7, 12, 16, 21, 22]
        favorable_varas = [1, 3]  # Monday, Wednesday

        return self._find_muhurta_generic(
            start_date, end_date, latitude, longitude, max_results,
            activity_type="travel",
            favorable_tithis=favorable_tithis,
            favorable_nakshatras=favorable_nakshatras,
            favorable_varas=favorable_varas,
            min_score=60
        )

    def find_property_purchase_muhurta(
        self,
        start_date: datetime,
        end_date: datetime,
        latitude: float,
        longitude: float,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find auspicious times for property purchase

        Criteria:
        - Favorable Tithis: 2, 3, 5, 7, 10, 11, 13 (stable tithis)
        - Favorable Nakshatras: Rohini (fixed), Uttara Phalguni, Uttara Ashadha, Uttara Bhadrapada (all Uttara - completion)
        - Favorable Varas: Thursday (Jupiter - expansion), Saturday (Saturn - property)
        - Avoid: Movable nakshatras for real estate
        - Need 4th house strength (check in natal chart separately)
        """
        favorable_tithis = [1, 2, 4, 6, 9, 10, 12, 16, 17, 19, 21, 24, 25]
        favorable_nakshatras = [3, 11, 20, 25]  # Fixed nakshatras
        favorable_varas = [4, 6]  # Thursday, Saturday

        return self._find_muhurta_generic(
            start_date, end_date, latitude, longitude, max_results,
            activity_type="property_purchase",
            favorable_tithis=favorable_tithis,
            favorable_nakshatras=favorable_nakshatras,
            favorable_varas=favorable_varas,
            min_score=65
        )

    def find_surgery_muhurta(
        self,
        start_date: datetime,
        end_date: datetime,
        latitude: float,
        longitude: float,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find auspicious times for surgery/medical procedures

        Criteria:
        - Favorable Nakshatras: Ashwini (healing), Rohini, Mrigashira, Pushya, Hasta, Anuradha, Revati
        - Avoid: Mars hora (blood/cutting)
        - Avoid: Ashtami, Navami (8th, 9th tithis)
        - Avoid: Vishti Karana
        - Prefer: Waxing moon (Shukla Paksha) for recovery
        - Avoid: Saturday (Saturn - complications)
        """
        favorable_tithis = [1, 2, 4, 6, 9, 10, 12]  # Shukla Paksha preferred
        favorable_nakshatras = [0, 3, 4, 7, 12, 16, 26]
        avoid_varas = [2, 6]  # Tuesday (Mars), Saturday (Saturn)
        avoid_horas = ["Mars", "Saturn"]

        return self._find_muhurta_generic(
            start_date, end_date, latitude, longitude, max_results,
            activity_type="surgery",
            favorable_tithis=favorable_tithis,
            favorable_nakshatras=favorable_nakshatras,
            avoid_varas=avoid_varas,
            avoid_horas=avoid_horas,
            min_score=70
        )

    def _find_muhurta_generic(
        self,
        start_date: datetime,
        end_date: datetime,
        latitude: float,
        longitude: float,
        max_results: int,
        activity_type: str,
        favorable_tithis: List[int] = None,
        favorable_nakshatras: List[int] = None,
        favorable_varas: List[int] = None,
        avoid_varas: List[int] = None,
        favorable_horas: List[str] = None,
        avoid_horas: List[str] = None,
        min_score: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Generic muhurta finder with scoring system

        Scans through date range and finds times matching criteria.
        Returns ONE best time per auspicious day (not multiple hours from same day).
        """
        daily_results = {}  # Store best result per day
        current_date = start_date

        # Scan through each day
        while current_date <= end_date:
            # Calculate panchang for the day
            panchang = self.calculate_panchang(current_date, latitude, longitude)

            # Score this day
            day_score = self._score_muhurta(
                panchang=panchang,
                favorable_tithis=favorable_tithis,
                favorable_nakshatras=favorable_nakshatras,
                favorable_varas=favorable_varas,
                avoid_varas=avoid_varas
            )

            # If day meets minimum criteria, find best hora
            if day_score >= min_score - 20:  # Give some flexibility
                # Get hora table only for promising days (optimization)
                hora_table = self.get_daily_hora_table(current_date, latitude, longitude)

                best_hora_for_day = None
                best_score_for_day = 0

                for hora in hora_table:
                    hora_score = self._score_hora(
                        hora,
                        favorable_horas=favorable_horas,
                        avoid_horas=avoid_horas
                    )

                    total_score = (day_score + hora_score) / 2

                    if total_score >= min_score and total_score > best_score_for_day:
                        best_score_for_day = total_score
                        best_hora_for_day = hora

                # Store best result for this day
                if best_hora_for_day and best_score_for_day >= min_score:
                    date_key = current_date.date().isoformat()
                    daily_results[date_key] = {
                        "datetime": best_hora_for_day["starts_at"],
                        "date": date_key,
                        "time_range": f"{best_hora_for_day['starts_at']} to {best_hora_for_day['ends_at']}",
                        "score": round(best_score_for_day, 1),
                        "quality": self._get_quality_label(best_score_for_day),
                        "tithi": panchang["tithi"]["tithi_name"],
                        "nakshatra": panchang["nakshatra"]["nakshatra_name"],
                        "vara": panchang["vara"]["vara_name"],
                        "hora_ruler": best_hora_for_day["ruling_planet"],
                        "yoga": panchang["yoga"]["yoga_name"],
                        "karana": panchang["karana"]["karana_name"],
                        "reasons": self._get_muhurta_reasons(
                            panchang, best_hora_for_day, activity_type,
                            favorable_tithis, favorable_nakshatras,
                            favorable_varas, favorable_horas
                        ),
                        "precautions": self._get_muhurta_precautions(
                            panchang, best_hora_for_day, activity_type
                        )
                    }

            current_date += timedelta(days=1)

        # Convert to list, sort by score, and return top results
        results = list(daily_results.values())
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:max_results]

    def _score_muhurta(
        self,
        panchang: Dict[str, Any],
        favorable_tithis: List[int] = None,
        favorable_nakshatras: List[int] = None,
        favorable_varas: List[int] = None,
        avoid_varas: List[int] = None
    ) -> float:
        """Score a muhurta based on panchang elements"""
        score = 50.0  # Base score

        # Tithi scoring (25 points)
        tithi_num = panchang["tithi"]["tithi_number"] - 1
        if favorable_tithis and tithi_num in favorable_tithis:
            score += 25
        elif panchang["tithi"]["is_auspicious"]:
            score += 15
        elif tithi_num in [7, 8, 13, 14, 29]:  # Very inauspicious
            score -= 20

        # Nakshatra scoring (20 points)
        nakshatra_num = panchang["nakshatra"]["nakshatra_number"] - 1
        if favorable_nakshatras and nakshatra_num in favorable_nakshatras:
            score += 20
        elif panchang["nakshatra"]["is_auspicious"]:
            score += 10

        # Vara scoring (15 points)
        vara_num = panchang["vara"]["vara_number"] - 1
        if avoid_varas and vara_num in avoid_varas:
            score -= 20
        elif favorable_varas and vara_num in favorable_varas:
            score += 15

        # Yoga scoring (15 points)
        if panchang["yoga"]["is_auspicious"]:
            score += 15
        else:
            score -= 10

        # Karana scoring (10 points)
        if panchang["karana"]["is_auspicious"]:
            score += 10
        else:
            score -= 15  # Vishti is very bad

        # Overall quality bonus (15 points)
        if panchang["overall_quality"] == "Highly Auspicious":
            score += 15
        elif panchang["overall_quality"] == "Auspicious":
            score += 10

        return max(0, min(100, score))  # Clamp between 0-100

    def _score_hora(
        self,
        hora: Dict[str, Any],
        favorable_horas: List[str] = None,
        avoid_horas: List[str] = None
    ) -> float:
        """Score a hora"""
        score = 50.0

        ruler = hora["ruling_planet"]

        if avoid_horas and ruler in avoid_horas:
            score -= 30
        elif favorable_horas and ruler in favorable_horas:
            score += 30

        # Strength bonus
        if hora["strength"] == "Strong":
            score += 20
        elif hora["strength"] == "Weak":
            score -= 10

        return max(0, min(100, score))

    def _get_quality_label(self, score: float) -> str:
        """Get quality label from score"""
        if score >= 85:
            return "Excellent"
        elif score >= 70:
            return "Very Good"
        elif score >= 60:
            return "Good"
        elif score >= 50:
            return "Moderate"
        else:
            return "Below Average"

    def _get_muhurta_reasons(
        self,
        panchang: Dict,
        hora: Dict,
        activity_type: str,
        favorable_tithis: List[int],
        favorable_nakshatras: List[int],
        favorable_varas: List[int],
        favorable_horas: List[str]
    ) -> List[str]:
        """Get reasons why this muhurta is favorable"""
        reasons = []

        # Check tithi
        tithi_num = panchang["tithi"]["tithi_number"] - 1
        if favorable_tithis and tithi_num in favorable_tithis:
            reasons.append(f"{panchang['tithi']['tithi_name']} Tithi is favorable for {activity_type}")

        # Check nakshatra
        nakshatra_num = panchang["nakshatra"]["nakshatra_number"] - 1
        if favorable_nakshatras and nakshatra_num in favorable_nakshatras:
            reasons.append(f"Moon in {panchang['nakshatra']['nakshatra_name']} is auspicious")

        # Check vara
        vara_num = panchang["vara"]["vara_number"] - 1
        if favorable_varas and vara_num in favorable_varas:
            reasons.append(f"{panchang['vara']['vara_name']} is favorable (ruled by {panchang['vara']['ruling_planet']})")

        # Check hora
        if favorable_horas and hora["ruling_planet"] in favorable_horas:
            reasons.append(f"{hora['ruling_planet']} hora supports this activity")

        # Check yoga
        if panchang["yoga"]["is_auspicious"]:
            reasons.append(f"{panchang['yoga']['yoga_name']} Yoga brings positive results")

        return reasons

    def _get_muhurta_precautions(
        self,
        panchang: Dict,
        hora: Dict,
        activity_type: str
    ) -> List[str]:
        """Get precautions or things to be aware of"""
        precautions = []

        # Check for inauspicious elements
        if not panchang["tithi"]["is_auspicious"]:
            precautions.append(f"Tithi {panchang['tithi']['tithi_name']} requires extra care")

        if not panchang["yoga"]["is_auspicious"]:
            precautions.append(f"{panchang['yoga']['yoga_name']} Yoga - proceed with caution")

        if not panchang["karana"]["is_auspicious"]:
            precautions.append(f"Avoid {panchang['karana']['karana_name']} Karana if possible")

        if hora["strength"] == "Weak":
            precautions.append(f"{hora['ruling_planet']} hora is weak at this time")

        return precautions

    def find_best_time_today(
        self,
        activity_type: str,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        Find best time for activity today

        Quick lookup for immediate planning
        """
        today = datetime.now()
        end_of_day = today.replace(hour=23, minute=59, second=59)

        if activity_type == "marriage":
            results = self.find_marriage_muhurta(today, end_of_day, latitude, longitude, max_results=3)
        elif activity_type == "business":
            results = self.find_business_start_muhurta(today, end_of_day, latitude, longitude, max_results=3)
        elif activity_type == "travel":
            results = self.find_travel_muhurta(today, end_of_day, latitude, longitude, max_results=3)
        elif activity_type == "property":
            results = self.find_property_purchase_muhurta(today, end_of_day, latitude, longitude, max_results=3)
        elif activity_type == "surgery":
            results = self.find_surgery_muhurta(today, end_of_day, latitude, longitude, max_results=3)
        else:
            return {"error": "Invalid activity type"}

        if results:
            return {
                "activity_type": activity_type,
                "best_time": results[0],
                "alternatives": results[1:] if len(results) > 1 else [],
                "total_found": len(results)
            }
        else:
            return {
                "activity_type": activity_type,
                "best_time": None,
                "message": "No highly auspicious time found today. Consider checking upcoming days."
            }


# Create singleton instance
muhurta_service = MuhurtaService()
