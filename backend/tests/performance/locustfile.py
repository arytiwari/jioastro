"""
Locust Load Testing Configuration
Run with: locust -f locustfile.py --host=http://localhost:8000
"""

from locust import HttpUser, task, between
import random
from datetime import datetime


class JioAstroUser(HttpUser):
    """Simulated user for load testing"""

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    # Authentication token (replace with real token for testing)
    auth_token = "test-token-123"

    def on_start(self):
        """Called when a user starts"""
        self.profile_id = "test-profile-123"
        self.headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }

    # ============================================================================
    # Numerology Tests (Critical Path)
    # ============================================================================

    @task(5)  # Weight: 5 (most common operation)
    def calculate_numerology(self):
        """Test numerology calculation endpoint"""
        names = ["John Doe", "Jane Smith", "Bob Johnson", "Alice Williams"]
        dates = ["1990-01-15", "1985-05-20", "1992-11-03", "1988-07-28"]

        payload = {
            "full_name": random.choice(names),
            "birth_date": random.choice(dates),
            "system": "both"
        }

        with self.client.post(
            "/api/v1/numerology/calculate",
            json=payload,
            headers=self.headers,
            catch_response=True,
            name="/numerology/calculate"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "western" in data and "vedic" in data:
                    response.success()
                else:
                    response.failure("Missing expected fields")
            else:
                response.failure(f"Got status {response.status_code}")

    # ============================================================================
    # Yoga Analysis Tests
    # ============================================================================

    @task(3)  # Weight: 3
    def analyze_yogas(self):
        """Test yoga analysis endpoint"""
        payload = {
            "profile_id": self.profile_id,
            "include_all": True
        }

        with self.client.post(
            "/api/v1/enhancements/yogas/analyze",
            json=payload,
            headers=self.headers,
            catch_response=True,
            name="/yogas/analyze"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "yogas" in data and "total_yogas" in data:
                    response.success()
                else:
                    response.failure("Missing yoga data")
            elif response.status_code == 404:
                # Expected if profile doesn't exist
                response.success()
            else:
                response.failure(f"Got status {response.status_code}")

    # ============================================================================
    # Remedy Generation Tests
    # ============================================================================

    @task(2)  # Weight: 2
    def generate_remedies(self):
        """Test remedy generation endpoint"""
        domains = ["career", "wealth", "health", "relationships"]

        payload = {
            "profile_id": self.profile_id,
            "domain": random.choice(domains),
            "max_remedies": 5,
            "include_practical": True
        }

        with self.client.post(
            "/api/v1/enhancements/remedies/generate",
            json=payload,
            headers=self.headers,
            catch_response=True,
            name="/remedies/generate"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "remedies" in data:
                    response.success()
                else:
                    response.failure("No remedies returned")
            elif response.status_code == 404:
                response.success()
            else:
                response.failure(f"Got status {response.status_code}")

    # ============================================================================
    # Transit Calculation Tests
    # ============================================================================

    @task(2)  # Weight: 2
    def calculate_transits(self):
        """Test transit calculation endpoint"""
        payload = {
            "profile_id": self.profile_id,
            "include_timeline": True
        }

        with self.client.post(
            "/api/v1/enhancements/transits/current",
            json=payload,
            headers=self.headers,
            catch_response=True,
            name="/transits/current"
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                response.success()
            else:
                response.failure(f"Got status {response.status_code}")

    # ============================================================================
    # Shadbala Calculation Tests
    # ============================================================================

    @task(1)  # Weight: 1
    def calculate_shadbala(self):
        """Test Shadbala calculation endpoint"""
        payload = {
            "profile_id": self.profile_id,
            "include_breakdown": True,
            "comparison": True
        }

        with self.client.post(
            "/api/v1/enhancements/shadbala/calculate",
            json=payload,
            headers=self.headers,
            catch_response=True,
            name="/shadbala/calculate"
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                response.success()
            else:
                response.failure(f"Got status {response.status_code}")

    # ============================================================================
    # Health Check Tests
    # ============================================================================

    @task(1)  # Weight: 1
    def health_check(self):
        """Test health check endpoint"""
        with self.client.get(
            "/health",
            catch_response=True,
            name="/health"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status {response.status_code}")


class HeavyLoadUser(HttpUser):
    """Heavy load user for stress testing"""

    wait_time = between(0.5, 1.5)  # Faster requests

    def on_start(self):
        self.auth_token = "test-token-123"
        self.profile_id = "test-profile-123"
        self.headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }

    @task
    def burst_numerology_requests(self):
        """Burst of numerology calculations"""
        for _ in range(5):
            payload = {
                "full_name": f"User {random.randint(1, 1000)}",
                "birth_date": f"199{random.randint(0, 9)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                "system": "both"
            }

            self.client.post(
                "/api/v1/numerology/calculate",
                json=payload,
                headers=self.headers,
                name="/numerology/calculate (burst)"
            )
