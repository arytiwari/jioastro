"""
Pydantic schemas for voice conversation endpoints
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ConversationalQuestionRequest(BaseModel):
    """Request for conversational question with voice/translation support"""
    profile_id: str = Field(..., description="Birth profile ID")
    question: str = Field(..., min_length=1, max_length=2000, description="User's question in any language")
    source_language: str = Field(default="en-US", description="User's language code (e.g., 'hi-IN', 'en-US')")
    is_voice: bool = Field(default=False, description="Whether input was from voice")
    include_audio_response: bool = Field(default=False, description="Whether to generate voice response")
    voice: Optional[str] = Field(default="alloy", description="TTS voice to use")
    context: Optional[List[dict]] = Field(default=None, description="Previous conversation context")


class TranscribeAudioRequest(BaseModel):
    """Request for audio transcription"""
    audio_data: str = Field(..., description="Base64 encoded audio data")
    language: str = Field(default="en", description="Expected language code")
    format: str = Field(default="webm", description="Audio format (webm, mp3, wav)")


class TranslateTextRequest(BaseModel):
    """Request for text translation"""
    text: str = Field(..., description="Text to translate")
    source_language: str = Field(..., description="Source language code")
    target_language: str = Field(..., description="Target language code")


class GenerateSpeechRequest(BaseModel):
    """Request for speech generation"""
    text: str = Field(..., description="Text to convert to speech")
    language: str = Field(default="en-US", description="Target language")
    voice: str = Field(default="alloy", description="Voice to use")
    speed: float = Field(default=1.0, ge=0.25, le=4.0, description="Speech speed")


class ConversationalQuestionResponse(BaseModel):
    """Response for conversational question"""
    answer: str = Field(..., description="AI answer in user's language")
    original_answer: Optional[str] = Field(None, description="Original English answer before translation")
    audio_data: Optional[str] = Field(None, description="Base64 encoded audio response (if requested)")
    audio_format: Optional[str] = Field(None, description="Audio format (mp3)")
    rules_used: List[dict] = Field(default_factory=list, description="BPHS rules used")
    confidence: str = Field(default="medium", description="Confidence level")
    source_language: str = Field(..., description="User's input language")
    target_language: str = Field(..., description="Response language")
    was_translated: bool = Field(..., description="Whether translation was performed")
    tokens_used: int = Field(default=0, description="Total tokens used")
    session_id: Optional[str] = Field(None, description="Conversation session ID")


class TranscribeAudioResponse(BaseModel):
    """Response for audio transcription"""
    text: str = Field(..., description="Transcribed text")
    language: str = Field(..., description="Detected language")
    duration: float = Field(..., description="Audio duration in seconds")


class TranslateTextResponse(BaseModel):
    """Response for text translation"""
    translated_text: str = Field(..., description="Translated text")
    source_language: str = Field(..., description="Source language name")
    target_language: str = Field(..., description="Target language name")
    confidence: float = Field(..., description="Translation confidence score")
    tokens_used: int = Field(default=0, description="Tokens used for translation")


class GenerateSpeechResponse(BaseModel):
    """Response for speech generation"""
    audio_data: str = Field(..., description="Base64 encoded audio")
    format: str = Field(default="mp3", description="Audio format")
    duration: Optional[float] = Field(None, description="Audio duration in seconds")


class ConversationMessage(BaseModel):
    """Single message in a conversation"""
    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")
    language: str = Field(..., description="Language of message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    is_voice: bool = Field(default=False, description="Whether message was voice")


class ConversationSession(BaseModel):
    """Conversation session"""
    session_id: str = Field(..., description="Session ID")
    profile_id: str = Field(..., description="Birth profile ID")
    user_id: str = Field(..., description="User ID")
    messages: List[ConversationMessage] = Field(default_factory=list)
    language: str = Field(default="en-US", description="Primary language")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
