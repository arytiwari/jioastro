"""
Instant Onboarding Feature Implementation

API endpoints for WhatsApp-to-chart in 90 seconds.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
import logging
import traceback

from app.features.base import BaseFeature
from app.core.feature_flags import require_feature
from app.core.security import get_current_user_optional, get_current_user
from app.db.database import get_db
from app.features.instant_onboarding import schemas, service
from app.features.instant_onboarding.models import OnboardingChannel

logger = logging.getLogger(__name__)


class InstantOnboardingFeature(BaseFeature):
    """
    Instant Onboarding feature implementation.

    WhatsApp-to-chart in 90 seconds

    Provides:
    - Session-based onboarding flow
    - WhatsApp bot integration
    - Quick chart generation
    - Voice input support
    - Multi-language support (EN, HI)
    """

    @property
    def name(self) -> str:
        return "instant_onboarding"

    @property
    def display_name(self) -> str:
        return "Instant Onboarding"

    @property
    def description(self) -> str:
        return "WhatsApp-to-chart in 90 seconds"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def author(self) -> str:
        return "Claude AI"

    @property
    def magical_twelve_number(self) -> int:
        return 13

    def _create_router(self) -> APIRouter:
        """Create API router for this feature."""
        router = APIRouter(
            prefix="/instant-onboarding",
            tags=["Instant Onboarding"]
        )

        @router.get("/")
        @require_feature("instant_onboarding")
        async def get_feature_info():
            """
            Get feature information.

            Returns basic information about the Instant Onboarding feature.
            """
            return {
                "feature": self.name,
                "version": self.version,
                "description": self.description,
                "magical_twelve_number": self.magical_twelve_number,
                "capabilities": [
                    "WhatsApp bot integration",
                    "Quick data collection",
                    "Instant chart generation",
                    "Voice input support",
                    "Multi-language (EN, HI)",
                    "Zero-friction signup"
                ],
                "endpoints": {
                    "start_session": "POST /instant-onboarding/session/start",
                    "collect_data": "POST /instant-onboarding/session/collect",
                    "quick_chart": "POST /instant-onboarding/quick-chart",
                    "whatsapp_webhook": "POST /instant-onboarding/whatsapp/webhook",
                    "voice_input": "POST /instant-onboarding/voice/process"
                }
            }

        # Session Management Endpoints

        @router.post("/session/start", response_model=schemas.SessionStartResponse)
        @require_feature("instant_onboarding")
        async def start_session(
            request_data: schemas.SessionStartRequest,
            request: Request,
            db: AsyncSession = Depends(get_db)
        ):
            """
            Start a new onboarding session.

            Initiates a new session for collecting user birth data.
            Returns a session key for tracking progress.

            **Supported channels:**
            - web: Web-based form
            - whatsapp: WhatsApp bot
            - voice: Voice assistant
            - sms: SMS-based

            **Supported languages:**
            - en: English
            - hi: Hindi
            """
            try:
                # Add IP address if not provided
                if not request_data.ip_address:
                    request_data.ip_address = request.client.host if request.client else None

                # Add user agent if not provided
                if not request_data.user_agent:
                    request_data.user_agent = request.headers.get("user-agent")

                response = await service.instant_onboarding_service.start_session(db, request_data)
                logger.info(f"Session started: {response.session_id}")
                return response
            except Exception as e:
                logger.error(f"Failed to start session: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @router.post("/session/collect", response_model=schemas.CollectDataResponse)
        @require_feature("instant_onboarding")
        async def collect_data(
            request_data: schemas.CollectDataRequest,
            db: AsyncSession = Depends(get_db)
        ):
            """
            Collect data for an onboarding session.

            Submit data collected from the user. The endpoint will validate
            the data and prompt for the next required field.

            **Supports flexible data structure:**
            - name: User's name
            - birth_date: Date of birth (date object)
            - birth_time: Time of birth (time object)
            - birth_place: Place name
            - latitude: Latitude coordinate
            - longitude: Longitude coordinate
            - timezone: Timezone string
            """
            try:
                response = await service.instant_onboarding_service.collect_data(db, request_data)
                logger.info(f"Data collected for session: {response.session_id}")
                return response
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
            except Exception as e:
                logger.error(f"Failed to collect data: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        # Quick Chart Generation

        @router.post("/quick-chart", response_model=schemas.QuickChartResponse)
        @require_feature("instant_onboarding")
        async def generate_quick_chart(
            request_data: schemas.QuickChartRequest,
            db: AsyncSession = Depends(get_db),
            current_user: Optional[dict] = Depends(get_current_user_optional)
        ):
            """
            Generate a quick birth chart.

            Can work in two modes:
            1. **Session-based**: Provide session_key from an active session
            2. **Direct**: Provide all birth data directly

            Returns a quick chart summary with:
            - Sun, Moon, and Ascendant signs
            - Top 3 personalized insights
            - Shareable link to full chart
            - QR code for easy sharing

            **Options:**
            - include_numerology: Also calculate numerology (default: false)
            - language: Response language (en, hi)
            """
            try:
                user_id = current_user.get("id") if current_user else None
                response = await service.instant_onboarding_service.quick_chart(
                    db,
                    request_data,
                    user_id
                )
                logger.info(f"Quick chart generated: profile_id={response.profile_id}")
                return response
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                error_msg = f"{type(e).__name__}: {str(e)}"
                logger.error(f"Failed to generate chart: {error_msg}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise HTTPException(status_code=500, detail=error_msg)

        # WhatsApp Integration

        @router.post("/whatsapp/webhook")
        @require_feature("instant_onboarding")
        async def whatsapp_webhook(
            request: Request,
            background_tasks: BackgroundTasks,
            db: AsyncSession = Depends(get_db)
        ):
            """
            WhatsApp Business API webhook endpoint.

            Receives incoming WhatsApp messages and processes them
            for the onboarding flow.

            **Note:** This endpoint expects payloads in the format
            specified by WhatsApp Business API.

            **Security:** Should be verified with webhook signature
            in production.
            """
            try:
                body = await request.json()
                logger.info(f"WhatsApp webhook received: {body}")

                # Verify webhook (in production, check signature)
                # For now, just check if it's a message event
                if body.get("object") != "whatsapp_business_account":
                    return JSONResponse({"status": "ok"})

                # Extract message data
                entry = body.get("entry", [{}])[0]
                changes = entry.get("changes", [{}])[0]
                value = changes.get("value", {})
                messages = value.get("messages", [])

                if not messages:
                    return JSONResponse({"status": "ok"})

                message_data = messages[0]

                # Convert to our schema
                wa_message = schemas.WhatsAppMessageRequest(
                    from_number=message_data.get("from"),
                    message_id=message_data.get("id"),
                    message_type=message_data.get("type", "text"),
                    content=message_data.get("text", {}).get("body", ""),
                    timestamp=message_data.get("timestamp")
                )

                # Process in background
                async def process_message():
                    try:
                        response = await service.instant_onboarding_service.process_whatsapp_message(
                            db, wa_message
                        )
                        logger.info(f"WhatsApp response: {response}")
                        # TODO: Send response back via WhatsApp API
                    except Exception as e:
                        logger.error(f"WhatsApp message processing failed: {e}")

                background_tasks.add_task(process_message)

                return JSONResponse({"status": "ok"})

            except Exception as e:
                logger.error(f"WhatsApp webhook error: {e}")
                return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

        @router.get("/whatsapp/webhook")
        async def whatsapp_webhook_verification(
            request: Request
        ):
            """
            WhatsApp webhook verification endpoint.

            Used by WhatsApp to verify the webhook URL during setup.
            """
            mode = request.query_params.get("hub.mode")
            token = request.query_params.get("hub.verify_token")
            challenge = request.query_params.get("hub.challenge")

            # TODO: Verify token matches your configured token
            if mode == "subscribe" and token:
                logger.info("WhatsApp webhook verified")
                return int(challenge)

            return JSONResponse({"status": "error"}, status_code=403)

        # Voice Input Processing

        @router.post("/voice/process", response_model=schemas.VoiceInputResponse)
        @require_feature("instant_onboarding")
        async def process_voice_input(
            request_data: schemas.VoiceInputRequest,
            db: AsyncSession = Depends(get_db)
        ):
            """
            Process voice input for onboarding.

            Accepts audio input (URL or base64 encoded) and:
            1. Transcribes the audio to text
            2. Extracts structured data (name, date, time, place)
            3. Returns extracted data and next prompt

            **Supported formats:**
            - Audio URL: MP3, WAV, M4A
            - Base64: Encoded audio data

            **Languages:** EN, HI (more coming soon)

            **Note:** Requires speech-to-text API integration.
            """
            try:
                response = await service.instant_onboarding_service.process_voice_input(
                    db, request_data
                )
                return response
            except Exception as e:
                logger.error(f"Voice processing failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        # Analytics & Monitoring

        @router.get("/stats")
        @require_feature("instant_onboarding")
        async def get_stats(
            current_user: dict = Depends(get_current_user),
            db: AsyncSession = Depends(get_db)
        ):
            """
            Get onboarding statistics.

            Returns metrics about onboarding sessions:
            - Total sessions started
            - Completion rate
            - Average time to complete
            - Channel breakdown
            - Language breakdown

            **Requires:** Authentication
            **Access:** Admin users only
            """
            # TODO: Implement admin check
            # For now, return placeholder
            return {
                "total_sessions": 0,
                "completed_sessions": 0,
                "completion_rate": 0.0,
                "avg_time_seconds": 0,
                "by_channel": {
                    "web": 0,
                    "whatsapp": 0,
                    "voice": 0,
                    "sms": 0
                },
                "by_language": {
                    "en": 0,
                    "hi": 0
                }
            }

        return router


# Create feature instance
instant_onboarding_feature = InstantOnboardingFeature()
