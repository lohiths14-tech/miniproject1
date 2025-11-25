"""
Load Testing Configuration for AI Grading System
Tests system performance under realistic load conditions
Uses Locust for distributed load testing
"""

from locust import HttpUser, task, between, events
import random
import json

class StudentUser(HttpUser):
    """Simulates student behavior"""
    wait_time = between(2, 5)

    def on_start(self):
        """Login when simulation starts"""
        self.client.post("/api/auth/login", json={
            "email": f"student{random.randint(1, 1000)}@example.com",
            "password": "password123"
        })

    @task(3)
    def view_dashboard(self):
        """View student dashboard"""
        self.client.get("/student-dashboard")

    @task(5)
    def view_assignments(self):
        """View assignments list"""
        self.client.get("/api/assignments")

    @task(10)
    def submit_code(self):
        """Submit code for grading - most common action"""
        sample_codes = [
            "def factorial(n):\n    if n == 0: return 1\n    return n * factorial(n-1)",
            "def fibonacci(n):\n    if n <= 1: return n\n    return fibonacci(n-1) + fibonacci(n-2)",
            "def bubble_sort(arr):\n    n = len(arr)\n    for i in range(n):\n        for j in range(0, n-i-1):\n            if arr[j] > arr[j+1]:\n                arr[j], arr[j+1] = arr[j+1], arr[j]"
        ]

        self.client.post("/api/submissions/submit", json={
            "code": random.choice(sample_codes),
            "language": "python",
            "assignment_id": f"assign_{random.randint(1, 10)}"
        })

    @task(2)
    def check_plagiarism(self):
        """Check plagiarism status"""
        self.client.get(f"/api/plagiarism/status/{random.randint(1, 100)}")

    @task(1)
    def view_leaderboard(self):
        """View leaderboard"""
        self.client.get("/api/gamification/leaderboard")


class LecturerUser(HttpUser):
    """Simulates lecturer behavior"""
    wait_time = between(3, 8)

    def on_start(self):
        """Login as lecturer"""
        self.client.post("/api/auth/login", json={
            "email": f"lecturer{random.randint(1, 50)}@example.com",
            "password": "password123"
        })

    @task(2)
    def view_dashboard(self):
        """View lecturer dashboard"""
        self.client.get("/lecturer-dashboard")

    @task(5)
    def view_submissions(self):
        """View student submissions"""
        self.client.get("/api/submissions/recent")

    @task(3)
    def view_analytics(self):
        """View analytics dashboard"""
        self.client.get("/api/dashboard/analytics")

    @task(1)
    def create_assignment(self):
        """Create new assignment"""
        self.client.post("/api/assignments/create", json={
            "title": f"Test Assignment {random.randint(1, 1000)}",
            "description": "Write a function to solve the problem",
            "difficulty": random.choice(["easy", "medium", "hard"])
        })

    @task(2)
    def initiate_plagiarism_scan(self):
        """Initiate plagiarism scan"""
        self.client.post("/api/plagiarism/scan", json={
            "assignment_id": f"assign_{random.randint(1, 10)}"
        })


# Performance thresholds
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Monitor request performance"""
    if response_time > 2000:  # 2 second threshold
        print(f"⚠️  Slow request: {name} took {response_time}ms")
    elif exception:
        print(f"❌ Failed request: {name} - {exception}")


# Test scenarios
class QuickTest(HttpUser):
    """Quick smoke test - 100 users for 1 minute"""
    tasks = [StudentUser, LecturerUser]
    wait_time = between(1, 3)


class StressTest(HttpUser):
    """Stress test - 1000 users for 10 minutes"""
    tasks = [StudentUser, LecturerUser]
    wait_time = between(0.5, 2)


class SpikeTest(HttpUser):
    """Spike test - sudden load increase"""
    tasks = [StudentUser]
    wait_time = between(0.1, 0.5)


# Run configurations:
# Quick test: locust -f locustfile.py --users 100 --spawn-rate 10 --run-time 1m
# Stress test: locust -f locustfile.py --users 1000 --spawn-rate 50 --run-time 10m
# Endurance: locust -f locustfile.py --users 500 --spawn-rate 25 --run-time 1h
