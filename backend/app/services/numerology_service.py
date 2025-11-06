"""
Numerology Service - Western/Pythagorean and Vedic/Chaldean Calculations

This module provides comprehensive numerology calculation capabilities:
- Western/Pythagorean system (Life Path, Expression, Soul Urge, etc.)
- Vedic/Chaldean system (Psychic Number, Destiny Number, etc.)
- Cycle calculations (Personal Year, Pinnacles, Challenges)
- Name correction suggestions

Author: JioAstro Team
Created: 2025-11-05
"""

from datetime import date, datetime
from typing import Dict, List, Any, Optional, Tuple
import hashlib
import re


# ============================================================================
# PYTHAGOREAN LETTER-TO-NUMBER MAPPING (A=1, B=2, ..., I=9, J=1, ...)
# ============================================================================

PYTHAGOREAN_MAP = {
    'A': 1, 'J': 1, 'S': 1,
    'B': 2, 'K': 2, 'T': 2,
    'C': 3, 'L': 3, 'U': 3,
    'D': 4, 'M': 4, 'V': 4,
    'E': 5, 'N': 5, 'W': 5,
    'F': 6, 'O': 6, 'X': 6,
    'G': 7, 'P': 7, 'Y': 7,
    'H': 8, 'Q': 8, 'Z': 8,
    'I': 9, 'R': 9
}

# ============================================================================
# CHALDEAN LETTER-TO-NUMBER MAPPING (Different system, no 9)
# ============================================================================

CHALDEAN_MAP = {
    'A': 1, 'I': 1, 'J': 1, 'Q': 1, 'Y': 1,
    'B': 2, 'K': 2, 'R': 2,
    'C': 3, 'G': 3, 'L': 3, 'S': 3,
    'D': 4, 'M': 4, 'T': 4,
    'E': 5, 'H': 5, 'N': 5, 'X': 5,
    'U': 6, 'V': 6, 'W': 6,
    'O': 7, 'Z': 7,
    'F': 8, 'P': 8
}

# ============================================================================
# VEDIC PLANET ASSOCIATIONS
# ============================================================================

PLANET_MAP = {
    1: "Sun",
    2: "Moon",
    3: "Jupiter",
    4: "Rahu",
    5: "Mercury",
    6: "Venus",
    7: "Ketu",
    8: "Saturn",
    9: "Mars"
}

# Favorable and unfavorable number combinations (Vedic)
FAVORABLE_COMBINATIONS = {
    1: [1, 2, 3, 9],    # Sun friends
    2: [1, 3, 6, 9],    # Moon friends
    3: [1, 2, 3, 6, 9], # Jupiter friends
    4: [5, 6, 8],       # Rahu friends
    5: [4, 5, 6],       # Mercury friends
    6: [3, 4, 5, 6, 8, 9], # Venus friends
    7: [1, 2, 4, 7],    # Ketu friends
    8: [4, 5, 6, 8],    # Saturn friends
    9: [1, 2, 3, 6, 9]  # Mars friends
}

# Master numbers that should not be reduced
MASTER_NUMBERS = {11, 22, 33}

# Karmic debt numbers
KARMIC_DEBT_NUMBERS = {13, 14, 16, 19}

VOWELS = set('AEIOU')


# ============================================================================
# COMPREHENSIVE NUMBER MEANINGS AND INTERPRETATIONS
# ============================================================================

# Life Path Number Meanings (Western/Pythagorean)
LIFE_PATH_MEANINGS = {
    1: {
        "title": "The Leader - The Pioneer",
        "description": "Independent, innovative, and pioneering spirit. Natural leaders who forge new paths.",
        "keywords": ["leadership", "independence", "innovation", "originality", "ambition"],
        "traits": "Independent, pioneering, innovative, courageous, determined, self-reliant",
        "challenges": "Can be domineering, stubborn, impatient, or overly self-centered",
        "purpose": "To develop independence and lead others through innovation and original thinking",
        "career": "Entrepreneur, CEO, inventor, director, self-employed professional",
        "relationships": "Needs independence in relationships; compatible with 3, 5, 6"
    },
    2: {
        "title": "The Peacemaker - The Diplomat",
        "description": "Diplomatic, cooperative, and sensitive. Natural mediators who value harmony.",
        "keywords": ["diplomacy", "cooperation", "harmony", "sensitivity", "partnership"],
        "traits": "Diplomatic, cooperative, sensitive, patient, understanding, intuitive",
        "challenges": "Can be overly dependent, indecisive, passive-aggressive, or too sensitive",
        "purpose": "To bring peace and harmony through cooperation and understanding",
        "career": "Counselor, mediator, diplomat, therapist, HR professional, team player",
        "relationships": "Natural partner; compatible with 6, 8, 9"
    },
    3: {
        "title": "The Creative - The Communicator",
        "description": "Expressive, artistic, and communicative. Natural entertainers and creators.",
        "keywords": ["creativity", "expression", "communication", "joy", "optimism"],
        "traits": "Creative, expressive, optimistic, charming, entertaining, articulate",
        "challenges": "Can be scattered, superficial, extravagant, or avoid serious issues",
        "purpose": "To inspire and uplift others through creative self-expression",
        "career": "Artist, writer, performer, speaker, designer, social media influencer",
        "relationships": "Fun-loving partner; compatible with 1, 5, 7"
    },
    4: {
        "title": "The Builder - The Organizer",
        "description": "Practical, stable, and hardworking. Master builders of solid foundations.",
        "keywords": ["stability", "organization", "discipline", "practicality", "foundation"],
        "traits": "Practical, disciplined, hardworking, reliable, organized, methodical",
        "challenges": "Can be rigid, stubborn, narrow-minded, or workaholic tendencies",
        "purpose": "To build lasting structures and systems through discipline and hard work",
        "career": "Engineer, architect, accountant, project manager, craftsperson, builder",
        "relationships": "Loyal partner; compatible with 2, 7, 8"
    },
    5: {
        "title": "The Freedom Seeker - The Adventurer",
        "description": "Adventurous, versatile, and dynamic. Seekers of freedom and new experiences.",
        "keywords": ["freedom", "adventure", "change", "versatility", "experience"],
        "traits": "Adventurous, versatile, dynamic, curious, adaptable, freedom-loving",
        "challenges": "Can be restless, irresponsible, scattered, or fear commitment",
        "purpose": "To experience life fully and inspire others to embrace change",
        "career": "Travel agent, journalist, salesperson, photographer, entrepreneur, consultant",
        "relationships": "Needs freedom in relationships; compatible with 1, 3, 7"
    },
    6: {
        "title": "The Nurturer - The Caregiver",
        "description": "Responsible, harmonious, and caring. Natural nurturers and problem solvers.",
        "keywords": ["nurturing", "responsibility", "harmony", "service", "family"],
        "traits": "Responsible, nurturing, harmonious, compassionate, protective, family-oriented",
        "challenges": "Can be interfering, anxious, self-righteous, or martyr complex",
        "purpose": "To bring harmony and healing through service and responsibility",
        "career": "Teacher, nurse, counselor, interior designer, chef, social worker",
        "relationships": "Devoted partner; compatible with 1, 2, 9"
    },
    7: {
        "title": "The Seeker - The Analyst",
        "description": "Analytical, spiritual, and introspective. Seekers of truth and wisdom.",
        "keywords": ["spirituality", "analysis", "wisdom", "introspection", "truth"],
        "traits": "Analytical, spiritual, introspective, intuitive, perfectionist, mysterious",
        "challenges": "Can be aloof, secretive, pessimistic, or overly critical",
        "purpose": "To seek truth and share wisdom through deep analysis and spiritual insight",
        "career": "Researcher, analyst, scientist, philosopher, spiritual teacher, investigator",
        "relationships": "Needs intellectual connection; compatible with 3, 4, 5"
    },
    8: {
        "title": "The Powerhouse - The Executive",
        "description": "Ambitious, authoritative, and materially successful. Masters of the material world.",
        "keywords": ["power", "success", "authority", "abundance", "achievement"],
        "traits": "Ambitious, authoritative, confident, business-minded, powerful, successful",
        "challenges": "Can be materialistic, domineering, workaholic, or abuse power",
        "purpose": "To achieve material success and use power for the greater good",
        "career": "Executive, banker, investor, politician, business owner, financial advisor",
        "relationships": "Strong partner; compatible with 2, 4, 6"
    },
    9: {
        "title": "The Humanitarian - The Philanthropist",
        "description": "Compassionate, idealistic, and selfless. Born to serve humanity.",
        "keywords": ["humanitarianism", "compassion", "idealism", "selflessness", "completion"],
        "traits": "Compassionate, idealistic, humanitarian, artistic, romantic, selfless",
        "challenges": "Can be self-sacrificing, emotionally distant, or impractical",
        "purpose": "To serve humanity with compassion and complete the cycle of growth",
        "career": "Humanitarian, non-profit leader, healer, artist, teacher, counselor",
        "relationships": "Universal love; compatible with 2, 3, 6"
    },
    11: {
        "title": "Master Number 11 - The Spiritual Messenger",
        "description": "Intuitive, inspirational, and enlightened. Spiritual messenger with heightened awareness.",
        "keywords": ["intuition", "inspiration", "enlightenment", "spirituality", "idealism"],
        "traits": "Intuitive, inspirational, enlightened, idealistic, visionary, spiritual",
        "challenges": "Can be impractical, nervous, overly sensitive, or struggle with high expectations",
        "purpose": "To inspire and enlighten others through spiritual insight and intuition",
        "career": "Spiritual teacher, psychic, counselor, motivational speaker, artist, healer",
        "relationships": "Seeks spiritual connection; needs understanding partner"
    },
    22: {
        "title": "Master Number 22 - The Master Builder",
        "description": "Visionary, practical idealist, and world-changer. Can turn dreams into reality.",
        "keywords": ["mastery", "vision", "manifestation", "building", "legacy"],
        "traits": "Visionary, practical, master builder, disciplined, powerful, legacy-focused",
        "challenges": "Can be overwhelmed, anxious, demanding, or frustrated by limitations",
        "purpose": "To build lasting structures that benefit humanity on a grand scale",
        "career": "Architect, engineer, CEO of major organization, social entrepreneur, planner",
        "relationships": "Needs supportive partner who understands their grand vision"
    },
    33: {
        "title": "Master Number 33 - The Master Teacher",
        "description": "Compassionate leader and spiritual guide. The most spiritually advanced number.",
        "keywords": ["mastery", "teaching", "compassion", "healing", "guidance"],
        "traits": "Master teacher, compassionate, healing, nurturing, selfless, spiritually advanced",
        "challenges": "Can be burdened by responsibility, self-sacrificing, or struggle with boundaries",
        "purpose": "To uplift humanity through compassionate teaching and spiritual guidance",
        "career": "Spiritual teacher, healer, counselor, humanitarian leader, guide",
        "relationships": "Universal love and compassion; devoted to service"
    }
}

# Expression Number Meanings
EXPRESSION_MEANINGS = {
    1: {
        "title": "Natural Leader",
        "description": "Talented at initiating, leading, and pioneering new ventures.",
        "traits": "Leadership ability, originality, independence, determination, courage"
    },
    2: {
        "title": "Natural Diplomat",
        "description": "Talented at bringing people together and creating harmony.",
        "traits": "Diplomacy, cooperation, sensitivity, patience, musical ability"
    },
    3: {
        "title": "Natural Communicator",
        "description": "Talented at expressing yourself creatively through various mediums.",
        "traits": "Artistic expression, communication, creativity, optimism, charm"
    },
    4: {
        "title": "Natural Organizer",
        "description": "Talented at building structures, systems, and practical solutions.",
        "traits": "Organization, discipline, practicality, reliability, craftsmanship"
    },
    5: {
        "title": "Natural Networker",
        "description": "Talented at adapting, communicating, and experiencing life fully.",
        "traits": "Versatility, adaptability, communication, curiosity, freedom-seeking"
    },
    6: {
        "title": "Natural Counselor",
        "description": "Talented at nurturing, healing, and creating harmony.",
        "traits": "Nurturing, responsibility, harmony, artistic sense, counseling ability"
    },
    7: {
        "title": "Natural Analyst",
        "description": "Talented at research, analysis, and uncovering hidden truths.",
        "traits": "Analysis, research, intuition, spirituality, perfectionism"
    },
    8: {
        "title": "Natural Executive",
        "description": "Talented at managing, organizing, and achieving material success.",
        "traits": "Business acumen, management, ambition, authority, material success"
    },
    9: {
        "title": "Natural Humanitarian",
        "description": "Talented at serving others and making a positive impact on the world.",
        "traits": "Humanitarianism, compassion, artistic ability, idealism, generosity"
    },
    11: {
        "title": "Natural Illuminator",
        "description": "Talented at inspiring and enlightening others through spiritual insight.",
        "traits": "Intuition, inspiration, spiritual awareness, idealism, inventiveness"
    },
    22: {
        "title": "Natural Master Builder",
        "description": "Talented at manifesting grand visions into practical reality.",
        "traits": "Master building, large-scale vision, practical idealism, discipline"
    },
    33: {
        "title": "Natural Master Healer",
        "description": "Talented at healing and uplifting humanity through compassionate service.",
        "traits": "Master healing, compassionate teaching, selfless service, spiritual guidance"
    }
}

# Soul Urge Number Meanings (Heart's Desire)
SOUL_URGE_MEANINGS = {
    1: "Desires independence, leadership, and recognition for individual achievements",
    2: "Desires peace, harmony, and meaningful partnerships",
    3: "Desires creative expression, joy, and social interaction",
    4: "Desires stability, order, and practical accomplishments",
    5: "Desires freedom, adventure, and varied experiences",
    6: "Desires to nurture, create harmony, and be appreciated for service",
    7: "Desires wisdom, understanding, and spiritual growth",
    8: "Desires success, recognition, and material abundance",
    9: "Desires to serve humanity and make the world better",
    11: "Desires spiritual enlightenment and to inspire others",
    22: "Desires to leave a lasting legacy that benefits humanity",
    33: "Desires to heal and uplift the world through compassionate teaching"
}

# Personality Number Meanings (First Impression)
PERSONALITY_MEANINGS = {
    1: "Appears confident, independent, and capable - a natural leader",
    2: "Appears gentle, diplomatic, and approachable - easy to talk to",
    3: "Appears charming, creative, and entertaining - life of the party",
    4: "Appears practical, reliable, and trustworthy - solid and stable",
    5: "Appears energetic, adventurous, and exciting - fun to be around",
    6: "Appears warm, responsible, and caring - like home",
    7: "Appears mysterious, intelligent, and dignified - intriguing",
    8: "Appears powerful, successful, and authoritative - commanding presence",
    9: "Appears compassionate, artistic, and idealistic - old soul",
    11: "Appears intuitive, inspiring, and otherworldly - spiritually aware",
    22: "Appears capable, disciplined, and visionary - impressive",
    33: "Appears nurturing, wise, and healing - spiritually advanced"
}

# Vedic Psychic Number Meanings (Who You Think You Are)
PSYCHIC_NUMBER_MEANINGS = {
    1: {
        "title": "Sun - Born Leader",
        "planet": "Sun",
        "description": "Natural leadership, confidence, and individuality. Strong ego and sense of self.",
        "personality": "Ambitious, confident, authoritative, dignified, generous, creative",
        "favorable_dates": [1, 10, 19, 28],
        "favorable_colors": ["gold", "orange", "yellow", "copper"],
        "favorable_gems": ["ruby", "red garnet"],
        "favorable_days": ["Sunday"],
        "element": "Fire",
        "characteristics": "Born leaders with strong willpower. Independent, creative, and ambitious. Natural authority figures who inspire others."
    },
    2: {
        "title": "Moon - The Emotional Soul",
        "planet": "Moon",
        "description": "Sensitive, intuitive, and emotionally attuned. Needs emotional security.",
        "personality": "Gentle, diplomatic, imaginative, intuitive, moody, romantic",
        "favorable_dates": [2, 11, 20, 29],
        "favorable_colors": ["white", "cream", "light green", "silver"],
        "favorable_gems": ["pearl", "moonstone"],
        "favorable_days": ["Monday"],
        "element": "Water",
        "characteristics": "Gentle and sensitive souls. Strong intuition and imagination. Need emotional connection and security."
    },
    3: {
        "title": "Jupiter - The Wise Teacher",
        "planet": "Jupiter",
        "description": "Optimistic, wise, and generous. Natural teachers and guides.",
        "personality": "Optimistic, wise, expansive, generous, disciplined, spiritual",
        "favorable_dates": [3, 12, 21, 30],
        "favorable_colors": ["yellow", "gold", "orange", "saffron"],
        "favorable_gems": ["yellow sapphire", "topaz"],
        "favorable_days": ["Thursday"],
        "element": "Ether",
        "characteristics": "Wise, optimistic, and generous. Natural teachers who seek knowledge and spiritual growth."
    },
    4: {
        "title": "Rahu - The Unconventional",
        "planet": "Rahu",
        "description": "Unconventional, mysterious, and materialistic. Sudden changes and transformations.",
        "personality": "Unconventional, secretive, rebellious, materialistic, sudden",
        "favorable_dates": [4, 13, 22, 31],
        "favorable_colors": ["grey", "black", "dark blue"],
        "favorable_gems": ["hessonite", "gomed"],
        "favorable_days": ["Saturday", "Sunday"],
        "element": "Air",
        "characteristics": "Unconventional and mysterious. Experience sudden changes. May face obstacles but achieve through perseverance."
    },
    5: {
        "title": "Mercury - The Communicator",
        "planet": "Mercury",
        "description": "Quick-thinking, communicative, and versatile. Youthful and adaptable.",
        "personality": "Quick, communicative, versatile, youthful, restless, intelligent",
        "favorable_dates": [5, 14, 23],
        "favorable_colors": ["green", "light shades"],
        "favorable_gems": ["emerald", "green tourmaline"],
        "favorable_days": ["Wednesday"],
        "element": "Earth",
        "characteristics": "Quick-witted and versatile. Excellent communicators who adapt easily. Youthful energy throughout life."
    },
    6: {
        "title": "Venus - The Artistic Lover",
        "planet": "Venus",
        "description": "Artistic, loving, and luxurious. Attracted to beauty and comfort.",
        "personality": "Artistic, loving, luxurious, charismatic, sensual, magnetic",
        "favorable_dates": [6, 15, 24],
        "favorable_colors": ["white", "light blue", "pink", "cream"],
        "favorable_gems": ["diamond", "white sapphire"],
        "favorable_days": ["Friday"],
        "element": "Water",
        "characteristics": "Artistic and charming. Love beauty, luxury, and comfort. Magnetic personality that attracts others."
    },
    7: {
        "title": "Ketu - The Spiritual Seeker",
        "planet": "Ketu",
        "description": "Spiritual, mysterious, and detached. Seeks inner wisdom and enlightenment.",
        "personality": "Spiritual, mysterious, intuitive, restless, philosophical, detached",
        "favorable_dates": [7, 16, 25],
        "favorable_colors": ["white", "grey", "light colors"],
        "favorable_gems": ["cat's eye"],
        "favorable_days": ["Monday"],
        "element": "Fire",
        "characteristics": "Deeply spiritual and intuitive. Mysterious and philosophical. Seek enlightenment and inner peace."
    },
    8: {
        "title": "Saturn - The Disciplined Worker",
        "planet": "Saturn",
        "description": "Disciplined, patient, and karmic. Success through hard work and perseverance.",
        "personality": "Disciplined, serious, patient, karmic, authoritative, enduring",
        "favorable_dates": [8, 17, 26],
        "favorable_colors": ["black", "dark blue", "purple"],
        "favorable_gems": ["blue sapphire", "amethyst"],
        "favorable_days": ["Saturday"],
        "element": "Air",
        "characteristics": "Disciplined and hardworking. Face delays but achieve lasting success. Strong sense of duty and responsibility."
    },
    9: {
        "title": "Mars - The Energetic Warrior",
        "planet": "Mars",
        "description": "Energetic, courageous, and action-oriented. Natural fighters and pioneers.",
        "personality": "Energetic, courageous, aggressive, impulsive, competitive, protective",
        "favorable_dates": [9, 18, 27],
        "favorable_colors": ["red", "pink", "orange"],
        "favorable_gems": ["coral", "red carnelian"],
        "favorable_days": ["Tuesday"],
        "element": "Fire",
        "characteristics": "Energetic and courageous. Natural fighters who take action. Competitive spirit and strong will."
    }
}

# Vedic Destiny Number Meanings (How Others See You)
DESTINY_NUMBER_MEANINGS = {
    1: "Others see you as a leader and authority figure. Commanding presence and respect.",
    2: "Others see you as diplomatic and cooperative. Peaceful and approachable demeanor.",
    3: "Others see you as optimistic and creative. Inspiring and uplifting presence.",
    4: "Others see you as reliable and hardworking. Stable and trustworthy presence.",
    5: "Others see you as dynamic and versatile. Exciting and unpredictable presence.",
    6: "Others see you as responsible and caring. Nurturing and harmonious presence.",
    7: "Others see you as wise and mysterious. Spiritual and analytical presence.",
    8: "Others see you as powerful and successful. Authoritative and business-like presence.",
    9: "Others see you as compassionate and humanitarian. Idealistic and generous presence."
}

# Personal Year Meanings (Annual Cycle)
PERSONAL_YEAR_MEANINGS = {
    1: {
        "title": "Year of New Beginnings",
        "theme": "Start fresh, take initiative, plant seeds for the future",
        "energy": "New opportunities, fresh starts, independence, leadership"
    },
    2: {
        "title": "Year of Cooperation",
        "theme": "Patience, partnerships, and diplomacy. Let seeds grow.",
        "energy": "Relationships, cooperation, patience, sensitivity, balance"
    },
    3: {
        "title": "Year of Creative Expression",
        "theme": "Express yourself, socialize, enjoy life. First harvest.",
        "energy": "Creativity, communication, joy, social expansion, self-expression"
    },
    4: {
        "title": "Year of Building Foundations",
        "theme": "Hard work, discipline, and building for the future.",
        "energy": "Hard work, discipline, organization, building, stability"
    },
    5: {
        "title": "Year of Change and Freedom",
        "theme": "Embrace change, travel, experience new things.",
        "energy": "Change, freedom, adventure, travel, expansion, unpredictability"
    },
    6: {
        "title": "Year of Responsibility",
        "theme": "Focus on home, family, and service to others.",
        "energy": "Responsibility, family, home, service, nurturing, harmony"
    },
    7: {
        "title": "Year of Introspection",
        "theme": "Rest, reflect, and seek inner wisdom. Spiritual growth.",
        "energy": "Introspection, spirituality, rest, analysis, inner growth"
    },
    8: {
        "title": "Year of Power and Achievement",
        "theme": "Achieve goals, gain recognition, financial success.",
        "energy": "Achievement, power, recognition, financial success, authority"
    },
    9: {
        "title": "Year of Completion",
        "theme": "Let go, complete projects, prepare for new cycle.",
        "energy": "Completion, release, humanitarianism, endings, transformation"
    }
}

# Karmic Debt Number Meanings
KARMIC_DEBT_MEANINGS = {
    13: {
        "number": "13/4",
        "title": "Karmic Debt of Laziness",
        "lesson": "Must overcome laziness and work hard in this lifetime. Previous life had wasted opportunities.",
        "challenge": "Tendency to take shortcuts, avoid hard work, or give up easily",
        "resolution": "Develop discipline, persistence, and commitment to hard work"
    },
    14: {
        "number": "14/5",
        "title": "Karmic Debt of Abuse of Freedom",
        "lesson": "Must learn moderation and responsibility. Previous life had excessive indulgence.",
        "challenge": "Tendency toward excess, addiction, or irresponsible behavior",
        "resolution": "Practice moderation, responsibility, and constructive use of freedom"
    },
    16: {
        "number": "16/7",
        "title": "Karmic Debt of Abuse of Love",
        "lesson": "Must rebuild relationships with humility. Previous life had ego issues in relationships.",
        "challenge": "Relationship challenges, ego battles, unexpected setbacks",
        "resolution": "Develop humility, authentic love, and spiritual awareness"
    },
    19: {
        "number": "19/1",
        "title": "Karmic Debt of Abuse of Power",
        "lesson": "Must learn to serve others. Previous life misused power and authority.",
        "challenge": "Difficulty accepting help, tendency toward isolation or domination",
        "resolution": "Learn interdependence, serve others, develop humility"
    }
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def normalize_name(name: str) -> str:
    """Normalize name by removing special characters and converting to uppercase."""
    # Remove numbers and special characters, keep only letters and spaces
    normalized = re.sub(r'[^A-Za-z\s]', '', name)
    return normalized.upper().strip()


def reduce_to_single_digit(number: int, preserve_master: bool = True) -> int:
    """
    Reduce a number to single digit (1-9).

    Args:
        number: The number to reduce
        preserve_master: If True, preserve master numbers (11, 22, 33)

    Returns:
        Reduced single digit or master number
    """
    if preserve_master and number in MASTER_NUMBERS:
        return number

    while number > 9:
        number = sum(int(digit) for digit in str(number))
        if preserve_master and number in MASTER_NUMBERS:
            return number

    return number


def get_letter_value(letter: str, system: str = 'pythagorean') -> int:
    """
    Get numeric value for a letter based on numerology system.

    Args:
        letter: Single letter character
        system: 'pythagorean' or 'chaldean'

    Returns:
        Numeric value of the letter
    """
    letter = letter.upper()

    if system == 'pythagorean':
        return PYTHAGOREAN_MAP.get(letter, 0)
    elif system == 'chaldean':
        return CHALDEAN_MAP.get(letter, 0)
    else:
        raise ValueError(f"Unknown system: {system}")


def calculate_name_value(name: str, system: str = 'pythagorean',
                         filter_letters: Optional[set] = None) -> Tuple[int, List[Dict[str, Any]]]:
    """
    Calculate the numeric value of a name.

    Args:
        name: The name to calculate
        system: 'pythagorean' or 'chaldean'
        filter_letters: If provided, only count these letters (e.g., vowels only)

    Returns:
        Tuple of (total_value, letter_breakdown)
    """
    name = normalize_name(name)
    letter_breakdown = []
    total = 0

    for char in name:
        if char == ' ':
            continue

        # Apply filter if provided
        if filter_letters and char not in filter_letters:
            continue

        value = get_letter_value(char, system)
        if value > 0:
            letter_breakdown.append({
                'letter': char,
                'value': value
            })
            total += value

    return total, letter_breakdown


def generate_calculation_hash(full_name: str, birth_date: date, system: str) -> str:
    """
    Generate a hash for caching numerology calculations.

    Args:
        full_name: Full name of the person
        birth_date: Birth date
        system: Numerology system ('western', 'vedic', 'both')

    Returns:
        SHA256 hash string
    """
    data = f"{full_name.lower()}|{birth_date.isoformat()}|{system}"
    return hashlib.sha256(data.encode()).hexdigest()


# ============================================================================
# WESTERN/PYTHAGOREAN NUMEROLOGY CLASS
# ============================================================================

class WesternNumerology:
    """
    Western/Pythagorean numerology calculation engine.

    Implements calculations for:
    - Life Path Number
    - Expression/Destiny Number
    - Soul Urge/Heart's Desire Number
    - Personality Number
    - Maturity Number
    - Birth Day Number
    - Master Numbers (11, 22, 33)
    - Karmic Debt Numbers (13, 14, 16, 19)
    - Personal Year/Month/Day
    - Pinnacles
    - Challenges
    """

    @staticmethod
    def calculate_life_path(birth_date: date) -> Dict[str, Any]:
        """
        Calculate Life Path number from birth date.

        The Life Path is the most important number in numerology, representing
        your life's purpose and the path you'll walk in this lifetime.

        Method: Add all digits of birth date, reducing to single digit or master number.
        Alternative method: Reduce month, day, year separately then add (more accurate for master numbers).

        Args:
            birth_date: Date of birth

        Returns:
            Dict with 'number', 'is_master', 'breakdown', 'karmic_debt'
        """
        year = birth_date.year
        month = birth_date.month
        day = birth_date.day

        # Calculate component sums, but preserve master numbers for day/month
        month_sum = sum(int(d) for d in str(month))
        year_sum = sum(int(digit) for digit in str(year))

        # If day is master number (11, 22), preserve it; otherwise sum digits
        if day in MASTER_NUMBERS:
            day_sum = day
        else:
            day_sum = sum(int(d) for d in str(day))

        # If month is master number (11), preserve it; otherwise use sum
        if month in MASTER_NUMBERS:
            month_sum_for_total = month
        else:
            month_sum_for_total = month_sum

        # Sum all components (with master numbers preserved)
        all_digits_sum = month_sum_for_total + day_sum + year_sum

        # For breakdown, show component-wise reduction
        month_reduced = reduce_to_single_digit(month, preserve_master=True)
        day_reduced = reduce_to_single_digit(day, preserve_master=True)
        year_reduced = reduce_to_single_digit(year_sum, preserve_master=True)

        # Detect karmic debt in intermediate sums (check both methods)
        karmic_debt = None
        # Method 1: Check sums with component digits
        intermediate_sums_1 = [day, month + day, month_sum + day_sum + year_sum, all_digits_sum]
        # Method 2: Check sums with fully reduced components
        reduced_sum = month_reduced + day_reduced + year_reduced
        intermediate_sums_2 = [reduced_sum]

        for num in intermediate_sums_1 + intermediate_sums_2:
            if num in KARMIC_DEBT_NUMBERS:
                karmic_debt = num
                break

        # Reduce to life path number (preserving master numbers)
        life_path = reduce_to_single_digit(all_digits_sum, preserve_master=True)

        # Get meaning/interpretation
        meaning_data = LIFE_PATH_MEANINGS.get(life_path, {})

        # Get karmic debt meaning if applicable
        karmic_meaning = None
        if karmic_debt:
            karmic_meaning = KARMIC_DEBT_MEANINGS.get(karmic_debt, {})

        return {
            'number': life_path,
            'is_master': life_path in MASTER_NUMBERS,
            'karmic_debt': karmic_debt,
            'karmic_debt_meaning': karmic_meaning,
            'meaning': meaning_data,
            'breakdown': {
                'month': month,
                'day': day,
                'year': year,
                'month_reduced': month_reduced,
                'day_reduced': day_reduced,
                'year_reduced': year_reduced,
                'sum_before_reduction': all_digits_sum,
                'final': life_path
            }
        }

    @staticmethod
    def calculate_expression(full_name: str) -> Dict[str, Any]:
        """
        Calculate Expression/Destiny number from full name.

        The Expression number reveals your natural talents, abilities, and
        shortcomings that you were born with.

        Method: Convert all letters to numbers and add them up.

        Args:
            full_name: Full birth name

        Returns:
            Dict with 'number', 'is_master', 'letter_values', 'breakdown'
        """
        total, letter_breakdown = calculate_name_value(full_name, 'pythagorean')

        # Check for karmic debt in intermediate sum
        karmic_debt = total if total in KARMIC_DEBT_NUMBERS else None

        # Reduce to single digit or master number
        expression = reduce_to_single_digit(total, preserve_master=True)

        # Get meaning/interpretation
        meaning_data = EXPRESSION_MEANINGS.get(expression, {})

        # Get karmic debt meaning if applicable
        karmic_meaning = None
        if karmic_debt:
            karmic_meaning = KARMIC_DEBT_MEANINGS.get(karmic_debt, {})

        return {
            'number': expression,
            'is_master': expression in MASTER_NUMBERS,
            'karmic_debt': karmic_debt,
            'karmic_debt_meaning': karmic_meaning,
            'meaning': meaning_data,
            'letter_values': letter_breakdown,
            'breakdown': {
                'total_before_reduction': total,
                'final': expression
            }
        }

    @staticmethod
    def calculate_soul_urge(full_name: str) -> Dict[str, Any]:
        """
        Calculate Soul Urge/Heart's Desire number from vowels in name.

        The Soul Urge number represents your inner motivation, what your
        heart truly desires.

        Method: Add numeric values of vowels only.

        Args:
            full_name: Full birth name

        Returns:
            Dict with 'number', 'is_master', 'vowel_values', 'breakdown'
        """
        total, vowel_breakdown = calculate_name_value(full_name, 'pythagorean', filter_letters=VOWELS)

        karmic_debt = total if total in KARMIC_DEBT_NUMBERS else None
        soul_urge = reduce_to_single_digit(total, preserve_master=True)

        # Get meaning/interpretation
        meaning_text = SOUL_URGE_MEANINGS.get(soul_urge, "Inner desires and motivations")

        return {
            'number': soul_urge,
            'is_master': soul_urge in MASTER_NUMBERS,
            'karmic_debt': karmic_debt,
            'meaning': {'description': meaning_text},
            'vowel_values': vowel_breakdown,
            'breakdown': {
                'total_before_reduction': total,
                'final': soul_urge
            }
        }

    @staticmethod
    def calculate_personality(full_name: str) -> Dict[str, Any]:
        """
        Calculate Personality number from consonants in name.

        The Personality number represents how others perceive you,
        your outer personality.

        Method: Add numeric values of consonants only.

        Args:
            full_name: Full birth name

        Returns:
            Dict with 'number', 'is_master', 'consonant_values', 'breakdown'
        """
        # Get all letters except vowels
        name = normalize_name(full_name)
        consonants = set(char for char in name if char.isalpha() and char not in VOWELS)

        total, consonant_breakdown = calculate_name_value(full_name, 'pythagorean', filter_letters=consonants)

        karmic_debt = total if total in KARMIC_DEBT_NUMBERS else None
        personality = reduce_to_single_digit(total, preserve_master=True)

        # Get meaning/interpretation
        meaning_text = PERSONALITY_MEANINGS.get(personality, "How others perceive you")

        return {
            'number': personality,
            'is_master': personality in MASTER_NUMBERS,
            'karmic_debt': karmic_debt,
            'meaning': {'description': meaning_text},
            'consonant_values': consonant_breakdown,
            'breakdown': {
                'total_before_reduction': total,
                'final': personality
            }
        }

    @staticmethod
    def calculate_maturity(life_path: int, expression: int) -> Dict[str, Any]:
        """
        Calculate Maturity number.

        The Maturity number indicates your ultimate goal in life,
        what you're working toward. It becomes significant after age 30-35.

        Method: Life Path + Expression, reduced.

        Args:
            life_path: Life Path number
            expression: Expression number

        Returns:
            Dict with 'number', 'is_master', 'breakdown'
        """
        total = life_path + expression
        maturity = reduce_to_single_digit(total, preserve_master=True)

        return {
            'number': maturity,
            'is_master': maturity in MASTER_NUMBERS,
            'breakdown': {
                'life_path': life_path,
                'expression': expression,
                'sum': total,
                'final': maturity
            }
        }

    @staticmethod
    def calculate_birth_day(birth_date: date) -> Dict[str, Any]:
        """
        Calculate Birth Day number.

        The Birth Day number represents a special talent or gift you possess.

        Method: Reduce day of birth to single digit or master number.

        Args:
            birth_date: Date of birth

        Returns:
            Dict with 'number', 'is_master'
        """
        day = birth_date.day
        birth_day = reduce_to_single_digit(day, preserve_master=True)

        return {
            'number': birth_day,
            'is_master': birth_day in MASTER_NUMBERS,
            'breakdown': {
                'day': day,
                'final': birth_day
            }
        }

    @staticmethod
    def detect_master_numbers(numbers: Dict[str, int]) -> List[int]:
        """
        Detect all master numbers present in the chart.

        Args:
            numbers: Dict of number type -> value

        Returns:
            List of master numbers found
        """
        return [num for num in numbers.values() if num in MASTER_NUMBERS]

    @staticmethod
    def detect_karmic_debt(birth_date: date, full_name: str) -> List[Dict[str, Any]]:
        """
        Detect karmic debt numbers in the chart.

        Karmic debt numbers (13, 14, 16, 19) indicate lessons from past lives
        that need to be learned in this lifetime.

        Args:
            birth_date: Date of birth
            full_name: Full birth name

        Returns:
            List of karmic debt occurrences with context
        """
        karmic_debts = []

        # Check Life Path
        life_path_data = WesternNumerology.calculate_life_path(birth_date)
        if life_path_data.get('karmic_debt'):
            karmic_debts.append({
                'number': life_path_data['karmic_debt'],
                'location': 'life_path',
                'context': 'Life Path karmic debt'
            })

        # Check Expression
        expression_data = WesternNumerology.calculate_expression(full_name)
        if expression_data.get('karmic_debt'):
            karmic_debts.append({
                'number': expression_data['karmic_debt'],
                'location': 'expression',
                'context': 'Expression karmic debt'
            })

        # Check day of birth directly
        if birth_date.day in KARMIC_DEBT_NUMBERS:
            karmic_debts.append({
                'number': birth_date.day,
                'location': 'birth_day',
                'context': 'Born on karmic debt day'
            })

        return karmic_debts

    @staticmethod
    def calculate_personal_year(birth_date: date, current_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Calculate Personal Year number.

        The Personal Year indicates the theme and opportunities for the current year.
        It's a 9-year cycle.

        Method: Birth month + Birth day + Current year, reduced.

        Args:
            birth_date: Date of birth
            current_date: Current date (defaults to today)

        Returns:
            Dict with 'number', 'year', 'cycle_position', 'breakdown'
        """
        if current_date is None:
            current_date = date.today()

        current_year = current_date.year
        birth_month = birth_date.month
        birth_day = birth_date.day

        # Personal Year = birth month + birth day + current year (all reduced)
        total = birth_month + birth_day + current_year
        personal_year = reduce_to_single_digit(total, preserve_master=False)  # Personal Year doesn't preserve master numbers

        # Get meaning/interpretation
        meaning_data = PERSONAL_YEAR_MEANINGS.get(personal_year, {})

        return {
            'number': personal_year,
            'year': current_year,
            'cycle_position': f"Year {personal_year} of 9",
            'meaning': meaning_data,
            'breakdown': {
                'birth_month': birth_month,
                'birth_day': birth_day,
                'current_year': current_year,
                'sum': total,
                'final': personal_year
            }
        }

    @staticmethod
    def calculate_personal_month(birth_date: date, current_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Calculate Personal Month number.

        The Personal Month refines the Personal Year theme for the current month.

        Method: Personal Year + Current Month, reduced.

        Args:
            birth_date: Date of birth
            current_date: Current date (defaults to today)

        Returns:
            Dict with 'number', 'month', 'year', 'breakdown'
        """
        if current_date is None:
            current_date = date.today()

        personal_year_data = WesternNumerology.calculate_personal_year(birth_date, current_date)
        personal_year = personal_year_data['number']
        current_month = current_date.month

        total = personal_year + current_month
        personal_month = reduce_to_single_digit(total, preserve_master=False)

        return {
            'number': personal_month,
            'month': current_month,
            'year': current_date.year,
            'breakdown': {
                'personal_year': personal_year,
                'current_month': current_month,
                'sum': total,
                'final': personal_month
            }
        }

    @staticmethod
    def calculate_personal_day(birth_date: date, current_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Calculate Personal Day number.

        The Personal Day gives daily guidance within the current month and year.

        Method: Personal Month + Current Day, reduced.

        Args:
            birth_date: Date of birth
            current_date: Current date (defaults to today)

        Returns:
            Dict with 'number', 'date', 'breakdown'
        """
        if current_date is None:
            current_date = date.today()

        personal_month_data = WesternNumerology.calculate_personal_month(birth_date, current_date)
        personal_month = personal_month_data['number']
        current_day = current_date.day

        total = personal_month + current_day
        personal_day = reduce_to_single_digit(total, preserve_master=False)

        return {
            'number': personal_day,
            'date': current_date.isoformat(),
            'breakdown': {
                'personal_month': personal_month,
                'current_day': current_day,
                'sum': total,
                'final': personal_day
            }
        }

    @staticmethod
    def calculate_pinnacles(birth_date: date) -> List[Dict[str, Any]]:
        """
        Calculate the 4 Pinnacle periods.

        Pinnacles represent opportunities and challenges during different life periods.
        Each pinnacle lasts several years and guides major life events.

        Calculation:
        - First Pinnacle: Month + Day
        - Second Pinnacle: Day + Year
        - Third Pinnacle: First + Second
        - Fourth Pinnacle: Month + Year

        Age ranges:
        - First: Birth to (36 - Life Path)
        - Second: Next 9 years
        - Third: Next 9 years
        - Fourth: Remainder of life

        Args:
            birth_date: Date of birth

        Returns:
            List of 4 pinnacles with number, start_age, end_age
        """
        month = birth_date.month
        day = birth_date.day
        year = birth_date.year

        # Calculate year sum
        year_sum = sum(int(digit) for digit in str(year))

        # Calculate Life Path for age ranges
        life_path_data = WesternNumerology.calculate_life_path(birth_date)
        life_path = life_path_data['number']

        # Calculate pinnacle numbers
        first_pinnacle_num = reduce_to_single_digit(month + day, preserve_master=True)
        second_pinnacle_num = reduce_to_single_digit(day + year_sum, preserve_master=True)
        third_pinnacle_num = reduce_to_single_digit(first_pinnacle_num + second_pinnacle_num, preserve_master=True)
        fourth_pinnacle_num = reduce_to_single_digit(month + year_sum, preserve_master=True)

        # Calculate age ranges
        first_end_age = 36 - life_path
        second_end_age = first_end_age + 9
        third_end_age = second_end_age + 9

        pinnacles = [
            {
                'period': 1,
                'number': first_pinnacle_num,
                'start_age': 0,
                'end_age': first_end_age,
                'description': f'First Pinnacle ({first_pinnacle_num}): Birth to age {first_end_age}'
            },
            {
                'period': 2,
                'number': second_pinnacle_num,
                'start_age': first_end_age + 1,
                'end_age': second_end_age,
                'description': f'Second Pinnacle ({second_pinnacle_num}): Age {first_end_age + 1} to {second_end_age}'
            },
            {
                'period': 3,
                'number': third_pinnacle_num,
                'start_age': second_end_age + 1,
                'end_age': third_end_age,
                'description': f'Third Pinnacle ({third_pinnacle_num}): Age {second_end_age + 1} to {third_end_age}'
            },
            {
                'period': 4,
                'number': fourth_pinnacle_num,
                'start_age': third_end_age + 1,
                'end_age': None,  # Remainder of life
                'description': f'Fourth Pinnacle ({fourth_pinnacle_num}): Age {third_end_age + 1} onwards'
            }
        ]

        return pinnacles

    @staticmethod
    def calculate_challenges(birth_date: date) -> List[Dict[str, Any]]:
        """
        Calculate the 4 Challenge periods.

        Challenges represent obstacles and lessons to overcome during life.
        They use subtraction (always positive difference).

        Calculation:
        - First Challenge: |Month - Day|
        - Second Challenge: |Day - Year|
        - Third Challenge: |First - Second|
        - Fourth Challenge: |Month - Year| (Main Life Challenge)

        Age ranges match Pinnacles.

        Args:
            birth_date: Date of birth

        Returns:
            List of 4 challenges with number, start_age, end_age
        """
        month = birth_date.month
        day = birth_date.day
        year = birth_date.year

        # Reduce to single digits first
        month_reduced = reduce_to_single_digit(month, preserve_master=False)
        day_reduced = reduce_to_single_digit(day, preserve_master=False)

        year_sum = sum(int(digit) for digit in str(year))
        year_reduced = reduce_to_single_digit(year_sum, preserve_master=False)

        # Calculate Life Path for age ranges
        life_path_data = WesternNumerology.calculate_life_path(birth_date)
        life_path = life_path_data['number']

        # Calculate challenge numbers (always positive difference)
        first_challenge_num = abs(month_reduced - day_reduced)
        second_challenge_num = abs(day_reduced - year_reduced)
        third_challenge_num = abs(first_challenge_num - second_challenge_num)
        fourth_challenge_num = abs(month_reduced - year_reduced)

        # Calculate age ranges (same as pinnacles)
        first_end_age = 36 - life_path
        second_end_age = first_end_age + 9
        third_end_age = second_end_age + 9

        challenges = [
            {
                'period': 1,
                'number': first_challenge_num,
                'start_age': 0,
                'end_age': first_end_age,
                'description': f'First Challenge ({first_challenge_num}): Birth to age {first_end_age}'
            },
            {
                'period': 2,
                'number': second_challenge_num,
                'start_age': first_end_age + 1,
                'end_age': second_end_age,
                'description': f'Second Challenge ({second_challenge_num}): Age {first_end_age + 1} to {second_end_age}'
            },
            {
                'period': 3,
                'number': third_challenge_num,
                'start_age': second_end_age + 1,
                'end_age': third_end_age,
                'description': f'Third Challenge ({third_challenge_num}): Age {second_end_age + 1} to {third_end_age}'
            },
            {
                'period': 4,
                'number': fourth_challenge_num,
                'start_age': third_end_age + 1,
                'end_age': None,  # Remainder of life
                'description': f'Fourth Challenge ({fourth_challenge_num}): Age {third_end_age + 1} onwards - Main Life Challenge'
            }
        ]

        return challenges

    @staticmethod
    def calculate_full_profile(full_name: str, birth_date: date,
                               current_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Calculate complete Western numerology profile.

        Args:
            full_name: Full birth name
            birth_date: Date of birth
            current_date: Current date for cycles (defaults to today)

        Returns:
            Dict with all Western numerology calculations
        """
        # Core numbers
        life_path = WesternNumerology.calculate_life_path(birth_date)
        expression = WesternNumerology.calculate_expression(full_name)
        soul_urge = WesternNumerology.calculate_soul_urge(full_name)
        personality = WesternNumerology.calculate_personality(full_name)
        maturity = WesternNumerology.calculate_maturity(life_path['number'], expression['number'])
        birth_day = WesternNumerology.calculate_birth_day(birth_date)

        # Special numbers
        master_numbers = WesternNumerology.detect_master_numbers({
            'life_path': life_path['number'],
            'expression': expression['number'],
            'soul_urge': soul_urge['number'],
            'personality': personality['number'],
            'maturity': maturity['number'],
            'birth_day': birth_day['number']
        })

        karmic_debt = WesternNumerology.detect_karmic_debt(birth_date, full_name)

        # Cycles
        personal_year = WesternNumerology.calculate_personal_year(birth_date, current_date)
        personal_month = WesternNumerology.calculate_personal_month(birth_date, current_date)
        personal_day = WesternNumerology.calculate_personal_day(birth_date, current_date)

        # Life periods
        pinnacles = WesternNumerology.calculate_pinnacles(birth_date)
        challenges = WesternNumerology.calculate_challenges(birth_date)

        return {
            'system': 'western',
            'core_numbers': {
                'life_path': life_path,
                'expression': expression,
                'soul_urge': soul_urge,
                'personality': personality,
                'maturity': maturity,
                'birth_day': birth_day
            },
            'special_numbers': {
                'master_numbers': master_numbers,
                'karmic_debt': karmic_debt
            },
            'current_cycles': {
                'personal_year': personal_year,
                'personal_month': personal_month,
                'personal_day': personal_day
            },
            'life_periods': {
                'pinnacles': pinnacles,
                'challenges': challenges
            },
            'calculation_hash': generate_calculation_hash(full_name, birth_date, 'western'),
            'calculated_at': datetime.utcnow().isoformat()
        }


# ============================================================================
# VEDIC/CHALDEAN NUMEROLOGY CLASS
# ============================================================================

class VedicNumerology:
    """
    Vedic/Chaldean numerology calculation engine.

    Implements calculations for:
    - Psychic Number (day of birth)
    - Destiny Number (name value using Chaldean system)
    - Name Value
    - Planet associations
    - Favorable/Unfavorable numbers
    - Name correction suggestions
    """

    @staticmethod
    def calculate_psychic_number(birth_date: date) -> Dict[str, Any]:
        """
        Calculate Psychic Number (Moolank).

        The Psychic Number represents how you see yourself internally,
        your inner personality. It's simply the day of birth reduced.

        Method: Reduce day of birth to single digit (1-9).

        Args:
            birth_date: Date of birth

        Returns:
            Dict with 'number', 'planet', 'characteristics'
        """
        day = birth_date.day
        psychic = reduce_to_single_digit(day, preserve_master=False)  # Vedic doesn't use master numbers the same way

        # Get comprehensive meaning/interpretation
        meaning_data = PSYCHIC_NUMBER_MEANINGS.get(psychic, {})

        return {
            'number': psychic,
            'planet': PLANET_MAP[psychic],
            'day_of_birth': day,
            'meaning': meaning_data,
            'breakdown': {
                'day': day,
                'final': psychic
            }
        }

    @staticmethod
    def calculate_destiny_number(input_value) -> Dict[str, Any]:
        """
        Calculate Destiny Number (Bhagyank).

        The Destiny Number represents how others see you and your
        destiny/life path. Can be calculated from birth date or name.

        Method:
        - If date: Sum all digits of birth date (month + day + year)
        - If name: Convert using Chaldean letter-to-number mapping

        Args:
            input_value: Either a date object (for date-based) or string (for name-based)

        Returns:
            Dict with 'number', 'planet', 'meaning', and 'breakdown'
        """
        # Check if input is a date or string
        if isinstance(input_value, date):
            # Date-based calculation: sum all digits
            month = input_value.month
            day = input_value.day
            year = input_value.year

            # Sum all individual digits
            total = sum(int(d) for d in str(month)) + \
                    sum(int(d) for d in str(day)) + \
                    sum(int(d) for d in str(year))

            destiny = reduce_to_single_digit(total, preserve_master=False)

            # Get meaning/interpretation
            meaning_text = DESTINY_NUMBER_MEANINGS.get(destiny, "How others perceive you")

            return {
                'number': destiny,
                'planet': PLANET_MAP[destiny],
                'meaning': meaning_text,
                'breakdown': {
                    'month': month,
                    'day': day,
                    'year': year,
                    'total_before_reduction': total,
                    'final': destiny
                }
            }
        else:
            # Name-based calculation using Chaldean system
            full_name = str(input_value)
            total, letter_breakdown = calculate_name_value(full_name, 'chaldean')
            destiny = reduce_to_single_digit(total, preserve_master=False)

            # Get meaning/interpretation
            meaning_text = DESTINY_NUMBER_MEANINGS.get(destiny, "How others perceive you")

            return {
                'number': destiny,
                'planet': PLANET_MAP[destiny],
                'meaning': meaning_text,  # Keep as string for VedicNameNumber schema
                'letter_values': letter_breakdown,
                'breakdown': {
                    'total_before_reduction': total,
                    'final': destiny
                }
            }

    @staticmethod
    def calculate_name_value(name: str) -> Dict[str, Any]:
        """
        Calculate raw name value (Namank) using Chaldean system.

        Args:
            name: Name to calculate

        Returns:
            Dict with 'number', 'planet', 'letter_values', 'breakdown'
        """
        total, letter_breakdown = calculate_name_value(name, 'chaldean')
        reduced = reduce_to_single_digit(total, preserve_master=False)

        return {
            'number': reduced,  # Use 'number' to match schema
            'reduced': reduced,  # Alias for backward compatibility
            'planet': PLANET_MAP[reduced],
            'letter_values': letter_breakdown,
            'breakdown': {
                'total_before_reduction': total,
                'final': reduced
            }
        }

    @staticmethod
    def get_favorable_numbers(psychic: int, destiny: int) -> Dict[str, Any]:
        """
        Get favorable and unfavorable numbers based on Psychic and Destiny.

        Args:
            psychic: Psychic Number
            destiny: Destiny Number

        Returns:
            Dict with 'favorable', 'unfavorable', 'reasoning'
        """
        # Get favorable for both numbers
        psychic_favorable = set(FAVORABLE_COMBINATIONS.get(psychic, []))
        destiny_favorable = set(FAVORABLE_COMBINATIONS.get(destiny, []))

        # Union for maximum favorable
        all_favorable = list(psychic_favorable | destiny_favorable)

        # Unfavorable are numbers NOT in favorable list
        all_numbers = set(range(1, 10))
        all_unfavorable = list(all_numbers - (psychic_favorable | destiny_favorable))

        return {
            'favorable': sorted(all_favorable),
            'unfavorable': sorted(all_unfavorable),
            'psychic_favorable': sorted(psychic_favorable),
            'destiny_favorable': sorted(destiny_favorable),
            'reasoning': {
                'psychic_planet': PLANET_MAP[psychic],
                'destiny_planet': PLANET_MAP[destiny]
            }
        }

    @staticmethod
    def get_favorable_dates(psychic: int, destiny: int) -> List[int]:
        """
        Get favorable dates of the month based on numerology.

        Args:
            psychic: Psychic Number
            destiny: Destiny Number

        Returns:
            List of favorable dates (1-31)
        """
        favorable_nums = VedicNumerology.get_favorable_numbers(psychic, destiny)['favorable']

        # Dates that reduce to favorable numbers
        favorable_dates = []
        for day in range(1, 32):
            day_reduced = reduce_to_single_digit(day, preserve_master=False)
            if day_reduced in favorable_nums:
                favorable_dates.append(day)

        return favorable_dates

    @staticmethod
    def suggest_name_corrections(full_name: str, psychic: int, destiny: int) -> List[Dict[str, Any]]:
        """
        Suggest name corrections for better numerological harmony.

        Analyzes current name and suggests modifications to improve
        compatibility with Psychic and Destiny numbers.

        Args:
            full_name: Current full name
            psychic: Psychic Number
            destiny: Destiny Number

        Returns:
            List of correction suggestions
        """
        favorable = VedicNumerology.get_favorable_numbers(psychic, destiny)['favorable']
        current_name_data = VedicNumerology.calculate_destiny_number(full_name)
        current_number = current_name_data['number']

        suggestions = []

        # Check if current name is already favorable
        if current_number in favorable:
            suggestions.append({
                'type': 'no_change_needed',
                'message': f'Your current name value ({current_number}) is already favorable',
                'current_value': current_number,
                'impact': 'positive'
            })
        else:
            suggestions.append({
                'type': 'unfavorable',
                'message': f'Your current name value ({current_number}) is not in your favorable numbers',
                'current_value': current_number,
                'favorable_targets': favorable,
                'impact': 'negative'
            })

        # Suggest target numbers
        for target in favorable:
            if target != current_number:
                suggestions.append({
                    'type': 'target_suggestion',
                    'message': f'Consider adjusting name to reach value {target} ({PLANET_MAP[target]})',
                    'target_value': target,
                    'target_planet': PLANET_MAP[target],
                    'impact': 'very_positive'
                })

        return suggestions

    @staticmethod
    def calculate_full_profile(full_name: str, birth_date: date) -> Dict[str, Any]:
        """
        Calculate complete Vedic numerology profile.

        Args:
            full_name: Full name
            birth_date: Date of birth

        Returns:
            Dict with all Vedic numerology calculations
        """
        psychic_data = VedicNumerology.calculate_psychic_number(birth_date)
        destiny_data = VedicNumerology.calculate_destiny_number(full_name)
        name_value = VedicNumerology.calculate_name_value(full_name)

        psychic = psychic_data['number']
        destiny = destiny_data['number']

        favorable = VedicNumerology.get_favorable_numbers(psychic, destiny)
        favorable_dates = VedicNumerology.get_favorable_dates(psychic, destiny)
        corrections = VedicNumerology.suggest_name_corrections(full_name, psychic, destiny)

        return {
            'system': 'vedic',
            'psychic_number': psychic_data,
            'destiny_number': destiny_data,
            'name_value': name_value,
            'planet_associations': {
                'psychic_planet': PLANET_MAP[psychic],
                'destiny_planet': PLANET_MAP[destiny]
            },
            'favorable_numbers': favorable,
            'favorable_dates': favorable_dates,
            'name_corrections': corrections,
            'calculation_hash': generate_calculation_hash(full_name, birth_date, 'vedic'),
            'calculated_at': datetime.utcnow().isoformat()
        }


# ============================================================================
# UNIFIED NUMEROLOGY SERVICE
# ============================================================================

class NumerologyService:
    """
    Unified numerology service providing both Western and Vedic calculations.
    """

    @staticmethod
    def calculate(full_name: str, birth_date: date,
                  system: str = 'both', current_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Calculate numerology profile based on requested system.

        Args:
            full_name: Full birth name
            birth_date: Date of birth
            system: 'western', 'vedic', or 'both'
            current_date: Current date for cycle calculations (Western only)

        Returns:
            Dict with numerology calculations based on system
        """
        result = {
            'full_name': full_name,
            'birth_date': birth_date.isoformat(),
            'system': system,
            'calculated_at': datetime.utcnow().isoformat()
        }

        if system in ['western', 'both']:
            result['western'] = WesternNumerology.calculate_full_profile(
                full_name, birth_date, current_date
            )

        if system in ['vedic', 'both']:
            result['vedic'] = VedicNumerology.calculate_full_profile(
                full_name, birth_date
            )

        # Add unified calculation hash
        result['calculation_hash'] = generate_calculation_hash(full_name, birth_date, system)

        return result
