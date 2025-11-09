"""
Palm Analysis Orchestrator Service.

Coordinates the AI analysis workflow for palm readings, including:
- Hand detection and validation
- Line detection and classification
- Mount detection and prominence analysis
- Shape classification
- RAG-based interpretation generation
- Cross-domain correlation with astrology and numerology
"""

import asyncio
import logging
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.palmistry import (
    PalmPhoto,
    PalmReading,
    PalmInterpretation,
    AIModel,
)
from app.schemas.palmistry import (
    LineDetection,
    MountDetection,
    PalmReading as PalmReadingSchema,
    PalmInterpretation as PalmInterpretationSchema,
    EventPrediction,
)


logger = logging.getLogger(__name__)


class PalmAnalysisService:
    """
    Orchestrates the complete palm analysis workflow.

    This service coordinates multiple AI models to analyze palm images:
    1. Hand detection and segmentation
    2. Line detection and characterization
    3. Mount detection and prominence
    4. Hand shape classification
    5. Event prediction and timing
    6. RAG-based interpretation generation
    """

    def __init__(self):
        """
        Initialize the analysis service.

        Note: No database session needed - uses Supabase REST API.
        """
        # Model placeholders (will be replaced with actual models)
        self.hand_detector = None
        self.line_detector = None
        self.mount_detector = None
        self.shape_classifier = None

        # Model versions (track in database)
        self.model_versions = {
            "hand_detection": "v1.0.0-placeholder",
            "line_detection": "v1.0.0-placeholder",
            "mount_detection": "v1.0.0-placeholder",
            "shape_classification": "v1.0.0-placeholder",
            "rag_model": "gpt-4-turbo-placeholder"
        }

    async def analyze_palm(
        self,
        photo_id: str,
        image_url: str,
        hand_type: str,
        view_type: str,
        profile_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict:
        """
        Perform complete palm analysis with optional holistic integration.

        Args:
            photo_id: Photo UUID to analyze
            image_url: URL of the palm image
            hand_type: Hand type ("left" or "right")
            view_type: View type ("front", "back", etc.)
            profile_id: Optional birth profile ID for holistic analysis
            user_id: Optional user ID for fetching holistic data

        Returns:
            Dictionary with analysis results including cross-domain correlations

        Raises:
            ValueError: If analysis fails
            Exception: If unexpected error occurs
        """
        start_time = datetime.utcnow()

        try:
            logger.info(
                f"Starting palm analysis: photo_id={photo_id}, "
                f"hand={hand_type}, view={view_type}, profile_id={profile_id}"
            )

            # Fetch holistic data if profile_id is provided
            holistic_data = None
            if profile_id and user_id:
                holistic_data = await self._fetch_holistic_data(profile_id, user_id)
                logger.info(f"Fetched holistic data for profile: {profile_id}")

            # 2. Detect and validate hand (placeholder)
            hand_data = await self._detect_hand_placeholder(image_url)

            # 3. Detect palm lines (placeholder)
            lines = await self._detect_lines_placeholder(image_url, hand_data)

            # 4. Detect palm mounts (placeholder)
            mounts = await self._detect_mounts_placeholder(image_url, hand_data)

            # 5. Classify hand shape (placeholder)
            hand_shape = await self._classify_hand_shape_placeholder(image_url)

            # 6. Predict life events (placeholder)
            life_events = await self._predict_life_events_placeholder(lines, mounts, hand_shape)

            # 7. Extract personality traits (placeholder)
            personality_traits = await self._extract_personality_traits_placeholder(
                lines, mounts, hand_shape
            )

            # 8. Calculate overall confidence
            overall_confidence = self._calculate_confidence_placeholder(
                hand_data, lines, mounts
            )

            # 9. Generate interpretation (placeholder with holistic data)
            interpretation = await self._generate_interpretation_placeholder(
                hand_type, hand_shape, lines, mounts, life_events, personality_traits,
                holistic_data=holistic_data
            )

            # Calculate processing time
            processing_time_ms = int(
                (datetime.utcnow() - start_time).total_seconds() * 1000
            )

            logger.info(
                f"Palm analysis completed: photo_id={photo_id}, "
                f"confidence={overall_confidence:.2f}, time={processing_time_ms}ms"
            )

            return {
                "hand_shape": hand_shape,
                "lines": [line.dict() if hasattr(line, 'dict') else line for line in lines],
                "mounts": [mount.dict() if hasattr(mount, 'dict') else mount for mount in mounts],
                "confidence": overall_confidence,
                "model_version": self.model_versions["hand_detection"],
                "processing_time_ms": processing_time_ms,  # Add processing time
                "interpretation": {
                    "summary": interpretation["summary"],
                    "detailed_analysis": interpretation["detailed_analysis"],
                    "personality_traits": personality_traits,
                    "life_events": [event.dict() if hasattr(event, 'dict') else event for event in life_events],
                    "recommendations": interpretation["recommendations"],
                    "astrology_correlations": interpretation.get("astrology_correlations"),
                    "numerology_correlations": interpretation.get("numerology_correlations"),
                    "rag_sources": interpretation.get("rag_sources", [])
                }
            }

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Palm analysis failed: {str(e)}")
            raise Exception(f"Analysis failed: {str(e)}")

    async def _get_photo(self, photo_id: UUID, user_id: UUID) -> Optional[PalmPhoto]:
        """Fetch photo from database."""
        stmt = select(PalmPhoto).where(
            PalmPhoto.id == photo_id,
            PalmPhoto.user_id == user_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _detect_hand(self, photo: PalmPhoto) -> Dict:
        """
        Detect and segment hand in image.

        This is a placeholder implementation. In production, this would use
        MediaPipe Hands or a custom trained model.

        Args:
            photo: PalmPhoto object

        Returns:
            Hand detection data including landmarks and bounding box
        """
        # PLACEHOLDER: Simulate hand detection
        # In production, this would:
        # 1. Load image from photo.image_url
        # 2. Run MediaPipe Hands or custom model
        # 3. Extract hand landmarks and bounding box
        # 4. Return structured detection data

        return {
            "detected": True,
            "confidence": 0.95,
            "landmarks": self._generate_mock_landmarks(),
            "bounding_box": {"x": 100, "y": 100, "width": 400, "height": 600},
        }

    def _generate_mock_landmarks(self) -> List[Dict]:
        """Generate mock hand landmarks for placeholder."""
        # 21 landmarks as per MediaPipe Hands
        return [
            {"x": random.random(), "y": random.random(), "z": 0.0}
            for _ in range(21)
        ]

    async def _detect_lines(
        self,
        photo: PalmPhoto,
        hand_data: Dict
    ) -> List[Dict]:
        """
        Detect palm lines.

        Placeholder implementation. Production version would use:
        - U-Net or ResNet for line segmentation
        - Custom trained model on palm line dataset
        - Line tracing and characterization algorithms

        Args:
            photo: PalmPhoto object
            hand_data: Hand detection results

        Returns:
            List of detected lines with characteristics
        """
        # PLACEHOLDER: Mock line detection
        major_lines = [
            {
                "line_type": "life",
                "confidence": 0.92,
                "coordinates": [[0.2, 0.3], [0.3, 0.5], [0.35, 0.8]],
                "characteristics": {
                    "length": "long",
                    "depth": "deep",
                    "clarity": "clear",
                    "breaks": [],
                    "branches": 2
                }
            },
            {
                "line_type": "head",
                "confidence": 0.88,
                "coordinates": [[0.1, 0.4], [0.5, 0.45], [0.7, 0.5]],
                "characteristics": {
                    "length": "medium",
                    "depth": "moderate",
                    "clarity": "clear",
                    "slope": "slight_downward",
                    "breaks": []
                }
            },
            {
                "line_type": "heart",
                "confidence": 0.85,
                "coordinates": [[0.1, 0.2], [0.5, 0.25], [0.8, 0.3]],
                "characteristics": {
                    "length": "long",
                    "depth": "deep",
                    "curve": "moderate",
                    "branches": 3
                }
            },
            {
                "line_type": "fate",
                "confidence": 0.78,
                "coordinates": [[0.5, 0.8], [0.5, 0.5], [0.5, 0.2]],
                "characteristics": {
                    "length": "long",
                    "depth": "moderate",
                    "clarity": "intermittent",
                    "starting_point": "wrist"
                }
            }
        ]

        return major_lines

    async def _detect_mounts(
        self,
        photo: PalmPhoto,
        hand_data: Dict
    ) -> List[Dict]:
        """
        Detect palm mounts and their prominence.

        Placeholder implementation. Production version would use:
        - CNN for mount region classification
        - Depth analysis from multi-angle images
        - Prominence scoring algorithm

        Args:
            photo: PalmPhoto object
            hand_data: Hand detection results

        Returns:
            List of detected mounts with prominence levels
        """
        # PLACEHOLDER: Mock mount detection
        mounts = [
            {
                "mount_name": "Venus",
                "prominence": "prominent",
                "confidence": 0.89,
                "area_coordinates": [[0.1, 0.6], [0.3, 0.6], [0.3, 0.9], [0.1, 0.9]]
            },
            {
                "mount_name": "Jupiter",
                "prominence": "moderate",
                "confidence": 0.82,
                "area_coordinates": [[0.1, 0.1], [0.2, 0.1], [0.2, 0.3], [0.1, 0.3]]
            },
            {
                "mount_name": "Saturn",
                "prominence": "moderate",
                "confidence": 0.85,
                "area_coordinates": [[0.4, 0.05], [0.5, 0.05], [0.5, 0.25], [0.4, 0.25]]
            },
            {
                "mount_name": "Apollo",
                "prominence": "prominent",
                "confidence": 0.87,
                "area_coordinates": [[0.6, 0.05], [0.7, 0.05], [0.7, 0.25], [0.6, 0.25]]
            },
            {
                "mount_name": "Mercury",
                "prominence": "flat",
                "confidence": 0.79,
                "area_coordinates": [[0.8, 0.1], [0.9, 0.1], [0.9, 0.3], [0.8, 0.3]]
            },
            {
                "mount_name": "Luna",
                "prominence": "very_prominent",
                "confidence": 0.91,
                "area_coordinates": [[0.7, 0.5], [0.9, 0.5], [0.9, 0.8], [0.7, 0.8]]
            }
        ]

        return mounts

    async def _classify_hand_shape(
        self,
        photo: PalmPhoto,
        hand_data: Dict
    ) -> str:
        """
        Classify hand shape into elemental categories.

        Placeholder implementation. Production version would use:
        - CNN for shape classification
        - Finger length ratio calculations
        - Palm aspect ratio analysis

        Args:
            photo: PalmPhoto object
            hand_data: Hand detection results

        Returns:
            Hand shape: "earth", "air", "fire", or "water"
        """
        # PLACEHOLDER: Random classification
        shapes = ["earth", "air", "fire", "water"]
        # In production, this would analyze finger/palm proportions
        return random.choice(shapes)

    async def _predict_life_events(
        self,
        lines: List[Dict],
        mounts: List[Dict],
        hand_shape: str
    ) -> List[Dict]:
        """
        Predict life events based on palm features.

        This uses traditional palmistry timing methods to estimate
        when certain events may occur based on line positions.

        Args:
            lines: Detected palm lines
            mounts: Detected palm mounts
            hand_shape: Classified hand shape

        Returns:
            List of predicted life events
        """
        # PLACEHOLDER: Mock predictions
        events = [
            {
                "event_type": "career",
                "description": "Significant career advancement or change in professional direction",
                "age_range": "28-32",
                "confidence": 0.75,
                "zone": "fate_line_intersection"
            },
            {
                "event_type": "relationship",
                "description": "Important relationship milestone or significant partnership",
                "age_range": "25-27",
                "confidence": 0.68,
                "zone": "heart_line_branch"
            },
            {
                "event_type": "health",
                "description": "Period requiring attention to physical well-being",
                "age_range": "45-50",
                "confidence": 0.62,
                "zone": "life_line_island"
            }
        ]

        return events

    async def _extract_personality_traits(
        self,
        lines: List[Dict],
        mounts: List[Dict],
        hand_shape: str
    ) -> List[str]:
        """
        Extract personality traits from palm features.

        Args:
            lines: Detected palm lines
            mounts: Detected palm mounts
            hand_shape: Classified hand shape

        Returns:
            List of personality trait descriptions
        """
        # PLACEHOLDER: Mock traits based on hand shape
        trait_map = {
            "earth": [
                "Practical and grounded",
                "Reliable and hardworking",
                "Values stability and security"
            ],
            "air": [
                "Intellectual and analytical",
                "Communicative and social",
                "Adaptable and curious"
            ],
            "fire": [
                "Energetic and passionate",
                "Confident and ambitious",
                "Creative and spontaneous"
            ],
            "water": [
                "Intuitive and empathetic",
                "Emotional and sensitive",
                "Imaginative and artistic"
            ]
        }

        return trait_map.get(hand_shape, trait_map["earth"])

    def _calculate_confidence(
        self,
        hand_data: Dict,
        lines: List[Dict],
        mounts: List[Dict]
    ) -> float:
        """
        Calculate overall reading confidence score.

        Args:
            hand_data: Hand detection results
            lines: Detected lines
            mounts: Detected mounts

        Returns:
            Confidence score (0.0-1.0)
        """
        # Calculate weighted average of individual confidences
        hand_conf = hand_data.get("confidence", 0.5)

        # Calculate mean confidence for lines
        if lines:
            line_confs = [l.get("confidence", 0.5) for l in lines]
            line_conf = sum(line_confs) / len(line_confs)
        else:
            line_conf = 0.5

        # Calculate mean confidence for mounts
        if mounts:
            mount_confs = [m.get("confidence", 0.5) for m in mounts]
            mount_conf = sum(mount_confs) / len(mount_confs)
        else:
            mount_conf = 0.5

        # Weighted average (hand detection most important)
        overall = (hand_conf * 0.5) + (line_conf * 0.3) + (mount_conf * 0.2)

        return round(overall, 2)

    async def _create_reading(
        self,
        photo_id: UUID,
        user_id: UUID,
        hand_type: str,
        hand_shape: str,
        lines: List[Dict],
        mounts: List[Dict],
        life_events: List[Dict],
        personality_traits: List[str],
        overall_confidence: float,
        processing_time_ms: int
    ) -> PalmReading:
        """Create and save PalmReading record to database."""
        reading = PalmReading(
            photo_id=photo_id,
            user_id=user_id,
            hand_type=hand_type,
            hand_shape=hand_shape,
            lines_detected=lines,
            mounts_detected=mounts,
            life_events=life_events,
            personality_traits=personality_traits,
            overall_confidence=overall_confidence,
            processing_time_ms=processing_time_ms,
            model_version=self.model_versions["line_detection"],
            detection_scores={
                "hand": 0.95,
                "lines": 0.85,
                "mounts": 0.82
            }
        )

        self.db.add(reading)
        await self.db.commit()
        await self.db.refresh(reading)

        return reading

    async def _generate_interpretation(
        self,
        reading_id: UUID,
        user_id: UUID,
        reading_data: Dict
    ) -> PalmInterpretation:
        """
        Generate RAG-based natural language interpretation.

        In production, this would:
        1. Query vector database for relevant palmistry knowledge
        2. Fetch user's astrology chart for correlation
        3. Fetch user's numerology profile for correlation
        4. Use GPT-4 to generate personalized interpretation
        5. Store sources and metadata

        Args:
            reading_id: PalmReading UUID
            user_id: User UUID
            reading_data: Extracted reading features

        Returns:
            PalmInterpretation record
        """
        # PLACEHOLDER: Generate mock interpretation
        hand_shape = reading_data.get("hand_shape", "earth")
        personality = reading_data.get("personality_traits", [])
        events = reading_data.get("life_events", [])

        # Create summary
        summary = (
            f"Your {reading_data['hand_type']} hand shows a {hand_shape} shape, "
            f"indicating {personality[0].lower()} characteristics. "
            f"The palm lines suggest {len(events)} significant life periods ahead."
        )

        # Create detailed analysis
        detailed_analysis = f"""
Your palm reading reveals several interesting insights:

**Hand Shape ({hand_shape.title()}):**
{' '.join(personality)}

**Major Lines:**
- **Life Line:** Strong and clear, indicating good vitality and resilience
- **Heart Line:** Curved and long, suggesting emotional depth and strong relationships
- **Head Line:** Moderate slope, showing balanced thinking between logic and intuition
- **Fate Line:** Present and clear, indicating a defined career path

**Mounts:**
- **Mount of Venus:** Prominent, showing warmth and appreciation for beauty
- **Mount of Luna:** Well-developed, indicating strong imagination and intuition
- **Mount of Apollo:** Moderate, suggesting artistic appreciation

**Life Events:**
{self._format_events(events)}

This reading is based on your {reading_data['hand_type']} hand. For a complete analysis,
comparing both hands provides insight into inherited traits vs. developed characteristics.
        """.strip()

        # Create recommendations
        recommendations = [
            "Compare this reading with your right hand for complete insights",
            "Consider consulting with an astrologer to correlate with your birth chart",
            "Focus on developing the positive traits indicated by your hand shape",
            "Be mindful of the predicted life periods and prepare accordingly"
        ]

        # Create interpretation record
        interpretation = PalmInterpretation(
            reading_id=reading_id,
            user_id=user_id,
            summary=summary,
            detailed_analysis=detailed_analysis,
            personality_traits=personality,
            life_events=[
                EventPrediction(**event).dict() for event in events
            ],
            recommendations=recommendations,
            rag_sources=[
                "Cheiro's Language of the Hand",
                "Practical Palmistry by Saint-Germain",
                "The Complete Guide to Palmistry by Dennis Fairchild"
            ],
            model_version=self.model_versions["rag_model"],
            generation_parameters={
                "temperature": 0.7,
                "model": "gpt-4-turbo"
            },
            coherence_score=0.88,
            relevance_score=0.92
        )

        self.db.add(interpretation)
        await self.db.commit()
        await self.db.refresh(interpretation)

        return interpretation

    def _format_events(self, events: List[Dict]) -> str:
        """Format life events for interpretation text."""
        if not events:
            return "No specific events predicted at this time."

        formatted = []
        for event in events:
            formatted.append(
                f"- **Age {event['age_range']}** ({event['event_type'].title()}): "
                f"{event['description']}"
            )

        return "\n".join(formatted)

    async def compare_hands(
        self,
        user_id: UUID,
        left_reading_id: Optional[UUID] = None,
        right_reading_id: Optional[UUID] = None
    ) -> Dict:
        """
        Compare left and right hand readings.

        Args:
            user_id: User UUID
            left_reading_id: Left hand reading UUID (optional, will fetch latest if not provided)
            right_reading_id: Right hand reading UUID (optional, will fetch latest if not provided)

        Returns:
            Comparison analysis with key differences
        """
        # PLACEHOLDER: Fetch readings and generate comparison
        # In production, this would:
        # 1. Fetch both readings from database
        # 2. Compare features systematically
        # 3. Generate RAG-based comparison interpretation
        # 4. Highlight key differences and their meanings

        return {
            "left_reading": None,
            "right_reading": None,
            "comparison_analysis": "Comparison analysis placeholder",
            "key_differences": [
                "Left hand shows inherited traits, right hand shows developed characteristics",
                "Life line length differs, suggesting conscious lifestyle choices",
                "Mount prominences vary, indicating growth in specific areas"
            ],
            "unified_interpretation": "Combined interpretation placeholder"
        }

    # ========================================================================
    # SIMPLIFIED PLACEHOLDER METHODS (No database dependency)
    # ========================================================================

    async def _detect_hand_placeholder(self, image_url: str) -> Dict:
        """Placeholder hand detection."""
        return {
            "detected": True,
            "confidence": 0.92,
            "bounding_box": [[100, 100], [400, 600]]
        }

    async def _detect_lines_placeholder(self, image_url: str, hand_data: Dict) -> List:
        """Placeholder line detection."""
        return [
            {
                "line_type": "life",
                "confidence": 0.88,
                "coordinates": [[150, 200], [200, 400]],
                "characteristics": {"length": "long", "depth": "deep", "clarity": "clear"}
            },
            {
                "line_type": "head",
                "confidence": 0.85,
                "coordinates": [[150, 180], [350, 250]],
                "characteristics": {"length": "medium", "slope": "slight", "branches": 2}
            },
            {
                "line_type": "heart",
                "confidence": 0.90,
                "coordinates": [[150, 150], [380, 180]],
                "characteristics": {"length": "long", "curve": "moderate", "clarity": "clear"}
            }
        ]

    async def _detect_mounts_placeholder(self, image_url: str, hand_data: Dict) -> List:
        """Placeholder mount detection."""
        return [
            {
                "mount_name": "Jupiter",
                "prominence": "prominent",  # Changed from "high" to match schema
                "confidence": 0.82,
                "area_coordinates": [[0.3, 0.2], [0.4, 0.2], [0.4, 0.3], [0.3, 0.3]]  # Required by schema
            },
            {
                "mount_name": "Saturn",
                "prominence": "moderate",  # Changed from "medium" to match schema
                "confidence": 0.78,
                "area_coordinates": [[0.4, 0.2], [0.5, 0.2], [0.5, 0.3], [0.4, 0.3]]
            },
            {
                "mount_name": "Apollo",
                "prominence": "prominent",  # Changed from "high" to match schema
                "confidence": 0.85,
                "area_coordinates": [[0.5, 0.2], [0.6, 0.2], [0.6, 0.3], [0.5, 0.3]]
            }
        ]

    async def _classify_hand_shape_placeholder(self, image_url: str) -> str:
        """Placeholder hand shape classification."""
        shapes = ["earth", "air", "fire", "water"]
        return random.choice(shapes)

    async def _predict_life_events_placeholder(
        self, lines: List, mounts: List, hand_shape: str
    ) -> List:
        """Placeholder life event prediction."""
        return [
            {
                "event_type": "career",
                "age_range": "28-32",
                "description": "Significant career advancement or change in professional direction",
                "confidence": 0.75
            },
            {
                "event_type": "relationship",
                "age_range": "35-40",
                "description": "Important relationship milestone or deepening of bonds",
                "confidence": 0.70
            }
        ]

    async def _extract_personality_traits_placeholder(
        self, lines: List, mounts: List, hand_shape: str
    ) -> List[str]:
        """Placeholder personality trait extraction."""
        return [
            "Natural leadership abilities and confidence",
            "Strong analytical and logical thinking",
            "Compassionate and emotionally intelligent",
            "Creative problem-solver with artistic tendencies"
        ]

    def _calculate_confidence_placeholder(
        self, hand_data: Dict, lines: List, mounts: List
    ) -> float:
        """Calculate overall confidence score."""
        hand_conf = hand_data.get("confidence", 0.85)
        line_confs = [l.get("confidence", 0.8) for l in lines]
        mount_confs = [m.get("confidence", 0.8) for m in mounts]
        
        all_confs = [hand_conf] + line_confs + mount_confs
        return round(sum(all_confs) / len(all_confs), 2)

    async def _generate_interpretation_placeholder(
        self,
        hand_type: str,
        hand_shape: str,
        lines: List,
        mounts: List,
        life_events: List,
        personality_traits: List[str],
        holistic_data: Optional[Dict] = None
    ) -> Dict:
        """
        Generate placeholder RAG-based interpretation with optional holistic integration.

        Args:
            hand_type: Left or right hand
            hand_shape: Earth, Air, Fire, or Water
            lines: Detected palm lines
            mounts: Detected palm mounts
            life_events: Predicted life events
            personality_traits: Extracted personality traits
            holistic_data: Optional dict with profile, chart, and numerology data

        Returns:
            Dictionary with interpretation and cross-domain correlations
        """
        # Base interpretation
        summary = f"Your {hand_type} {hand_shape} hand reveals a unique blend of characteristics. "
        detailed_analysis = f"Based on the analysis of your {hand_type} palm, several key features stand out:\n\n"
        detailed_analysis += f"**Hand Shape ({hand_shape.title()})**: This indicates {self._get_shape_meaning(hand_shape)}.\n\n"

        # Add holistic correlations if data is available
        astrology_correlations = None
        numerology_correlations = None

        if holistic_data:
            profile = holistic_data.get("profile")
            chart = holistic_data.get("chart")
            numerology = holistic_data.get("numerology")

            if profile:
                name = profile.get("name")
                summary = f"{name}, your {hand_type} {hand_shape} hand reveals fascinating insights that align with your birth chart and numerology. "

            # Add astrology correlations
            if chart:
                astrology_correlations = {
                    "sun_sign": chart.get("sun_sign"),
                    "moon_sign": chart.get("moon_sign"),
                    "ascendant": chart.get("ascendant"),
                    "correlation_notes": self._generate_astrology_correlation(hand_shape, chart)
                }

                detailed_analysis += f"\n**Astrological Alignment**: Your {hand_shape} hand beautifully complements your "
                detailed_analysis += f"{chart.get('ascendant', '')} rising and {chart.get('sun_sign', '')} Sun. "
                detailed_analysis += f"This combination suggests {self._get_element_correlation(hand_shape, chart)}.\n\n"

            # Add numerology correlations
            if numerology:
                numerology_correlations = {
                    "life_path": numerology.get("life_path"),
                    "destiny_number": numerology.get("destiny_number"),
                    "personal_year": numerology.get("personal_year"),
                    "correlation_notes": self._generate_numerology_correlation(hand_shape, numerology)
                }

                detailed_analysis += f"\n**Numerological Harmony**: Your Life Path {numerology.get('life_path', '')} "
                detailed_analysis += f"resonates with the patterns in your palm, particularly in the {self._get_numerology_palm_link(numerology)}.\n\n"

        # Standard analysis continues
        detailed_analysis += f"**Major Lines**: Your life, head, and heart lines show clear definition, suggesting "
        detailed_analysis += f"emotional depth, intellectual clarity, and vitality. The specific formations indicate "
        detailed_analysis += f"periods of significant growth and transformation.\n\n"
        detailed_analysis += f"**Mounts**: The prominence of certain mounts reflects your natural talents and inclinations. "
        detailed_analysis += f"These elevations in the palm correspond to different planetary influences in traditional palmistry."

        return {
            "summary": summary,
            "detailed_analysis": detailed_analysis,
            "recommendations": [
                "Focus on developing your natural leadership abilities",
                "Trust your intuition in decision-making processes",
                "Maintain balance between professional ambitions and personal relationships",
                "Consider creative pursuits to channel your artistic energy"
            ],
            "astrology_correlations": astrology_correlations,
            "numerology_correlations": numerology_correlations,
            "rag_sources": ["Classical Palmistry Vol. 1", "Modern Hand Analysis", "Vedic Palm Reading", "Cross-Domain Astrology"]
        }

    def _get_shape_meaning(self, shape: str) -> str:
        """Get meaning for hand shape."""
        meanings = {
            "earth": "practical, grounded nature with strong work ethic",
            "air": "intellectual curiosity and excellent communication skills",
            "fire": "passionate, energetic personality with natural charisma",
            "water": "deep emotional sensitivity and strong intuitive abilities"
        }
        return meanings.get(shape, "a unique combination of traits")

    async def _fetch_holistic_data(self, profile_id: str, user_id: str) -> Optional[Dict]:
        """
        Fetch birth profile, astrology chart, and numerology data for holistic analysis.

        Args:
            profile_id: Birth profile UUID
            user_id: User UUID

        Returns:
            Dictionary with profile, chart, and numerology data, or None if not found
        """
        try:
            from app.core.supabase_client import SupabaseClient

            supabase = SupabaseClient()

            # Fetch birth profile
            profile = await supabase.select(
                "profiles",
                filters={"id": profile_id, "user_id": user_id},
                single=True
            )

            if not profile:
                logger.warning(f"Profile not found: {profile_id}")
                return None

            holistic_data = {"profile": profile}

            # Fetch astrology chart if exists
            chart = await supabase.select(
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
                    "houses": chart.get("house_positions", {}),
                }

            # Fetch numerology profile if exists
            numerology_profiles = await supabase.select(
                "numerology_profiles",
                filters={"user_id": user_id, "name": profile.get("name")},
                limit=1
            )

            if numerology_profiles:
                num = numerology_profiles[0]
                holistic_data["numerology"] = {
                    "life_path": num.get("life_path"),
                    "expression": num.get("expression"),
                    "soul_urge": num.get("soul_urge"),
                    "personality": num.get("personality_number"),
                    "destiny_number": num.get("destiny_number"),
                    "personal_year": num.get("personal_year"),
                }

            logger.info(f"Holistic data fetched successfully for profile: {profile_id}")
            return holistic_data

        except Exception as e:
            logger.error(f"Failed to fetch holistic data: {str(e)}")
            return None

    def _generate_astrology_correlation(self, hand_shape: str, chart: Dict) -> str:
        """Generate astrology correlation notes."""
        sun_sign = chart.get("sun_sign", "")
        ascendant = chart.get("ascendant", "")

        # Element mapping
        fire_signs = ["Aries", "Leo", "Sagittarius"]
        earth_signs = ["Taurus", "Virgo", "Capricorn"]
        air_signs = ["Gemini", "Libra", "Aquarius"]
        water_signs = ["Cancer", "Scorpio", "Pisces"]

        hand_shape_lower = hand_shape.lower()

        if hand_shape_lower == "fire" and (sun_sign in fire_signs or ascendant in fire_signs):
            return f"Strong fire element alignment - your {hand_shape} hand perfectly matches your fiery astrological nature, amplifying your natural energy and passion."
        elif hand_shape_lower == "earth" and (sun_sign in earth_signs or ascendant in earth_signs):
            return f"Grounded earth element harmony - your practical {hand_shape} hand reflects your stable and methodical astrological foundation."
        elif hand_shape_lower == "air" and (sun_sign in air_signs or ascendant in air_signs):
            return f"Intellectual air element synergy - your {hand_shape} hand mirrors your communicative and analytical astrological traits."
        elif hand_shape_lower == "water" and (sun_sign in water_signs or ascendant in water_signs):
            return f"Emotional water element resonance - your sensitive {hand_shape} hand aligns with your intuitive and empathetic astrological nature."
        else:
            return f"Complementary element balance - your {hand_shape} hand balances your {sun_sign} Sun and {ascendant} rising, creating a well-rounded energy."

    def _get_element_correlation(self, hand_shape: str, chart: Dict) -> str:
        """Get element correlation description."""
        return "a harmonious blend of practical and intuitive energies, with potential for both grounding and expansion"

    def _generate_numerology_correlation(self, hand_shape: str, numerology: Dict) -> str:
        """Generate numerology correlation notes."""
        life_path = numerology.get("life_path")
        
        # Number-hand correlations
        if life_path in [1, 8, 9]:  # Leadership numbers
            return f"Life Path {life_path}'s leadership qualities are reflected in the strength of your major palm lines, particularly the fate line."
        elif life_path in [2, 6]:  # Harmony numbers
            return f"Life Path {life_path}'s harmonious nature is visible in the balanced curves of your heart and head lines."
        elif life_path in [3, 5]:  # Expression numbers
            return f"Life Path {life_path}'s creative and expressive energy shows in the prominence of your mount of Venus."
        elif life_path in [4, 7]:  # Analytical numbers
            return f"Life Path {life_path}'s analytical mindset is evident in the clarity and precision of your head line."
        else:
            return f"Life Path {life_path}'s unique qualities resonate throughout your palm's landscape."

    def _get_numerology_palm_link(self, numerology: Dict) -> str:
        """Get specific palm feature linked to numerology."""
        life_path = numerology.get("life_path", 0)
        
        if life_path in [1, 8]:
            return "strength and clarity of your fate line"
        elif life_path in [2, 6]:
            return "harmonious balance of your heart and head lines"
        elif life_path in [3, 5]:
            return "prominence of your mounts of Venus and Mercury"
        elif life_path in [4, 7]:
            return "precision and depth of your head line"
        else:
            return "overall palm configuration"
