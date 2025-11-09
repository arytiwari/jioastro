"""
Reality Check Loop Service
Handles predictions, outcomes, learning insights, and accuracy metrics
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, date, timedelta
from app.services.supabase_service import supabase_service

logger = logging.getLogger(__name__)


class RealityCheckService:
    """Service for Reality Check Loop operations"""

    def __init__(self):
        self.supabase = supabase_service

    # =====================================================
    # PREDICTION MANAGEMENT
    # =====================================================

    async def create_prediction(
        self, user_id: str, prediction_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Create a new prediction"""
        try:
            data = {
                "user_id": user_id,
                "profile_id": prediction_data.get("profile_id"),
                "prediction_type": prediction_data["prediction_type"],
                "prediction_category": prediction_data["prediction_category"],
                "source_type": prediction_data["source_type"],
                "source_id": prediction_data.get("source_id"),
                "prediction_text": prediction_data["prediction_text"],
                "prediction_summary": prediction_data.get("prediction_summary"),
                "confidence_level": prediction_data.get("confidence_level", "medium"),
                "expected_timeframe_start": prediction_data.get("expected_timeframe_start"),
                "expected_timeframe_end": prediction_data.get("expected_timeframe_end"),
                "timeframe_description": prediction_data.get("timeframe_description"),
                "astrological_context": prediction_data.get("astrological_context"),
                "key_factors": prediction_data.get("key_factors"),
                "status": "active",
                "tags": prediction_data.get("tags", []),
                "notes": prediction_data.get("notes"),
            }

            result = await self.supabase.insert(table="predictions", data=data)
            return result[0] if result else None

        except Exception as e:
            logger.error(f"Error creating prediction: {e}")
            raise

    async def get_predictions(
        self,
        user_id: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Get user's predictions with optional filters"""
        try:
            # Base filter
            query_filters = {"user_id": user_id}

            # Apply additional filters
            if filters:
                if filters.get("status"):
                    query_filters["status"] = filters["status"]
                if filters.get("category"):
                    query_filters["prediction_category"] = filters["category"]
                if filters.get("prediction_type"):
                    query_filters["prediction_type"] = filters["prediction_type"]
                if filters.get("confidence_level"):
                    query_filters["confidence_level"] = filters["confidence_level"]
                if filters.get("profile_id"):
                    query_filters["profile_id"] = filters["profile_id"]

            # Get predictions
            predictions = await self.supabase.select(
                table="predictions",
                filters=query_filters,
                order="created_at.desc",
                limit=limit,
                offset=offset,
            )

            # Count total
            total_count = await self.supabase.count(
                table="predictions", filters=query_filters
            )

            # Count predictions with outcomes
            has_outcomes_count = 0
            pending_outcomes_count = 0

            if predictions:
                for pred in predictions:
                    outcome = await self.supabase.select(
                        table="prediction_outcomes",
                        filters={"prediction_id": pred["id"]},
                        limit=1,
                    )
                    if outcome:
                        has_outcomes_count += 1
                    elif pred["status"] == "active":
                        pending_outcomes_count += 1

            return {
                "predictions": predictions or [],
                "total_count": total_count,
                "has_outcomes": has_outcomes_count,
                "pending_outcomes": pending_outcomes_count,
            }

        except Exception as e:
            logger.error(f"Error getting predictions: {e}")
            raise

    async def get_prediction(
        self, prediction_id: str, user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get a specific prediction"""
        try:
            result = await self.supabase.select(
                table="predictions",
                filters={"id": prediction_id, "user_id": user_id},
                limit=1,
            )
            return result[0] if result else None

        except Exception as e:
            logger.error(f"Error getting prediction: {e}")
            raise

    async def update_prediction(
        self, prediction_id: str, user_id: str, updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update a prediction"""
        try:
            # Verify ownership
            existing = await self.get_prediction(prediction_id, user_id)
            if not existing:
                return None

            result = await self.supabase.update(
                table="predictions",
                filters={"id": prediction_id, "user_id": user_id},
                data=updates,
            )
            return result[0] if result else None

        except Exception as e:
            logger.error(f"Error updating prediction: {e}")
            raise

    async def delete_prediction(
        self, prediction_id: str, user_id: str
    ) -> bool:
        """Delete a prediction"""
        try:
            await self.supabase.delete(
                table="predictions",
                filters={"id": prediction_id, "user_id": user_id},
            )
            return True

        except Exception as e:
            logger.error(f"Error deleting prediction: {e}")
            raise

    # =====================================================
    # OUTCOME MANAGEMENT
    # =====================================================

    async def create_outcome(
        self, user_id: str, outcome_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Record an outcome for a prediction"""
        try:
            prediction_id = outcome_data["prediction_id"]

            # Verify prediction ownership
            prediction = await self.get_prediction(prediction_id, user_id)
            if not prediction:
                raise ValueError("Prediction not found or access denied")

            # Calculate accuracy score
            accuracy_score = self._calculate_accuracy_score(
                outcome_data["outcome_occurred"],
                outcome_data.get("timing_accuracy"),
                outcome_data.get("severity_match"),
            )

            data = {
                "prediction_id": prediction_id,
                "user_id": user_id,
                "outcome_occurred": outcome_data["outcome_occurred"],
                "actual_date": outcome_data.get("actual_date"),
                "outcome_description": outcome_data["outcome_description"],
                "accuracy_score": accuracy_score,
                "timing_accuracy": outcome_data.get("timing_accuracy"),
                "severity_match": outcome_data.get("severity_match"),
                "what_matched": outcome_data.get("what_matched"),
                "what_differed": outcome_data.get("what_differed"),
                "additional_events": outcome_data.get("additional_events"),
                "helpfulness_rating": outcome_data["helpfulness_rating"],
                "would_trust_again": outcome_data["would_trust_again"],
            }

            result = await self.supabase.insert(table="prediction_outcomes", data=data)

            # Update prediction status (handled by DB trigger, but we can also do it here)
            await self.update_prediction(
                prediction_id,
                user_id,
                {"status": "verified" if outcome_data["outcome_occurred"] else "rejected"},
            )

            # Trigger learning analysis (async background task in production)
            # await self._analyze_for_insights(user_id)

            return result[0] if result else None

        except Exception as e:
            logger.error(f"Error creating outcome: {e}")
            raise

    async def get_outcome(
        self, prediction_id: str, user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get outcome for a prediction"""
        try:
            result = await self.supabase.select(
                table="prediction_outcomes",
                filters={"prediction_id": prediction_id, "user_id": user_id},
                limit=1,
            )
            return result[0] if result else None

        except Exception as e:
            logger.error(f"Error getting outcome: {e}")
            raise

    async def update_outcome(
        self, outcome_id: str, user_id: str, updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update an outcome"""
        try:
            # Recalculate accuracy score if relevant fields changed
            if any(k in updates for k in ["outcome_occurred", "timing_accuracy", "severity_match"]):
                # Get existing outcome to merge data
                existing = await self.supabase.select(
                    table="prediction_outcomes",
                    filters={"id": outcome_id, "user_id": user_id},
                    limit=1,
                )
                if existing:
                    outcome = existing[0]
                    accuracy_score = self._calculate_accuracy_score(
                        updates.get("outcome_occurred", outcome["outcome_occurred"]),
                        updates.get("timing_accuracy", outcome["timing_accuracy"]),
                        updates.get("severity_match", outcome["severity_match"]),
                    )
                    updates["accuracy_score"] = accuracy_score

            result = await self.supabase.update(
                table="prediction_outcomes",
                filters={"id": outcome_id, "user_id": user_id},
                data=updates,
            )
            return result[0] if result else None

        except Exception as e:
            logger.error(f"Error updating outcome: {e}")
            raise

    def _calculate_accuracy_score(
        self,
        outcome_occurred: bool,
        timing_accuracy: Optional[str],
        severity_match: Optional[str],
    ) -> int:
        """Calculate accuracy score (0-100)"""
        if not outcome_occurred:
            return 0

        base_score = 60  # Base score for occurrence

        # Timing bonus (up to 20%)
        timing_bonus = {
            "on_time": 20,
            "early": 15,
            "late": 10,
            "significantly_late": 5,
        }.get(timing_accuracy, 0)

        # Severity bonus (up to 20%)
        severity_bonus = {
            "accurate": 20,
            "understated": 10,
            "overstated": 10,
        }.get(severity_match, 0)

        return base_score + timing_bonus + severity_bonus

    # =====================================================
    # LEARNING INSIGHTS
    # =====================================================

    async def get_insights(
        self,
        category: Optional[str] = None,
        insight_type: Optional[str] = None,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """Get learning insights"""
        try:
            filters = {}
            if category:
                filters["category"] = category
            if insight_type:
                filters["insight_type"] = insight_type

            insights = await self.supabase.select(
                table="learning_insights",
                filters=filters,
                order="accuracy_rate.desc",
                limit=limit,
            )

            total_count = await self.supabase.count(
                table="learning_insights", filters=filters
            )

            return {
                "insights": insights or [],
                "total_count": total_count,
            }

        except Exception as e:
            logger.error(f"Error getting insights: {e}")
            raise

    async def create_insight(
        self, insight_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Create a learning insight (system/admin only)"""
        try:
            data = {
                "insight_type": insight_data["insight_type"],
                "category": insight_data["category"],
                "title": insight_data["title"],
                "description": insight_data["description"],
                "sample_size": insight_data["sample_size"],
                "accuracy_rate": insight_data.get("accuracy_rate"),
                "confidence_interval": insight_data.get("confidence_interval"),
                "astrological_factors": insight_data.get("astrological_factors"),
                "successful_patterns": insight_data.get("successful_patterns"),
                "failure_patterns": insight_data.get("failure_patterns"),
                "impact_level": insight_data.get("impact_level", "medium"),
                "actionable_recommendations": insight_data.get("actionable_recommendations", []),
            }

            result = await self.supabase.insert(table="learning_insights", data=data)
            return result[0] if result else None

        except Exception as e:
            logger.error(f"Error creating insight: {e}")
            raise

    # =====================================================
    # ACCURACY METRICS
    # =====================================================

    async def get_user_accuracy_stats(
        self, user_id: str
    ) -> Dict[str, Any]:
        """Get comprehensive accuracy statistics for a user"""
        try:
            # Get all user predictions
            all_predictions = await self.supabase.select(
                table="predictions",
                filters={"user_id": user_id},
            )

            total_predictions = len(all_predictions) if all_predictions else 0

            # Get predictions with outcomes
            verified_predictions = []
            accurate_predictions = []
            helpfulness_ratings = []
            trust_count = 0
            category_stats = {}

            if all_predictions:
                for pred in all_predictions:
                    outcome = await self.supabase.select(
                        table="prediction_outcomes",
                        filters={"prediction_id": pred["id"]},
                        limit=1,
                    )

                    if outcome:
                        outcome_data = outcome[0]
                        verified_predictions.append(pred)

                        # Track accuracy
                        if outcome_data.get("accuracy_score", 0) >= 60:
                            accurate_predictions.append(pred)

                        # Track helpfulness
                        if outcome_data.get("helpfulness_rating"):
                            helpfulness_ratings.append(outcome_data["helpfulness_rating"])

                        # Track trust
                        if outcome_data.get("would_trust_again"):
                            trust_count += 1

                        # Track by category
                        category = pred["prediction_category"]
                        if category not in category_stats:
                            category_stats[category] = {
                                "total": 0,
                                "verified": 0,
                                "accurate": 0,
                            }
                        category_stats[category]["total"] += 1
                        category_stats[category]["verified"] += 1
                        if outcome_data.get("accuracy_score", 0) >= 60:
                            category_stats[category]["accurate"] += 1

            verified_count = len(verified_predictions)
            pending_count = total_predictions - verified_count

            # Calculate rates
            overall_accuracy_rate = None
            if verified_count > 0:
                overall_accuracy_rate = (len(accurate_predictions) / verified_count) * 100

            avg_helpfulness = None
            if helpfulness_ratings:
                avg_helpfulness = sum(helpfulness_ratings) / len(helpfulness_ratings)

            trust_rate = None
            if verified_count > 0:
                trust_rate = (trust_count / verified_count) * 100

            # Find best and worst categories
            best_category = None
            best_category_accuracy = None
            worst_category = None
            worst_category_accuracy = None

            for category, stats in category_stats.items():
                if stats["verified"] > 0:
                    accuracy = (stats["accurate"] / stats["verified"]) * 100
                    stats["accuracy_rate"] = accuracy

                    if best_category_accuracy is None or accuracy > best_category_accuracy:
                        best_category = category
                        best_category_accuracy = accuracy

                    if worst_category_accuracy is None or accuracy < worst_category_accuracy:
                        worst_category = category
                        worst_category_accuracy = accuracy

            return {
                "total_predictions": total_predictions,
                "verified_predictions": verified_count,
                "pending_predictions": pending_count,
                "overall_accuracy_rate": overall_accuracy_rate,
                "avg_helpfulness_rating": avg_helpfulness,
                "trust_rate": trust_rate,
                "best_category": best_category,
                "best_category_accuracy": best_category_accuracy,
                "worst_category": worst_category,
                "worst_category_accuracy": worst_category_accuracy,
                "recent_trend": None,  # TODO: Calculate trend
                "category_breakdown": category_stats,
            }

        except Exception as e:
            logger.error(f"Error getting user accuracy stats: {e}")
            raise

    async def get_dashboard_data(
        self, user_id: str
    ) -> Dict[str, Any]:
        """Get complete dashboard data for Reality Check Loop"""
        try:
            # Get user stats
            user_stats = await self.get_user_accuracy_stats(user_id)

            # Get recent predictions
            recent_predictions = await self.get_predictions(
                user_id, limit=5, offset=0
            )

            # Get pending outcomes
            pending_predictions = await self.get_predictions(
                user_id, filters={"status": "active"}, limit=10, offset=0
            )

            # Get top insights
            insights = await self.get_insights(limit=5)

            # Calculate category accuracy
            category_accuracy = []
            for category, stats in user_stats["category_breakdown"].items():
                category_accuracy.append({
                    "category": category,
                    "total_predictions": stats["total"],
                    "verified_predictions": stats["verified"],
                    "accuracy_rate": stats.get("accuracy_rate"),
                    "avg_helpfulness": None,  # TODO: Calculate per category
                })

            # TODO: Calculate confidence calibration and monthly trends

            return {
                "user_stats": user_stats,
                "recent_predictions": recent_predictions["predictions"][:5],
                "pending_outcomes": pending_predictions["predictions"],
                "category_accuracy": category_accuracy,
                "confidence_calibration": [],  # TODO
                "monthly_trends": [],  # TODO
                "top_insights": insights["insights"],
            }

        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            raise

    # =====================================================
    # REMINDERS
    # =====================================================

    async def create_reminder(
        self, prediction_id: str, user_id: str, reminder_type: str
    ) -> Optional[Dict[str, Any]]:
        """Create a prediction reminder"""
        try:
            data = {
                "prediction_id": prediction_id,
                "user_id": user_id,
                "reminder_type": reminder_type,
            }

            result = await self.supabase.insert(table="prediction_reminders", data=data)
            return result[0] if result else None

        except Exception as e:
            logger.error(f"Error creating reminder: {e}")
            raise

    async def mark_reminder_opened(
        self, reminder_id: str, user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Mark a reminder as opened"""
        try:
            result = await self.supabase.update(
                table="prediction_reminders",
                filters={"id": reminder_id, "user_id": user_id},
                data={"opened": True, "opened_at": datetime.utcnow().isoformat()},
            )
            return result[0] if result else None

        except Exception as e:
            logger.error(f"Error marking reminder opened: {e}")
            raise


# Singleton instance
reality_check_service = RealityCheckService()
