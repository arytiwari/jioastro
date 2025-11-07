"""Main API Router"""

from fastapi import APIRouter

from app.api.v1.endpoints import profiles, charts, queries, feedback, admin, readings, knowledge, enhancements, setup, cities, numerology, compatibility, varshaphal

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
api_router.include_router(charts.router, prefix="/charts", tags=["charts"])
api_router.include_router(queries.router, prefix="/queries", tags=["queries"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(readings.router, prefix="/readings", tags=["readings"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
api_router.include_router(enhancements.router, prefix="/enhancements", tags=["enhancements"])
api_router.include_router(setup.router, prefix="/setup", tags=["setup"])
api_router.include_router(cities.router, prefix="/cities", tags=["cities"])
api_router.include_router(numerology.router, prefix="/numerology", tags=["numerology"])
api_router.include_router(compatibility.router, prefix="/compatibility", tags=["compatibility"])
api_router.include_router(varshaphal.router, prefix="/varshaphal", tags=["varshaphal"])
