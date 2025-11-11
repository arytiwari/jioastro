"""
Comprehensive Palmistry Interpretation Service.

Provides detailed palm reading interpretations based on traditional palmistry:
- Major lines (Life, Heart, Head, Fate, Sun, Marriage, Health, Travel, Intuition)
- All mounts (Jupiter, Saturn, Apollo, Mercury, Venus, Mars Upper/Lower, Luna)
- Special markings (Stars, Crosses, Triangles, Islands, Chains, Squares, Grilles)
- Line characteristics (Length, depth, clarity, breaks, branches)
- Hand shape and finger analysis
- Mount prominence and relationships
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime


logger = logging.getLogger(__name__)


class PalmistryInterpretationService:
    """
    Comprehensive palmistry interpretation engine.

    This service generates detailed palm readings by analyzing:
    - All major and minor lines with their characteristics
    - All palm mounts and their prominence levels
    - Special markings and their locations
    - Interactions between different palm features
    - Age timeline predictions based on line positions
    """

    def __init__(self):
        """Initialize the interpretation service with palmistry knowledge base."""
        self._initialize_knowledge_base()

    def _initialize_knowledge_base(self):
        """Initialize comprehensive palmistry knowledge."""

        # Line interpretations based on characteristics
        self.line_interpretations = {
            "life": {
                "description": "Represents vitality, physical health, life force, and major life changes",
                "characteristics": {
                    "long_deep": "Robust health, strong vitality, resilient constitution, long life potential",
                    "short_deep": "Intense but shorter life energy, needs careful health management",
                    "long_thin": "Refined constitution, may be prone to nervous exhaustion",
                    "broken": "Health disruptions, major life changes, need for lifestyle adjustments",
                    "chained": "Periods of health fluctuation, digestive issues, need for stress management",
                    "island": "Health challenges during the period, possible hospitalization or illness",
                    "tasseled_end": "Energy dissipation in later life, need for health vigilance",
                    "forked_end": "Multiple life paths, travel or relocation in later years",
                    "branches_up": "Positive life developments, achievements, upward momentum",
                    "branches_down": "Challenges overcome, lessons learned, strength through adversity",
                    "curved": "Energetic, adventure-seeking personality",
                    "straight": "Cautious, security-oriented approach to life",
                    "wide_curve": "Generous, outgoing, physically active nature",
                    "close_to_thumb": "Reserved, needs personal space, introspective",
                    "crosses": "Critical health events or major life crossroads",
                    "stars": "Sudden events requiring immediate attention",
                    "squares": "Protection during difficult periods, recovery and resilience",
                    "triangles": "Intelligence applied to health matters, healing abilities"
                }
            },

            "heart": {
                "description": "Emotional life, relationships, romantic nature, and heart health",
                "characteristics": {
                    "long_deep": "Deep emotional capacity, passionate, committed in relationships",
                    "short": "Self-sufficient emotionally, practical in relationships",
                    "curved": "Demonstrative affection, expressive love, warm-hearted",
                    "straight": "Mentally oriented in love, values intellectual connection",
                    "ending_under_jupiter": "Idealistic in love, high standards, loyal partner",
                    "ending_under_saturn": "Serious about relationships, may marry for security",
                    "ending_between_jupiter_saturn": "Balanced expectations in love",
                    "broken": "Emotional trauma, relationship endings, heart-healing needed",
                    "chained": "Multiple relationships, emotional complexity, indecisiveness",
                    "island": "Depression, emotional difficulties, relationship strain",
                    "branches_up": "Multiple love interests, flirtatious nature, social butterfly",
                    "branches_down": "Disappointments in love, lessons through relationships",
                    "forked_ending": "Divorce indication, separation from significant relationship",
                    "parallel_lines": "Multiple simultaneous relationships or strong friendships",
                    "crosses": "Emotional crisis points, significant relationship challenges",
                    "stars": "Sudden passionate encounters, heart-related events",
                    "circles": "Heart health concerns, need for cardiac care",
                    "grilles": "Emotional volatility, confused feelings",
                    "dots": "Romantic disappointments or minor heart concerns"
                }
            },

            "head": {
                "description": "Intellect, thinking style, learning ability, and mental approach",
                "characteristics": {
                    "long": "Analytical, detail-oriented, thorough thinker, strategic mind",
                    "short": "Quick thinker, acts on instinct, practical rather than theoretical",
                    "deep": "Excellent concentration, profound thinking, philosophical depth",
                    "faint": "Poor concentration, scattered thinking, needs focus techniques",
                    "straight": "Realistic, practical, logical, left-brain dominant",
                    "curved": "Imaginative, creative, intuitive, right-brain dominant",
                    "steeply_sloped": "Highly creative, artistic, may struggle with practical matters",
                    "slightly_sloped": "Balanced logic and creativity, versatile thinker",
                    "separate_from_life": "Independent thinker, adventurous, risk-taker from youth",
                    "joined_to_life": "Cautious, security-conscious, thoughtful before acting",
                    "long_join_to_life": "Very cautious, dependent on family, late bloomer",
                    "broken": "Mental confusion, major belief system changes, trauma recovery",
                    "chained": "Headaches, mental stress, scattered energy, needs meditation",
                    "island": "Period of mental strain, possible depression or confusion",
                    "forked": "Writer's fork - versatile mind, multiple talents, adaptability",
                    "double_head_line": "Dual nature, multiple careers, exceptional mental capacity",
                    "branches_up": "Academic or career success, mental achievements",
                    "branches_down": "Financial losses due to poor decisions",
                    "crosses": "Major decisions or accidents affecting thinking",
                    "stars": "Brilliant discoveries or head injuries",
                    "squares": "Protection from mental breakdown, healing after trauma",
                    "dots": "Headaches, minor head injuries, temporary confusion"
                }
            },

            "fate": {
                "description": "Career path, life direction, sense of purpose, and destiny",
                "characteristics": {
                    "present_strong": "Clear life direction, strong sense of purpose, career-focused",
                    "absent": "Freedom-loving, creates own path, resists predetermined destiny",
                    "faint": "Uncertain life direction, multiple career changes",
                    "deep": "Strong fate influence, destined achievements, karmic purpose",
                    "starting_life_line": "Family influence on career, traditional path",
                    "starting_luna": "Public career, creative fields, independent success",
                    "starting_wrist": "Early career clarity, childhood ambitions realized",
                    "starting_midpalm": "Late bloomer, career direction found after 35",
                    "ending_jupiter": "Leadership positions, recognition, high achievements",
                    "ending_saturn": "Steady career, teaching or mentoring role",
                    "ending_apollo": "Fame, artistic success, public recognition",
                    "broken": "Career changes, unemployment periods, direction shifts",
                    "multiple_lines": "Multiple career paths, varied interests, portfolio career",
                    "branches_up": "Promotions, career advances, success milestones",
                    "branches_down": "Setbacks overcome, resilience through challenges",
                    "crosses": "Obstacles in career, interference from others",
                    "stars": "Sudden fame or notoriety, dramatic career events",
                    "squares": "Protection during career crises, recovery from failures",
                    "islands": "Career difficulties, reputation challenges"
                }
            },

            "sun": {
                "description": "Success, fame, creativity, artistic talents, and public image",
                "characteristics": {
                    "present_strong": "Artistic talents, success in creative fields, natural charisma",
                    "absent": "Success through hard work rather than luck, practical achievements",
                    "long_deep": "Major success and recognition, fame potential, influential",
                    "short": "Modest success, quiet achievements, behind-the-scenes influence",
                    "starting_life_line": "Self-made success through personal effort",
                    "starting_fate_line": "Success through career, professional recognition",
                    "starting_heart_line": "Success in later life, wisdom brings recognition",
                    "multiple_lines": "Many talents, multiple sources of income and fame",
                    "branches": "Additional success paths, diversified achievements",
                    "ending_strong": "Lasting legacy, remembered after death",
                    "crosses": "Obstacles to success, public challenges",
                    "stars": "Sudden fame, dramatic success, spotlight moments",
                    "islands": "Scandal or reputation damage, success challenges",
                    "squares": "Protection of reputation, recovery from public failures"
                }
            },

            "marriage": {
                "description": "Significant relationships, marriage timing, relationship quality",
                "characteristics": {
                    "multiple_lines": "Multiple significant relationships or possibilities",
                    "one_deep": "One major lifelong relationship, strong marriage",
                    "high_on_mercury": "Late marriage (after 30), mature relationship",
                    "middle_mercury": "Marriage around 25-30, typical timing",
                    "low_on_mercury": "Early marriage (before 25), young love",
                    "long": "Long-lasting relationship, enduring bond",
                    "short": "Brief relationship or relationship not central to life",
                    "broken": "Separation, divorce, or relationship crisis",
                    "forked_start": "Delayed marriage, indecision about commitment",
                    "forked_end": "Divorce, separation, relationship dissolution",
                    "curved_down": "Partner's health issues or relationship decline",
                    "curved_up": "Relationship improves over time, happy partnership",
                    "islands": "Difficulties in marriage, infidelity, or separation",
                    "crosses": "Obstacles to marriage, relationship conflicts",
                    "parallel_lines": "Affairs or multiple relationships simultaneously"
                }
            },

            "health": {
                "description": "Health constitution, digestive system, overall wellness",
                "characteristics": {
                    "absent": "Strong constitution, no major health concerns",
                    "present": "Need for health awareness, digestive sensitivity",
                    "broken": "Health problems, digestive issues, need for medical attention",
                    "islands": "Specific health crises, hospitalization periods",
                    "crosses": "Operations, injuries, medical interventions",
                    "dots": "Temporary illness, minor health issues",
                    "squares": "Protection during illness, successful medical treatment"
                }
            },

            "travel": {
                "description": "Travel opportunities, relocations, foreign connections",
                "characteristics": {
                    "present": "Strong travel opportunities, life abroad, global connections",
                    "multiple_lines": "Frequent traveler, many relocations, nomadic tendencies",
                    "long": "Long-distance moves, permanent relocations, emigration",
                    "short": "Short trips, tourism, temporary stays abroad",
                    "crossing_life_line": "Travel changes life direction significantly"
                }
            },

            "intuition": {
                "description": "Psychic abilities, intuitive powers, spiritual sensitivity",
                "characteristics": {
                    "present": "Strong intuition, psychic sensitivity, spiritual awareness",
                    "deep": "Powerful intuitive gifts, mediumship potential, prophetic dreams",
                    "connecting_luna_mercury": "Communication of intuitive insights, teaching gifts"
                }
            }
        }

        # Mount interpretations based on prominence
        self.mount_interpretations = {
            "Jupiter": {
                "location": "Base of index finger",
                "rules": "Leadership, ambition, confidence, authority, pride, honor",
                "prominent": {
                    "positive": "Natural leader, ambitious, confident, honorable, successful, respected, authoritative, dignified, religious, just, generous",
                    "negative": "Overbearing, domineering, arrogant, prideful, dictatorial, self-important, excessive ambition",
                    "career": "Leadership roles, politics, law, religion, teaching, management, entrepreneurship",
                    "personality": "Commanding presence, inspirational, motivational, protective, seeks recognition"
                },
                "moderate": "Balanced ambition, healthy self-esteem, reasonable confidence, good leadership when needed",
                "flat": "Lacks ambition, low self-esteem, avoids leadership, follower mentality, needs encouragement, passive",
                "zodiac": "Connected to Sagittarius energy",
                "finger": "Index finger strength amplifies Jupiter qualities"
            },

            "Saturn": {
                "location": "Base of middle finger",
                "rules": "Discipline, responsibility, wisdom, solitude, seriousness, patience",
                "prominent": {
                    "positive": "Serious, responsible, disciplined, patient, wise, prudent, organized, studious, philosophical, solitary by choice",
                    "negative": "Pessimistic, gloomy, melancholic, isolated, overly serious, cynical, depressive tendencies, misanthropic",
                    "career": "Research, science, mathematics, philosophy, archaeology, history, farming, mining, solitary work",
                    "personality": "Introspective, cautious, conservative, traditional, methodical, prefers solitude"
                },
                "moderate": "Balanced seriousness, healthy caution, appropriate responsibility, wisdom with joy",
                "flat": "Lacks discipline, irresponsible, frivolous, avoids commitment, immature, unreliable, scattered",
                "zodiac": "Connected to Capricorn and Aquarius energy",
                "finger": "Middle finger length indicates Saturn's influence strength"
            },

            "Apollo": {
                "location": "Base of ring finger (also called Mount of Sun)",
                "rules": "Creativity, arts, fame, success, happiness, optimism, charisma",
                "prominent": {
                    "positive": "Artistic, creative, successful, charismatic, optimistic, joyful, talented, famous, versatile, appreciates beauty",
                    "negative": "Vain, extravagant, pretentious, superficial, wasteful, attention-seeking, gambling tendencies",
                    "career": "Arts, entertainment, design, fashion, jewelry, luxury goods, public relations, advertising, performance",
                    "personality": "Charming, warm, generous, loves beauty, seeks pleasure, socially magnetic"
                },
                "moderate": "Appreciation for arts, balanced creativity, moderate success drive, healthy self-expression",
                "flat": "Lacks artistic sense, dull life, no appreciation for beauty, struggles with self-expression, melancholic",
                "zodiac": "Connected to Leo energy and Sun qualities",
                "finger": "Ring finger length shows creative expression level"
            },

            "Mercury": {
                "location": "Base of little finger",
                "rules": "Communication, business, intellect, wit, science, medicine, commerce",
                "prominent": {
                    "positive": "Excellent communicator, business-minded, witty, clever, scientific, medical aptitude, quick learner, persuasive",
                    "negative": "Deceptive, manipulative, dishonest, scheming, unscrupulous in business, sharp-tongued, cunning",
                    "career": "Business, sales, marketing, medicine, science, teaching, writing, communication, commerce, technology",
                    "personality": "Talkative, sociable, mentally agile, entrepreneurial, adaptable, curious"
                },
                "moderate": "Good communication skills, honest business dealings, balanced intellect, appropriate wit",
                "flat": "Poor communication, lacks business sense, naive, gullible, struggles with expression, limited commercial success",
                "zodiac": "Connected to Gemini and Virgo energy",
                "finger": "Little finger length determines communication effectiveness"
            },

            "Venus": {
                "location": "Base of thumb, forms the ball of the thumb",
                "rules": "Love, passion, sensuality, vitality, family, beauty, harmony",
                "prominent": {
                    "positive": "Passionate, loving, affectionate, vital, energetic, appreciates beauty, family-oriented, warm, sensual, musical",
                    "negative": "Lustful, excessive passions, jealous, possessive, temperamental, self-indulgent, hedonistic",
                    "career": "Music, dance, relationships, counseling, hospitality, beauty industry, food/culinary arts",
                    "personality": "Warm, affectionate, emotional, physically demonstrative, loves pleasure and comfort"
                },
                "moderate": "Balanced affections, healthy sensuality, appropriate family bonds, love of beauty without excess",
                "flat": "Cold, unaffectionate, low vitality, indifferent to beauty, weak family bonds, passionless, physically weak",
                "zodiac": "Connected to Taurus and Libra energy",
                "girdle": "Girdle of Venus (line across top of palm) intensifies Venus qualities"
            },

            "Mars_Upper": {
                "location": "Between thumb and Jupiter mount, inside life line",
                "rules": "Physical courage, aggression, resistance, self-defense",
                "prominent": {
                    "positive": "Courageous, brave, warrior spirit, protective, assertive, stands up for self and others, athletic",
                    "negative": "Aggressive, violent, quarrelsome, hot-tempered, bully, cruel, brutal, reckless",
                    "career": "Military, police, sports, security, firefighting, emergency services, martial arts, surgery",
                    "personality": "Bold, confrontational, competitive, physically strong, quick to anger"
                },
                "moderate": "Appropriate assertiveness, healthy competitive spirit, courage when needed",
                "flat": "Cowardly, passive, avoids confrontation, physically weak, submissive, lacks fighting spirit"
            },

            "Mars_Lower": {
                "location": "Opposite Upper Mars, between heart and head lines",
                "rules": "Moral courage, mental resistance, perseverance, self-control",
                "prominent": {
                    "positive": "Mentally strong, perseverant, determined, self-controlled, enduring, cool under pressure",
                    "negative": "Stubborn, inflexible, repressed anger, passive-aggressive, sullen",
                    "career": "Long-term projects requiring persistence, endurance sports, therapy, counseling",
                    "personality": "Patient, enduring, mentally tough, self-disciplined, doesn't give up easily"
                },
                "moderate": "Balanced persistence, appropriate self-control, healthy determination",
                "flat": "Gives up easily, weak-willed, lacks perseverance, poor self-control, defeated easily"
            },

            "Luna": {
                "location": "Opposite Venus mount, outer palm below little finger",
                "rules": "Imagination, intuition, creativity, subconscious, dreams, mysticism",
                "prominent": {
                    "positive": "Highly imaginative, creative, intuitive, psychic, dreamy, mystical, poetic, romantic, loves travel",
                    "negative": "Over-imaginative, unrealistic, delusional, escapist, moody, unstable, anxiety, depression, fears",
                    "career": "Creative arts, writing, poetry, psychology, mysticism, sailing, travel industry, fantasy/sci-fi",
                    "personality": "Dreamy, imaginative, sensitive, intuitive, loves water and travel, introspective"
                },
                "moderate": "Healthy imagination, balanced intuition, creative without losing touch with reality",
                "flat": "Unimaginative, prosaic, lacks intuition, no creative flair, materialistic, insensitive",
                "zodiac": "Connected to Moon, Cancer, and Pisces energy"
            },

            "Mars_Plain": {
                "location": "Center of palm (hollow in middle)",
                "rules": "Energy distribution, balance, grounding",
                "description": "The Plain of Mars should be slightly hollow. If too deep, it indicates lack of energy and enthusiasm. If too raised, it shows aggressive, quarrelsome nature."
            }
        }

        # Special markings and their meanings
        self.special_markings = {
            "star": {
                "general": "Sudden, dramatic event - positive or negative depending on location",
                "on_jupiter": "Great achievement, honor, position of authority, sudden success",
                "on_saturn": "Danger, accident, tragedy, fate-changing event (often negative)",
                "on_apollo": "Sudden fame, brilliant success, recognition, winning",
                "on_mercury": "Business success, scientific discovery, communication breakthrough",
                "on_venus": "Great love, passionate affair, exceptional romance",
                "on_luna": "Psychic experience, imagination realized, creative breakthrough or delusion",
                "on_life_line": "Life-threatening event, serious accident or illness",
                "on_heart_line": "Heart attack warning, emotional crisis, passionate encounter",
                "on_head_line": "Mental brilliance or head injury, stroke warning",
                "on_fate_line": "Sudden career change, fame or notoriety"
            },

            "cross": {
                "general": "Obstacles, crossroads, critical decisions, challenges",
                "on_jupiter": "Happy marriage, successful union, good partnership",
                "on_saturn": "Mysticism, interest in occult, fateful events (can be negative)",
                "on_apollo": "Disappointment in ambitions, blocked creativity, failed projects",
                "on_mercury": "Dishonesty in business, deception, tendency to lie",
                "on_venus": "One great love, all-consuming passion (can cause problems)",
                "on_luna": "Superstition, unfounded fears, overactive imagination",
                "between_heart_head": "Mystical cross - spiritual gifts, healing abilities",
                "on_life_line": "Critical health event, accident, major life change",
                "on_heart_line": "Emotional crisis, relationship difficulties",
                "on_head_line": "Injury to head, difficult decision, mental crisis"
            },

            "triangle": {
                "general": "Talent, intelligence, success through mental ability",
                "on_jupiter": "Diplomatic skills, success in politics or foreign affairs",
                "on_saturn": "Mystical knowledge, occult wisdom, deep study",
                "on_apollo": "Artistic genius, scientific creativity, brilliant success",
                "on_mercury": "Business acumen, medical skill, diplomatic ability",
                "on_venus": "Calculating in love, logical approach to relationships",
                "on_luna": "Psychic ability controlled by reason, mystical wisdom",
                "on_life_line": "Intelligence applied to health, self-healing ability",
                "on_head_line": "Brilliant mind, exceptional intelligence, strategic thinking",
                "on_fate_line": "Success through intelligence and planning"
            },

            "square": {
                "general": "Protection, preservation, healing, containment of damage",
                "on_any_mount": "Protection of mount qualities from excess or damage",
                "on_life_line": "Protection during illness, recovery from health crisis, medical help",
                "on_heart_line": "Protection from emotional trauma, healing of heartbreak",
                "on_head_line": "Protection from mental breakdown, recovery from head injury",
                "on_fate_line": "Protection of career, recovery from professional failures",
                "teacher_square": "Square on Jupiter - teaching ability, educational success"
            },

            "island": {
                "general": "Weakness, division of energy, problematic period",
                "on_life_line": "Illness, hospitalization, loss of vitality during period",
                "on_heart_line": "Depression, emotional crisis, relationship problems",
                "on_head_line": "Mental confusion, poor concentration, psychological issues",
                "on_fate_line": "Career difficulties, loss of direction, reputation damage",
                "on_sun_line": "Loss of reputation, scandal, diminished success"
            },

            "chain": {
                "general": "Complications, fluctuations, uncertainty, weakness",
                "on_life_line": "Health fluctuations, various illnesses, weak constitution",
                "on_heart_line": "Emotional instability, multiple relationships, heart problems",
                "on_head_line": "Mental instability, difficulty concentrating, nervousness",
                "on_fate_line": "Career uncertainties, changes in direction, no clear path"
            },

            "grille": {
                "general": "Blocked energy, frustration, confusion, obstacles",
                "on_jupiter": "Excessive pride, arrogance, dictatorial tendencies",
                "on_saturn": "Pessimism, depression, misery, gloom",
                "on_apollo": "Vanity, pretension, unsuccessful attempts at fame",
                "on_mercury": "Dishonesty, theft, business failures",
                "on_venus": "Excessive passion, jealousy, relationship problems",
                "on_luna": "Fears, anxieties, nightmares, mental instability"
            },

            "circle": {
                "general": "Rare marking, usually negative, disease or crisis",
                "on_life_line": "Serious health crisis, often involving eyes or head",
                "on_apollo": "Fame that becomes burdensome, public attention problems",
                "on_jupiter": "Injury or disease affecting head or eyes"
            },

            "trident": {
                "general": "Very fortunate, success, wealth, good fortune",
                "on_fate_line": "Multiple income sources, diversified success",
                "on_apollo": "Multiple talents bringing success, fame and fortune",
                "on_jupiter": "Leadership in multiple areas, varied achievements"
            },

            "spot": {
                "general": "Temporary obstacle, minor health issue, brief setback",
                "color_matters": "Red dots more serious than white/pale dots",
                "on_life_line": "Temporary illness or minor accident",
                "on_heart_line": "Brief romantic disappointment or minor heart concern",
                "on_head_line": "Temporary mental stress or minor head problem"
            }
        }

        # Hand shape interpretations (elemental types)
        self.hand_shapes = {
            "earth": {
                "description": "Square palm, short fingers",
                "element": "Earth",
                "personality": "Practical, reliable, grounded, hardworking, loyal, patient, stubborn, materialistic, physical",
                "strengths": "Dependable, strong, enduring, honest, down-to-earth, good with hands, practical skills",
                "weaknesses": "Inflexible, resistant to change, unimaginative, overly cautious, materialistic, closed-minded",
                "career": "Construction, farming, mechanics, crafts, physical labor, traditional professions, banking",
                "love": "Loyal, committed, sensual, needs physical affection, slow to commit but devoted",
                "money": "Conservative with finances, saves for security, prefers tangible assets"
            },

            "air": {
                "description": "Square palm, long fingers",
                "element": "Air",
                "personality": "Intellectual, analytical, communicative, social, curious, logical, restless, detached",
                "strengths": "Intelligent, articulate, objective, adaptable, good communicator, quick learner",
                "weaknesses": "Overthinking, emotionally detached, superficial, scattered, commitment-phobic",
                "career": "Teaching, writing, journalism, law, psychology, technology, sales, communications",
                "love": "Needs mental stimulation, values conversation, may intellectualize emotions",
                "money": "Makes money through ideas and communication, may be impractical with finances"
            },

            "fire": {
                "description": "Rectangular palm, short fingers",
                "element": "Fire",
                "personality": "Energetic, passionate, spontaneous, confident, ambitious, impulsive, adventurous, charismatic",
                "strengths": "Natural leaders, motivating, enthusiastic, courageous, entrepreneurial, action-oriented",
                "weaknesses": "Impatient, aggressive, dominating, reckless, insensitive, hot-tempered",
                "career": "Entrepreneurship, sales, marketing, entertainment, sports, emergency services, military",
                "love": "Passionate, romantic, needs excitement, can be jealous, physically expressive",
                "money": "Risk-taker, entrepreneurial ventures, may be reckless with spending"
            },

            "water": {
                "description": "Rectangular palm, long fingers",
                "element": "Water",
                "personality": "Emotional, intuitive, sensitive, artistic, empathetic, imaginative, moody, secretive",
                "strengths": "Compassionate, creative, intuitive, understanding, artistic, spiritually aware",
                "weaknesses": "Overly emotional, moody, thin-skinned, easily hurt, escapist, manipulative",
                "career": "Arts, music, counseling, nursing, social work, mysticism, healing, therapy",
                "love": "Deeply emotional, romantic, needs emotional security, highly sensitive to partner's moods",
                "money": "Impractical with finances, may be taken advantage of, generous to excess"
            }
        }

        # Age timeline for major lines (approximate ages along the line)
        self.age_timelines = {
            "life": {
                "method": "From where life line starts (between thumb and Jupiter) downward to wrist",
                "ages": {
                    "start": 0,
                    "first_third": "0-25 years - Youth and formation",
                    "middle_third": "25-50 years - Prime of life, career building",
                    "final_third": "50-75+ years - Later life, wisdom period",
                    "near_wrist": "75+ years - Advanced age, life reflection"
                },
                "reading_method": "Divide the line into equal parts or measure from start point downward"
            },

            "fate": {
                "method": "From wrist upward toward fingers",
                "ages": {
                    "wrist": "Birth to age 20",
                    "head_line_cross": "Around age 35",
                    "heart_line_cross": "Around age 50",
                    "near_saturn": "Age 60+"
                }
            },

            "marriage": {
                "method": "Lines on Mercury mount side - count from heart line upward",
                "ages": {
                    "near_heart_line": "Ages 18-25 - Early relationships",
                    "middle": "Ages 25-35 - Prime marriage years",
                    "upper": "Ages 35+ - Later relationships"
                }
            }
        }

    def generate_comprehensive_interpretation(
        self,
        hand_type: str,
        hand_shape: str,
        lines: List[Dict],
        mounts: List[Dict],
        markings: Optional[List[Dict]] = None,
        holistic_data: Optional[Dict] = None
    ) -> Dict:
        """
        Generate comprehensive palm reading interpretation.

        Args:
            hand_type: "left" or "right"
            hand_shape: "earth", "air", "fire", or "water"
            lines: List of detected lines with characteristics
            mounts: List of detected mounts with prominence levels
            markings: Optional list of special markings detected
            holistic_data: Optional birth chart and numerology data

        Returns:
            Dictionary with comprehensive interpretation including:
            - Overall summary
            - Detailed line-by-line analysis
            - Mount analysis
            - Special markings interpretation
            - Personality synthesis
            - Life predictions and timing
            - Career and relationship guidance
            - Health insights
            - Recommendations
        """
        try:
            logger.info(f"Generating comprehensive palmistry interpretation for {hand_type} {hand_shape} hand")

            # Build comprehensive interpretation
            interpretation = {
                "summary": self._generate_summary(hand_type, hand_shape, lines, mounts, holistic_data),
                "hand_shape_analysis": self._analyze_hand_shape(hand_shape),
                "line_analysis": self._analyze_all_lines(lines),
                "mount_analysis": self._analyze_all_mounts(mounts),
                "special_markings_analysis": self._analyze_special_markings(markings) if markings else [],
                "personality_synthesis": self._synthesize_personality(hand_shape, lines, mounts),
                "life_predictions": self._generate_life_predictions(lines, mounts),
                "career_guidance": self._generate_career_guidance(hand_shape, lines, mounts),
                "relationship_insights": self._generate_relationship_insights(lines, mounts),
                "health_insights": self._generate_health_insights(lines, mounts),
                "timing_analysis": self._analyze_timing(lines),
                "recommendations": self._generate_recommendations(hand_shape, lines, mounts),
                "detailed_analysis": ""  # Will be formatted text version
            }

            # Add holistic correlations if available
            if holistic_data:
                interpretation["astrology_correlations"] = self._correlate_with_astrology(
                    hand_shape, lines, mounts, holistic_data.get("chart")
                )
                interpretation["numerology_correlations"] = self._correlate_with_numerology(
                    hand_shape, lines, mounts, holistic_data.get("numerology")
                )

            # Generate formatted detailed analysis text
            interpretation["detailed_analysis"] = self._format_detailed_analysis(interpretation)

            logger.info("Comprehensive palmistry interpretation generated successfully")
            return interpretation

        except Exception as e:
            logger.error(f"Error generating comprehensive interpretation: {str(e)}")
            raise

    def _generate_summary(
        self,
        hand_type: str,
        hand_shape: str,
        lines: List[Dict],
        mounts: List[Dict],
        holistic_data: Optional[Dict]
    ) -> str:
        """Generate overall summary of the palm reading."""
        name_prefix = ""
        if holistic_data and holistic_data.get("profile"):
            name = holistic_data["profile"].get("name", "")
            if name:
                name_prefix = f"{name}, your "
            else:
                name_prefix = "Your "
        else:
            name_prefix = "Your "

        hand_shape_meaning = self.hand_shapes[hand_shape]["personality"].split(",")[0]

        # Count major positive and challenging features
        strong_features = []
        if any(m.get("prominence") in ["prominent", "very_prominent"] for m in mounts):
            strong_features.append("strong mount development")
        if any(l.get("characteristics", {}).get("depth") == "deep" for l in lines):
            strong_features.append("deep major lines")

        summary = f"{name_prefix}{hand_type} hand reveals a {hand_shape} type personality, indicating a {hand_shape_meaning} nature. "

        if strong_features:
            summary += f"Notable features include {' and '.join(strong_features)}, "

        summary += f"suggesting a life path marked by {self._get_life_theme(hand_shape, lines, mounts)}. "

        # Add holistic integration note if available
        if holistic_data:
            summary += "This palm reading harmonizes with your astrological chart and numerological profile for a complete picture of your life path."

        return summary

    def _analyze_hand_shape(self, hand_shape: str) -> Dict:
        """Analyze hand shape in detail."""
        shape_data = self.hand_shapes.get(hand_shape, self.hand_shapes["earth"])

        return {
            "shape_type": hand_shape.title(),
            "element": shape_data["element"],
            "description": shape_data["description"],
            "personality_traits": shape_data["personality"],
            "strengths": shape_data["strengths"],
            "weaknesses": shape_data["weaknesses"],
            "career_aptitudes": shape_data["career"],
            "love_style": shape_data["love"],
            "money_approach": shape_data["money"]
        }

    def _analyze_all_lines(self, lines: List[Dict]) -> Dict:
        """Analyze all detected palm lines in detail."""
        line_analyses = {}

        for line_data in lines:
            line_type = line_data.get("line_type", "").lower()
            if line_type not in self.line_interpretations:
                continue

            line_info = self.line_interpretations[line_type]
            characteristics = line_data.get("characteristics", {})

            # Build detailed analysis for this line
            analysis = {
                "line_name": line_type.title() + " Line",
                "description": line_info["description"],
                "detected_characteristics": [],
                "interpretation": [],
                "confidence": line_data.get("confidence", 0.0)
            }

            # Analyze each characteristic
            for char_key, char_value in characteristics.items():
                char_desc = f"{char_key}: {char_value}"
                analysis["detected_characteristics"].append(char_desc)

                # Look up interpretation
                lookup_key = f"{char_key}_{char_value}".replace(" ", "_").replace("-", "_")
                if lookup_key in line_info["characteristics"]:
                    analysis["interpretation"].append(line_info["characteristics"][lookup_key])
                elif char_key in line_info["characteristics"]:
                    analysis["interpretation"].append(line_info["characteristics"][char_key])

            # Add general characteristics interpretations
            for char_type in ["length", "depth", "clarity"]:
                if char_type in characteristics:
                    value = characteristics[char_type]
                    key = f"{value}_{char_type}" if value else char_type
                    if key in line_info["characteristics"]:
                        if line_info["characteristics"][key] not in analysis["interpretation"]:
                            analysis["interpretation"].append(line_info["characteristics"][key])

            line_analyses[line_type] = analysis

        return line_analyses

    def _analyze_all_mounts(self, mounts: List[Dict]) -> Dict:
        """Analyze all palm mounts in detail."""
        mount_analyses = {}

        for mount_data in mounts:
            mount_name = mount_data.get("mount_name", "")
            if mount_name not in self.mount_interpretations:
                continue

            mount_info = self.mount_interpretations[mount_name]
            prominence = mount_data.get("prominence", "moderate")

            analysis = {
                "mount_name": mount_name,
                "location": mount_info["location"],
                "rules": mount_info["rules"],
                "prominence_level": prominence,
                "confidence": mount_data.get("confidence", 0.0),
                "interpretation": ""
            }

            # Get interpretation based on prominence
            if prominence in ["prominent", "very_prominent"]:
                prom_data = mount_info.get("prominent", {})
                analysis["interpretation"] = prom_data.get("positive", "Significant influence")
                analysis["negative_potential"] = prom_data.get("negative", "")
                analysis["career_implications"] = prom_data.get("career", "")
                analysis["personality_impact"] = prom_data.get("personality", "")
            elif prominence == "moderate":
                analysis["interpretation"] = mount_info.get("moderate", "Balanced influence")
            elif prominence in ["flat", "absent"]:
                analysis["interpretation"] = mount_info.get("flat", "Minimal influence")

            if "zodiac" in mount_info:
                analysis["zodiac_connection"] = mount_info["zodiac"]

            mount_analyses[mount_name] = analysis

        return mount_analyses

    def _analyze_special_markings(self, markings: List[Dict]) -> List[Dict]:
        """Analyze special markings on the palm."""
        if not markings:
            return []

        marking_analyses = []

        for marking in markings:
            marking_type = marking.get("type", "").lower()
            location = marking.get("location", "")

            if marking_type not in self.special_markings:
                continue

            marking_info = self.special_markings[marking_type]

            analysis = {
                "marking_type": marking_type.title(),
                "location": location,
                "general_meaning": marking_info.get("general", ""),
                "specific_interpretation": "",
                "significance": marking.get("significance", "moderate")
            }

            # Get location-specific interpretation
            location_key = f"on_{location.lower().replace(' ', '_')}"
            if location_key in marking_info:
                analysis["specific_interpretation"] = marking_info[location_key]
            else:
                analysis["specific_interpretation"] = marking_info["general"]

            marking_analyses.append(analysis)

        return marking_analyses

    def _synthesize_personality(
        self,
        hand_shape: str,
        lines: List[Dict],
        mounts: List[Dict]
    ) -> Dict:
        """Synthesize overall personality from all palm features."""
        personality_traits = []

        # Add hand shape traits
        shape_traits = self.hand_shapes[hand_shape]["personality"].split(", ")
        personality_traits.extend(shape_traits[:3])  # Top 3 traits

        # Add dominant mount traits
        prominent_mounts = [m for m in mounts if m.get("prominence") in ["prominent", "very_prominent"]]
        for mount in prominent_mounts[:2]:  # Top 2 prominent mounts
            mount_name = mount.get("mount_name")
            if mount_name in self.mount_interpretations:
                mount_info = self.mount_interpretations[mount_name]
                if "prominent" in mount_info:
                    personality = mount_info["prominent"].get("personality", "")
                    if personality:
                        traits = personality.split(", ")
                        personality_traits.append(traits[0] if traits else personality)

        return {
            "core_traits": personality_traits,
            "overall_temperament": self._determine_temperament(hand_shape, mounts),
            "motivations": self._determine_motivations(mounts),
            "interpersonal_style": self._determine_interpersonal_style(hand_shape, lines),
            "decision_making_style": self._determine_decision_style(lines)
        }

    def _generate_life_predictions(self, lines: List[Dict], mounts: List[Dict]) -> List[Dict]:
        """Generate life predictions based on lines and mounts."""
        predictions = []

        # Analyze fate line for career predictions
        fate_line = next((l for l in lines if l.get("line_type") == "fate"), None)
        if fate_line:
            predictions.append({
                "area": "Career & Life Purpose",
                "prediction": "Significant career developments and sense of purpose throughout life",
                "timing": "Career milestones at ages 28-32, 40-45, and 55-60",
                "confidence": fate_line.get("confidence", 0.7)
            })

        # Analyze sun line for success predictions
        sun_line = next((l for l in lines if l.get("line_type") == "sun"), None)
        if sun_line:
            predictions.append({
                "area": "Success & Recognition",
                "prediction": "Achievement and recognition in creative or professional pursuits",
                "timing": "Peak success periods ages 35-45 and 55-65",
                "confidence": sun_line.get("confidence", 0.7)
            })

        # Analyze heart line for relationship predictions
        heart_line = next((l for l in lines if l.get("line_type") == "heart"), None)
        if heart_line:
            char = heart_line.get("characteristics", {})
            if char.get("length") == "long":
                predictions.append({
                    "area": "Relationships & Love",
                    "prediction": "Capacity for deep, lasting relationships with strong emotional bonds",
                    "timing": "Significant relationships forming throughout life, particularly ages 25-30 and 40-50",
                    "confidence": heart_line.get("confidence", 0.7)
                })

        # Analyze life line for health and vitality
        life_line = next((l for l in lines if l.get("line_type") == "life"), None)
        if life_line:
            char = life_line.get("characteristics", {})
            if char.get("depth") == "deep":
                predictions.append({
                    "area": "Health & Vitality",
                    "prediction": "Strong constitution with good recovery ability and general vitality",
                    "timing": "Maintain health through preventive care; key health focus ages 45-55 and 65+",
                    "confidence": life_line.get("confidence", 0.8)
                })

        return predictions

    def _generate_career_guidance(
        self,
        hand_shape: str,
        lines: List[Dict],
        mounts: List[Dict]
    ) -> Dict:
        """Generate career guidance based on palm features."""
        shape_careers = self.hand_shapes[hand_shape]["career"]

        # Identify dominant mounts for career influence
        prominent_mounts = [m for m in mounts if m.get("prominence") in ["prominent", "very_prominent"]]
        mount_careers = []
        for mount in prominent_mounts:
            mount_name = mount.get("mount_name")
            if mount_name in self.mount_interpretations:
                mount_info = self.mount_interpretations[mount_name]
                if "prominent" in mount_info:
                    career = mount_info["prominent"].get("career", "")
                    if career:
                        mount_careers.append(career)

        return {
            "primary_aptitudes": shape_careers,
            "mount_influences": mount_careers[:2] if mount_careers else ["General skills applicable across fields"],
            "success_indicators": self._identify_success_indicators(lines, mounts),
            "challenges_to_overcome": self._identify_career_challenges(lines, mounts),
            "timing_for_changes": "Best periods for career changes: Ages 28-32, 35-40, 50-55"
        }

    def _generate_relationship_insights(self, lines: List[Dict], mounts: List[Dict]) -> Dict:
        """Generate relationship insights from heart line and Venus mount."""
        heart_line = next((l for l in lines if l.get("line_type") == "heart"), None)
        venus_mount = next((m for m in mounts if m.get("mount_name") == "Venus"), None)

        relationship_style = "Emotionally engaged"
        capacity_for_love = "Strong capacity for deep emotional bonds"
        marriage_timing = "Significant relationships likely ages 25-35"

        if heart_line:
            char = heart_line.get("characteristics", {})
            if char.get("length") == "long":
                relationship_style = "Deeply emotional, expressive, passionate in love"
            elif char.get("length") == "short":
                relationship_style = "Independent, self-sufficient emotionally"

            if char.get("curve") == "moderate":
                capacity_for_love = "Balanced emotional expression with warmth and practicality"

        if venus_mount:
            if venus_mount.get("prominence") in ["prominent", "very_prominent"]:
                capacity_for_love += ". Strong passion and affectionate nature"

        return {
            "relationship_style": relationship_style,
            "capacity_for_love": capacity_for_love,
            "marriage_indications": marriage_timing,
            "emotional_nature": self._determine_emotional_nature(heart_line, venus_mount),
            "compatibility_factors": "Most compatible with partners who appreciate your emotional style"
        }

    def _generate_health_insights(self, lines: List[Dict], mounts: List[Dict]) -> Dict:
        """Generate health insights from life line and other indicators."""
        life_line = next((l for l in lines if l.get("line_type") == "life"), None)
        health_line = next((l for l in lines if l.get("line_type") == "health"), None)

        vitality_level = "Good general vitality"
        health_areas_attention = []

        if life_line:
            char = life_line.get("characteristics", {})
            if char.get("depth") == "deep":
                vitality_level = "Strong vitality, robust constitution, good recovery ability"
            elif char.get("depth") == "faint":
                vitality_level = "Moderate vitality, needs attention to energy management"

            if "broken" in char:
                health_areas_attention.append("Pay attention during life transitions - vulnerable periods")
            if "island" in char:
                health_areas_attention.append("Specific health challenges during middle life - preventive care important")

        if health_line:
            health_areas_attention.append("Digestive system needs attention - maintain healthy diet")

        if not health_areas_attention:
            health_areas_attention.append("General wellness focus on prevention and healthy lifestyle")

        return {
            "vitality_assessment": vitality_level,
            "areas_needing_attention": health_areas_attention,
            "preventive_recommendations": [
                "Regular health checkups, especially after age 40",
                "Stress management and adequate rest",
                "Balanced diet and appropriate exercise for your constitution",
                "Listen to your body's signals and address concerns early"
            ],
            "recovery_ability": "Good" if life_line and life_line.get("characteristics", {}).get("depth") == "deep" else "Moderate"
        }

    def _analyze_timing(self, lines: List[Dict]) -> Dict:
        """Analyze timing of major life events using age timelines."""
        timing_predictions = {}

        # Life line timing
        life_line = next((l for l in lines if l.get("line_type") == "life"), None)
        if life_line:
            timing_predictions["life_timeline"] = {
                "method": self.age_timelines["life"]["method"],
                "periods": self.age_timelines["life"]["ages"],
                "predictions": "Major life events and health developments tracked along life line from start to end"
            }

        # Fate line timing
        fate_line = next((l for l in lines if l.get("line_type") == "fate"), None)
        if fate_line:
            timing_predictions["career_timeline"] = {
                "method": self.age_timelines["fate"]["method"],
                "ages": self.age_timelines["fate"]["ages"],
                "predictions": "Career developments and life direction changes visible at various points"
            }

        # Marriage line timing
        marriage_line = next((l for l in lines if l.get("line_type") == "marriage"), None)
        if marriage_line:
            timing_predictions["relationship_timeline"] = {
                "method": self.age_timelines["marriage"]["method"],
                "ages": self.age_timelines["marriage"]["ages"],
                "predictions": "Significant relationship timing indicated by position on mount of Mercury"
            }

        return timing_predictions

    def _generate_recommendations(
        self,
        hand_shape: str,
        lines: List[Dict],
        mounts: List[Dict]
    ) -> List[str]:
        """Generate personalized recommendations based on palm features."""
        recommendations = []

        # Hand shape based recommendations
        if hand_shape == "earth":
            recommendations.append("Embrace change gradually - your stable nature is a strength, but flexibility will enhance your growth")
        elif hand_shape == "air":
            recommendations.append("Ground your ideas in practical action - your intellectual gifts need physical manifestation")
        elif hand_shape == "fire":
            recommendations.append("Channel your abundant energy wisely - patience and planning will multiply your natural enthusiasm")
        elif hand_shape == "water":
            recommendations.append("Protect your emotional sensitivity while staying open - boundaries enhance rather than limit your gifts")

        # Check for prominent mounts and add specific recommendations
        prominent_mounts = [m.get("mount_name") for m in mounts if m.get("prominence") in ["prominent", "very_prominent"]]

        if "Jupiter" in prominent_mounts:
            recommendations.append("Your leadership qualities are strong - seek positions of authority where you can guide others ethically")
        if "Saturn" in prominent_mounts:
            recommendations.append("Your seriousness and discipline are assets - balance them with joy and social connection")
        if "Apollo" in prominent_mounts:
            recommendations.append("Your creative talents deserve expression - pursue artistic or aesthetic endeavors seriously")
        if "Mercury" in prominent_mounts:
            recommendations.append("Your communication skills are exceptional - use them in business, teaching, or writing")
        if "Venus" in prominent_mounts:
            recommendations.append("Your capacity for love is profound - ensure it's mutual and doesn't lead to self-sacrifice")
        if "Luna" in prominent_mounts:
            recommendations.append("Your imagination is powerful - channel it into creative projects rather than worry or fantasy")

        # General recommendations
        recommendations.extend([
            "Compare both hands regularly - your non-dominant hand shows potential, dominant hand shows development",
            "Major palm features remain constant, but minor lines can change - review your palm annually",
            "Use challenging indicators as awareness tools, not limitations - free will shapes your destiny",
            "Consult your birth chart and numerology for complete self-understanding - palmistry is one piece of the puzzle"
        ])

        return recommendations

    def _format_detailed_analysis(self, interpretation: Dict) -> str:
        """Format the comprehensive interpretation into readable text."""
        sections = []

        # Header
        sections.append("=" * 80)
        sections.append("COMPREHENSIVE PALM READING ANALYSIS")
        sections.append("=" * 80)
        sections.append("")

        # Summary
        sections.append("OVERVIEW")
        sections.append("-" * 80)
        sections.append(interpretation["summary"])
        sections.append("")

        # Hand Shape
        sections.append("HAND SHAPE ANALYSIS")
        sections.append("-" * 80)
        shape = interpretation["hand_shape_analysis"]
        sections.append(f"**Type:** {shape['shape_type']} ({shape['element']} Element)")
        sections.append(f"**Description:** {shape['description']}")
        sections.append(f"**Personality:** {shape['personality_traits']}")
        sections.append(f"**Strengths:** {shape['strengths']}")
        sections.append(f"**Challenges:** {shape['weaknesses']}")
        sections.append(f"**Career Aptitudes:** {shape['career_aptitudes']}")
        sections.append("")

        # Lines Analysis
        sections.append("MAJOR PALM LINES")
        sections.append("-" * 80)
        for line_name, line_data in interpretation["line_analysis"].items():
            sections.append(f"\n**{line_data['line_name']}:**")
            sections.append(f"*Purpose:* {line_data['description']}")
            sections.append(f"*Confidence:* {line_data['confidence']:.0%}")
            if line_data["detected_characteristics"]:
                sections.append(f"*Characteristics Detected:* {', '.join(line_data['detected_characteristics'])}")
            if line_data["interpretation"]:
                sections.append("*Interpretation:*")
                for interp in line_data["interpretation"]:
                    sections.append(f"  • {interp}")
        sections.append("")

        # Mounts Analysis
        sections.append("PALM MOUNTS")
        sections.append("-" * 80)
        for mount_name, mount_data in interpretation["mount_analysis"].items():
            sections.append(f"\n**{mount_data['mount_name']}:**")
            sections.append(f"*Location:* {mount_data['location']}")
            sections.append(f"*Rules:* {mount_data['rules']}")
            sections.append(f"*Prominence:* {mount_data['prominence_level'].title()} (Confidence: {mount_data['confidence']:.0%})")
            sections.append(f"*Interpretation:* {mount_data['interpretation']}")
            if mount_data.get("career_implications"):
                sections.append(f"*Career Impact:* {mount_data['career_implications']}")
        sections.append("")

        # Special Markings
        if interpretation["special_markings_analysis"]:
            sections.append("SPECIAL MARKINGS")
            sections.append("-" * 80)
            for marking in interpretation["special_markings_analysis"]:
                sections.append(f"\n**{marking['marking_type']} on {marking['location']}:**")
                sections.append(f"*General Meaning:* {marking['general_meaning']}")
                sections.append(f"*Specific Interpretation:* {marking['specific_interpretation']}")
            sections.append("")

        # Personality Synthesis
        sections.append("PERSONALITY SYNTHESIS")
        sections.append("-" * 80)
        personality = interpretation["personality_synthesis"]
        sections.append(f"**Core Traits:** {', '.join(personality['core_traits'])}")
        sections.append(f"**Overall Temperament:** {personality['overall_temperament']}")
        sections.append(f"**Primary Motivations:** {personality['motivations']}")
        sections.append(f"**Interpersonal Style:** {personality['interpersonal_style']}")
        sections.append(f"**Decision-Making:** {personality['decision_making_style']}")
        sections.append("")

        # Life Predictions
        sections.append("LIFE PREDICTIONS & TIMING")
        sections.append("-" * 80)
        for prediction in interpretation["life_predictions"]:
            sections.append(f"\n**{prediction['area']}:**")
            sections.append(f"*Prediction:* {prediction['prediction']}")
            sections.append(f"*Timing:* {prediction['timing']}")
            sections.append(f"*Confidence:* {prediction['confidence']:.0%}")
        sections.append("")

        # Career Guidance
        sections.append("CAREER GUIDANCE")
        sections.append("-" * 80)
        career = interpretation["career_guidance"]
        sections.append(f"**Primary Aptitudes:** {career['primary_aptitudes']}")
        sections.append(f"**Mount Influences:** {', '.join(career['mount_influences'])}")
        sections.append(f"**Success Indicators:** {', '.join(career['success_indicators'])}")
        sections.append(f"**Challenges:** {', '.join(career['challenges_to_overcome'])}")
        sections.append(f"**Timing:** {career['timing_for_changes']}")
        sections.append("")

        # Relationship Insights
        sections.append("RELATIONSHIP & LOVE INSIGHTS")
        sections.append("-" * 80)
        relationship = interpretation["relationship_insights"]
        sections.append(f"**Relationship Style:** {relationship['relationship_style']}")
        sections.append(f"**Capacity for Love:** {relationship['capacity_for_love']}")
        sections.append(f"**Marriage Indications:** {relationship['marriage_indications']}")
        sections.append(f"**Emotional Nature:** {relationship['emotional_nature']}")
        sections.append(f"**Compatibility:** {relationship['compatibility_factors']}")
        sections.append("")

        # Health Insights
        sections.append("HEALTH & VITALITY")
        sections.append("-" * 80)
        health = interpretation["health_insights"]
        sections.append(f"**Vitality Assessment:** {health['vitality_assessment']}")
        sections.append(f"**Areas Needing Attention:**")
        for area in health["areas_needing_attention"]:
            sections.append(f"  • {area}")
        sections.append(f"\n**Preventive Recommendations:**")
        for rec in health["preventive_recommendations"]:
            sections.append(f"  • {rec}")
        sections.append(f"\n**Recovery Ability:** {health['recovery_ability']}")
        sections.append("")

        # Holistic Correlations
        if interpretation.get("astrology_correlations"):
            sections.append("ASTROLOGICAL CORRELATIONS")
            sections.append("-" * 80)
            astro = interpretation["astrology_correlations"]
            sections.append(f"**Sun Sign:** {astro.get('sun_sign', 'N/A')}")
            sections.append(f"**Moon Sign:** {astro.get('moon_sign', 'N/A')}")
            sections.append(f"**Ascendant:** {astro.get('ascendant', 'N/A')}")
            sections.append(f"**Correlation Notes:** {astro.get('correlation_notes', '')}")
            sections.append("")

        if interpretation.get("numerology_correlations"):
            sections.append("NUMEROLOGICAL CORRELATIONS")
            sections.append("-" * 80)
            num = interpretation["numerology_correlations"]
            sections.append(f"**Life Path Number:** {num.get('life_path', 'N/A')}")
            sections.append(f"**Destiny Number:** {num.get('destiny_number', 'N/A')}")
            sections.append(f"**Correlation Notes:** {num.get('correlation_notes', '')}")
            sections.append("")

        # Recommendations
        sections.append("RECOMMENDATIONS & GUIDANCE")
        sections.append("-" * 80)
        for i, rec in enumerate(interpretation["recommendations"], 1):
            sections.append(f"{i}. {rec}")
        sections.append("")

        # Footer
        sections.append("=" * 80)
        sections.append("This reading is based on traditional palmistry principles and should be used")
        sections.append("for self-awareness and personal growth. Your choices and free will shape your destiny.")
        sections.append("=" * 80)

        return "\n".join(sections)

    # Helper methods for personality synthesis

    def _determine_temperament(self, hand_shape: str, mounts: List[Dict]) -> str:
        """Determine overall temperament from shape and mounts."""
        base_temp = {
            "earth": "Stable and grounded",
            "air": "Mental and communicative",
            "fire": "Dynamic and passionate",
            "water": "Emotional and intuitive"
        }.get(hand_shape, "Balanced")

        # Modify based on dominant mounts
        prominent = [m.get("mount_name") for m in mounts if m.get("prominence") in ["prominent", "very_prominent"]]
        if "Jupiter" in prominent:
            base_temp += " with leadership drive"
        if "Venus" in prominent:
            base_temp += " and affectionate nature"

        return base_temp

    def _determine_motivations(self, mounts: List[Dict]) -> str:
        """Determine primary motivations from mounts."""
        motivations = []
        prominent = [m.get("mount_name") for m in mounts if m.get("prominence") in ["prominent", "very_prominent"]]

        if "Jupiter" in prominent:
            motivations.append("Achievement and recognition")
        if "Saturn" in prominent:
            motivations.append("Knowledge and understanding")
        if "Apollo" in prominent:
            motivations.append("Creative expression and beauty")
        if "Mercury" in prominent:
            motivations.append("Communication and commerce")
        if "Venus" in prominent:
            motivations.append("Love and connection")
        if "Luna" in prominent:
            motivations.append("Imagination and exploration")

        return ", ".join(motivations) if motivations else "Balanced personal growth"

    def _determine_interpersonal_style(self, hand_shape: str, lines: List[Dict]) -> str:
        """Determine how person relates to others."""
        heart_line = next((l for l in lines if l.get("line_type") == "heart"), None)

        base_style = {
            "earth": "Practical and loyal",
            "air": "Social and communicative",
            "fire": "Direct and enthusiastic",
            "water": "Empathetic and sensitive"
        }.get(hand_shape, "Balanced")

        if heart_line:
            char = heart_line.get("characteristics", {})
            if char.get("curve") == "moderate":
                base_style += ", warm but not overwhelming"
            elif char.get("length") == "long":
                base_style += ", deeply engaged in relationships"

        return base_style

    def _determine_decision_style(self, lines: List[Dict]) -> str:
        """Determine decision-making approach from head line."""
        head_line = next((l for l in lines if l.get("line_type") == "head"), None)

        if not head_line:
            return "Balanced decision-making approach"

        char = head_line.get("characteristics", {})
        if char.get("length") == "long":
            style = "Analytical and thorough"
        elif char.get("length") == "short":
            style = "Quick and instinctive"
        else:
            style = "Balanced analysis"

        if char.get("slope") == "steeply_sloped" or char.get("curved"):
            style += ", influenced by creativity and intuition"
        elif char.get("straight"):
            style += ", logical and practical"

        return style

    def _determine_emotional_nature(self, heart_line: Optional[Dict], venus_mount: Optional[Dict]) -> str:
        """Determine emotional nature from heart line and Venus."""
        if not heart_line:
            return "Emotionally balanced"

        char = heart_line.get("characteristics", {})
        nature = []

        if char.get("length") == "long":
            nature.append("deeply feeling")
        if char.get("depth") == "deep":
            nature.append("intensely emotional")
        if char.get("curve") == "moderate":
            nature.append("warm")

        if venus_mount and venus_mount.get("prominence") in ["prominent", "very_prominent"]:
            nature.append("passionate")

        return ", ".join(nature) if nature else "emotionally balanced"

    def _identify_success_indicators(self, lines: List[Dict], mounts: List[Dict]) -> List[str]:
        """Identify indicators of success in the palm."""
        indicators = []

        fate_line = next((l for l in lines if l.get("line_type") == "fate"), None)
        sun_line = next((l for l in lines if l.get("line_type") == "sun"), None)

        if fate_line:
            indicators.append("Clear fate line shows defined career path")
        if sun_line:
            indicators.append("Sun line indicates recognition and success potential")

        prominent = [m.get("mount_name") for m in mounts if m.get("prominence") in ["prominent", "very_prominent"]]
        if "Jupiter" in prominent:
            indicators.append("Strong Jupiter mount shows leadership ability")
        if "Apollo" in prominent:
            indicators.append("Prominent Apollo mount indicates creative success")

        return indicators if indicators else ["Success through consistent effort"]

    def _identify_career_challenges(self, lines: List[Dict], mounts: List[Dict]) -> List[str]:
        """Identify potential career challenges."""
        challenges = []

        fate_line = next((l for l in lines if l.get("line_type") == "fate"), None)
        if not fate_line:
            challenges.append("Need to create your own direction without clear path")
        elif fate_line.get("characteristics", {}).get("broken"):
            challenges.append("Career changes and transitions to navigate")

        saturn_mount = next((m for m in mounts if m.get("mount_name") == "Saturn"), None)
        if saturn_mount and saturn_mount.get("prominence") in ["prominent", "very_prominent"]:
            challenges.append("Tendency toward pessimism may hinder opportunities")

        return challenges if challenges else ["Minor obstacles overcome through persistence"]

    def _get_life_theme(self, hand_shape: str, lines: List[Dict], mounts: List[Dict]) -> str:
        """Determine overall life theme."""
        themes = {
            "earth": "practical achievements and steady growth",
            "air": "intellectual pursuits and communication",
            "fire": "dynamic action and passionate endeavors",
            "water": "emotional depth and creative expression"
        }

        base_theme = themes.get(hand_shape, "balanced personal development")

        # Check for strong fate/sun lines
        fate_line = next((l for l in lines if l.get("line_type") == "fate"), None)
        sun_line = next((l for l in lines if l.get("line_type") == "sun"), None)

        if fate_line and sun_line:
            base_theme += " leading to recognition and fulfillment"
        elif fate_line:
            base_theme += " with clear sense of purpose"

        return base_theme

    def _correlate_with_astrology(self, hand_shape: str, lines: List[Dict], mounts: List[Dict], chart: Optional[Dict]) -> Optional[Dict]:
        """Correlate palm features with astrological chart."""
        if not chart:
            return None

        # Element correlation
        palm_element = self.hand_shapes[hand_shape]["element"]
        sun_sign = chart.get("sun_sign", "")

        # Determine chart's primary element
        fire_signs = ["Aries", "Leo", "Sagittarius"]
        earth_signs = ["Taurus", "Virgo", "Capricorn"]
        air_signs = ["Gemini", "Libra", "Aquarius"]
        water_signs = ["Cancer", "Scorpio", "Pisces"]

        chart_element = ""
        if sun_sign in fire_signs:
            chart_element = "Fire"
        elif sun_sign in earth_signs:
            chart_element = "Earth"
        elif sun_sign in air_signs:
            chart_element = "Air"
        elif sun_sign in water_signs:
            chart_element = "Water"

        correlation_note = f"Your {palm_element} hand "
        if palm_element == chart_element:
            correlation_note += f"perfectly aligns with your {sun_sign} Sun, creating a powerful resonance of {palm_element.lower()} energy."
        else:
            correlation_note += f"complements your {sun_sign} Sun ({chart_element}), providing balance between {palm_element.lower()} and {chart_element.lower()} qualities."

        return {
            "sun_sign": sun_sign,
            "moon_sign": chart.get("moon_sign"),
            "ascendant": chart.get("ascendant"),
            "palm_element": palm_element,
            "chart_element": chart_element,
            "correlation_notes": correlation_note
        }

    def _correlate_with_numerology(self, hand_shape: str, lines: List[Dict], mounts: List[Dict], numerology: Optional[Dict]) -> Optional[Dict]:
        """Correlate palm features with numerology profile."""
        if not numerology:
            return None

        life_path = numerology.get("life_path")

        # Correlate life path with palm features
        correlation_note = f"Your Life Path {life_path} "

        if life_path in [1, 8]:
            correlation_note += "leadership energy is reflected in "
            if any(m.get("mount_name") == "Jupiter" and m.get("prominence") in ["prominent", "very_prominent"] for m in mounts):
                correlation_note += "your prominent Jupiter mount, indicating natural authority."
            else:
                correlation_note += "your palm's overall configuration, suggesting development of leadership qualities."

        elif life_path in [2, 6]:
            correlation_note += "harmonious nature aligns with "
            heart_line = next((l for l in lines if l.get("line_type") == "heart"), None)
            if heart_line:
                correlation_note += "your strong heart line, emphasizing relationships and cooperation."
            else:
                correlation_note += "your palm's balance, supporting your peacemaking abilities."

        elif life_path in [3, 5]:
            correlation_note += "creative and expressive energy is visible in "
            if any(m.get("mount_name") in ["Apollo", "Mercury"] and m.get("prominence") in ["prominent", "very_prominent"] for m in mounts):
                correlation_note += "your prominent creative mounts, showing natural artistic talents."
            else:
                correlation_note += "your palm's features, suggesting creative potential to develop."

        elif life_path in [4, 7]:
            correlation_note += "analytical and structured approach is evident in "
            head_line = next((l for l in lines if l.get("line_type") == "head"), None)
            if head_line and head_line.get("characteristics", {}).get("length") == "long":
                correlation_note += "your long head line, indicating detailed and thorough thinking."
            else:
                correlation_note += "your palm's configuration, supporting systematic approaches."

        else:
            correlation_note += "unique qualities are reflected throughout your palm's features."

        return {
            "life_path": life_path,
            "destiny_number": numerology.get("destiny_number"),
            "personal_year": numerology.get("personal_year"),
            "correlation_notes": correlation_note
        }


# Singleton instance
palmistry_interpretation_service = PalmistryInterpretationService()
