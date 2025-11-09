"""
Feng Shui Integration Service
Handles Kua number calculation, direction analysis, and personalized recommendations
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from app.core.supabase_client import SupabaseClient

logger = logging.getLogger(__name__)


class FengShuiService:
    """Service for feng shui analysis and recommendations"""

    # Kua number mappings
    EAST_LIFE_GROUP = [1, 3, 4, 9]  # East group Kuas
    WEST_LIFE_GROUP = [2, 5, 6, 7, 8]  # West group Kuas

    # Element associations by Kua number
    KUA_ELEMENTS = {
        1: "water",
        2: "earth",
        3: "wood",
        4: "wood",
        5: "earth",  # 5 is special (doesn't exist - males use 2, females use 8)
        6: "metal",
        7: "metal",
        8: "earth",
        9: "fire"
    }

    # Favorable directions for each Kua (in priority order)
    FAVORABLE_DIRECTIONS = {
        1: {"sheng_qi": "SE", "tian_yi": "E", "yan_nian": "S", "fu_wei": "N"},
        2: {"sheng_qi": "NE", "tian_yi": "W", "yan_nian": "NW", "fu_wei": "SW"},
        3: {"sheng_qi": "S", "tian_yi": "N", "yan_nian": "SE", "fu_wei": "E"},
        4: {"sheng_qi": "N", "tian_yi": "S", "yan_nian": "E", "fu_wei": "SE"},
        6: {"sheng_qi": "W", "tian_yi": "NE", "yan_nian": "SW", "fu_wei": "NW"},
        7: {"sheng_qi": "NW", "tian_yi": "SW", "yan_nian": "NE", "fu_wei": "W"},
        8: {"sheng_qi": "SW", "tian_yi": "NW", "yan_nian": "W", "fu_wei": "NE"},
        9: {"sheng_qi": "E", "tian_yi": "SE", "yan_nian": "N", "fu_wei": "S"},
    }

    # Unfavorable directions for each Kua
    UNFAVORABLE_DIRECTIONS = {
        1: {"huo_hai": "W", "wu_gui": "NE", "liu_sha": "NW", "jue_ming": "SW"},
        2: {"huo_hai": "E", "wu_gui": "SE", "liu_sha": "S", "jue_ming": "N"},
        3: {"huo_hai": "SW", "wu_gui": "NW", "liu_sha": "W", "jue_ming": "NE"},
        4: {"huo_hai": "NW", "wu_gui": "W", "liu_sha": "SW", "jue_ming": "NE"},
        6: {"huo_hai": "S", "wu_gui": "E", "liu_sha": "N", "jue_ming": "SE"},
        7: {"huo_hai": "N", "wu_gui": "S", "liu_sha": "E", "jue_ming": "SE"},
        8: {"huo_hai": "SE", "wu_gui": "N", "liu_sha": "S", "jue_ming": "E"},
        9: {"huo_hai": "NW", "wu_gui": "SW", "liu_sha": "W", "jue_ming": "NE"},
    }

    # Color associations by element
    ELEMENT_COLORS = {
        "wood": {
            "lucky": ["green", "brown", "teal", "olive"],
            "unlucky": ["white", "gold", "silver", "gray"]
        },
        "fire": {
            "lucky": ["red", "orange", "pink", "purple", "maroon"],
            "unlucky": ["black", "blue", "navy"]
        },
        "earth": {
            "lucky": ["yellow", "beige", "tan", "brown", "orange"],
            "unlucky": ["green", "dark green"]
        },
        "metal": {
            "lucky": ["white", "gold", "silver", "gray", "bronze"],
            "unlucky": ["red", "pink", "orange"]
        },
        "water": {
            "lucky": ["black", "blue", "navy", "teal", "dark gray"],
            "unlucky": ["yellow", "beige", "tan", "brown"]
        }
    }

    # Element productive (generation) cycle
    PRODUCTIVE_CYCLE = {
        "wood": "fire",  # Wood feeds fire
        "fire": "earth",  # Fire creates earth (ash)
        "earth": "metal",  # Earth produces metal
        "metal": "water",  # Metal collects water
        "water": "wood"  # Water nourishes wood
    }

    # Element destructive (control) cycle
    DESTRUCTIVE_CYCLE = {
        "wood": "earth",  # Wood depletes earth
        "earth": "water",  # Earth dams water
        "water": "fire",  # Water extinguishes fire
        "fire": "metal",  # Fire melts metal
        "metal": "wood"  # Metal cuts wood
    }

    def __init__(self):
        self.supabase = SupabaseClient()

    def calculate_kua_number(self, birth_year: int, gender: str) -> int:
        """
        Calculate Kua number from birth year and gender

        Args:
            birth_year: Year of birth (YYYY)
            gender: 'male' or 'female'

        Returns:
            Kua number (1-9, excluding 5)
        """
        # Use last 2 digits
        year_digits = birth_year % 100

        # Sum the digits
        sum_digits = (year_digits // 10) + (year_digits % 10)

        # If sum >= 10, sum again
        if sum_digits >= 10:
            sum_digits = (sum_digits // 10) + (sum_digits % 10)

        # Calculate Kua based on gender
        if gender.lower() == 'male':
            kua = 10 - sum_digits
            # Kua 5 doesn't exist for males, becomes 2
            if kua == 5:
                kua = 2
        else:  # female
            kua = 5 + sum_digits
            if kua >= 10:
                kua = kua - 9
            # Kua 5 doesn't exist for females, becomes 8
            if kua == 5:
                kua = 8

        return kua

    def get_life_gua_group(self, kua_number: int) -> str:
        """Determine if Kua belongs to East or West life group"""
        return "east" if kua_number in self.EAST_LIFE_GROUP else "west"

    def get_personal_element(self, kua_number: int) -> str:
        """Get personal element based on Kua number"""
        return self.KUA_ELEMENTS.get(kua_number, "earth")

    def get_supporting_elements(self, element: str) -> List[str]:
        """Get elements that support/nourish the personal element"""
        # Element that produces this element (parent)
        # Element that this element produces (child)
        supporting = []

        # Find parent element (what produces this element)
        for parent, child in self.PRODUCTIVE_CYCLE.items():
            if child == element:
                supporting.append(parent)

        # Add the element itself
        supporting.append(element)

        return supporting

    def get_weakening_elements(self, element: str) -> List[str]:
        """Get elements that weaken/control the personal element"""
        weakening = []

        # Element that destroys this element
        for destroyer, destroyed in self.DESTRUCTIVE_CYCLE.items():
            if destroyed == element:
                weakening.append(destroyer)

        # Element that this element produces (drains energy)
        if element in self.PRODUCTIVE_CYCLE:
            weakening.append(self.PRODUCTIVE_CYCLE[element])

        return weakening

    def get_lucky_colors(self, element: str) -> List[str]:
        """Get lucky colors based on element"""
        return self.ELEMENT_COLORS.get(element, {}).get("lucky", [])

    def get_unlucky_colors(self, element: str) -> List[str]:
        """Get unlucky colors based on element"""
        return self.ELEMENT_COLORS.get(element, {}).get("unlucky", [])

    async def create_analysis(
        self,
        user_id: str,
        profile_id: str,
        space_type: Optional[str] = None,
        space_orientation: Optional[str] = None,
        space_layout: Optional[Dict] = None
    ) -> Dict:
        """
        Create feng shui analysis for a user based on their birth profile

        Args:
            user_id: User ID
            profile_id: Birth profile ID
            space_type: Type of space (home, office, bedroom, etc.)
            space_orientation: Main entrance direction
            space_layout: Room layout details

        Returns:
            Complete feng shui analysis with recommendations
        """
        # Fetch birth profile
        profile = await self.supabase.select(
            "profiles",
            filters={"id": profile_id, "user_id": user_id},
            single=True
        )

        if not profile:
            raise ValueError("Profile not found")

        # Extract birth year and gender
        birth_date = profile.get("birth_date")
        gender = profile.get("gender", "male")

        if not birth_date:
            raise ValueError("Birth date required for Kua calculation")

        birth_year = datetime.fromisoformat(birth_date.replace('Z', '+00:00')).year

        # Calculate Kua number
        kua_number = self.calculate_kua_number(birth_year, gender)
        personal_element = self.get_personal_element(kua_number)
        life_gua_group = self.get_life_gua_group(kua_number)

        # Get directions
        favorable_dirs = self.FAVORABLE_DIRECTIONS.get(kua_number, {})
        unfavorable_dirs = self.UNFAVORABLE_DIRECTIONS.get(kua_number, {})

        # Get colors
        lucky_colors = self.get_lucky_colors(personal_element)
        unlucky_colors = self.get_unlucky_colors(personal_element)

        # Get supporting/weakening elements
        supporting_elements = self.get_supporting_elements(personal_element)
        weakening_elements = self.get_weakening_elements(personal_element)

        # Fetch holistic data (astrology chart)
        chart = await self.supabase.select(
            "charts",
            filters={"profile_id": profile_id},
            single=True
        )

        birth_element = None
        planetary_influences = None
        astrology_feng_shui_harmony = None

        if chart:
            # Determine birth element from sun sign
            sun_sign = chart.get("sun_sign", "")
            birth_element = self._get_astrology_element(sun_sign)

            # Check harmony between feng shui element and birth element
            astrology_feng_shui_harmony = self._analyze_element_harmony(
                personal_element, birth_element
            )

        # Calculate compatibility score for space
        compatibility_score = self._calculate_space_compatibility(
            kua_number, space_orientation, favorable_dirs
        )

        # Generate summary
        analysis_summary = self._generate_analysis_summary(
            profile_name=profile.get("name", "User"),
            kua_number=kua_number,
            personal_element=personal_element,
            life_gua_group=life_gua_group,
            space_type=space_type
        )

        # Store analysis
        analysis_data = {
            "user_id": user_id,
            "profile_id": profile_id,
            "kua_number": kua_number,
            "personal_element": personal_element,
            "life_gua_group": life_gua_group,
            "favorable_directions": favorable_dirs,
            "unfavorable_directions": unfavorable_dirs,
            "lucky_colors": lucky_colors,
            "unlucky_colors": unlucky_colors,
            "supporting_elements": supporting_elements,
            "weakening_elements": weakening_elements,
            "space_type": space_type,
            "space_orientation": space_orientation,
            "space_layout": space_layout,
            "analysis_summary": analysis_summary,
            "compatibility_score": compatibility_score,
            "birth_element": birth_element,
            "planetary_influences": planetary_influences,
            "astrology_feng_shui_harmony": astrology_feng_shui_harmony,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }

        analysis = await self.supabase.insert("feng_shui_analyses", analysis_data)

        # Generate recommendations
        recommendations = await self._generate_recommendations(
            analysis_id=str(analysis["id"]),
            user_id=user_id,
            profile_id=profile_id,
            kua_number=kua_number,
            personal_element=personal_element,
            favorable_dirs=favorable_dirs,
            unlucky_colors=unlucky_colors,
            space_type=space_type,
            chart=chart
        )

        return {
            "analysis": analysis,
            "recommendations": recommendations
        }

    def _get_astrology_element(self, sun_sign: str) -> str:
        """Determine element from zodiac sign"""
        fire_signs = ["Aries", "Leo", "Sagittarius"]
        earth_signs = ["Taurus", "Virgo", "Capricorn"]
        air_signs = ["Gemini", "Libra", "Aquarius"]
        water_signs = ["Cancer", "Scorpio", "Pisces"]

        if sun_sign in fire_signs:
            return "fire"
        elif sun_sign in earth_signs:
            return "earth"
        elif sun_sign in air_signs:
            return "air"
        elif sun_sign in water_signs:
            return "water"
        return "earth"

    def _analyze_element_harmony(self, feng_shui_element: str, astrology_element: str) -> str:
        """Analyze harmony between feng shui personal element and astrological element"""
        if not astrology_element:
            return "Feng shui element guidance can be applied independently."

        # Air is treated as Wood in feng shui
        if astrology_element == "air":
            astrology_element = "wood"

        if feng_shui_element == astrology_element:
            return f"Perfect harmony! Your feng shui {feng_shui_element} element aligns with your astrological {astrology_element} nature, creating powerful synergy."

        # Check productive cycle
        if self.PRODUCTIVE_CYCLE.get(astrology_element) == feng_shui_element:
            return f"Your astrological {astrology_element} element nourishes your feng shui {feng_shui_element} element, creating supportive energy flow."

        if self.PRODUCTIVE_CYCLE.get(feng_shui_element) == astrology_element:
            return f"Your feng shui {feng_shui_element} element supports your astrological {astrology_element} nature, enhancing natural tendencies."

        # Check destructive cycle
        if self.DESTRUCTIVE_CYCLE.get(astrology_element) == feng_shui_element:
            return f"Your astrological {astrology_element} element challenges your feng shui {feng_shui_element} element. Balance both through remedies and awareness."

        return f"Your {astrology_element} and {feng_shui_element} elements work independently. Use feng shui adjustments to enhance your space energy."

    def _calculate_space_compatibility(
        self,
        kua_number: int,
        space_orientation: Optional[str],
        favorable_dirs: Dict[str, str]
    ) -> float:
        """Calculate how well space orientation aligns with favorable directions"""
        if not space_orientation:
            return 0.0

        # Check if space orientation matches any favorable direction
        if space_orientation in favorable_dirs.values():
            # Determine which favorable direction it matches
            for direction_type, direction in favorable_dirs.items():
                if direction == space_orientation:
                    if direction_type == "sheng_qi":  # Best direction
                        return 100.0
                    elif direction_type == "tian_yi":
                        return 85.0
                    elif direction_type == "yan_nian":
                        return 75.0
                    elif direction_type == "fu_wei":
                        return 65.0

        # Check if it's an unfavorable direction
        unfavorable_dirs = self.UNFAVORABLE_DIRECTIONS.get(kua_number, {})
        if space_orientation in unfavorable_dirs.values():
            for direction_type, direction in unfavorable_dirs.items():
                if direction == space_orientation:
                    if direction_type == "jue_ming":  # Worst direction
                        return 10.0
                    else:
                        return 30.0

        return 50.0  # Neutral

    def _generate_analysis_summary(
        self,
        profile_name: str,
        kua_number: int,
        personal_element: str,
        life_gua_group: str,
        space_type: Optional[str]
    ) -> str:
        """Generate human-readable analysis summary"""
        summary = f"{profile_name}, your Kua number is {kua_number}, placing you in the {life_gua_group.title()} Life Group. "
        summary += f"Your personal element is {personal_element.title()}, which influences your energy and environment.\n\n"

        if space_type:
            summary += f"For your {space_type}, we recommend aligning key areas with your favorable directions to maximize positive energy flow. "

        summary += "Use the specific recommendations below to optimize your space for wealth, health, relationships, and personal growth."

        return summary

    async def _generate_recommendations(
        self,
        analysis_id: str,
        user_id: str,
        profile_id: str,
        kua_number: int,
        personal_element: str,
        favorable_dirs: Dict[str, str],
        unlucky_colors: List[str],
        space_type: Optional[str],
        chart: Optional[Dict]
    ) -> List[Dict]:
        """Generate specific feng shui recommendations"""
        recommendations = []

        # Direction recommendations
        directions_rec = {
            "analysis_id": analysis_id,
            "user_id": user_id,
            "profile_id": profile_id,
            "category": "directions",
            "area": "workspace",
            "title": "Position Desk in Wealth Direction",
            "recommendation": f"Face {favorable_dirs.get('sheng_qi')} when working at your desk to activate wealth and success energy (Sheng Qi direction).",
            "reason": "Sheng Qi is your most auspicious direction for prosperity and career advancement.",
            "priority": "high",
            "impact_score": 9.0,
            "difficulty": "easy",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        recommendations.append(directions_rec)

        # Bedroom direction
        bed_rec = {
            "analysis_id": analysis_id,
            "user_id": user_id,
            "profile_id": profile_id,
            "category": "directions",
            "area": "bedroom",
            "title": "Sleep with Head Toward Health Direction",
            "recommendation": f"Position your bed so your head points toward {favorable_dirs.get('tian_yi')} for optimal health and rest.",
            "reason": "Tian Yi (Heavenly Doctor) direction promotes healing and well-being during sleep.",
            "priority": "high",
            "impact_score": 8.5,
            "difficulty": "moderate",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        recommendations.append(bed_rec)

        # Color therapy
        color_rec = {
            "analysis_id": analysis_id,
            "user_id": user_id,
            "profile_id": profile_id,
            "category": "colors",
            "area": "general",
            "title": f"Incorporate {personal_element.title()} Element Colors",
            "recommendation": f"Use {', '.join(self.get_lucky_colors(personal_element)[:3])} in your decor, clothing, and accessories. Avoid {', '.join(unlucky_colors[:2])}.",
            "reason": f"These colors strengthen your {personal_element} element and support your natural energy.",
            "priority": "medium",
            "impact_score": 7.0,
            "difficulty": "easy",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        recommendations.append(color_rec)

        # Element balance
        element_rec = {
            "analysis_id": analysis_id,
            "user_id": user_id,
            "profile_id": profile_id,
            "category": "elements",
            "area": "living_room",
            "title": f"Balance Space with {personal_element.title()} Elements",
            "recommendation": self._get_element_remedy(personal_element),
            "reason": f"Adding {personal_element} element objects harmonizes your space with your personal energy.",
            "priority": "medium",
            "impact_score": 7.5,
            "difficulty": "easy",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        recommendations.append(element_rec)

        # Entrance/door facing
        entrance_rec = {
            "analysis_id": analysis_id,
            "user_id": user_id,
            "profile_id": profile_id,
            "category": "placement",
            "area": "entrance",
            "title": "Main Entrance Energy",
            "recommendation": f"If possible, use an entrance facing {favorable_dirs.get('sheng_qi')} or {favorable_dirs.get('tian_yi')}. If not, add feng shui cures like mirrors or plants.",
            "reason": "The main entrance is where energy (Qi) enters your space.",
            "priority": "high",
            "impact_score": 8.0,
            "difficulty": "difficult",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        recommendations.append(entrance_rec)

        # Insert all recommendations
        for rec in recommendations:
            await self.supabase.insert("feng_shui_recommendations", rec)

        return recommendations

    def _get_element_remedy(self, element: str) -> str:
        """Get specific element remedy recommendations"""
        remedies = {
            "wood": "Add plants, wooden furniture, or green/brown decor. Vertical shapes and columns represent wood energy.",
            "fire": "Use candles, warm lighting, triangular shapes, and warm colors (red, orange, purple) to enhance fire energy.",
            "earth": "Incorporate ceramics, crystals, square shapes, and earth tones (yellow, beige, brown) for grounding earth energy.",
            "metal": "Add metal objects, round shapes, white/gold/silver colors, and metallic finishes to strengthen metal energy.",
            "water": "Include water features, mirrors, wavy shapes, and dark colors (black, blue) to activate water energy."
        }
        return remedies.get(element, "Balance elements in your space.")

    async def get_user_analyses(self, user_id: str) -> Dict:
        """Fetch user's feng shui analyses"""
        try:
            analyses = await self.supabase.select(
                "feng_shui_analyses",
                filters={"user_id": user_id},
                order_by="created_at DESC"
            )

            return {
                "analyses": analyses,
                "total_count": len(analyses)
            }
        except Exception as e:
            logger.error(f"Failed to fetch analyses: {str(e)}")
            raise

    async def get_recommendations_for_analysis(
        self,
        analysis_id: str,
        user_id: str
    ) -> Dict:
        """Get all recommendations for an analysis"""
        try:
            recommendations = await self.supabase.select(
                "feng_shui_recommendations",
                filters={"analysis_id": analysis_id, "user_id": user_id},
                order_by="priority DESC"
            )

            # Group by category
            by_category = {}
            by_priority = {"high": 0, "medium": 0, "low": 0}
            implemented_count = 0

            for rec in recommendations:
                category = rec.get("category", "general")
                priority = rec.get("priority", "medium")

                by_category[category] = by_category.get(category, 0) + 1
                by_priority[priority] = by_priority.get(priority, 0) + 1

                if rec.get("is_implemented"):
                    implemented_count += 1

            return {
                "recommendations": recommendations,
                "total_count": len(recommendations),
                "by_category": by_category,
                "by_priority": by_priority,
                "implemented_count": implemented_count
            }
        except Exception as e:
            logger.error(f"Failed to fetch recommendations: {str(e)}")
            raise
