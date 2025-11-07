"""
Constants for Life Snapshot feature.
"""

# Feature configuration
FEATURE_NAME = "life_snapshot"
FEATURE_VERSION = "1.0.0"
FEATURE_DISPLAY_NAME = "Life Snapshot"

# Cache configuration
SNAPSHOT_CACHE_TTL_SECONDS = 3600  # 1 hour
SNAPSHOT_MAX_AGE_SECONDS = 86400  # 24 hours

# Insights configuration
TOP_THEMES_COUNT = 3
RISKS_COUNT = 3
OPPORTUNITIES_COUNT = 3
ACTIONS_COUNT = 3

# Read time
ESTIMATED_READ_TIME_SECONDS = 60

# Confidence thresholds
MIN_THEME_CONFIDENCE = 0.6
MIN_OPPORTUNITY_CONFIDENCE = 0.5

# Time windows
DEFAULT_TIME_WINDOW_DAYS = 30  # Look ahead 30 days for opportunities

# Scoring weights
WEIGHT_YOGAS = 0.3
WEIGHT_DASHA = 0.25
WEIGHT_TRANSITS = 0.25
WEIGHT_NUMEROLOGY = 0.2

# Severity levels
SEVERITY_LOW = "low"
SEVERITY_MEDIUM = "medium"
SEVERITY_HIGH = "high"

# Priority levels
PRIORITY_LOW = "low"
PRIORITY_MEDIUM = "medium"
PRIORITY_HIGH = "high"

# Life phases
LIFE_PHASE_GROWTH = "Growth Period"
LIFE_PHASE_CONSOLIDATION = "Consolidation Period"
LIFE_PHASE_TRANSFORMATION = "Transformation Period"
LIFE_PHASE_STABILITY = "Stability Period"
LIFE_PHASE_CHALLENGE = "Challenge Period"

# Rate limiting
MAX_REQUESTS_PER_MINUTE = 10
