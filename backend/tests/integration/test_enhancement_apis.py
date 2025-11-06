"""
Integration tests for Phase 4 Enhancement APIs
Tests remedies, transits, shadbala, and yoga endpoints
"""

import pytest
from unittest.mock import patch, AsyncMock
from datetime import datetime


class TestRemedyAPI:
    """Test remedy generation API"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_generate_remedies_success(self, async_client, mock_supabase_service, sample_chart_data):
        """Test successful remedy generation"""

        with patch('app.api.v1.endpoints.enhancements.supabase_service', mock_supabase_service):
            with patch('app.api.v1.endpoints.enhancements.remedy_service') as mock_remedy:
                mock_remedy.generate_remedies.return_value = {
                    "remedies": [
                        {
                            "type": "mantra",
                            "title": "Sun Mantra",
                            "description": "Chant Sun mantra for strength",
                            "instructions": "Chant 108 times daily",
                            "frequency": "Daily",
                            "duration": "40 days",
                            "difficulty": "easy",
                            "cost": "free",
                            "planet": "Sun",
                            "benefits": ["Confidence", "Leadership"]
                        }
                    ],
                    "analysis": {},
                    "priority_planets": ["Sun"],
                    "current_dasha": "Sun",
                    "notes": "Focus on Solar remedies"
                }

                mock_supabase_service.get_chart.return_value = {"chart_data": sample_chart_data}

                response = await async_client.post(
                    "/api/v1/enhancements/remedies/generate",
                    json={
                        "profile_id": "test-profile-123",
                        "domain": "career",
                        "max_remedies": 5,
                        "include_practical": True
                    }
                )

                assert response.status_code == 200
                data = response.json()
                assert "remedies" in data
                assert len(data["remedies"]) > 0

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_generate_remedies_profile_not_found(self, async_client, mock_supabase_service):
        """Test remedy generation with non-existent profile"""

        mock_supabase_service.get_profile.return_value = None

        with patch('app.api.v1.endpoints.enhancements.supabase_service', mock_supabase_service):
            response = await async_client.post(
                "/api/v1/enhancements/remedies/generate",
                json={
                    "profile_id": "non-existent",
                    "max_remedies": 5
                },
                )

            assert response.status_code == 404


class TestTransitAPI:
    """Test transit calculation API"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_calculate_transits_success(self, async_client, mock_supabase_service, sample_chart_data):
        """Test successful transit calculation"""

        with patch('app.api.v1.endpoints.enhancements.supabase_service', mock_supabase_service):
            with patch('app.api.v1.endpoints.enhancements.transit_service') as mock_transit:
                mock_transit.calculate_current_transits.return_value = {
                    "transit_date": datetime.now().isoformat(),
                    "current_positions": [],
                    "significant_aspects": [],
                    "upcoming_sign_changes": [],
                    "summary": "Test transit summary",
                    "focus_areas": ["career"]
                }

                mock_supabase_service.get_chart.return_value = {"chart_data": sample_chart_data}

                response = await async_client.post(
                    "/api/v1/enhancements/transits/current",
                    json={
                        "profile_id": "test-profile-123",
                        "include_timeline": True
                    }
                )

                assert response.status_code == 200
                data = response.json()
                assert "transit_date" in data
                assert "current_positions" in data


class TestShadbalaAPI:
    """Test Shadbala calculation API"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_calculate_shadbala_success(self, async_client, mock_supabase_service, sample_chart_data):
        """Test successful Shadbala calculation"""

        with patch('app.api.v1.endpoints.enhancements.supabase_service', mock_supabase_service):
            with patch('app.api.v1.endpoints.enhancements.shadbala_service') as mock_shadbala:
                mock_shadbala.calculate_shadbala.return_value = {
                    "shadbala_by_planet": {
                        "Sun": {
                            "total_shadbala": 450.0,
                            "required_shadbala": 390.0,
                            "percentage": 115.4,
                            "strength_rating": "Strong",
                            "components": {}
                        }
                    },
                    "strongest_planet": "Sun",
                    "weakest_planet": "Saturn",
                    "average_percentage": 100.0,
                    "planets_above_required": 5,
                    "overall_strength": "Good"
                }

                mock_supabase_service.get_chart.return_value = {"chart_data": sample_chart_data}

                response = await async_client.post(
                    "/api/v1/enhancements/shadbala/calculate",
                    json={
                        "profile_id": "test-profile-123",
                        "include_breakdown": True,
                        "comparison": True
                    }
                )

                assert response.status_code == 200
                data = response.json()
                assert "planetary_strengths" in data
                assert "strongest_planet" in data


class TestYogaAPI:
    """Test Yoga detection API"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_analyze_yogas_success(self, async_client, mock_supabase_service, sample_chart_data):
        """Test successful yoga analysis"""

        with patch('app.api.v1.endpoints.enhancements.supabase_service', mock_supabase_service):
            with patch('app.api.v1.endpoints.enhancements.extended_yoga_service') as mock_yoga:
                mock_yoga.detect_extended_yogas.return_value = [
                    {
                        "name": "Gaja Kesari Yoga",
                        "description": "Jupiter in Kendra from Moon",
                        "strength": "Strong",
                        "category": "Wealth & Wisdom"
                    },
                    {
                        "name": "Raj Yoga",
                        "description": "Kendra-Trikona lords",
                        "strength": "Very Strong",
                        "category": "Power & Status"
                    }
                ]

                mock_supabase_service.get_chart.return_value = {"chart_data": sample_chart_data}

                response = await async_client.post(
                    "/api/v1/enhancements/yogas/analyze",
                    json={
                        "profile_id": "test-profile-123",
                        "include_all": True
                    }
                )

                assert response.status_code == 200
                data = response.json()
                assert "yogas" in data
                assert "total_yogas" in data
                assert data["total_yogas"] == 2
                assert "chart_quality" in data

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_analyze_yogas_chart_not_found(self, async_client, mock_supabase_service):
        """Test yoga analysis when chart doesn't exist"""

        mock_supabase_service.get_chart.return_value = None

        with patch('app.api.v1.endpoints.enhancements.supabase_service', mock_supabase_service):
            response = await async_client.post(
                "/api/v1/enhancements/yogas/analyze",
                json={
                    "profile_id": "test-profile-123",
                    "include_all": True
                },
                )

            assert response.status_code == 404


class TestRectificationAPI:
    """Test birth time rectification API"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_rectify_birth_time_success(self, async_client):
        """Test successful birth time rectification"""

        with patch('app.api.v1.endpoints.enhancements.rectification_service') as mock_rect:
            mock_rect.rectify_birth_time.return_value = {
                "rectification": {
                    "top_candidates": [
                        {
                            "birth_time": "14:32:00",
                            "confidence_score": 85.5,
                            "ascendant": "Leo",
                            "moon_sign": "Scorpio",
                            "event_matches": [],
                            "reasoning": "Best match for events"
                        }
                    ],
                    "analysis_summary": "Analyzed 2 events",
                    "events_analyzed": 2,
                    "candidates_tested": 30,
                    "recommendation": "Use 14:32:00"
                }
            }

            response = await async_client.post(
                "/api/v1/enhancements/rectification/calculate",
                json={
                    "name": "Test User",
                    "birth_date": "1990-01-15",
                    "approximate_time": "14:30:00",
                    "time_window_minutes": 30,
                    "birth_lat": 28.6139,
                    "birth_lon": 77.2090,
                    "birth_timezone": "Asia/Kolkata",
                    "birth_city": "New Delhi",
                    "event_anchors": [
                        {
                            "event_type": "marriage",
                            "event_date": "2015-06-15",
                            "significance": 9
                        }
                    ]
                },
                )

            assert response.status_code == 200
            data = response.json()
            assert "rectification" in data or "top_candidates" in data


# ============================================================================
# Performance Tests for APIs
# ============================================================================

@pytest.mark.performance
@pytest.mark.integration
class TestAPIPerformance:
    """Performance tests for API endpoints"""

    @pytest.mark.asyncio
    async def test_yoga_analysis_performance(self, async_client, mock_supabase_service, sample_chart_data, performance_threshold):
        """Test yoga analysis response time"""
        import time

        mock_supabase_service.get_chart.return_value = {"chart_data": sample_chart_data}

        with patch('app.api.v1.endpoints.enhancements.supabase_service', mock_supabase_service):
            start = time.time()

            response = await async_client.post(
                "/api/v1/enhancements/yogas/analyze",
                json={
                    "profile_id": "test-profile-123",
                    "include_all": True
                },
                )

            duration = time.time() - start

            assert response.status_code == 200
            # API should respond in under 500ms
            assert duration < performance_threshold["medium"], f"API took {duration}s, expected < {performance_threshold['medium']}s"

    @pytest.mark.asyncio
    async def test_numerology_calculation_performance(self, async_client, performance_threshold):
        """Test numerology calculation response time"""
        import time

        start = time.time()

        response = await async_client.post(
            "/api/v1/numerology/calculate",
            json={
                "full_name": "John Doe",
                "birth_date": "1990-01-15",
                "system": "both"
            },
        )

        duration = time.time() - start

        assert response.status_code == 200
        # Should be very fast (< 100ms)
        assert duration < performance_threshold["fast"], f"Numerology API took {duration}s, expected < {performance_threshold['fast']}s"
