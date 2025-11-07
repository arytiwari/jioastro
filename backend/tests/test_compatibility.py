"""
Comprehensive Test Suite for Vedic Astrology Compatibility Matching

Tests for:
- Nakshatra calculations
- Ashtakoot (Guna Milan) matching
- Manglik Dosha analysis
- Complete compatibility analysis

Includes:
- Unit tests
- Integration tests
- Performance tests
"""

import pytest
import time
from typing import Dict, Any

from app.services.compatibility_service import compatibility_service


# ==================== Test Fixtures ====================

@pytest.fixture
def sample_boy_chart() -> Dict[str, Any]:
    """Sample boy's birth chart data for testing."""
    return {
        "planets": {
            "Sun": {"longitude": 268.5, "sign": "Sagittarius", "house": 9},
            "Moon": {"longitude": 156.3, "sign": "Virgo", "house": 6},  # Hasta nakshatra
            "Mars": {"longitude": 298.4, "sign": "Capricorn", "house": 10},
            "Mercury": {"longitude": 245.2, "sign": "Sagittarius", "house": 9},
            "Jupiter": {"longitude": 78.9, "sign": "Gemini", "house": 3},
            "Venus": {"longitude": 287.1, "sign": "Capricorn", "house": 10},
            "Saturn": {"longitude": 134.5, "sign": "Leo", "house": 5},
            "Rahu": {"longitude": 198.7, "sign": "Libra", "house": 7},
            "Ketu": {"longitude": 18.7, "sign": "Aries", "house": 1}
        }
    }


@pytest.fixture
def sample_girl_chart() -> Dict[str, Any]:
    """Sample girl's birth chart data for testing."""
    return {
        "planets": {
            "Sun": {"longitude": 45.2, "sign": "Taurus", "house": 2},
            "Moon": {"longitude": 123.7, "sign": "Leo", "house": 5},  # Magha nakshatra
            "Mars": {"longitude": 189.3, "sign": "Libra", "house": 7},
            "Mercury": {"longitude": 52.8, "sign": "Taurus", "house": 2},
            "Jupiter": {"longitude": 156.4, "sign": "Virgo", "house": 6},
            "Venus": {"longitude": 34.2, "sign": "Taurus", "house": 2},
            "Saturn": {"longitude": 267.8, "sign": "Sagittarius", "house": 9},
            "Rahu": {"longitude": 98.2, "sign": "Cancer", "house": 4},
            "Ketu": {"longitude": 278.2, "sign": "Capricorn", "house": 10}
        }
    }


@pytest.fixture
def manglik_chart() -> Dict[str, Any]:
    """Chart with Manglik Dosha (Mars in 7th house)."""
    return {
        "planets": {
            "Sun": {"longitude": 45.2, "sign": "Taurus", "house": 2},
            "Moon": {"longitude": 123.7, "sign": "Leo", "house": 5},
            "Mars": {"longitude": 189.3, "sign": "Libra", "house": 7},  # Manglik
            "Mercury": {"longitude": 52.8, "sign": "Taurus", "house": 2},
            "Jupiter": {"longitude": 156.4, "sign": "Virgo", "house": 6},
            "Venus": {"longitude": 34.2, "sign": "Taurus", "house": 2},
            "Saturn": {"longitude": 267.8, "sign": "Sagittarius", "house": 9}
        }
    }


@pytest.fixture
def non_manglik_chart() -> Dict[str, Any]:
    """Chart without Manglik Dosha."""
    return {
        "planets": {
            "Sun": {"longitude": 268.5, "sign": "Sagittarius", "house": 9},
            "Moon": {"longitude": 156.3, "sign": "Virgo", "house": 6},
            "Mars": {"longitude": 298.4, "sign": "Capricorn", "house": 10},  # Not manglik
            "Mercury": {"longitude": 245.2, "sign": "Sagittarius", "house": 9},
            "Jupiter": {"longitude": 78.9, "sign": "Gemini", "house": 3},
            "Venus": {"longitude": 287.1, "sign": "Capricorn", "house": 10},
            "Saturn": {"longitude": 134.5, "sign": "Leo", "house": 5}
        }
    }


# ==================== Unit Tests: Nakshatra Calculations ====================

class TestNakshatraCalculations:
    """Test Nakshatra calculations."""

    def test_get_nakshatra_ashwini(self):
        """Test nakshatra calculation for Ashwini (0-13.33°)."""
        result = compatibility_service.get_nakshatra(5.0)
        assert result["name"] == "Ashwini"
        assert result["number"] == 1
        assert 1 <= result["pada"] <= 4

    def test_get_nakshatra_revati(self):
        """Test nakshatra calculation for Revati (last nakshatra)."""
        result = compatibility_service.get_nakshatra(356.0)
        assert result["name"] == "Revati"
        assert result["number"] == 27

    def test_get_nakshatra_uttara_phalguni(self):
        """Test nakshatra calculation for Uttara Phalguni."""
        result = compatibility_service.get_nakshatra(156.3)
        assert result["name"] == "Uttara Phalguni"
        assert result["number"] == 12

    def test_nakshatra_pada_calculation(self):
        """Test pada (quarter) calculation within nakshatra."""
        # Test all 4 padas
        nakshatra_start = 0.0  # Ashwini starts at 0°
        nakshatra_size = 360.0 / 27.0
        pada_size = nakshatra_size / 4

        for pada in range(1, 5):
            position = nakshatra_start + (pada - 0.5) * pada_size
            result = compatibility_service.get_nakshatra(position)
            assert result["pada"] == pada


# ==================== Unit Tests: Ashtakoot Factors ====================

class TestAshtakootFactors:
    """Test individual Ashtakoot (Guna Milan) factors."""

    def test_calculate_varna(self):
        """Test Varna calculation (max 1 point)."""
        result = compatibility_service.calculate_varna("Hasta", "Magha")
        assert result["name"] == "Varna"
        assert result["max_points"] == 1
        assert 0 <= result["obtained_points"] <= 1
        assert "boy_value" in result
        assert "girl_value" in result

    def test_calculate_vashya(self):
        """Test Vashya calculation (max 2 points)."""
        result = compatibility_service.calculate_vashya("Hasta", "Magha")
        assert result["name"] == "Vashya"
        assert result["max_points"] == 2
        assert 0 <= result["obtained_points"] <= 2

    def test_calculate_tara(self):
        """Test Tara calculation (max 3 points)."""
        result = compatibility_service.calculate_tara(13, 10)  # Hasta and Magha
        assert result["name"] == "Tara"
        assert result["max_points"] == 3
        assert 0 <= result["obtained_points"] <= 3

    def test_calculate_yoni(self):
        """Test Yoni calculation (max 4 points)."""
        result = compatibility_service.calculate_yoni("Hasta", "Magha")
        assert result["name"] == "Yoni"
        assert result["max_points"] == 4
        assert 0 <= result["obtained_points"] <= 4

    def test_calculate_graha_maitri(self, sample_boy_chart, sample_girl_chart):
        """Test Graha Maitri calculation (max 5 points)."""
        result = compatibility_service.calculate_graha_maitri(
            sample_boy_chart, sample_girl_chart, "Hasta", "Magha"
        )
        assert result["name"] == "Graha Maitri"
        assert result["max_points"] == 5
        assert 0 <= result["obtained_points"] <= 5
        assert "relationship" in result

    def test_calculate_gana(self):
        """Test Gana calculation (max 6 points)."""
        result = compatibility_service.calculate_gana("Hasta", "Magha")
        assert result["name"] == "Gana"
        assert result["max_points"] == 6
        assert 0 <= result["obtained_points"] <= 6

    def test_calculate_bhakoot(self):
        """Test Bhakoot calculation (max 7 points)."""
        result = compatibility_service.calculate_bhakoot("Hasta", "Magha")
        assert result["name"] == "Bhakoot"
        assert result["max_points"] == 7
        assert result["obtained_points"] in [0, 7]  # Bhakoot is either 0 or 7

    def test_calculate_nadi(self):
        """Test Nadi calculation (max 8 points)."""
        result = compatibility_service.calculate_nadi("Hasta", "Magha")
        assert result["name"] == "Nadi"
        assert result["max_points"] == 8
        assert result["obtained_points"] in [0, 8]  # Nadi is either 0 or 8


# ==================== Unit Tests: Manglik Dosha ====================

class TestManglikDosha:
    """Test Manglik Dosha analysis."""

    def test_manglik_in_seventh_house(self, manglik_chart):
        """Test Manglik detection when Mars is in 7th house."""
        result = compatibility_service.calculate_manglik_dosha(manglik_chart)
        assert result["is_manglik"] is True
        assert result["mars_house"] == 7
        assert result["severity"] in ["high", "medium", "none"]

    def test_non_manglik_chart(self, non_manglik_chart):
        """Test non-Manglik chart."""
        result = compatibility_service.calculate_manglik_dosha(non_manglik_chart)
        assert result["is_manglik"] is False
        assert result["severity"] == "none"

    def test_manglik_severity_levels(self):
        """Test different severity levels of Manglik Dosha."""
        # High severity houses: 1, 7, 8
        high_severity_houses = [1, 7, 8]
        medium_severity_houses = [4, 12]

        for house in high_severity_houses:
            chart = {"planets": {"Mars": {"house": house}}}
            result = compatibility_service.calculate_manglik_dosha(chart)
            assert result["is_manglik"] is True
            assert result["severity"] == "high"

        for house in medium_severity_houses:
            chart = {"planets": {"Mars": {"house": house}}}
            result = compatibility_service.calculate_manglik_dosha(chart)
            assert result["is_manglik"] is True
            assert result["severity"] == "medium"

    def test_manglik_cancellations(self):
        """Test Manglik Dosha cancellation scenarios."""
        # Mars in own sign (Aries or Scorpio)
        chart_aries = {
            "planets": {
                "Mars": {"house": 7, "sign": "Aries"},
                "Jupiter": {"house": 1}
            }
        }
        result = compatibility_service.calculate_manglik_dosha(chart_aries)
        assert len(result["cancellations"]) > 0


# ==================== Integration Tests ====================

class TestCompatibilityAnalysis:
    """Test complete compatibility analysis."""

    def test_complete_analysis(self, sample_boy_chart, sample_girl_chart):
        """Test complete compatibility analysis."""
        result = compatibility_service.analyze_compatibility(
            sample_boy_chart, sample_girl_chart
        )

        # Check structure
        assert "boy_nakshatra" in result
        assert "girl_nakshatra" in result
        assert "guna_milan" in result
        assert "manglik_analysis" in result
        assert "overall_compatibility" in result

        # Check guna milan
        guna_milan = result["guna_milan"]
        assert "total_points" in guna_milan
        assert "max_points" in guna_milan
        assert guna_milan["max_points"] == 36
        assert 0 <= guna_milan["total_points"] <= 36
        assert "percentage" in guna_milan
        assert "factors" in guna_milan
        assert len(guna_milan["factors"]) == 8

    def test_compatibility_rating_excellent(self, sample_boy_chart, sample_girl_chart):
        """Test compatibility rating for high scores."""
        result = compatibility_service.analyze_compatibility(
            sample_boy_chart, sample_girl_chart
        )

        total_points = result["guna_milan"]["total_points"]
        level = result["overall_compatibility"]["level"]

        if total_points >= 28:
            assert level == "excellent"
        elif total_points >= 24:
            assert level == "very_good"
        elif total_points >= 18:
            assert level == "good"

    def test_manglik_compatibility(self, manglik_chart, non_manglik_chart):
        """Test Manglik compatibility between charts."""
        result = compatibility_service.analyze_compatibility(
            manglik_chart, non_manglik_chart
        )

        manglik_analysis = result["manglik_analysis"]
        assert "boy_manglik" in manglik_analysis
        assert "girl_manglik" in manglik_analysis
        assert "compatible" in manglik_analysis

    def test_both_manglik_cancellation(self, manglik_chart):
        """Test that both partners being Manglik cancels the dosha."""
        result = compatibility_service.analyze_compatibility(
            manglik_chart, manglik_chart
        )

        manglik_analysis = result["manglik_analysis"]
        # Both being manglik should be compatible
        assert manglik_analysis["compatible"] is True


# ==================== Performance Tests ====================

class TestPerformance:
    """Test performance benchmarks."""

    def test_nakshatra_calculation_speed(self):
        """Test nakshatra calculation performance (<1ms per calculation)."""
        iterations = 1000
        start_time = time.time()

        for i in range(iterations):
            compatibility_service.get_nakshatra(i % 360)

        end_time = time.time()
        avg_time = (end_time - start_time) / iterations

        assert avg_time < 0.001, f"Nakshatra calculation took {avg_time*1000:.2f}ms (target: <1ms)"

    def test_ashtakoot_calculation_speed(self):
        """Test Ashtakoot factor calculation speed (<5ms per factor)."""
        iterations = 100
        start_time = time.time()

        for i in range(iterations):
            compatibility_service.calculate_gana("Hasta", "Magha")
            compatibility_service.calculate_yoni("Hasta", "Magha")
            compatibility_service.calculate_nadi("Hasta", "Magha")

        end_time = time.time()
        avg_time = (end_time - start_time) / (iterations * 3)

        assert avg_time < 0.005, f"Ashtakoot factor calculation took {avg_time*1000:.2f}ms (target: <5ms)"

    def test_complete_analysis_speed(self, sample_boy_chart, sample_girl_chart):
        """Test complete compatibility analysis speed (<100ms)."""
        start_time = time.time()

        result = compatibility_service.analyze_compatibility(
            sample_boy_chart, sample_girl_chart
        )

        end_time = time.time()
        elapsed_time = end_time - start_time

        assert elapsed_time < 0.1, f"Complete analysis took {elapsed_time*1000:.2f}ms (target: <100ms)"


# ==================== Edge Case Tests ====================

class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_same_nakshatra_compatibility(self, sample_boy_chart):
        """Test compatibility when both partners have same nakshatra."""
        result = compatibility_service.analyze_compatibility(
            sample_boy_chart, sample_boy_chart
        )

        assert result is not None
        assert result["boy_nakshatra"]["name"] == result["girl_nakshatra"]["name"]

    def test_missing_moon_data(self):
        """Test handling of missing Moon data - defaults to 0."""
        incomplete_chart = {"planets": {}}

        # Should use Moon longitude of 0 for missing data
        result = compatibility_service.analyze_compatibility(incomplete_chart, incomplete_chart)
        assert result is not None
        # Both should have Ashwini nakshatra (longitude 0)
        assert result["boy_nakshatra"]["name"] == "Ashwini"
        assert result["girl_nakshatra"]["name"] == "Ashwini"

    def test_boundary_longitudes(self):
        """Test nakshatra calculation at boundary longitudes."""
        # Test at 0°
        result_zero = compatibility_service.get_nakshatra(0.0)
        assert result_zero["name"] == "Ashwini"

        # Test at 359.99°
        result_end = compatibility_service.get_nakshatra(359.99)
        assert result_end["name"] == "Revati"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
