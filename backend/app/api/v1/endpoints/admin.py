"""Admin Endpoints - Cleanup and Maintenance"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_user
from app.services.supabase_service import supabase_service

router = APIRouter()


@router.delete("/cleanup/all-data", status_code=status.HTTP_200_OK)
async def cleanup_all_data(current_user: dict = Depends(get_current_user)):
    """
    Delete all old astrological data (queries, responses, charts, feedback)
    Keeps user accounts and profiles intact
    """
    try:
        deleted_counts = {
            "feedback": 0,
            "responses": 0,
            "queries": 0,
            "charts": 0
        }

        # Delete feedback (no user_id filter needed, cascade will work)
        feedback_response = supabase_service.client.table("feedback").delete().neq("id", "").execute()
        deleted_counts["feedback"] = len(feedback_response.data) if feedback_response.data else 0

        # Delete responses
        responses_response = supabase_service.client.table("responses").delete().neq("id", "").execute()
        deleted_counts["responses"] = len(responses_response.data) if responses_response.data else 0

        # Delete queries
        queries_response = supabase_service.client.table("queries").delete().neq("id", "").execute()
        deleted_counts["queries"] = len(queries_response.data) if queries_response.data else 0

        # Delete charts
        charts_response = supabase_service.client.table("charts").delete().neq("id", "").execute()
        deleted_counts["charts"] = len(charts_response.data) if charts_response.data else 0

        return {
            "success": True,
            "message": "All old astrological data has been deleted successfully",
            "deleted_counts": deleted_counts,
            "note": "User accounts and profiles remain intact. New calculations will use accurate Swiss Ephemeris."
        }

    except Exception as e:
        print(f"Error cleaning up data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cleanup data: {str(e)}"
        )


@router.delete("/cleanup/my-data", status_code=status.HTTP_200_OK)
async def cleanup_my_data(current_user: dict = Depends(get_current_user)):
    """
    Delete only the current user's astrological data
    Keeps profiles but removes queries, responses, and charts
    """
    try:
        user_id = current_user["user_id"]
        deleted_counts = {
            "feedback": 0,
            "responses": 0,
            "queries": 0,
            "charts": 0
        }

        # Get all queries for this user
        user_queries = await supabase_service.get_queries(user_id=user_id, limit=1000)
        query_ids = [q["id"] for q in user_queries]

        if query_ids:
            # Delete feedback for user's responses
            for query_id in query_ids:
                query_data = await supabase_service.get_query(query_id, user_id)
                if query_data and "responses" in query_data:
                    for response in query_data["responses"]:
                        feedback = await supabase_service.get_feedback_for_response(response["id"])
                        if feedback:
                            supabase_service.client.table("feedback").delete().eq("id", feedback["id"]).execute()
                            deleted_counts["feedback"] += 1

            # Delete responses for user's queries
            for query_id in query_ids:
                responses = supabase_service.client.table("responses").delete().eq("query_id", query_id).execute()
                deleted_counts["responses"] += len(responses.data) if responses.data else 0

        # Delete user's queries
        queries_response = supabase_service.client.table("queries").delete().eq("user_id", user_id).execute()
        deleted_counts["queries"] = len(queries_response.data) if queries_response.data else 0

        # Get user's profiles
        user_profiles = await supabase_service.get_profiles(user_id)
        profile_ids = [p["id"] for p in user_profiles]

        # Delete charts for user's profiles
        for profile_id in profile_ids:
            charts = supabase_service.client.table("charts").delete().eq("profile_id", profile_id).execute()
            deleted_counts["charts"] += len(charts.data) if charts.data else 0

        return {
            "success": True,
            "message": "Your astrological data has been deleted successfully",
            "deleted_counts": deleted_counts,
            "note": "Your profiles remain intact. New queries will use accurate Swiss Ephemeris calculations."
        }

    except Exception as e:
        print(f"Error cleaning up user data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cleanup your data: {str(e)}"
        )


@router.delete("/cleanup/charts-only", status_code=status.HTTP_200_OK)
async def cleanup_charts_only(current_user: dict = Depends(get_current_user)):
    """
    Delete only chart data (birth charts and navamsa)
    Keeps queries and responses, but they will use recalculated charts
    """
    try:
        # Delete all charts
        charts_response = supabase_service.client.table("charts").delete().neq("id", "").execute()
        deleted_count = len(charts_response.data) if charts_response.data else 0

        return {
            "success": True,
            "message": "All chart data has been deleted successfully",
            "deleted_charts": deleted_count,
            "note": "Charts will be recalculated with accurate Swiss Ephemeris when needed"
        }

    except Exception as e:
        print(f"Error cleaning up charts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cleanup charts: {str(e)}"
        )
