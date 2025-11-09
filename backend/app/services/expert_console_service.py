"""
Expert Console Service
Professional astrologer tools: custom settings, rectification, bulk analysis
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, date, time, timedelta
from app.services.supabase_service import supabase_service
import asyncio


class ExpertConsoleService:
    """Service for Expert Console professional features"""

    def __init__(self):
        self.supabase = supabase_service

    # =========================================================================
    # EXPERT SETTINGS
    # =========================================================================

    async def get_or_create_settings(self, user_id: str) -> Dict[str, Any]:
        """Get user's expert settings, create default if not exists"""
        # Try to get existing settings
        results = await self.supabase.select(
            table="expert_settings",
            filters={"user_id": user_id}
        )

        if results and len(results) > 0:
            return results[0]

        # Create default settings
        default_settings = {
            "user_id": user_id,
            "preferred_ayanamsa": "lahiri",
            "preferred_house_system": "placidus",
            "show_seconds": False,
            "show_retrograde_symbols": True,
            "show_dignity_symbols": True,
            "decimal_precision": 2,
            "use_true_node": True,
            "include_uranus": False,
            "include_neptune": False,
            "include_pluto": False,
            "default_vargas": ["D1", "D9"],
            "enable_rectification_tools": False,
            "enable_bulk_analysis": False,
            "enable_custom_exports": False
        }

        result = await self.supabase.insert(
            table="expert_settings",
            data=default_settings
        )

        return result[0] if result else None

    async def update_settings(
        self,
        user_id: str,
        settings_update: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update expert settings"""
        result = await self.supabase.update(
            table="expert_settings",
            data=settings_update,
            filters={"user_id": user_id}
        )

        return result[0] if result else None

    async def get_settings_stats(self, user_id: str) -> Dict[str, Any]:
        """Get usage statistics for expert settings"""
        # Get user's settings
        settings = await self.get_or_create_settings(user_id)

        # Count sessions and jobs
        rectification_sessions = await self.supabase.select(
            table="rectification_sessions",
            filters={"user_id": user_id}
        )

        bulk_jobs = await self.supabase.select(
            table="bulk_analysis_jobs",
            filters={"user_id": user_id}
        )

        presets = await self.supabase.select(
            table="calculation_presets",
            filters={"user_id": user_id}
        )

        # Calculate stats
        completed_rectifications = len([s for s in rectification_sessions if s.get("status") == "completed"])
        completed_jobs = len([j for j in bulk_jobs if j.get("status") == "completed"])

        return {
            "total_rectification_sessions": len(rectification_sessions),
            "total_bulk_jobs": len(bulk_jobs),
            "total_presets": len(presets),
            "rectifications_completed": completed_rectifications,
            "bulk_jobs_completed": completed_jobs,
            "favorite_ayanamsa": settings.get("preferred_ayanamsa"),
            "favorite_house_system": settings.get("preferred_house_system")
        }

    # =========================================================================
    # BIRTH TIME RECTIFICATION
    # =========================================================================

    async def create_rectification_session(
        self,
        user_id: str,
        session_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a birth time rectification session"""
        data = {
            "user_id": user_id,
            "profile_id": session_data.get("profile_id"),
            "original_name": session_data["name"],
            "original_date": session_data["birth_date"],
            "original_time": session_data["birth_time"],
            "original_latitude": session_data["latitude"],
            "original_longitude": session_data["longitude"],
            "original_timezone": session_data["timezone"],
            "time_window_minutes": session_data.get("time_window_minutes", 120),
            "increment_seconds": session_data.get("increment_seconds", 60),
            "life_events": session_data.get("life_events", []),
            "status": "pending",
            "tested_times_count": 0,
            "notes": session_data.get("notes")
        }

        result = await self.supabase.insert(
            table="rectification_sessions",
            data=data
        )

        return result[0] if result else None

    async def get_rectification_sessions(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get user's rectification sessions"""
        sessions = await self.supabase.select(
            table="rectification_sessions",
            filters={"user_id": user_id},
            order="created_at.desc",
            limit=limit,
            offset=offset
        )

        # Get total count
        all_sessions = await self.supabase.select(
            table="rectification_sessions",
            filters={"user_id": user_id}
        )

        return {
            "sessions": sessions,
            "total_count": len(all_sessions)
        }

    async def get_rectification_session(
        self,
        session_id: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get a specific rectification session"""
        results = await self.supabase.select(
            table="rectification_sessions",
            filters={"id": session_id, "user_id": user_id}
        )

        return results[0] if results else None

    async def process_rectification(
        self,
        session_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Execute rectification algorithm
        Tests multiple birth times and scores them based on life events
        """
        # Get session
        session = await self.get_rectification_session(session_id, user_id)
        if not session:
            raise ValueError("Rectification session not found")

        # Update status to running
        await self.supabase.update(
            table="rectification_sessions",
            data={
                "status": "running",
                "started_at": datetime.utcnow().isoformat()
            },
            filters={"id": session_id}
        )

        try:
            # Parse original time
            original_time = session["original_time"]
            if isinstance(original_time, str):
                original_time = datetime.strptime(original_time, "%H:%M:%S").time()

            # Generate test times
            window_minutes = session["time_window_minutes"]
            increment_seconds = session["increment_seconds"]

            original_datetime = datetime.combine(date.today(), original_time)
            start_datetime = original_datetime - timedelta(minutes=window_minutes)
            end_datetime = original_datetime + timedelta(minutes=window_minutes)

            test_times = []
            current_datetime = start_datetime
            while current_datetime <= end_datetime:
                test_times.append(current_datetime.time())
                current_datetime += timedelta(seconds=increment_seconds)

            # Score each time (simplified scoring for now)
            # In production, this would use dasha analysis, yoga detection, etc.
            scores = []
            for test_time in test_times:
                # Calculate score based on life events
                # For now, use a simple placeholder score
                score = self._calculate_rectification_score(
                    birth_date=session["original_date"],
                    birth_time=test_time,
                    latitude=session["original_latitude"],
                    longitude=session["original_longitude"],
                    timezone=session["original_timezone"],
                    life_events=session.get("life_events", [])
                )

                scores.append({
                    "time": test_time.isoformat(),
                    "score": score
                })

            # Find best match
            best_match = max(scores, key=lambda x: x["score"])
            best_match_time = datetime.strptime(best_match["time"], "%H:%M:%S").time()

            # Get top 5 matches for results summary
            top_matches = sorted(scores, key=lambda x: x["score"], reverse=True)[:5]

            # Update session with results
            await self.supabase.update(
                table="rectification_sessions",
                data={
                    "status": "completed",
                    "tested_times_count": len(test_times),
                    "best_match_time": best_match_time.isoformat(),
                    "best_match_score": best_match["score"],
                    "results_summary": {"top_matches": top_matches},
                    "completed_at": datetime.utcnow().isoformat()
                },
                filters={"id": session_id}
            )

            return {
                "session_id": session_id,
                "status": "completed",
                "tested_times": len(test_times),
                "best_match_time": best_match_time.isoformat(),
                "best_match_score": best_match["score"],
                "top_matches": top_matches
            }

        except Exception as e:
            # Update status to failed
            await self.supabase.update(
                table="rectification_sessions",
                data={
                    "status": "failed",
                    "completed_at": datetime.utcnow().isoformat()
                },
                filters={"id": session_id}
            )
            raise e

    def _calculate_rectification_score(
        self,
        birth_date: date,
        birth_time: time,
        latitude: float,
        longitude: float,
        timezone: str,
        life_events: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate rectification score for a given birth time

        In production, this would:
        1. Calculate chart for this birth time
        2. Check dasha periods for each life event
        3. Verify yoga formations at event times
        4. Score based on astrological correlations

        For now, using simplified placeholder logic
        """
        # Placeholder: Random score between 0-100
        # In production, replace with actual dasha/yoga analysis
        import random
        random.seed(f"{birth_time.hour}{birth_time.minute}{birth_time.second}")
        return round(random.uniform(0, 100), 2)

    async def delete_rectification_session(
        self,
        session_id: str,
        user_id: str
    ) -> bool:
        """Delete a rectification session"""
        return await self.supabase.delete(
            table="rectification_sessions",
            filters={"id": session_id, "user_id": user_id}
        )

    # =========================================================================
    # BULK ANALYSIS JOBS
    # =========================================================================

    async def create_bulk_job(
        self,
        user_id: str,
        job_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a bulk analysis job"""
        data = {
            "user_id": user_id,
            "job_name": job_data["job_name"],
            "analysis_type": job_data["analysis_type"],
            "input_profiles": job_data["input_profiles"],
            "total_profiles": len(job_data["input_profiles"]),
            "status": "queued",
            "processed_count": 0,
            "failed_count": 0,
            "export_format": job_data.get("export_format", "json")
        }

        result = await self.supabase.insert(
            table="bulk_analysis_jobs",
            data=data
        )

        return result[0] if result else None

    async def get_bulk_jobs(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get user's bulk analysis jobs"""
        jobs = await self.supabase.select(
            table="bulk_analysis_jobs",
            filters={"user_id": user_id},
            order="created_at.desc",
            limit=limit,
            offset=offset
        )

        # Get total count
        all_jobs = await self.supabase.select(
            table="bulk_analysis_jobs",
            filters={"user_id": user_id}
        )

        return {
            "jobs": jobs,
            "total_count": len(all_jobs)
        }

    async def get_bulk_job(
        self,
        job_id: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get a specific bulk job"""
        results = await self.supabase.select(
            table="bulk_analysis_jobs",
            filters={"id": job_id, "user_id": user_id}
        )

        return results[0] if results else None

    async def process_bulk_job(
        self,
        job_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Process bulk analysis job
        This would run asynchronously in production (Celery/RQ)
        """
        job = await self.get_bulk_job(job_id, user_id)
        if not job:
            raise ValueError("Bulk job not found")

        # Update status to processing
        await self.supabase.update(
            table="bulk_analysis_jobs",
            data={
                "status": "processing",
                "started_at": datetime.utcnow().isoformat()
            },
            filters={"id": job_id}
        )

        try:
            input_profiles = job["input_profiles"]
            analysis_type = job["analysis_type"]
            results = []

            # Process each profile
            for idx, profile in enumerate(input_profiles):
                try:
                    # Perform analysis based on type
                    result = await self._process_single_analysis(profile, analysis_type)
                    results.append(result)

                    # Update progress
                    await self.supabase.update(
                        table="bulk_analysis_jobs",
                        data={"processed_count": idx + 1},
                        filters={"id": job_id}
                    )

                except Exception as e:
                    print(f"Error processing profile {idx}: {str(e)}")
                    results.append({"error": str(e)})

                    # Increment failed count
                    await self.supabase.update(
                        table="bulk_analysis_jobs",
                        data={"failed_count": job["failed_count"] + 1},
                        filters={"id": job_id}
                    )

            # Calculate processing time
            start_time = datetime.fromisoformat(job["started_at"]) if job.get("started_at") else datetime.utcnow()
            processing_seconds = int((datetime.utcnow() - start_time).total_seconds())

            # Update job with results
            await self.supabase.update(
                table="bulk_analysis_jobs",
                data={
                    "status": "completed",
                    "results_summary": {"results": results},
                    "processing_time_seconds": processing_seconds,
                    "completed_at": datetime.utcnow().isoformat()
                },
                filters={"id": job_id}
            )

            return {
                "job_id": job_id,
                "status": "completed",
                "processed": len(results),
                "failed": job["failed_count"],
                "processing_time": processing_seconds
            }

        except Exception as e:
            await self.supabase.update(
                table="bulk_analysis_jobs",
                data={
                    "status": "failed",
                    "completed_at": datetime.utcnow().isoformat()
                },
                filters={"id": job_id}
            )
            raise e

    async def _process_single_analysis(
        self,
        profile: Dict[str, Any],
        analysis_type: str
    ) -> Dict[str, Any]:
        """Process a single profile for bulk analysis"""
        # Placeholder for actual analysis logic
        # In production, this would call astrology service methods
        return {
            "name": profile.get("name"),
            "analysis_type": analysis_type,
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat()
        }

    async def delete_bulk_job(
        self,
        job_id: str,
        user_id: str
    ) -> bool:
        """Delete a bulk job"""
        return await self.supabase.delete(
            table="bulk_analysis_jobs",
            filters={"id": job_id, "user_id": user_id}
        )

    # =========================================================================
    # CALCULATION PRESETS
    # =========================================================================

    async def create_preset(
        self,
        user_id: str,
        preset_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a calculation preset"""
        data = {
            "user_id": user_id,
            "preset_name": preset_data["preset_name"],
            "preset_description": preset_data.get("preset_description"),
            "is_public": preset_data.get("is_public", False),
            "ayanamsa": preset_data["ayanamsa"],
            "house_system": preset_data["house_system"],
            "calculation_options": preset_data.get("calculation_options", {}),
            "varga_selection": preset_data.get("varga_selection", ["D1", "D9"]),
            "usage_count": 0
        }

        result = await self.supabase.insert(
            table="calculation_presets",
            data=data
        )

        return result[0] if result else None

    async def get_presets(
        self,
        user_id: str,
        include_public: bool = True,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get user's presets and optionally public presets"""
        # Get user's own presets
        user_presets = await self.supabase.select(
            table="calculation_presets",
            filters={"user_id": user_id},
            order="created_at.desc"
        )

        presets = user_presets

        # Add public presets if requested
        if include_public:
            public_presets = await self.supabase.select(
                table="calculation_presets",
                filters={"is_public": True},
                order="usage_count.desc",
                limit=20
            )
            # Filter out user's own public presets to avoid duplicates
            public_presets = [p for p in public_presets if p["user_id"] != user_id]
            presets = user_presets + public_presets

        return {
            "presets": presets[offset:offset + limit],
            "total_count": len(presets)
        }

    async def get_preset(
        self,
        preset_id: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get a specific preset (must be owned by user or public)"""
        results = await self.supabase.select(
            table="calculation_presets",
            filters={"id": preset_id}
        )

        if not results:
            return None

        preset = results[0]

        # Check access permission
        if preset["user_id"] != user_id and not preset["is_public"]:
            return None

        return preset

    async def update_preset(
        self,
        preset_id: str,
        user_id: str,
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a preset (only owner can update)"""
        result = await self.supabase.update(
            table="calculation_presets",
            data=update_data,
            filters={"id": preset_id, "user_id": user_id}
        )

        return result[0] if result else None

    async def increment_preset_usage(
        self,
        preset_id: str
    ) -> None:
        """Increment usage count when preset is used"""
        preset = await self.supabase.select(
            table="calculation_presets",
            filters={"id": preset_id}
        )

        if preset:
            current_count = preset[0].get("usage_count", 0)
            await self.supabase.update(
                table="calculation_presets",
                data={
                    "usage_count": current_count + 1,
                    "last_used_at": datetime.utcnow().isoformat()
                },
                filters={"id": preset_id}
            )

    async def delete_preset(
        self,
        preset_id: str,
        user_id: str
    ) -> bool:
        """Delete a preset (only owner can delete)"""
        return await self.supabase.delete(
            table="calculation_presets",
            filters={"id": preset_id, "user_id": user_id}
        )


# Singleton instance
expert_console_service = ExpertConsoleService()
