"""
Memory Service
Privacy-first memory system for contextual AI readings
Stores user preferences, event anchors, and reading history
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import hashlib
import json

from app.services.supabase_service import supabase_service


class MemoryType:
    """Memory type constants"""
    PREFERENCE = "preference"
    FEEDBACK = "feedback"
    CORRECTION = "correction"
    CONTEXT = "context"
    EVENT = "event"
    GOAL = "goal"
    QUESTION_HISTORY = "question_history"


class MemoryService:
    """Service for managing user memory and contextual information"""

    def __init__(self):
        """Initialize memory service"""
        self.client = supabase_service.client

    async def store_memory(
        self,
        user_id: str,
        memory_type: str,
        key: str,
        value: Any,
        profile_id: Optional[str] = None,
        source: Optional[str] = None,
        source_id: Optional[str] = None,
        confidence: float = 1.0
    ) -> Dict[str, Any]:
        """
        Store a memory entry

        Args:
            user_id: User ID
            memory_type: Type of memory (preference, feedback, context, etc.)
            key: Memory key
            value: Memory value (will be JSON serialized if dict/list)
            profile_id: Optional profile ID
            source: Source of memory
            source_id: Reference ID
            confidence: Confidence level (0-1)

        Returns:
            Created memory entry
        """
        # Serialize value if needed
        if isinstance(value, (dict, list)):
            value_str = json.dumps(value)
        else:
            value_str = str(value)

        memory_data = {
            "user_id": user_id,
            "profile_id": profile_id,
            "memory_type": memory_type,
            "key": key,
            "value": value_str,
            "confidence": confidence,
            "source": source,
            "source_id": source_id,
            "relevance_score": 1.0,
            "access_count": 0
        }

        # Try to insert, update if already exists
        try:
            result = self.client.from_("user_memory")\
                .upsert(memory_data)\
                .execute()

            return result.data[0] if result.data else {}

        except Exception as e:
            print(f"Error storing memory: {e}")
            raise

    async def get_memory(
        self,
        user_id: str,
        memory_type: Optional[str] = None,
        key: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve memories for a user

        Args:
            user_id: User ID
            memory_type: Optional memory type filter
            key: Optional specific key
            limit: Maximum number of results

        Returns:
            List of memory entries
        """
        query = self.client.from_("user_memory")\
            .select("*")\
            .eq("user_id", user_id)

        if memory_type:
            query = query.eq("memory_type", memory_type)

        if key:
            query = query.eq("key", key)

        query = query.order("relevance_score", desc=True)\
            .order("last_accessed_at", desc=True)\
            .limit(limit)

        result = query.execute()

        # Update access tracking
        if result.data:
            memory_ids = [m['id'] for m in result.data]
            self._update_access_tracking(memory_ids)

        return result.data

    async def get_relevant_context(
        self,
        user_id: str,
        profile_id: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get most relevant contextual memories for current reading

        Args:
            user_id: User ID
            profile_id: Optional profile ID
            limit: Maximum number of results

        Returns:
            List of relevant memories
        """
        query = self.client.from_("user_memory")\
            .select("*")\
            .eq("user_id", user_id)\
            .in_("memory_type", [MemoryType.CONTEXT, MemoryType.GOAL, MemoryType.PREFERENCE])

        if profile_id:
            query = query.eq("profile_id", profile_id)

        query = query.order("relevance_score", desc=True)\
            .limit(limit)

        result = query.execute()
        return result.data

    def _update_access_tracking(self, memory_ids: List[str]):
        """Update last_accessed_at and access_count for memories"""
        try:
            # Increment access count and update timestamp
            for memory_id in memory_ids:
                self.client.from_("user_memory")\
                    .update({
                        "last_accessed_at": datetime.utcnow().isoformat(),
                        "access_count": self.client.from_("user_memory")
                            .select("access_count")
                            .eq("id", memory_id)
                            .execute().data[0]['access_count'] + 1
                    })\
                    .eq("id", memory_id)\
                    .execute()
        except Exception as e:
            print(f"Warning: Failed to update access tracking: {e}")

    async def delete_memory(
        self,
        user_id: str,
        memory_id: Optional[str] = None,
        memory_type: Optional[str] = None,
        key: Optional[str] = None
    ) -> int:
        """
        Delete memories

        Args:
            user_id: User ID
            memory_id: Specific memory ID to delete
            memory_type: Delete all of this type
            key: Delete specific key

        Returns:
            Number of deleted entries
        """
        query = self.client.from_("user_memory")\
            .delete()\
            .eq("user_id", user_id)

        if memory_id:
            query = query.eq("id", memory_id)
        elif memory_type:
            query = query.eq("memory_type", memory_type)
        elif key:
            query = query.eq("key", key)

        result = query.execute()
        return len(result.data) if result.data else 0

    # ========================================================================
    # EVENT ANCHORS (for Birth Time Rectification)
    # ========================================================================

    async def store_event_anchor(
        self,
        user_id: str,
        profile_id: str,
        event_type: str,
        event_date: str,  # ISO format
        event_description: Optional[str] = None,
        event_significance: str = "medium",
        helps_rectify: bool = True
    ) -> Dict[str, Any]:
        """
        Store a major life event for birth time rectification

        Args:
            user_id: User ID
            profile_id: Profile ID
            event_type: Type of event (marriage, job_start, etc.)
            event_date: Date of event (YYYY-MM-DD)
            event_description: Description
            event_significance: very_high, high, medium, low
            helps_rectify: Whether this event helps rectification

        Returns:
            Created event anchor
        """
        event_data = {
            "user_id": user_id,
            "profile_id": profile_id,
            "event_type": event_type,
            "event_date": event_date,
            "event_description": event_description,
            "event_significance": event_significance,
            "helps_rectify": helps_rectify,
            "verified": False
        }

        result = self.client.from_("event_anchors")\
            .insert(event_data)\
            .execute()

        return result.data[0] if result.data else {}

    async def get_event_anchors(
        self,
        profile_id: str,
        helps_rectify_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get event anchors for a profile

        Args:
            profile_id: Profile ID
            helps_rectify_only: Only return anchors useful for rectification

        Returns:
            List of event anchors
        """
        query = self.client.from_("event_anchors")\
            .select("*")\
            .eq("profile_id", profile_id)

        if helps_rectify_only:
            query = query.eq("helps_rectify", True)

        query = query.order("event_date", desc=True)

        result = query.execute()
        return result.data

    async def update_event_anchor_correlation(
        self,
        anchor_id: str,
        correlation_strength: float,
        expected_dasha: Optional[str] = None,
        expected_transit: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update event anchor with astrological correlation data

        Args:
            anchor_id: Event anchor ID
            correlation_strength: How well this matches chart (0-1)
            expected_dasha: Expected dasha period
            expected_transit: Expected transit conditions

        Returns:
            Updated event anchor
        """
        update_data = {
            "correlation_strength": correlation_strength
        }

        if expected_dasha:
            update_data["expected_dasha"] = expected_dasha

        if expected_transit:
            update_data["expected_transit"] = expected_transit

        result = self.client.from_("event_anchors")\
            .update(update_data)\
            .eq("id", anchor_id)\
            .execute()

        return result.data[0] if result.data else {}

    # ========================================================================
    # READING SESSIONS (Caching)
    # ========================================================================

    def generate_canonical_hash(
        self,
        profile_id: str,
        domains: List[str],
        include_predictions: bool,
        prediction_window_months: int
    ) -> str:
        """
        Generate canonical hash for reading session

        Args:
            profile_id: Profile ID
            domains: Domains to analyze
            include_predictions: Whether predictions included
            prediction_window_months: Prediction window

        Returns:
            SHA256 hash string
        """
        # Sort domains for consistency
        sorted_domains = sorted(domains) if domains else []

        # Create hash input
        hash_input = f"{profile_id}:{','.join(sorted_domains)}:{include_predictions}:{prediction_window_months}"

        # Generate hash
        return hashlib.sha256(hash_input.encode()).hexdigest()

    async def get_cached_reading(
        self,
        canonical_hash: str,
        max_age_hours: int = 24
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached reading session if available and fresh

        Args:
            canonical_hash: Hash of reading parameters
            max_age_hours: Maximum age of cache in hours

        Returns:
            Cached reading or None
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)

        result = self.client.from_("reading_sessions")\
            .select("*")\
            .eq("canonical_hash", canonical_hash)\
            .gte("created_at", cutoff_time.isoformat())\
            .order("created_at", desc=True)\
            .limit(1)\
            .execute()

        if result.data:
            # Update access tracking
            session = result.data[0]
            self._update_reading_access(session['id'])
            return session

        return None

    async def store_reading_session(
        self,
        user_id: str,
        profile_id: str,
        canonical_hash: str,
        interpretation: str,
        domain_analyses: Dict[str, Any],
        predictions: List[Dict[str, Any]],
        rules_used: List[Dict[str, Any]],
        verification: Dict[str, Any],
        orchestration_metadata: Dict[str, Any],
        query: Optional[str] = None,
        domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Store reading session result

        Args:
            user_id: User ID
            profile_id: Profile ID
            canonical_hash: Canonical hash
            interpretation: Main interpretation text
            domain_analyses: Domain-specific analyses
            predictions: Time-based predictions
            rules_used: Rules cited
            verification: Quality metrics
            orchestration_metadata: Orchestration details
            query: User's query
            domains: Domains analyzed

        Returns:
            Created reading session
        """
        # Build session data with all Phase 3 fields
        session_data = {
            "user_id": user_id,
            "profile_id": profile_id,  # Include profile_id
            "canonical_hash": canonical_hash,
            "interpretation": interpretation,
            "domain_analyses": domain_analyses,
            "predictions": predictions,
            "rules_used": rules_used,
            "verification": verification,
            "orchestration_metadata": orchestration_metadata,
            "query": query,
            "domains": domains,
            "total_tokens_used": orchestration_metadata.get("tokens_used", 0) if orchestration_metadata else 0,
            "cache_hit": False,
        }

        print(f"💾 Storing reading session with full data: {len(interpretation)} chars, {len(predictions)} predictions, {len(rules_used)} rules")

        # Try to insert - if duplicate, return existing reading
        try:
            result = self.client.from_("reading_sessions")\
                .insert(session_data)\
                .execute()

            if result.data:
                print(f"✅ Reading session stored successfully: {result.data[0]['id']}")
                return result.data[0]
            return {}
        except Exception as e:
            error_str = str(e)

            # Check if it's a duplicate key error (code 23505)
            if '23505' in error_str or 'duplicate key' in error_str.lower():
                print(f"📦 Duplicate canonical_hash detected - returning existing reading")

                # Fetch the existing reading by canonical_hash
                try:
                    existing = self.client.from_("reading_sessions")\
                        .select("*")\
                        .eq("canonical_hash", canonical_hash)\
                        .eq("user_id", user_id)\
                        .order("created_at", desc=True)\
                        .limit(1)\
                        .execute()

                    if existing.data:
                        # Update access tracking
                        self._update_reading_access(existing.data[0]['id'])
                        return existing.data[0]
                except Exception as fetch_error:
                    print(f"Error fetching existing reading: {fetch_error}")

            # For other errors, log and return minimal mock session
            print(f"Warning: Could not store reading session (table may need migration): {e}")
            import uuid
            return {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "canonical_hash": canonical_hash,
                "created_at": datetime.utcnow().isoformat()
            }

    def _update_reading_access(self, session_id: str):
        """Update reading session access tracking"""
        try:
            # Get current access count
            current = self.client.from_("reading_sessions")\
                .select("times_accessed")\
                .eq("id", session_id)\
                .execute()

            if current.data:
                new_count = current.data[0]['times_accessed'] + 1

                self.client.from_("reading_sessions")\
                    .update({
                        "times_accessed": new_count,
                        "last_accessed_at": datetime.utcnow().isoformat(),
                        "cache_hit": True
                    })\
                    .eq("id", session_id)\
                    .execute()

        except Exception as e:
            print(f"Warning: Failed to update reading access tracking: {e}")

    async def store_reading_feedback(
        self,
        session_id: str,
        user_rating: int,
        user_feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Store user feedback for a reading

        Args:
            session_id: Reading session ID
            user_rating: Rating 1-5
            user_feedback: Optional text feedback

        Returns:
            Updated reading session
        """
        update_data = {
            "user_rating": user_rating,
            "user_feedback": user_feedback
        }

        result = self.client.from_("reading_sessions")\
            .update(update_data)\
            .eq("id", session_id)\
            .execute()

        return result.data[0] if result.data else {}

    # ========================================================================
    # PRIVACY & GDPR
    # ========================================================================

    async def erase_all_user_data(self, user_id: str) -> Dict[str, int]:
        """
        Erase all user data (GDPR compliance)

        Args:
            user_id: User ID to erase

        Returns:
            Dictionary with counts of deleted items
        """
        counts = {}

        try:
            # Delete memories
            memory_result = self.client.from_("user_memory")\
                .delete()\
                .eq("user_id", user_id)\
                .execute()
            counts['memories'] = len(memory_result.data) if memory_result.data else 0

            # Delete event anchors
            anchors_result = self.client.from_("event_anchors")\
                .delete()\
                .eq("user_id", user_id)\
                .execute()
            counts['event_anchors'] = len(anchors_result.data) if anchors_result.data else 0

            # Delete reading sessions
            sessions_result = self.client.from_("reading_sessions")\
                .delete()\
                .eq("user_id", user_id)\
                .execute()
            counts['reading_sessions'] = len(sessions_result.data) if sessions_result.data else 0

            print(f"✅ Erased all data for user {user_id}: {counts}")
            return counts

        except Exception as e:
            print(f"Error erasing user data: {e}")
            raise


# Singleton instance
memory_service = MemoryService()
