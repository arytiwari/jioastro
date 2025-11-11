"""
Cosmic Energy Score™ Service

Calculates daily cosmic energy score (0-100) based on:
- Current Dasha period (30%): Mahadasha/Antardasha benefic/malefic strength
- Jupiter transit (20%): Current transit position relative to natal chart
- Saturn transit (15%): Saturn's influence (inverse - farther = better)
- Moon Nakshatra (15%): Today's Moon nakshatra compatibility with natal Moon
- Weekday Lord (10%): Weekday planetary ruler vs. birth chart
- Hourly Lagna (10%): Current hora/muhurta strength

Score Ranges:
- 70-100: 🟢 HIGH ENERGY (great for bold decisions, networking, launches)
- 40-69:  🟡 MODERATE ENERGY (proceed with caution, mixed results)
- 0-39:   🔴 LOW ENERGY (avoid major decisions, focus on rest/planning)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, date, timedelta
import swisseph as swe
from app.services.astrology import astrology_service


class CosmicEnergyService:
    """Calculate and cache cosmic energy scores"""

    # Benefic and malefic planets
    BENEFICS = ["Jupiter", "Venus", "Mercury", "Moon"]
    MALEFICS = ["Saturn", "Mars", "Rahu", "Ketu", "Sun"]

    # Weekday lords (0=Monday)
    WEEKDAY_LORDS = {
        0: "Moon",     # Monday
        1: "Mars",     # Tuesday
        2: "Mercury",  # Wednesday
        3: "Jupiter",  # Thursday
        4: "Venus",    # Friday
        5: "Saturn",   # Saturday
        6: "Sun"       # Sunday
    }

    def __init__(self):
        """Initialize with Lahiri ayanamsa"""
        swe.set_sid_mode(swe.SIDM_LAHIRI)

    def calculate_cosmic_score(
        self,
        birth_chart: Dict[str, Any],
        target_date: Optional[date] = None,
        target_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Calculate cosmic energy score for a given date/time

        Args:
            birth_chart: User's birth chart data (planets, houses, dasha)
            target_date: Date to calculate score for (default: today)
            target_time: Specific time for hourly modifier (default: now)

        Returns:
            {
                "score": 72,
                "level": "HIGH ENERGY",
                "color": "green",
                "emoji": "🟢",
                "best_for": ["Bold decisions", "Networking"],
                "avoid": ["Impulse purchases", "Major purchases after 3 PM"],
                "breakdown": {
                    "dasha_strength": 85,
                    "jupiter_transit": 70,
                    "saturn_transit": 65,
                    "moon_nakshatra": 80,
                    "weekday_lord": 60,
                    "hourly_modifier": 75
                }
            }
        """
        if target_date is None:
            target_date = date.today()
        if target_time is None:
            target_time = datetime.now()

        # Extract birth chart data
        planets = birth_chart.get("planets", {})
        dasha_data = birth_chart.get("dasha", {})

        # Calculate each component
        dasha_score = self._calculate_dasha_strength(dasha_data, target_date)
        jupiter_score = self._calculate_jupiter_transit_score(planets, target_date)
        saturn_score = self._calculate_saturn_transit_score(planets, target_date)
        moon_score = self._calculate_moon_nakshatra_score(planets, target_date)
        weekday_score = self._calculate_weekday_lord_score(planets, target_date)
        hourly_score = self._calculate_hourly_modifier(planets, target_time)

        # Weighted average (total = 100%)
        cosmic_score = (
            dasha_score * 0.30 +      # 30%
            jupiter_score * 0.20 +    # 20%
            saturn_score * 0.15 +     # 15%
            moon_score * 0.15 +       # 15%
            weekday_score * 0.10 +    # 10%
            hourly_score * 0.10       # 10%
        )

        # Normalize to 0-100, round to integer
        final_score = max(0, min(100, int(cosmic_score)))

        # Determine level, color, emoji
        if final_score >= 70:
            level = "HIGH ENERGY"
            color = "green"
            emoji = "🟢"
            best_for = ["Bold decisions", "Networking", "Product launches", "Asking for favors"]
            avoid = ["Overthinking", "Procrastination"]
        elif final_score >= 40:
            level = "MODERATE ENERGY"
            color = "yellow"
            emoji = "🟡"
            best_for = ["Routine tasks", "Planning", "Research"]
            avoid = ["Major commitments", "Risky decisions"]
        else:
            level = "LOW ENERGY"
            color = "red"
            emoji = "🔴"
            best_for = ["Rest", "Reflection", "Meditation", "Strategic planning"]
            avoid = ["Major decisions", "Confrontations", "Investments"]

        return {
            "score": final_score,
            "level": level,
            "color": color,
            "emoji": emoji,
            "best_for": best_for,
            "avoid": avoid,
            "breakdown": {
                "dasha_strength": round(dasha_score, 1),
                "jupiter_transit": round(jupiter_score, 1),
                "saturn_transit": round(saturn_score, 1),
                "moon_nakshatra": round(moon_score, 1),
                "weekday_lord": round(weekday_score, 1),
                "hourly_modifier": round(hourly_score, 1)
            },
            "calculated_at": target_time.isoformat(),
            "valid_for_date": target_date.isoformat()
        }

    def _calculate_dasha_strength(self, dasha_data: Dict[str, Any], target_date: date) -> float:
        """
        Calculate strength of current Mahadasha/Antardasha period (0-100)

        Benefic dasha = high score (80-100)
        Malefic dasha = low score (20-40)
        Mixed = moderate (40-70)
        """
        try:
            # Get current dasha periods
            current_mahadasha = dasha_data.get("current_mahadasha", {})
            current_antardasha = dasha_data.get("current_antardasha", {})

            maha_planet = current_mahadasha.get("planet", "")
            antar_planet = current_antardasha.get("planet", "")

            # Calculate scores
            maha_score = 90 if maha_planet in self.BENEFICS else 30
            antar_score = 85 if antar_planet in self.BENEFICS else 35

            # Weighted average (Mahadasha 70%, Antardasha 30%)
            dasha_strength = (maha_score * 0.7) + (antar_score * 0.3)

            return dasha_strength

        except Exception as e:
            # Default to moderate if dasha data unavailable
            return 50.0

    def _calculate_jupiter_transit_score(self, natal_planets: Dict[str, Any], target_date: date) -> float:
        """
        Calculate Jupiter transit score (0-100)

        Jupiter in 1st, 5th, 9th, 11th from natal Moon = HIGH (80-95)
        Jupiter in 3rd, 6th, 7th, 10th = MODERATE (50-70)
        Jupiter in 2nd, 4th, 8th, 12th = LOW (30-50)
        """
        try:
            # Get natal Moon sign
            natal_moon = natal_planets.get("Moon", {})
            natal_moon_sign = natal_moon.get("sign_num", 0)

            # Calculate Jupiter's current position
            jd = swe.julday(target_date.year, target_date.month, target_date.day, 12.0)
            ayanamsa = swe.get_ayanamsa_ut(jd)

            result = swe.calc_ut(jd, swe.JUPITER, swe.FLG_SWIEPH)
            tropical_long = result[0][0]
            sidereal_long = (tropical_long - ayanamsa) % 360
            jupiter_sign = int(sidereal_long / 30)

            # Calculate house from natal Moon (1-12)
            house_from_moon = ((jupiter_sign - natal_moon_sign) % 12) + 1

            # Score based on house
            favorable_houses = {
                1: 90,   # Self - expansion, growth
                5: 95,   # Children/creativity - very auspicious
                9: 93,   # Luck - dharma, fortune
                11: 88   # Gains - income, fulfillment
            }
            moderate_houses = {
                3: 65,   # Efforts - hard work pays off
                6: 70,   # Service - overcoming obstacles
                7: 60,   # Partnerships - expansion in relationships
                10: 75   # Career - professional growth
            }
            difficult_houses = {
                2: 45,   # Wealth - expenses for family
                4: 50,   # Home - property expenses
                8: 35,   # Obstacles - transformation
                12: 40   # Losses - spiritual growth through loss
            }

            score = favorable_houses.get(
                house_from_moon,
                moderate_houses.get(
                    house_from_moon,
                    difficult_houses.get(house_from_moon, 50)
                )
            )

            return float(score)

        except Exception as e:
            return 60.0  # Default moderate

    def _calculate_saturn_transit_score(self, natal_planets: Dict[str, Any], target_date: date) -> float:
        """
        Calculate Saturn transit score (0-100)

        Saturn in 3rd, 6th, 11th from natal Moon = HIGH (80-90) - Upachaya houses
        Saturn in other houses = Lower scores based on distance from Moon
        Saturn in 1st, 8th = Very challenging (20-30)
        """
        try:
            # Get natal Moon sign
            natal_moon = natal_planets.get("Moon", {})
            natal_moon_sign = natal_moon.get("sign_num", 0)

            # Calculate Saturn's current position
            jd = swe.julday(target_date.year, target_date.month, target_date.day, 12.0)
            ayanamsa = swe.get_ayanamsa_ut(jd)

            result = swe.calc_ut(jd, swe.SATURN, swe.FLG_SWIEPH)
            tropical_long = result[0][0]
            sidereal_long = (tropical_long - ayanamsa) % 360
            saturn_sign = int(sidereal_long / 30)

            # Calculate house from natal Moon (1-12)
            house_from_moon = ((saturn_sign - natal_moon_sign) % 12) + 1

            # Score based on house (Saturn benefits from upachaya houses)
            upachaya_houses = {
                3: 85,   # Courage - Saturn gives strength here
                6: 90,   # Service/enemies - Saturn excels here
                11: 88   # Gains - delayed but steady gains
            }

            # Sade Sati period (12th, 1st, 2nd from Moon)
            sade_sati_houses = {
                12: 35,  # Rising phase - expenses, anxiety
                1: 25,   # Peak phase - health, obstacles
                2: 40    # Setting phase - financial stress
            }

            # Other houses
            neutral_houses = {
                4: 55,   # Home - responsibilities
                5: 50,   # Children - delays in creativity
                7: 55,   # Partnerships - serious relationships
                8: 30,   # Transformation - very difficult
                9: 60,   # Luck - spiritual discipline
                10: 70   # Career - hard work pays off
            }

            score = upachaya_houses.get(
                house_from_moon,
                sade_sati_houses.get(
                    house_from_moon,
                    neutral_houses.get(house_from_moon, 50)
                )
            )

            return float(score)

        except Exception as e:
            return 55.0  # Default moderate-low

    def _calculate_moon_nakshatra_score(self, natal_planets: Dict[str, Any], target_date: date) -> float:
        """
        Calculate Moon nakshatra compatibility score (0-100)

        Today's Moon nakshatra compatibility with natal Moon nakshatra
        Based on traditional nakshatra friendship (Tara Bala)
        """
        try:
            # Get natal Moon nakshatra
            natal_moon = natal_planets.get("Moon", {})
            natal_nakshatra = natal_moon.get("nakshatra", "")
            natal_nakshatra_num = natal_moon.get("nakshatra_num", 0)

            # Calculate today's Moon nakshatra
            jd = swe.julday(target_date.year, target_date.month, target_date.day, 12.0)
            ayanamsa = swe.get_ayanamsa_ut(jd)

            result = swe.calc_ut(jd, swe.MOON, swe.FLG_SWIEPH)
            tropical_long = result[0][0]
            sidereal_long = (tropical_long - ayanamsa) % 360

            # Each nakshatra is 13°20' (360/27)
            transit_nakshatra_num = int(sidereal_long / (360.0 / 27)) + 1

            # Calculate Tara Bala (nakshatra distance)
            # Distance from natal nakshatra (1-27)
            distance = ((transit_nakshatra_num - natal_nakshatra_num) % 27) + 1

            # Tara (star) positions
            # Janma (1st, 10th, 19th) = 50
            # Sampat (2nd, 11th, 20th) = 90 - Wealth
            # Vipat (3rd, 12th, 21st) = 30 - Danger
            # Kshema (4th, 13th, 22nd) = 85 - Well-being
            # Pratyak (5th, 14th, 23rd) = 40 - Obstacles
            # Sadhana (6th, 15th, 24th) = 70 - Achievement
            # Naidhana (7th, 16th, 25th) = 20 - Death/loss
            # Mitra (8th, 17th, 26th) = 80 - Friend
            # Parama Mitra (9th, 18th, 27th) = 95 - Best friend

            tara_scores = {
                1: 50, 10: 50, 19: 50,      # Janma
                2: 90, 11: 90, 20: 90,      # Sampat
                3: 30, 12: 30, 21: 30,      # Vipat
                4: 85, 13: 85, 22: 85,      # Kshema
                5: 40, 14: 40, 23: 40,      # Pratyak
                6: 70, 15: 70, 24: 70,      # Sadhana
                7: 20, 16: 20, 25: 20,      # Naidhana
                8: 80, 17: 80, 26: 80,      # Mitra
                9: 95, 18: 95, 27: 95       # Parama Mitra
            }

            score = tara_scores.get(distance, 50)
            return float(score)

        except Exception as e:
            return 60.0  # Default moderate

    def _calculate_weekday_lord_score(self, natal_planets: Dict[str, Any], target_date: date) -> float:
        """
        Calculate weekday lord strength score (0-100)

        If weekday lord is:
        - Strong/exalted in birth chart = HIGH (80-90)
        - Well-placed = MODERATE (60-70)
        - Weak/debilitated = LOW (30-50)
        """
        try:
            # Get weekday (0=Monday, 6=Sunday)
            weekday = target_date.weekday()
            weekday_lord = self.WEEKDAY_LORDS.get(weekday, "Sun")

            # Get weekday lord's natal strength
            lord_data = natal_planets.get(weekday_lord, {})

            # Check if lord is exalted/debilitated
            is_exalted = lord_data.get("is_exalted", False)
            is_debilitated = lord_data.get("is_debilitated", False)

            # Check if lord is in own sign
            is_own_sign = lord_data.get("is_in_own_sign", False)

            # Check house position (1, 4, 5, 7, 9, 10 are good houses - Kendra/Trikona)
            house = lord_data.get("house", 0)
            is_good_house = house in [1, 4, 5, 7, 9, 10]

            # Calculate score
            if is_exalted:
                score = 90
            elif is_debilitated:
                score = 35
            elif is_own_sign:
                score = 80
            elif is_good_house:
                score = 70
            else:
                score = 55

            return float(score)

        except Exception as e:
            return 60.0  # Default moderate

    def _calculate_hourly_modifier(self, natal_planets: Dict[str, Any], target_time: datetime) -> float:
        """
        Calculate hourly lagna/hora strength (0-100)

        Hora system:
        - Sun hora (day), Moon hora (night) = neutral (60)
        - Benefic planet hora = HIGH (80-90)
        - Malefic planet hora = LOW (40-50)
        """
        try:
            # Simple hora calculation based on hour of day
            # Each hora is ruled by a planet in sequence: Sun, Venus, Mercury, Moon, Saturn, Jupiter, Mars
            # Repeating cycle

            hour = target_time.hour
            weekday = target_time.weekday()

            # Hora sequence for each weekday (starts at sunrise, approx 6 AM)
            # Simplified: Use hour % 7 to get planet index
            hora_sequence = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]

            # Calculate hora planet (simplified - real hora needs sunrise time)
            hora_index = (weekday * 24 + hour) % 7
            hora_lord = hora_sequence[hora_index]

            # Score based on benefic/malefic
            if hora_lord in self.BENEFICS:
                score = 85
            elif hora_lord in self.MALEFICS:
                score = 45
            else:
                score = 60

            return float(score)

        except Exception as e:
            return 65.0  # Default moderate-high

    def calculate_30_day_scores(
        self,
        birth_chart: Dict[str, Any],
        start_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Precompute cosmic energy scores for next 30 days

        Used for caching and displaying trends

        Returns:
            List of 30 daily scores with dates
        """
        if start_date is None:
            start_date = date.today()

        scores = []
        for i in range(30):
            target_date = start_date + timedelta(days=i)
            score_data = self.calculate_cosmic_score(
                birth_chart=birth_chart,
                target_date=target_date,
                target_time=datetime.combine(target_date, datetime.min.time().replace(hour=12))
            )
            scores.append({
                "date": target_date.isoformat(),
                "score": score_data["score"],
                "level": score_data["level"],
                "emoji": score_data["emoji"]
            })

        return scores


# Singleton instance
cosmic_energy_service = CosmicEnergyService()
