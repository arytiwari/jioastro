"""
AstroWordle API Endpoints
Daily astrology quiz game with viral mechanics
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List, Optional
from datetime import date, datetime
import logging
from uuid import UUID

from app.core.security import get_current_user
from app.services.supabase_service import supabase_service
from app.services.astrowordle_service import AstroWordleService

router = APIRouter()
logger = logging.getLogger(__name__)
game_service = AstroWordleService()


# ============================================================================
# DAILY CHALLENGE ENDPOINTS
# ============================================================================

@router.get("/today")
async def get_todays_challenge(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get today's AstroWordle challenge

    Returns:
        - challenge_id: UUID
        - challenge_number: int (days since launch)
        - question: Question object (without answer)
        - user_attempt: User's attempt if already played
        - is_completed: bool
    """
    try:
        supabase = get_supabase_client()
        user_id = current_user["sub"]
        today = date.today()

        # Get or create today's challenge using database function
        result = supabase.rpc("generate_daily_astrowordle_challenge", {
            "p_date": today.isoformat()
        }).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate daily challenge"
            )

        challenge_id = result.data

        # Get challenge details
        challenge = supabase.table("astrowordle_daily_challenges") \
            .select("*, question:astrowordle_questions(*)") \
            .eq("id", challenge_id) \
            .single() \
            .execute()

        if not challenge.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Challenge not found"
            )

        # Check if user has already attempted today
        attempt = supabase.table("astrowordle_user_attempts") \
            .select("*") \
            .eq("user_id", user_id) \
            .eq("challenge_id", challenge_id) \
            .execute()

        user_attempt = attempt.data[0] if attempt.data else None
        is_completed = user_attempt is not None if user_attempt else False

        # Format question (hide answer if not completed)
        question_data = challenge.data.get("question", {})
        formatted_question = game_service.format_question_for_display(
            question_data,
            hide_answer=not is_completed
        )

        # Get challenge number
        challenge_number = game_service.get_challenge_number(today)

        return {
            "success": True,
            "data": {
                "challenge_id": challenge_id,
                "challenge_number": challenge_number,
                "challenge_date": today.isoformat(),
                "question": formatted_question,
                "user_attempt": user_attempt,
                "is_completed": is_completed,
                "guesses_remaining": (
                    game_service.MAX_GUESSES - user_attempt.get("num_guesses", 0)
                    if user_attempt and not user_attempt.get("is_completed")
                    else game_service.MAX_GUESSES
                )
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting today's challenge: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get today's challenge: {str(e)}"
        )


@router.post("/submit-guess")
async def submit_guess(
    guess: str,
    challenge_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Submit a guess for today's challenge

    Request:
        - guess: str
        - challenge_id: UUID

    Returns:
        - is_correct: bool
        - feedback: str ("correct", "very_close", "close", "wrong")
        - hint: str
        - guesses_remaining: int
        - is_completed: bool
        - score: int (if completed)
        - badge: dict (if completed)
    """
    try:
        supabase = get_supabase_client()
        user_id = current_user["sub"]

        # Get challenge and question
        challenge = supabase.table("astrowordle_daily_challenges") \
            .select("*, question:astrowordle_questions(*)") \
            .eq("id", challenge_id) \
            .single() \
            .execute()

        if not challenge.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Challenge not found"
            )

        question = challenge.data.get("question", {})

        # Get or create user attempt
        attempt = supabase.table("astrowordle_user_attempts") \
            .select("*") \
            .eq("user_id", user_id) \
            .eq("challenge_id", challenge_id) \
            .execute()

        if attempt.data:
            current_attempt = attempt.data[0]

            # Check if already completed
            if current_attempt.get("is_completed"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Challenge already completed"
                )

            # Check if max guesses reached
            current_guesses = current_attempt.get("num_guesses", 0)
            if current_guesses >= game_service.MAX_GUESSES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Maximum guesses reached"
                )

            guesses_list = current_attempt.get("guesses", [])
        else:
            current_guesses = 0
            guesses_list = []

        # Validate guess
        validation = game_service.validate_answer(
            guess,
            question.get("correct_answer"),
            question.get("acceptable_answers")
        )

        # Add guess to list
        new_guess = {
            "guess": guess,
            "is_correct": validation["is_correct"],
            "feedback": validation["feedback"],
            "timestamp": datetime.now().isoformat()
        }
        guesses_list.append(new_guess)

        num_guesses = len(guesses_list)
        is_completed = validation["is_correct"] or num_guesses >= game_service.MAX_GUESSES

        # Calculate score if completed
        score = 0
        badge = None
        if is_completed:
            score = game_service.calculate_score(num_guesses, validation["is_correct"])
            badge = game_service.get_performance_badge(num_guesses, validation["is_correct"])

        # Update or create attempt
        attempt_data = {
            "user_id": user_id,
            "challenge_id": challenge_id,
            "guesses": guesses_list,
            "num_guesses": num_guesses,
            "is_completed": is_completed,
            "is_correct": validation["is_correct"],
            "score": score
        }

        if attempt.data:
            # Update existing attempt
            updated = supabase.table("astrowordle_user_attempts") \
                .update(attempt_data) \
                .eq("id", current_attempt["id"]) \
                .execute()
        else:
            # Create new attempt
            updated = supabase.table("astrowordle_user_attempts") \
                .insert(attempt_data) \
                .execute()

        # Update streak if completed
        if is_completed:
            challenge_date = challenge.data.get("challenge_date")
            supabase.rpc("update_astrowordle_streak", {
                "p_user_id": user_id,
                "p_challenge_date": challenge_date,
                "p_is_correct": validation["is_correct"],
                "p_num_guesses": num_guesses
            }).execute()

        return {
            "success": True,
            "data": {
                "is_correct": validation["is_correct"],
                "feedback": validation["feedback"],
                "hint": validation["hint"],
                "guesses_remaining": game_service.MAX_GUESSES - num_guesses,
                "num_guesses": num_guesses,
                "is_completed": is_completed,
                "score": score if is_completed else None,
                "badge": badge if is_completed else None,
                "correct_answer": question.get("correct_answer") if is_completed else None,
                "explanation": question.get("explanation") if is_completed else None
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting guess: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit guess: {str(e)}"
        )


# ============================================================================
# STATS & STREAKS
# ============================================================================

@router.get("/my-stats")
async def get_my_stats(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get user's AstroWordle statistics and streaks

    Returns comprehensive stats including:
        - current_streak
        - longest_streak
        - total_games_played
        - total_games_won
        - win_percentage
        - average_guesses
        - wins_distribution {1: 5, 2: 10, ...}
    """
    try:
        supabase = get_supabase_client()
        user_id = current_user["sub"]

        # Get streak data
        streak = supabase.table("astrowordle_streaks") \
            .select("*") \
            .eq("user_id", user_id) \
            .execute()

        if not streak.data:
            # No stats yet
            return {
                "success": True,
                "data": {
                    "current_streak": 0,
                    "longest_streak": 0,
                    "total_games_played": 0,
                    "total_games_won": 0,
                    "win_percentage": 0,
                    "average_guesses": 0,
                    "wins_distribution": {}
                }
            }

        streak_data = streak.data[0]

        # Build wins distribution
        wins_distribution = {
            1: streak_data.get("wins_in_1", 0),
            2: streak_data.get("wins_in_2", 0),
            3: streak_data.get("wins_in_3", 0),
            4: streak_data.get("wins_in_4", 0),
            5: streak_data.get("wins_in_5", 0),
            6: streak_data.get("wins_in_6", 0)
        }

        # Generate comprehensive stats
        stats = game_service.generate_stats_summary(
            total_games=streak_data.get("total_games_played", 0),
            total_wins=streak_data.get("total_games_won", 0),
            current_streak=streak_data.get("current_streak", 0),
            longest_streak=streak_data.get("longest_streak", 0),
            wins_distribution=wins_distribution
        )

        return {
            "success": True,
            "data": stats
        }

    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )


@router.get("/history")
async def get_my_history(
    limit: int = 30,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get user's play history

    Query params:
        - limit: int (default 30, max 100)

    Returns list of past attempts with results
    """
    try:
        supabase = get_supabase_client()
        user_id = current_user["sub"]

        # Validate limit
        limit = min(max(1, limit), 100)

        # Get attempts with challenge info
        attempts = supabase.table("astrowordle_user_attempts") \
            .select("*, challenge:astrowordle_daily_challenges(challenge_date, question:astrowordle_questions(question_text, difficulty))") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()

        return {
            "success": True,
            "data": attempts.data or []
        }

    except Exception as e:
        logger.error(f"Error getting history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get history: {str(e)}"
        )


# ============================================================================
# LEADERBOARDS
# ============================================================================

@router.get("/leaderboard")
async def get_leaderboard(
    leaderboard_type: str = "all_time",  # all_time, monthly, weekly, daily
    limit: int = 100,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get global leaderboard

    Query params:
        - leaderboard_type: "all_time", "monthly", "weekly", "daily"
        - limit: int (default 100, max 500)

    Returns ranked list of users by score
    """
    try:
        supabase = get_supabase_client()
        user_id = current_user["sub"]

        # Validate limit
        limit = min(max(1, limit), 500)

        # Get leaderboard based on type
        if leaderboard_type == "all_time":
            # Use streaks table for all-time stats
            leaderboard = supabase.table("astrowordle_streaks") \
                .select("user_id, current_streak, longest_streak, total_games_played, total_games_won") \
                .order("longest_streak", desc=True) \
                .order("total_games_won", desc=True) \
                .limit(limit) \
                .execute()

        else:
            # Use leaderboard_entries table for time-based
            leaderboard = supabase.table("astrowordle_leaderboard_entries") \
                .select("*") \
                .eq("leaderboard_type", leaderboard_type) \
                .order("total_score", desc=True) \
                .limit(limit) \
                .execute()

        # Find current user's rank
        user_rank = None
        if leaderboard.data:
            for idx, entry in enumerate(leaderboard.data):
                if entry.get("user_id") == user_id:
                    user_rank = idx + 1
                    break

        return {
            "success": True,
            "data": {
                "leaderboard_type": leaderboard_type,
                "entries": leaderboard.data or [],
                "user_rank": user_rank,
                "total_entries": len(leaderboard.data) if leaderboard.data else 0
            }
        }

    except Exception as e:
        logger.error(f"Error getting leaderboard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get leaderboard: {str(e)}"
        )


@router.get("/friends-leaderboard")
async def get_friends_leaderboard(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get leaderboard of friends only

    Returns ranked list of friends by current streak and total wins
    """
    try:
        supabase = get_supabase_client()
        user_id = current_user["sub"]

        # Get friend IDs
        friends = supabase.table("friend_connections") \
            .select("friend_user_id") \
            .eq("user_id", user_id) \
            .eq("status", "accepted") \
            .execute()

        if not friends.data:
            return {
                "success": True,
                "data": {
                    "entries": [],
                    "message": "No friends yet. Invite friends to compare scores!"
                }
            }

        friend_ids = [f["friend_user_id"] for f in friends.data]
        friend_ids.append(user_id)  # Include current user

        # Get stats for all friends
        streaks = supabase.table("astrowordle_streaks") \
            .select("*") \
            .in_("user_id", friend_ids) \
            .order("current_streak", desc=True) \
            .order("total_games_won", desc=True) \
            .execute()

        # Add rank
        ranked_entries = []
        for idx, entry in enumerate(streaks.data or []):
            ranked_entry = {**entry, "rank": idx + 1}
            ranked_entries.append(ranked_entry)

        return {
            "success": True,
            "data": {
                "entries": ranked_entries,
                "total_friends": len(friend_ids) - 1
            }
        }

    except Exception as e:
        logger.error(f"Error getting friends leaderboard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get friends leaderboard: {str(e)}"
        )


# ============================================================================
# SHARE & VIRAL FEATURES
# ============================================================================

@router.post("/generate-share")
async def generate_share(
    attempt_id: str,
    template_type: str = "whatsapp",  # whatsapp, instagram_story, twitter
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Generate share template for social media

    Request:
        - attempt_id: UUID
        - template_type: "whatsapp", "instagram_story", "twitter"

    Returns:
        - emoji_grid: str
        - share_text: str
        - share_code: str (for viral tracking)
    """
    try:
        supabase = get_supabase_client()
        user_id = current_user["sub"]

        # Get attempt
        attempt = supabase.table("astrowordle_user_attempts") \
            .select("*, challenge:astrowordle_daily_challenges(challenge_date)") \
            .eq("id", attempt_id) \
            .eq("user_id", user_id) \
            .single() \
            .execute()

        if not attempt.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attempt not found"
            )

        # Generate emoji grid
        guesses = attempt.data.get("guesses", [])
        is_won = attempt.data.get("is_correct", False)
        emoji_grid = game_service.generate_emoji_grid(guesses, is_won)

        # Generate share code
        share_code = game_service.generate_share_code(user_id, attempt_id)

        # Get challenge number
        challenge_date = date.fromisoformat(attempt.data["challenge"]["challenge_date"])
        challenge_number = game_service.get_challenge_number(challenge_date)

        # Generate share text
        share_text = game_service.generate_share_text(
            challenge_number=challenge_number,
            num_guesses=attempt.data.get("num_guesses", 0),
            is_won=is_won,
            emoji_grid=emoji_grid,
            share_code=share_code
        )

        # Save share record
        share_record = {
            "user_id": user_id,
            "attempt_id": attempt_id,
            "share_code": share_code,
            "emoji_grid": emoji_grid,
            "share_text": share_text,
            "template_type": template_type
        }

        supabase.table("astrowordle_shares").insert(share_record).execute()

        # Update attempt share count
        supabase.table("astrowordle_user_attempts") \
            .update({"has_shared": True, "share_count": (attempt.data.get("share_count", 0) + 1)}) \
            .eq("id", attempt_id) \
            .execute()

        return {
            "success": True,
            "data": {
                "emoji_grid": emoji_grid,
                "share_text": share_text,
                "share_code": share_code
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating share: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate share: {str(e)}"
        )


# ============================================================================
# FRIEND CHALLENGES
# ============================================================================

@router.post("/challenge-friend")
async def challenge_friend(
    friend_user_id: str,
    attempt_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Challenge a friend to beat your score

    Request:
        - friend_user_id: UUID
        - attempt_id: UUID (your attempt to challenge with)

    Returns:
        - challenge_id: UUID
        - message: str
    """
    try:
        supabase = get_supabase_client()
        user_id = current_user["sub"]

        # Verify friendship
        friendship = supabase.table("friend_connections") \
            .select("*") \
            .eq("user_id", user_id) \
            .eq("friend_user_id", friend_user_id) \
            .eq("status", "accepted") \
            .execute()

        if not friendship.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not friends with this user"
            )

        # Get attempt
        attempt = supabase.table("astrowordle_user_attempts") \
            .select("*, challenge:astrowordle_daily_challenges(*)") \
            .eq("id", attempt_id) \
            .eq("user_id", user_id) \
            .single() \
            .execute()

        if not attempt.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attempt not found"
            )

        # Create friend challenge
        challenge_data = {
            "challenger_user_id": user_id,
            "challenged_user_id": friend_user_id,
            "challenge_id": attempt.data["challenge_id"],
            "challenger_score": attempt.data.get("score", 0),
            "challenger_guesses": attempt.data.get("num_guesses", 0)
        }

        result = supabase.table("astrowordle_friend_challenges") \
            .insert(challenge_data) \
            .execute()

        return {
            "success": True,
            "data": {
                "challenge_id": result.data[0]["id"] if result.data else None,
                "message": "Challenge sent! Your friend will be notified."
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating friend challenge: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create challenge: {str(e)}"
        )


@router.get("/my-challenges")
async def get_my_challenges(
    status_filter: str = "all",  # all, pending, completed
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get challenges sent to or by the current user

    Query params:
        - status_filter: "all", "pending", "completed"

    Returns list of challenges with details
    """
    try:
        supabase = get_supabase_client()
        user_id = current_user["sub"]

        # Get challenges (both sent and received)
        query = supabase.table("astrowordle_friend_challenges") \
            .select("*") \
            .or_(f"challenger_user_id.eq.{user_id},challenged_user_id.eq.{user_id}")

        if status_filter == "pending":
            query = query.eq("has_responded", False)
        elif status_filter == "completed":
            query = query.eq("has_responded", True)

        challenges = query.order("created_at", desc=True).execute()

        return {
            "success": True,
            "data": challenges.data or []
        }

    except Exception as e:
        logger.error(f"Error getting challenges: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get challenges: {str(e)}"
        )
