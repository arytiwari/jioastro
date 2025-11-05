# OpenAI Voice & Conversation - Complete Implementation Guide

## ✅ What's Already Created

### 1. Backend Services

#### `/backend/app/services/openai_voice_service.py` ✅
Complete service with:
- **Whisper API** integration for speech-to-text (15+ languages)
- **TTS API** integration for text-to-speech (high-quality voices)
- **GPT-4 Translation** for accurate multilingual support
- **Language Detection** automatic language identification
- Supports both Azure OpenAI and standard OpenAI

**Key Methods:**
```python
async def transcribe_audio(audio_data: bytes, language: str) -> Dict
async def generate_speech(text: str, language: str, voice: str) -> bytes
async def translate_text(text: str, source_lang: str, target_lang: str) -> Dict
async def detect_language(text: str) -> str
```

#### `/backend/app/schemas/conversation.py` ✅
Pydantic schemas for all conversation endpoints:
- `ConversationalQuestionRequest`
- `TranscribeAudioRequest`
- `GenerateSpeechRequest`
- `TranslateTextRequest`
- Complete response models

### 2. Frontend Components

#### `/frontend/components/VoiceConversation.tsx` ✅
Full conversational UI with:
- Voice recording (browser-based or will use OpenAI Whisper)
- Text-to-speech (browser-based or will use Open AI TTS)
- Multi-language support (15 languages)
- Chat interface with history
- Auto-play toggle for voice responses

## 🔧 Remaining Integration Steps

### Step 1: Add Conversational Endpoints to Backend

Add these endpoints to `/backend/app/api/v1/endpoints/readings.py`:

```python
from app.schemas.conversation import (
    ConversationalQuestionRequest,
    ConversationalQuestionResponse,
    TranscribeAudioRequest,
    TranscribeAudioResponse,
    GenerateSpeechRequest,
    GenerateSpeechResponse
)
from app.services.openai_voice_service import openai_voice_service
import base64

@router.post("/ask/conversational", response_model=ConversationalQuestionResponse)
async def ask_conversational_question(
    request: ConversationalQuestionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Conversational Q&A with voice and translation support

    Flow:
    1. Translate question to English (if needed)
    2. Process with AI orchestrator
    3. Translate response back to user's language
    4. Generate voice response (if requested)
    """
    try:
        user_id = current_user["user_id"]

        # Get profile and chart
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
            # Calculate chart (same logic as comprehensive reading)
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

        # Translate question to English if needed
        if request.source_language[:2] != 'en':
            print(f"🌐 Translating from {request.source_language} to English...")
            translation_result = await openai_voice_service.translate_text(
                text=request.question,
                source_lang=request.source_language,
                target_lang='en-US'
            )
            english_question = translation_result['translated_text']
        else:
            english_question = request.question

        # Process with AI orchestrator (existing functionality)
        from app.services.ai_orchestrator import ai_orchestrator

        result = await ai_orchestrator.answer_question(
            chart_data=chart.get("chart_data", {}),
            question=english_question,
            include_predictions=True
        )

        # Translate response back to user's language
        if request.source_language[:2] != 'en':
            print(f"🌐 Translating response back to {request.source_language}...")
            translation_result = await openai_voice_service.translate_text(
                text=result['answer'],
                source_lang='en-US',
                target_lang=request.source_language
            )
            translated_answer = translation_result['translated_text']
        else:
            translated_answer = result['answer']

        # Generate audio response if requested
        audio_data = None
        audio_format = None
        if request.include_audio_response:
            print(f"🔊 Generating speech in {request.source_language}...")
            audio_bytes = await openai_voice_service.generate_speech(
                text=translated_answer,
                language=request.source_language,
                voice=request.voice or 'alloy'
            )
            # Encode to base64 for JSON response
            audio_data = base64.b64encode(audio_bytes).decode('utf-8')
            audio_format = 'mp3'

        return ConversationalQuestionResponse(
            answer=translated_answer,
            original_answer=result['answer'] if request.source_language[:2] != 'en' else None,
            audio_data=audio_data,
            audio_format=audio_format,
            rules_used=result.get('rules_used', []),
            confidence=result.get('confidence', 'medium'),
            source_language=request.source_language,
            target_language=request.source_language,  # Same for now
            was_translated=request.source_language[:2] != 'en',
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
async def transcribe_audio(
    request: TranscribeAudioRequest,
    current_user: dict = Depends(get_current_user)
):
    """Transcribe audio using OpenAI Whisper"""
    try:
        # Decode base64 audio
        audio_bytes = base64.b64decode(request.audio_data)

        # Transcribe with Whisper
        result = await openai_voice_service.transcribe_audio(
            audio_data=audio_bytes,
            language=request.language,
            format=request.format
        )

        return TranscribeAudioResponse(**result)

    except Exception as e:
        print(f"❌ Transcription error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to transcribe audio: {str(e)}"
        )


@router.post("/voice/generate", response_model=GenerateSpeechResponse)
async def generate_speech(
    request: GenerateSpeechRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate speech using OpenAI TTS"""
    try:
        # Generate audio
        audio_bytes = await openai_voice_service.generate_speech(
            text=request.text,
            language=request.language,
            voice=request.voice,
            speed=request.speed
        )

        # Encode to base64
        audio_data = base64.b64encode(audio_bytes).decode('utf-8')

        return GenerateSpeechResponse(
            audio_data=audio_data,
            format='mp3'
        )

    except Exception as e:
        print(f"❌ Speech generation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate speech: {str(e)}"
        )
```

### Step 2: Update Frontend API Client

Add to `/frontend/lib/api.ts`:

```typescript
// Voice conversation endpoints
async askConversationalQuestion(data: {
  profile_id: string
  question: string
  source_language?: string
  is_voice?: boolean
  include_audio_response?: boolean
  voice?: string
}) {
  return this.request('/readings/ask/conversational', {
    method: 'POST',
    body: JSON.stringify({
      ...data,
      source_language: data.source_language || 'en-US',
      is_voice: data.is_voice || false,
      include_audio_response: data.include_audio_response || false
    }),
  })
}

async transcribeAudio(data: {
  audio_data: string
  language?: string
  format?: string
}) {
  return this.request('/readings/voice/transcribe', {
    method: 'POST',
    body: JSON.stringify({
      audio_data: data.audio_data,
      language: data.language || 'en',
      format: data.format || 'webm'
    }),
  })
}

async generateSpeech(data: {
  text: string
  language?: string
  voice?: string
  speed?: number
}) {
  return this.request('/readings/voice/generate', {
    method: 'POST',
    body: JSON.stringify({
      text: data.text,
      language: data.language || 'en-US',
      voice: data.voice || 'alloy',
      speed: data.speed || 1.0
    }),
  })
}
```

### Step 3: Update Ask Page with Voice Interface

Replace `/frontend/app/dashboard/ask/page.tsx` with:

```typescript
'use client'

import { useState } from 'react'
import { VoiceConversation } from '@/components/VoiceConversation'
import { apiClient } from '@/lib/api'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Mic, FileText } from '@/components/icons'
// ... existing imports

export default function AskQuestionPage() {
  const [mode, setMode] = useState<'conversation' | 'form'>('conversation')
  const [selectedProfile, setSelectedProfile] = useState('')

  // Existing profile loading logic...

  // Handle conversational messages
  const handleConversationalMessage = async (
    message: string,
    language: string,
    isVoice: boolean
  ): Promise<string> => {
    try {
      const response = await apiClient.askConversationalQuestion({
        profile_id: selectedProfile,
        question: message,
        source_language: language,
        is_voice: isVoice,
        include_audio_response: true  // Get voice response
      })

      // If audio response provided, play it
      if (response.data.audio_data) {
        const audio = new Audio(`data:audio/mp3;base64,${response.data.audio_data}`)
        await audio.play()
      }

      return response.data.answer
    } catch (error) {
      console.error('Conversational error:', error)
      throw new Error('Failed to get answer. Please try again.')
    }
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Ask a Question</h1>
        <p className="text-gray-600 mt-2">
          Talk or type in any language - powered by OpenAI Voice & GPT-4
        </p>
      </div>

      {/* Mode Selector */}
      <Tabs value={mode} onValueChange={(v) => setMode(v as any)} className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="conversation">
            <Mic className="w-4 h-4 mr-2" />
            Voice Conversation
          </TabsTrigger>
          <TabsTrigger value="form">
            <FileText className="w-4 h-4 mr-2" />
            Traditional Form
          </TabsTrigger>
        </TabsList>

        <TabsContent value="conversation" className="mt-6">
          <Card className="p-6">
            <div className="h-[600px]">
              {selectedProfile ? (
                <VoiceConversation
                  onSendMessage={handleConversationalMessage}
                  selectedLanguage="en-US"
                  profileId={selectedProfile}
                />
              ) : (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center">
                    <p className="text-gray-600 mb-4">Select a birth profile to start</p>
                    {/* Profile selector here */}
                  </div>
                </div>
              )}
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="form">
          {/* Existing form UI */}
        </TabsContent>
      </Tabs>
    </div>
  )
}
```

### Step 4: Environment Variables

Add to `.env`:

```bash
# Already have these (from existing OpenAI integration)
AZURE_OPENAI_KEY=your_azure_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Add these deployment names
AZURE_GPT4_DEPLOYMENT_NAME=gpt-4
AZURE_WHISPER_DEPLOYMENT_NAME=whisper
AZURE_TTS_DEPLOYMENT_NAME=tts-1

# Or if using standard OpenAI (not Azure)
OPENAI_API_KEY=sk-your-key
```

## 🎯 User Experience Flow

### Example: Hindi User Asking About Career

1. **User clicks microphone** → Speaks in Hindi: "मेरे करियर के लिए सबसे अच्छा समय कब है?"

2. **Browser captures audio** → Web Speech API transcribes to Hindi text (or send to Whisper for better accuracy)

3. **Frontend sends to backend**:
   ```json
   {
     "profile_id": "abc-123",
     "question": "मेरे करियर के लिए सबसे अच्छा समय कब है?",
     "source_language": "hi-IN",
     "is_voice": true,
     "include_audio_response": true
   }
   ```

4. **Backend processes**:
   - Translates to English: "When is the best time for my career?"
   - Calls AI orchestrator (existing) → Analyzes chart, retrieves BPHS rules
   - Generates English answer
   - Translates back to Hindi
   - Generates Hindi audio with OpenAI TTS

5. **Frontend receives**:
   ```json
   {
     "answer": "आपके चार्ट के अनुसार, बृहस्पति की महादशा...",
     "audio_data": "base64_encoded_mp3",
     "rules_used": [...]
   }
   ```

6. **User hears/reads response** in Hindi with proper pronunciation!

## 🚀 Benefits of OpenAI Approach

### vs Microsoft/Google Translate:
- ✅ Better context understanding (GPT-4 knows astrology)
- ✅ Preserves Vedic terminology accurately
- ✅ More natural translations
- ✅ Single vendor (already using OpenAI)

### vs Browser Speech APIs:
- ✅ Much better voice quality (OpenAI TTS)
- ✅ More accurate transcription (Whisper)
- ✅ Consistent across all browsers
- ✅ Works on mobile perfectly
- ✅ 50+ languages supported

### Voice Quality Comparison:
- **Browser TTS**: Robotic, inconsistent
- **OpenAI TTS**: Near-human, expressive, multilingual

## 📊 Cost Estimation

### OpenAI Pricing:
- **Whisper**: $0.006 per minute (~1 min conversation = $0.006)
- **TTS**: $15 per 1M characters (~500 chars response = $0.0075)
- **GPT-4 Translation**: ~$0.03 per translation
- **AI Orchestrator** (existing): ~$0.07 per query

**Total per voice conversation**: ~$0.11 per interaction

### Cost Optimization:
1. Cache translations for common responses
2. Use browser speech for English (free)
3. Batch TTS requests
4. Use GPT-4-mini for simple translations

## 🧪 Testing

### Test 1: English Voice
```bash
curl -X POST http://localhost:8000/api/v1/readings/ask/conversational \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "profile_id": "xxx",
    "question": "What is my current Mahadasha?",
    "source_language": "en-US",
    "include_audio_response": true
  }'
```

### Test 2: Hindi Translation
```bash
curl -X POST http://localhost:8000/api/v1/readings/ask/conversational \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "profile_id": "xxx",
    "question": "मेरी राशि क्या है?",
    "source_language": "hi-IN",
    "include_audio_response": true
  }'
```

## 🎤 Advanced: OpenAI Realtime API (Optional)

For real-time streaming conversations:

```python
# Future enhancement - streaming voice conversation
from openai import AsyncOpenAI

@router.websocket("/ws/voice-chat")
async def voice_chat_websocket(
    websocket: WebSocket,
    token: str = Query(...)
):
    """Real-time voice conversation using OpenAI Realtime API"""
    await websocket.accept()

    client = AsyncOpenAI()

    async with client.beta.realtime.connect(model="gpt-4o-realtime-preview") as connection:
        # Stream audio bidirectionally
        # Handle voice input/output in real-time
        # Context from birth chart maintained throughout
        pass
```

## 📝 Summary

You now have:
- ✅ Complete backend voice service (Whisper, TTS, Translation)
- ✅ Pydantic schemas for all endpoints
- ✅ Frontend voice conversation component
- ✅ Clear integration steps

**Remaining**: Wire up the endpoints and test!

The system will provide a world-class multilingual voice astrology experience powered entirely by OpenAI. 🎤✨🌟
