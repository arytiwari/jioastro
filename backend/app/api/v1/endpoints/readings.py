"""Reading API Endpoints - MVP Bridge & AI Engine"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import Dict, Any
import uuid
import base64

from app.schemas.reading import (
    ReadingCalculateRequest,
    ReadingResponse,
    AIReadingRequest,
    AIReadingResponse,
    QuestionRequest,
    QuestionResponse
)
from app.schemas.conversation import (
    ConversationalQuestionRequest,
    ConversationalQuestionResponse,
    TranscribeAudioRequest,
    TranscribeAudioResponse,
    GenerateSpeechRequest,
    GenerateSpeechResponse
)
from app.core.security import get_current_user
from app.services.mvp_bridge import mvp_bridge

router = APIRouter()


@router.post("/calculate", response_model=dict, status_code=status.HTTP_201_CREATED)
async def calculate_reading(
    request: ReadingCalculateRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Calculate charts using MVP bridge (wraps existing services)
    Returns basic charts with caching by canonical hash

    This endpoint reuses existing Swiss Ephemeris calculations
    """
    try:
        user_id = current_user["user_id"]

        # Validate location data
        if not (request.latitude and request.longitude) and not (request.city_id and request.country_code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provide either (latitude, longitude) or (city_id, country_code)"
            )

        # Call MVP bridge
        result = await mvp_bridge.get_charts(
            name=request.name,
            dob=request.dob,
            tob=request.tob,
            city_id=request.city_id,
            country_code=request.country_code,
            latitude=request.latitude,
            longitude=request.longitude,
            timezone_str=request.timezone,
            city=request.city,
            user_id=user_id,
            chart_types=request.chart_types
        )

        # Add session ID
        result['session_id'] = str(uuid.uuid4())
        result['created_at'] = result['meta']['calculated_at']

        return result

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error calculating reading: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate reading: {str(e)}"
        )


@router.get("/health", response_model=dict, tags=["health"])
async def health_check():
    """
    Health check for reading service (public endpoint)

    No authentication required
    """
    return {
        "status": "healthy",
        "service": "readings",
        "mvp_bridge": "active",
        "ai_engine": "phase_3_complete",
        "orchestration": "multi-role (Coordinator, Retriever, Synthesizer, Verifier, Predictor)",
        "knowledge_base": "120 BPHS rules",
        "memory_system": "active",
        "endpoints": {
            "calculate": "/api/v1/readings/calculate - MVP chart calculation (requires auth)",
            "ai_reading": "/api/v1/readings/ai - Full orchestrated reading with predictions (requires auth)",
            "ask_question": "/api/v1/readings/ask - Targeted question answering (requires auth)",
            "list": "/api/v1/readings/ - List reading history (requires auth)",
            "get": "/api/v1/readings/{id} - Get specific reading (requires auth)"
        },
        "phase_3_features": [
            "Multi-role LLM orchestration",
            "Scripture-grounded interpretations",
            "Time-based predictions (dasha × transit)",
            "Confidence scoring",
            "Rule citations with BPHS anchors",
            "Memory system",
            "Reading session caching"
        ]
    }


@router.get("/{session_id}", response_model=dict)
async def get_reading(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a cached reading session by ID"""
    try:
        user_id = current_user["user_id"]

        # Query reading_sessions table
        from app.services.supabase_service import supabase_service

        response = supabase_service.client.table("reading_sessions")\
            .select("*")\
            .eq("id", session_id)\
            .eq("user_id", user_id)\
            .execute()

        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reading session not found"
            )

        return response.data[0]

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting reading: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get reading: {str(e)}"
        )


@router.get("/", response_model=list)
async def list_readings(
    current_user: dict = Depends(get_current_user),
    limit: int = 20,
    offset: int = 0
):
    """List user's reading sessions"""
    try:
        user_id = current_user["user_id"]

        from app.services.supabase_service import supabase_service

        # Select all columns - if table doesn't exist or has different schema, return empty
        try:
            response = supabase_service.client.table("reading_sessions")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()
        except Exception as e:
            # Table might not exist yet or have different schema
            print(f"Note: reading_sessions table not available: {e}")
            return []

        return response.data if response.data else []

    except Exception as e:
        print(f"Error listing readings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list readings: {str(e)}"
        )


@router.post("/ai", response_model=dict)
async def generate_ai_reading(
    request: AIReadingRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate AI-powered comprehensive reading using multi-role orchestration

    This endpoint:
    1. Uses MVP bridge for charts (reuses existing calculations)
    2. Uses AI orchestrator (Coordinator, Retriever, Synthesizer, Verifier, Predictor)
    3. Retrieves relevant rules from knowledge base
    4. Generates time-based predictions with dasha × transit overlap
    5. Returns structured reading with scripture citations and confidence scores

    Phase 3: COMPLETE ✅
    """
    try:
        user_id = current_user["user_id"]

        # Import orchestrator and memory service
        from app.services.ai_orchestrator import ai_orchestrator
        from app.services.memory_service import memory_service

        # Get chart data from profile
        from app.services.supabase_service import supabase_service

        profile = await supabase_service.get_profile(
            profile_id=request.profile_id,
            user_id=user_id
        )

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )

        # Get or calculate chart
        chart = await supabase_service.get_chart(
            profile_id=request.profile_id,
            chart_type="D1"
        )

        if not chart:
            # Calculate chart if it doesn't exist
            from datetime import datetime
            from app.services.astrology import astrology_service

            # Parse birth data
            if isinstance(profile['birth_date'], str):
                birth_date = datetime.fromisoformat(profile['birth_date']).date()
            else:
                birth_date = profile['birth_date']

            if isinstance(profile['birth_time'], str):
                birth_time = datetime.fromisoformat(f"2000-01-01T{profile['birth_time']}").time()
            else:
                birth_time = profile['birth_time']

            chart_data = astrology_service.calculate_birth_chart(
                name=profile['name'],
                birth_date=birth_date,
                birth_time=birth_time,
                latitude=float(profile['birth_lat']),
                longitude=float(profile['birth_lon']),
                timezone_str=profile.get('birth_timezone') or 'UTC',
                city=profile.get('birth_city') or 'Unknown'
            )

            chart = await supabase_service.create_chart({
                "profile_id": str(request.profile_id),
                "chart_type": "D1",
                "chart_data": chart_data
            })

        # Generate canonical hash for caching
        canonical_hash = memory_service.generate_canonical_hash(
            profile_id=str(request.profile_id),
            domains=request.domains or ["general"],
            include_predictions=request.include_predictions,
            prediction_window_months=request.prediction_window_months
        )

        # Check for cached reading
        if not request.force_regenerate:
            cached_reading = await memory_service.get_cached_reading(
                canonical_hash=canonical_hash,
                max_age_hours=24
            )
            if cached_reading:
                print(f"✨ Cache hit! Returning cached reading: {cached_reading.get('id')}")
                return {
                    "reading": {
                        "session_id": cached_reading.get('id'),
                        "interpretation": cached_reading.get('interpretation', ''),
                        "domain_analyses": cached_reading.get('domain_analyses', {}),
                        "predictions": cached_reading.get('predictions', []),
                        "rules_used": cached_reading.get('rules_used', []),
                        "total_rules_retrieved": len(cached_reading.get('rules_used', [])),
                        "verification": cached_reading.get('verification', {}),
                        "orchestration_metadata": cached_reading.get('orchestration_metadata', {}),
                        "confidence": cached_reading.get('verification', {}).get('confidence_level', 'medium'),
                        "created_at": cached_reading.get('created_at')
                    },
                    "cache_hit": True,
                    "success": True
                }

        # Generate comprehensive reading using orchestrator
        print(f"🎭 Generating comprehensive reading with orchestrator...")
        result = await ai_orchestrator.generate_comprehensive_reading(
            chart_data=chart.get("chart_data", {}),
            query=request.query,
            domains=request.domains,
            include_predictions=request.include_predictions,
            include_transits=request.include_transits,
            prediction_window_months=request.prediction_window_months
        )

        # Store reading session
        reading_session = await memory_service.store_reading_session(
            user_id=user_id,
            profile_id=str(request.profile_id),
            canonical_hash=canonical_hash,
            interpretation=result['interpretation'],
            domain_analyses=result.get('domain_analyses', {}),
            predictions=result.get('predictions', []),
            rules_used=result.get('rules_used', []),
            verification=result.get('verification', {}),
            orchestration_metadata=result.get('orchestration_metadata', {}),
            query=request.query,
            domains=request.domains
        )

        return {
            "reading": {
                "session_id": reading_session['id'],
                "interpretation": result['interpretation'],
                "domain_analyses": result.get('domain_analyses', {}),
                "predictions": result.get('predictions', []),
                "rules_used": result.get('rules_used', []),
                "total_rules_retrieved": result.get('total_rules_retrieved', 0),
                "verification": result.get('verification', {}),
                "orchestration_metadata": result.get('orchestration_metadata', {}),
                "confidence": result.get('confidence', 'medium'),
                "created_at": reading_session.get('created_at')
            },
            "cache_hit": False,
            "success": True
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating AI reading: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate AI reading: {str(e)}"
        )


@router.post("/ask", response_model=dict)
async def ask_question(
    request: QuestionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Ask a specific question about a chart using orchestrated AI system

    This endpoint:
    1. Takes a targeted question
    2. Uses coordinator to determine relevant domains
    3. Retrieves relevant rules
    4. Generates focused answer with citations

    Lighter and faster than full reading generation.

    Phase 3: COMPLETE ✅
    """
    try:
        user_id = current_user["user_id"]

        # Import services
        from app.services.ai_orchestrator import ai_orchestrator
        from app.services.supabase_service import supabase_service

        # Get profile and chart
        profile = await supabase_service.get_profile(
            profile_id=request.profile_id,
            user_id=user_id
        )

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )

        chart = await supabase_service.get_chart(
            profile_id=request.profile_id,
            chart_type="D1"
        )

        if not chart:
            # Calculate chart if it doesn't exist
            from datetime import datetime
            from app.services.astrology import astrology_service

            if isinstance(profile['birth_date'], str):
                birth_date = datetime.fromisoformat(profile['birth_date']).date()
            else:
                birth_date = profile['birth_date']

            if isinstance(profile['birth_time'], str):
                birth_time = datetime.fromisoformat(f"2000-01-01T{profile['birth_time']}").time()
            else:
                birth_time = profile['birth_time']

            chart_data = astrology_service.calculate_birth_chart(
                name=profile['name'],
                birth_date=birth_date,
                birth_time=birth_time,
                latitude=float(profile['birth_lat']),
                longitude=float(profile['birth_lon']),
                timezone_str=profile.get('birth_timezone') or 'UTC',
                city=profile.get('birth_city') or 'Unknown'
            )

            chart = await supabase_service.create_chart({
                "profile_id": str(request.profile_id),
                "chart_type": "D1",
                "chart_data": chart_data
            })

        # Generate answer using orchestrator
        # Don't include predictions for questions, just focused analysis
        print(f"❓ Answering question: {request.question[:50]}...")
        result = await ai_orchestrator.generate_comprehensive_reading(
            chart_data=chart.get("chart_data", {}),
            query=request.question,
            domains=None,  # Let coordinator determine domains
            include_predictions=False,  # No time predictions for questions
            include_transits=False,
            prediction_window_months=0
        )

        return {
            "answer": result['interpretation'],
            "question": request.question,
            "rules_used": result.get('rules_used', []),
            "total_rules_retrieved": result.get('total_rules_retrieved', 0),
            "domains_analyzed": result.get('orchestration_metadata', {}).get('domains_analyzed', []),
            "verification": result.get('verification', {}),
            "confidence": result.get('confidence', 'medium'),
            "tokens_used": result.get('orchestration_metadata', {}).get('tokens_used', 0),
            "success": True
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error answering question: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to answer question: {str(e)}"
        )

# ===========================================================================
# CONVERSATIONAL & VOICE ENDPOINTS (OpenAI Whisper, TTS, Translation)
# ===========================================================================

@router.post("/ask/conversational", response_model=ConversationalQuestionResponse)
async def ask_conversational_question(
    request: ConversationalQuestionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Conversational Q&A with voice and multi-language support

    Flow:
    1. Translate question to English (if needed) using GPT-4
    2. Process with AI orchestrator (existing)
    3. Translate response back to user's language
    4. Generate voice response if requested (OpenAI TTS)

    Supports 15+ languages including Hindi, Marathi, Gujarati, Tamil, etc.
    """
    try:
        user_id = current_user["user_id"]

        # Import voice service
        from app.services.openai_voice_service import openai_voice_service

        # Get profile and chart (reuse existing logic)
        from app.services.supabase_service import supabase_service

        profile = await supabase_service.get_profile(
            profile_id=request.profile_id,
            user_id=user_id
        )

        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        # Get or calculate chart
        chart = await supabase_service.get_chart(
            profile_id=request.profile_id,
            chart_type="D1"
        )

        if not chart:
            # Calculate chart (same logic as other endpoints)
            from datetime import datetime
            from app.services.astrology import astrology_service

            birth_date = datetime.fromisoformat(profile['birth_date']).date() \
                if isinstance(profile['birth_date'], str) else profile['birth_date']
            birth_time = datetime.fromisoformat(f"2000-01-01T{profile['birth_time']}").time() \
                if isinstance(profile['birth_time'], str) else profile['birth_time']

            chart_data = astrology_service.calculate_birth_chart(
                name=profile['name'],
                birth_date=birth_date,
                birth_time=birth_time,
                latitude=float(profile['birth_lat']),
                longitude=float(profile['birth_lon']),
                timezone_str=profile.get('birth_timezone') or 'UTC',
                city=profile.get('birth_city') or 'Unknown'
            )

            chart = await supabase_service.create_chart({
                "profile_id": str(request.profile_id),
                "chart_type": "D1",
                "chart_data": chart_data
            })

        # Step 1: Translate question to English if needed
        was_translated = request.source_language[:2] != 'en'
        if was_translated:
            print(f"🌐 Translating from {request.source_language} to English...")
            translation_result = await openai_voice_service.translate_text(
                text=request.question,
                source_lang=request.source_language,
                target_lang='en-US'
            )
            english_question = translation_result['translated_text']
            print(f"📝 Translated: {english_question[:100]}...")
        else:
            english_question = request.question

        # Step 2: Process with AI orchestrator (existing functionality)
        from app.services.ai_orchestrator import ai_orchestrator

        print(f"🤖 Processing question with AI orchestrator...")
        result = await ai_orchestrator.generate_comprehensive_reading(
            chart_data=chart.get("chart_data", {}),
            query=english_question,
            domains=None,  # Let coordinator determine domains
            include_predictions=False,  # For questions, focus on answer
            include_transits=False,
            prediction_window_months=0
        )

        english_answer = result['interpretation']

        # Step 3: Translate response back to user's language
        if was_translated:
            print(f"🌐 Translating response back to {request.source_language}...")
            translation_result = await openai_voice_service.translate_text(
                text=english_answer,
                source_lang='en-US',
                target_lang=request.source_language
            )
            translated_answer = translation_result['translated_text']
            print(f"✅ Translation complete")
        else:
            translated_answer = english_answer

        # Step 4: Generate audio response if requested
        audio_data = None
        audio_format = None
        if request.include_audio_response:
            print(f"🔊 Generating speech in {request.source_language}...")
            audio_bytes = await openai_voice_service.generate_speech(
                text=translated_answer,
                language=request.source_language,
                voice=request.voice or 'alloy',
                speed=1.0
            )
            # Encode to base64 for JSON response
            audio_data = base64.b64encode(audio_bytes).decode('utf-8')
            audio_format = 'mp3'
            print(f"✅ Audio generated: {len(audio_bytes)} bytes")

        return ConversationalQuestionResponse(
            answer=translated_answer,
            original_answer=english_answer if was_translated else None,
            audio_data=audio_data,
            audio_format=audio_format,
            rules_used=result.get('rules_used', []),
            confidence=result.get('confidence', 'medium'),
            source_language=request.source_language,
            target_language=request.source_language,
            was_translated=was_translated,
            tokens_used=result.get('orchestration_metadata', {}).get('tokens_used', 0)
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Conversational question error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process question: {str(e)}"
        )


@router.post("/voice/transcribe", response_model=TranscribeAudioResponse)
async def transcribe_audio_endpoint(
    request: TranscribeAudioRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Transcribe audio using OpenAI Whisper

    Converts speech to text in 50+ languages with high accuracy.
    Better than browser Speech Recognition API.
    """
    try:
        from app.services.openai_voice_service import openai_voice_service

        # Decode base64 audio
        audio_bytes = base64.b64decode(request.audio_data)

        print(f"🎤 Transcribing audio: {len(audio_bytes)} bytes, language: {request.language}")

        # Transcribe with Whisper
        result = await openai_voice_service.transcribe_audio(
            audio_data=audio_bytes,
            language=request.language,
            format=request.format
        )

        print(f"✅ Transcription complete: {result['text'][:100]}...")

        return TranscribeAudioResponse(**result)

    except Exception as e:
        print(f"❌ Transcription error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to transcribe audio: {str(e)}"
        )


@router.post("/voice/generate", response_model=GenerateSpeechResponse)
async def generate_speech_endpoint(
    request: GenerateSpeechRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate speech using OpenAI TTS

    High-quality text-to-speech in multiple languages.
    Supports 6 voices: alloy, echo, fable, onyx, nova, shimmer
    """
    try:
        from app.services.openai_voice_service import openai_voice_service

        print(f"🔊 Generating speech: {len(request.text)} chars, voice: {request.voice}")

        # Generate audio
        audio_bytes = await openai_voice_service.generate_speech(
            text=request.text,
            language=request.language,
            voice=request.voice,
            speed=request.speed
        )

        # Encode to base64
        audio_data = base64.b64encode(audio_bytes).decode('utf-8')

        print(f"✅ Speech generated: {len(audio_bytes)} bytes")

        return GenerateSpeechResponse(
            audio_data=audio_data,
            format='mp3'
        )

    except Exception as e:
        print(f"❌ Speech generation error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate speech: {str(e)}"
        )
