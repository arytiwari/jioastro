"""Main API Router"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    profiles,
    charts,
    queries,
    feedback,
    admin,
    readings,
    knowledge,
    enhancements,
    setup,
    cities,
    numerology,
    compatibility,
    varshaphal,
    calendar_year,
    muhurta,
    prashna,
    chart_comparison,
    palmistry,
    tarot,
    feng_shui,
    life_threads,
    remedy_planner,
    hyperlocal_panchang,
    astrotwin_circles,
    expert_console,
    rituals,
    reality_check,
    expert_knowledge,
)

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
api_router.include_router(calendar_year.router, prefix="/calendar-year", tags=["calendar-year"])
api_router.include_router(muhurta.router, prefix="/muhurta", tags=["muhurta"])
api_router.include_router(prashna.router, prefix="/prashna", tags=["prashna"])
api_router.include_router(chart_comparison.router, prefix="/chart-comparison", tags=["chart-comparison"])
api_router.include_router(palmistry.router, prefix="/palmistry", tags=["palmistry"])
api_router.include_router(tarot.router, prefix="/tarot", tags=["tarot"])
api_router.include_router(feng_shui.router, prefix="/feng-shui", tags=["feng-shui"])
api_router.include_router(life_threads.router, prefix="/life-threads", tags=["life-threads"])
api_router.include_router(remedy_planner.router, prefix="/remedy-planner", tags=["remedy-planner"])
api_router.include_router(hyperlocal_panchang.router, prefix="/panchang", tags=["panchang"])
api_router.include_router(astrotwin_circles.router, prefix="/astrotwin", tags=["astrotwin-circles"])
api_router.include_router(expert_console.router, prefix="/expert", tags=["expert-console"])
api_router.include_router(rituals.router, prefix="/rituals", tags=["rituals"])
api_router.include_router(reality_check.router, prefix="/reality-check", tags=["reality-check"])
api_router.include_router(expert_knowledge.router, prefix="/admin/expert-knowledge", tags=["expert-knowledge"])
