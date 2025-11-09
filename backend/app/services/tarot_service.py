"""
Tarot Reading Service
Handles card drawing, spread layouts, and AI interpretation generation
"""

import random
import hashlib
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import logging

from app.core.supabase_client import SupabaseClient

logger = logging.getLogger(__name__)


class TarotService:
    """Service for tarot card readings and interpretations"""

    def __init__(self):
        self.supabase = SupabaseClient()

    async def get_all_cards(self) -> List[Dict]:
        """Fetch all 78 tarot cards from database"""
        try:
            cards = await self.supabase.select(
                "tarot_cards",
                filters={},
                order_by="card_number"
            )
            return cards
        except Exception as e:
            logger.error(f"Failed to fetch tarot cards: {str(e)}")
            raise

    async def get_card_by_id(self, card_id: str) -> Optional[Dict]:
        """Fetch a single card by ID"""
        try:
            card = await self.supabase.select(
                "tarot_cards",
                filters={"id": card_id},
                single=True
            )
            return card
        except Exception as e:
            logger.error(f"Failed to fetch card {card_id}: {str(e)}")
            return None

    async def get_spreads(self, category: Optional[str] = None) -> List[Dict]:
        """Fetch available tarot spreads"""
        try:
            filters = {"is_active": True}
            if category:
                filters["category"] = category

            spreads = await self.supabase.select(
                "tarot_spreads",
                filters=filters,
                order_by="num_cards"
            )
            return spreads
        except Exception as e:
            logger.error(f"Failed to fetch spreads: {str(e)}")
            raise

    async def get_spread_by_id(self, spread_id: str) -> Optional[Dict]:
        """Fetch a specific spread by ID"""
        try:
            spread = await self.supabase.select(
                "tarot_spreads",
                filters={"id": spread_id},
                single=True
            )
            return spread
        except Exception as e:
            logger.error(f"Failed to fetch spread {spread_id}: {str(e)}")
            return None

    def shuffle_and_draw(self, num_cards: int, seed: Optional[str] = None) -> List[Dict]:
        """
        Shuffle deck and draw specified number of cards

        Args:
            num_cards: Number of cards to draw
            seed: Optional seed for reproducible shuffling (for testing)

        Returns:
            List of drawn card dictionaries with is_reversed flag
        """
        # Create seed from current timestamp if not provided
        if seed is None:
            seed = f"{datetime.utcnow().timestamp()}"

        # Initialize random with seed for shuffling
        random.seed(seed)

        # Create deck of card numbers (0-77)
        deck = list(range(78))
        random.shuffle(deck)

        # Draw cards
        drawn_card_numbers = deck[:num_cards]

        # For each card, randomly determine if reversed (30% chance)
        drawn_cards = []
        for card_number in drawn_card_numbers:
            is_reversed = random.random() < 0.3  # 30% chance of reversal
            drawn_cards.append({
                "card_number": card_number,
                "is_reversed": is_reversed
            })

        return drawn_cards

    async def draw_cards_for_reading(
        self,
        num_cards: int,
        spread_positions: List[Dict],
        seed: Optional[str] = None
    ) -> List[Dict]:
        """
        Draw cards and map to spread positions

        Args:
            num_cards: Number of cards to draw
            spread_positions: List of position definitions
            seed: Optional seed for reproducible drawing

        Returns:
            List of drawn cards with full details and position mapping
        """
        # Shuffle and draw card numbers
        drawn = self.shuffle_and_draw(num_cards, seed)

        # Fetch all cards from database
        all_cards = await self.get_all_cards()
        card_lookup = {card["card_number"]: card for card in all_cards}

        # Map to spread positions
        drawn_cards = []
        for i, drawn_card in enumerate(drawn):
            card_number = drawn_card["card_number"]
            card_data = card_lookup.get(card_number)

            if not card_data:
                continue

            position = spread_positions[i] if i < len(spread_positions) else {
                "position": i + 1,
                "name": f"Position {i + 1}",
                "meaning": "Card position"
            }

            drawn_cards.append({
                "card_id": str(card_data["id"]),
                "card_name": card_data["name"],
                "card_number": card_number,
                "position": position["position"],
                "position_name": position["name"],
                "position_meaning": position["meaning"],
                "is_reversed": drawn_card["is_reversed"],
                "suit": card_data.get("suit"),
                "element": card_data.get("element"),
                "arcana_type": card_data.get("arcana_type"),
                "upright_meaning": card_data.get("upright_meaning"),
                "reversed_meaning": card_data.get("reversed_meaning"),
                "upright_keywords": card_data.get("upright_keywords", []),
                "reversed_keywords": card_data.get("reversed_keywords", [])
            })

        return drawn_cards

    async def draw_daily_card(self, user_id: str) -> Dict:
        """
        Draw a daily card for the user
        Checks if user already drew a card today

        Returns:
            Card data with interpretation
        """
        # Check if user already drew a card today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        existing_reading = await self.supabase.select(
            "tarot_readings",
            filters={
                "user_id": user_id,
                "reading_type": "daily_card"
            },
            limit=1,
            order_by="created_at DESC"
        )

        if existing_reading and len(existing_reading) > 0:
            reading_date = datetime.fromisoformat(existing_reading[0]["created_at"].replace('Z', '+00:00'))
            if reading_date >= today_start:
                # Return today's card
                cards_drawn = existing_reading[0]["cards_drawn"]
                if cards_drawn and len(cards_drawn) > 0:
                    card_id = cards_drawn[0]["card_id"]
                    card = await self.get_card_by_id(card_id)
                    if card:
                        return {
                            "card": card,
                            "is_reversed": cards_drawn[0]["is_reversed"],
                            "already_drawn_today": True,
                            "reading_id": existing_reading[0]["id"]
                        }

        # Draw new daily card
        drawn_cards = await self.draw_cards_for_reading(
            num_cards=1,
            spread_positions=[{
                "position": 1,
                "name": "Daily Card",
                "meaning": "Energy and guidance for today"
            }]
        )

        if not drawn_cards or len(drawn_cards) == 0:
            raise Exception("Failed to draw daily card")

        return {
            "card": drawn_cards[0],
            "is_reversed": drawn_cards[0]["is_reversed"],
            "already_drawn_today": False
        }

    async def create_reading(
        self,
        user_id: str,
        spread_id: Optional[str],
        spread_name: str,
        reading_type: str,
        num_cards: int,
        question: Optional[str] = None,
        profile_id: Optional[str] = None
    ) -> Dict:
        """
        Create a new tarot reading

        Args:
            user_id: User ID
            spread_id: Spread template ID (optional for custom spreads)
            spread_name: Name of the spread
            reading_type: Type of reading (daily_card, three_card, celtic_cross, custom)
            num_cards: Number of cards to draw
            question: User's question (optional)
            profile_id: Birth profile ID for holistic analysis (optional)

        Returns:
            Complete reading with interpretation
        """
        # Fetch spread if using a template
        spread_positions = []
        if spread_id:
            spread = await self.get_spread_by_id(spread_id)
            if spread:
                spread_positions = spread.get("positions", [])

        # If no spread template, create default positions
        if not spread_positions:
            spread_positions = [
                {"position": i + 1, "name": f"Card {i + 1}", "meaning": f"Position {i + 1}"}
                for i in range(num_cards)
            ]

        # Draw cards
        drawn_cards = await self.draw_cards_for_reading(num_cards, spread_positions)

        # Fetch holistic data if profile provided
        holistic_data = None
        if profile_id:
            holistic_data = await self._fetch_holistic_data(profile_id, user_id)

        # Generate interpretation
        interpretation_result = await self._generate_interpretation(
            drawn_cards=drawn_cards,
            question=question,
            spread_name=spread_name,
            holistic_data=holistic_data
        )

        # Store reading in database
        reading_data = {
            "user_id": user_id,
            "profile_id": profile_id,
            "reading_type": reading_type,
            "spread_id": spread_id,
            "spread_name": spread_name,
            "question": question,
            "cards_drawn": drawn_cards,
            "interpretation": interpretation_result["interpretation"],
            "summary": interpretation_result["summary"],
            "astrology_correlations": interpretation_result.get("astrology_correlations"),
            "numerology_correlations": interpretation_result.get("numerology_correlations"),
            "confidence_score": interpretation_result.get("confidence_score", 0.85),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }

        reading = await self.supabase.insert("tarot_readings", reading_data)

        return {
            "reading": reading,
            "cards": drawn_cards,
            "interpretation": interpretation_result
        }

    async def _fetch_holistic_data(self, profile_id: str, user_id: str) -> Optional[Dict]:
        """Fetch birth profile, astrology chart, and numerology data for holistic interpretation"""
        try:
            # Fetch birth profile
            profile = await self.supabase.select(
                "profiles",
                filters={"id": profile_id, "user_id": user_id},
                single=True
            )

            if not profile:
                return None

            holistic_data = {"profile": profile}

            # Fetch astrology chart
            chart = await self.supabase.select(
                "charts",
                filters={"profile_id": profile_id},
                single=True
            )

            if chart:
                holistic_data["chart"] = {
                    "sun_sign": chart.get("sun_sign"),
                    "moon_sign": chart.get("moon_sign"),
                    "ascendant": chart.get("ascendant"),
                    "planets": chart.get("planet_positions", {}),
                }

            # Fetch numerology profile
            numerology_profiles = await self.supabase.select(
                "numerology_profiles",
                filters={"user_id": user_id},
                limit=1
            )

            if numerology_profiles:
                num = numerology_profiles[0]
                holistic_data["numerology"] = {
                    "life_path": num.get("life_path"),
                    "expression": num.get("expression"),
                    "personal_year": num.get("personal_year"),
                }

            return holistic_data

        except Exception as e:
            logger.error(f"Failed to fetch holistic data: {str(e)}")
            return None

    async def _generate_interpretation(
        self,
        drawn_cards: List[Dict],
        question: Optional[str],
        spread_name: str,
        holistic_data: Optional[Dict] = None
    ) -> Dict:
        """
        Generate AI interpretation of the reading
        For now, generates placeholder interpretation
        TODO: Integrate with OpenAI GPT-4 for real AI interpretations
        """
        # Build card summary
        card_names = [
            f"{card['position_name']}: {card['card_name']} ({'Reversed' if card['is_reversed'] else 'Upright'})"
            for card in drawn_cards
        ]

        # Generate summary
        summary = f"Your {spread_name} reading"
        if question:
            summary += f" regarding '{question}'"
        summary += f" reveals {len(drawn_cards)} cards with important messages."

        # Generate detailed interpretation
        interpretation = f"**{spread_name} Reading**\n\n"
        if question:
            interpretation += f"*Question: {question}*\n\n"

        interpretation += "**Cards Drawn:**\n"
        for card in drawn_cards:
            orientation = "Reversed" if card["is_reversed"] else "Upright"
            meaning = card["reversed_meaning"] if card["is_reversed"] else card["upright_meaning"]
            keywords = card["reversed_keywords"] if card["is_reversed"] else card["upright_keywords"]

            interpretation += f"\n**{card['position_name']}** - *{card['position_meaning']}*\n"
            interpretation += f"🃏 **{card['card_name']}** ({orientation})\n"
            interpretation += f"Keywords: {', '.join(keywords[:5])}\n"
            interpretation += f"{meaning}\n"

        # Add holistic correlations if available
        astrology_correlations = None
        numerology_correlations = None

        if holistic_data:
            profile = holistic_data.get("profile", {})
            chart = holistic_data.get("chart")
            numerology = holistic_data.get("numerology")

            interpretation += f"\n\n**Personalized Insights for {profile.get('name', 'You')}**\n\n"

            if chart:
                astrology_correlations = {
                    "sun_sign": chart.get("sun_sign"),
                    "moon_sign": chart.get("moon_sign"),
                    "ascendant": chart.get("ascendant"),
                    "correlation_notes": self._generate_astrology_correlation(drawn_cards, chart)
                }
                interpretation += f"**Astrological Connection**: {astrology_correlations['correlation_notes']}\n\n"

            if numerology:
                numerology_correlations = {
                    "life_path": numerology.get("life_path"),
                    "personal_year": numerology.get("personal_year"),
                    "correlation_notes": self._generate_numerology_correlation(drawn_cards, numerology)
                }
                interpretation += f"**Numerological Connection**: {numerology_correlations['correlation_notes']}\n"

        return {
            "summary": summary,
            "interpretation": interpretation,
            "astrology_correlations": astrology_correlations,
            "numerology_correlations": numerology_correlations,
            "confidence_score": 0.85
        }

    def _generate_astrology_correlation(self, cards: List[Dict], chart: Dict) -> str:
        """Generate correlation between tarot cards and birth chart"""
        sun_sign = chart.get("sun_sign", "")
        moon_sign = chart.get("moon_sign", "")

        # Count major vs minor arcana
        major_count = sum(1 for card in cards if card.get("arcana_type") == "major")

        correlation = ""
        if major_count >= len(cards) * 0.6:  # 60% or more major arcana
            correlation = f"The predominance of Major Arcana cards suggests karmic themes that resonate with your {sun_sign} Sun's life purpose. "

        # Check for element alignment
        elements_in_cards = [card.get("element") for card in cards if card.get("element")]
        if "fire" in elements_in_cards and sun_sign in ["Aries", "Leo", "Sagittarius"]:
            correlation += f"The fire energy in your cards aligns beautifully with your {sun_sign} nature, emphasizing action and passion. "
        elif "water" in elements_in_cards and sun_sign in ["Cancer", "Scorpio", "Pisces"]:
            correlation += f"The water element in your cards reflects your {sun_sign} emotional depth and intuition. "

        if moon_sign:
            correlation += f"Your {moon_sign} Moon suggests paying special attention to emotional undercurrents in this reading."

        return correlation if correlation else f"This reading complements your {sun_sign} solar energy and life path."

    def _generate_numerology_correlation(self, cards: List[Dict], numerology: Dict) -> str:
        """Generate correlation between tarot cards and numerology"""
        life_path = numerology.get("life_path")
        personal_year = numerology.get("personal_year")

        # Check if any card numbers match life path
        card_numbers = [card.get("numerological_value") or (card.get("card_number") % 22) for card in cards]

        correlation = ""
        if life_path in card_numbers:
            correlation = f"Your Life Path {life_path} appears in this reading, indicating alignment with your soul's purpose. "

        if personal_year:
            correlation += f"In your Personal Year {personal_year}, this reading suggests "
            if personal_year in [1, 5, 9]:  # Change years
                correlation += "embracing new beginnings and transformations shown in the cards. "
            elif personal_year in [2, 6]:  # Relationship years
                correlation += "focusing on partnerships and harmony as reflected in the spread. "
            else:
                correlation += "building on foundations with the guidance provided. "

        return correlation if correlation else f"The card numbers resonate with your Life Path {life_path} journey."

    async def get_user_readings(
        self,
        user_id: str,
        limit: int = 20,
        reading_type: Optional[str] = None
    ) -> Dict:
        """Fetch user's tarot readings"""
        try:
            filters = {"user_id": user_id}
            if reading_type:
                filters["reading_type"] = reading_type

            readings = await self.supabase.select(
                "tarot_readings",
                filters=filters,
                limit=limit,
                order_by="created_at DESC"
            )

            return {
                "readings": readings,
                "total_count": len(readings)
            }
        except Exception as e:
            logger.error(f"Failed to fetch user readings: {str(e)}")
            raise

    async def get_reading_by_id(self, reading_id: str, user_id: str) -> Optional[Dict]:
        """Fetch a specific reading"""
        try:
            reading = await self.supabase.select(
                "tarot_readings",
                filters={"id": reading_id, "user_id": user_id},
                single=True
            )
            return reading
        except Exception as e:
            logger.error(f"Failed to fetch reading {reading_id}: {str(e)}")
            return None

    async def update_reading(
        self,
        reading_id: str,
        user_id: str,
        is_favorite: Optional[bool] = None,
        notes: Optional[str] = None
    ) -> Dict:
        """Update reading (favorite status, notes)"""
        try:
            update_data = {"updated_at": datetime.utcnow().isoformat()}

            if is_favorite is not None:
                update_data["is_favorite"] = is_favorite
            if notes is not None:
                update_data["notes"] = notes

            updated = await self.supabase.update(
                "tarot_readings",
                filters={"id": reading_id, "user_id": user_id},
                data=update_data
            )

            return updated
        except Exception as e:
            logger.error(f"Failed to update reading: {str(e)}")
            raise
