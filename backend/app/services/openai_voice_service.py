"""
OpenAI Voice Services - Whisper, TTS, and Translation
Uses OpenAI APIs for high-quality voice and translation
"""

import os
import io
import base64
from typing import Dict, Any, Optional
from openai import AsyncAzureOpenAI, AsyncOpenAI
from app.core.config import settings

class OpenAIVoiceService:
    """
    Service for OpenAI voice capabilities:
    - Whisper for speech-to-text
    - TTS for text-to-speech
    - GPT-4 for translation
    """

    def __init__(self):
        # Initialize Azure OpenAI client (you're already using Azure)
        if settings.AZURE_OPENAI_ENDPOINT:
            self.client = AsyncAzureOpenAI(
                api_key=settings.AZURE_OPENAI_API_KEY,
                api_version=settings.AZURE_OPENAI_API_VERSION,
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
            )
            self.use_azure = True
        else:
            # Fallback to standard OpenAI
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            self.use_azure = False

        # Language code mapping
        self.language_names = {
            'en-US': 'English',
            'hi-IN': 'Hindi',
            'mr-IN': 'Marathi',
            'gu-IN': 'Gujarati',
            'ta-IN': 'Tamil',
            'te-IN': 'Telugu',
            'kn-IN': 'Kannada',
            'bn-IN': 'Bengali',
            'pa-IN': 'Punjabi',
            'es-ES': 'Spanish',
            'fr-FR': 'French',
            'de-DE': 'German',
            'zh-CN': 'Chinese',
            'ja-JP': 'Japanese',
            'ko-KR': 'Korean',
        }

    async def transcribe_audio(
        self,
        audio_data: bytes,
        language: str = 'en',
        format: str = 'webm'
    ) -> Dict[str, Any]:
        """
        Transcribe audio using Whisper API

        Args:
            audio_data: Audio file bytes
            language: ISO language code (e.g., 'en', 'hi', 'es')
            format: Audio format (webm, mp3, wav, etc.)

        Returns:
            {
                'text': 'transcribed text',
                'language': 'detected language',
                'duration': 12.5
            }
        """
        try:
            # Create file-like object from bytes
            audio_file = io.BytesIO(audio_data)
            audio_file.name = f"audio.{format}"

            # Call Whisper API
            if self.use_azure:
                # Azure OpenAI Whisper
                response = await self.client.audio.transcriptions.create(
                    model=settings.AZURE_WHISPER_DEPLOYMENT_NAME or "whisper",
                    file=audio_file,
                    language=language[:2],  # ISO 639-1 code
                    response_format="verbose_json"
                )
            else:
                # Standard OpenAI Whisper
                response = await self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language[:2],
                    response_format="verbose_json"
                )

            return {
                'text': response.text,
                'language': response.language if hasattr(response, 'language') else language,
                'duration': response.duration if hasattr(response, 'duration') else 0
            }

        except Exception as e:
            print(f"❌ Whisper transcription error: {e}")
            raise Exception(f"Failed to transcribe audio: {str(e)}")

    async def generate_speech(
        self,
        text: str,
        language: str = 'en-US',
        voice: str = 'alloy',
        speed: float = 1.0
    ) -> bytes:
        """
        Generate speech from text using TTS API

        Args:
            text: Text to convert to speech
            language: Language code (not used by TTS, but for voice selection)
            voice: Voice ID (alloy, echo, fable, onyx, nova, shimmer)
            speed: Speech speed (0.25 to 4.0)

        Returns:
            Audio data as bytes (MP3 format)
        """
        try:
            # Select appropriate voice based on language
            # OpenAI TTS voices are multilingual but have different characteristics
            voice_map = {
                'en': 'alloy',    # Neutral, good for English
                'hi': 'nova',     # Female, works well for Indian languages
                'es': 'onyx',     # Male, good for Spanish
                'fr': 'shimmer',  # Female, good for French
                'de': 'fable',    # Male, good for German
                'zh': 'echo',     # Male, good for Chinese
                'ja': 'nova',     # Female, good for Japanese
            }

            lang_code = language[:2]
            selected_voice = voice_map.get(lang_code, voice)

            # Call TTS API
            if self.use_azure:
                response = await self.client.audio.speech.create(
                    model=settings.AZURE_TTS_DEPLOYMENT_NAME or "tts-1",
                    voice=selected_voice,
                    input=text,
                    speed=speed,
                    response_format="mp3"
                )
            else:
                response = await self.client.audio.speech.create(
                    model="tts-1",  # or "tts-1-hd" for higher quality
                    voice=selected_voice,
                    input=text,
                    speed=speed,
                    response_format="mp3"
                )

            # Return audio bytes
            return response.content

        except Exception as e:
            print(f"❌ TTS generation error: {e}")
            raise Exception(f"Failed to generate speech: {str(e)}")

    async def translate_text(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> Dict[str, Any]:
        """
        Translate text using GPT-4

        Args:
            text: Text to translate
            source_lang: Source language code (e.g., 'hi-IN')
            target_lang: Target language code (e.g., 'en-US')

        Returns:
            {
                'translated_text': 'translated content',
                'source_language': 'Hindi',
                'target_language': 'English',
                'confidence': 0.95
            }
        """
        try:
            # Get language names
            source_name = self.language_names.get(source_lang, source_lang)
            target_name = self.language_names.get(target_lang, target_lang)

            # Skip if same language
            if source_lang[:2] == target_lang[:2]:
                return {
                    'translated_text': text,
                    'source_language': source_name,
                    'target_language': target_name,
                    'confidence': 1.0,
                    'skipped': True
                }

            # Prepare translation prompt
            system_prompt = f"""You are an expert translator specializing in astrological and spiritual content.
Translate the following text from {source_name} to {target_name}.

IMPORTANT RULES:
1. Maintain the tone and formality
2. Preserve astrological terms accurately (e.g., Mahadasha, Antardasha, Rashi)
3. Keep Sanskrit/Vedic terms in original form (e.g., Vimshottari, BPHS)
4. If translating astrological interpretations, ensure accuracy
5. Return ONLY the translated text, no explanations

Text to translate:"""

            # Call GPT-4 for translation
            if self.use_azure:
                response = await self.client.chat.completions.create(
                    model=settings.AZURE_GPT4_DEPLOYMENT_NAME or settings.AZURE_OPENAI_DEPLOYMENT or "gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": text}
                    ],
                    temperature=0.3,  # Low temperature for consistent translation
                    max_tokens=2000
                )
            else:
                response = await self.client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": text}
                    ],
                    temperature=0.3,
                    max_tokens=2000
                )

            translated_text = response.choices[0].message.content.strip()

            return {
                'translated_text': translated_text,
                'source_language': source_name,
                'target_language': target_name,
                'confidence': 0.9,  # GPT-4 translations are high quality
                'tokens_used': response.usage.total_tokens if hasattr(response, 'usage') else 0
            }

        except Exception as e:
            print(f"❌ Translation error: {e}")
            raise Exception(f"Failed to translate text: {str(e)}")

    async def detect_language(self, text: str) -> str:
        """
        Detect language of text using GPT-4

        Args:
            text: Text to analyze

        Returns:
            ISO language code (e.g., 'hi-IN', 'en-US')
        """
        try:
            prompt = f"""Detect the language of the following text and return ONLY the ISO 639-1 language code (e.g., 'en', 'hi', 'es').

Text: {text[:200]}

Language code:"""

            response = await self.client.chat.completions.create(
                model="gpt-4" if self.use_azure else "gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=10
            )

            lang_code = response.choices[0].message.content.strip().lower()

            # Map to full locale code
            locale_map = {
                'en': 'en-US',
                'hi': 'hi-IN',
                'mr': 'mr-IN',
                'gu': 'gu-IN',
                'ta': 'ta-IN',
                'te': 'te-IN',
                'kn': 'kn-IN',
                'bn': 'bn-IN',
                'pa': 'pa-IN',
                'es': 'es-ES',
                'fr': 'fr-FR',
                'de': 'de-DE',
                'zh': 'zh-CN',
                'ja': 'ja-JP',
                'ko': 'ko-KR',
            }

            return locale_map.get(lang_code, 'en-US')

        except Exception as e:
            print(f"⚠️ Language detection error: {e}")
            return 'en-US'  # Default to English


# Global instance
openai_voice_service = OpenAIVoiceService()
