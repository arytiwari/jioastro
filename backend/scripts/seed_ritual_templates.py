"""
Seed Ritual Templates Database
Populates the ritual_templates table with 10 diverse Vedic ritual templates
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.supabase_client import SupabaseClient


# ============================================================================
# RITUAL TEMPLATE DATA
# ============================================================================

RITUAL_TEMPLATES = [
    # 1. DAILY - Morning Prayers
    {
        "name": "Morning Prayers (Pratha Smarana)",
        "category": "daily",
        "deity": "Brahma",
        "duration_minutes": 5,
        "difficulty": "beginner",
        "description": "Simple morning prayer to begin the day with positive energy and gratitude",
        "required_items": ["water", "clean space"],
        "audio_enabled": True,
        "benefits": [
            "Peaceful start to the day",
            "Increased mental clarity",
            "Positive mindset",
            "Gratitude practice"
        ],
        "best_time_of_day": "Sunrise (Brahma Muhurta)",
        "steps": [
            {
                "step_number": 1,
                "title": "Wake Up and Cleanse",
                "description": "Wake up during Brahma Muhurta (1.5 hours before sunrise), wash face and hands",
                "duration_seconds": 60,
                "required_items": ["water"],
                "tips": ["Use cold water for alertness", "Face East while washing"]
            },
            {
                "step_number": 2,
                "title": "Gratitude Prayer",
                "description": "Sit comfortably, close eyes, and express gratitude for the new day",
                "mantra": "Om Brahmane Namaha",
                "mantra_transliteration": "Om Brahmaane Namaha",
                "mantra_translation": "Salutations to Lord Brahma, the Creator",
                "duration_seconds": 120,
                "tips": ["Sit with straight spine", "Breathe deeply", "Feel grateful"]
            },
            {
                "step_number": 3,
                "title": "Sun Salutation Chant",
                "description": "Face the rising sun and chant surya mantra",
                "mantra": "Om Suryaya Namaha",
                "mantra_transliteration": "Om Sooryaaya Namaha",
                "mantra_translation": "Salutations to the Sun God",
                "duration_seconds": 60,
                "tips": ["Face East", "Stand or sit comfortably"]
            },
            {
                "step_number": 4,
                "title": "Set Daily Intention",
                "description": "Close with a personal intention or prayer for the day ahead",
                "duration_seconds": 60,
                "tips": ["Be specific", "Visualize success", "Stay positive"]
            }
        ]
    },

    # 2. DAILY - Ganesh Puja
    {
        "name": "Ganesh Puja",
        "category": "daily",
        "deity": "Ganesha",
        "duration_minutes": 15,
        "difficulty": "beginner",
        "description": "Daily worship of Lord Ganesha for removing obstacles and ensuring success",
        "required_items": [
            "Ganesh idol or picture",
            "flowers (red hibiscus preferred)",
            "incense sticks",
            "lamp (diya)",
            "coconut",
            "sweets (modak or ladoo)",
            "water",
            "bell"
        ],
        "audio_enabled": True,
        "benefits": [
            "Obstacle removal",
            "Success in new ventures",
            "Mental clarity",
            "Wisdom and prosperity"
        ],
        "best_time_of_day": "Morning or before starting any new work",
        "steps": [
            {
                "step_number": 1,
                "title": "Preparation and Cleansing",
                "description": "Clean the puja area, arrange all items, and sit comfortably facing East",
                "duration_seconds": 60,
                "required_items": ["water", "clean cloth"],
                "tips": ["Maintain cleanliness", "Create calm atmosphere"]
            },
            {
                "step_number": 2,
                "title": "Purification (Achamana)",
                "description": "Sprinkle water around puja area for purification",
                "mantra": "Om Apavitra Pavitra Va Sarvavastham Gatopi Va",
                "mantra_transliteration": "Om Apaavitra Paavitra Vaa Sarvaavasthaam Gatopi Vaa",
                "mantra_translation": "May all impurities be removed, making everything pure",
                "duration_seconds": 60,
                "required_items": ["water"],
                "tips": ["Sprinkle water clockwise"]
            },
            {
                "step_number": 3,
                "title": "Invocation",
                "description": "Ring bell, light lamp and incense, invoke Lord Ganesha",
                "mantra": "Om Gan Ganapataye Namaha",
                "mantra_transliteration": "Om Gam Ganapataye Namaha",
                "mantra_translation": "Salutations to Lord Ganesha",
                "duration_seconds": 120,
                "required_items": ["bell", "lamp", "incense"],
                "tips": ["Ring bell throughout", "Focus on deity"]
            },
            {
                "step_number": 4,
                "title": "Offer Flowers",
                "description": "Place fresh flowers at the feet of Lord Ganesha",
                "mantra": "Om Gajananaya Namaha",
                "mantra_transliteration": "Om Gajaananaaya Namaha",
                "mantra_translation": "Salutations to the elephant-faced Lord",
                "duration_seconds": 120,
                "required_items": ["flowers"],
                "tips": ["Use red flowers if possible"]
            },
            {
                "step_number": 5,
                "title": "Offer Sweets",
                "description": "Place sweets before the deity",
                "mantra": "Om Vakratundaya Namaha",
                "mantra_transliteration": "Om Vakratundaaya Namaha",
                "mantra_translation": "Salutations to the curved-trunk Lord",
                "duration_seconds": 60,
                "required_items": ["sweets"],
                "tips": ["Modak is Lord Ganesha's favorite"]
            },
            {
                "step_number": 6,
                "title": "Aarti",
                "description": "Circle lamp clockwise 7 times while singing aarti",
                "mantra": "Jai Ganesh Jai Ganesh Jai Ganesh Deva",
                "duration_seconds": 180,
                "required_items": ["lamp"],
                "tips": ["Maintain rhythm", "Sing with devotion"]
            },
            {
                "step_number": 7,
                "title": "Prayers and Closing",
                "description": "Make personal prayers and thank Lord Ganesha",
                "mantra": "Om Shanti Shanti Shanti",
                "duration_seconds": 120,
                "tips": ["Bow with gratitude", "Distribute prasad"]
            }
        ]
    },

    # 3. MEDITATION - Gayatri Mantra Japa
    {
        "name": "Gayatri Mantra Japa (108 times)",
        "category": "meditation",
        "deity": "Surya (Sun God)",
        "duration_minutes": 20,
        "difficulty": "intermediate",
        "description": "Chanting the most powerful Vedic mantra 108 times for spiritual enlightenment",
        "required_items": ["mala beads (108 beads)", "quiet space", "mat or cushion"],
        "audio_enabled": True,
        "benefits": [
            "Spiritual awakening",
            "Mental clarity",
            "Wisdom and knowledge",
            "Protection from negative energies",
            "Inner peace"
        ],
        "best_time_of_day": "Sunrise, noon, or sunset",
        "steps": [
            {
                "step_number": 1,
                "title": "Preparation",
                "description": "Sit in a comfortable meditation posture facing East, hold mala in right hand",
                "duration_seconds": 60,
                "required_items": ["mat", "mala beads"],
                "tips": ["Lotus or cross-legged position", "Straight spine", "Relaxed shoulders"]
            },
            {
                "step_number": 2,
                "title": "Pranayama (Breathing)",
                "description": "Perform 5-10 deep breaths to calm the mind",
                "duration_seconds": 120,
                "tips": ["Inhale through nose", "Exhale slowly", "Clear your mind"]
            },
            {
                "step_number": 3,
                "title": "Invoke the Sun God",
                "description": "Close eyes and visualize the rising sun",
                "mantra": "Om Bhur Bhuvah Svah",
                "mantra_transliteration": "Om Bhoor Bhuvah Swaha",
                "mantra_translation": "Om, Earth, Atmosphere, Heaven",
                "duration_seconds": 60,
                "tips": ["Visualize golden light"]
            },
            {
                "step_number": 4,
                "title": "Chant Gayatri Mantra (108 times)",
                "description": "Chant the mantra while moving one bead at a time",
                "mantra": "Om Bhur Bhuvah Svah, Tat Savitur Varenyam, Bhargo Devasya Dhimahi, Dhiyo Yo Nah Prachodayat",
                "mantra_transliteration": "Om Bhoor Bhuvah Swaha, Tat Savitur Varenyam, Bhargo Devasya Dheemahi, Dhiyo Yo Nah Prachodayaat",
                "mantra_translation": "We meditate on the glory of the Creator who has created the Universe, who is worthy of worship, who is the embodiment of knowledge and light, who is the remover of all sins and ignorance. May He enlighten our intellect.",
                "duration_seconds": 900,
                "required_items": ["mala beads"],
                "tips": ["Use thumb and middle finger", "Don't cross the meru (central bead)", "Maintain steady pace"]
            },
            {
                "step_number": 5,
                "title": "Closing Meditation",
                "description": "Sit in silence for a few minutes feeling the vibrations",
                "duration_seconds": 180,
                "tips": ["Observe sensations", "Stay present", "Gradually open eyes"]
            }
        ]
    },

    # 4. SPECIAL - Satyanarayan Puja
    {
        "name": "Satyanarayan Puja",
        "category": "special",
        "deity": "Vishnu",
        "duration_minutes": 90,
        "difficulty": "advanced",
        "description": "Elaborate worship of Lord Vishnu for fulfillment of wishes and family prosperity",
        "required_items": [
            "Vishnu idol or picture",
            "yellow cloth",
            "flowers (tulsi preferred)",
            "fruits",
            "banana",
            "betel leaves and nuts",
            "coconut",
            "incense",
            "lamp",
            "rice",
            "turmeric",
            "kumkum",
            "sweets",
            "panchaamrit (milk, yogurt, ghee, honey, sugar)",
            "kalash (water pot)"
        ],
        "audio_enabled": True,
        "benefits": [
            "Wish fulfillment",
            "Family prosperity",
            "Peace and harmony",
            "Removal of obstacles",
            "Divine blessings"
        ],
        "best_time_of_day": "Morning or evening on auspicious days",
        "steps": [
            {
                "step_number": 1,
                "title": "Setup and Kalash Sthapana",
                "description": "Prepare the altar, setup kalash (water pot) with mango leaves and coconut",
                "duration_seconds": 600,
                "required_items": ["yellow cloth", "kalash", "coconut", "mango leaves"],
                "tips": ["Cover altar with yellow cloth", "Fill kalash with water", "Place coconut on top"]
            },
            {
                "step_number": 2,
                "title": "Sankalp (Resolution)",
                "description": "Take resolution stating your intention for performing the puja",
                "duration_seconds": 180,
                "tips": ["State your name", "State the purpose", "Seek blessings"]
            },
            {
                "step_number": 3,
                "title": "Panchaamrit Abhishek",
                "description": "Bathe the deity with panchaamrit (five nectars)",
                "duration_seconds": 600,
                "required_items": ["milk", "yogurt", "ghee", "honey", "sugar", "water"],
                "tips": ["Pour gently", "Chant Vishnu mantras", "Clean and dry after"]
            },
            {
                "step_number": 4,
                "title": "Shodashopachara (16 Steps)",
                "description": "Perform the 16 traditional steps of worship",
                "duration_seconds": 1800,
                "tips": ["Follow traditional sequence", "Maintain focus", "Offer with devotion"]
            },
            {
                "step_number": 5,
                "title": "Satyanarayan Katha",
                "description": "Read or listen to the sacred story of Lord Satyanarayan",
                "duration_seconds": 1800,
                "tips": ["Read with devotion", "Listen attentively", "Understand the moral"]
            },
            {
                "step_number": 6,
                "title": "Aarti and Prasad",
                "description": "Perform aarti and distribute prasad to all present",
                "duration_seconds": 420,
                "required_items": ["lamp", "bell", "sweets"],
                "tips": ["Sing with devotion", "Distribute to everyone", "Consume with gratitude"]
            }
        ]
    },

    # 5. REMEDIAL - Navagraha Puja
    {
        "name": "Navagraha Puja (Nine Planets)",
        "category": "remedial",
        "deity": "Navagraha",
        "duration_minutes": 60,
        "difficulty": "intermediate",
        "description": "Worship of nine celestial deities to pacify planetary afflictions and seek blessings",
        "required_items": [
            "Navagraha idols or pictures",
            "9 types of flowers",
            "9 types of grains",
            "9 colored cloths",
            "incense",
            "lamps",
            "fruits",
            "sweets"
        ],
        "audio_enabled": True,
        "benefits": [
            "Pacify planetary doshas",
            "Reduce malefic effects",
            "Enhance beneficial planets",
            "Success and prosperity",
            "Health and happiness"
        ],
        "best_time_of_day": "Sunday morning preferred",
        "steps": [
            {
                "step_number": 1,
                "title": "Setup Navagraha Mandala",
                "description": "Arrange the nine planetary deities in traditional formation",
                "duration_seconds": 300,
                "tips": ["Sun in center", "Other planets around", "Use colored cloths"]
            },
            {
                "step_number": 2,
                "title": "Worship Sun (Surya)",
                "description": "Offer red flowers and chant Surya mantra",
                "mantra": "Om Hram Hreem Hroum Sah Suryaya Namaha",
                "duration_seconds": 240,
                "required_items": ["red flowers", "wheat"],
                "tips": ["Face East", "Visualize golden sun"]
            },
            {
                "step_number": 3,
                "title": "Worship Moon (Chandra)",
                "description": "Offer white flowers and chant Chandra mantra",
                "mantra": "Om Shram Shreem Shroum Sah Chandraya Namaha",
                "duration_seconds": 240,
                "required_items": ["white flowers", "rice"],
                "tips": ["Use silver items if possible"]
            },
            {
                "step_number": 4,
                "title": "Worship Mars (Mangal)",
                "description": "Offer red flowers and chant Mangal mantra",
                "mantra": "Om Kram Kreem Kroum Sah Bhaumaya Namaha",
                "duration_seconds": 240,
                "required_items": ["red flowers", "red lentils"],
                "tips": ["Especially important if Mars is afflicted"]
            },
            {
                "step_number": 5,
                "title": "Worship Mercury (Budh)",
                "description": "Offer green flowers and chant Budh mantra",
                "mantra": "Om Bram Breem Broum Sah Budhaya Namaha",
                "duration_seconds": 240,
                "required_items": ["green flowers", "green moong dal"],
                "tips": ["For intelligence and communication"]
            },
            {
                "step_number": 6,
                "title": "Worship Jupiter (Guru)",
                "description": "Offer yellow flowers and chant Guru mantra",
                "mantra": "Om Gram Greem Groum Sah Gurave Namaha",
                "duration_seconds": 240,
                "required_items": ["yellow flowers", "yellow chana dal"],
                "tips": ["For wisdom and prosperity"]
            },
            {
                "step_number": 7,
                "title": "Worship Venus (Shukra)",
                "description": "Offer white flowers and chant Shukra mantra",
                "mantra": "Om Dram Dreem Droum Sah Shukraya Namaha",
                "duration_seconds": 240,
                "required_items": ["white flowers", "white rice"],
                "tips": ["For love and luxury"]
            },
            {
                "step_number": 8,
                "title": "Worship Saturn (Shani)",
                "description": "Offer blue/black flowers and chant Shani mantra",
                "mantra": "Om Pram Preem Proum Sah Shanaye Namaha",
                "duration_seconds": 240,
                "required_items": ["black flowers", "black sesame seeds"],
                "tips": ["Very important for Shani dosha"]
            },
            {
                "step_number": 9,
                "title": "Worship Rahu",
                "description": "Offer dark flowers and chant Rahu mantra",
                "mantra": "Om Bhram Bhreem Bhroum Sah Rahave Namaha",
                "duration_seconds": 240,
                "required_items": ["dark flowers", "urad dal"],
                "tips": ["For protection from eclipse effects"]
            },
            {
                "step_number": 10,
                "title": "Worship Ketu",
                "description": "Offer multi-colored flowers and chant Ketu mantra",
                "mantra": "Om Sram Sreem Sroum Sah Ketave Namaha",
                "duration_seconds": 240,
                "required_items": ["mixed flowers", "horse gram"],
                "tips": ["For spiritual evolution"]
            },
            {
                "step_number": 11,
                "title": "Collective Aarti",
                "description": "Perform aarti for all nine planets together",
                "duration_seconds": 300,
                "tips": ["Maintain equal devotion to all"]
            }
        ]
    },

    # 6. FESTIVAL - Diwali Lakshmi Puja
    {
        "name": "Diwali Lakshmi Puja",
        "category": "festival",
        "deity": "Lakshmi",
        "duration_minutes": 45,
        "difficulty": "intermediate",
        "description": "Grand worship of Goddess Lakshmi on Diwali for wealth and prosperity",
        "required_items": [
            "Lakshmi idol/picture",
            "red cloth",
            "lotus flowers",
            "gold/silver coins",
            "new clothes",
            "sweets",
            "fruits",
            "lamps (21 diyas)",
            "incense",
            "kumkum",
            "turmeric",
            "rice",
            "new account books"
        ],
        "audio_enabled": True,
        "benefits": [
            "Wealth and prosperity",
            "Business success",
            "Financial stability",
            "Family happiness",
            "Abundance"
        ],
        "best_time_of_day": "Evening of Diwali (Amavasya)",
        "steps": [
            {
                "step_number": 1,
                "title": "Clean and Decorate",
                "description": "Thoroughly clean the house and puja area, decorate with rangoli and flowers",
                "duration_seconds": 600,
                "tips": ["Spotless cleanliness", "Beautiful rangoli", "Fresh flowers"]
            },
            {
                "step_number": 2,
                "title": "Light 21 Lamps",
                "description": "Light 21 earthen lamps with ghee and place around the house",
                "duration_seconds": 300,
                "required_items": ["21 diyas", "ghee", "wicks"],
                "tips": ["Use ghee not oil", "Place at main entrance", "In dark corners"]
            },
            {
                "step_number": 3,
                "title": "Invoke Goddess Lakshmi",
                "description": "Invoke the Goddess with Lakshmi Gayatri mantra",
                "mantra": "Om Mahalakshmyai Cha Vidmahe Vishnu Patnyai Cha Dhimahi Tanno Lakshmi Prachodayat",
                "duration_seconds": 180,
                "tips": ["Visualize Goddess on lotus"]
            },
            {
                "step_number": 4,
                "title": "Offer New Clothes and Coins",
                "description": "Offer new clothes, gold/silver coins at the altar",
                "duration_seconds": 180,
                "required_items": ["new clothes", "coins"],
                "tips": ["Symbol of prosperity"]
            },
            {
                "step_number": 5,
                "title": "Chant Lakshmi Ashtakam",
                "description": "Recite the eight verses praising Goddess Lakshmi",
                "duration_seconds": 600,
                "tips": ["Chant with devotion", "Understand the meaning"]
            },
            {
                "step_number": 6,
                "title": "Worship Account Books",
                "description": "Place new account books at the altar for blessing",
                "duration_seconds": 300,
                "required_items": ["new account books"],
                "tips": ["Traditional for traders", "Seek business prosperity"]
            },
            {
                "step_number": 7,
                "title": "Lakshmi Aarti",
                "description": "Perform grand aarti with family members",
                "mantra": "Om Jai Lakshmi Mata",
                "duration_seconds": 420,
                "tips": ["Sing together", "Ring bells", "Distribute prasad"]
            }
        ]
    },

    # 7. REMEDIAL - Mangal Shanti Puja
    {
        "name": "Mangal Shanti Puja (Mars Pacification)",
        "category": "remedial",
        "deity": "Mangal (Mars)",
        "duration_minutes": 45,
        "difficulty": "intermediate",
        "description": "Special puja to reduce Manglik dosha and pacify Mars for marriage and success",
        "required_items": [
            "Hanuman picture/idol",
            "red flowers",
            "red cloth",
            "jaggery",
            "red lentils (masoor dal)",
            "copper vessel",
            "incense",
            "lamp",
            "sweets for Hanuman",
            "sindoor (vermillion)"
        ],
        "audio_enabled": True,
        "benefits": [
            "Reduce Manglik dosha",
            "Marriage obstacles removed",
            "Courage and confidence",
            "Protection from enemies",
            "Physical strength"
        ],
        "best_time_of_day": "Tuesday morning or evening",
        "steps": [
            {
                "step_number": 1,
                "title": "Setup Red Altar",
                "description": "Cover altar with red cloth, place Hanuman idol (Mars deity)",
                "duration_seconds": 120,
                "required_items": ["red cloth", "Hanuman picture"],
                "tips": ["Face South", "Use red decorations"]
            },
            {
                "step_number": 2,
                "title": "Offer Red Items",
                "description": "Offer red flowers, red lentils, and jaggery",
                "duration_seconds": 180,
                "required_items": ["red flowers", "red lentils", "jaggery"],
                "tips": ["Red color pacifies Mars"]
            },
            {
                "step_number": 3,
                "title": "Chant Mars Mantra (108 times)",
                "description": "Chant Mangal beej mantra 108 times using red coral mala",
                "mantra": "Om Kram Kreem Kroum Sah Bhaumaya Namaha",
                "mantra_transliteration": "Om Kraam Kreem Kroum Sah Bhaumaaya Namaha",
                "mantra_translation": "Salutations to Lord Mars",
                "duration_seconds": 1200,
                "required_items": ["red coral mala"],
                "tips": ["Maintain steady pace", "Visualize Mars planet"]
            },
            {
                "step_number": 4,
                "title": "Hanuman Chalisa",
                "description": "Recite Hanuman Chalisa (40 verses)",
                "duration_seconds": 600,
                "tips": ["Hanuman ruled by Mars", "Chant with devotion"]
            },
            {
                "step_number": 5,
                "title": "Offer Sindoor",
                "description": "Apply sindoor (vermillion) to Hanuman's feet and forehead",
                "duration_seconds": 120,
                "required_items": ["sindoor"],
                "tips": ["Hanuman's favorite offering"]
            },
            {
                "step_number": 6,
                "title": "Donate Red Items",
                "description": "Prepare red lentils, jaggery, red cloth for donation",
                "duration_seconds": 180,
                "required_items": ["red lentils", "jaggery", "red cloth"],
                "tips": ["Donate on Tuesday", "Give to needy"]
            },
            {
                "step_number": 7,
                "title": "Closing Aarti",
                "description": "Perform aarti and distribute prasad",
                "duration_seconds": 300,
                "tips": ["Complete on Tuesday", "Repeat for 21/40 Tuesdays"]
            }
        ]
    },

    # 8. MEDITATION - Om Meditation
    {
        "name": "Om Meditation",
        "category": "meditation",
        "deity": "Universal Consciousness",
        "duration_minutes": 15,
        "difficulty": "beginner",
        "description": "Simple yet powerful meditation using the primordial sound Om for peace and spiritual connection",
        "required_items": ["quiet space", "mat or cushion"],
        "audio_enabled": True,
        "benefits": [
            "Deep relaxation",
            "Mental peace",
            "Stress relief",
            "Spiritual awakening",
            "Energy balance"
        ],
        "best_time_of_day": "Early morning or before bed",
        "steps": [
            {
                "step_number": 1,
                "title": "Comfortable Seating",
                "description": "Sit in any comfortable position with straight spine",
                "duration_seconds": 60,
                "required_items": ["mat", "cushion"],
                "tips": ["Lotus, cross-legged, or chair", "Hands in lap or on knees", "Close eyes gently"]
            },
            {
                "step_number": 2,
                "title": "Body Scan Relaxation",
                "description": "Mentally scan body from head to toe, releasing tension",
                "duration_seconds": 180,
                "tips": ["Relax each part", "Notice sensations", "Let go of tension"]
            },
            {
                "step_number": 3,
                "title": "Breath Awareness",
                "description": "Observe natural breath without controlling it",
                "duration_seconds": 120,
                "tips": ["Notice inhale and exhale", "Don't change breath", "Just watch"]
            },
            {
                "step_number": 4,
                "title": "Chant Om (7 times)",
                "description": "Chant Om 7 times, feeling vibrations throughout body",
                "mantra": "Om",
                "mantra_transliteration": "Aum (A-U-M)",
                "mantra_translation": "The primordial sound of universe",
                "duration_seconds": 210,
                "tips": ["A from belly", "U from chest", "M from head", "Feel vibrations"]
            },
            {
                "step_number": 5,
                "title": "Silent Meditation",
                "description": "Sit in silence, mentally repeating Om",
                "duration_seconds": 300,
                "tips": ["Mental repetition", "Stay aware", "Return when mind wanders"]
            },
            {
                "step_number": 6,
                "title": "Gradual Return",
                "description": "Slowly bring awareness back, wiggle fingers and toes",
                "duration_seconds": 30,
                "tips": ["No rush", "Gentle opening", "Feel refreshed"]
            }
        ]
    },

    # 9. DAILY - Evening Aarti
    {
        "name": "Evening Aarti",
        "category": "daily",
        "deity": "Family Deity",
        "duration_minutes": 10,
        "difficulty": "beginner",
        "description": "Simple evening prayer to conclude the day with gratitude and divine blessings",
        "required_items": [
            "idol or picture of deity",
            "lamp (diya)",
            "incense sticks",
            "bell",
            "flowers"
        ],
        "audio_enabled": True,
        "benefits": [
            "Peaceful evening",
            "Family bonding",
            "Gratitude practice",
            "Divine protection",
            "Positive closure of day"
        ],
        "best_time_of_day": "Sunset time",
        "steps": [
            {
                "step_number": 1,
                "title": "Light the Lamp",
                "description": "Light lamp and incense sticks at the altar",
                "duration_seconds": 60,
                "required_items": ["lamp", "incense"],
                "tips": ["Use ghee or oil", "Light as sun sets"]
            },
            {
                "step_number": 2,
                "title": "Ring the Bell",
                "description": "Ring bell to invoke divine presence",
                "duration_seconds": 30,
                "required_items": ["bell"],
                "tips": ["Clear, melodious sound"]
            },
            {
                "step_number": 3,
                "title": "Offer Flowers",
                "description": "Offer fresh flowers to the deity",
                "duration_seconds": 60,
                "required_items": ["flowers"],
                "tips": ["With gratitude", "Fresh flowers preferred"]
            },
            {
                "step_number": 4,
                "title": "Perform Aarti",
                "description": "Circle the lamp before deity in clockwise motion",
                "duration_seconds": 180,
                "required_items": ["lamp"],
                "tips": ["3 or 7 circles", "Sing aarti song", "Ring bell throughout"]
            },
            {
                "step_number": 5,
                "title": "Evening Prayer",
                "description": "Recite short prayer of gratitude for the day",
                "mantra": "Om Shanti Shanti Shanti",
                "mantra_transliteration": "Om Shaanti Shaanti Shaanti",
                "mantra_translation": "Om Peace Peace Peace",
                "duration_seconds": 120,
                "tips": ["Express gratitude", "Seek blessings for night"]
            },
            {
                "step_number": 6,
                "title": "Take Aarti Blessings",
                "description": "Take blessings by passing hands over lamp and touching forehead",
                "duration_seconds": 30,
                "tips": ["Traditional practice", "Feel blessed"]
            }
        ]
    },

    # 10. SPECIAL - Griha Pravesh (Housewarming)
    {
        "name": "Griha Pravesh (Housewarming Puja)",
        "category": "special",
        "deity": "Ganesha and Lakshmi",
        "duration_minutes": 120,
        "difficulty": "advanced",
        "description": "Elaborate ceremony for entering a new home, ensuring prosperity and positive energy",
        "required_items": [
            "Ganesha idol",
            "Lakshmi idol",
            "kalash (water pot)",
            "coconut",
            "mango leaves",
            "turmeric",
            "kumkum",
            "rice",
            "flowers",
            "fruits",
            "sweets",
            "incense",
            "lamps",
            "milk to boil",
            "new broom",
            "salt",
            "camphor"
        ],
        "audio_enabled": True,
        "benefits": [
            "Positive energy in new home",
            "Protection from negative forces",
            "Family prosperity",
            "Happiness and peace",
            "Divine blessings"
        ],
        "best_time_of_day": "Morning on auspicious muhurta",
        "steps": [
            {
                "step_number": 1,
                "title": "Clean and Purify",
                "description": "Thoroughly clean the house, sprinkle holy water",
                "duration_seconds": 600,
                "required_items": ["holy water", "new broom"],
                "tips": ["Every corner", "Remove all dirt", "Open windows"]
            },
            {
                "step_number": 2,
                "title": "Kalash Sthapana",
                "description": "Setup kalash (pot) with water, mango leaves, and coconut at entrance",
                "duration_seconds": 300,
                "required_items": ["kalash", "coconut", "mango leaves", "water"],
                "tips": ["Traditional symbol", "Represents abundance"]
            },
            {
                "step_number": 3,
                "title": "Draw Rangoli and Swastik",
                "description": "Draw colorful rangoli and swastik at entrance",
                "duration_seconds": 600,
                "required_items": ["rangoli colors", "kumkum"],
                "tips": ["Auspicious symbols", "Welcome prosperity"]
            },
            {
                "step_number": 4,
                "title": "Ganesh Puja",
                "description": "Perform complete Ganesh puja for obstacle removal",
                "duration_seconds": 900,
                "required_items": ["Ganesha idol", "flowers", "sweets"],
                "tips": ["First deity to worship", "Essential ritual"]
            },
            {
                "step_number": 5,
                "title": "Lakshmi Puja",
                "description": "Worship Goddess Lakshmi for prosperity",
                "duration_seconds": 900,
                "required_items": ["Lakshmi idol", "lotus flowers", "coins"],
                "tips": ["For wealth and happiness"]
            },
            {
                "step_number": 6,
                "title": "Boil Milk at Entrance",
                "description": "Boil milk at the entrance until it overflows (symbol of abundance)",
                "duration_seconds": 600,
                "required_items": ["milk", "stove"],
                "tips": ["Important tradition", "Let it overflow", "Symbolizes plenty"]
            },
            {
                "step_number": 7,
                "title": "First Entry Ritual",
                "description": "Lady of house enters first with kalash, followed by family",
                "duration_seconds": 300,
                "required_items": ["kalash with rice"],
                "tips": ["Right foot first", "Chant mantras", "Entire family enters"]
            },
            {
                "step_number": 8,
                "title": "Light Lamps in All Rooms",
                "description": "Light lamps in every room of the house",
                "duration_seconds": 600,
                "required_items": ["lamps", "oil"],
                "tips": ["Dispel darkness", "Positive energy", "All corners"]
            },
            {
                "step_number": 9,
                "title": "Vastu Shanti Havan",
                "description": "Perform sacred fire ritual for Vastu (directional) peace",
                "duration_seconds": 1200,
                "required_items": ["havan kund", "ghee", "wood", "herbs"],
                "tips": ["Optional but recommended", "Purifies environment"]
            },
            {
                "step_number": 10,
                "title": "Community Feast",
                "description": "Serve prasad and food to family, friends, and needy",
                "duration_seconds": 1200,
                "required_items": ["food", "sweets"],
                "tips": ["Share joy", "Feed Brahmins", "Bless the poor"]
            }
        ]
    }
]


# ============================================================================
# SEED FUNCTION
# ============================================================================

async def seed_rituals():
    """Seed the database with ritual templates"""
    print("🌱 Starting ritual templates seeding...")

    try:
        supabase = SupabaseClient()
        print(f"✅ Connected to Supabase")

        # Check if rituals already exist
        existing = await supabase.select("ritual_templates", limit=1)
        if existing:
            print(f"⚠️  Found {len(existing)} existing ritual(s)")
            response = input("Do you want to delete existing rituals and re-seed? (yes/no): ")
            if response.lower() == 'yes':
                print("🗑️  Deleting existing rituals...")
                # Note: Supabase REST API doesn't support delete all easily
                # For now, we'll insert new ones (duplicates may occur)
                print("⚠️  Proceeding with insertion (duplicates may occur)")

        # Insert rituals
        inserted_count = 0
        for idx, ritual in enumerate(RITUAL_TEMPLATES, 1):
            try:
                print(f"\n📿 Inserting {idx}/10: {ritual['name']}...")

                result = await supabase.insert("ritual_templates", ritual)

                if result:
                    print(f"   ✅ Inserted: {ritual['name']}")
                    print(f"      Category: {ritual['category']}")
                    print(f"      Deity: {ritual['deity']}")
                    print(f"      Duration: {ritual['duration_minutes']} minutes")
                    print(f"      Difficulty: {ritual['difficulty']}")
                    print(f"      Steps: {len(ritual['steps'])}")
                    inserted_count += 1
                else:
                    print(f"   ❌ Failed to insert: {ritual['name']}")

            except Exception as e:
                print(f"   ❌ Error inserting {ritual['name']}: {str(e)}")
                continue

        print(f"\n✅ Seeding complete! Inserted {inserted_count}/10 rituals")

        # Summary
        all_rituals = await supabase.select("ritual_templates")
        print(f"\n📊 Database now contains {len(all_rituals)} total ritual template(s)")

        # Category breakdown
        categories = {}
        for r in all_rituals:
            cat = r.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1

        print("\n📁 Category Breakdown:")
        for cat, count in categories.items():
            print(f"   {cat}: {count}")

    except Exception as e:
        print(f"❌ Seeding failed: {str(e)}")
        import traceback
        traceback.print_exc()


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    asyncio.run(seed_rituals())
