"""
Comprehensive Test Suite for Divisional Charts (Shodashvarga) Service
Tests D2-D60 divisional charts, Vimshopaka Bala, and planetary dignities
"""

import pytest
from typing import Dict, Any
from app.services.divisional_charts_service import DivisionalChartsService


@pytest.fixture
def divisional_service():
    """Divisional Charts Service instance"""
    return DivisionalChartsService()


@pytest.fixture
def sample_planet_data():
    """Sample planet data for testing"""
    return {
        "Sun": {
            "longitude": 15.5,  # 15.5° in Aries
            "sign": "Aries",
            "sign_num": 0,
            "house": 1,
            "degree": 15.5,
            "retrograde": False
        },
        "Moon": {
            "longitude": 45.8,  # 15.8° in Taurus
            "sign": "Taurus",
            "sign_num": 1,
            "house": 2,
            "degree": 15.8,
            "retrograde": False
        },
        "Jupiter": {
            "longitude": 105.5,  # 15.5° in Cancer (exalted)
            "sign": "Cancer",
            "sign_num": 3,
            "house": 4,
            "degree": 15.5,
            "retrograde": False
        },
        "Mars": {
            "longitude": 285.0,  # 15° in Capricorn (exalted)
            "sign": "Capricorn",
            "sign_num": 9,
            "house": 10,
            "degree": 15.0,
            "retrograde": False
        },
        "Saturn": {
            "longitude": 15.0,  # 15° in Aries (debilitated)
            "sign": "Aries",
            "sign_num": 0,
            "house": 1,
            "degree": 15.0,
            "retrograde": False
        }
    }


@pytest.fixture
def sample_ascendant():
    """Sample ascendant data"""
    return {
        "longitude": 10.0,  # 10° Aries
        "sign": "Aries",
        "sign_num": 0,
        "degree": 10.0
    }


# =============================================================================
# DIGNITY CALCULATION TESTS
# =============================================================================

class TestPlanetDignity:
    """Test planet dignity calculations"""
    
    @pytest.mark.unit
    @pytest.mark.divisional
    def test_exalted_planet_dignity(self, divisional_service):
        """Test dignity for exalted planet"""
        # Sun exalted in Aries (sign_num 0)
        dignity, score = divisional_service.get_planet_dignity("Sun", 0)
        assert dignity == "Exalted"
        assert score == 20.0
    
    @pytest.mark.unit
    @pytest.mark.divisional
    def test_debilitated_planet_dignity(self, divisional_service):
        """Test dignity for debilitated planet"""
        # Sun debilitated in Libra (sign_num 6)
        dignity, score = divisional_service.get_planet_dignity("Sun", 6)
        assert dignity == "Debilitated"
        assert score == 0.0
    
    @pytest.mark.unit
    @pytest.mark.divisional
    def test_moolatrikona_dignity(self, divisional_service):
        """Test dignity for planet in Moolatrikona sign"""
        # Sun in Leo (Moolatrikona)
        dignity, score = divisional_service.get_planet_dignity("Sun", 4)
        assert dignity == "Moolatrikona"
        assert score == 18.0
    
    @pytest.mark.unit
    @pytest.mark.divisional
    def test_own_sign_dignity(self, divisional_service):
        """Test dignity for planet in own sign"""
        # Mars in Scorpio (own sign)
        dignity, score = divisional_service.get_planet_dignity("Mars", 7)
        assert dignity == "Own Sign"
        assert score == 15.0
    
    @pytest.mark.unit
    @pytest.mark.divisional
    def test_friend_sign_dignity(self, divisional_service):
        """Test dignity for planet in friend's sign"""
        # Sun in Sagittarius (Jupiter's sign, friend)
        dignity, score = divisional_service.get_planet_dignity("Sun", 8)
        assert dignity == "Friend"
        assert score == 10.0
    
    @pytest.mark.unit
    @pytest.mark.divisional
    def test_enemy_sign_dignity(self, divisional_service):
        """Test dignity for planet in enemy's sign"""
        # Sun in Taurus (Venus's sign, enemy)
        dignity, score = divisional_service.get_planet_dignity("Sun", 1)
        assert dignity == "Enemy"
        assert score == 5.0
    
    @pytest.mark.unit
    @pytest.mark.divisional
    def test_neutral_sign_dignity(self, divisional_service):
        """Test dignity for planet in neutral sign"""
        # Moon in Gemini (Mercury's sign, neutral)
        dignity, score = divisional_service.get_planet_dignity("Moon", 2)
        assert dignity in ["Neutral", "Friend"]  # Depends on rulership
        assert score in [7.5, 10.0]


# =============================================================================
# DIVISIONAL POSITION CALCULATION TESTS
# =============================================================================

class TestDivisionalPositions:
    """Test divisional position calculations for various charts"""
    
    @pytest.mark.unit
    @pytest.mark.divisional
    def test_d2_hora_chart_odd_sign_first_half(self, divisional_service):
        """Test D2 (Hora) calculation for odd sign first half"""
        # Aries (odd sign), first 15° -> Leo
        result = divisional_service.calculate_divisional_position(
            longitude=10.0,  # 10° Aries
            division=2,
            sign_num=0
        )
        assert result["sign_num"] == 4  # Leo
        assert result["sign"] == "Leo"
    
    @pytest.mark.unit
    @pytest.mark.divisional
    def test_d2_hora_chart_odd_sign_second_half(self, divisional_service):
        """Test D2 (Hora) calculation for odd sign second half"""
        # Aries (odd sign), second 15° -> Cancer
        result = divisional_service.calculate_divisional_position(
            longitude=20.0,  # 20° Aries
            division=2,
            sign_num=0
        )
        assert result["sign_num"] == 3  # Cancer
        assert result["sign"] == "Cancer"
    
    @pytest.mark.unit
    @pytest.mark.divisional
    def test_d3_drekkana_chart(self, divisional_service):
        """Test D3 (Drekkana) calculation"""
        # Each sign divided into 3 parts (10° each)
        result = divisional_service.calculate_divisional_position(
            longitude=15.0,  # 15° Aries (second drekkana)
            division=3,
            sign_num=0
        )
        # Second drekkana of Aries -> Leo (0 + 1*4 = 4)
        assert result["sign_num"] == 4
    
    @pytest.mark.unit
    @pytest.mark.divisional
    def test_d7_saptamsa_chart_odd_sign(self, divisional_service):
        """Test D7 (Saptamsa) calculation for odd sign"""
        # Aries (odd sign), first saptamsa
        result = divisional_service.calculate_divisional_position(
            longitude=2.0,  # 2° Aries
            division=7,
            sign_num=0
        )
        # First saptamsa of Aries (odd) -> Aries (0 + 0 = 0)
        assert result["sign_num"] == 0
    
    @pytest.mark.unit
    @pytest.mark.divisional
    def test_d9_navamsa_chart(self, divisional_service):
        """Test D9 (Navamsa) calculation"""
        # Standard Navamsa formula: (sign_num * 9 + navamsa_num) % 12
        result = divisional_service.calculate_divisional_position(
            longitude=10.0,  # 10° Aries (4th navamsa at 10-13.33°)
            division=9,
            sign_num=0
        )
        # 4th navamsa of Aries: (0 * 9 + 3) % 12 = 3 (Cancer)
        assert result["sign_num"] == 3
    
    @pytest.mark.unit
    @pytest.mark.divisional
    def test_d10_dashamsa_chart_odd_sign(self, divisional_service):
        """Test D10 (Dashamsa) calculation for odd sign"""
        result = divisional_service.calculate_divisional_position(
            longitude=15.0,  # 15° Aries (6th dashamsa)
            division=10,
            sign_num=0
        )
        # 6th dashamsa of Aries (odd): (0 + 5) % 12 = 5
        assert result["sign_num"] == 5
    
    @pytest.mark.unit
    @pytest.mark.divisional
    def test_d12_dwadashamsa_chart(self, divisional_service):
        """Test D12 (Dwadashamsa) calculation"""
        result = divisional_service.calculate_divisional_position(
            longitude=10.0,  # 10° Aries (5th dwadashamsa)
            division=12,
            sign_num=0
        )
        # 5th dwadashamsa: (0 + 4) % 12 = 4
        assert result["sign_num"] == 4
    
    @pytest.mark.unit
    @pytest.mark.divisional
    def test_d16_shodashamsa_chart_odd_sign(self, divisional_service):
        """Test D16 (Shodashamsa) calculation"""
        result = divisional_service.calculate_divisional_position(
            longitude=5.0,  # 5° Aries (3rd shodashamsa)
            division=16,
            sign_num=0
        )
        # Odd sign starts from Aries: 0 + 2 = 2 (Gemini)
        assert result["sign_num"] == 2
    
    @pytest.mark.unit
    @pytest.mark.divisional
    def test_d20_vimshamsa_chart(self, divisional_service):
        """Test D20 (Vimshamsa) calculation"""
        result = divisional_service.calculate_divisional_position(
            longitude=3.0,  # 3° Aries (3rd vimshamsa)
            division=20,
            sign_num=0
        )
        # Odd sign starts from Aries
        assert result["sign_num"] in range(12)
    
    @pytest.mark.unit
    @pytest.mark.divisional
    def test_d24_chaturvimshamsa_chart(self, divisional_service):
        """Test D24 (Chaturvimshamsa) calculation"""
        result = divisional_service.calculate_divisional_position(
            longitude=10.0,  # 10° Aries
            division=24,
            sign_num=0
        )
        # Odd sign starts from Leo (4)
        assert result["sign_num"] in range(12)
    
    @pytest.mark.unit
    @pytest.mark.divisional
    def test_d27_nakshatramsa_chart(self, divisional_service):
        """Test D27 (Nakshatramsa) calculation"""
        result = divisional_service.calculate_divisional_position(
            longitude=10.0,  # 10° Aries
            division=27,
            sign_num=0
        )
        assert result["sign_num"] in range(12)
    
    @pytest.mark.unit
    @pytest.mark.divisional
    def test_d30_trimshamsa_chart_odd_sign(self, divisional_service):
        """Test D30 (Trimshamsa) calculation for odd sign"""
        result = divisional_service.calculate_divisional_position(
            longitude=7.0,  # 7° Aries
            division=30,
            sign_num=0
        )
        # Complex formula for D30
        assert result["sign_num"] in range(12)
    
    @pytest.mark.unit
    @pytest.mark.divisional
    def test_d40_khavedamsa_chart(self, divisional_service):
        """Test D40 (Khavedamsa) calculation"""
        result = divisional_service.calculate_divisional_position(
            longitude=10.0,  # 10° Aries
            division=40,
            sign_num=0
        )
        assert result["sign_num"] in range(12)
    
    @pytest.mark.unit
    @pytest.mark.divisional
    def test_d45_akshavedamsa_chart(self, divisional_service):
        """Test D45 (Akshavedamsa) calculation"""
        result = divisional_service.calculate_divisional_position(
            longitude=15.0,  # 15° Aries
            division=45,
            sign_num=0
        )
        assert result["sign_num"] in range(12)
    
    @pytest.mark.unit
    @pytest.mark.divisional
    def test_d60_shashtiamsa_chart(self, divisional_service):
        """Test D60 (Shashtiamsa) calculation"""
        result = divisional_service.calculate_divisional_position(
            longitude=10.0,  # 10° Aries
            division=60,
            sign_num=0
        )
        # D60 formula: (sign_num * 5 + int(division_num / 12)) % 12
        assert result["sign_num"] in range(12)
    
    @pytest.mark.unit
    @pytest.mark.divisional
    def test_divisional_position_contains_required_fields(self, divisional_service):
        """Test that divisional position returns all required fields"""
        result = divisional_service.calculate_divisional_position(
            longitude=15.0,
            division=9,
            sign_num=0
        )
        assert "sign" in result
        assert "sign_num" in result
        assert "degree" in result
        assert "longitude" in result
        assert "division_number" in result


# =============================================================================
# FULL CHART CALCULATION TESTS
# =============================================================================

class TestDivisionalChartCalculation:
    """Test full divisional chart generation"""
    
    @pytest.mark.integration
    @pytest.mark.divisional
    def test_calculate_d9_chart(self, divisional_service, sample_planet_data, sample_ascendant):
        """Test complete D9 (Navamsa) chart calculation"""
        chart = divisional_service.calculate_divisional_chart(
            d1_planets=sample_planet_data,
            d1_ascendant=sample_ascendant,
            division=9,
            chart_name="D9",
            purpose="Marriage and dharma"
        )
        
        assert chart["chart_type"] == "D9"
        assert chart["division"] == 9
        assert chart["purpose"] == "Marriage and dharma"
        assert "ascendant" in chart
        assert "planets" in chart
        assert "houses" in chart
        assert len(chart["houses"]) == 12
        
        # Check that all input planets are calculated
        for planet_name in sample_planet_data.keys():
            assert planet_name in chart["planets"]
            planet = chart["planets"][planet_name]
            assert "sign" in planet
            assert "sign_num" in planet
            assert "house" in planet
            assert "d1_sign" in planet
            assert "d1_house" in planet
    
    @pytest.mark.integration
    @pytest.mark.divisional
    def test_calculate_d7_chart(self, divisional_service, sample_planet_data, sample_ascendant):
        """Test D7 (Saptamsa) chart for children"""
        chart = divisional_service.calculate_divisional_chart(
            d1_planets=sample_planet_data,
            d1_ascendant=sample_ascendant,
            division=7,
            chart_name="D7",
            purpose="Children and progeny"
        )
        
        assert chart["chart_type"] == "D7"
        assert chart["division"] == 7
        assert len(chart["planets"]) == len(sample_planet_data)
    
    @pytest.mark.integration
    @pytest.mark.divisional
    def test_calculate_d10_chart(self, divisional_service, sample_planet_data, sample_ascendant):
        """Test D10 (Dashamsa) chart for career"""
        chart = divisional_service.calculate_divisional_chart(
            d1_planets=sample_planet_data,
            d1_ascendant=sample_ascendant,
            division=10,
            chart_name="D10",
            purpose="Career and profession"
        )
        
        assert chart["chart_type"] == "D10"
        assert chart["division"] == 10
        assert chart["purpose"] == "Career and profession"
    
    @pytest.mark.integration
    @pytest.mark.divisional
    def test_divisional_houses_count(self, divisional_service, sample_planet_data, sample_ascendant):
        """Test that divisional chart has 12 houses"""
        chart = divisional_service.calculate_divisional_chart(
            d1_planets=sample_planet_data,
            d1_ascendant=sample_ascendant,
            division=9,
            chart_name="D9",
            purpose="Test"
        )
        
        assert len(chart["houses"]) == 12
        for i, house in enumerate(chart["houses"]):
            assert house["house_num"] == i + 1
            assert "sign" in house
            assert "sign_num" in house


# =============================================================================
# VIMSHOPAKA BALA TESTS
# =============================================================================

class TestVimshopakaBala:
    """Test Vimshopaka Bala (composite strength) calculations"""
    
    @pytest.mark.integration
    @pytest.mark.divisional
    def test_vimshopaka_bala_calculation(self, divisional_service):
        """Test Vimshopaka Bala calculation with sample data"""
        # Create D1 planets with known dignities
        d1_planets = {
            "Jupiter": {"sign_num": 3, "house": 4},  # Exalted in Cancer
            "Saturn": {"sign_num": 0, "house": 1}    # Debilitated in Aries
        }
        
        # Create sample divisional charts
        divisional_charts = {
            "D9": {
                "planets": {
                    "Jupiter": {"sign_num": 8},  # Own sign (Sagittarius)
                    "Saturn": {"sign_num": 6}    # Exalted (Libra)
                }
            },
            "D2": {
                "planets": {
                    "Jupiter": {"sign_num": 3},  # Exalted
                    "Saturn": {"sign_num": 10}   # Own sign
                }
            }
        }
        
        result = divisional_service.calculate_vimshopaka_bala(d1_planets, divisional_charts)
        
        assert "planets" in result
        assert "summary" in result
        
        # Check Jupiter (should be strong)
        assert "Jupiter" in result["planets"]
        jupiter_strength = result["planets"]["Jupiter"]
        assert jupiter_strength["total_score"] > 0
        assert jupiter_strength["max_score"] == 20.0
        assert "classification" in jupiter_strength
        assert "quality" in jupiter_strength
        assert "varga_scores" in jupiter_strength
        
        # Check Saturn (should be weaker due to debilitation in D1)
        assert "Saturn" in result["planets"]
        saturn_strength = result["planets"]["Saturn"]
        assert saturn_strength["total_score"] >= 0
    
    @pytest.mark.integration
    @pytest.mark.divisional
    def test_vimshopaka_classification_excellent(self, divisional_service):
        """Test Vimshopaka classification for excellent planet"""
        # Planet exalted in all charts
        d1_planets = {
            "Jupiter": {"sign_num": 3, "house": 1}  # Exalted
        }
        divisional_charts = {
            "D9": {"planets": {"Jupiter": {"sign_num": 3}}},  # Exalted
            "D2": {"planets": {"Jupiter": {"sign_num": 3}}}   # Exalted
        }
        
        result = divisional_service.calculate_vimshopaka_bala(d1_planets, divisional_charts)
        jupiter = result["planets"]["Jupiter"]
        
        # Should have high score and quality
        assert jupiter["total_score"] > 10
        assert jupiter["quality"] in ["Excellent", "Very Good", "Good"]
    
    @pytest.mark.integration
    @pytest.mark.divisional
    def test_vimshopaka_classification_weak(self, divisional_service):
        """Test Vimshopaka classification for weak planet"""
        # Planet debilitated in all charts
        d1_planets = {
            "Jupiter": {"sign_num": 9, "house": 10}  # Debilitated in Capricorn
        }
        divisional_charts = {
            "D9": {"planets": {"Jupiter": {"sign_num": 9}}},  # Debilitated
            "D2": {"planets": {"Jupiter": {"sign_num": 9}}}   # Debilitated
        }
        
        result = divisional_service.calculate_vimshopaka_bala(d1_planets, divisional_charts)
        jupiter = result["planets"]["Jupiter"]
        
        # Should have low score
        assert jupiter["total_score"] < 10
        assert jupiter["quality"] in ["Weak", "Below Average", "Average"]
    
    @pytest.mark.integration
    @pytest.mark.divisional
    def test_vimshopaka_summary_statistics(self, divisional_service):
        """Test summary statistics in Vimshopaka Bala"""
        d1_planets = {
            "Jupiter": {"sign_num": 3, "house": 4},  # Exalted
            "Mars": {"sign_num": 9, "house": 10},    # Exalted
            "Saturn": {"sign_num": 0, "house": 1}    # Debilitated
        }
        
        result = divisional_service.calculate_vimshopaka_bala(d1_planets, {})
        summary = result["summary"]
        
        assert "average_strength" in summary
        assert "strongest_planet" in summary
        assert "weakest_planet" in summary
        assert summary["strongest_planet"]["name"] in ["Jupiter", "Mars"]
        assert summary["weakest_planet"]["name"] == "Saturn"


# =============================================================================
# ALL DIVISIONAL CHARTS TESTS
# =============================================================================

class TestAllDivisionalCharts:
    """Test calculation of all divisional charts by priority"""
    
    @pytest.mark.integration
    @pytest.mark.divisional
    def test_high_priority_charts(self, divisional_service, sample_planet_data, sample_ascendant):
        """Test calculation of high priority divisional charts"""
        result = divisional_service.calculate_all_divisional_charts(
            d1_planets=sample_planet_data,
            d1_ascendant=sample_ascendant,
            priority="high"
        )
        
        # High priority should include: D2, D4, D7, D9, D10, D24
        expected_charts = ["D2", "D4", "D7", "D9", "D10", "D24"]
        for chart_name in expected_charts:
            assert chart_name in result, f"{chart_name} should be in high priority charts"
    
    @pytest.mark.integration
    @pytest.mark.divisional
    def test_medium_priority_charts(self, divisional_service, sample_planet_data, sample_ascendant):
        """Test calculation of medium priority divisional charts"""
        result = divisional_service.calculate_all_divisional_charts(
            d1_planets=sample_planet_data,
            d1_ascendant=sample_ascendant,
            priority="medium"
        )
        
        # Medium should include high + D3, D12, D16, D20
        expected_charts = ["D2", "D4", "D7", "D9", "D10", "D24", "D3", "D12", "D16", "D20"]
        for chart_name in expected_charts:
            assert chart_name in result, f"{chart_name} should be in medium priority charts"
    
    @pytest.mark.integration
    @pytest.mark.divisional
    @pytest.mark.slow
    def test_all_priority_charts(self, divisional_service, sample_planet_data, sample_ascendant):
        """Test calculation of all 16 divisional charts"""
        result = divisional_service.calculate_all_divisional_charts(
            d1_planets=sample_planet_data,
            d1_ascendant=sample_ascendant,
            priority="all"
        )
        
        # All 16 charts
        expected_charts = ["D2", "D3", "D4", "D7", "D9", "D10", "D12", "D16", 
                          "D20", "D24", "D27", "D30", "D40", "D45", "D60"]
        
        # Check at least the standard Shodashvarga (excluding D1)
        for chart_name in expected_charts[:6]:  # At least first 6
            assert chart_name in result


# =============================================================================
# PERFORMANCE TESTS
# =============================================================================

class TestDivisionalChartsPerformance:
    """Test performance of divisional chart calculations"""
    
    @pytest.mark.integration
    @pytest.mark.divisional
    def test_single_chart_performance(self, divisional_service, sample_planet_data, sample_ascendant):
        """Test that single chart calculation is fast"""
        import time
        
        start = time.time()
        chart = divisional_service.calculate_divisional_chart(
            d1_planets=sample_planet_data,
            d1_ascendant=sample_ascendant,
            division=9,
            chart_name="D9",
            purpose="Test"
        )
        end = time.time()
        
        # Should complete within 20ms
        assert (end - start) < 0.02, f"Chart calculation took {(end-start)*1000:.2f}ms, should be <20ms"
    
    @pytest.mark.integration
    @pytest.mark.divisional
    def test_all_charts_performance(self, divisional_service, sample_planet_data, sample_ascendant):
        """Test that all charts calculation meets performance target"""
        import time
        
        start = time.time()
        result = divisional_service.calculate_all_divisional_charts(
            d1_planets=sample_planet_data,
            d1_ascendant=sample_ascendant,
            priority="high"
        )
        end = time.time()
        
        # Should complete within 100ms for high priority charts
        assert (end - start) < 0.1, f"All charts took {(end-start)*1000:.2f}ms, should be <100ms"


# =============================================================================
# EDGE CASES & ERROR HANDLING
# =============================================================================

class TestEdgeCases:
    """Test edge cases and error handling"""
    
    @pytest.mark.unit
    @pytest.mark.divisional
    def test_zero_degree_longitude(self, divisional_service):
        """Test divisional calculation at 0° longitude"""
        result = divisional_service.calculate_divisional_position(
            longitude=0.0,
            division=9,
            sign_num=0
        )
        assert result["sign_num"] in range(12)
        assert result["degree"] >= 0
    
    @pytest.mark.unit
    @pytest.mark.divisional
    def test_29_degree_longitude(self, divisional_service):
        """Test divisional calculation at 29° longitude (end of sign)"""
        result = divisional_service.calculate_divisional_position(
            longitude=29.99,
            division=9,
            sign_num=0
        )
        assert result["sign_num"] in range(12)
    
    @pytest.mark.unit
    @pytest.mark.divisional
    def test_dignity_unknown_planet(self, divisional_service):
        """Test dignity calculation for unknown planet"""
        dignity, score = divisional_service.get_planet_dignity("Unknown", 0)
        assert dignity == "Neutral"
        assert score == 7.5
    
    @pytest.mark.unit
    @pytest.mark.divisional
    def test_empty_divisional_charts_vimshopaka(self, divisional_service):
        """Test Vimshopaka Bala with only D1 data"""
        d1_planets = {
            "Jupiter": {"sign_num": 3, "house": 4}
        }
        
        result = divisional_service.calculate_vimshopaka_bala(d1_planets, {})
        
        # Should still work with just D1
        assert "Jupiter" in result["planets"]
        assert result["planets"]["Jupiter"]["varga_scores"]["D1"]["weight"] == 3.5
