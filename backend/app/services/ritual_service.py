"""
Ritual Service - Handles guided Vedic ritual templates and user sessions

This service provides:
- Ritual template management (CRUD operations)
- User ritual session tracking
- Progress management
- History and statistics
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from app.core.supabase_client import SupabaseClient


class RitualService:
    """Service for managing Vedic ritual templates and user sessions"""

    def __init__(self, supabase_client: SupabaseClient):
        self.supabase = supabase_client

    # ========================================================================
    # RITUAL TEMPLATE METHODS
    # ========================================================================

    async def get_all_rituals(
        self,
        limit: Optional[int] = None,
        offset: int = 0,
        order_by: str = "created_at.desc"
    ) -> List[Dict[str, Any]]:
        """
        Get all available ritual templates.

        Args:
            limit: Maximum number of rituals to return
            offset: Number of rituals to skip (for pagination)
            order_by: Field to order by (default: created_at.desc)

        Returns:
            List of ritual template dictionaries
        """
        rituals = await self.supabase.select(
            "ritual_templates",
            order=order_by,
            limit=limit,
            offset=offset
        )
        return rituals if rituals else []

    async def get_ritual_by_id(self, ritual_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get a specific ritual template by ID.

        Args:
            ritual_id: UUID of the ritual template

        Returns:
            Ritual template dictionary or None if not found
        """
        rituals = await self.supabase.select(
            "ritual_templates",
            filters={"id": str(ritual_id)}
        )
        return rituals[0] if rituals else None

    async def get_rituals_by_category(
        self,
        category: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get rituals filtered by category.

        Args:
            category: Category filter ('daily', 'special', 'remedial', 'festival', 'meditation')
            limit: Maximum number of rituals to return

        Returns:
            List of ritual template dictionaries
        """
        rituals = await self.supabase.select(
            "ritual_templates",
            filters={"category": category},
            order="name.asc",
            limit=limit
        )
        return rituals if rituals else []

    async def get_rituals_by_deity(
        self,
        deity: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get rituals filtered by deity.

        Args:
            deity: Deity name (e.g., 'Ganesha', 'Shiva', 'Lakshmi')
            limit: Maximum number of rituals to return

        Returns:
            List of ritual template dictionaries
        """
        rituals = await self.supabase.select(
            "ritual_templates",
            filters={"deity": deity},
            order="name.asc",
            limit=limit
        )
        return rituals if rituals else []

    async def get_rituals_by_difficulty(
        self,
        difficulty: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get rituals filtered by difficulty level.

        Args:
            difficulty: Difficulty level ('beginner', 'intermediate', 'advanced')
            limit: Maximum number of rituals to return

        Returns:
            List of ritual template dictionaries
        """
        rituals = await self.supabase.select(
            "ritual_templates",
            filters={"difficulty": difficulty},
            order="name.asc",
            limit=limit
        )
        return rituals if rituals else []

    async def search_rituals(
        self,
        query: str,
        limit: Optional[int] = 20
    ) -> List[Dict[str, Any]]:
        """
        Search rituals by name or description.

        Args:
            query: Search query string
            limit: Maximum number of results

        Returns:
            List of matching ritual template dictionaries
        """
        # Note: Supabase REST API supports text search with ilike
        # For more advanced search, we'll use ilike pattern matching
        search_pattern = f"%{query}%"

        # Search in name field
        rituals = await self.supabase.select(
            "ritual_templates",
            filters={"name": f"ilike.{search_pattern}"},
            limit=limit
        )

        return rituals if rituals else []

    # ========================================================================
    # USER RITUAL SESSION METHODS
    # ========================================================================

    async def start_ritual_session(
        self,
        user_id: UUID,
        ritual_template_id: UUID,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Start a new ritual session for a user.

        Args:
            user_id: UUID of the user
            ritual_template_id: UUID of the ritual template
            notes: Optional notes from user

        Returns:
            Created session dictionary
        """
        # First, get the ritual template to know total steps
        ritual = await self.get_ritual_by_id(ritual_template_id)
        if not ritual:
            raise ValueError(f"Ritual template {ritual_template_id} not found")

        # Count steps from the steps JSONB array
        total_steps = len(ritual.get('steps', []))
        if total_steps == 0:
            raise ValueError(f"Ritual template {ritual_template_id} has no steps")

        # Create new session
        session_data = {
            "user_id": str(user_id),
            "ritual_template_id": str(ritual_template_id),
            "current_step": 1,
            "total_steps": total_steps,
            "status": "in_progress",
            "notes": notes,
            "started_at": datetime.utcnow().isoformat()
        }

        session = await self.supabase.insert("user_ritual_sessions", session_data)
        return session

    async def update_progress(
        self,
        session_id: UUID,
        user_id: UUID,
        current_step: int
    ) -> Dict[str, Any]:
        """
        Update the current step of a ritual session.

        Args:
            session_id: UUID of the session
            user_id: UUID of the user (for authorization)
            current_step: New current step number

        Returns:
            Updated session dictionary
        """
        update_data = {
            "current_step": current_step,
            "updated_at": datetime.utcnow().isoformat()
        }

        sessions = await self.supabase.update(
            "user_ritual_sessions",
            filters={"id": str(session_id), "user_id": str(user_id)},
            data=update_data
        )

        if not sessions:
            raise ValueError(f"Session {session_id} not found or not authorized")

        return sessions[0]

    async def pause_ritual(
        self,
        session_id: UUID,
        user_id: UUID
    ) -> Dict[str, Any]:
        """
        Pause a ritual session.

        Args:
            session_id: UUID of the session
            user_id: UUID of the user (for authorization)

        Returns:
            Updated session dictionary
        """
        update_data = {
            "status": "paused",
            "updated_at": datetime.utcnow().isoformat()
        }

        sessions = await self.supabase.update(
            "user_ritual_sessions",
            filters={"id": str(session_id), "user_id": str(user_id)},
            data=update_data
        )

        if not sessions:
            raise ValueError(f"Session {session_id} not found or not authorized")

        return sessions[0]

    async def resume_ritual(
        self,
        session_id: UUID,
        user_id: UUID
    ) -> Dict[str, Any]:
        """
        Resume a paused ritual session.

        Args:
            session_id: UUID of the session
            user_id: UUID of the user (for authorization)

        Returns:
            Updated session dictionary
        """
        update_data = {
            "status": "in_progress",
            "updated_at": datetime.utcnow().isoformat()
        }

        sessions = await self.supabase.update(
            "user_ritual_sessions",
            filters={"id": str(session_id), "user_id": str(user_id), "status": "paused"},
            data=update_data
        )

        if not sessions:
            raise ValueError(f"Session {session_id} not found, not authorized, or not paused")

        return sessions[0]

    async def complete_ritual(
        self,
        session_id: UUID,
        user_id: UUID,
        rating: Optional[int] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Mark a ritual session as completed.

        Args:
            session_id: UUID of the session
            user_id: UUID of the user (for authorization)
            rating: Optional rating (1-5 stars)
            notes: Optional completion notes

        Returns:
            Updated session dictionary
        """
        update_data = {
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }

        if rating is not None:
            if rating < 1 or rating > 5:
                raise ValueError("Rating must be between 1 and 5")
            update_data["rating"] = rating

        if notes is not None:
            update_data["notes"] = notes

        sessions = await self.supabase.update(
            "user_ritual_sessions",
            filters={"id": str(session_id), "user_id": str(user_id)},
            data=update_data
        )

        if not sessions:
            raise ValueError(f"Session {session_id} not found or not authorized")

        return sessions[0]

    async def abandon_ritual(
        self,
        session_id: UUID,
        user_id: UUID
    ) -> Dict[str, Any]:
        """
        Mark a ritual session as abandoned.

        Args:
            session_id: UUID of the session
            user_id: UUID of the user (for authorization)

        Returns:
            Updated session dictionary
        """
        update_data = {
            "status": "abandoned",
            "updated_at": datetime.utcnow().isoformat()
        }

        sessions = await self.supabase.update(
            "user_ritual_sessions",
            filters={"id": str(session_id), "user_id": str(user_id)},
            data=update_data
        )

        if not sessions:
            raise ValueError(f"Session {session_id} not found or not authorized")

        return sessions[0]

    async def get_session_by_id(
        self,
        session_id: UUID,
        user_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """
        Get a specific ritual session by ID.

        Args:
            session_id: UUID of the session
            user_id: UUID of the user (for authorization)

        Returns:
            Session dictionary or None if not found
        """
        sessions = await self.supabase.select(
            "user_ritual_sessions",
            filters={"id": str(session_id), "user_id": str(user_id)}
        )
        return sessions[0] if sessions else None

    async def get_user_ritual_history(
        self,
        user_id: UUID,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get user's ritual session history.

        Args:
            user_id: UUID of the user
            status: Optional status filter ('in_progress', 'completed', 'paused', 'abandoned')
            limit: Maximum number of sessions to return
            offset: Number of sessions to skip (for pagination)

        Returns:
            List of session dictionaries
        """
        filters = {"user_id": str(user_id)}
        if status:
            filters["status"] = status

        sessions = await self.supabase.select(
            "user_ritual_sessions",
            filters=filters,
            order="started_at.desc",
            limit=limit,
            offset=offset
        )

        return sessions if sessions else []

    async def get_user_stats(self, user_id: UUID) -> Dict[str, Any]:
        """
        Get user's ritual practice statistics.

        Args:
            user_id: UUID of the user

        Returns:
            Dictionary with statistics (total, completed, in_progress, average_rating, etc.)
        """
        # Get all sessions
        all_sessions = await self.get_user_ritual_history(user_id, limit=1000)

        # Calculate statistics
        total_sessions = len(all_sessions)
        completed = [s for s in all_sessions if s.get('status') == 'completed']
        in_progress = [s for s in all_sessions if s.get('status') == 'in_progress']
        paused = [s for s in all_sessions if s.get('status') == 'paused']
        abandoned = [s for s in all_sessions if s.get('status') == 'abandoned']

        # Calculate average rating
        ratings = [s.get('rating') for s in completed if s.get('rating')]
        avg_rating = sum(ratings) / len(ratings) if ratings else None

        # Calculate completion rate
        completion_rate = (len(completed) / total_sessions * 100) if total_sessions > 0 else 0

        return {
            "total_sessions": total_sessions,
            "completed": len(completed),
            "in_progress": len(in_progress),
            "paused": len(paused),
            "abandoned": len(abandoned),
            "completion_rate": round(completion_rate, 2),
            "average_rating": round(avg_rating, 2) if avg_rating else None
        }

    async def delete_session(
        self,
        session_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Delete a ritual session.

        Args:
            session_id: UUID of the session
            user_id: UUID of the user (for authorization)

        Returns:
            True if deleted successfully
        """
        await self.supabase.delete(
            "user_ritual_sessions",
            filters={"id": str(session_id), "user_id": str(user_id)}
        )
        return True
