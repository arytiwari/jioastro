"""
Remedy Planner Service
Handles remedy catalog, assignments, tracking, streaks, and achievements
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import date, datetime, timedelta, time
from decimal import Decimal
import logging

from app.core.supabase_client import SupabaseClient
from app.schemas.remedy_planner import (
    SearchRemediesRequest,
    AssignRemedyRequest,
    UpdateAssignmentRequest,
    TrackRemedyRequest,
    RemedyCatalogItem,
    RemedyAssignment,
    RemedyTracking,
    RemedyAchievement,
    DashboardStats,
    StreakInfo,
    CalendarView,
    AssignedBy,
    AssignmentStatus
)

logger = logging.getLogger(__name__)


class RemedyPlannerService:
    """Service for Remedy Planner - Habit tracking with streaks"""

    # Achievement thresholds
    ACHIEVEMENT_THRESHOLDS = {
        "week_streak": 7,
        "month_streak": 30,
        "completion_100_days": 100,
        "multiple_remedies": 3  # Active remedies count
    }

    def __init__(self, supabase: SupabaseClient):
        self.supabase = supabase

    async def search_remedies(
        self,
        request: SearchRemediesRequest
    ) -> Tuple[List[RemedyCatalogItem], int]:
        """Search remedies catalog with filters"""

        filters = {"is_active": True}

        if request.remedy_type:
            filters["remedy_type"] = request.remedy_type.value
        if request.planet:
            filters["planet"] = request.planet
        if request.dosha:
            filters["dosha"] = request.dosha
        if request.difficulty_level:
            filters["difficulty_level"] = request.difficulty_level.value
        if request.frequency:
            filters["frequency"] = request.frequency.value
        if request.cost_estimate:
            filters["cost_estimate"] = request.cost_estimate

        # Get remedies
        remedies = await self.supabase.select(
            "remedies_catalog",
            filters=filters,
            order="remedy_name.asc",
            limit=request.limit,
            offset=request.offset
        )

        total = await self.supabase.count("remedies_catalog", filters=filters)

        remedy_items = [RemedyCatalogItem(**remedy) for remedy in remedies] if remedies else []
        return remedy_items, total

    async def get_remedy(self, remedy_id: str) -> Optional[RemedyCatalogItem]:
        """Get a specific remedy from catalog"""
        result = await self.supabase.select(
            "remedies_catalog",
            filters={"id": remedy_id, "is_active": True}
        )

        if not result or len(result) == 0:
            return None

        return RemedyCatalogItem(**result[0])

    async def assign_remedy(
        self,
        user_id: str,
        request: AssignRemedyRequest
    ) -> RemedyAssignment:
        """Assign a remedy to user"""

        # Verify remedy exists
        remedy = await self.get_remedy(request.remedy_id)
        if not remedy:
            raise ValueError("Remedy not found")

        # If profile_id provided, verify ownership
        if request.profile_id:
            profile = await self.supabase.select(
                "profiles",
                filters={"id": request.profile_id, "user_id": user_id}
            )
            if not profile or len(profile) == 0:
                raise ValueError("Profile not found or access denied")

        # Create assignment
        assignment_data = {
            "user_id": user_id,
            "remedy_id": request.remedy_id,
            "profile_id": request.profile_id,
            "assigned_reason": request.assigned_reason,
            "assigned_by": AssignedBy.SELF.value,
            "custom_instructions": request.custom_instructions,
            "target_start_date": request.target_start_date.isoformat() if request.target_start_date else None,
            "target_end_date": request.target_end_date.isoformat() if request.target_end_date else None,
            "custom_frequency": request.custom_frequency,
            "total_days_target": request.total_days_target,
            "status": AssignmentStatus.PENDING.value,
            "reminder_enabled": request.reminder_enabled,
            "reminder_time": request.reminder_time.isoformat() if request.reminder_time else None,
            "reminder_days": request.reminder_days
        }

        result = await self.supabase.insert("remedy_assignments", assignment_data)

        if not result or len(result) == 0:
            raise RuntimeError("Failed to create assignment")

        # Fetch complete assignment with remedy details
        return await self.get_assignment(user_id, result[0]["id"])

    async def get_assignment(self, user_id: str, assignment_id: str) -> RemedyAssignment:
        """Get assignment with remedy details"""
        assignment = await self.supabase.select(
            "remedy_assignments",
            filters={"id": assignment_id, "user_id": user_id}
        )

        if not assignment or len(assignment) == 0:
            raise ValueError("Assignment not found")

        assignment_data = assignment[0]

        # Get remedy details
        remedy = await self.get_remedy(assignment_data["remedy_id"])
        if not remedy:
            raise ValueError("Remedy not found")

        # Convert dates
        if assignment_data.get("started_at"):
            assignment_data["started_at"] = datetime.fromisoformat(assignment_data["started_at"])
        if assignment_data.get("completed_at"):
            assignment_data["completed_at"] = datetime.fromisoformat(assignment_data["completed_at"])
        if assignment_data.get("paused_at"):
            assignment_data["paused_at"] = datetime.fromisoformat(assignment_data["paused_at"])
        if assignment_data.get("last_completed_date"):
            assignment_data["last_completed_date"] = datetime.fromisoformat(assignment_data["last_completed_date"]).date()

        return RemedyAssignment(
            **assignment_data,
            remedy=remedy
        )

    async def update_assignment(
        self,
        user_id: str,
        assignment_id: str,
        request: UpdateAssignmentRequest
    ) -> RemedyAssignment:
        """Update assignment settings"""

        update_data = {}
        if request.status is not None:
            update_data["status"] = request.status.value
            # Set timestamps based on status
            if request.status == AssignmentStatus.ACTIVE and "started_at" not in update_data:
                update_data["started_at"] = datetime.now().isoformat()
            elif request.status == AssignmentStatus.COMPLETED:
                update_data["completed_at"] = datetime.now().isoformat()
            elif request.status == AssignmentStatus.PAUSED:
                update_data["paused_at"] = datetime.now().isoformat()

        if request.custom_instructions is not None:
            update_data["custom_instructions"] = request.custom_instructions
        if request.reminder_enabled is not None:
            update_data["reminder_enabled"] = request.reminder_enabled
        if request.reminder_time is not None:
            update_data["reminder_time"] = request.reminder_time.isoformat()
        if request.reminder_days is not None:
            update_data["reminder_days"] = request.reminder_days
        if request.user_notes is not None:
            update_data["user_notes"] = request.user_notes
        if request.effectiveness_rating is not None:
            update_data["effectiveness_rating"] = request.effectiveness_rating
        if request.user_feedback is not None:
            update_data["user_feedback"] = request.user_feedback

        if not update_data:
            raise ValueError("No fields to update")

        await self.supabase.update(
            "remedy_assignments",
            filters={"id": assignment_id, "user_id": user_id},
            data=update_data
        )

        return await self.get_assignment(user_id, assignment_id)

    async def delete_assignment(self, user_id: str, assignment_id: str) -> bool:
        """Delete an assignment"""
        await self.supabase.delete(
            "remedy_assignments",
            filters={"id": assignment_id, "user_id": user_id}
        )
        return True

    async def list_assignments(
        self,
        user_id: str,
        status: Optional[AssignmentStatus] = None,
        profile_id: Optional[str] = None
    ) -> Tuple[List[RemedyAssignment], int, int]:
        """List user's assignments"""

        filters = {"user_id": user_id}
        if status:
            filters["status"] = status.value
        if profile_id:
            filters["profile_id"] = profile_id

        assignments = await self.supabase.select(
            "remedy_assignments",
            filters=filters,
            order="created_at.desc"
        )

        total = await self.supabase.count("remedy_assignments", filters={"user_id": user_id})
        active = await self.supabase.count(
            "remedy_assignments",
            filters={"user_id": user_id, "status": AssignmentStatus.ACTIVE.value}
        )
        completed = await self.supabase.count(
            "remedy_assignments",
            filters={"user_id": user_id, "status": AssignmentStatus.COMPLETED.value}
        )

        # Fetch full assignment details
        assignment_list = []
        for assignment_data in (assignments or []):
            try:
                assignment = await self.get_assignment(user_id, assignment_data["id"])
                assignment_list.append(assignment)
            except Exception as e:
                logger.error(f"Error fetching assignment {assignment_data['id']}: {e}")
                continue

        return assignment_list, total, active, completed

    async def track_remedy(
        self,
        user_id: str,
        request: TrackRemedyRequest
    ) -> RemedyTracking:
        """Track daily remedy completion"""

        # Verify assignment ownership
        assignment = await self.supabase.select(
            "remedy_assignments",
            filters={"id": request.assignment_id, "user_id": user_id}
        )

        if not assignment or len(assignment) == 0:
            raise ValueError("Assignment not found or access denied")

        # Create or update tracking
        tracking_data = {
            "assignment_id": request.assignment_id,
            "user_id": user_id,
            "tracking_date": request.tracking_date.isoformat(),
            "completed": request.completed,
            "completed_at": datetime.now().isoformat() if request.completed else None,
            "quality_rating": request.quality_rating,
            "duration_minutes": request.duration_minutes,
            "notes": request.notes,
            "mood_before": request.mood_before.value if request.mood_before else None,
            "mood_after": request.mood_after.value if request.mood_after else None,
            "location": request.location,
            "time_of_day": request.time_of_day.value if request.time_of_day else None
        }

        # Upsert tracking (one per day per assignment)
        result = await self.supabase.upsert(
            "remedy_tracking",
            tracking_data,
            on_conflict="assignment_id,tracking_date"
        )

        if not result or len(result) == 0:
            raise RuntimeError("Failed to create tracking")

        # Streak is updated automatically via SQL trigger
        # But we can also check for achievements
        await self._check_and_unlock_achievements(user_id, request.assignment_id)

        return RemedyTracking(**result[0])

    async def get_tracking_history(
        self,
        user_id: str,
        assignment_id: str,
        limit: int = 30
    ) -> List[RemedyTracking]:
        """Get tracking history for an assignment"""

        # Verify ownership
        assignment = await self.supabase.select(
            "remedy_assignments",
            filters={"id": assignment_id, "user_id": user_id}
        )

        if not assignment or len(assignment) == 0:
            raise ValueError("Assignment not found")

        tracking = await self.supabase.select(
            "remedy_tracking",
            filters={"assignment_id": assignment_id, "user_id": user_id},
            order="tracking_date.desc",
            limit=limit
        )

        return [RemedyTracking(**t) for t in tracking] if tracking else []

    async def get_dashboard_stats(self, user_id: str) -> DashboardStats:
        """Get user's remedy dashboard statistics"""

        # Get all assignments
        filters = {"user_id": user_id}
        all_assignments = await self.supabase.select("remedy_assignments", filters=filters)

        total_assignments = len(all_assignments) if all_assignments else 0

        # Count by status
        active_assignments = sum(1 for a in (all_assignments or []) if a["status"] == AssignmentStatus.ACTIVE.value)
        completed_assignments = sum(1 for a in (all_assignments or []) if a["status"] == AssignmentStatus.COMPLETED.value)

        # Total days practiced
        total_days_practiced = sum(a.get("days_completed", 0) for a in (all_assignments or []))

        # Total streaks
        total_streaks = sum(a.get("current_streak", 0) for a in (all_assignments or []))
        longest_current_streak = max((a.get("current_streak", 0) for a in (all_assignments or [])), default=0)

        # Today's completions
        today = date.today()
        today_tracking = await self.supabase.select(
            "remedy_tracking",
            filters={"user_id": user_id, "tracking_date": today.isoformat(), "completed": True}
        )
        total_remedies_completed_today = len(today_tracking) if today_tracking else 0

        # Achievements
        achievements = await self.supabase.select(
            "remedy_achievements",
            filters={"user_id": user_id},
            order="unlocked_at.desc",
            limit=5
        )
        achievements_count = await self.supabase.count("remedy_achievements", filters={"user_id": user_id})
        recent_achievements = [RemedyAchievement(**a) for a in (achievements or [])]

        # Active streaks
        active_streaks = []
        for assignment in (all_assignments or []):
            if assignment["status"] == AssignmentStatus.ACTIVE.value:
                streak_info = await self._get_streak_info(user_id, assignment["id"])
                if streak_info:
                    active_streaks.append(streak_info)

        # Completion rates
        completion_rate_week = await self._calculate_completion_rate(user_id, days=7)
        completion_rate_month = await self._calculate_completion_rate(user_id, days=30)

        return DashboardStats(
            total_assignments=total_assignments,
            active_assignments=active_assignments,
            completed_assignments=completed_assignments,
            total_remedies_completed_today=total_remedies_completed_today,
            total_days_practiced=total_days_practiced,
            total_streaks=total_streaks,
            longest_current_streak=longest_current_streak,
            achievements_count=achievements_count,
            recent_achievements=recent_achievements,
            active_streaks=active_streaks[:5],  # Top 5
            completion_rate_this_week=completion_rate_week,
            completion_rate_this_month=completion_rate_month
        )

    async def _get_streak_info(self, user_id: str, assignment_id: str) -> Optional[StreakInfo]:
        """Get streak information for an assignment"""
        assignment = await self.supabase.select(
            "remedy_assignments",
            filters={"id": assignment_id, "user_id": user_id}
        )

        if not assignment or len(assignment) == 0:
            return None

        a = assignment[0]

        # Get remedy name
        remedy = await self.get_remedy(a["remedy_id"])
        remedy_name = remedy.remedy_name if remedy else "Unknown"

        last_completed = None
        if a.get("last_completed_date"):
            last_completed = datetime.fromisoformat(a["last_completed_date"]).date()

        # Calculate days until break
        days_until_break = 0
        is_at_risk = False
        if last_completed:
            days_since_last = (date.today() - last_completed).days
            if days_since_last == 1:
                days_until_break = 0
                is_at_risk = True

        return StreakInfo(
            assignment_id=assignment_id,
            remedy_name=remedy_name,
            current_streak=a.get("current_streak", 0),
            longest_streak=a.get("longest_streak", 0),
            last_completed_date=last_completed,
            days_until_break=days_until_break,
            is_at_risk=is_at_risk
        )

    async def _calculate_completion_rate(self, user_id: str, days: int) -> float:
        """Calculate completion rate for last N days"""
        start_date = date.today() - timedelta(days=days)

        # Get active assignments
        active = await self.supabase.select(
            "remedy_assignments",
            filters={"user_id": user_id, "status": AssignmentStatus.ACTIVE.value}
        )

        if not active:
            return 100.0  # No active assignments = 100% completion

        # Get completed tracking in period
        tracking = await self.supabase.select(
            "remedy_tracking",
            filters={"user_id": user_id, "completed": True}
        )

        if not tracking:
            return 0.0

        # Count completions in period
        completions_in_period = sum(
            1 for t in tracking
            if datetime.fromisoformat(t["tracking_date"]).date() >= start_date
        )

        # Expected completions = active assignments * days
        expected = len(active) * days

        return (completions_in_period / expected * 100) if expected > 0 else 0.0

    async def _check_and_unlock_achievements(self, user_id: str, assignment_id: str):
        """Check and unlock achievements for user"""

        # Get assignment
        assignment = await self.supabase.select(
            "remedy_assignments",
            filters={"id": assignment_id, "user_id": user_id}
        )

        if not assignment or len(assignment) == 0:
            return

        a = assignment[0]
        current_streak = a.get("current_streak", 0)
        days_completed = a.get("days_completed", 0)

        # Check for achievements
        achievements_to_unlock = []

        # Week streak
        if current_streak >= 7:
            achievements_to_unlock.append({
                "achievement_type": "week_streak",
                "achievement_name": "Week Warrior",
                "achievement_description": "Completed 7 days in a row",
                "achievement_icon": "🔥",
                "streak_count": current_streak
            })

        # Month streak
        if current_streak >= 30:
            achievements_to_unlock.append({
                "achievement_type": "month_streak",
                "achievement_name": "Month Master",
                "achievement_description": "Completed 30 days in a row",
                "achievement_icon": "⭐",
                "streak_count": current_streak
            })

        # 100 days
        if days_completed >= 100:
            achievements_to_unlock.append({
                "achievement_type": "completion_100_days",
                "achievement_name": "Century Club",
                "achievement_description": "Completed 100 days total",
                "achievement_icon": "💯"
            })

        # Insert achievements (upsert to avoid duplicates)
        for achievement in achievements_to_unlock:
            await self.supabase.upsert(
                "remedy_achievements",
                {
                    "user_id": user_id,
                    "assignment_id": assignment_id,
                    **achievement
                },
                on_conflict="user_id,assignment_id,achievement_type"
            )

    async def get_calendar_view(
        self,
        user_id: str,
        assignment_id: str,
        year: int,
        month: int
    ) -> CalendarView:
        """Get calendar view of completions for a month"""

        # Verify assignment
        assignment = await self.get_assignment(user_id, assignment_id)

        # Get tracking for month
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)

        tracking = await self.supabase.select(
            "remedy_tracking",
            filters={"assignment_id": assignment_id, "user_id": user_id}
        )

        # Build daily completions dict
        daily_completions = {}
        days_completed = 0

        for t in (tracking or []):
            tracking_date = datetime.fromisoformat(t["tracking_date"]).date()
            if start_date <= tracking_date <= end_date:
                day = tracking_date.day
                daily_completions[day] = t["completed"]
                if t["completed"]:
                    days_completed += 1

        total_days_in_month = end_date.day

        return CalendarView(
            year=year,
            month=month,
            assignment_id=assignment_id,
            remedy_name=assignment.remedy.remedy_name,
            daily_completions=daily_completions,
            total_days_in_month=total_days_in_month,
            days_completed=days_completed,
            completion_rate=(days_completed / total_days_in_month * 100) if total_days_in_month > 0 else 0.0
        )
