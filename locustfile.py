from locust import HttpUser, task, between
import random

class GradingSystemUser(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        """Login on start"""
        self.client.post("/api/auth/login", json={
            "email": "student@example.com",
            "password": "password123"
        })

    @task(2)
    def view_dashboard(self):
        self.client.get("/student-dashboard")

    @task(1)
    def submit_assignment(self):
        """Simulate code submission"""
        self.client.post("/api/submissions/submit", json={
            "assignment_id": "test_assignment_id",
            "code": "print('Hello World')",
            "programming_language": "python"
        })

    @task(1)
    def check_leaderboard(self):
        self.client.get("/leaderboard")
