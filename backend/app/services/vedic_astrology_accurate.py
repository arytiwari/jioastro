"""
Accurate Vedic Astrology Calculation Service using Swiss Ephemeris
Based on classical Jyotish principles with professional-grade accuracy
"""

from typing import Dict, List, Any, Tuple
from datetime import datetime, date, time, timedelta
import swisseph as swe
import pytz
from app.services.extended_yoga_service import extended_yoga_service
from app.services.divisional_charts_service import divisional_charts_service
from app.services.dosha_detection_service import dosha_detection_service
from app.services.transit_service import transit_service
from app.services.dasha_interpretation_service import dasha_interpretation_service


class AccurateVedicAstrology:
    """Professional-grade Vedic astrology calculations using Swiss Ephemeris"""

    # Zodiac signs (Rashi)
    SIGNS = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]

    # Nakshatras (27 lunar mansions)
    NAKSHATRAS = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
        "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
        "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
        "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
        "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
    ]

    # Nakshatra lords for Vimshottari Dasha
    NAKSHATRA_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]

    # Vimshottari Dasha periods (in years)
    DASHA_YEARS = {
        "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16,
        "Saturn": 19, "Mercury": 17, "Ketu": 7, "Venus": 20
    }

    # Planet constants for Swiss Ephemeris
    PLANETS = {
        "Sun": swe.SUN,
        "Moon": swe.MOON,
        "Mars": swe.MARS,
        "Mercury": swe.MERCURY,
        "Jupiter": swe.JUPITER,
        "Venus": swe.VENUS,
        "Saturn": swe.SATURN,
        "Rahu": swe.MEAN_NODE,  # North Node (Rahu)
        "Ketu": swe.MEAN_NODE   # South Node (Ketu is 180° from Rahu)
    }

    def __init__(self):
        """Initialize Swiss Ephemeris with Lahiri ayanamsa"""
        # Set sidereal mode with Lahiri ayanamsa (Government of India standard)
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        print("✅ Swiss Ephemeris initialized with Lahiri ayanamsa")

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
        Calculate accurate Vedic birth chart (Rashi chart/D1)

        Uses:
        - Swiss Ephemeris for planetary positions
        - Lahiri ayanamsa for sidereal zodiac
        - Whole Sign house system (authentic Vedic method)
        """

        # Combine date and time
        birth_datetime = datetime.combine(birth_date, birth_time)

        # Convert to UTC if timezone provided
        if timezone_str != "UTC":
            try:
                local_tz = pytz.timezone(timezone_str)
                local_dt = local_tz.localize(birth_datetime)
                birth_datetime_utc = local_dt.astimezone(pytz.UTC)
            except:
                birth_datetime_utc = birth_datetime
        else:
            birth_datetime_utc = birth_datetime

        # Calculate Julian Day
        jd = swe.julday(
            birth_datetime_utc.year,
            birth_datetime_utc.month,
            birth_datetime_utc.day,
            birth_datetime_utc.hour + birth_datetime_utc.minute/60.0
        )

        # Calculate Ascendant (Lagna)
        # Using houses() instead of houses_ex() for simpler output
        # Returns (cusps, ascmc) where ascmc[0] is the Ascendant
        cusps, ascmc = swe.houses(jd, latitude, longitude, b'P')  # 'P' = Placidus
        asc_longitude = ascmc[0]  # Ascendant longitude in tropical

        # Convert to sidereal
        # Use get_ayanamsa_ut (not _ex) which returns a single float value
        ayanamsa = swe.get_ayanamsa_ut(jd)
        print(f"🔢 Ayanamsa value: {ayanamsa} (type: {type(ayanamsa)})")
        print(f"🔢 Ascendant tropical: {asc_longitude}")

        asc_sidereal = (asc_longitude - ayanamsa) % 360
        asc_sign = int(asc_sidereal / 30)
        asc_degree = asc_sidereal % 30

        print(f"✅ Ascendant sidereal: {asc_sidereal} (Sign: {self.SIGNS[asc_sign]} {asc_degree:.2f}°)")

        # Calculate all planets
        planets = self._calculate_planets(jd, ayanamsa, asc_sign)

        # Calculate houses using Whole Sign system (Vedic standard)
        houses = self._calculate_whole_sign_houses(asc_sign)

        # Determine which planets are in which houses
        planets = self._assign_houses_to_planets(planets, asc_sign)

        # Calculate nakshatras
        planets = self._add_nakshatras(planets)

        # Calculate Vimshottari Dasha
        dasha = self._calculate_vimshottari_dasha(planets["Moon"], birth_datetime)

        # Prepare chart context for AI personalization
        chart_context = {
            "planets": planets,
            "ascendant": {
                "sign": self.SIGNS[asc_sign],
                "sign_num": asc_sign,
                "degree": asc_degree
            }
        }

        # Enhance dasha with interpretations (includes AI personalization)
        dasha = dasha_interpretation_service.enhance_dasha_with_interpretations(
            dasha,
            chart_data=chart_context,
            use_ai=True  # Enable AI personalization
        )

        # Detect yogas
        yogas = self._detect_vedic_yogas(planets, asc_sign)

        # Calculate ALL divisional charts (D2-D60 Shodashvarga system)
        print("🔢 Calculating all divisional charts (D2-D60)...")
        divisional_charts = divisional_charts_service.calculate_all_divisional_charts(
            planets,
            {
                "sign": self.SIGNS[asc_sign],
                "sign_num": asc_sign,
                "degree": asc_degree,
                "longitude": asc_sidereal
            },
            priority="all"  # Calculate all 16 divisional charts (complete Shodashvarga)
        )

        # Calculate Vimshopaka Bala (composite planetary strength)
        print("💪 Calculating Vimshopaka Bala (planetary strengths)...")
        vimshopaka_bala = divisional_charts_service.calculate_vimshopaka_bala(
            planets,
            divisional_charts
        )

        # Detect doshas
        print("⚠️  Detecting doshas...")
        doshas = dosha_detection_service.detect_all_doshas(
            planets,
            {
                "sign_num": asc_sign,
                "degree": asc_degree,
                "longitude": asc_sidereal
            }
        )

        # Calculate current transits
        print("🪐 Calculating current transits...")
        moon_sign = planets["Moon"]["sign_num"]
        current_transits = transit_service.get_current_transits(
            moon_sign,
            asc_sign
        )

        # Calculate Sade Sati
        print("🔮 Calculating Sade Sati...")
        sade_sati = transit_service.calculate_sade_sati(moon_sign)

        print("✅ All calculations complete!")

        return {
            "basic_info": {
                "name": name,
                "birth_datetime": birth_datetime.isoformat(),
                "birth_datetime_utc": birth_datetime_utc.isoformat(),
                "location": {
                    "city": city,
                    "latitude": latitude,
                    "longitude": longitude,
                    "timezone": timezone_str
                },
                "ayanamsa": round(ayanamsa, 6),
                "ayanamsa_name": "Lahiri"
            },
            "ascendant": {
                "sign": self.SIGNS[asc_sign],
                "sign_num": asc_sign + 1,  # Convert 0-indexed (0-11) to 1-indexed (1-12)
                "degree": round(asc_degree, 6),
                "longitude": round(asc_sidereal, 6),
                "house": 1
            },
            "planets": planets,
            "houses": houses,
            "dasha": dasha,
            "yogas": yogas,
            "divisional_charts": divisional_charts,
            "vimshopaka_bala": vimshopaka_bala,
            "doshas": doshas,
            "transits": current_transits,
            "sade_sati": sade_sati,
            "chart_type": "D1",
            "calculation_method": "Swiss Ephemeris with Lahiri Ayanamsa",
            "house_system": "Whole Sign (Vedic Standard)"
        }

    def _calculate_planets(self, jd: float, ayanamsa: float, asc_sign: int) -> Dict[str, Any]:
        """Calculate accurate planetary positions using Swiss Ephemeris"""

        planets_data = {}

        for planet_name, planet_id in self.PLANETS.items():
            if planet_name == "Ketu":
                # Ketu is 180° opposite to Rahu
                continue

            # Calculate planet position
            result = swe.calc_ut(jd, planet_id, swe.FLG_SWIEPH)
            tropical_long = result[0][0]
            speed = result[0][3]

            # Convert to sidereal
            sidereal_long = (tropical_long - ayanamsa) % 360
            sign = int(sidereal_long / 30)
            degree = sidereal_long % 30

            # Check if retrograde (negative speed)
            is_retrograde = speed < 0

            planets_data[planet_name] = {
                "sign": self.SIGNS[sign],
                "sign_num": sign + 1,  # Convert 0-indexed (0-11) to 1-indexed (1-12)
                "degree": round(degree, 6),
                "longitude": round(sidereal_long, 6),
                "speed": round(speed, 6),
                "retrograde": is_retrograde,
                "house": 0  # Will be calculated later
            }

        # Calculate Ketu (180° from Rahu)
        if "Rahu" in planets_data:
            rahu_long = planets_data["Rahu"]["longitude"]
            ketu_long = (rahu_long + 180) % 360
            ketu_sign = int(ketu_long / 30)
            ketu_degree = ketu_long % 30

            planets_data["Ketu"] = {
                "sign": self.SIGNS[ketu_sign],
                "sign_num": ketu_sign + 1,  # Convert 0-indexed (0-11) to 1-indexed (1-12)
                "degree": round(ketu_degree, 6),
                "longitude": round(ketu_long, 6),
                "speed": -planets_data["Rahu"]["speed"],  # Opposite speed
                "retrograde": True,  # Always retrograde
                "house": 0
            }

        return planets_data

    def _calculate_whole_sign_houses(self, asc_sign: int) -> List[Dict[str, Any]]:
        """
        Calculate Whole Sign houses (authentic Vedic method)
        In Whole Sign system, each house = one complete sign
        """

        houses = []
        for i in range(12):
            house_sign = (asc_sign + i) % 12
            houses.append({
                "house_num": i + 1,
                "sign": self.SIGNS[house_sign],
                "sign_num": house_sign + 1,  # Convert 0-indexed (0-11) to 1-indexed (1-12)
                "start_degree": 0.0,
                "end_degree": 30.0
            })

        return houses

    def _assign_houses_to_planets(self, planets: Dict, asc_sign: int) -> Dict:
        """
        Assign house positions to planets using Whole Sign system

        Args:
            planets: Dictionary with planet data (sign_num is 1-indexed after recent fix)
            asc_sign: Ascendant sign (0-indexed internal variable)
        """

        for planet_name, planet_data in planets.items():
            planet_sign = planet_data["sign_num"]  # Now 1-indexed (1-12)

            # Convert asc_sign from 0-indexed to 1-indexed for consistent calculation
            asc_sign_1indexed = asc_sign + 1

            # In Whole Sign: house = how many signs from ascendant
            # Both values are now 1-indexed (1-12)
            house_num = ((planet_sign - asc_sign_1indexed) % 12) + 1
            planet_data["house"] = house_num

        return planets

    def _add_nakshatras(self, planets: Dict) -> Dict:
        """Add nakshatra information for each planet"""

        for planet_name, planet_data in planets.items():
            longitude = planet_data["longitude"]

            # Each nakshatra is 13°20' (13.333333°)
            nakshatra_num = int(longitude / 13.333333)
            nakshatra_lord_idx = nakshatra_num % 9

            # Pada (quarter) within nakshatra
            pada = int((longitude % 13.333333) / 3.333333) + 1

            planet_data["nakshatra"] = {
                "name": self.NAKSHATRAS[nakshatra_num],
                "number": nakshatra_num + 1,
                "lord": self.NAKSHATRA_LORDS[nakshatra_lord_idx],
                "pada": pada
            }

        return planets

    def _calculate_vimshottari_dasha(self, moon_data: Dict, birth_datetime: datetime) -> Dict[str, Any]:
        """
        Calculate Vimshottari Dasha with correct formula
        Based on Moon's nakshatra position at birth
        """

        moon_longitude = moon_data["longitude"]

        # Determine current nakshatra and lord
        nakshatra_num = int(moon_longitude / 13.333333)
        nakshatra_lord_idx = nakshatra_num % 9
        current_lord = self.NAKSHATRA_LORDS[nakshatra_lord_idx]

        # Calculate how much of the nakshatra has been traversed
        traversed_in_nakshatra = (moon_longitude % 13.333333) / 13.333333

        # Calculate remaining period of current Mahadasha
        total_years = self.DASHA_YEARS[current_lord]
        elapsed_years = traversed_in_nakshatra * total_years
        remaining_years = total_years - elapsed_years

        # Generate Mahadasha sequence
        mahadashas = []
        current_date = birth_datetime
        lord_idx = nakshatra_lord_idx

        # Add remaining portion of birth Mahadasha
        end_date = current_date + timedelta(days=remaining_years * 365.25)
        mahadashas.append({
            "planet": current_lord,
            "start_date": current_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "years": round(remaining_years, 2),
            "months": int(remaining_years * 12),
            "days": int(remaining_years * 365.25)
        })
        current_date = end_date

        # Add next 8 Mahadashas (complete 120-year cycle)
        for i in range(1, 9):
            lord_idx = (nakshatra_lord_idx + i) % 9
            lord = self.NAKSHATRA_LORDS[lord_idx]
            years = self.DASHA_YEARS[lord]

            end_date = current_date + timedelta(days=years * 365.25)
            mahadashas.append({
                "planet": lord,
                "start_date": current_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "years": years,
                "months": years * 12,
                "days": int(years * 365.25)
            })
            current_date = end_date

        # Find currently active Mahadasha (based on today's date)
        today = datetime.now()
        current_maha_idx = 0
        for idx, maha in enumerate(mahadashas):
            start = datetime.strptime(maha["start_date"], "%Y-%m-%d")
            end = datetime.strptime(maha["end_date"], "%Y-%m-%d")
            if start <= today <= end:
                current_maha_idx = idx
                break

        # Calculate Antardashas for the CURRENT Mahadasha (not birth mahadasha)
        current_maha = mahadashas[current_maha_idx]
        antardashas = self._calculate_antardashas(
            current_maha["planet"],
            datetime.strptime(current_maha["start_date"], "%Y-%m-%d"),
            current_maha["years"]
        )

        # Find currently active Antardasha within current Mahadasha
        current_antar = None
        for antar in antardashas:
            start = datetime.strptime(antar["start_date"], "%Y-%m-%d")
            end = datetime.strptime(antar["end_date"], "%Y-%m-%d")
            if start <= today <= end:
                current_antar = antar
                break

        return {
            "current_mahadasha": {
                "planet": current_maha["planet"],
                "start_date": current_maha["start_date"],
                "end_date": current_maha["end_date"],
                "remaining_years": round(current_maha["years"], 2)
            },
            "current_antardasha": current_antar if current_antar else None,
            "mahadashas": mahadashas,
            "antardashas": antardashas,
            "total_cycle_years": 120,
            "calculation_method": "Vimshottari Dasha System"
        }

    def _calculate_antardashas(self, maha_lord: str, start_date: datetime, maha_years: float) -> List[Dict]:
        """
        Calculate Antardashas (sub-periods) using correct Vedic formula
        Formula: Antardasha period = (Maha lord years × Antar lord years) / 120
        """

        antardashas = []
        current_date = start_date

        # Find starting index
        start_idx = self.NAKSHATRA_LORDS.index(maha_lord)

        for i in range(9):
            antar_lord = self.NAKSHATRA_LORDS[(start_idx + i) % 9]

            # Correct Vedic formula
            antar_years = (self.DASHA_YEARS[maha_lord] * self.DASHA_YEARS[antar_lord]) / 120
            antar_days = antar_years * 365.25

            end_date = current_date + timedelta(days=antar_days)

            antardashas.append({
                "planet": antar_lord,
                "start_date": current_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "years": round(antar_years, 3),
                "months": round(antar_years * 12, 1),
                "days": int(antar_days)
            })

            current_date = end_date

        return antardashas

    def calculate_navamsa(
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
        Calculate Navamsa chart (D9) - 9th divisional chart
        Used for marriage, dharma, and spiritual analysis
        """

        # First get D1 chart
        d1_chart = self.calculate_birth_chart(
            name, birth_date, birth_time, latitude, longitude, timezone_str, city
        )

        # Calculate Navamsa positions for all planets
        navamsa_planets = {}

        # Calculate Navamsa ascendant
        asc_long = d1_chart["ascendant"]["longitude"]
        navamsa_asc = self._get_navamsa_position(asc_long)
        navamsa_asc_sign = navamsa_asc["sign_num"]

        # Calculate Navamsa for each planet
        for planet_name, planet_data in d1_chart["planets"].items():
            navamsa_pos = self._get_navamsa_position(planet_data["longitude"])

            # Calculate house in Navamsa chart
            navamsa_house = ((navamsa_pos["sign_num"] - navamsa_asc_sign) % 12) + 1

            navamsa_planets[planet_name] = {
                **navamsa_pos,
                "house": navamsa_house,
                "retrograde": planet_data["retrograde"],
                "d1_sign": planet_data["sign"],
                "nakshatra": planet_data["nakshatra"]
            }

        # Generate Navamsa houses
        # Note: _calculate_whole_sign_houses expects 0-indexed asc_sign
        navamsa_asc_sign_0indexed = navamsa_asc_sign - 1
        navamsa_houses = self._calculate_whole_sign_houses(navamsa_asc_sign_0indexed)

        return {
            "basic_info": d1_chart["basic_info"],
            "ascendant": {
                **navamsa_asc,
                "house": 1
            },
            "planets": navamsa_planets,
            "houses": navamsa_houses,
            "dasha": d1_chart["dasha"],
            "chart_type": "D9",
            "calculation_method": "Swiss Ephemeris with Lahiri Ayanamsa",
            "house_system": "Whole Sign (Vedic Standard)",
            "note": "Navamsa - Marriage, Dharma, and Spiritual Potential"
        }

    def _get_navamsa_position(self, longitude: float) -> Dict[str, Any]:
        """
        Calculate Navamsa position from Rashi position
        Correct Vedic formula for D9
        """

        # Determine sign and position within sign
        rashi_sign = int(longitude / 30)
        degree_in_sign = longitude % 30

        # Each navamsa is 3°20' (3.333333°)
        navamsa_in_sign = int(degree_in_sign / 3.333333)

        # Navamsa sign calculation
        # Formula: (Rashi × 9 + Navamsa_in_sign) mod 12
        navamsa_sign = ((rashi_sign * 9) + navamsa_in_sign) % 12

        # Degree within navamsa sign
        navamsa_degree = (degree_in_sign % 3.333333) * 9
        navamsa_longitude = (navamsa_sign * 30) + navamsa_degree

        return {
            "sign": self.SIGNS[navamsa_sign],
            "sign_num": navamsa_sign + 1,  # Convert 0-indexed (0-11) to 1-indexed (1-12)
            "degree": round(navamsa_degree, 6),
            "longitude": round(navamsa_longitude, 6),
            "navamsa_number": navamsa_in_sign + 1
        }

    def _detect_vedic_yogas(self, planets: Dict, asc_sign: int) -> List[Dict[str, str]]:
        """Detect important Vedic yogas based on classical principles"""

        yogas = []

        # 1. Gaja Kesari Yoga: Jupiter in Kendra (1,4,7,10) from Moon
        moon_house = planets["Moon"]["house"]
        jupiter_house = planets["Jupiter"]["house"]
        house_diff = (jupiter_house - moon_house) % 12

        if house_diff in [0, 3, 6, 9]:  # Kendra positions
            yogas.append({
                "name": "Gaja Kesari Yoga",
                "description": "Jupiter in angle from Moon - brings wisdom, prosperity, fame, and good character",
                "strength": "Strong",
                "category": "Wealth & Wisdom"
            })

        # 2. Raj Yoga: Kendra and Trikona lords in mutual relationship
        # Simplified: Jupiter and Sun in good houses
        kendra_houses = [1, 4, 7, 10]
        if jupiter_house in kendra_houses and planets["Sun"]["house"] in kendra_houses:
            yogas.append({
                "name": "Raj Yoga",
                "description": "Combination indicating authority, power, and leadership qualities",
                "strength": "Strong",
                "category": "Power & Status"
            })

        # 3. Dhana Yoga: 2nd, 5th, 9th, 11th house connections
        dhana_houses = [2, 5, 9, 11]
        beneficial_planets_in_dhana = sum(1 for p in ["Jupiter", "Venus", "Mercury"]
                                          if planets[p]["house"] in dhana_houses)

        if beneficial_planets_in_dhana >= 2:
            yogas.append({
                "name": "Dhana Yoga",
                "description": "Wealth combination - beneficial planets in wealth houses",
                "strength": "Medium",
                "category": "Wealth"
            })

        # 4. Extended Yogas: Add 25+ additional classical yogas
        try:
            extended_yogas = extended_yoga_service.detect_extended_yogas(planets)
            yogas.extend(extended_yogas)
        except Exception as e:
            print(f"Warning: Extended yoga detection failed: {e}")

        # If no major yogas found
        if not yogas:
            yogas.append({
                "name": "Standard Chart",
                "description": "Chart shows balanced planetary influences. Consult detailed analysis for specific combinations",
                "strength": "Variable",
                "category": "General"
            })

        # Remove duplicates (keep first occurrence)
        seen = set()
        unique_yogas = []
        for yoga in yogas:
            if yoga["name"] not in seen:
                seen.add(yoga["name"])
                unique_yogas.append(yoga)

        return unique_yogas

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
        Calculate Moon chart (Chandra Kundali) - chart with Moon's sign as 1st house
        Used for emotional nature, mind, mother, and general life fortune

        In Moon chart, the sign occupied by Moon becomes the ascendant (1st house),
        and all planets are placed relative to the Moon's position.
        """

        # First calculate D1 chart to get all planetary positions
        d1_chart = self.calculate_birth_chart(
            name, birth_date, birth_time, latitude, longitude, timezone_str, city
        )

        # Get Moon's position to use as ascendant
        moon_data = d1_chart["planets"]["Moon"]
        moon_sign = moon_data["sign_num"]
        moon_degree = moon_data["degree"]
        moon_longitude = moon_data["longitude"]

        # Recalculate all planets' house positions relative to Moon's sign
        moon_chart_planets = {}

        for planet_name, planet_data in d1_chart["planets"].items():
            planet_sign = planet_data["sign_num"]

            # Calculate house position from Moon's sign
            # Moon's sign becomes house 1
            house_from_moon = ((planet_sign - moon_sign) % 12) + 1

            moon_chart_planets[planet_name] = {
                "sign": planet_data["sign"],
                "sign_num": planet_data["sign_num"],
                "degree": planet_data["degree"],
                "longitude": planet_data["longitude"],
                "speed": planet_data.get("speed", 0),
                "retrograde": planet_data["retrograde"],
                "house": house_from_moon,
                "nakshatra": planet_data["nakshatra"],
                "d1_house": planet_data["house"]  # Original house from birth chart
            }

        # Generate Moon chart houses (starting from Moon's sign)
        # Note: _calculate_whole_sign_houses expects 0-indexed asc_sign
        moon_sign_0indexed = moon_sign - 1
        moon_chart_houses = self._calculate_whole_sign_houses(moon_sign_0indexed)

        # Detect yogas from Moon's perspective
        moon_chart_yogas = self._detect_vedic_yogas(moon_chart_planets, moon_sign_0indexed)

        return {
            "basic_info": d1_chart["basic_info"],
            "ascendant": {
                "sign": self.SIGNS[moon_sign],
                "sign_num": moon_sign,
                "degree": round(moon_degree, 6),
                "longitude": round(moon_longitude, 6),
                "house": 1,
                "note": "Moon's position as ascendant"
            },
            "planets": moon_chart_planets,
            "houses": moon_chart_houses,
            "dasha": d1_chart["dasha"],
            "yogas": moon_chart_yogas,
            "chart_type": "Moon",
            "calculation_method": "Swiss Ephemeris with Lahiri Ayanamsa",
            "house_system": "Whole Sign from Moon (Chandra Kundali)",
            "note": "Moon chart shows emotional nature, mind, and life fortune from lunar perspective"
        }


# Singleton instance
accurate_vedic_astrology = AccurateVedicAstrology()
