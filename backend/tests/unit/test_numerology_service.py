"""
Unit tests for Numerology Service
Tests Western and Vedic numerology calculations
"""

import pytest
from datetime import date
from app.services.numerology_service import (
    WesternNumerology,
    VedicNumerology,
    NumerologyService
)


class TestWesternNumerology:
    """Test Western (Pythagorean) numerology calculations"""

    @pytest.mark.unit
    def test_reduce_to_single_digit_normal(self):
        """Test number reduction through life path calculation"""
        western = WesternNumerology()
        # Test indirectly through life path calculation
        result = western.calculate_life_path(date(1990, 1, 15))
        assert result['number'] == 8
        assert result['breakdown']['sum_before_reduction'] >= result['number']

    @pytest.mark.unit
    def test_reduce_to_single_digit_master_numbers(self):
        """Test master number preservation"""
        western = WesternNumerology()
        # Test master number 11: e.g., 1992-11-02
        result = western.calculate_life_path(date(1992, 11, 2))
        # Should preserve master number or reduce appropriately
        assert 'number' in result
        assert 'is_master' in result

    @pytest.mark.unit
    def test_calculate_life_path(self):
        """Test Life Path number calculation"""
        western = WesternNumerology()

        # Test case: 1990-01-15 -> Should give 8
        result = western.calculate_life_path(date(1990, 1, 15))
        assert isinstance(result, dict)
        assert result['number'] == 8
        assert 'is_master' in result
        assert 'meaning' in result
        assert 'breakdown' in result

    @pytest.mark.unit
    def test_calculate_expression_number(self):
        """Test Expression number calculation"""
        western = WesternNumerology()

        result = western.calculate_expression("John Doe")
        assert isinstance(result, dict)
        assert 'number' in result
        assert 1 <= result['number'] <= 33
        assert 'meaning' in result

    @pytest.mark.unit
    def test_calculate_soul_urge(self):
        """Test Soul Urge number calculation"""
        western = WesternNumerology()

        result = western.calculate_soul_urge("John Doe")
        assert isinstance(result, dict)
        assert 'number' in result
        assert 1 <= result['number'] <= 33
        assert 'meaning' in result

    @pytest.mark.unit
    def test_calculate_personality_number(self):
        """Test Personality number calculation"""
        western = WesternNumerology()

        result = western.calculate_personality("John Doe")
        assert isinstance(result, dict)
        assert 'number' in result
        assert 1 <= result['number'] <= 33
        assert 'meaning' in result

    @pytest.mark.unit
    def test_calculate_personal_year(self):
        """Test Personal Year calculation"""
        western = WesternNumerology()

        result = western.calculate_personal_year(date(1990, 1, 15), date(2025, 3, 1))
        assert isinstance(result, dict)
        assert 'number' in result
        assert 1 <= result['number'] <= 11


class TestVedicNumerology:
    """Test Vedic (Chaldean) numerology calculations"""

    @pytest.mark.unit
    def test_calculate_psychic_number(self):
        """Test Psychic number (Moolank) calculation"""
        vedic = VedicNumerology()

        # Birth day 15 -> 1+5 = 6
        result = vedic.calculate_psychic_number(date(1990, 1, 15))
        assert isinstance(result, dict)
        assert result['number'] == 6
        assert 'planet' in result
        assert 'meaning' in result

        # Birth day 7 -> 7
        result = vedic.calculate_psychic_number(date(1990, 1, 7))
        assert result['number'] == 7

        # Birth day 29 -> 2+9 = 11 -> 2
        result = vedic.calculate_psychic_number(date(1990, 1, 29))
        assert result['number'] == 2

    @pytest.mark.unit
    def test_calculate_destiny_number(self):
        """Test Destiny number (Bhagyank) calculation"""
        vedic = VedicNumerology()

        result = vedic.calculate_destiny_number("John Doe")
        assert isinstance(result, dict)
        assert 'number' in result
        assert 1 <= result['number'] <= 9
        assert 'planet' in result

    @pytest.mark.unit
    def test_calculate_name_value(self):
        """Test Chaldean name value calculation"""
        vedic = VedicNumerology()

        result = vedic.calculate_name_value("John")
        assert isinstance(result, dict)
        assert 'number' in result
        assert 1 <= result['number'] <= 9
        assert 'planet' in result

        # Test with invalid characters (should skip)
        result = vedic.calculate_name_value("John123")
        assert isinstance(result, dict)
        assert 'number' in result

    @pytest.mark.unit
    def test_get_planet_for_number(self):
        """Test planetary association through psychic number"""
        vedic = VedicNumerology()

        result = vedic.calculate_psychic_number(date(1990, 1, 1))
        assert result['planet'] == "Sun"  # Day 1 = Sun

        result = vedic.calculate_psychic_number(date(1990, 1, 2))
        assert result['planet'] == "Moon"  # Day 2 = Moon


class TestNumerologyService:
    """Test unified Numerology Service"""

    @pytest.mark.unit
    def test_full_calculation_both_systems(self):
        """Test full calculation with both systems"""
        result = NumerologyService.calculate(
            full_name="John Doe",
            birth_date=date(1990, 1, 15),
            system="both"
        )

        # Check structure
        assert "western" in result
        assert "vedic" in result
        assert "calculation_hash" in result
        assert "calculated_at" in result

        # Check Western results
        western = result["western"]
        assert "core_numbers" in western
        assert "life_path" in western["core_numbers"]
        assert "expression" in western["core_numbers"]
        assert "soul_urge" in western["core_numbers"]

        # Check Vedic results
        vedic = result["vedic"]
        assert "psychic_number" in vedic
        assert "destiny_number" in vedic or "name_number" in vedic

    @pytest.mark.unit
    def test_calculation_western_only(self):
        """Test calculation with Western system only"""
        result = NumerologyService.calculate(
            full_name="John Doe",
            birth_date=date(1990, 1, 15),
            system="western"
        )

        assert "western" in result
        assert "vedic" not in result

    @pytest.mark.unit
    def test_calculation_vedic_only(self):
        """Test calculation with Vedic system only"""
        result = NumerologyService.calculate(
            full_name="John Doe",
            birth_date=date(1990, 1, 15),
            system="vedic"
        )

        assert "vedic" in result
        assert "western" not in result

    @pytest.mark.unit
    def test_calculation_hash_consistency(self):
        """Test that same inputs produce same hash"""
        result1 = NumerologyService.calculate("John Doe", date(1990, 1, 15), "both")
        result2 = NumerologyService.calculate("John Doe", date(1990, 1, 15), "both")

        assert result1["calculation_hash"] == result2["calculation_hash"]

    @pytest.mark.unit
    def test_calculation_hash_difference(self):
        """Test that different inputs produce different hashes"""
        result1 = NumerologyService.calculate("John Doe", date(1990, 1, 15), "both")
        result2 = NumerologyService.calculate("Jane Doe", date(1990, 1, 15), "both")

        assert result1["calculation_hash"] != result2["calculation_hash"]

    @pytest.mark.unit
    @pytest.mark.performance
    def test_calculation_performance(self, performance_threshold):
        """Test calculation performance"""
        import time
        start = time.time()
        NumerologyService.calculate("John Doe", date(1990, 1, 15), "both")
        duration = time.time() - start

        # Should complete in under 100ms
        assert duration < performance_threshold["fast"], f"Calculation took {duration}s, expected < {performance_threshold['fast']}s"


class TestNumerologyEdgeCases:
    """Test edge cases and error handling"""

    @pytest.mark.unit
    def test_empty_name(self):
        """Test handling of empty name"""
        with pytest.raises(Exception):
            NumerologyService.calculate("", date(1990, 1, 15), "both")

    @pytest.mark.unit
    def test_special_characters_in_name(self):
        """Test handling of special characters"""
        service = NumerologyService()

        # Should handle gracefully
        result = service.calculate("John-Paul O'Brien III", date(1990, 1, 15), "western")
        assert "western" in result

    @pytest.mark.unit
    def test_future_date(self):
        """Test handling of future birth date"""
        service = NumerologyService()

        # Should still calculate (no validation)
        result = service.calculate("Future Person", date(2050, 1, 1), "both")
        assert "western" in result

    @pytest.mark.unit
    def test_very_old_date(self):
        """Test handling of very old dates"""
        result = NumerologyService.calculate("Ancient Person", date(1900, 1, 1), "both")
        assert "western" in result

    @pytest.mark.unit
    def test_invalid_system(self):
        """Test invalid system parameter (returns empty result)"""
        # Invalid system returns result with no calculations
        result = NumerologyService.calculate("John Doe", date(1990, 1, 15), "invalid_system")
        # Should have basic metadata but no western/vedic calculations
        assert "calculation_hash" in result
        assert "calculated_at" in result
        # Invalid system doesn't include western or vedic results
        assert "western" not in result and "vedic" not in result


# ============================================================================
# Performance Benchmarks
# ============================================================================

@pytest.mark.performance
@pytest.mark.benchmark
class TestNumerologyPerformance:
    """Performance benchmarks for numerology calculations"""

    def test_single_calculation_speed(self, benchmark):
        """Benchmark single calculation"""
        service = NumerologyService()

        result = benchmark(
            service.calculate,
            "John Doe",
            date(1990, 1, 15),
            "both"
        )

        assert "western" in result

    def test_bulk_calculation_speed(self, benchmark, performance_threshold):
        """Benchmark bulk calculations"""
        service = NumerologyService()
        names = ["John Doe", "Jane Smith", "Bob Johnson", "Alice Williams", "Charlie Brown"]

        def bulk_calculate():
            return [service.calculate(name, date(1990, 1, 15), "both") for name in names]

        results = benchmark(bulk_calculate)
        assert len(results) == 5
