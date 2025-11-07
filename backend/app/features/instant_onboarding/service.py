"""
Business logic for Instant Onboarding feature.

Handles WhatsApp bot integration, quick chart generation,
voice input, and multi-language support for zero-friction onboarding.
"""

from typing import Optional, Dict, Any, List, Tuple
from uuid import UUID, uuid4
from datetime import datetime, date, time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
import secrets
import re
import json
import traceback

from app.features.instant_onboarding.models import (
    InstantOnboardingSession,
    InstantOnboardingProfile,
    SessionStatus,
    OnboardingChannel
)
from app.features.instant_onboarding.schemas import (
    SessionStartRequest,
    SessionStartResponse,
    CollectDataRequest,
    CollectDataResponse,
    QuickChartRequest,
    QuickChartResponse,
    WhatsAppMessageRequest,
    WhatsAppResponse,
    VoiceInputRequest,
    VoiceInputResponse
)
from app.models.profile import Profile
from app.services.astrology import VedicAstrologyService
from app.core.config import settings

logger = logging.getLogger(__name__)


# Multi-language prompts
LANGUAGE_PROMPTS = {
    "en": {
        "welcome": "Welcome! Let's create your birth chart in 90 seconds. What's your name?",
        "ask_name": "What's your name?",
        "ask_date": "What's your date of birth? (DD/MM/YYYY or DD-MM-YYYY)",
        "ask_time": "What time were you born? (HH:MM AM/PM or 24-hour format)",
        "ask_place": "Where were you born? (City, Country)",
        "generating": "Generating your chart...",
        "complete": "Your chart is ready! 🎉",
        "error": "Sorry, I didn't understand. Could you try again?",
    },
    "hi": {
        "welcome": "स्वागत है! आइए 90 सेकंड में आपका जन्म कुंडली बनाते हैं। आपका नाम क्या है?",
        "ask_name": "आपका नाम क्या है?",
        "ask_date": "आपकी जन्म तिथि क्या है? (DD/MM/YYYY या DD-MM-YYYY)",
        "ask_time": "आप किस समय पैदा हुए थे? (HH:MM AM/PM या 24-घंटे प्रारूप)",
        "ask_place": "आप कहाँ पैदा हुए थे? (शहर, देश)",
        "generating": "आपकी कुंडली बनाई जा रही है...",
        "complete": "आपकी कुंडली तैयार है! 🎉",
        "error": "क्षमा करें, मैं समझ नहीं पाया। क्या आप फिर से कोशिश कर सकते हैं?",
    }
}


class InstantOnboardingService:
    """
    Service for Instant Onboarding feature.

    Handles:
    - Session management
    - WhatsApp bot integration
    - Quick chart generation
    - Voice input processing
    - Multi-language support
    - NLP data extraction
    """

    def __init__(self):
        self._initialized = False
        self.astrology_service = VedicAstrologyService()

    def initialize(self):
        """Initialize the service."""
        if self._initialized:
            return

        logger.info("Initializing Instant Onboarding service")
        self._initialized = True

    # Session Management

    async def start_session(
        self,
        db: AsyncSession,
        request: SessionStartRequest
    ) -> SessionStartResponse:
        """
        Start a new onboarding session.

        Args:
            db: Database session
            request: Session start request

        Returns:
            Session start response with session key
        """
        logger.info(f"Starting new session: channel={request.channel}, lang={request.language}")

        # Generate unique session key
        session_key = self._generate_session_key()

        # Create session
        session = InstantOnboardingSession(
            session_key=session_key,
            channel=request.channel,
            language=request.language,
            phone_number=request.phone_number,
            ip_address=request.ip_address,
            user_agent=request.user_agent,
            status=SessionStatus.COLLECTING_DATA,
            current_step=0,
            collected_data={},
            steps_completed=[]
        )

        db.add(session)
        await db.commit()
        await db.refresh(session)

        # Get welcome message
        prompts = LANGUAGE_PROMPTS.get(request.language, LANGUAGE_PROMPTS["en"])

        return SessionStartResponse(
            session_id=session.id,
            session_key=session_key,
            status=session.status,
            next_step="name",
            message=prompts["welcome"]
        )

    async def collect_data(
        self,
        db: AsyncSession,
        request: CollectDataRequest
    ) -> CollectDataResponse:
        """
        Collect and validate data for onboarding session.

        Args:
            db: Database session
            request: Data collection request

        Returns:
            Collection response with validation status
        """
        # Get session
        result = await db.execute(
            select(InstantOnboardingSession).where(
                InstantOnboardingSession.session_key == request.session_key
            )
        )
        session = result.scalar_one_or_none()

        if not session:
            raise ValueError("Session not found")

        # Merge new data with existing
        session.collected_data.update(request.data)

        # Validate and determine next step
        next_step, missing_fields = self._determine_next_step(session.collected_data)

        session.current_step += 1
        session.updated_at = datetime.utcnow()

        # Get prompt for next step
        prompts = LANGUAGE_PROMPTS.get(session.language, LANGUAGE_PROMPTS["en"])
        message = self._get_prompt_for_step(next_step, prompts)

        # Check if complete
        is_complete = len(missing_fields) == 0

        if is_complete:
            session.status = SessionStatus.GENERATING_CHART
            message = prompts["generating"]

        await db.commit()
        await db.refresh(session)

        return CollectDataResponse(
            session_id=session.id,
            status=session.status,
            current_step=session.current_step,
            next_step=next_step,
            message=message,
            is_complete=is_complete,
            missing_fields=missing_fields
        )

    async def quick_chart(
        self,
        db: AsyncSession,
        request: QuickChartRequest,
        user_id: Optional[UUID] = None
    ) -> QuickChartResponse:
        """
        Generate quick birth chart.

        Args:
            db: Database session
            request: Quick chart request
            user_id: Optional user ID

        Returns:
            Quick chart response with summary
        """
        logger.info(f"Generating quick chart: session_key={request.session_key}")

        # Get data from session or request
        if request.session_key:
            result = await db.execute(
                select(InstantOnboardingSession).where(
                    InstantOnboardingSession.session_key == request.session_key
                )
            )
            session = result.scalar_one_or_none()
            if not session:
                raise ValueError("Session not found")

            data = session.collected_data
        else:
            # Use directly provided data
            data = {
                "name": request.name,
                "birth_date": request.birth_date,
                "birth_time": request.birth_time,
                "birth_place": request.birth_place,
                "latitude": request.latitude,
                "longitude": request.longitude,
                "timezone": request.timezone
            }
            # Create ephemeral session
            session_key = self._generate_session_key()
            session = InstantOnboardingSession(
                session_key=session_key,
                channel=OnboardingChannel.WEB,
                language=request.language,
                status=SessionStatus.GENERATING_CHART,
                collected_data=data
            )
            db.add(session)

        # Validate required data
        required = ["name", "birth_date", "birth_time", "latitude", "longitude"]
        missing = [f for f in required if not data.get(f)]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        # Generate chart (basic calculation) - do this first to avoid DB issues
        try:
            chart_data = self.astrology_service.calculate_birth_chart(
                name=data["name"],
                birth_date=data["birth_date"],
                birth_time=data["birth_time"],
                latitude=data["latitude"],
                longitude=data["longitude"],
                timezone_str=data.get("timezone", "UTC"),
                city=data.get("birth_place", "Unknown")
            )
        except Exception as e:
            logger.error(f"Chart calculation failed: {type(e).__name__}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise ValueError(f"Chart calculation failed: {type(e).__name__}: {str(e)}")

        # For unauthenticated users, skip database persistence
        # Just return the chart data with temporary IDs
        if not user_id:
            logger.info("Skipping database persistence for unauthenticated quick chart")
            temp_profile_id = uuid4()
            temp_session_id = uuid4()

            # Extract key insights
            sun_sign = chart_data.get("planets", {}).get("Sun", {}).get("sign", "Unknown")
            moon_sign = chart_data.get("planets", {}).get("Moon", {}).get("sign", "Unknown")
            ascendant = chart_data.get("ascendant", {}).get("sign", "Unknown")

            # Generate top 3 insights
            top_insights = self._generate_top_insights(chart_data, request.language)

            # Generate shareable link
            frontend_url = settings.ALLOWED_ORIGINS[0] if settings.ALLOWED_ORIGINS else "http://localhost:3000"
            shareable_link = f"{frontend_url}/chart/{temp_profile_id}?ref=instant&temp=true"

            return QuickChartResponse(
                session_id=temp_session_id,
                profile_id=temp_profile_id,
                chart_url=shareable_link,
                summary=chart_data,
                sun_sign=sun_sign,
                moon_sign=moon_sign,
                ascendant=ascendant,
                top_insights=top_insights,
                shareable_link=shareable_link,
                name=data["name"],
                birth_date=str(data["birth_date"]),
                generated_at=datetime.utcnow().isoformat()
            )

        # For authenticated users, save to database
        profile_user_id = user_id
        profile = Profile(
            user_id=profile_user_id,
            name=data["name"],
            birth_date=data["birth_date"],
            birth_time=data["birth_time"],
            birth_city=data.get("birth_place", ""),
            birth_lat=data["latitude"],
            birth_lon=data["longitude"],
            birth_timezone=data.get("timezone", "UTC")
        )
        db.add(profile)
        await db.flush()

        # Extract key insights
        sun_sign = chart_data.get("planets", {}).get("Sun", {}).get("sign", "Unknown")
        moon_sign = chart_data.get("planets", {}).get("Moon", {}).get("sign", "Unknown")
        ascendant = chart_data.get("ascendant", {}).get("sign", "Unknown")

        # Generate top 3 insights
        top_insights = self._generate_top_insights(chart_data, request.language)

        # Update session
        session.status = SessionStatus.COMPLETED
        session.profile_id = profile.id
        session.chart_generated = True
        session.completed_at = datetime.utcnow()
        session.user_id = user_id

        # Create onboarding profile record
        onboarding_profile = InstantOnboardingProfile(
            session_id=session.id,
            user_id=user_id,
            profile_id=profile.id,
            channel=session.channel,
            language=session.language,
            time_taken_seconds=int((datetime.utcnow() - session.created_at).total_seconds())
        )
        db.add(onboarding_profile)

        await db.commit()
        await db.refresh(session)
        await db.refresh(profile)

        # Generate shareable link
        frontend_url = settings.ALLOWED_ORIGINS[0] if settings.ALLOWED_ORIGINS else "http://localhost:3000"
        shareable_link = f"{frontend_url}/chart/{profile.id}?ref=instant"

        return QuickChartResponse(
            session_id=session.id,
            profile_id=profile.id,
            chart_url=shareable_link,
            summary=chart_data,
            sun_sign=sun_sign,
            moon_sign=moon_sign,
            ascendant=ascendant,
            top_insights=top_insights,
            shareable_link=shareable_link,
            name=data["name"],
            birth_date=str(data["birth_date"]),
            generated_at=datetime.utcnow().isoformat()
        )

    # WhatsApp Integration

    async def process_whatsapp_message(
        self,
        db: AsyncSession,
        message: WhatsAppMessageRequest
    ) -> WhatsAppResponse:
        """
        Process incoming WhatsApp message.

        Args:
            db: Database session
            message: Incoming message

        Returns:
            Response to send back
        """
        logger.info(f"Processing WhatsApp message from {message.from_number}")

        # Get or create session for this phone number
        result = await db.execute(
            select(InstantOnboardingSession).where(
                InstantOnboardingSession.phone_number == message.from_number,
                InstantOnboardingSession.status.in_([
                    SessionStatus.STARTED,
                    SessionStatus.COLLECTING_DATA
                ])
            ).order_by(InstantOnboardingSession.created_at.desc())
        )
        session = result.scalar_one_or_none()

        if not session:
            # Start new session
            session_request = SessionStartRequest(
                channel=OnboardingChannel.WHATSAPP,
                phone_number=message.from_number,
                language="en"  # Default, can be detected from message
            )
            start_response = await self.start_session(db, session_request)

            return WhatsAppResponse(
                to_number=message.from_number,
                content=start_response.message
            )

        # Process message based on type
        if message.message_type == "text":
            extracted_data = self._extract_data_from_text(
                message.content,
                session.current_step
            )
        elif message.message_type == "voice":
            # TODO: Integrate speech-to-text
            extracted_data = {}
        elif message.message_type == "location":
            extracted_data = {
                "latitude": message.content.get("latitude"),
                "longitude": message.content.get("longitude"),
                "birth_place": message.content.get("name", "Unknown")
            }
        else:
            extracted_data = {}

        # Collect data
        collect_request = CollectDataRequest(
            session_key=session.session_key,
            data=extracted_data
        )
        collect_response = await self.collect_data(db, collect_request)

        # If complete, generate chart
        if collect_response.is_complete:
            chart_request = QuickChartRequest(
                session_key=session.session_key,
                language=session.language
            )
            try:
                chart_response = await self.quick_chart(db, chart_request)
                content = f"{collect_response.message}\n\nView your chart: {chart_response.shareable_link}"
            except Exception as e:
                logger.error(f"Chart generation failed: {e}")
                content = "Sorry, there was an error generating your chart. Please try again."
        else:
            content = collect_response.message

        return WhatsAppResponse(
            to_number=message.from_number,
            content=content
        )

    # Voice Input Processing

    async def process_voice_input(
        self,
        db: AsyncSession,
        request: VoiceInputRequest
    ) -> VoiceInputResponse:
        """
        Process voice input and extract data.

        Args:
            db: Database session
            request: Voice input request

        Returns:
            Voice processing response
        """
        # TODO: Integrate with speech-to-text API (OpenAI Whisper, Google Speech-to-Text)
        # For now, return placeholder
        return VoiceInputResponse(
            transcription="[Voice transcription would go here]",
            extracted_data={},
            confidence=0.0,
            next_prompt="Please provide your birth date"
        )

    # Helper Methods

    def _generate_session_key(self) -> str:
        """Generate a unique session key."""
        return secrets.token_urlsafe(32)

    def _determine_next_step(
        self,
        collected_data: Dict[str, Any]
    ) -> Tuple[Optional[str], List[str]]:
        """
        Determine next step based on collected data.

        Returns:
            Tuple of (next_step, missing_fields)
        """
        required_fields = {
            "name": "name",
            "birth_date": "date",
            "birth_time": "time",
            "latitude": "place",
            "longitude": "place"
        }

        missing = []
        for field in required_fields:
            if not collected_data.get(field):
                missing.append(field)

        if not missing:
            return None, []

        # Return first missing field's step
        next_field = missing[0]
        next_step = required_fields[next_field]

        return next_step, missing

    def _get_prompt_for_step(
        self,
        step: Optional[str],
        prompts: Dict[str, str]
    ) -> str:
        """Get user prompt for given step."""
        if not step:
            return prompts["complete"]

        step_prompts = {
            "name": prompts["ask_name"],
            "date": prompts["ask_date"],
            "time": prompts["ask_time"],
            "place": prompts["ask_place"]
        }

        return step_prompts.get(step, prompts["error"])

    def _extract_data_from_text(
        self,
        text: str,
        current_step: int
    ) -> Dict[str, Any]:
        """
        Extract structured data from text using NLP/regex.

        This is a simplified version. In production, use:
        - OpenAI for advanced extraction
        - spaCy for entity recognition
        - Geocoding API for locations
        """
        data = {}

        # Step 0: Name
        if current_step == 0:
            # Simple name extraction
            data["name"] = text.strip().title()

        # Step 1: Date
        elif current_step == 1:
            # Try to parse date
            date_patterns = [
                r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # DD/MM/YYYY or DD-MM-YYYY
                r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # YYYY-MM-DD
            ]
            for pattern in date_patterns:
                match = re.search(pattern, text)
                if match:
                    groups = match.groups()
                    if len(groups) == 3:
                        # Assume DD/MM/YYYY
                        try:
                            data["birth_date"] = date(
                                int(groups[2]),
                                int(groups[1]),
                                int(groups[0])
                            )
                            break
                        except ValueError:
                            continue

        # Step 2: Time
        elif current_step == 2:
            # Try to parse time
            time_patterns = [
                r'(\d{1,2}):(\d{2})\s*(AM|PM)?',  # HH:MM AM/PM
            ]
            for pattern in time_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    hour, minute, meridiem = match.groups()
                    hour = int(hour)
                    minute = int(minute)

                    if meridiem:
                        if meridiem.upper() == "PM" and hour != 12:
                            hour += 12
                        elif meridiem.upper() == "AM" and hour == 12:
                            hour = 0

                    try:
                        data["birth_time"] = time(hour, minute)
                        break
                    except ValueError:
                        continue

        # Step 3: Place
        elif current_step == 3:
            # TODO: Use geocoding API to get lat/lng
            # For now, store place name
            data["birth_place"] = text.strip()
            # Placeholder coordinates (should be from geocoding)
            data["latitude"] = 0.0
            data["longitude"] = 0.0

        return data

    def _generate_top_insights(
        self,
        chart_data: Dict[str, Any],
        language: str
    ) -> List[str]:
        """Generate top 3 insights from chart data."""
        # Simplified insight generation
        # In production, use AI or comprehensive rules engine
        insights = []

        sun_sign = chart_data.get("planets", {}).get("Sun", {}).get("sign", "Unknown")
        moon_sign = chart_data.get("planets", {}).get("Moon", {}).get("sign", "Unknown")
        ascendant = chart_data.get("ascendant", {}).get("sign", "Unknown")

        if language == "hi":
            insights.append(f"आपकी सूर्य राशि {sun_sign} है")
            insights.append(f"आपकी चंद्र राशि {moon_sign} है")
            insights.append(f"आपकी लग्न {ascendant} है")
        else:
            insights.append(f"Your Sun sign is {sun_sign}")
            insights.append(f"Your Moon sign is {moon_sign}")
            insights.append(f"Your Ascendant is {ascendant}")

        return insights[:3]


# Global service instance
instant_onboarding_service = InstantOnboardingService()
