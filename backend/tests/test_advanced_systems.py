"""
Comprehensive Test Suite for Advanced Astrological Systems

Tests for:
- Jaimini System (Chara Karakas, Karakamsha, Arudha Padas)
- Lal Kitab (Planetary Debts, Blind Planets, Remedies)
- Ashtakavarga (Bhinna, Sarva, Transit Analysis)

Includes:
- Unit tests
- Integration tests
- Performance tests
- Regression tests
"""

import pytest
import time
from datetime import date, datetime
from typing import Dict, Any

# Import services
from app.services.jaimini_service import jaimini_service
from app.services.lal_kitab_service import lal_kitab_service
from app.services.ashtakavarga_service import ashtakavarga_service


# ==================== Test Fixtures ====================

@pytest.fixture
def sample_chart_data() -> Dict[str, Any]:
    """Sample birth chart data for testing."""
    return {
        "planets": {
            "Sun": {
                "longitude": 268.5,
                "sign": "Sagittarius",
                "sign_num": 9,
                "house": 9,
                "is_retrograde": False
            },
            "Moon": {
                "longitude": 156.3,
                "sign": "Virgo",
                "sign_num": 6,
                "house": 6,
                "is_retrograde": False
            },
            "Mars": {
                "longitude": 298.4,
                "sign": "Capricorn",
                "sign_num": 10,
                "house": 10,
                "is_retrograde": False
            },
            "Mercury": {
                "longitude": 275.1,
                "sign": "Sagittarius",
                "sign_num": 9,
                "house": 9,
                "is_retrograde": False
            },
            "Jupiter": {
                "longitude": 125.7,
                "sign": "Leo",
                "sign_num": 5,
                "house": 5,
                "is_retrograde": False
            },
            "Venus": {
                "longitude": 285.2,
                "sign": "Capricorn",
                "sign_num": 10,
                "house": 10,
                "is_retrograde": False
            },
            "Saturn": {
                "longitude": 245.6,
                "sign": "Scorpio",
                "sign_num": 8,
                "house": 8,
                "is_retrograde": False
            },
            "Rahu": {
                "longitude": 95.0,
                "sign": "Cancer",
                "sign_num": 4,
                "house": 4,
                "is_retrograde": True
            },
            "Ketu": {
                "longitude": 275.0,
                "sign": "Capricorn",
                "sign_num": 10,
                "house": 10,
                "is_retrograde": True
            },
            "Ascendant": {
                "longitude": 30.0,
                "sign": "Taurus",
                "sign_num": 2,
                "house": 1
            }
        },
        "houses": {
            "1": {"sign": "Taurus", "sign_num": 2, "lord": "Venus"},
            "2": {"sign": "Gemini", "sign_num": 3, "lord": "Mercury"},
            "3": {"sign": "Cancer", "sign_num": 4, "lord": "Moon"},
            "4": {"sign": "Leo", "sign_num": 5, "lord": "Sun"},
            "5": {"sign": "Virgo", "sign_num": 6, "lord": "Mercury"},
            "6": {"sign": "Libra", "sign_num": 7, "lord": "Venus"},
            "7": {"sign": "Scorpio", "sign_num": 8, "lord": "Mars"},
            "8": {"sign": "Sagittarius", "sign_num": 9, "lord": "Jupiter"},
            "9": {"sign": "Capricorn", "sign_num": 10, "lord": "Saturn"},
            "10": {"sign": "Aquarius", "sign_num": 11, "lord": "Saturn"},
            "11": {"sign": "Pisces", "sign_num": 12, "lord": "Jupiter"},
            "12": {"sign": "Aries", "sign_num": 1, "lord": "Mars"}
        }
    }


@pytest.fixture
def sample_d9_chart() -> Dict[str, Any]:
    """Sample D9 (Navamsa) chart for testing."""
    return {
        "planets": {
            "Sun": {"longitude": 100.0, "sign": "Cancer", "sign_num": 4, "house": 3},
            "Moon": {"longitude": 210.0, "sign": "Scorpio", "sign_num": 8, "house": 7},
            "Mars": {"longitude": 15.0, "sign": "Aries", "sign_num": 1, "house": 1},
            "Mercury": {"longitude": 85.0, "sign": "Gemini", "sign_num": 3, "house": 2},
            "Jupiter": {"longitude": 190.0, "sign": "Libra", "sign_num": 7, "house": 6},
            "Venus": {"longitude": 135.0, "sign": "Leo", "sign_num": 5, "house": 4},
            "Saturn": {"longitude": 260.0, "sign": "Sagittarius", "sign_num": 9, "house": 8},
            "Ascendant": {"longitude": 45.0, "sign": "Taurus", "sign_num": 2, "house": 1}
        }
    }


# ==================== Jaimini System Tests ====================

class TestJaiminiService:
    """Test suite for Jaimini Astrology Service."""

    def test_service_initialization(self):
        """Test that Jaimini service initializes correctly."""
        assert jaimini_service is not None
        assert jaimini_service._initialized is True
        assert len(jaimini_service.MOVABLE_SIGNS) == 4
        assert len(jaimini_service.FIXED_SIGNS) == 4
        assert len(jaimini_service.DUAL_SIGNS) == 4

    def test_calculate_chara_karakas(self, sample_chart_data):
        """Test Chara Karakas calculation."""
        planets = sample_chart_data["planets"]
        karakas = jaimini_service.calculate_chara_karakas(planets)

        # Verify structure
        assert "AK" in karakas
        assert "AmK" in karakas
        assert "BK" in karakas
        assert "MK" in karakas
        assert "PK" in karakas
        assert "GK" in karakas
        assert "DK" in karakas

        # Verify all 7 karakas are assigned
        assert len(karakas) == 7

        # Mars has highest degree (298.4°) so should be AK
        assert karakas["AK"]["planet"] == "Mars"

    def test_get_atmakaraka(self, sample_chart_data):
        """Test Atmakaraka extraction."""
        planets = sample_chart_data["planets"]
        karakas = jaimini_service.calculate_chara_karakas(planets)
        atmakaraka = jaimini_service.get_atmakaraka(karakas)

        assert atmakaraka["planet"] == "Mars"
        assert "longitude" in atmakaraka
        assert "signification" in atmakaraka

    def test_calculate_karakamsha(self, sample_chart_data, sample_d9_chart):
        """Test Karakamsha calculation."""
        planets = sample_chart_data["planets"]
        karakas = jaimini_service.calculate_chara_karakas(planets)
        atmakaraka = jaimini_service.get_atmakaraka(karakas)

        karakamsha = jaimini_service.calculate_karakamsha(atmakaraka, sample_d9_chart)

        assert "sign" in karakamsha
        assert "house_in_d9" in karakamsha
        assert "lord" in karakamsha

    def test_calculate_arudha_pada(self, sample_chart_data):
        """Test single Arudha Pada calculation."""
        pada = jaimini_service.calculate_arudha_pada(1, sample_chart_data)

        assert "sign" in pada
        assert "house" in pada
        assert "lord" in pada

    def test_calculate_all_arudha_padas(self, sample_chart_data):
        """Test all Arudha Padas calculation."""
        arudha_padas = jaimini_service.calculate_all_arudha_padas(sample_chart_data)

        # Verify Arudha Lagna present (AL is the key)
        assert "AL" in arudha_padas

        # Verify all 12 Arudha Padas present (A2-A12 and AL)
        assert "AL" in arudha_padas
        for i in range(2, 13):
            key = f"A{i}"
            assert key in arudha_padas

    def test_get_sign_type(self):
        """Test sign type classification."""
        assert jaimini_service.get_sign_type(1) == "movable"  # Aries
        assert jaimini_service.get_sign_type(2) == "fixed"    # Taurus
        assert jaimini_service.get_sign_type(3) == "dual"     # Gemini

    def test_calculate_rashi_drishti(self):
        """Test Rashi Drishti (sign aspects)."""
        # Aries (movable) aspects fixed signs
        aspects = jaimini_service.calculate_rashi_drishti(1)
        assert 2 in aspects  # Taurus
        assert 5 in aspects  # Leo
        assert 8 in aspects  # Scorpio
        assert 11 in aspects  # Aquarius
        assert 1 not in aspects  # Not itself

    def test_performance_chara_karakas(self, sample_chart_data):
        """Performance test: Chara Karakas should calculate in < 10ms."""
        planets = sample_chart_data["planets"]

        start = time.time()
        for _ in range(100):
            jaimini_service.calculate_chara_karakas(planets)
        elapsed = time.time() - start

        avg_time = elapsed / 100
        assert avg_time < 0.01, f"Average time {avg_time:.4f}s exceeds 10ms"


# ==================== Lal Kitab Tests ====================

class TestLalKitabService:
    """Test suite for Lal Kitab Service."""

    def test_service_initialization(self):
        """Test that Lal Kitab service initializes correctly."""
        assert lal_kitab_service is not None
        assert lal_kitab_service._initialized is True
        assert len(lal_kitab_service.PAKKA_GHAR) == 9

    def test_detect_planetary_debts(self, sample_chart_data):
        """Test planetary debts detection."""
        debts = lal_kitab_service.detect_planetary_debts(sample_chart_data)

        assert "debts" in debts
        assert "total_debts" in debts
        assert "overall_severity" in debts
        assert isinstance(debts["debts"], list)

    def test_detect_blind_planets(self, sample_chart_data):
        """Test blind planets detection."""
        blind_planets = lal_kitab_service.detect_blind_planets(sample_chart_data)

        assert isinstance(blind_planets, list)

        # Saturn in 8th house should be blind
        saturn_blind = any(bp["planet"] == "Saturn" for bp in blind_planets)
        assert saturn_blind, "Saturn in 8th house should be blind"

    def test_is_planet_blind(self, sample_chart_data):
        """Test individual planet blindness check."""
        # Saturn in 8th house (from sample data)
        is_blind = lal_kitab_service.is_planet_blind("Saturn", sample_chart_data)
        assert is_blind is True

    def test_check_pakka_ghar_placement(self, sample_chart_data):
        """Test Pakka Ghar placement analysis."""
        placements = lal_kitab_service.check_pakka_ghar_placement(sample_chart_data)

        assert "Sun" in placements
        assert "Moon" in placements

        # Each placement should have required fields
        for planet, data in placements.items():
            assert "pakka_ghar" in data
            assert "actual_house" in data
            assert "in_pakka_ghar" in data
            assert "result" in data

    def test_get_remedies_for_debt(self):
        """Test debt-specific remedies."""
        remedies = lal_kitab_service.get_remedies_for_debt("father")

        assert isinstance(remedies, list)
        assert len(remedies) > 0

    def test_get_general_remedies(self, sample_chart_data):
        """Test general remedies."""
        remedies = lal_kitab_service.get_general_remedies(sample_chart_data)

        assert isinstance(remedies, list)
        assert len(remedies) > 0

    def test_analyze_lal_kitab_chart(self, sample_chart_data):
        """Test comprehensive Lal Kitab analysis."""
        analysis = lal_kitab_service.analyze_lal_kitab_chart(sample_chart_data)

        assert "debts" in analysis
        assert "blind_planets" in analysis
        assert "pakka_ghar_status" in analysis
        assert "priority_remedies" in analysis
        assert "overall_assessment" in analysis

    def test_performance_debt_detection(self, sample_chart_data):
        """Performance test: Debt detection should complete in < 50ms."""
        start = time.time()
        for _ in range(100):
            lal_kitab_service.detect_planetary_debts(sample_chart_data)
        elapsed = time.time() - start

        avg_time = elapsed / 100
        assert avg_time < 0.05, f"Average time {avg_time:.4f}s exceeds 50ms"


# ==================== Ashtakavarga Tests ====================

class TestAshtakavargaService:
    """Test suite for Ashtakavarga Service."""

    def test_service_initialization(self):
        """Test that Ashtakavarga service initializes correctly."""
        assert ashtakavarga_service is not None
        assert ashtakavarga_service._initialized is True
        assert len(ashtakavarga_service.BENEFIC_POINTS) == 7  # 7 planets

    def test_calculate_bhinna_ashtakavarga(self, sample_chart_data):
        """Test Bhinna Ashtakavarga calculation for single planet."""
        bhinna = ashtakavarga_service.calculate_bhinna_ashtakavarga("Sun", sample_chart_data)

        assert "planet" in bhinna
        assert bhinna["planet"] == "Sun"
        assert "bindus_by_house" in bhinna
        assert "total_bindus" in bhinna

        # Should have bindus for all 12 houses
        assert len(bhinna["bindus_by_house"]) == 12

        # Total bindus should be sum of all houses
        total = sum(bhinna["bindus_by_house"].values())
        assert total == bhinna["total_bindus"]

    def test_calculate_all_bhinna_ashtakavarga(self, sample_chart_data):
        """Test Bhinna Ashtakavarga for all planets."""
        bhinna_charts = ashtakavarga_service.calculate_all_bhinna_ashtakavarga(sample_chart_data)

        # Should have charts for all 7 planets
        assert len(bhinna_charts) == 7
        assert "Sun" in bhinna_charts
        assert "Moon" in bhinna_charts
        assert "Saturn" in bhinna_charts

    def test_calculate_sarva_ashtakavarga(self, sample_chart_data):
        """Test Sarva Ashtakavarga (collective chart)."""
        sarva = ashtakavarga_service.calculate_sarva_ashtakavarga(sample_chart_data)

        assert "bindus_by_house" in sarva
        assert "total_bindus" in sarva
        assert "house_strength" in sarva
        assert "strongest_houses" in sarva
        assert "weakest_houses" in sarva

        # Total bindus should be reasonable (typically 330-350)
        assert 200 < sarva["total_bindus"] < 400

    def test_calculate_graha_pinda(self, sample_chart_data):
        """Test Graha Pinda calculation."""
        pinda = ashtakavarga_service.calculate_graha_pinda("Sun", sample_chart_data)

        assert isinstance(pinda, int)
        assert pinda >= 0

    def test_calculate_all_pindas(self, sample_chart_data):
        """Test all Pinda calculations."""
        pindas = ashtakavarga_service.calculate_all_pindas(sample_chart_data)

        assert "graha_pindas" in pindas
        assert "rashi_pindas" in pindas
        assert "strongest_planets" in pindas
        assert "weakest_planets" in pindas

        # Should have pindas for all 7 planets
        assert len(pindas["graha_pindas"]) == 7

    def test_analyze_transit(self, sample_chart_data):
        """Test transit strength analysis."""
        transit = ashtakavarga_service.analyze_transit("Saturn", 7, sample_chart_data)

        assert "transiting_planet" in transit
        assert transit["transiting_planet"] == "Saturn"
        assert "current_house" in transit
        assert "bhinna_bindus" in transit
        assert "sarva_bindus" in transit
        assert "transit_strength" in transit
        assert "effects" in transit

    def test_get_kakshya_lord(self):
        """Test Kakshya lord calculation."""
        # Test various longitudes within a sign
        lord1 = ashtakavarga_service.get_kakshya_lord(30.0)  # Start of Taurus
        assert lord1 == "Saturn"

        lord2 = ashtakavarga_service.get_kakshya_lord(37.5)  # 7.5° into Taurus
        assert lord2 == "Mars"

    def test_analyze_ashtakavarga(self, sample_chart_data):
        """Test comprehensive Ashtakavarga analysis."""
        analysis = ashtakavarga_service.analyze_ashtakavarga(sample_chart_data)

        assert "sarva_ashtakavarga" in analysis
        assert "bhinna_ashtakavarga" in analysis
        assert "pindas" in analysis
        assert "kakshya_positions" in analysis
        assert "summary" in analysis
        assert "interpretation" in analysis

    def test_performance_sarva_calculation(self, sample_chart_data):
        """Performance test: Sarva Ashtakavarga should calculate in < 200ms."""
        start = time.time()
        for _ in range(50):
            ashtakavarga_service.calculate_sarva_ashtakavarga(sample_chart_data)
        elapsed = time.time() - start

        avg_time = elapsed / 50
        assert avg_time < 0.2, f"Average time {avg_time:.4f}s exceeds 200ms"


# ==================== Integration Tests ====================

class TestIntegration:
    """Integration tests combining multiple systems."""

    def test_full_jaimini_analysis(self, sample_chart_data, sample_d9_chart):
        """Test full Jaimini analysis workflow."""
        birth_date = date(1990, 1, 15)

        analysis = jaimini_service.analyze_jaimini_chart(
            sample_chart_data,
            sample_d9_chart,
            birth_date
        )

        assert "chara_karakas" in analysis
        assert "karakamsha" in analysis
        assert "arudha_padas" in analysis
        assert "chara_dasha" in analysis

    def test_full_lal_kitab_analysis(self, sample_chart_data):
        """Test full Lal Kitab analysis workflow."""
        analysis = lal_kitab_service.analyze_lal_kitab_chart(sample_chart_data)

        assert "debts" in analysis
        assert "blind_planets" in analysis
        assert "priority_remedies" in analysis
        assert len(analysis["priority_remedies"]) > 0

    def test_full_ashtakavarga_analysis(self, sample_chart_data):
        """Test full Ashtakavarga analysis workflow."""
        analysis = ashtakavarga_service.analyze_ashtakavarga(sample_chart_data)

        assert "summary" in analysis
        assert analysis["summary"]["total_bindus"] > 0


# ==================== Regression Tests ====================

class TestRegression:
    """Regression tests to ensure no breaking changes."""

    def test_chara_karakas_consistency(self, sample_chart_data):
        """Ensure Chara Karakas calculation is consistent."""
        planets = sample_chart_data["planets"]

        # Run multiple times and verify same result
        result1 = jaimini_service.calculate_chara_karakas(planets)
        result2 = jaimini_service.calculate_chara_karakas(planets)

        assert result1["AK"]["planet"] == result2["AK"]["planet"]

    def test_ashtakavarga_total_consistency(self, sample_chart_data):
        """Ensure Sarva Ashtakavarga total is consistent."""
        result1 = ashtakavarga_service.calculate_sarva_ashtakavarga(sample_chart_data)
        result2 = ashtakavarga_service.calculate_sarva_ashtakavarga(sample_chart_data)

        assert result1["total_bindus"] == result2["total_bindus"]


# ==================== Edge Case Tests ====================

class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_chart_data(self):
        """Test behavior with empty chart data."""
        empty_chart = {"planets": {}, "houses": {}}

        # Should not crash
        karakas = jaimini_service.calculate_chara_karakas({})
        assert karakas == {}

    def test_missing_planets(self):
        """Test behavior with missing planets."""
        incomplete_chart = {
            "planets": {
                "Sun": {"longitude": 100, "house": 4, "sign_num": 4}
            }
        }

        # Should handle gracefully
        debts = lal_kitab_service.detect_planetary_debts(incomplete_chart)
        assert "debts" in debts

    def test_invalid_house_number(self, sample_chart_data):
        """Test transit analysis with invalid house."""
        # Should handle out of range gracefully
        # This would be handled at API level, but service should be robust
        try:
            ashtakavarga_service.analyze_transit("Sun", 13, sample_chart_data)
        except:
            pass  # Expected to fail or handle gracefully


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
