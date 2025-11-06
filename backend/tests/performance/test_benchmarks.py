"""
Performance Benchmarks using pytest-benchmark
Run with: pytest tests/performance/test_benchmarks.py --benchmark-only
"""

import pytest
from datetime import date
from app.services.numerology_service import NumerologyService
from app.services.extended_yoga_service import extended_yoga_service


@pytest.fixture
def numerology_service():
    return NumerologyService()


@pytest.fixture
def sample_planets():
    return {
        "Sun": {"longitude": 45.5, "sign_num": 2, "house": 1, "retrograde": False},
        "Moon": {"longitude": 120.3, "sign_num": 4, "house": 3, "retrograde": False},
        "Mars": {"longitude": 200.7, "sign_num": 7, "house": 6, "retrograde": False},
        "Mercury": {"longitude": 55.2, "sign_num": 2, "house": 1, "retrograde": False},
        "Jupiter": {"longitude": 95.8, "sign_num": 4, "house": 3, "retrograde": False},
        "Venus": {"longitude": 30.1, "sign_num": 1, "house": 12, "retrograde": False},
        "Saturn": {"longitude": 280.4, "sign_num": 10, "house": 9, "retrograde": False}
    }


class TestNumerologyPerformance:
    """Benchmark numerology calculations"""

    @pytest.mark.performance
    @pytest.mark.benchmark
    def test_single_calculation(self, benchmark, numerology_service):
        """Benchmark single numerology calculation"""
        result = benchmark(
            numerology_service.calculate,
            "John Doe",
            date(1990, 1, 15),
            "both"
        )

        assert "western" in result
        assert "vedic" in result

    @pytest.mark.performance
    @pytest.mark.benchmark
    def test_bulk_calculations(self, benchmark, numerology_service):
        """Benchmark bulk numerology calculations"""
        names = ["John Doe", "Jane Smith", "Bob Johnson", "Alice Williams", "Charlie Brown"]
        birth_date = date(1990, 1, 15)

        def bulk_calculate():
            return [numerology_service.calculate(name, birth_date, "both") for name in names]

        results = benchmark(bulk_calculate)
        assert len(results) == 5


class TestYogaPerformance:
    """Benchmark yoga detection"""

    @pytest.mark.performance
    @pytest.mark.benchmark
    def test_yoga_detection(self, benchmark, sample_planets):
        """Benchmark yoga detection"""
        result = benchmark(
            extended_yoga_service.detect_extended_yogas,
            sample_planets
        )

        assert isinstance(result, list)

    @pytest.mark.performance
    @pytest.mark.benchmark
    def test_yoga_detection_bulk(self, benchmark, sample_planets):
        """Benchmark multiple yoga detections"""
        def bulk_detect():
            return [extended_yoga_service.detect_extended_yogas(sample_planets) for _ in range(10)]

        results = benchmark(bulk_detect)
        assert len(results) == 10


# ============================================================================
# Performance Regression Tests
# ============================================================================

class TestPerformanceRegression:
    """Ensure performance doesn't degrade over time"""

    @pytest.mark.performance
    @pytest.mark.regression
    def test_numerology_speed_threshold(self, numerology_service, performance_threshold):
        """Ensure numerology calculation meets speed threshold"""
        import time

        start = time.time()
        result = numerology_service.calculate("John Doe", date(1990, 1, 15), "both")
        duration = time.time() - start

        # Should complete in under 100ms (0.1s)
        assert duration < performance_threshold["fast"], \
            f"Numerology took {duration:.3f}s, threshold is {performance_threshold['fast']}s"

        assert "western" in result

    @pytest.mark.performance
    @pytest.mark.regression
    def test_yoga_detection_speed_threshold(self, sample_planets, performance_threshold):
        """Ensure yoga detection meets speed threshold"""
        import time

        start = time.time()
        result = extended_yoga_service.detect_extended_yogas(sample_planets)
        duration = time.time() - start

        # Should complete in under 100ms (0.1s)
        assert duration < performance_threshold["fast"], \
            f"Yoga detection took {duration:.3f}s, threshold is {performance_threshold['fast']}s"

        assert isinstance(result, list)

    @pytest.mark.performance
    @pytest.mark.regression
    def test_bulk_numerology_throughput(self, numerology_service):
        """Ensure bulk calculations maintain throughput"""
        import time

        names = ["User" + str(i) for i in range(100)]
        birth_date = date(1990, 1, 15)

        start = time.time()
        results = [numerology_service.calculate(name, birth_date, "both") for name in names]
        duration = time.time() - start

        # 100 calculations should complete in under 10 seconds
        assert duration < 10.0, f"100 calculations took {duration:.2f}s, expected < 10s"

        throughput = len(results) / duration
        # Should achieve at least 10 calculations per second
        assert throughput > 10, f"Throughput was {throughput:.2f} calcs/sec, expected > 10"
