"""
Hyperlocal Panchang Service
Handles complete Panchang calculations using Swiss Ephemeris
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import date, datetime, time, timedelta
from decimal import Decimal
import logging
import swisseph as swe

from app.core.supabase_client import SupabaseClient
from app.schemas.hyperlocal_panchang import (
    GetPanchangRequest,
    SubscribeLocationRequest,
    UpdatePanchangPreferencesRequest,
    Panchang,
    TithiInfo,
    NakshatraInfo,
    YogaInfo,
    KaranaInfo,
    VaraInfo,
    HoraInfo,
    SunMoonData,
    InauspiciousTime,
    AuspiciousTime,
    PanchangSubscription,
    PanchangPreferences,
    DailyGuidance,
    Paksha,
    MoonPhase,
    Ritu,
    DayQuality
)

logger = logging.getLogger(__name__)


class HyperlocalPanchangService:
    """Service for Hyperlocal Panchang calculations"""

    # Tithi names (30 lunar days)
    TITHI_NAMES = [
        "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
        "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
        "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima/Amavasya"
    ] * 2  # Repeat for both Pakshas

    # Nakshatra names (27 lunar mansions)
    NAKSHATRA_NAMES = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
        "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
        "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
        "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
        "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
    ]

    # Nakshatra lords
    NAKSHATRA_LORDS = [
        "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"
    ] * 3

    # Yoga names (27)
    YOGA_NAMES = [
        "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda",
        "Sukarman", "Dhriti", "Shula", "Ganda", "Vriddhi", "Dhruva",
        "Vyaghata", "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyan",
        "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla",
        "Brahma", "Indra", "Vaidhriti"
    ]

    # Karana names (11)
    KARANA_NAMES = [
        "Bava", "Balava", "Kaulava", "Taitila", "Garaja", "Vanija", "Vishti",
        "Shakuni", "Chatushpada", "Naga", "Kimstughna"
    ]

    # Weekday names and lords
    VARA_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    VARA_LORDS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

    # Hora sequence (planetary hours)
    HORA_LORDS = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]

    def __init__(self, supabase: SupabaseClient):
        self.supabase = supabase
        # Set ephemeris path (adjust based on your setup)
        swe.set_ephe_path('/usr/share/ephe')  # or wherever Swiss Ephemeris files are

    async def get_panchang(
        self,
        request: GetPanchangRequest
    ) -> Panchang:
        """Calculate complete Panchang for date and location"""

        # Check cache first
        cached = await self._get_cached_panchang(
            request.panchang_date,
            request.latitude,
            request.longitude
        )

        if cached:
            return Panchang(**cached)

        # Calculate Panchang
        panchang_data = await self._calculate_panchang(
            request.panchang_date,
            float(request.latitude),
            float(request.longitude),
            request.timezone,
            request.location_name
        )

        # Cache it
        await self._cache_panchang(panchang_data)

        return Panchang(**panchang_data)

    async def _calculate_panchang(
        self,
        panchang_date: date,
        latitude: float,
        longitude: float,
        timezone: str,
        location_name: Optional[str]
    ) -> Dict[str, Any]:
        """Calculate all Panchang elements"""

        # Convert date to Julian Day
        jd = swe.julday(
            panchang_date.year,
            panchang_date.month,
            panchang_date.day,
            12.0  # Noon
        )

        # Calculate Sun and Moon positions
        sun_pos = swe.calc_ut(jd, swe.SUN)[0][0]  # Longitude in degrees
        moon_pos = swe.calc_ut(jd, swe.MOON)[0][0]

        # Calculate Tithi
        tithi_info = self._calculate_tithi(moon_pos, sun_pos, jd, latitude, longitude)

        # Calculate Nakshatra
        nakshatra_info = self._calculate_nakshatra(moon_pos, jd, latitude, longitude)

        # Calculate Yoga
        yoga_info = self._calculate_yoga(sun_pos, moon_pos, jd, latitude, longitude)

        # Calculate Karana
        karana_info = self._calculate_karana(moon_pos, sun_pos)

        # Calculate Vara (weekday)
        weekday = panchang_date.weekday()
        vara_name = self.VARA_NAMES[(weekday + 1) % 7]  # Adjust: Python Monday=0, we want Sunday=0
        vara_lord = self.VARA_LORDS[(weekday + 1) % 7]

        # Calculate Sun/Moon times
        sun_moon_data = self._calculate_sun_moon_times(panchang_date, latitude, longitude)

        # Calculate Rahukaal
        sunrise_time = sun_moon_data["sunrise"].time()
        sunset_time = sun_moon_data["sunset"].time()
        rahukaal_start, rahukaal_end = self._calculate_rahukaal(
            (weekday + 1) % 7,  # Adjust to Sunday=0
            sunrise_time,
            sunset_time
        )

        # Calculate Hora sequence
        hora_sequence = self._calculate_hora_sequence(
            panchang_date,
            sunrise_time,
            sunset_time,
            (weekday + 1) % 7
        )

        # Check special days
        is_ekadashi = tithi_info["tithi_number"] == 11
        is_purnima = tithi_info["tithi_number"] == 15 and tithi_info["paksha"] == "Shukla"
        is_amavasya = tithi_info["tithi_number"] == 15 and tithi_info["paksha"] == "Krishna"

        # Build Panchang data
        panchang_data = {
            "panchang_date": panchang_date.isoformat(),
            "location_name": location_name,
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone,

            # Panchang elements
            "tithi": tithi_info,
            "nakshatra": nakshatra_info,
            "yoga": yoga_info,
            "karana": karana_info,
            "vara": {
                "vara_name": vara_name,
                "vara_lord": vara_lord,
                "vara_number": (weekday + 1) % 7
            },
            "paksha": tithi_info["paksha"],

            # Sun/Moon
            "sun_moon": sun_moon_data,

            # Inauspicious times
            "rahukaal_start": rahukaal_start.isoformat(),
            "rahukaal_end": rahukaal_end.isoformat(),

            # Auspicious times
            "abhijit_muhurta_start": self._calculate_abhijit_muhurta(sunrise_time, sunset_time)[0].isoformat(),
            "abhijit_muhurta_end": self._calculate_abhijit_muhurta(sunrise_time, sunset_time)[1].isoformat(),
            "brahma_muhurta_start": self._calculate_brahma_muhurta(sun_moon_data["sunrise"])[0].isoformat(),
            "brahma_muhurta_end": self._calculate_brahma_muhurta(sun_moon_data["sunrise"])[1].isoformat(),

            # Hora
            "hora_sequence": hora_sequence,

            # Special days
            "is_ekadashi": is_ekadashi,
            "is_amavasya": is_amavasya,
            "is_purnima": is_purnima,
            "is_festival": False,  # Would check database

            # Metadata
            "calculated_at": datetime.now().isoformat(),
            "calculation_version": "1.0"
        }

        return panchang_data

    def _calculate_tithi(
        self,
        moon_long: float,
        sun_long: float,
        jd: float,
        lat: float,
        lon: float
    ) -> Dict[str, Any]:
        """Calculate Tithi (lunar day)"""

        # Tithi = (Moon - Sun) / 12 degrees
        elongation = (moon_long - sun_long) % 360

        # Each Tithi is 12 degrees
        tithi_num = int(elongation / 12) + 1

        # Determine Paksha
        if tithi_num <= 15:
            paksha = Paksha.SHUKLA
            tithi_index = tithi_num - 1
        else:
            paksha = Paksha.KRISHNA
            tithi_index = tithi_num - 1

        tithi_name = self.TITHI_NAMES[tithi_index]

        # Calculate Tithi end time (simplified - would need iterative calculation)
        # For now, placeholder
        tithi_start_utc = swe.jdut1_to_utc(jd - 0.5)
        tithi_start = datetime(tithi_start_utc[0], tithi_start_utc[1], tithi_start_utc[2],
                               int(tithi_start_utc[3]), int(tithi_start_utc[4]), int(tithi_start_utc[5]))
        tithi_end_utc = swe.jdut1_to_utc(jd + 0.5)
        tithi_end = datetime(tithi_end_utc[0], tithi_end_utc[1], tithi_end_utc[2],
                             int(tithi_end_utc[3]), int(tithi_end_utc[4]), int(tithi_end_utc[5]))

        return {
            "tithi_name": tithi_name,
            "tithi_number": tithi_num,
            "paksha": paksha.value,
            "tithi_start_time": tithi_start.isoformat(),
            "tithi_end_time": tithi_end.isoformat(),
            "tithi_quality": self._get_tithi_quality(tithi_num),
            "is_active": True
        }

    def _calculate_nakshatra(
        self,
        moon_long: float,
        jd: float,
        lat: float,
        lon: float
    ) -> Dict[str, Any]:
        """Calculate Nakshatra (lunar mansion)"""

        # Each Nakshatra is 13°20' (13.333...)
        nakshatra_num = int(moon_long / (360 / 27)) + 1
        nakshatra_index = nakshatra_num - 1

        # Pada (quarter) - each Pada is 3°20'
        pada_num = int((moon_long % (360 / 27)) / (360 / 108)) + 1

        nakshatra_name = self.NAKSHATRA_NAMES[nakshatra_index]
        nakshatra_lord = self.NAKSHATRA_LORDS[nakshatra_index]

        # Placeholder times
        nakshatra_start_utc = swe.jdut1_to_utc(jd - 0.5)
        nakshatra_start = datetime(nakshatra_start_utc[0], nakshatra_start_utc[1], nakshatra_start_utc[2],
                                   int(nakshatra_start_utc[3]), int(nakshatra_start_utc[4]), int(nakshatra_start_utc[5]))
        nakshatra_end_utc = swe.jdut1_to_utc(jd + 0.5)
        nakshatra_end = datetime(nakshatra_end_utc[0], nakshatra_end_utc[1], nakshatra_end_utc[2],
                                 int(nakshatra_end_utc[3]), int(nakshatra_end_utc[4]), int(nakshatra_end_utc[5]))

        return {
            "nakshatra_name": nakshatra_name,
            "nakshatra_number": nakshatra_num,
            "nakshatra_start_time": nakshatra_start.isoformat(),
            "nakshatra_end_time": nakshatra_end.isoformat(),
            "nakshatra_pada": pada_num,
            "nakshatra_lord": nakshatra_lord,
            "nakshatra_quality": "favorable",  # Would have quality mapping
            "is_active": True
        }

    def _calculate_yoga(
        self,
        sun_long: float,
        moon_long: float,
        jd: float,
        lat: float,
        lon: float
    ) -> Dict[str, Any]:
        """Calculate Yoga"""

        # Yoga = (Sun + Moon) / 13.333...
        yoga_sum = (sun_long + moon_long) % 360
        yoga_num = int(yoga_sum / (360 / 27)) + 1
        yoga_name = self.YOGA_NAMES[yoga_num - 1]

        yoga_start_utc = swe.jdut1_to_utc(jd - 0.5)
        yoga_start = datetime(yoga_start_utc[0], yoga_start_utc[1], yoga_start_utc[2],
                              int(yoga_start_utc[3]), int(yoga_start_utc[4]), int(yoga_start_utc[5]))
        yoga_end_utc = swe.jdut1_to_utc(jd + 0.5)
        yoga_end = datetime(yoga_end_utc[0], yoga_end_utc[1], yoga_end_utc[2],
                            int(yoga_end_utc[3]), int(yoga_end_utc[4]), int(yoga_end_utc[5]))

        return {
            "yoga_name": yoga_name,
            "yoga_number": yoga_num,
            "yoga_start_time": yoga_start.isoformat(),
            "yoga_end_time": yoga_end.isoformat(),
            "yoga_quality": "favorable",
            "is_active": True
        }

    def _calculate_karana(self, moon_long: float, sun_long: float) -> Dict[str, Any]:
        """Calculate Karana (half Tithi)"""

        elongation = (moon_long - sun_long) % 360
        karana_num = int(elongation / 6) % 11 + 1  # Simplified

        karana_name = self.KARANA_NAMES[(karana_num - 1) % 11]

        return {
            "karana_name": karana_name,
            "karana_number": karana_num,
            "karana_quality": "favorable"
        }

    def _calculate_sun_moon_times(
        self,
        panchang_date: date,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """Calculate Sun and Moon rise/set times"""

        # Use Swiss Ephemeris for rise/set
        jd = swe.julday(panchang_date.year, panchang_date.month, panchang_date.day, 0.0)

        # Geographic position tuple: (longitude, latitude, altitude)
        geopos = (longitude, latitude, 0.0)

        # Sunrise
        sunrise_result = swe.rise_trans(
            jd, swe.SUN, geopos,
            swe.CALC_RISE | swe.BIT_DISC_CENTER
        )
        sunrise_jd = sunrise_result[1][0] if sunrise_result[0] == swe.OK else jd

        # Sunset
        sunset_result = swe.rise_trans(
            jd, swe.SUN, geopos,
            swe.CALC_SET | swe.BIT_DISC_CENTER
        )
        sunset_jd = sunset_result[1][0] if sunset_result[0] == swe.OK else jd + 0.5

        # Convert to datetime
        sunrise_utc = swe.jdut1_to_utc(sunrise_jd)
        sunrise_dt = datetime(sunrise_utc[0], sunrise_utc[1], sunrise_utc[2],
                              int(sunrise_utc[3]), int(sunrise_utc[4]), int(sunrise_utc[5]))
        sunset_utc = swe.jdut1_to_utc(sunset_jd)
        sunset_dt = datetime(sunset_utc[0], sunset_utc[1], sunset_utc[2],
                             int(sunset_utc[3]), int(sunset_utc[4]), int(sunset_utc[5]))

        # Moon phase calculation
        moon_pos = swe.calc_ut(jd, swe.MOON)[0][0]
        sun_pos = swe.calc_ut(jd, swe.SUN)[0][0]
        elongation = (moon_pos - sun_pos) % 360

        # Moon illumination (simplified)
        illumination = (1 - abs(elongation - 180) / 180) * 100

        # Determine moon phase
        if elongation < 22.5 or elongation > 337.5:
            moon_phase = MoonPhase.NEW_MOON
        elif 22.5 <= elongation < 67.5:
            moon_phase = MoonPhase.WAXING_CRESCENT
        elif 67.5 <= elongation < 112.5:
            moon_phase = MoonPhase.FIRST_QUARTER
        elif 112.5 <= elongation < 157.5:
            moon_phase = MoonPhase.WAXING_GIBBOUS
        elif 157.5 <= elongation < 202.5:
            moon_phase = MoonPhase.FULL_MOON
        elif 202.5 <= elongation < 247.5:
            moon_phase = MoonPhase.WANING_GIBBOUS
        elif 247.5 <= elongation < 292.5:
            moon_phase = MoonPhase.LAST_QUARTER
        else:
            moon_phase = MoonPhase.WANING_CRESCENT

        return {
            "sunrise": sunrise_dt.isoformat(),
            "sunset": sunset_dt.isoformat(),
            "moonrise": None,  # Would calculate similarly
            "moonset": None,
            "moon_phase": moon_phase.value,
            "moon_illumination": round(illumination, 2)
        }

    def _calculate_rahukaal(
        self,
        weekday: int,  # 0=Sunday
        sunrise: time,
        sunset: time
    ) -> Tuple[time, time]:
        """Calculate Rahukaal (inauspicious period)"""

        # Calculate day duration
        sunrise_minutes = sunrise.hour * 60 + sunrise.minute
        sunset_minutes = sunset.hour * 60 + sunset.minute
        day_duration = sunset_minutes - sunrise_minutes

        # One-eighth of day
        one_eighth = day_duration / 8

        # Rahukaal period varies by weekday
        rahukaal_period = {
            0: 8,  # Sunday - 8th period
            1: 2,  # Monday - 2nd period
            2: 7,  # Tuesday - 7th period
            3: 5,  # Wednesday - 5th period
            4: 6,  # Thursday - 6th period
            5: 4,  # Friday - 4th period
            6: 3   # Saturday - 3rd period
        }[weekday]

        # Calculate start and end
        start_minutes = sunrise_minutes + (one_eighth * (rahukaal_period - 1))
        end_minutes = sunrise_minutes + (one_eighth * rahukaal_period)

        start_time = time(int(start_minutes // 60), int(start_minutes % 60))
        end_time = time(int(end_minutes // 60), int(end_minutes % 60))

        return start_time, end_time

    def _calculate_hora_sequence(
        self,
        panchang_date: date,
        sunrise: time,
        sunset: time,
        weekday: int
    ) -> List[Dict[str, Any]]:
        """Calculate 24-hour Hora (planetary hours) sequence"""

        # Day and night duration
        sunrise_minutes = sunrise.hour * 60 + sunrise.minute
        sunset_minutes = sunset.hour * 60 + sunset.minute

        day_duration = sunset_minutes - sunrise_minutes
        night_duration = 1440 - day_duration  # 24 hours = 1440 minutes

        # 12 day horas, 12 night horas
        day_hora_length = day_duration / 12
        night_hora_length = night_duration / 12

        # Hora sequence starts with weekday lord
        hora_sequence = []
        current_lord_index = weekday

        # Day horas
        current_time = sunrise_minutes
        for i in range(12):
            lord = self.HORA_LORDS[current_lord_index % 7]
            start_time = time(int(current_time // 60), int(current_time % 60))
            current_time += day_hora_length
            end_time = time(int(current_time // 60), int(current_time % 60))

            start_dt = datetime.combine(panchang_date, start_time)
            end_dt = datetime.combine(panchang_date, end_time)

            hora_sequence.append({
                "hora_number": i + 1,
                "planet": lord,
                "start_time": start_dt.isoformat(),
                "end_time": end_dt.isoformat(),
                "is_favorable": lord in ["Jupiter", "Venus", "Mercury", "Moon"]
            })

            current_lord_index += 1

        # Night horas
        current_time = sunset_minutes
        for i in range(12, 24):
            lord = self.HORA_LORDS[current_lord_index % 7]
            start_time = time(int(current_time // 60) % 24, int(current_time % 60))
            current_time += night_hora_length
            end_time = time(int(current_time // 60) % 24, int(current_time % 60))

            start_dt = datetime.combine(panchang_date, start_time)
            if current_time >= 1440:  # Next day
                end_dt = datetime.combine(panchang_date + timedelta(days=1), end_time)
            else:
                end_dt = datetime.combine(panchang_date, end_time)

            hora_sequence.append({
                "hora_number": i + 1,
                "planet": lord,
                "start_time": start_dt.isoformat(),
                "end_time": end_dt.isoformat(),
                "is_favorable": lord in ["Jupiter", "Venus", "Mercury", "Moon"]
            })

            current_lord_index += 1

        return hora_sequence

    def _calculate_abhijit_muhurta(
        self,
        sunrise: time,
        sunset: time
    ) -> Tuple[time, time]:
        """Calculate Abhijit Muhurta (most auspicious period around noon)"""

        sunrise_minutes = sunrise.hour * 60 + sunrise.minute
        sunset_minutes = sunset.hour * 60 + sunset.minute

        # Abhijit is 8/15th of the day (approximately noon)
        day_duration = sunset_minutes - sunrise_minutes
        abhijit_start = sunrise_minutes + (day_duration * 8 / 15)
        abhijit_duration = day_duration / 15  # One Muhurta

        start_time = time(int(abhijit_start // 60), int(abhijit_start % 60))
        end_time = time(int((abhijit_start + abhijit_duration) // 60), int((abhijit_start + abhijit_duration) % 60))

        return start_time, end_time

    def _calculate_brahma_muhurta(self, sunrise: datetime) -> Tuple[time, time]:
        """Calculate Brahma Muhurta (1.5 hours before sunrise)"""

        brahma_end = sunrise
        brahma_start = sunrise - timedelta(hours=1, minutes=36)

        return brahma_start.time(), brahma_end.time()

    def _get_tithi_quality(self, tithi_num: int) -> str:
        """Get quality of Tithi"""
        # Simplified quality mapping
        auspicious = [2, 3, 5, 7, 10, 11, 13]
        if tithi_num in auspicious:
            return "Auspicious"
        return "Neutral"

    async def _cache_panchang(self, panchang_data: Dict[str, Any]):
        """Cache Panchang in database"""
        await self.supabase.upsert(
            "panchang_cache",
            panchang_data,
            on_conflict="panchang_date,latitude,longitude"
        )

    async def _get_cached_panchang(
        self,
        panchang_date: date,
        latitude: Decimal,
        longitude: Decimal
    ) -> Optional[Dict[str, Any]]:
        """Get cached Panchang"""
        result = await self.supabase.select(
            "panchang_cache",
            filters={
                "panchang_date": panchang_date.isoformat(),
                "latitude": float(latitude),
                "longitude": float(longitude)
            }
        )

        return result[0] if result and len(result) > 0 else None

    # Location subscription methods
    async def subscribe_location(
        self,
        user_id: str,
        request: SubscribeLocationRequest
    ) -> PanchangSubscription:
        """Subscribe to location for daily Panchang"""

        subscription_data = {
            "user_id": user_id,
            "location_name": request.location_name,
            "latitude": float(request.latitude),
            "longitude": float(request.longitude),
            "timezone": request.timezone,
            "country": request.country,
            "state": request.state,
            "city": request.city,
            "is_primary": request.is_primary,
            "notification_enabled": request.notification_enabled,
            "notification_time": request.notification_time.isoformat()
        }

        result = await self.supabase.upsert(
            "panchang_subscriptions",
            subscription_data,
            on_conflict="user_id,location_name"
        )

        return PanchangSubscription(**result[0]) if result else None

    async def list_subscriptions(self, user_id: str) -> List[PanchangSubscription]:
        """List user's location subscriptions"""
        result = await self.supabase.select(
            "panchang_subscriptions",
            filters={"user_id": user_id}
        )

        return [PanchangSubscription(**sub) for sub in result] if result else []
