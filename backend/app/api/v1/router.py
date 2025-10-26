"""Main API Router"""

from fastapi import APIRouter

from app.api.v1.endpoints import profiles, charts, queries, feedback

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
api_router.include_router(charts.router, prefix="/charts", tags=["charts"])
api_router.include_router(queries.router, prefix="/queries", tags=["queries"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
