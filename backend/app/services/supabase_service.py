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

    async def get_profile(self, profile_id: str, user_id: str = None) -> Optional[Dict[str, Any]]:
        """Get a specific profile - user_id is optional for admin access"""
        query = self.client.table("profiles").select("*").eq("id", profile_id)
        if user_id:
            query = query.eq("user_id", user_id)
        response = query.execute()
        return response.data[0] if response.data else None

    async def update_profile(self, profile_id: str, user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a profile"""
        # If setting as primary, unset others
        if update_data.get("is_primary"):
            self.client.table("profiles").update({"is_primary": False}).eq("user_id", user_id).execute()

        response = self.client.table("profiles").update(update_data).eq("id", profile_id).eq("user_id", user_id).execute()
        return response.data[0] if response.data else None

    async def delete_profile(self, profile_id: str, user_id: str = None) -> bool:
        """Delete a profile - user_id is optional for admin deletion"""
        query = self.client.table("profiles").delete().eq("id", profile_id)
        if user_id:
            query = query.eq("user_id", user_id)
        response = query.execute()
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

    # Numerology operations
    async def get_numerology_profiles(self, user_id: str, profile_id: str = None) -> List[Dict[str, Any]]:
        """Get numerology profiles for a user, optionally filtered by birth profile"""
        query = self.client.table("numerology_profiles").select("*").eq("user_id", user_id)

        if profile_id:
            query = query.eq("profile_id", profile_id)

        query = query.order("created_at", desc=True)
        response = query.execute()
        return response.data if response.data else []

    # Admin operations
    async def get_admin_by_username_or_email(self, username_or_email: str) -> Optional[Dict[str, Any]]:
        """Get admin user by username or email"""
        try:
            # Try by username first
            response = self.client.table("admin_users").select("*").eq("username", username_or_email).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]

            # Try by email if username didn't match
            response = self.client.table("admin_users").select("*").eq("email", username_or_email).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]

            return None
        except Exception as e:
            print(f"Error fetching admin user: {str(e)}")
            return None

    async def get_admin_by_id(self, admin_id: str) -> Optional[Dict[str, Any]]:
        """Get admin user by ID"""
        try:
            response = self.client.table("admin_users").select("*").eq("id", admin_id).execute()
            return response.data[0] if response.data and len(response.data) > 0 else None
        except Exception as e:
            print(f"Error fetching admin user by ID: {str(e)}")
            return None

    async def update_admin_last_login(self, admin_id: str) -> bool:
        """Update admin last login timestamp"""
        try:
            self.client.table("admin_users").update({
                "last_login": datetime.utcnow().isoformat()
            }).eq("id", admin_id).execute()
            return True
        except Exception as e:
            print(f"Error updating admin last login: {str(e)}")
            return False

    async def create_admin_user(self, admin_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new admin user"""
        try:
            data = {
                "id": str(uuid.uuid4()),
                **admin_data,
                "created_at": datetime.utcnow().isoformat()
            }
            response = self.client.table("admin_users").insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating admin user: {str(e)}")
            return None

    async def get_all_profiles_admin(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all user profiles (admin only)"""
        try:
            response = self.client.table("profiles").select("*").range(offset, offset + limit - 1).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error fetching all profiles: {str(e)}")
            return []

    async def get_knowledge_documents(self, document_type: Optional[str] = None, limit: int = 50, offset: int = 0) -> tuple[List[Dict[str, Any]], int]:
        """Get knowledge documents with optional filtering"""
        try:
            query = self.client.table("knowledge_documents").select("*", count="exact")

            if document_type:
                query = query.eq("document_type", document_type)

            query = query.range(offset, offset + limit - 1).order("created_at", desc=True)
            response = query.execute()

            total = response.count if hasattr(response, 'count') else len(response.data)
            return response.data if response.data else [], total
        except Exception as e:
            print(f"Error fetching knowledge documents: {str(e)}")
            return [], 0

    async def get_knowledge_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific knowledge document"""
        try:
            response = self.client.table("knowledge_documents").select("*").eq("id", document_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error fetching knowledge document: {str(e)}")
            return None

    async def create_knowledge_document(self, document_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new knowledge document"""
        try:
            data = {
                "id": str(uuid.uuid4()),
                **document_data,
                "created_at": datetime.utcnow().isoformat()
            }
            response = self.client.table("knowledge_documents").insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating knowledge document: {str(e)}")
            return None

    async def update_knowledge_document(self, document_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a knowledge document"""
        try:
            update_data["updated_at"] = datetime.utcnow().isoformat()
            response = self.client.table("knowledge_documents").update(update_data).eq("id", document_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating knowledge document: {str(e)}")
            return None

    async def delete_knowledge_document(self, document_id: str) -> bool:
        """Delete a knowledge document"""
        try:
            self.client.table("knowledge_documents").delete().eq("id", document_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting knowledge document: {str(e)}")
            return False

    # =========================================================================
    # GENERIC CRUD OPERATIONS (for new features like AstroTwin)
    # =========================================================================

    async def select(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
        order: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Generic SELECT operation via Supabase REST API

        Args:
            table: Table name
            filters: Dictionary of {column: value} for WHERE clauses
            order: Column name with optional .asc or .desc suffix (e.g., "created_at.desc")
            limit: Number of rows to return
            offset: Number of rows to skip

        Returns:
            List of matching rows
        """
        try:
            query = self.client.table(table).select("*")

            # Apply filters
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)

            # Apply ordering
            if order:
                if ".desc" in order:
                    col = order.replace(".desc", "")
                    query = query.order(col, desc=True)
                elif ".asc" in order:
                    col = order.replace(".asc", "")
                    query = query.order(col, desc=False)
                else:
                    query = query.order(order)

            # Apply pagination
            if limit:
                if offset:
                    query = query.range(offset, offset + limit - 1)
                else:
                    query = query.limit(limit)

            response = query.execute()
            return response.data if response.data else []

        except Exception as e:
            print(f"Error in select from {table}: {str(e)}")
            return []

    async def insert(
        self,
        table: str,
        data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generic INSERT operation via Supabase REST API

        Args:
            table: Table name
            data: Dictionary of column-value pairs to insert

        Returns:
            List containing the inserted row(s)
        """
        try:
            # Add UUID if not provided
            if "id" not in data:
                data["id"] = str(uuid.uuid4())

            # Add timestamp if not provided
            if "created_at" not in data:
                data["created_at"] = datetime.utcnow().isoformat()

            response = self.client.table(table).insert(data).execute()
            return response.data if response.data else []

        except Exception as e:
            print(f"Error in insert to {table}: {str(e)}")
            raise

    async def update(
        self,
        table: str,
        data: Dict[str, Any],
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generic UPDATE operation via Supabase REST API

        Args:
            table: Table name
            data: Dictionary of column-value pairs to update
            filters: Dictionary of {column: value} for WHERE clauses

        Returns:
            List containing the updated row(s)
        """
        try:
            # Add updated_at timestamp
            if "updated_at" not in data:
                data["updated_at"] = datetime.utcnow().isoformat()

            query = self.client.table(table).update(data)

            # Apply filters
            for key, value in filters.items():
                query = query.eq(key, value)

            response = query.execute()
            return response.data if response.data else []

        except Exception as e:
            print(f"Error in update to {table}: {str(e)}")
            raise

    async def delete(
        self,
        table: str,
        filters: Dict[str, Any]
    ) -> bool:
        """
        Generic DELETE operation via Supabase REST API

        Args:
            table: Table name
            filters: Dictionary of {column: value} for WHERE clauses

        Returns:
            True if rows were deleted, False otherwise
        """
        try:
            query = self.client.table(table).delete()

            # Apply filters
            for key, value in filters.items():
                query = query.eq(key, value)

            response = query.execute()
            return len(response.data) > 0 if response.data else False

        except Exception as e:
            print(f"Error in delete from {table}: {str(e)}")
            return False

    async def count(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        COUNT operation via Supabase REST API

        Args:
            table: Table name
            filters: Dictionary of {column: value} for WHERE clauses

        Returns:
            Number of matching records
        """
        try:
            query = self.client.table(table).select("id", count="exact")

            # Apply filters
            if filters:
                for key, value in filters.items():
                    if value is None:
                        query = query.is_(key, None)
                    else:
                        query = query.eq(key, value)

            response = query.execute()
            return response.count if hasattr(response, 'count') and response.count is not None else 0

        except Exception as e:
            print(f"Error in count from {table}: {str(e)}")
            return 0


# Singleton instance
supabase_service = SupabaseService()
