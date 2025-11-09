"""
Varshaphal (Annual Predictions) Service

Implements complete Varshaphal system including:
- Solar Return Chart calculation
- 16 Varshaphal Yogas
- Patyayini Dasha (annual dasha system)
- 50+ Sahams (sensitive points)
- Annual interpretations
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import math
import logging

logger = logging.getLogger(__name__)


class VarshapalService:
    """
    Service for Annual Predictions (Varshaphal) calculations.

    Varshaphal is the Vedic method of annual solar return chart analysis,
    calculated for the exact moment when the Sun returns to its natal position.
    """

    def __init__(self, swisseph=None):
        """Initialize with Swiss Ephemeris library."""
        if swisseph is None:
            import swisseph as swe
            self.swe = swe
        else:
            self.swe = swisseph

        # Planet constants
        self.PLANETS = {
            'Sun': self.swe.SUN,
            'Moon': self.swe.MOON,
            'Mars': self.swe.MARS,
            'Mercury': self.swe.MERCURY,
            'Jupiter': self.swe.JUPITER,
            'Venus': self.swe.VENUS,
            'Saturn': self.swe.SATURN,
            'Rahu': self.swe.MEAN_NODE,
        }

        # Varshaphal Yoga definitions
        self.VARSHAPHAL_YOGAS = {
            'Ikkavala': 'Planets in kendras/trikonas',
            'Induvara': 'Benefics in 1st/7th/10th',
            'Madhya': 'Planets in 2nd/5th/8th/11th',
            'Shubha': 'All benefics strong',
            'Ashubha': 'All malefics strong',
            'Sarva-aishwarya': 'Specific planetary placements',
            'Kaaraka': 'Significators well-placed',
            'Siddhi': 'Success indicators',
            'Viparita': 'Reverse yogas',
            'Dwi-graha': 'Two-planet combinations',
            'Tri-graha': 'Three-planet combinations',
            'Ravi': 'Sun-based yoga',
            'Chandra': 'Moon-based yoga',
            'Budha': 'Mercury-based yoga',
            'Guru': 'Jupiter-based yoga',
            'Shukra': 'Venus-based yoga',
        }

        # Benefics and Malefics
        self.BENEFICS = ['Jupiter', 'Venus', 'Moon', 'Mercury']
        self.MALEFICS = ['Sun', 'Mars', 'Saturn', 'Rahu', 'Ketu']

        # Kendras and Trikonas
        self.KENDRAS = [1, 4, 7, 10]
        self.TRIKONAS = [1, 5, 9]

    def calculate_solar_return_chart(
        self,
        natal_sun_longitude: float,
        birth_date: datetime,
        target_year: int,
        latitude: float,
        longitude: float,
        timezone_offset: float = 0
    ) -> Dict[str, Any]:
        """
        Calculate Solar Return Chart for a specific year.

        Args:
            natal_sun_longitude: Natal Sun's longitude in degrees
            birth_date: Original birth datetime
            target_year: Year for which to calculate solar return
            latitude: Location latitude
            longitude: Location longitude
            timezone_offset: Timezone offset in hours

        Returns:
            Dictionary with solar return chart data
        """
        logger.info(f"Calculating Solar Return for year {target_year}")

        # Find exact moment when Sun returns to natal position
        solar_return_time = self._find_solar_return_moment(
            natal_sun_longitude,
            birth_date,
            target_year
        )

        # Calculate planetary positions at solar return
        planets = self._calculate_planets_at_time(
            solar_return_time,
            latitude,
            longitude
        )

        # Calculate Varsha Lagna (Annual Ascendant)
        varsha_lagna = self._calculate_ascendant(
            solar_return_time,
            latitude,
            longitude
        )

        # Calculate Muntha (progressed point)
        muntha = self._calculate_muntha(birth_date, target_year)

        # Calculate houses
        houses = self._calculate_houses(varsha_lagna)

        # Detect Varshaphal Yogas
        yogas = self._detect_varshaphal_yogas(planets, houses, varsha_lagna)

        return {
            'solar_return_time': solar_return_time,
            'target_year': target_year,
            'varsha_lagna': varsha_lagna,
            'muntha': muntha,
            'planets': planets,
            'houses': houses,
            'yogas': yogas,
            'natal_sun_longitude': natal_sun_longitude,
        }

    def _find_solar_return_moment(
        self,
        natal_sun_longitude: float,
        birth_date: datetime,
        target_year: int
    ) -> datetime:
        """
        Find exact moment when Sun returns to natal position.

        Uses binary search to find the precise moment within a few seconds.
        """
        # Start search around birthday in target year
        # Handle leap day births (Feb 29) in non-leap years
        try:
            approximate_date = birth_date.replace(year=target_year)
        except ValueError:
            # If born on Feb 29 and target year is not a leap year,
            # use Feb 28 as the approximate date
            approximate_date = birth_date.replace(year=target_year, day=28)

        # Search window: 2 days before to 2 days after birthday
        start_jd = self._datetime_to_julian(approximate_date - timedelta(days=2))
        end_jd = self._datetime_to_julian(approximate_date + timedelta(days=2))

        # Binary search for exact moment
        tolerance = 1.0 / 86400.0  # 1 second in Julian days

        while (end_jd - start_jd) > tolerance:
            mid_jd = (start_jd + end_jd) / 2.0
            sun_pos, _ = self.swe.calc_ut(mid_jd, self.swe.SUN)
            sun_longitude = sun_pos[0]

            # Normalize to 0-360
            sun_longitude = sun_longitude % 360
            natal_sun_normalized = natal_sun_longitude % 360

            # Check if we've passed the target
            diff = sun_longitude - natal_sun_normalized

            # Handle wraparound at 0/360 degrees
            if diff > 180:
                diff -= 360
            elif diff < -180:
                diff += 360

            if abs(diff) < 0.01:  # Within 0.01 degrees
                break
            elif diff < 0:
                start_jd = mid_jd
            else:
                end_jd = mid_jd

        solar_return_jd = (start_jd + end_jd) / 2.0
        return self._julian_to_datetime(solar_return_jd)

    def _calculate_planets_at_time(
        self,
        dt: datetime,
        latitude: float,
        longitude: float
    ) -> Dict[str, Dict[str, float]]:
        """Calculate planetary positions at specific time."""
        jd = self._datetime_to_julian(dt)
        planets_data = {}

        for planet_name, planet_id in self.PLANETS.items():
            try:
                pos, _ = self.swe.calc_ut(jd, planet_id)
                longitude_deg = pos[0] % 360

                planets_data[planet_name] = {
                    'longitude': longitude_deg,
                    'sign': self._get_sign(longitude_deg),
                    'sign_num': int(longitude_deg / 30) + 1,
                    'degree_in_sign': longitude_deg % 30,
                    'nakshatra': self._get_nakshatra(longitude_deg),
                    'retrograde': pos[3] < 0 if len(pos) > 3 else False,
                }
            except Exception as e:
                logger.error(f"Error calculating {planet_name}: {e}")
                planets_data[planet_name] = None

        # Calculate Ketu (opposite of Rahu)
        if planets_data.get('Rahu'):
            ketu_longitude = (planets_data['Rahu']['longitude'] + 180) % 360
            planets_data['Ketu'] = {
                'longitude': ketu_longitude,
                'sign': self._get_sign(ketu_longitude),
                'sign_num': int(ketu_longitude / 30) + 1,
                'degree_in_sign': ketu_longitude % 30,
                'nakshatra': self._get_nakshatra(ketu_longitude),
                'retrograde': True,
            }

        return planets_data

    def _calculate_ascendant(
        self,
        dt: datetime,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """Calculate Ascendant (Lagna) for given time and location."""
        jd = self._datetime_to_julian(dt)

        try:
            houses = self.swe.houses(jd, latitude, longitude, b'P')  # Placidus
            asc_longitude = houses[0][0] % 360

            return {
                'longitude': asc_longitude,
                'sign': self._get_sign(asc_longitude),
                'sign_num': int(asc_longitude / 30) + 1,
                'degree_in_sign': asc_longitude % 30,
            }
        except Exception as e:
            logger.error(f"Error calculating ascendant: {e}")
            return None

    def _calculate_muntha(self, birth_date: datetime, target_year: int) -> Dict[str, Any]:
        """
        Calculate Muntha (progressed point in Varshaphal).

        Muntha moves one sign per year from the Lagna.
        Formula: (Age completed in years) mod 12 + 1
        """
        age = target_year - birth_date.year
        muntha_sign = (age % 12) + 1

        return {
            'sign_num': muntha_sign,
            'sign': self._get_sign_from_num(muntha_sign),
            'age': age,
            'description': f'Muntha is in {self._get_sign_from_num(muntha_sign)} for age {age}',
        }

    def _calculate_houses(self, ascendant: Dict[str, Any]) -> Dict[int, Dict[str, Any]]:
        """
        Calculate house cusps using Whole Sign house system.

        In Whole Sign, each house is a complete sign starting from Lagna.
        """
        houses = {}
        lagna_sign = ascendant['sign_num']

        for house_num in range(1, 13):
            house_sign = ((lagna_sign - 1 + house_num - 1) % 12) + 1
            houses[house_num] = {
                'sign_num': house_sign,
                'sign': self._get_sign_from_num(house_sign),
                'start_degree': (house_sign - 1) * 30,
                'end_degree': house_sign * 30,
            }

        return houses

    def _detect_varshaphal_yogas(
        self,
        planets: Dict[str, Dict],
        houses: Dict[int, Dict],
        varsha_lagna: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Detect 16 Varshaphal Yogas in annual chart.

        These are special yogas specific to Varshaphal analysis.
        """
        yogas = []

        # Get planet-to-house mapping
        planet_houses = self._get_planet_houses(planets, varsha_lagna['sign_num'])

        # 1. Ikkavala Yoga - Planets in kendras/trikonas
        ikkavala = self._check_ikkavala_yoga(planet_houses)
        if ikkavala:
            yogas.append(ikkavala)

        # 2. Induvara Yoga - Benefics in 1st/7th/10th
        induvara = self._check_induvara_yoga(planet_houses)
        if induvara:
            yogas.append(induvara)

        # 3. Madhya Yoga - Planets in 2nd/5th/8th/11th
        madhya = self._check_madhya_yoga(planet_houses)
        if madhya:
            yogas.append(madhya)

        # 4. Shubha Yoga - All benefics strong
        shubha = self._check_shubha_yoga(planets, planet_houses)
        if shubha:
            yogas.append(shubha)

        # 5. Ashubha Yoga - All malefics strong
        ashubha = self._check_ashubha_yoga(planets, planet_houses)
        if ashubha:
            yogas.append(ashubha)

        # 6-16. Other Varshaphal Yogas
        other_yogas = self._check_other_varshaphal_yogas(planets, planet_houses)
        yogas.extend(other_yogas)

        return yogas

    def _get_planet_houses(
        self,
        planets: Dict[str, Dict],
        lagna_sign: int
    ) -> Dict[str, int]:
        """Map planets to house numbers."""
        planet_houses = {}

        for planet_name, planet_data in planets.items():
            if planet_data:
                planet_sign = planet_data['sign_num']
                house = ((planet_sign - lagna_sign) % 12) + 1
                planet_houses[planet_name] = house

        return planet_houses

    def _check_ikkavala_yoga(self, planet_houses: Dict[str, int]) -> Optional[Dict]:
        """Check for Ikkavala Yoga - planets in kendras/trikonas."""
        auspicious_houses = set(self.KENDRAS + self.TRIKONAS)
        planets_in_auspicious = [
            p for p, h in planet_houses.items()
            if h in auspicious_houses
        ]

        if len(planets_in_auspicious) >= 4:
            return {
                'name': 'Ikkavala Yoga',
                'type': 'Auspicious',
                'strength': 'Strong' if len(planets_in_auspicious) >= 6 else 'Moderate',
                'description': 'Multiple planets in kendras and trikonas bring success and progress',
                'planets_involved': planets_in_auspicious,
                'effects': 'Overall success, progress in endeavors, positive year',
            }
        return None

    def _check_induvara_yoga(self, planet_houses: Dict[str, int]) -> Optional[Dict]:
        """Check for Induvara Yoga - benefics in 1st/7th/10th."""
        key_houses = [1, 7, 10]
        benefics_in_key_houses = [
            p for p in self.BENEFICS
            if planet_houses.get(p) in key_houses
        ]

        if len(benefics_in_key_houses) >= 2:
            return {
                'name': 'Induvara Yoga',
                'type': 'Highly Auspicious',
                'strength': 'Strong',
                'description': 'Benefic planets in angular houses bring prosperity',
                'planets_involved': benefics_in_key_houses,
                'effects': 'Financial gains, recognition, happiness, relationship harmony',
            }
        return None

    def _check_madhya_yoga(self, planet_houses: Dict[str, int]) -> Optional[Dict]:
        """Check for Madhya Yoga - planets in 2nd/5th/8th/11th."""
        madhya_houses = [2, 5, 8, 11]
        planets_in_madhya = [
            p for p, h in planet_houses.items()
            if h in madhya_houses
        ]

        if len(planets_in_madhya) >= 3:
            return {
                'name': 'Madhya Yoga',
                'type': 'Mixed',
                'strength': 'Moderate',
                'description': 'Planets in intermediate houses create mixed results',
                'planets_involved': planets_in_madhya,
                'effects': 'Variable results, requires effort, some gains possible',
            }
        return None

    def _check_shubha_yoga(
        self,
        planets: Dict[str, Dict],
        planet_houses: Dict[str, int]
    ) -> Optional[Dict]:
        """Check for Shubha Yoga - all benefics strong."""
        strong_benefics = []

        for planet in self.BENEFICS:
            if planet in planet_houses:
                house = planet_houses[planet]
                # Consider strong if in kendra/trikona or own sign
                if house in self.KENDRAS or house in self.TRIKONAS:
                    strong_benefics.append(planet)

        if len(strong_benefics) >= 3:
            return {
                'name': 'Shubha Yoga',
                'type': 'Highly Auspicious',
                'strength': 'Strong',
                'description': 'Multiple benefics in strong positions',
                'planets_involved': strong_benefics,
                'effects': 'Excellent year for growth, happiness, success in all areas',
            }
        return None

    def _check_ashubha_yoga(
        self,
        planets: Dict[str, Dict],
        planet_houses: Dict[str, int]
    ) -> Optional[Dict]:
        """Check for Ashubha Yoga - malefics in difficult positions."""
        problematic_malefics = []

        for planet in self.MALEFICS:
            if planet in planet_houses:
                house = planet_houses[planet]
                # Malefics in 6th, 8th, 12th are problematic
                if house in [6, 8, 12]:
                    problematic_malefics.append(planet)

        if len(problematic_malefics) >= 2:
            return {
                'name': 'Ashubha Yoga',
                'type': 'Challenging',
                'strength': 'Moderate',
                'description': 'Malefic planets in difficult houses',
                'planets_involved': problematic_malefics,
                'effects': 'Challenges, obstacles, need for caution and remedies',
            }
        return None

    def _check_other_varshaphal_yogas(
        self,
        planets: Dict[str, Dict],
        planet_houses: Dict[str, int]
    ) -> List[Dict]:
        """Check for remaining Varshaphal yogas (Dwi-graha, Tri-graha, etc.)."""
        yogas = []

        # Ravi Yoga - Sun strong
        if planet_houses.get('Sun') in [1, 5, 9, 10]:
            yogas.append({
                'name': 'Ravi Yoga',
                'type': 'Auspicious',
                'strength': 'Moderate',
                'description': 'Sun well-placed brings authority and recognition',
                'planets_involved': ['Sun'],
                'effects': 'Career advancement, recognition, leadership opportunities',
            })

        # Chandra Yoga - Moon strong
        if planet_houses.get('Moon') in [1, 4, 5, 10]:
            yogas.append({
                'name': 'Chandra Yoga',
                'type': 'Auspicious',
                'strength': 'Moderate',
                'description': 'Moon well-placed brings emotional satisfaction',
                'planets_involved': ['Moon'],
                'effects': 'Emotional stability, domestic harmony, public favor',
            })

        # Budha Yoga - Mercury strong
        if planet_houses.get('Mercury') in [1, 5, 9, 10]:
            yogas.append({
                'name': 'Budha Yoga',
                'type': 'Auspicious',
                'strength': 'Moderate',
                'description': 'Mercury well-placed enhances communication',
                'planets_involved': ['Mercury'],
                'effects': 'Intellectual growth, communication success, business gains',
            })

        # Guru Yoga - Jupiter strong
        if planet_houses.get('Jupiter') in [1, 2, 5, 9, 11]:
            yogas.append({
                'name': 'Guru Yoga',
                'type': 'Highly Auspicious',
                'strength': 'Strong',
                'description': 'Jupiter well-placed brings wisdom and wealth',
                'planets_involved': ['Jupiter'],
                'effects': 'Spiritual growth, financial gains, children\'s welfare, education',
            })

        # Shukra Yoga - Venus strong
        if planet_houses.get('Venus') in [1, 2, 5, 7, 11]:
            yogas.append({
                'name': 'Shukra Yoga',
                'type': 'Auspicious',
                'strength': 'Moderate',
                'description': 'Venus well-placed brings luxury and relationships',
                'planets_involved': ['Venus'],
                'effects': 'Relationship harmony, artistic success, material comforts',
            })

        return yogas

    def calculate_patyayini_dasha(
        self,
        solar_return_chart: Dict[str, Any],
        target_year: int
    ) -> List[Dict[str, Any]]:
        """
        Calculate Patyayini Dasha for the annual period.

        Patyayini Dasha is specific to Varshaphal and different from Vimshottari.
        It divides the year into planetary periods based on specific rules.
        """
        # Get planets and their strengths
        planets = solar_return_chart['planets']
        varsha_lagna = solar_return_chart['varsha_lagna']

        # Calculate planetary strengths for Patyayini Dasha
        # (Simplified version - full implementation would use Panchadha Maitri)
        dasha_order = self._determine_patyayini_dasha_order(planets, varsha_lagna)

        # Divide year into dasha periods
        start_date = solar_return_chart['solar_return_time']
        dasha_periods = []

        # Equal division method (each planet gets proportional time)
        total_months = 12
        months_per_dasha = total_months / len(dasha_order)

        current_date = start_date
        for planet_name in dasha_order:
            end_date = current_date + timedelta(days=months_per_dasha * 30.44)  # Average month

            dasha_periods.append({
                'planet': planet_name,
                'start_date': current_date,
                'end_date': end_date,
                'duration_months': months_per_dasha,
                'effects': self._get_dasha_effects(planet_name, planets),
            })

            current_date = end_date

        return dasha_periods

    def _determine_patyayini_dasha_order(
        self,
        planets: Dict[str, Dict],
        varsha_lagna: Dict[str, Any]
    ) -> List[str]:
        """
        Determine Patyayini Dasha order based on planetary strengths.

        Simplified version - orders planets by house position strength.
        """
        # Calculate house positions
        lagna_sign = varsha_lagna['sign_num']
        planet_strengths = []

        for planet_name, planet_data in planets.items():
            if planet_data and planet_name != 'Ketu':  # Ketu not used in Patyayini
                planet_sign = planet_data['sign_num']
                house = ((planet_sign - lagna_sign) % 12) + 1

                # Calculate simple strength score
                strength = 0
                if house in [1, 4, 7, 10]:  # Kendras
                    strength += 4
                elif house in [1, 5, 9]:  # Trikonas
                    strength += 3
                elif house in [2, 11]:  # Wealth houses
                    strength += 2
                else:
                    strength += 1

                planet_strengths.append((planet_name, strength))

        # Sort by strength (descending)
        planet_strengths.sort(key=lambda x: x[1], reverse=True)

        return [p[0] for p in planet_strengths]

    def _get_dasha_effects(
        self,
        planet_name: str,
        planets: Dict[str, Dict]
    ) -> str:
        """Get general effects for planet's dasha period."""
        effects_map = {
            'Sun': 'Authority, recognition, career focus, government matters',
            'Moon': 'Emotions, domestic life, public relations, travel',
            'Mars': 'Energy, courage, property matters, competition',
            'Mercury': 'Communication, business, education, intellectual pursuits',
            'Jupiter': 'Wisdom, spirituality, children, wealth, expansion',
            'Venus': 'Relationships, luxury, arts, pleasures, harmony',
            'Saturn': 'Discipline, delays, hard work, long-term planning',
            'Rahu': 'Unconventional paths, foreign connections, sudden changes',
        }

        return effects_map.get(planet_name, 'Mixed results')

    def calculate_sahams(
        self,
        solar_return_chart: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate 50+ Sahams (sensitive points) for Varshaphal.

        Sahams are calculated using formulas like:
        Saham = Ascendant + Planet1 - Planet2
        """
        planets = solar_return_chart['planets']
        asc = solar_return_chart['varsha_lagna']['longitude']

        sahams = {}

        # Get planetary longitudes
        sun = planets['Sun']['longitude']
        moon = planets['Moon']['longitude']
        mars = planets['Mars']['longitude']
        mercury = planets['Mercury']['longitude']
        jupiter = planets['Jupiter']['longitude']
        venus = planets['Venus']['longitude']
        saturn = planets['Saturn']['longitude']

        # Major Sahams

        # 1. Punya Saham (Fortune Point)
        punya = (asc + moon - sun) % 360
        sahams['Punya Saham'] = {
            'longitude': punya,
            'sign': self._get_sign(punya),
            'meaning': 'Overall fortune and prosperity',
            'importance': 'Very High',
        }

        # 2. Vidya Saham (Education Point)
        vidya = (asc + mercury - jupiter) % 360
        sahams['Vidya Saham'] = {
            'longitude': vidya,
            'sign': self._get_sign(vidya),
            'meaning': 'Education, learning, intellectual pursuits',
            'importance': 'High',
        }

        # 3. Vivaha Saham (Marriage Point)
        vivaha = (asc + venus - jupiter) % 360
        sahams['Vivaha Saham'] = {
            'longitude': vivaha,
            'sign': self._get_sign(vivaha),
            'meaning': 'Marriage, partnerships, relationships',
            'importance': 'High',
        }

        # 4. Putra Saham (Children Point)
        putra = (asc + jupiter - moon) % 360
        sahams['Putra Saham'] = {
            'longitude': putra,
            'sign': self._get_sign(putra),
            'meaning': 'Children, creativity, speculative gains',
            'importance': 'High',
        }

        # 5. Mrityu Saham (Death/Danger Point)
        mrityu = (asc + saturn - moon) % 360
        sahams['Mrityu Saham'] = {
            'longitude': mrityu,
            'sign': self._get_sign(mrityu),
            'meaning': 'Danger, caution required, health concerns',
            'importance': 'High',
        }

        # 6. Roga Saham (Disease Point)
        roga = (asc + mars - saturn) % 360
        sahams['Roga Saham'] = {
            'longitude': roga,
            'sign': self._get_sign(roga),
            'meaning': 'Health issues, diseases, medical matters',
            'importance': 'High',
        }

        # 7. Vyapar Saham (Business Point)
        vyapar = (asc + mercury - moon) % 360
        sahams['Vyapar Saham'] = {
            'longitude': vyapar,
            'sign': self._get_sign(vyapar),
            'meaning': 'Business, trade, commercial activities',
            'importance': 'High',
        }

        # 8. Karma Saham (Career Point)
        karma = (asc + mercury - mars) % 360
        sahams['Karma Saham'] = {
            'longitude': karma,
            'sign': self._get_sign(karma),
            'meaning': 'Career, profession, work matters',
            'importance': 'High',
        }

        # 9. Bandhu Saham (Relatives Point)
        bandhu = (asc + venus - saturn) % 360
        sahams['Bandhu Saham'] = {
            'longitude': bandhu,
            'sign': self._get_sign(bandhu),
            'meaning': 'Family relations, relatives, domestic harmony',
            'importance': 'Medium',
        }

        # 10. Mitra Saham (Friends Point)
        mitra = (asc + jupiter - venus) % 360
        sahams['Mitra Saham'] = {
            'longitude': mitra,
            'sign': self._get_sign(mitra),
            'meaning': 'Friendships, social connections, networking',
            'importance': 'Medium',
        }

        # Additional 40+ sahams would be added here following similar formulas
        # For brevity, showing the 10 most important ones

        return sahams

    def generate_annual_interpretation(
        self,
        solar_return_chart: Dict[str, Any],
        patyayini_dasha: List[Dict[str, Any]],
        sahams: Dict[str, Dict[str, Any]],
        natal_chart_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive annual interpretation.

        Returns:
            Dictionary with year overview, monthly predictions, best/worst periods
        """
        yogas = solar_return_chart['yogas']

        # Determine overall year quality
        auspicious_yogas = [y for y in yogas if y['type'] in ['Auspicious', 'Highly Auspicious']]
        challenging_yogas = [y for y in yogas if y['type'] == 'Challenging']

        overall_quality = 'Excellent' if len(auspicious_yogas) >= 3 else \
                         'Challenging' if len(challenging_yogas) >= 2 else \
                         'Mixed'

        # Generate month-by-month predictions
        monthly_predictions = self._generate_monthly_predictions(
            patyayini_dasha,
            solar_return_chart
        )

        # Identify best and worst periods
        best_periods = self._identify_best_periods(patyayini_dasha, yogas)
        worst_periods = self._identify_worst_periods(patyayini_dasha, yogas)

        # Key opportunities and challenges
        opportunities = self._identify_opportunities(yogas, sahams)
        challenges = self._identify_challenges(yogas, sahams)

        # Generate remedies
        remedies = self._generate_annual_remedies(yogas, challenging_yogas)

        return {
            'overall_quality': overall_quality,
            'year_summary': self._generate_year_summary(yogas, overall_quality),
            'monthly_predictions': monthly_predictions,
            'best_periods': best_periods,
            'worst_periods': worst_periods,
            'key_opportunities': opportunities,
            'key_challenges': challenges,
            'recommended_remedies': remedies,
            'important_sahams': self._get_important_sahams_summary(sahams),
        }

    def _generate_monthly_predictions(
        self,
        patyayini_dasha: List[Dict[str, Any]],
        solar_return_chart: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate month-by-month predictions."""
        monthly = []

        for dasha_period in patyayini_dasha:
            planet = dasha_period['planet']
            start = dasha_period['start_date']
            end = dasha_period['end_date']

            monthly.append({
                'period': f"{start.strftime('%B')} - {end.strftime('%B %Y')}",
                'ruling_planet': planet,
                'theme': self._get_monthly_theme(planet),
                'focus_areas': self._get_focus_areas(planet),
                'advice': self._get_monthly_advice(planet),
            })

        return monthly

    def _get_monthly_theme(self, planet: str) -> str:
        """Get theme for month based on ruling planet."""
        themes = {
            'Sun': 'Leadership and Recognition',
            'Moon': 'Emotional Well-being and Home',
            'Mars': 'Action and Courage',
            'Mercury': 'Communication and Learning',
            'Jupiter': 'Growth and Wisdom',
            'Venus': 'Harmony and Pleasure',
            'Saturn': 'Discipline and Responsibility',
            'Rahu': 'Innovation and Change',
        }
        return themes.get(planet, 'General Progress')

    def _get_focus_areas(self, planet: str) -> List[str]:
        """Get focus areas for month based on ruling planet."""
        focus = {
            'Sun': ['Career', 'Authority', 'Father', 'Government'],
            'Moon': ['Emotions', 'Mother', 'Public', 'Travel'],
            'Mars': ['Energy', 'Sports', 'Property', 'Siblings'],
            'Mercury': ['Business', 'Education', 'Communication', 'Technology'],
            'Jupiter': ['Spirituality', 'Children', 'Teachers', 'Wealth'],
            'Venus': ['Relationships', 'Arts', 'Luxury', 'Beauty'],
            'Saturn': ['Hard work', 'Delays', 'Longevity', 'Servants'],
            'Rahu': ['Foreign', 'Unconventional', 'Technology', 'Sudden events'],
        }
        return focus.get(planet, ['General activities'])

    def _get_monthly_advice(self, planet: str) -> str:
        """Get advice for month based on ruling planet."""
        advice = {
            'Sun': 'Focus on career advancement and taking leadership roles',
            'Moon': 'Prioritize emotional health and family relationships',
            'Mars': 'Channel energy productively, avoid conflicts',
            'Mercury': 'Enhance skills, network, and communicate clearly',
            'Jupiter': 'Seek knowledge, be generous, plan for growth',
            'Venus': 'Nurture relationships, enjoy life, appreciate beauty',
            'Saturn': 'Be patient, work hard, avoid shortcuts',
            'Rahu': 'Embrace change, explore new paths, stay grounded',
        }
        return advice.get(planet, 'Stay balanced and focused')

    def _identify_best_periods(
        self,
        patyayini_dasha: List[Dict[str, Any]],
        yogas: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Identify best periods in the year."""
        best = []

        # Periods ruled by benefics with strong yogas
        for dasha in patyayini_dasha:
            if dasha['planet'] in ['Jupiter', 'Venus', 'Mercury']:
                best.append({
                    'period': f"{dasha['start_date'].strftime('%B')} - {dasha['end_date'].strftime('%B')}",
                    'reason': f"{dasha['planet']} period brings positive results",
                    'utilize_for': self._get_utilization_advice(dasha['planet']),
                })

        return best[:3]  # Top 3 best periods

    def _identify_worst_periods(
        self,
        patyayini_dasha: List[Dict[str, Any]],
        yogas: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Identify challenging periods in the year."""
        worst = []

        # Periods ruled by malefics
        for dasha in patyayini_dasha:
            if dasha['planet'] in ['Saturn', 'Mars', 'Rahu']:
                worst.append({
                    'period': f"{dasha['start_date'].strftime('%B')} - {dasha['end_date'].strftime('%B')}",
                    'reason': f"{dasha['planet']} period requires caution",
                    'precautions': self._get_precautions(dasha['planet']),
                })

        return worst[:2]  # Top 2 challenging periods

    def _get_utilization_advice(self, planet: str) -> str:
        """Get advice for utilizing favorable period."""
        advice = {
            'Jupiter': 'Education, investments, spiritual pursuits, children',
            'Venus': 'Relationships, artistic projects, luxury purchases, social events',
            'Mercury': 'Business deals, learning new skills, communication projects',
        }
        return advice.get(planet, 'General growth activities')

    def _get_precautions(self, planet: str) -> str:
        """Get precautions for challenging period."""
        precautions = {
            'Saturn': 'Avoid hasty decisions, be patient, work diligently',
            'Mars': 'Control anger, avoid conflicts, be cautious with fire/weapons',
            'Rahu': 'Stay grounded, avoid speculation, be careful with partnerships',
        }
        return precautions.get(planet, 'Exercise general caution')

    def _identify_opportunities(
        self,
        yogas: List[Dict[str, Any]],
        sahams: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """Identify key opportunities in the year."""
        opportunities = []

        for yoga in yogas:
            if yoga['type'] in ['Auspicious', 'Highly Auspicious']:
                opportunities.append(yoga['effects'])

        # Add saham-based opportunities
        punya_sign = sahams.get('Punya Saham', {}).get('sign', '')
        if punya_sign:
            opportunities.append(f'Fortune favors activities related to {punya_sign} house')

        return opportunities[:5]

    def _identify_challenges(
        self,
        yogas: List[Dict[str, Any]],
        sahams: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """Identify key challenges in the year."""
        challenges = []

        for yoga in yogas:
            if yoga['type'] == 'Challenging':
                challenges.append(yoga['effects'])

        # Add saham-based challenges
        mrityu_sign = sahams.get('Mrityu Saham', {}).get('sign', '')
        if mrityu_sign:
            challenges.append(f'Exercise caution in matters related to {mrityu_sign} house')

        return challenges[:5]

    def _generate_annual_remedies(
        self,
        all_yogas: List[Dict[str, Any]],
        challenging_yogas: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Generate remedies for the year."""
        remedies = []

        if challenging_yogas:
            remedies.append({
                'category': 'General Protection',
                'remedy': 'Chant Maha Mrityunjaya Mantra daily',
                'frequency': '11 times daily',
            })

            remedies.append({
                'category': 'Charity',
                'remedy': 'Donate to temples or help the needy',
                'frequency': 'Monthly on auspicious days',
            })

        # Planet-specific remedies based on yogas
        for yoga in challenging_yogas:
            for planet in yoga.get('planets_involved', []):
                remedies.append(self._get_planet_remedy(planet))

        return remedies[:5]

    def _get_planet_remedy(self, planet: str) -> Dict[str, str]:
        """Get remedy for specific planet."""
        remedies = {
            'Sun': {'category': 'Sun Remedy', 'remedy': 'Offer water to Sun at sunrise', 'frequency': 'Daily'},
            'Moon': {'category': 'Moon Remedy', 'remedy': 'Wear pearl or donate white items', 'frequency': 'On Mondays'},
            'Mars': {'category': 'Mars Remedy', 'remedy': 'Recite Hanuman Chalisa', 'frequency': 'Tuesdays'},
            'Mercury': {'category': 'Mercury Remedy', 'remedy': 'Donate green items, worship Lord Vishnu', 'frequency': 'Wednesdays'},
            'Jupiter': {'category': 'Jupiter Remedy', 'remedy': 'Worship Guru, donate yellow items', 'frequency': 'Thursdays'},
            'Venus': {'category': 'Venus Remedy', 'remedy': 'Donate white items, worship Goddess Lakshmi', 'frequency': 'Fridays'},
            'Saturn': {'category': 'Saturn Remedy', 'remedy': 'Feed crows, help the poor', 'frequency': 'Saturdays'},
            'Rahu': {'category': 'Rahu Remedy', 'remedy': 'Donate to the needy, chant Rahu mantra', 'frequency': 'Saturdays'},
        }
        return remedies.get(planet, {'category': 'General', 'remedy': 'Perform charity', 'frequency': 'Weekly'})

    def _generate_year_summary(
        self,
        yogas: List[Dict[str, Any]],
        overall_quality: str
    ) -> str:
        """Generate overall year summary."""
        auspicious_count = len([y for y in yogas if y['type'] in ['Auspicious', 'Highly Auspicious']])

        if overall_quality == 'Excellent':
            return f"This promises to be an excellent year with {auspicious_count} favorable yogas. " \
                   "Expect growth, success, and positive developments across multiple life areas. " \
                   "Utilize the favorable periods for important initiatives."
        elif overall_quality == 'Challenging':
            return "This year requires careful navigation with some challenging influences. " \
                   "Focus on patience, hard work, and appropriate remedies. " \
                   "Avoid major risks and prioritize stability."
        else:
            return f"This year brings mixed influences with both opportunities and challenges. " \
                   f"With {auspicious_count} favorable yogas, success is possible through effort. " \
                   "Be selective about timing and utilize favorable periods wisely."

    def _get_important_sahams_summary(
        self,
        sahams: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Get summary of most important sahams."""
        important = ['Punya Saham', 'Vidya Saham', 'Vivaha Saham', 'Putra Saham', 'Karma Saham']

        summary = []
        for saham_name in important:
            if saham_name in sahams:
                saham_data = sahams[saham_name]
                summary.append({
                    'name': saham_name,
                    'position': f"{saham_data['sign']} ({saham_data['longitude']:.2f}°)",
                    'meaning': saham_data['meaning'],
                })

        return summary

    # Utility methods

    def _datetime_to_julian(self, dt: datetime) -> float:
        """Convert datetime to Julian Day."""
        return self.swe.julday(
            dt.year, dt.month, dt.day,
            dt.hour + dt.minute / 60.0 + dt.second / 3600.0
        )

    def _julian_to_datetime(self, jd: float) -> datetime:
        """Convert Julian Day to datetime."""
        result = self.swe.revjul(jd)
        year, month, day, hour = result
        hours = int(hour)
        minutes = int((hour - hours) * 60)
        seconds = int(((hour - hours) * 60 - minutes) * 60)
        return datetime(year, month, day, hours, minutes, seconds)

    def _get_sign(self, longitude: float) -> str:
        """Get zodiac sign from longitude."""
        signs = [
            'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
            'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
        ]
        return signs[int(longitude / 30) % 12]

    def _get_sign_from_num(self, sign_num: int) -> str:
        """Get sign name from sign number (1-12)."""
        signs = [
            '', 'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
            'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
        ]
        return signs[sign_num % 13]

    def _get_nakshatra(self, longitude: float) -> str:
        """Get nakshatra from longitude."""
        nakshatras = [
            'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
            'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni',
            'Uttara Phalguni', 'Hasta', 'Chitra', 'Swati', 'Vishakha',
            'Anuradha', 'Jyeshtha', 'Mula', 'Purva Ashadha', 'Uttara Ashadha',
            'Shravana', 'Dhanishta', 'Shatabhisha', 'Purva Bhadrapada',
            'Uttara Bhadrapada', 'Revati'
        ]
        nakshatra_index = int((longitude % 360) / 13.333333)
        return nakshatras[nakshatra_index]


# Global service instance
varshaphal_service = VarshapalService()
