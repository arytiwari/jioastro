"""
Calendar Year Predictions Service

Provides transit-based annual predictions for calendar years (Jan 1 - Dec 31).
Different from Varshaphal (Solar Return) which runs birthday to birthday.

Features:
- Monthly transit predictions (Gochar)
- Major planetary movements (Saturn, Jupiter, Rahu/Ketu)
- Eclipse predictions
- Best/worst months analysis
- Auspicious periods
"""

from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Tuple, Any
import calendar
import logging

logger = logging.getLogger(__name__)


class CalendarYearService:
    """
    Service for Calendar Year Predictions (Jan 1 - Dec 31).

    Uses transit analysis (Gochar) to predict how current planetary
    positions will affect the natal chart throughout the year.
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

        # Benefics and Malefics
        self.BENEFICS = ['Jupiter', 'Venus', 'Mercury', 'Moon']
        self.MALEFICS = ['Saturn', 'Mars', 'Rahu', 'Ketu', 'Sun']

        # Transit speeds (approximate days to transit one sign)
        self.TRANSIT_SPEEDS = {
            'Moon': 2.5,      # Fast - completes in a month
            'Sun': 30,        # One sign per month
            'Mercury': 30,    # Variable, about a month
            'Venus': 30,      # Variable, about a month
            'Mars': 45,       # About 1.5 months
            'Jupiter': 365,   # About 1 year per sign
            'Saturn': 912,    # About 2.5 years per sign
            'Rahu': -548,     # Retrograde, about 1.5 years per sign
            'Ketu': -548,     # Retrograde, about 1.5 years per sign
        }

    def generate_calendar_year_predictions(
        self,
        natal_chart: Dict[str, Any],
        target_year: int,
        birth_lat: float,
        birth_lon: float
    ) -> Dict[str, Any]:
        """
        Generate complete calendar year predictions.

        Args:
            natal_chart: Natal chart data with planet positions and houses
            target_year: Calendar year (e.g., 2026)
            birth_lat: Birth latitude
            birth_lon: Birth longitude

        Returns:
            Dictionary with monthly predictions, transits, eclipses, etc.
        """
        logger.info(f"Generating calendar year predictions for {target_year}")

        # Year start and end
        year_start = datetime(target_year, 1, 1, 0, 0, 0)
        year_end = datetime(target_year, 12, 31, 23, 59, 59)

        # Calculate major transits for the year
        major_transits = self._calculate_major_transits(
            natal_chart,
            year_start,
            year_end
        )

        # Generate monthly predictions
        monthly_predictions = self._generate_monthly_predictions(
            natal_chart,
            target_year,
            major_transits
        )

        # Find eclipses
        eclipses = self._find_eclipses(target_year)

        # Analyze best and worst months
        best_months = self._identify_best_months(monthly_predictions, major_transits)
        worst_months = self._identify_worst_months(monthly_predictions, major_transits)

        # Key opportunities and challenges
        opportunities = self._identify_opportunities(major_transits, natal_chart)
        challenges = self._identify_challenges(major_transits, natal_chart)

        # Generate remedies
        remedies = self._generate_remedies(worst_months, challenges)

        return {
            'target_year': target_year,
            'year_start': year_start.isoformat(),
            'year_end': year_end.isoformat(),
            'monthly_predictions': monthly_predictions,
            'major_transits': major_transits,
            'eclipses': eclipses,
            'best_months': best_months,
            'worst_months': worst_months,
            'key_opportunities': opportunities,
            'key_challenges': challenges,
            'recommended_remedies': remedies,
            'overall_summary': self._generate_year_summary(
                best_months,
                worst_months,
                major_transits
            ),
        }

    def _calculate_major_transits(
        self,
        natal_chart: Dict[str, Any],
        year_start: datetime,
        year_end: datetime
    ) -> List[Dict[str, Any]]:
        """
        Calculate major planetary transits for the year.

        Focuses on slow-moving planets: Saturn, Jupiter, Rahu, Ketu.
        """
        major_transits = []
        slow_planets = ['Saturn', 'Jupiter', 'Rahu']

        for planet_name in slow_planets:
            # Get planet position at start and end of year
            start_pos = self._get_planet_position(planet_name, year_start)
            end_pos = self._get_planet_position(planet_name, year_end)

            start_sign = int(start_pos / 30) + 1
            end_sign = int(end_pos / 30) + 1

            # Check for sign changes during the year
            if start_sign != end_sign:
                # Find exact date of sign change
                change_date = self._find_sign_change_date(
                    planet_name,
                    year_start,
                    year_end
                )

                major_transits.append({
                    'planet': planet_name,
                    'event_type': 'Sign Change',
                    'date': change_date.isoformat() if change_date else year_start.isoformat(),
                    'from_sign': self._get_sign_name(start_sign),
                    'to_sign': self._get_sign_name(end_sign),
                    'significance': self._get_transit_significance(
                        planet_name,
                        end_sign,
                        natal_chart
                    ),
                    'effects': self._get_transit_effects(
                        planet_name,
                        end_sign,
                        natal_chart
                    ),
                })
            else:
                # No sign change, but still note the transit
                natal_moon_sign = natal_chart.get('moon_sign', 1)
                transit_house = ((start_sign - natal_moon_sign) % 12) + 1

                major_transits.append({
                    'planet': planet_name,
                    'event_type': 'Continues in Sign',
                    'date': year_start.isoformat(),
                    'sign': self._get_sign_name(start_sign),
                    'house_from_moon': transit_house,
                    'significance': self._get_house_transit_significance(
                        planet_name,
                        transit_house
                    ),
                    'effects': self._get_house_transit_effects(
                        planet_name,
                        transit_house
                    ),
                })

        return major_transits

    def _generate_monthly_predictions(
        self,
        natal_chart: Dict[str, Any],
        target_year: int,
        major_transits: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate predictions for each month of the year."""
        monthly = []

        for month in range(1, 13):
            # Mid-month date for calculating transits
            mid_month = datetime(target_year, month, 15, 12, 0, 0)

            # Calculate Sun's position (determines month's energy)
            sun_pos = self._get_planet_position('Sun', mid_month)
            sun_sign = int(sun_pos / 30) + 1

            # Calculate Jupiter and Saturn positions (major influences)
            jupiter_pos = self._get_planet_position('Jupiter', mid_month)
            saturn_pos = self._get_planet_position('Saturn', mid_month)

            jupiter_house = self._calculate_transit_house(
                jupiter_pos,
                natal_chart.get('moon_sign', 1)
            )
            saturn_house = self._calculate_transit_house(
                saturn_pos,
                natal_chart.get('moon_sign', 1)
            )

            # Determine month quality
            quality = self._determine_month_quality(
                jupiter_house,
                saturn_house,
                month
            )

            monthly.append({
                'month': calendar.month_name[month],
                'month_number': month,
                'quality': quality,
                'sun_sign': self._get_sign_name(sun_sign),
                'jupiter_house': jupiter_house,
                'saturn_house': saturn_house,
                'key_themes': self._get_month_themes(
                    quality,
                    jupiter_house,
                    saturn_house
                ),
                'focus_areas': self._get_month_focus_areas(month, quality),
                'advice': self._get_month_advice(quality, month),
                'important_dates': self._get_important_dates(target_year, month),
            })

        return monthly

    def _find_eclipses(self, target_year: int) -> List[Dict[str, Any]]:
        """
        Find all eclipses occurring in the target year.

        Uses Swiss Ephemeris eclipse search functions.
        """
        eclipses = []

        # Search period
        start_jd = self.swe.julday(target_year, 1, 1, 0)
        end_jd = self.swe.julday(target_year, 12, 31, 23.99)

        # Search for solar eclipses
        current_jd = start_jd
        while current_jd < end_jd:
            try:
                result = self.swe.sol_eclipse_when_glob(current_jd, backward=False)
                eclipse_jd = result[1][0]

                if eclipse_jd > end_jd:
                    break

                # Convert to datetime
                eclipse_date = self._julian_to_datetime(eclipse_jd)

                if eclipse_date.year == target_year:
                    eclipse_type = self._get_eclipse_type(result[0])
                    eclipses.append({
                        'type': 'Solar',
                        'subtype': eclipse_type,
                        'date': eclipse_date.isoformat(),
                        'effects': 'New beginnings, changes, focus on external matters',
                        'recommendations': 'Avoid major decisions, perform eclipse remedies',
                    })

                current_jd = eclipse_jd + 10  # Move forward to find next eclipse
            except:
                break

        # Search for lunar eclipses
        current_jd = start_jd
        while current_jd < end_jd:
            try:
                result = self.swe.lun_eclipse_when(current_jd, backward=False)
                eclipse_jd = result[1][0]

                if eclipse_jd > end_jd:
                    break

                eclipse_date = self._julian_to_datetime(eclipse_jd)

                if eclipse_date.year == target_year:
                    eclipse_type = self._get_eclipse_type(result[0])
                    eclipses.append({
                        'type': 'Lunar',
                        'subtype': eclipse_type,
                        'date': eclipse_date.isoformat(),
                        'effects': 'Emotional insights, endings, focus on internal matters',
                        'recommendations': 'Practice meditation, avoid emotional decisions',
                    })

                current_jd = eclipse_jd + 10
            except:
                break

        return sorted(eclipses, key=lambda x: x['date'])

    def _identify_best_months(
        self,
        monthly_predictions: List[Dict[str, Any]],
        major_transits: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Identify the best 3 months of the year."""
        best = []

        for month_data in monthly_predictions:
            if month_data['quality'] in ['Excellent', 'Very Good']:
                best.append({
                    'month': month_data['month'],
                    'quality': month_data['quality'],
                    'reason': f"Jupiter in {self._get_house_ordinal(month_data['jupiter_house'])} house brings positive results",
                    'utilize_for': ', '.join(month_data['focus_areas'][:3]),
                })

        return sorted(best, key=lambda x: ['Excellent', 'Very Good'].index(x['quality']))[:3]

    def _identify_worst_months(
        self,
        monthly_predictions: List[Dict[str, Any]],
        major_transits: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Identify the most challenging months."""
        worst = []

        for month_data in monthly_predictions:
            if month_data['quality'] in ['Challenging', 'Difficult']:
                worst.append({
                    'month': month_data['month'],
                    'quality': month_data['quality'],
                    'reason': f"Saturn in {self._get_house_ordinal(month_data['saturn_house'])} house requires caution",
                    'precautions': month_data['advice'],
                })

        return worst[:2]

    def _identify_opportunities(
        self,
        major_transits: List[Dict[str, Any]],
        natal_chart: Dict[str, Any]
    ) -> List[str]:
        """Identify key opportunities in the year."""
        opportunities = []

        for transit in major_transits:
            if transit['planet'] == 'Jupiter' and 'effects' in transit:
                if 'growth' in transit['effects'].lower() or 'success' in transit['effects'].lower():
                    opportunities.append(transit['effects'])

        return opportunities[:5]

    def _identify_challenges(
        self,
        major_transits: List[Dict[str, Any]],
        natal_chart: Dict[str, Any]
    ) -> List[str]:
        """Identify key challenges in the year."""
        challenges = []

        for transit in major_transits:
            if transit['planet'] == 'Saturn' and 'effects' in transit:
                if 'challenge' in transit['effects'].lower() or 'delay' in transit['effects'].lower():
                    challenges.append(transit['effects'])

        return challenges[:5]

    def _generate_remedies(
        self,
        worst_months: List[Dict[str, Any]],
        challenges: List[str]
    ) -> List[Dict[str, str]]:
        """Generate remedies for challenging periods."""
        remedies = []

        if worst_months or challenges:
            remedies.append({
                'category': 'General Protection',
                'remedy': 'Chant Maha Mrityunjaya Mantra',
                'frequency': '11 times daily',
            })

            remedies.append({
                'category': 'Saturn Remedy',
                'remedy': 'Donate to the needy, especially on Saturdays',
                'frequency': 'Weekly',
            })

            remedies.append({
                'category': 'Jupiter Grace',
                'remedy': 'Worship on Thursdays, donate yellow items',
                'frequency': 'Weekly',
            })

        return remedies

    def _generate_year_summary(
        self,
        best_months: List[Dict[str, Any]],
        worst_months: List[Dict[str, Any]],
        major_transits: List[Dict[str, Any]]
    ) -> str:
        """Generate overall year summary."""
        num_best = len(best_months)
        num_worst = len(worst_months)

        if num_best > num_worst:
            return f"This year shows {num_best} favorable months with good opportunities for growth. " \
                   "Focus on utilizing the positive periods for important initiatives while being " \
                   "mindful during challenging phases."
        elif num_worst > num_best:
            return f"This year presents some challenges with {num_worst} difficult months. " \
                   "Patience and remedies will be essential. Use the favorable periods wisely " \
                   "and avoid major risks during challenging times."
        else:
            return "This year brings a balanced mix of opportunities and challenges. " \
                   "Success depends on timing and effort. Stay flexible and make the most " \
                   "of favorable transits while managing difficult periods with care."

    # Helper methods

    def _get_planet_position(self, planet_name: str, dt: datetime) -> float:
        """Get planet's longitude at specific datetime."""
        jd = self._datetime_to_julian(dt)
        planet_id = self.PLANETS[planet_name]
        pos, _ = self.swe.calc_ut(jd, planet_id)
        return pos[0] % 360

    def _calculate_transit_house(self, planet_longitude: float, moon_sign: int) -> int:
        """Calculate which house (from Moon) the planet transits."""
        planet_sign = int(planet_longitude / 30) + 1
        house = ((planet_sign - moon_sign) % 12) + 1
        return house

    def _determine_month_quality(
        self,
        jupiter_house: int,
        saturn_house: int,
        month: int
    ) -> str:
        """Determine overall quality of the month."""
        # Jupiter in favorable houses (1, 2, 5, 7, 9, 11)
        jupiter_favorable = jupiter_house in [1, 2, 5, 7, 9, 11]

        # Saturn in difficult houses (1, 4, 7, 8, 10, 12)
        saturn_difficult = saturn_house in [1, 4, 7, 8, 10, 12]

        if jupiter_favorable and not saturn_difficult:
            return 'Excellent'
        elif jupiter_favorable:
            return 'Very Good'
        elif saturn_difficult:
            return 'Challenging'
        else:
            return 'Moderate'

    def _get_month_themes(self, quality: str, jupiter_house: int, saturn_house: int) -> List[str]:
        """Get key themes for the month."""
        themes = []

        if quality in ['Excellent', 'Very Good']:
            themes.append('Growth and expansion')
            themes.append('Positive opportunities')
        else:
            themes.append('Patience required')
            themes.append('Hard work')

        # Add house-specific theme
        house_themes = {
            1: 'Self-development',
            2: 'Financial matters',
            3: 'Communication',
            4: 'Home and family',
            5: 'Creativity',
            6: 'Health and service',
            7: 'Partnerships',
            8: 'Transformation',
            9: 'Higher learning',
            10: 'Career',
            11: 'Gains',
            12: 'Spirituality',
        }

        if jupiter_house in house_themes:
            themes.append(house_themes[jupiter_house])

        return themes[:3]

    def _get_month_focus_areas(self, month: int, quality: str) -> List[str]:
        """Get focus areas for specific month."""
        # General focus based on quality
        if quality == 'Excellent':
            return ['Major initiatives', 'Investments', 'New beginnings', 'Expansion']
        elif quality == 'Very Good':
            return ['Growth projects', 'Relationships', 'Learning', 'Travel']
        elif quality == 'Challenging':
            return ['Caution', 'Review', 'Patience', 'Remedies']
        else:
            return ['Steady progress', 'Maintenance', 'Planning', 'Balance']

    def _get_month_advice(self, quality: str, month: int) -> str:
        """Get advice for the month."""
        if quality == 'Excellent':
            return 'Excellent time for important decisions and new projects'
        elif quality == 'Very Good':
            return 'Good period for growth, but stay balanced'
        elif quality == 'Challenging':
            return 'Exercise patience, avoid major changes, focus on remedies'
        else:
            return 'Maintain steady effort, moderate expectations'

    def _get_important_dates(self, year: int, month: int) -> List[str]:
        """Get astrologically important dates in the month."""
        # This is a simplified version - you could expand with actual calculations
        dates = []

        # Full Moon (typically middle of month)
        dates.append(f"Full Moon: {calendar.month_name[month]} 15, {year}")

        # New Moon (typically end of previous month or start)
        dates.append(f"New Moon: {calendar.month_name[month]} 1, {year}")

        return dates

    def _find_sign_change_date(
        self,
        planet_name: str,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[datetime]:
        """Find exact date when planet changes signs."""
        # Binary search for sign change
        start_jd = self._datetime_to_julian(start_date)
        end_jd = self._datetime_to_julian(end_date)

        start_pos = self._get_planet_position(planet_name, start_date)
        start_sign = int(start_pos / 30)

        # Search day by day (can be optimized)
        current_jd = start_jd
        while current_jd < end_jd:
            current_date = self._julian_to_datetime(current_jd)
            current_pos = self._get_planet_position(planet_name, current_date)
            current_sign = int(current_pos / 30)

            if current_sign != start_sign:
                return current_date

            current_jd += 1  # Check next day

        return None

    def _get_transit_significance(
        self,
        planet_name: str,
        to_sign: int,
        natal_chart: Dict[str, Any]
    ) -> str:
        """Get significance of transit to a sign."""
        if planet_name == 'Jupiter':
            return 'Very High - Jupiter brings growth and blessings'
        elif planet_name == 'Saturn':
            return 'High - Saturn brings lessons and discipline'
        elif planet_name == 'Rahu':
            return 'High - Rahu brings unconventional changes'
        else:
            return 'Moderate'

    def _get_transit_effects(
        self,
        planet_name: str,
        to_sign: int,
        natal_chart: Dict[str, Any]
    ) -> str:
        """Get effects of transit."""
        moon_sign = natal_chart.get('moon_sign', 1)
        house = ((to_sign - moon_sign) % 12) + 1

        return self._get_house_transit_effects(planet_name, house)

    def _get_house_transit_significance(self, planet_name: str, house: int) -> str:
        """Get significance of planet transiting a house."""
        if house in [1, 5, 9]:  # Trikonas
            return 'High - Favorable trikona house'
        elif house in [1, 4, 7, 10]:  # Kendras
            return 'High - Angular house with strong impact'
        elif house in [6, 8, 12]:  # Dusthanas
            return 'Challenging - Difficult house placement'
        else:
            return 'Moderate'

    def _get_house_transit_effects(self, planet_name: str, house: int) -> str:
        """Get effects based on house transit."""
        effects_map = {
            1: 'Personal growth, health, vitality',
            2: 'Finances, family, speech',
            3: 'Courage, siblings, short travels',
            4: 'Home, mother, emotional security',
            5: 'Creativity, children, intelligence',
            6: 'Health challenges, enemies, service',
            7: 'Partnerships, marriage, business',
            8: 'Transformation, obstacles, research',
            9: 'Fortune, higher learning, spirituality',
            10: 'Career, status, achievements',
            11: 'Gains, social network, aspirations',
            12: 'Expenses, spirituality, foreign matters',
        }

        base_effect = effects_map.get(house, 'General life matters')

        if planet_name in self.BENEFICS:
            return f"Positive influence on {base_effect.lower()}"
        else:
            return f"Challenges or lessons in {base_effect.lower()}"

    def _get_eclipse_type(self, eclipse_code: int) -> str:
        """Determine eclipse type from Swiss Ephemeris code."""
        if eclipse_code in [1, 2]:
            return 'Total'
        elif eclipse_code in [3, 4]:
            return 'Partial'
        else:
            return 'Annular or Penumbral'

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

    def _get_sign_name(self, sign_num: int) -> str:
        """Get sign name from number (1-12)."""
        signs = [
            '', 'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
            'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
        ]
        return signs[sign_num % 13]

    def _get_house_ordinal(self, house: int) -> str:
        """Convert house number to ordinal (1st, 2nd, etc.)."""
        if house == 1:
            return '1st'
        elif house == 2:
            return '2nd'
        elif house == 3:
            return '3rd'
        else:
            return f'{house}th'


# Global service instance
calendar_year_service = CalendarYearService()
