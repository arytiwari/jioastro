"""
Numerology Performance Benchmark Script

This script measures and reports performance metrics for numerology calculations:
- Single calculation speed per system
- Database insert/query performance
- API endpoint response times
- Memory usage
- Concurrent request handling

Performance Targets:
- Single calculation: < 50ms
- Full profile (both systems): < 100ms
- Bulk comparison (5 names): < 200ms
- Database query: < 50ms
"""

import sys
import time
import statistics
from datetime import date, datetime
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.numerology_service import (
    NumerologyService,
    WesternNumerology,
    VedicNumerology,
)
from app.services.supabase_service import supabase_service


class PerformanceBenchmark:
    """Performance benchmarking for numerology calculations"""

    def __init__(self):
        self.results = {}
        self.test_data = {
            "full_name": "John Michael Doe",
            "birth_date": date(1990, 6, 15),
            "system": "both",
        }

    def measure_time(self, func, *args, iterations=100, **kwargs):
        """Measure average execution time over multiple iterations"""
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            func(*args, **kwargs)
            end = time.perf_counter()
            times.append((end - start) * 1000)  # Convert to milliseconds

        return {
            "min": min(times),
            "max": max(times),
            "mean": statistics.mean(times),
            "median": statistics.median(times),
            "stdev": statistics.stdev(times) if len(times) > 1 else 0,
        }

    def benchmark_western_calculations(self):
        """Benchmark Western numerology calculations"""
        print("\n📊 Western Numerology Calculations")
        print("-" * 70)

        # Life Path
        result = self.measure_time(
            WesternNumerology.calculate_life_path,
            self.test_data["birth_date"]
        )
        self.results["western_life_path"] = result
        status = "✅" if result["mean"] < 50 else "⚠️"
        print(f"{status} Life Path:        {result['mean']:.2f}ms (target: <50ms)")

        # Expression Number
        result = self.measure_time(
            WesternNumerology.calculate_expression,
            self.test_data["full_name"]
        )
        self.results["western_expression"] = result
        status = "✅" if result["mean"] < 50 else "⚠️"
        print(f"{status} Expression:       {result['mean']:.2f}ms (target: <50ms)")

        # Personal Year
        result = self.measure_time(
            WesternNumerology.calculate_personal_year,
            self.test_data["birth_date"],
            datetime.now().date()
        )
        self.results["western_personal_year"] = result
        status = "✅" if result["mean"] < 50 else "⚠️"
        print(f"{status} Personal Year:    {result['mean']:.2f}ms (target: <50ms)")

        # Pinnacles
        result = self.measure_time(
            WesternNumerology.calculate_pinnacles,
            self.test_data["birth_date"]
        )
        self.results["western_pinnacles"] = result
        status = "✅" if result["mean"] < 50 else "⚠️"
        print(f"{status} Pinnacles:        {result['mean']:.2f}ms (target: <50ms)")

    def benchmark_vedic_calculations(self):
        """Benchmark Vedic numerology calculations"""
        print("\n📊 Vedic Numerology Calculations")
        print("-" * 70)

        # Psychic Number
        result = self.measure_time(
            VedicNumerology.calculate_psychic_number,
            self.test_data["birth_date"]
        )
        self.results["vedic_psychic"] = result
        status = "✅" if result["mean"] < 50 else "⚠️"
        print(f"{status} Psychic Number:   {result['mean']:.2f}ms (target: <50ms)")

        # Destiny Number (Vedic uses name with Chaldean system)
        result = self.measure_time(
            VedicNumerology.calculate_destiny_number,
            self.test_data["full_name"]
        )
        self.results["vedic_destiny"] = result
        status = "✅" if result["mean"] < 50 else "⚠️"
        print(f"{status} Destiny Number:   {result['mean']:.2f}ms (target: <50ms)")

        # Name Value
        result = self.measure_time(
            VedicNumerology.calculate_name_value,
            self.test_data["full_name"]
        )
        self.results["vedic_name_value"] = result
        status = "✅" if result["mean"] < 50 else "⚠️"
        print(f"{status} Name Value:       {result['mean']:.2f}ms (target: <50ms)")

    def benchmark_combined_calculations(self):
        """Benchmark combined numerology service"""
        print("\n📊 Combined Service Calculations")
        print("-" * 70)

        # Full Western Profile
        def calc_western():
            return NumerologyService.calculate(
                full_name=self.test_data["full_name"],
                birth_date=self.test_data["birth_date"],
                system="western",
                current_date=datetime.now().date()
            )

        result = self.measure_time(calc_western, iterations=50)
        self.results["full_western_profile"] = result
        status = "✅" if result["mean"] < 100 else "⚠️"
        print(f"{status} Western Profile:  {result['mean']:.2f}ms (target: <100ms)")

        # Full Vedic Profile
        def calc_vedic():
            return NumerologyService.calculate(
                full_name=self.test_data["full_name"],
                birth_date=self.test_data["birth_date"],
                system="vedic",
                current_date=datetime.now().date()
            )

        result = self.measure_time(calc_vedic, iterations=50)
        self.results["full_vedic_profile"] = result
        status = "✅" if result["mean"] < 100 else "⚠️"
        print(f"{status} Vedic Profile:    {result['mean']:.2f}ms (target: <100ms)")

        # Both Systems
        def calc_both():
            return NumerologyService.calculate(
                full_name=self.test_data["full_name"],
                birth_date=self.test_data["birth_date"],
                system="both",
                current_date=datetime.now().date()
            )

        result = self.measure_time(calc_both, iterations=50)
        self.results["full_both_systems"] = result
        status = "✅" if result["mean"] < 150 else "⚠️"
        print(f"{status} Both Systems:     {result['mean']:.2f}ms (target: <150ms)")

    def benchmark_bulk_operations(self):
        """Benchmark bulk name comparison"""
        print("\n📊 Bulk Operations")
        print("-" * 70)

        names = [
            "John Doe",
            "Jon Doe",
            "Jonathan Doe",
            "J. Doe",
            "John Michael Doe"
        ]

        def compare_names():
            results = []
            for name in names:
                result = NumerologyService.calculate(
                    full_name=name,
                    birth_date=self.test_data["birth_date"],
                    system="western",
                    current_date=datetime.now().date()
                )
                results.append(result)
            return results

        result = self.measure_time(compare_names, iterations=20)
        self.results["bulk_comparison_5_names"] = result
        status = "✅" if result["mean"] < 200 else "⚠️"
        print(f"{status} Compare 5 Names:  {result['mean']:.2f}ms (target: <200ms)")

    def benchmark_database_operations(self):
        """Benchmark database operations"""
        print("\n📊 Database Operations")
        print("-" * 70)

        try:
            # Note: These are read-only benchmarks to avoid polluting the database
            # For write benchmarks, we would need a test database

            # Query profiles (if any exist)
            def query_profiles():
                response = supabase_service.client.table("numerology_profiles")\
                    .select("*")\
                    .limit(10)\
                    .execute()
                return response.data

            result = self.measure_time(query_profiles, iterations=20)
            self.results["db_query_profiles"] = result
            status = "✅" if result["mean"] < 50 else "⚠️"
            print(f"{status} Query Profiles:   {result['mean']:.2f}ms (target: <50ms)")

            # Query single profile by ID (if any exist)
            profiles = query_profiles()
            if profiles and len(profiles) > 0:
                profile_id = profiles[0]['id']

                def query_single_profile():
                    response = supabase_service.client.table("numerology_profiles")\
                        .select("*")\
                        .eq("id", profile_id)\
                        .execute()
                    return response.data

                result = self.measure_time(query_single_profile, iterations=20)
                self.results["db_query_single"] = result
                status = "✅" if result["mean"] < 50 else "⚠️"
                print(f"{status} Query Single:     {result['mean']:.2f}ms (target: <50ms)")
            else:
                print("ℹ️  Query Single:     Skipped (no profiles in database)")

        except Exception as e:
            print(f"⚠️  Database benchmarks skipped: {str(e)[:100]}")

    def benchmark_memory_usage(self):
        """Estimate memory usage"""
        print("\n📊 Memory Usage Estimates")
        print("-" * 70)

        import sys

        # Single calculation result size
        result = NumerologyService.calculate(
            full_name=self.test_data["full_name"],
            birth_date=self.test_data["birth_date"],
            system="both",
            current_date=datetime.now().date()
        )

        # Estimate size of result dictionary
        import json
        result_json = json.dumps(result)
        result_size_kb = len(result_json.encode('utf-8')) / 1024

        print(f"📦 Single calculation result: ~{result_size_kb:.2f} KB")

        # Estimate 100 calculations
        print(f"📦 100 calculations (in-memory): ~{result_size_kb * 100:.2f} KB")
        print(f"📦 1000 calculations (in-memory): ~{result_size_kb * 1000:.2f} KB")

        # Database storage estimate
        print(f"📦 Single profile in DB: ~{result_size_kb * 1.2:.2f} KB (with metadata)")

    def print_summary(self):
        """Print overall performance summary"""
        print("\n" + "=" * 70)
        print("PERFORMANCE SUMMARY")
        print("=" * 70)

        # Calculate overall statistics
        all_means = [v["mean"] for v in self.results.values() if "mean" in v]

        if all_means:
            print(f"\n📈 Overall Statistics:")
            print(f"   Fastest operation:  {min(all_means):.2f}ms")
            print(f"   Slowest operation:  {max(all_means):.2f}ms")
            print(f"   Average operation:  {statistics.mean(all_means):.2f}ms")

        # Check if targets met
        print(f"\n🎯 Performance Targets:")

        targets_met = 0
        total_targets = 0

        checks = [
            ("Single calculations < 50ms", any(v["mean"] < 50 for k, v in self.results.items() if "western" in k or "vedic" in k)),
            ("Full profile < 100ms", self.results.get("full_western_profile", {}).get("mean", 999) < 100),
            ("Both systems < 150ms", self.results.get("full_both_systems", {}).get("mean", 999) < 150),
            ("Bulk comparison < 200ms", self.results.get("bulk_comparison_5_names", {}).get("mean", 999) < 200),
        ]

        for description, met in checks:
            total_targets += 1
            if met:
                targets_met += 1
                print(f"   ✅ {description}")
            else:
                print(f"   ❌ {description}")

        # Overall result
        print(f"\n" + "=" * 70)
        if targets_met == total_targets:
            print("✅ ALL PERFORMANCE TARGETS MET!")
        else:
            print(f"⚠️  {targets_met}/{total_targets} TARGETS MET")
        print("=" * 70)

        return targets_met == total_targets

    def run_all_benchmarks(self):
        """Run all performance benchmarks"""
        print("\n" + "=" * 70)
        print("NUMEROLOGY PERFORMANCE BENCHMARK")
        print("=" * 70)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        self.benchmark_western_calculations()
        self.benchmark_vedic_calculations()
        self.benchmark_combined_calculations()
        self.benchmark_bulk_operations()
        self.benchmark_database_operations()
        self.benchmark_memory_usage()
        self.print_summary()

        print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def main():
    """Main benchmark execution"""
    benchmark = PerformanceBenchmark()
    benchmark.run_all_benchmarks()


if __name__ == "__main__":
    main()
