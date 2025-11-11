"""
AstroWordle Game Service
Handles game logic, answer validation, scoring, and daily challenge management
"""

from datetime import date, datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import re
from difflib import SequenceMatcher
import secrets
import hashlib


class AstroWordleService:
    """Service for AstroWordle game logic"""

    # Score mapping based on number of guesses
    SCORE_MAP = {
        1: 100,
        2: 83,
        3: 66,
        4: 50,
        5: 33,
        6: 16
    }

    MAX_GUESSES = 6

    def __init__(self):
        pass

    @staticmethod
    def normalize_answer(answer: str) -> str:
        """Normalize answer for comparison"""
        # Convert to lowercase
        answer = answer.lower().strip()
        # Remove extra spaces
        answer = re.sub(r'\s+', ' ', answer)
        # Remove special characters except degrees, apostrophes
        answer = re.sub(r'[^\w\s°\']', '', answer)
        return answer

    @staticmethod
    def calculate_similarity(guess: str, correct: str) -> float:
        """Calculate similarity between guess and correct answer (0.0 to 1.0)"""
        guess_norm = AstroWordleService.normalize_answer(guess)
        correct_norm = AstroWordleService.normalize_answer(correct)
        return SequenceMatcher(None, guess_norm, correct_norm).ratio()

    def validate_answer(
        self,
        guess: str,
        correct_answer: str,
        acceptable_answers: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Validate a guess against the correct answer

        Returns:
            {
                "is_correct": bool,
                "similarity": float,  # 0.0 to 1.0
                "feedback": str,  # "correct", "close", "wrong"
                "hint": str  # Helpful hint based on proximity
            }
        """
        acceptable_answers = acceptable_answers or []
        all_acceptable = [correct_answer] + acceptable_answers

        # Normalize guess
        guess_norm = self.normalize_answer(guess)

        # Check exact matches
        for acceptable in all_acceptable:
            if guess_norm == self.normalize_answer(acceptable):
                return {
                    "is_correct": True,
                    "similarity": 1.0,
                    "feedback": "correct",
                    "hint": "Perfect! That's correct!"
                }

        # Calculate similarity to correct answer
        max_similarity = max(
            self.calculate_similarity(guess, acceptable)
            for acceptable in all_acceptable
        )

        # Determine feedback based on similarity
        if max_similarity >= 0.9:
            feedback = "very_close"
            hint = "You're very close! Check your spelling."
        elif max_similarity >= 0.7:
            feedback = "close"
            hint = "You're getting closer!"
        elif max_similarity >= 0.5:
            feedback = "somewhat_close"
            hint = "On the right track, but not quite."
        else:
            feedback = "wrong"
            hint = "Try again!"

        return {
            "is_correct": False,
            "similarity": max_similarity,
            "feedback": feedback,
            "hint": hint
        }

    def calculate_score(self, num_guesses: int, is_correct: bool) -> int:
        """Calculate score based on number of guesses"""
        if not is_correct:
            return 0

        if num_guesses <= 0 or num_guesses > self.MAX_GUESSES:
            return 0

        return self.SCORE_MAP.get(num_guesses, 0)

    def generate_emoji_grid(self, guesses: List[Dict[str, Any]], is_won: bool) -> str:
        """
        Generate emoji grid for sharing (like Wordle)

        Args:
            guesses: List of guess objects with feedback
            is_won: Whether the user won

        Returns:
            Emoji grid string like:
            🟢⬜⬜⬜⬜
            🟢🟡⬜⬜⬜
            🟢🟢🟢🟢🟢
        """
        emoji_map = {
            "correct": "🟢",
            "very_close": "🟡",
            "close": "🟠",
            "somewhat_close": "🔵",
            "wrong": "⬜"
        }

        grid_lines = []
        for guess in guesses:
            feedback = guess.get("feedback", "wrong")
            # Create a line of 5 emojis (simplified visual representation)
            emoji = emoji_map.get(feedback, "⬜")
            line = emoji * 5 if feedback == "correct" else emoji + "⬜⬜⬜⬜"
            grid_lines.append(line)

        # Fill remaining lines if not all guesses used
        while len(grid_lines) < len(guesses):
            grid_lines.append("⬜⬜⬜⬜⬜")

        return "\n".join(grid_lines)

    def generate_share_text(
        self,
        challenge_number: int,
        num_guesses: int,
        is_won: bool,
        emoji_grid: str,
        share_code: Optional[str] = None
    ) -> str:
        """
        Generate share text for social media

        Returns formatted text like:
        AstroWordle #123 3/6

        🟢⬜⬜⬜⬜
        🟢🟡⬜⬜⬜
        🟢🟢🟢🟢🟢

        Test your astrology knowledge!
        jioastro.com/astrowordle?ref=ABC123
        """
        result = f"{num_guesses}/6" if is_won else "X/6"

        share_text = f"AstroWordle #{challenge_number} {result}\n\n{emoji_grid}\n\n"
        share_text += "Test your astrology knowledge! 🌟\n"

        if share_code:
            share_text += f"jioastro.com/astrowordle?ref={share_code}"
        else:
            share_text += "jioastro.com/astrowordle"

        return share_text

    def generate_share_code(self, user_id: str, challenge_id: str) -> str:
        """Generate unique share code for viral tracking"""
        # Create deterministic but unique code
        seed = f"{user_id}{challenge_id}{datetime.now().isoformat()}"
        hash_obj = hashlib.sha256(seed.encode())
        # Take first 8 characters of hex digest
        return hash_obj.hexdigest()[:8].upper()

    def get_challenge_number(self, challenge_date: date) -> int:
        """Calculate challenge number from date (days since launch)"""
        # Launch date: January 1, 2025
        launch_date = date(2025, 1, 1)
        delta = challenge_date - launch_date
        return delta.days + 1

    def calculate_streak(
        self,
        last_played_date: Optional[date],
        current_streak: int,
        new_play_date: date,
        is_correct: bool
    ) -> Dict[str, Any]:
        """
        Calculate updated streak information

        Returns:
            {
                "current_streak": int,
                "streak_updated": bool,
                "streak_broken": bool,
                "new_record": bool
            }
        """
        if not is_correct:
            return {
                "current_streak": 0,
                "streak_updated": True,
                "streak_broken": current_streak > 0,
                "new_record": False
            }

        if last_played_date is None:
            # First time playing
            return {
                "current_streak": 1,
                "streak_updated": True,
                "streak_broken": False,
                "new_record": True
            }

        # Check if consecutive day
        expected_date = last_played_date + timedelta(days=1)

        if new_play_date == expected_date:
            # Continue streak
            new_streak = current_streak + 1
            return {
                "current_streak": new_streak,
                "streak_updated": True,
                "streak_broken": False,
                "new_record": False
            }
        elif new_play_date == last_played_date:
            # Same day (replay)
            return {
                "current_streak": current_streak,
                "streak_updated": False,
                "streak_broken": False,
                "new_record": False
            }
        else:
            # Streak broken
            return {
                "current_streak": 1,
                "streak_updated": True,
                "streak_broken": True,
                "new_record": False
            }

    def get_difficulty_hints(self, difficulty: str, num_guesses: int) -> List[str]:
        """Get progressive hints based on difficulty and number of guesses"""
        hints = {
            "beginner": [
                "Think about the basic properties...",
                "Consider the common associations...",
                "Check the fundamental characteristics..."
            ],
            "intermediate": [
                "Think about the planetary relationships...",
                "Consider the house placements...",
                "Review the astrological principles..."
            ],
            "advanced": [
                "Think about the specific degrees...",
                "Consider the subtle interactions...",
                "Review the classical texts..."
            ]
        }

        difficulty_hints = hints.get(difficulty, hints["beginner"])
        # Return hints progressively based on number of guesses
        hint_index = min(num_guesses - 1, len(difficulty_hints) - 1)
        return difficulty_hints[:hint_index + 1]

    def calculate_leaderboard_rank(
        self,
        user_score: int,
        all_scores: List[int]
    ) -> int:
        """Calculate user's rank in leaderboard"""
        all_scores_sorted = sorted(all_scores, reverse=True)
        try:
            return all_scores_sorted.index(user_score) + 1
        except ValueError:
            return len(all_scores) + 1

    def generate_stats_summary(
        self,
        total_games: int,
        total_wins: int,
        current_streak: int,
        longest_streak: int,
        wins_distribution: Dict[int, int]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive stats summary

        Args:
            wins_distribution: {1: 5, 2: 10, 3: 8, ...} - wins by number of guesses

        Returns:
            Formatted stats dictionary
        """
        win_percentage = (total_wins / total_games * 100) if total_games > 0 else 0

        # Calculate average guesses for wins
        total_guesses_for_wins = sum(
            num_guesses * count
            for num_guesses, count in wins_distribution.items()
        )
        avg_guesses = (
            total_guesses_for_wins / total_wins
            if total_wins > 0
            else 0
        )

        # Find most common win guess count
        if wins_distribution:
            most_common_win = max(wins_distribution, key=wins_distribution.get)
        else:
            most_common_win = None

        return {
            "total_games": total_games,
            "total_wins": total_wins,
            "win_percentage": round(win_percentage, 1),
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "average_guesses": round(avg_guesses, 1),
            "most_common_win": most_common_win,
            "wins_distribution": wins_distribution
        }

    def format_question_for_display(
        self,
        question: Dict[str, Any],
        hide_answer: bool = True
    ) -> Dict[str, Any]:
        """Format question data for client display"""
        formatted = {
            "id": question.get("id"),
            "question_text": question.get("question_text"),
            "question_type": question.get("question_type"),
            "difficulty": question.get("difficulty"),
            "answer_format": question.get("answer_format"),
            "options": question.get("options"),
            "hint": question.get("hint"),
            "category": question.get("category"),
            "tags": question.get("tags", [])
        }

        # Only include answer and explanation after completion
        if not hide_answer:
            formatted["correct_answer"] = question.get("correct_answer")
            formatted["explanation"] = question.get("explanation")

        return formatted

    def validate_guess_count(self, current_guesses: int) -> Tuple[bool, str]:
        """Validate if user can make another guess"""
        if current_guesses >= self.MAX_GUESSES:
            return False, "Maximum number of guesses reached"

        if current_guesses < 0:
            return False, "Invalid guess count"

        return True, "OK"

    def get_performance_badge(self, num_guesses: int, is_won: bool) -> Dict[str, str]:
        """Get performance badge based on result"""
        if not is_won:
            return {
                "badge": "better_luck",
                "title": "Better Luck Tomorrow!",
                "emoji": "🌙",
                "message": "Every day is a new chance to learn!"
            }

        badges = {
            1: {
                "badge": "genius",
                "title": "Astrological Genius!",
                "emoji": "🌟",
                "message": "Perfect first guess!"
            },
            2: {
                "badge": "expert",
                "title": "Astrology Expert!",
                "emoji": "⭐",
                "message": "Impressive knowledge!"
            },
            3: {
                "badge": "skilled",
                "title": "Well Done!",
                "emoji": "✨",
                "message": "Great astrological skills!"
            },
            4: {
                "badge": "good",
                "title": "Good Job!",
                "emoji": "🌙",
                "message": "Solid performance!"
            },
            5: {
                "badge": "close",
                "title": "That Was Close!",
                "emoji": "🌠",
                "message": "You made it!"
            },
            6: {
                "badge": "clutch",
                "title": "Clutch Victory!",
                "emoji": "💫",
                "message": "Just in time!"
            }
        }

        return badges.get(num_guesses, badges[6])
