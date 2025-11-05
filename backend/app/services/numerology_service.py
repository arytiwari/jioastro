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

        # Reduce each component separately (more accurate for master numbers)
        month_reduced = reduce_to_single_digit(month, preserve_master=True)
        day_reduced = reduce_to_single_digit(day, preserve_master=True)

        # Year reduction
        year_sum = sum(int(digit) for digit in str(year))
        year_reduced = reduce_to_single_digit(year_sum, preserve_master=True)

        # Detect karmic debt in intermediate sums
        karmic_debt = None
        intermediate_sums = [day, month + day, month + day + year_sum]
        for num in intermediate_sums:
            if num in KARMIC_DEBT_NUMBERS:
                karmic_debt = num
                break

        # Add reduced components
        total = month_reduced + day_reduced + year_reduced

        # Check if this intermediate sum is karmic debt
        if total in KARMIC_DEBT_NUMBERS and karmic_debt is None:
            karmic_debt = total

        # Final reduction
        life_path = reduce_to_single_digit(total, preserve_master=True)

        return {
            'number': life_path,
            'is_master': life_path in MASTER_NUMBERS,
            'karmic_debt': karmic_debt,
            'breakdown': {
                'month': month,
                'day': day,
                'year': year,
                'month_reduced': month_reduced,
                'day_reduced': day_reduced,
                'year_reduced': year_reduced,
                'sum_before_reduction': total,
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

        return {
            'number': expression,
            'is_master': expression in MASTER_NUMBERS,
            'karmic_debt': karmic_debt,
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

        return {
            'number': soul_urge,
            'is_master': soul_urge in MASTER_NUMBERS,
            'karmic_debt': karmic_debt,
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

        return {
            'number': personality,
            'is_master': personality in MASTER_NUMBERS,
            'karmic_debt': karmic_debt,
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

        return {
            'number': personal_year,
            'year': current_year,
            'cycle_position': f"Year {personal_year} of 9",
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

        return {
            'number': psychic,
            'planet': PLANET_MAP[psychic],
            'day_of_birth': day,
            'breakdown': {
                'day': day,
                'final': psychic
            }
        }

    @staticmethod
    def calculate_destiny_number(full_name: str) -> Dict[str, Any]:
        """
        Calculate Destiny Number (Bhagyank) using Chaldean system.

        The Destiny Number represents how others see you and your
        destiny/life path. Uses Chaldean letter-to-number mapping.

        Method: Convert name using Chaldean values, reduce to single digit.

        Args:
            full_name: Full name (current name, not necessarily birth name)

        Returns:
            Dict with 'number', 'planet', 'letter_values', 'breakdown'
        """
        total, letter_breakdown = calculate_name_value(full_name, 'chaldean')
        destiny = reduce_to_single_digit(total, preserve_master=False)

        return {
            'number': destiny,
            'planet': PLANET_MAP[destiny],
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
            Dict with 'value', 'reduced', 'letter_values'
        """
        total, letter_breakdown = calculate_name_value(name, 'chaldean')
        reduced = reduce_to_single_digit(total, preserve_master=False)

        return {
            'value': total,
            'reduced': reduced,
            'planet': PLANET_MAP[reduced],
            'letter_values': letter_breakdown
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
