"""
AstroTwin Service
Handles chart similarity search, circle management, and pattern discovery
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, date
from app.services.supabase_service import SupabaseService
from app.services.chart_vectorization_service import ChartVectorizationService
import logging

logger = logging.getLogger(__name__)


class AstroTwinService:
    """Main service for AstroTwin Circles feature"""

    def __init__(self):
        self.supabase = SupabaseService()
        self.vectorizer = ChartVectorizationService()

    # =========================================================================
    # CHART VECTORIZATION & DISCOVERY
    # =========================================================================

    async def enable_discovery(
        self,
        user_id: str,
        profile_id: str,
        privacy_opt_in: bool = True,
        visible_in_search: bool = True,
        allow_pattern_learning: bool = False
    ) -> Dict[str, Any]:
        """
        Enable AstroTwin discovery for a user's profile
        Generates and stores chart vector
        """
        try:
            # Get profile and chart data
            profile = await self.supabase.select(
                "profiles",
                filters={"id": profile_id, "user_id": user_id}
            )

            if not profile:
                raise ValueError("Profile not found")

            profile_data = profile[0]

            # Get chart data
            chart = await self.supabase.select(
                "charts",
                filters={"profile_id": profile_id}
            )

            if not chart:
                raise ValueError("Chart not found. Please generate chart first.")

            chart_data = chart[0]

            # Encode chart to vector
            vector, metadata = self.vectorizer.encode_chart(chart_data, profile_data)

            # Store in database
            vector_record = {
                "profile_id": profile_id,
                "user_id": user_id,
                "chart_vector": vector,  # pgvector will handle this
                "feature_metadata": metadata,
                "privacy_opt_in": privacy_opt_in,
                "visible_in_search": visible_in_search,
                "allow_pattern_learning": allow_pattern_learning,
                "vectorization_version": "1.0"
            }

            # Upsert (insert or update)
            existing = await self.supabase.select(
                "chart_vectors",
                filters={"profile_id": profile_id}
            )

            if existing:
                result = await self.supabase.update(
                    "chart_vectors",
                    data=vector_record,
                    filters={"profile_id": profile_id}
                )
            else:
                result = await self.supabase.insert("chart_vectors", vector_record)

            logger.info(f"Enabled discovery for profile {profile_id}")

            return {
                "success": True,
                "message": "Discovery enabled successfully",
                "metadata": metadata
            }

        except Exception as e:
            logger.error(f"Failed to enable discovery: {str(e)}")
            raise

    async def find_twins(
        self,
        user_id: str,
        similarity_threshold: float = 0.3,
        limit: int = 100,
        filter_by: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Find AstroTwins for a user using vector similarity search
        """
        try:
            # Get user's chart vector
            user_vector = await self.supabase.select(
                "chart_vectors",
                filters={"user_id": user_id}
            )

            if not user_vector:
                raise ValueError("User has not enabled discovery. Please enable first.")

            user_vector_data = user_vector[0]
            user_chart_vector = user_vector_data["chart_vector"]
            user_metadata = user_vector_data["feature_metadata"]

            # Use custom SQL function for similarity search
            # This leverages pgvector's <=> operator
            query = f"""
                SELECT
                    profile_id,
                    user_id,
                    feature_metadata,
                    (1 - (chart_vector <=> '{user_chart_vector}'::vector))::DECIMAL AS similarity_score
                FROM chart_vectors
                WHERE user_id != '{user_id}'
                  AND privacy_opt_in = true
                  AND visible_in_search = true
                  AND (chart_vector <=> '{user_chart_vector}'::vector) < {similarity_threshold}
                ORDER BY chart_vector <=> '{user_chart_vector}'::vector
                LIMIT {limit};
            """

            # Execute raw SQL (Supabase REST API doesn't support vector ops directly)
            # For now, we'll use a simpler approach - get all eligible users and compute similarity in Python
            # In production, use Supabase Edge Functions or direct PostgreSQL connection

            all_vectors = await self.supabase.select(
                "chart_vectors",
                filters={
                    "privacy_opt_in": True,
                    "visible_in_search": True
                }
            )

            # Filter out current user
            other_vectors = [v for v in all_vectors if v["user_id"] != user_id]

            # Compute similarities
            matches = []
            for other in other_vectors:
                other_vector = other["chart_vector"]
                similarity = self.vectorizer.calculate_similarity(
                    user_chart_vector,
                    other_vector
                )

                # Convert similarity to distance for threshold comparison
                distance = 1 - similarity

                if distance < similarity_threshold:
                    # Extract shared features
                    shared_features = self.vectorizer.extract_shared_features(
                        user_metadata,
                        other["feature_metadata"]
                    )

                    matches.append({
                        "profile_id": other["profile_id"],
                        "similarity_score": round(similarity, 3),
                        "feature_metadata": other["feature_metadata"],
                        "shared_features": shared_features
                    })

            # Sort by similarity descending
            matches.sort(key=lambda x: x["similarity_score"], reverse=True)

            # Apply limit
            matches = matches[:limit]

            logger.info(f"Found {len(matches)} AstroTwins for user {user_id}")

            return {
                "matches": matches,
                "total_count": len(matches),
                "your_features": user_metadata
            }

        except Exception as e:
            logger.error(f"Failed to find twins: {str(e)}")
            raise

    # =========================================================================
    # CIRCLE MANAGEMENT
    # =========================================================================

    async def create_circle(
        self,
        user_id: str,
        circle_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new AstroTwin circle"""
        try:
            circle_record = {
                "creator_user_id": user_id,
                **circle_data
            }

            result = await self.supabase.insert("astrotwin_circles", circle_record)

            if result:
                circle = result[0]
                # Auto-join creator as admin
                await self._add_member(
                    circle_id=circle["id"],
                    user_id=user_id,
                    role="admin",
                    auto_approve=True
                )

                logger.info(f"Created circle {circle['id']} by user {user_id}")
                return circle

            raise ValueError("Failed to create circle")

        except Exception as e:
            logger.error(f"Failed to create circle: {str(e)}")
            raise

    async def get_circles(
        self,
        user_id: str,
        circle_type: Optional[str] = None,
        is_private: Optional[bool] = None
    ) -> Dict[str, Any]:
        """List circles (public circles + user's circles)"""
        try:
            filters = {}

            if circle_type:
                filters["circle_type"] = circle_type

            # Get public circles
            public_filters = {**filters, "is_private": False}
            public_circles = await self.supabase.select(
                "astrotwin_circles",
                filters=public_filters
            )

            # Get user's circles (member or creator)
            user_memberships = await self.supabase.select(
                "circle_memberships",
                filters={"user_id": user_id, "join_status": "active"}
            )

            user_circle_ids = [m["circle_id"] for m in user_memberships]

            # Combine results
            all_circles = public_circles or []

            if user_circle_ids:
                # Get user's private circles
                user_private_circles = await self.supabase.select(
                    "astrotwin_circles",
                    filters={"id": {"in": user_circle_ids}}
                )

                # Merge (avoid duplicates)
                existing_ids = {c["id"] for c in all_circles}
                for circle in (user_private_circles or []):
                    if circle["id"] not in existing_ids:
                        all_circles.append(circle)

            # Add user's role and status
            membership_map = {m["circle_id"]: m for m in user_memberships}

            for circle in all_circles:
                circle_id = circle["id"]
                if circle_id in membership_map:
                    membership = membership_map[circle_id]
                    circle["user_role"] = membership["role"]
                    circle["user_join_status"] = membership["join_status"]

            return {
                "circles": all_circles,
                "total_count": len(all_circles)
            }

        except Exception as e:
            logger.error(f"Failed to get circles: {str(e)}")
            raise

    async def get_circle_by_id(self, circle_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get circle details"""
        try:
            circles = await self.supabase.select(
                "astrotwin_circles",
                filters={"id": circle_id}
            )

            if not circles:
                return None

            circle = circles[0]

            # Check access permissions
            if circle["is_private"]:
                # Check if user is a member
                membership = await self.supabase.select(
                    "circle_memberships",
                    filters={"circle_id": circle_id, "user_id": user_id}
                )

                if not membership:
                    # User is not a member
                    return None

                # Add user's role
                circle["user_role"] = membership[0]["role"]
                circle["user_join_status"] = membership[0]["join_status"]

            return circle

        except Exception as e:
            logger.error(f"Failed to get circle: {str(e)}")
            raise

    async def join_circle(
        self,
        circle_id: str,
        user_id: str,
        profile_id: Optional[str] = None,
        share_outcomes: bool = False
    ) -> Dict[str, Any]:
        """Request to join or auto-join a circle"""
        try:
            # Get circle
            circle = await self.get_circle_by_id(circle_id, user_id)
            if not circle:
                raise ValueError("Circle not found or access denied")

            # Check if already a member
            existing = await self.supabase.select(
                "circle_memberships",
                filters={"circle_id": circle_id, "user_id": user_id}
            )

            if existing:
                return {"message": "Already a member or pending"}

            # Determine join status
            join_status = "pending" if circle["requires_approval"] else "active"

            membership = {
                "circle_id": circle_id,
                "user_id": user_id,
                "profile_id": profile_id,
                "role": "member",
                "join_status": join_status,
                "shared_outcomes": share_outcomes
            }

            result = await self.supabase.insert("circle_memberships", membership)

            if result:
                logger.info(f"User {user_id} joined circle {circle_id} ({join_status})")
                return {
                    "success": True,
                    "message": f"Join request {join_status}",
                    "membership": result[0]
                }

            raise ValueError("Failed to join circle")

        except Exception as e:
            logger.error(f"Failed to join circle: {str(e)}")
            raise

    async def leave_circle(self, circle_id: str, user_id: str) -> Dict[str, Any]:
        """Leave a circle"""
        try:
            await self.supabase.update(
                "circle_memberships",
                data={"join_status": "left", "left_at": datetime.utcnow().isoformat()},
                filters={"circle_id": circle_id, "user_id": user_id}
            )

            logger.info(f"User {user_id} left circle {circle_id}")

            return {"success": True, "message": "Left circle successfully"}

        except Exception as e:
            logger.error(f"Failed to leave circle: {str(e)}")
            raise

    async def _add_member(
        self,
        circle_id: str,
        user_id: str,
        role: str = "member",
        auto_approve: bool = False
    ):
        """Internal: Add a member to circle"""
        membership = {
            "circle_id": circle_id,
            "user_id": user_id,
            "role": role,
            "join_status": "active" if auto_approve else "pending"
        }

        await self.supabase.insert("circle_memberships", membership)

    # =========================================================================
    # LIFE OUTCOMES
    # =========================================================================

    async def report_outcome(
        self,
        user_id: str,
        outcome_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Report a life outcome for pattern analysis"""
        try:
            # If dasha/transit context not provided, fetch current context
            if not outcome_data.get("dasha_context"):
                # Get user's profile and chart
                profile_id = outcome_data.get("profile_id")
                if profile_id:
                    chart = await self.supabase.select(
                        "charts",
                        filters={"profile_id": profile_id}
                    )

                    if chart:
                        outcome_data["dasha_context"] = chart[0].get("current_dasha")

            outcome_record = {
                "user_id": user_id,
                **outcome_data
            }

            result = await self.supabase.insert("life_outcomes", outcome_record)

            if result:
                logger.info(f"Recorded outcome for user {user_id}: {outcome_data.get('outcome_type')}")
                return result[0]

            raise ValueError("Failed to record outcome")

        except Exception as e:
            logger.error(f"Failed to report outcome: {str(e)}")
            raise

    async def get_user_outcomes(
        self,
        user_id: str,
        outcome_type: Optional[str] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Get user's reported outcomes"""
        try:
            filters = {"user_id": user_id}

            if outcome_type:
                filters["outcome_type"] = outcome_type

            outcomes = await self.supabase.select(
                "life_outcomes",
                filters=filters,
                order="created_at.desc",
                limit=limit
            )

            return {
                "outcomes": outcomes or [],
                "total_count": len(outcomes or [])
            }

        except Exception as e:
            logger.error(f"Failed to get outcomes: {str(e)}")
            raise

    # =========================================================================
    # STATS
    # =========================================================================

    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user's AstroTwin statistics"""
        try:
            # Check if discovery enabled
            user_vector = await self.supabase.select(
                "chart_vectors",
                filters={"user_id": user_id}
            )

            discovery_enabled = len(user_vector or []) > 0

            # Count circles joined
            memberships = await self.supabase.select(
                "circle_memberships",
                filters={"user_id": user_id, "join_status": "active"}
            )

            circles_joined = len(memberships or [])

            # Count outcomes reported
            outcomes = await self.supabase.select(
                "life_outcomes",
                filters={"user_id": user_id}
            )

            outcomes_reported = len(outcomes or [])

            # Find total twins (simplified - actual count would use vector search)
            total_twins_found = 0
            most_similar_twin_score = None

            if discovery_enabled:
                # This is a simplified version - in production, use actual vector search
                twins_result = await self.find_twins(user_id, similarity_threshold=0.3, limit=10)
                total_twins_found = twins_result["total_count"]
                if twins_result["matches"]:
                    most_similar_twin_score = twins_result["matches"][0]["similarity_score"]

            return {
                "total_twins_found": total_twins_found,
                "circles_joined": circles_joined,
                "outcomes_reported": outcomes_reported,
                "patterns_matched": 0,  # TODO: Implement pattern matching
                "discovery_enabled": discovery_enabled,
                "most_similar_twin_score": most_similar_twin_score
            }

        except Exception as e:
            logger.error(f"Failed to get user stats: {str(e)}")
            raise
