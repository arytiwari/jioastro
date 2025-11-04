"""
Supabase Database Service
Handles all database operations via Supabase REST API instead of direct PostgreSQL connections
"""

from typing import List, Dict, Any, Optional
from supabase import create_client, Client
from app.core.config import settings
from datetime import datetime
import uuid


class SupabaseService:
    """Service for database operations using Supabase REST API"""

    def __init__(self):
        """Initialize Supabase client with service role key (bypasses RLS for backend operations)"""
        # Use service role key for backend operations - this bypasses Row Level Security
        supabase_key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY

        if not supabase_key:
            raise ValueError("SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY must be set")

        self.client: Client = create_client(
            settings.SUPABASE_URL,
            supabase_key
        )

        key_type = "service_role" if settings.SUPABASE_SERVICE_ROLE_KEY else "anon"
        print(f"✅ Supabase REST API client initialized (using {key_type} key)")

    # Profile operations
    async def create_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new profile"""
        data = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            **profile_data,
            "created_at": datetime.utcnow().isoformat()
        }

        # If this is primary, unset other primary profiles
        if data.get("is_primary"):
            self.client.table("profiles").update({"is_primary": False}).eq("user_id", user_id).execute()

        response = self.client.table("profiles").insert(data).execute()
        return response.data[0] if response.data else None

    async def get_profiles(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all profiles for a user"""
        response = self.client.table("profiles").select("*").eq("user_id", user_id).order("is_primary", desc=True).order("created_at", desc=True).execute()
        return response.data if response.data else []

    async def get_profile(self, profile_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific profile"""
        response = self.client.table("profiles").select("*").eq("id", profile_id).eq("user_id", user_id).execute()
        return response.data[0] if response.data else None

    async def update_profile(self, profile_id: str, user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a profile"""
        # If setting as primary, unset others
        if update_data.get("is_primary"):
            self.client.table("profiles").update({"is_primary": False}).eq("user_id", user_id).execute()

        response = self.client.table("profiles").update(update_data).eq("id", profile_id).eq("user_id", user_id).execute()
        return response.data[0] if response.data else None

    async def delete_profile(self, profile_id: str, user_id: str) -> bool:
        """Delete a profile"""
        response = self.client.table("profiles").delete().eq("id", profile_id).eq("user_id", user_id).execute()
        return len(response.data) > 0 if response.data else False

    # Chart operations
    async def create_chart(self, chart_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a chart"""
        data = {
            "id": str(uuid.uuid4()),
            **chart_data,
            "calculated_at": datetime.utcnow().isoformat()
        }
        response = self.client.table("charts").insert(data).execute()
        return response.data[0] if response.data else None

    async def get_chart(self, profile_id: str, chart_type: str) -> Optional[Dict[str, Any]]:
        """Get a chart"""
        response = self.client.table("charts").select("*").eq("profile_id", profile_id).eq("chart_type", chart_type).execute()
        return response.data[0] if response.data else None

    async def delete_chart(self, profile_id: str, chart_type: str) -> bool:
        """Delete a chart"""
        response = self.client.table("charts").delete().eq("profile_id", profile_id).eq("chart_type", chart_type).execute()
        return len(response.data) > 0 if response.data else False

    # Query operations
    async def create_query(self, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a query"""
        data = {
            "id": str(uuid.uuid4()),
            **query_data,
            "created_at": datetime.utcnow().isoformat()
        }
        response = self.client.table("queries").insert(data).execute()
        return response.data[0] if response.data else None

    async def get_queries(self, user_id: str, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Get queries for a user"""
        response = self.client.table("queries").select("*, responses(*)").eq("user_id", user_id).order("created_at", desc=True).range(offset, offset + limit - 1).execute()
        print(f"📊 Supabase get_queries raw response: {response.data[:2] if response.data else []}")
        return response.data if response.data else []

    async def get_query(self, query_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific query"""
        response = self.client.table("queries").select("*, responses(*)").eq("id", query_id).eq("user_id", user_id).execute()
        return response.data[0] if response.data else None

    # Response operations
    async def create_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a response"""
        data = {
            "id": str(uuid.uuid4()),
            **response_data,
            "created_at": datetime.utcnow().isoformat()
        }
        response = self.client.table("responses").insert(data).execute()
        return response.data[0] if response.data else None

    # Feedback operations
    async def create_feedback(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create feedback"""
        data = {
            "id": str(uuid.uuid4()),
            **feedback_data,
            "created_at": datetime.utcnow().isoformat()
        }
        response = self.client.table("feedback").insert(data).execute()
        return response.data[0] if response.data else None

    async def get_feedback_for_response(self, response_id: str) -> Optional[Dict[str, Any]]:
        """Get feedback for a response"""
        response = self.client.table("feedback").select("*").eq("response_id", response_id).execute()
        return response.data[0] if response.data else None

    async def get_feedback_stats(self) -> Dict[str, Any]:
        """Get feedback statistics"""
        # Get all feedback
        response = self.client.table("feedback").select("rating").execute()

        if not response.data:
            return {
                "total_feedback": 0,
                "average_rating": 0.0,
                "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            }

        ratings = [f["rating"] for f in response.data]
        total = len(ratings)
        avg_rating = sum(ratings) / total if total > 0 else 0.0

        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for rating in ratings:
            distribution[rating] = distribution.get(rating, 0) + 1

        return {
            "total_feedback": total,
            "average_rating": round(avg_rating, 2),
            "rating_distribution": distribution
        }


# Singleton instance
supabase_service = SupabaseService()
