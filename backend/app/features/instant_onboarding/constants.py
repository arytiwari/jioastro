"""
Constants for Instant Onboarding feature.
"""

# Feature configuration
FEATURE_NAME = "instant_onboarding"
FEATURE_VERSION = "1.0.0"
FEATURE_MAGICAL_NUMBER = 13

# Session configuration
SESSION_EXPIRY_HOURS = 24  # Sessions expire after 24 hours
MAX_SESSIONS_PER_PHONE = 5  # Max concurrent sessions per phone number

# Data collection
REQUIRED_FIELDS = ["name", "birth_date", "birth_time", "latitude", "longitude"]
OPTIONAL_FIELDS = ["birth_place", "timezone"]

# Language support
SUPPORTED_LANGUAGES = ["en", "hi"]  # English, Hindi
DEFAULT_LANGUAGE = "en"

# Channel configuration
SUPPORTED_CHANNELS = ["web", "whatsapp", "voice", "sms"]
DEFAULT_CHANNEL = "web"

# Rate limiting
MAX_SESSIONS_PER_IP_PER_HOUR = 10  # Prevent abuse
CHART_GENERATION_TIMEOUT_SECONDS = 30

# WhatsApp configuration
WHATSAPP_API_VERSION = "v18.0"  # Meta WhatsApp Business API version
WHATSAPP_WEBHOOK_VERIFY_TOKEN = "jioastro_instant_onboarding"  # Should be in env

# Voice configuration
VOICE_MAX_DURATION_SECONDS = 60  # Max audio duration
VOICE_SUPPORTED_FORMATS = ["mp3", "wav", "m4a", "ogg"]

# Chart generation
QUICK_CHART_CACHE_TTL = 3600  # Cache quick charts for 1 hour
INCLUDE_NUMEROLOGY_DEFAULT = False

# Shareable links
SHAREABLE_LINK_EXPIRY_DAYS = 30  # Links expire after 30 days
ENABLE_QR_CODE_GENERATION = True

# Performance targets (from feature requirements)
TARGET_TIME_TO_COMPLETE_SECONDS = 90  # 90 seconds goal
ALERT_IF_SLOWER_THAN_SECONDS = 120  # Alert if taking longer than 2 minutes

# Analytics
TRACK_CONVERSION_EVENTS = True  # Track when users convert to full accounts
TRACK_SHARE_EVENTS = True  # Track when charts are shared
