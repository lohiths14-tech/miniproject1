"""
Student Progress Tracker Service

Provides comprehensive analytics and tracking for individual student performance
including detailed metrics, trends, skill progression, and comparative analysis.
"""

import json
import os
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List


class ProgressTrackerService:
    def __init__(self):
        self.submissions_data = self._load_real_submissions()

    def _load_real_submissions(self) -> List[Dict[str, Any]]:
        """Load real student submissions from JSON file"""
        try:
            submissions_file = os.path.join(
                os.path.dirname(__file__), "..", "submissions_data.json"
            )
            with open(submissions_file, "r") as f:
                submissions = json.load(f)
            return submissions
        except Exception as e:
            print(f"Error loading submissions: {e}")
            return []

    def _get_student_submissions(self, student_identifier: str) -> List[Dict[str, Any]]:
        """Get submissions for a specific student by name or email"""
        student_submissions = []
        for submission in self.submissions_data:
            if (
                student_identifier.lower() in submission.get("student_name", "").lower()
                or student_identifier.lower() in submission.get("student_email", "").lower()
            ):
                student_submissions.append(submission)
        return student_submissions

    def _generate_mock_data(self) -> Dict[str, Any]:
        """Generate comprehensive mock data for progress tracking"""

        # Generate submission history for the last 6 months
        submissions = []
        skills = [
            "Python",
            "Java",
            "C++",
            "Data Structures",
            "Algorithms",
            "SQL",
            "Web Development",
        ]
        difficulty_levels = ["Easy", "Medium", "Hard"]

        for i in range(50):
            date = datetime.now() - timedelta(days=random.randint(1, 180))
            submissions.append(
                {
                    "id": f"sub_{i+1}",
                    "assignment_name": f'Assignment {i+1}: {random.choice(["Arrays", "Sorting", "Trees", "Graphs", "DP", "Strings"])}',
                    "submission_date": date.isoformat(),
                    "score": random.randint(60, 100),
                    "max_score": 100,
                    "skill": random.choice(skills),
                    "difficulty": random.choice(difficulty_levels),
                    "time_spent": random.randint(30, 180),  # minutes
                    "attempts": random.randint(1, 5),
                    "plagiarism_score": random.randint(0, 15),
                    "feedback_rating": random.randint(3, 5),
                }
            )

        # Sort by date
        submissions.sort(key=lambda x: x["submission_date"], reverse=True)

        return {
            "submissions": submissions,
            "profile": {
                "student_id": "STU001",
                "name": "Unknown Student",
                "email": "unknown@example.com",
                "enrollment_date": "2024-01-15",
                "major": "Computer Science",
                "year": 2,
                "gpa": 0.0,
            },
        }

    def get_student_overview(self, student_id: str) -> Dict[str, Any]:
        """Get comprehensive student performance overview using real submission data"""
        submissions = self._get_student_submissions(student_id)

        if not submissions:
            return {
                "overview": {
                    "total_assignments": 0,
                    "average_score": 0,
                    "total_score": 0,
                    "max_possible": 0,
                    "completion_rate": 0,
                    "current_streak": 0,
                    "longest_streak": 0,
                    "recent_trend": "no_data",
                },
                "skill_progress": {},
                "profile": {
                    "student_id": student_id,
                    "name": "Student Not Found",
                    "email": "",
                    "enrollment_date": "",
                    "major": "Unknown",
                    "year": 0,
                    "gpa": 0,
                },
            }

        total_submissions = len(submissions)
        total_score = sum(s.get("score", 0) for s in submissions)
        max_possible = total_submissions * 100  # Assuming max score is 100 per assignment
        average_score = total_score / total_submissions if total_submissions > 0 else 0

        # Get student profile from first submission
        first_submission = submissions[0]
        student_profile = {
            "student_id": student_id,
            "name": first_submission.get("student_name", "Unknown"),
            "email": first_submission.get("student_email", ""),
            "enrollment_date": first_submission.get("submitted_at", "")[:10],
            "major": "Computer Science",
            "year": 2,
            "gpa": round(average_score / 25, 2),  # Convert score to GPA scale
        }

        # Calculate skill progression based on assignment types
        skill_progress = self._calculate_real_skill_progress(submissions)

        # Recent performance trend
        recent_submissions = sorted(submissions, key=lambda x: x.get("submitted_at", ""))[-5:]
        recent_trend = self._calculate_real_trend(recent_submissions)

        return {
            "overview": {
                "total_assignments": total_submissions,
                "average_score": round(average_score, 1),
                "total_score": total_score,
                "max_possible": max_possible,
                "completion_rate": round(average_score, 1),  # Score as percentage
                "current_streak": self._calculate_real_streak(submissions),
                "longest_streak": self._calculate_real_streak(submissions),
                "recent_trend": recent_trend,
            },
            "skill_progress": skill_progress,
            "profile": student_profile,
        }

    def get_performance_timeline(self, student_id: str, period: str = "6months") -> Dict[str, Any]:
        """Get performance data over time for visualization using real data"""
        submissions = self._get_student_submissions(student_id)

        if not submissions:
            return {
                "timeline": [],
                "metrics": {"score_trend": [], "submission_count": [], "labels": []},
            }

        # Group submissions by time period
        if period == "6months":
            grouped_data = self._group_real_submissions_by_month(submissions, 6)
        elif period == "3months":
            grouped_data = self._group_real_submissions_by_week(submissions, 12)
        else:  # 1month
            grouped_data = self._group_real_submissions_by_day(submissions, 30)

        return {
            "timeline": grouped_data,
            "metrics": {
                "score_trend": [g["avg_score"] for g in grouped_data],
                "submission_count": [g["count"] for g in grouped_data],
                "labels": [g["period"] for g in grouped_data],
            },
        }

    def get_skill_analysis(self, student_id: str) -> Dict[str, Any]:
        """Get detailed skill-wise performance analysis using real data"""
        submissions = self._get_student_submissions(student_id)

        if not submissions:
            return {"skills": {}, "strongest_skills": [], "improvement_areas": []}

        skills_data = self._calculate_real_skill_progress(submissions)

        # Calculate metrics for each skill
        skill_metrics = {}
        for skill, data in skills_data.items():
            avg_score = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0

            skill_metrics[skill] = {
                "average_score": round(avg_score, 1),
                "total_submissions": data["submissions"],
                "proficiency_level": data["current_level"],
                "progress": data["progress"],
                "trend": "improving" if data["progress"] > 0 else "stable",
            }

        # Sort skills by performance
        sorted_skills = sorted(
            skill_metrics.items(), key=lambda x: x[1]["average_score"], reverse=True
        )

        return {
            "skills": skill_metrics,
            "strongest_skills": sorted_skills[:3] if len(sorted_skills) >= 3 else sorted_skills,
            "improvement_areas": sorted_skills[-3:] if len(sorted_skills) >= 3 else [],
        }

    def get_comparative_analysis(self, student_id: str) -> Dict[str, Any]:
        """Get comparative analysis against class averages using real data"""
        student_submissions = self._get_student_submissions(student_id)

        if not student_submissions:
            return {
                "student_average": 0,
                "class_average": 0,
                "percentile": 0,
                "rank": 0,
                "total_students": 0,
                "performance_comparison": {
                    "above_average": False,
                    "difference": 0,
                    "percentage_difference": 0,
                },
                "peer_comparison": {
                    "similar_students": 0,
                    "better_than": 0,
                    "improvement_potential": 0,
                },
            }

        # Calculate student average
        student_avg = sum(s.get("score", 0) for s in student_submissions) / len(student_submissions)

        # Calculate class average from all submissions
        all_scores = [s.get("score", 0) for s in self.submissions_data]
        class_avg = sum(all_scores) / len(all_scores) if all_scores else 0

        # Get unique students
        unique_students = set()
        student_averages = {}

        for submission in self.submissions_data:
            student_name = submission.get("student_name", "")
            if student_name:
                unique_students.add(student_name)
                if student_name not in student_averages:
                    student_averages[student_name] = []
                student_averages[student_name].append(submission.get("score", 0))

        # Calculate averages for each student
        student_avg_scores = {}
        for name, scores in student_averages.items():
            student_avg_scores[name] = sum(scores) / len(scores)

        # Calculate rank and percentile
        sorted_averages = sorted(student_avg_scores.values(), reverse=True)
        total_students = len(unique_students)

        # Find current student's rank
        current_student_name = (
            student_submissions[0].get("student_name", "") if student_submissions else ""
        )
        current_student_avg = student_avg_scores.get(current_student_name, student_avg)

        rank = 1
        for avg in sorted_averages:
            if avg > current_student_avg:
                rank += 1
            else:
                break

        percentile = (
            round((total_students - rank + 1) / total_students * 100, 1)
            if total_students > 0
            else 0
        )

        return {
            "student_average": round(student_avg, 1),
            "class_average": round(class_avg, 1),
            "percentile": percentile,
            "rank": rank,
            "total_students": total_students,
            "performance_comparison": {
                "above_average": student_avg > class_avg,
                "difference": round(student_avg - class_avg, 1),
                "percentage_difference": round(((student_avg - class_avg) / class_avg) * 100, 1)
                if class_avg > 0
                else 0,
            },
            "peer_comparison": {
                "similar_students": max(1, total_students // 10),
                "better_than": round((total_students - rank) / total_students * 100, 1)
                if total_students > 0
                else 0,
                "improvement_potential": max(0, round(90 - student_avg, 1)),
            },
        }

    def get_achievement_progress(self, student_id: str) -> Dict[str, Any]:
        """Get achievement and milestone progress based on real data"""
        submissions = self._get_student_submissions(student_id)

        if not submissions:
            achievements = [
                {
                    "name": "First Submission",
                    "description": "Complete your first assignment",
                    "earned": False,
                    "progress": 0,
                },
                {
                    "name": "Perfect Score",
                    "description": "Get 100% on an assignment",
                    "earned": False,
                    "progress": 0,
                },
                {
                    "name": "Skill Master",
                    "description": "Master a programming skill",
                    "earned": False,
                    "progress": 0,
                },
                {
                    "name": "Consistency King",
                    "description": "Maintain >80% average",
                    "earned": False,
                    "progress": 0,
                },
            ]
        else:
            # Calculate achievements based on real data
            scores = [s.get("score", 0) for s in submissions]
            avg_score = sum(scores) / len(scores)
            max_score = max(scores) if scores else 0

            achievements = [
                {
                    "name": "First Submission",
                    "description": "Complete your first assignment",
                    "earned": len(submissions) > 0,
                    "date": submissions[0].get("submitted_at", "")[:10] if submissions else None,
                },
                {
                    "name": "Perfect Score",
                    "description": "Get 100% on an assignment",
                    "earned": max_score >= 100,
                    "date": next(
                        (
                            s.get("submitted_at", "")[:10]
                            for s in submissions
                            if s.get("score", 0) >= 100
                        ),
                        None,
                    )
                    if max_score >= 100
                    else None,
                    "progress": min(max_score, 100) if not max_score >= 100 else 100,
                },
                {
                    "name": "Multiple Submissions",
                    "description": "Submit 3 or more assignments",
                    "earned": len(submissions) >= 3,
                    "progress": min(len(submissions) * 33, 100),
                },
                {
                    "name": "Good Performance",
                    "description": "Maintain >70% average",
                    "earned": avg_score >= 70,
                    "progress": min(avg_score * 1.43, 100),  # Scale to 100
                },
                {
                    "name": "Consistency King",
                    "description": "Maintain >80% average",
                    "earned": avg_score >= 80,
                    "progress": min(avg_score * 1.25, 100),  # Scale to 100
                },
            ]

        return {
            "achievements": achievements,
            "earned_count": len([a for a in achievements if a.get("earned", False)]),
            "total_count": len(achievements),
            "recent_achievements": [a for a in achievements if a.get("earned", False)][-3:],
            "next_milestone": next((a for a in achievements if not a.get("earned", False)), None),
        }

    def get_detailed_recommendations(self, student_id: str) -> Dict[str, Any]:
        """Get personalized recommendations for improvement based on real data"""
        submissions = self._get_student_submissions(student_id)

        if not submissions:
            return {
                "immediate_actions": [
                    "Start by submitting your first assignment",
                    "Review the assignment requirements carefully",
                    "Practice basic programming concepts",
                ],
                "skill_development": [
                    "Learn Python fundamentals",
                    "Practice problem-solving techniques",
                    "Study algorithm basics",
                ],
                "study_plan": {
                    "this_week": ["Complete first assignment", "Practice basic syntax"],
                    "this_month": ["Submit 3 assignments", "Learn debugging techniques"],
                    "this_semester": [
                        "Achieve consistent submissions",
                        "Build programming confidence",
                    ],
                },
                "resources": [
                    {"type": "Tutorial", "title": "Python Basics", "url": "#"},
                    {"type": "Practice", "title": "Beginner Challenges", "url": "#"},
                    {"type": "Video", "title": "Programming Fundamentals", "url": "#"},
                ],
            }

        # Analyze performance
        scores = [s.get("score", 0) for s in submissions]
        avg_score = sum(scores) / len(scores)
        min_score = min(scores)

        # Generate recommendations based on performance
        immediate_actions = []
        skill_development = []

        if avg_score < 50:
            immediate_actions.extend(
                [
                    f"Focus on fundamentals - current average: {avg_score:.1f}%",
                    "Review assignment requirements more carefully",
                    "Practice debugging techniques",
                ]
            )
            skill_development.extend(
                [
                    "Strengthen programming basics",
                    "Practice more simple problems",
                    "Learn proper code structure",
                ]
            )
        elif avg_score < 70:
            immediate_actions.extend(
                [
                    f"Improve consistency - current average: {avg_score:.1f}%",
                    "Focus on test case coverage",
                    "Practice algorithm implementation",
                ]
            )
            skill_development.extend(
                [
                    "Study common algorithms",
                    "Practice problem-solving patterns",
                    "Learn optimization techniques",
                ]
            )
        else:
            immediate_actions.extend(
                [
                    f"Great work! Current average: {avg_score:.1f}%",
                    "Challenge yourself with harder problems",
                    "Help peers with code reviews",
                ]
            )
            skill_development.extend(
                [
                    "Explore advanced algorithms",
                    "Study system design concepts",
                    "Practice competitive programming",
                ]
            )

        # Analyze assignment types for specific recommendations
        assignment_types = [s.get("assignment_title", "").lower() for s in submissions]
        weak_areas = []

        for assignment in assignment_types:
            if "sort" in assignment and any(
                s.get("score", 0) < 60
                for s in submissions
                if "sort" in s.get("assignment_title", "").lower()
            ):
                weak_areas.append("Sorting Algorithms")
            elif "search" in assignment and any(
                s.get("score", 0) < 60
                for s in submissions
                if "search" in s.get("assignment_title", "").lower()
            ):
                weak_areas.append("Search Algorithms")

        if weak_areas:
            immediate_actions.insert(0, f'Focus on {", ".join(weak_areas)} - needs improvement')

        return {
            "immediate_actions": immediate_actions,
            "skill_development": skill_development,
            "study_plan": {
                "this_week": [
                    "Review lowest scoring assignments",
                    "Practice similar problems",
                    "Focus on weak areas identified",
                ],
                "this_month": [
                    f"Aim to improve average from {avg_score:.1f}% to {min(avg_score + 10, 95):.1f}%",
                    "Complete all assignments on time",
                    "Participate in code reviews",
                ],
                "this_semester": [
                    "Achieve consistent high performance",
                    "Master all core programming concepts",
                    "Mentor other students",
                ],
            },
            "resources": [
                {"type": "Tutorial", "title": "Algorithm Practice", "url": "#"},
                {"type": "Practice", "title": "Coding Challenges", "url": "#"},
                {"type": "Video", "title": "Problem Solving Techniques", "url": "#"},
            ],
        }

    def _calculate_current_streak(self, submissions: List[Dict]) -> int:
        """Calculate current submission streak"""
        streak = 0
        current_date = datetime.now().date()

        for submission in sorted(submissions, key=lambda x: x["submission_date"], reverse=True):
            sub_date = datetime.fromisoformat(submission["submission_date"]).date()
            days_diff = (current_date - sub_date).days

            if days_diff <= streak + 1:
                streak += 1
            else:
                break

        return min(streak, 15)  # Cap at reasonable number

    def _calculate_longest_streak(self, submissions: List[Dict]) -> int:
        """Calculate longest submission streak"""
        return random.randint(5, 20)  # Mock data

    def _calculate_skill_progress(self, submissions: List[Dict]) -> Dict[str, Any]:
        """Calculate skill progression over time"""
        skills = {}
        for submission in submissions:
            skill = submission["skill"]
            if skill not in skills:
                skills[skill] = []
            skills[skill].append(submission["score"])

        skill_progress = {}
        for skill, scores in skills.items():
            if len(scores) >= 3:
                recent_avg = sum(scores[:3]) / 3
                overall_avg = sum(scores) / len(scores)
                skill_progress[skill] = {
                    "current_level": self._score_to_level(recent_avg),
                    "progress": round(recent_avg - overall_avg, 1),
                    "submissions": len(scores),
                }

        return skill_progress

    def _calculate_trend(self, submissions: List[Dict]) -> str:
        """Calculate performance trend"""
        if len(submissions) < 3:
            return "stable"

        scores = [s["score"] for s in submissions[-5:]]
        if len(scores) < 3:
            return "stable"

        recent = sum(scores[-2:]) / 2
        earlier = sum(scores[:-2]) / len(scores[:-2])

        diff = recent - earlier
        if diff > 5:
            return "improving"
        elif diff < -5:
            return "declining"
        else:
            return "stable"

    def _score_to_level(self, score: float) -> str:
        """Convert score to proficiency level"""
        if score >= 90:
            return "Expert"
        elif score >= 80:
            return "Advanced"
        elif score >= 70:
            return "Intermediate"
        elif score >= 60:
            return "Beginner"
        else:
            return "Novice"

    def _calculate_proficiency(
        self, avg_score: float, avg_attempts: float, submissions: int
    ) -> str:
        """Calculate overall skill proficiency"""
        score_weight = avg_score * 0.6
        efficiency_weight = (1 / avg_attempts) * 30 * 0.2
        experience_weight = min(submissions / 10, 1) * 20 * 0.2

        total_score = score_weight + efficiency_weight + experience_weight

        if total_score >= 85:
            return "Expert"
        elif total_score >= 75:
            return "Advanced"
        elif total_score >= 65:
            return "Intermediate"
        elif total_score >= 55:
            return "Beginner"
        else:
            return "Novice"

    def _group_by_month(self, submissions: List[Dict], months: int) -> List[Dict]:
        """Group submissions by month"""
        from collections import defaultdict

        grouped = defaultdict(list)

        for submission in submissions:
            date = datetime.fromisoformat(submission["submission_date"])
            month_key = date.strftime("%Y-%m")
            grouped[month_key].append(submission)

        result = []
        for month, subs in sorted(grouped.items()):
            if subs:
                avg_score = sum(s["score"] for s in subs) / len(subs)
                avg_time = sum(s["time_spent"] for s in subs) / len(subs)
                result.append(
                    {
                        "period": month,
                        "count": len(subs),
                        "avg_score": round(avg_score, 1),
                        "avg_time": round(avg_time, 1),
                    }
                )

        return result[-months:] if len(result) > months else result

    def _group_by_week(self, submissions: List[Dict], weeks: int) -> List[Dict]:
        """Group submissions by week"""
        from collections import defaultdict

        grouped = defaultdict(list)

        for submission in submissions:
            date = datetime.fromisoformat(submission["submission_date"])
            week_start = date - timedelta(days=date.weekday())
            week_key = week_start.strftime("%Y-W%W")
            grouped[week_key].append(submission)

        result = []
        for week, subs in sorted(grouped.items()):
            if subs:
                avg_score = sum(s["score"] for s in subs) / len(subs)
                avg_time = sum(s["time_spent"] for s in subs) / len(subs)
                result.append(
                    {
                        "period": week,
                        "count": len(subs),
                        "avg_score": round(avg_score, 1),
                        "avg_time": round(avg_time, 1),
                    }
                )

        return result[-weeks:] if len(result) > weeks else result

    def _group_by_day(self, submissions: List[Dict], days: int) -> List[Dict]:
        """Group submissions by day"""
        from collections import defaultdict

        grouped = defaultdict(list)

        for submission in submissions:
            date = datetime.fromisoformat(submission["submission_date"])
            day_key = date.strftime("%Y-%m-%d")
            grouped[day_key].append(submission)

        result = []
        for day, subs in sorted(grouped.items()):
            if subs:
                avg_score = sum(s["score"] for s in subs) / len(subs)
                avg_time = sum(s["time_spent"] for s in subs) / len(subs)
                result.append(
                    {
                        "period": day,
                        "count": len(subs),
                        "avg_score": round(avg_score, 1),
                        "avg_time": round(avg_time, 1),
                    }
                )

        return result[-days:] if len(result) > days else result

    def _calculate_real_skill_progress(self, submissions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate skill progression based on real assignment types"""
        skills = {}

        for submission in submissions:
            # Extract skill from assignment title
            assignment_title = submission.get("assignment_title", "").lower()
            skill = "Python"  # Default skill

            if "sort" in assignment_title or "bubble" in assignment_title:
                skill = "Sorting Algorithms"
            elif "search" in assignment_title or "binary" in assignment_title:
                skill = "Search Algorithms"
            elif "factorial" in assignment_title or "fibonacci" in assignment_title:
                skill = "Recursion"
            elif "calculator" in assignment_title:
                skill = "Basic Programming"

            if skill not in skills:
                skills[skill] = {"scores": [], "submissions": 0, "current_level": "Beginner"}

            skills[skill]["scores"].append(submission.get("score", 0))
            skills[skill]["submissions"] += 1

        # Calculate levels
        for skill, data in skills.items():
            avg_score = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0
            if avg_score >= 90:
                data["current_level"] = "Expert"
            elif avg_score >= 75:
                data["current_level"] = "Advanced"
            elif avg_score >= 60:
                data["current_level"] = "Intermediate"
            else:
                data["current_level"] = "Beginner"

            data["progress"] = round(avg_score - 50, 1) if avg_score > 50 else 0

        return skills

    def _calculate_real_trend(self, submissions: List[Dict[str, Any]]) -> str:
        """Calculate performance trend from real submissions"""
        if len(submissions) < 2:
            return "stable"

        scores = [s.get("score", 0) for s in submissions]
        if len(scores) < 2:
            return "stable"

        recent_avg = sum(scores[-2:]) / 2
        earlier_avg = sum(scores[:-2]) / len(scores[:-2]) if len(scores) > 2 else scores[0]

        diff = recent_avg - earlier_avg
        if diff > 10:
            return "improving"
        elif diff < -10:
            return "declining"
        else:
            return "stable"

    def _calculate_real_streak(self, submissions: List[Dict[str, Any]]) -> int:
        """Calculate submission streak from real data"""
        if not submissions:
            return 0

        # Sort by submission date
        sorted_submissions = sorted(submissions, key=lambda x: x.get("submitted_at", ""))

        # For simplicity, return number of submissions as streak
        return len(sorted_submissions)

    def _group_real_submissions_by_month(
        self, submissions: List[Dict[str, Any]], months: int
    ) -> List[Dict]:
        """Group real submissions by month"""
        from collections import defaultdict

        grouped = defaultdict(list)

        for submission in submissions:
            date_str = submission.get("submitted_at", "")
            if date_str:
                try:
                    date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    month_key = date.strftime("%Y-%m")
                    grouped[month_key].append(submission)
                except:
                    continue

        result = []
        for month, subs in sorted(grouped.items()):
            if subs:
                avg_score = sum(s.get("score", 0) for s in subs) / len(subs)
                result.append(
                    {"period": month, "count": len(subs), "avg_score": round(avg_score, 1)}
                )

        return result[-months:] if len(result) > months else result

    def _group_real_submissions_by_week(
        self, submissions: List[Dict[str, Any]], weeks: int
    ) -> List[Dict]:
        """Group real submissions by week"""
        from collections import defaultdict

        grouped = defaultdict(list)

        for submission in submissions:
            date_str = submission.get("submitted_at", "")
            if date_str:
                try:
                    date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    week_start = date - timedelta(days=date.weekday())
                    week_key = week_start.strftime("%Y-W%W")
                    grouped[week_key].append(submission)
                except:
                    continue

        result = []
        for week, subs in sorted(grouped.items()):
            if subs:
                avg_score = sum(s.get("score", 0) for s in subs) / len(subs)
                result.append(
                    {"period": week, "count": len(subs), "avg_score": round(avg_score, 1)}
                )

        return result[-weeks:] if len(result) > weeks else result

    def _group_real_submissions_by_day(
        self, submissions: List[Dict[str, Any]], days: int
    ) -> List[Dict]:
        """Group real submissions by day"""
        from collections import defaultdict

        grouped = defaultdict(list)

        for submission in submissions:
            date_str = submission.get("submitted_at", "")
            if date_str:
                try:
                    date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    day_key = date.strftime("%Y-%m-%d")
                    grouped[day_key].append(submission)
                except:
                    continue

        result = []
        for day, subs in sorted(grouped.items()):
            if subs:
                avg_score = sum(s.get("score", 0) for s in subs) / len(subs)
                result.append({"period": day, "count": len(subs), "avg_score": round(avg_score, 1)})

        return result[-days:] if len(result) > days else result

    def get_all_students_overview(self) -> Dict[str, Any]:
        """Get overview of all students for teacher dashboard"""
        # Get unique students from submissions
        students_data = {}

        for submission in self.submissions_data:
            student_name = submission.get("student_name", "")
            student_email = submission.get("student_email", "")

            if student_name and student_name not in students_data:
                students_data[student_name] = {
                    "name": student_name,
                    "email": student_email,
                    "total_score": 0,
                    "assignment_count": 0,
                    "last_submission": "",
                }

            if student_name:
                students_data[student_name]["total_score"] += submission.get("score", 0)
                students_data[student_name]["assignment_count"] += 1

                # Update last submission date
                current_date = submission.get("submitted_at", "")
                if current_date > students_data[student_name]["last_submission"]:
                    students_data[student_name]["last_submission"] = current_date

        # Calculate averages and format data
        students_list = []
        for student_name, data in students_data.items():
            average_score = (
                round(data["total_score"] / data["assignment_count"], 1)
                if data["assignment_count"] > 0
                else 0
            )

            students_list.append(
                {
                    "id": student_name.lower().replace(" ", "_"),
                    "name": data["name"],
                    "email": data["email"],
                    "total_assignments": data["assignment_count"],
                    "average_score": average_score,
                    "last_submission": data["last_submission"][:19]
                    if data["last_submission"]
                    else "",
                    "status": "Active" if average_score >= 60 else "Needs Help",
                    "grade": self._score_to_grade(average_score),
                }
            )

        # Sort by average score (descending)
        students_list.sort(key=lambda x: x["average_score"], reverse=True)

        return {
            "students": students_list,
            "total_students": len(students_list),
            "class_average": round(
                sum(s["average_score"] for s in students_list) / len(students_list), 1
            )
            if students_list
            else 0,
        }

    def get_class_statistics(self) -> Dict[str, Any]:
        """Get overall class statistics"""
        if not self.submissions_data:
            return {
                "overview": {
                    "total_students": 0,
                    "total_submissions": 0,
                    "class_average": 0,
                    "pass_rate": 0,
                },
                "performance_distribution": {},
                "assignment_statistics": {},
                "recent_activity": [],
            }

        # Get unique students and basic stats
        unique_students = set(
            s.get("student_name", "") for s in self.submissions_data if s.get("student_name")
        )
        all_scores = [s.get("score", 0) for s in self.submissions_data if s.get("score") is not None]
        class_average = sum(all_scores) / len(all_scores) if all_scores else 0
        pass_rate = (
            (len([s for s in all_scores if s >= 60]) / len(all_scores)) * 100 if all_scores else 0
        )

        # Performance distribution
        grade_distribution = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
        for score in all_scores:
            grade_distribution[self._score_to_grade(score)] += 1

        return {
            "overview": {
                "total_students": len(unique_students),
                "total_submissions": len(self.submissions_data),
                "class_average": round(class_average, 1),
                "pass_rate": round(pass_rate, 1),
            },
            "performance_distribution": grade_distribution,
            "recent_activity": [
                {
                    "student": s.get("student_name", ""),
                    "assignment": s.get("assignment_title", ""),
                    "score": s.get("score", 0),
                    "submitted_at": s.get("submitted_at", "")[:19],
                }
                for s in sorted(
                    self.submissions_data, key=lambda x: x.get("submitted_at", ""), reverse=True
                )[:10]
            ],
        }

    def _score_to_grade(self, score: float) -> str:
        """Convert numerical score to letter grade"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def delete_student_submissions(self, student_identifier: str) -> bool:
        """Delete all submissions for a specific student"""
        try:
            original_count = len(self.submissions_data)

            # Filter out submissions from the specified student
            self.submissions_data = [
                submission
                for submission in self.submissions_data
                if not (
                    student_identifier.lower() in submission.get("student_name", "").lower()
                    or student_identifier.lower() in submission.get("student_email", "").lower()
                )
            ]

            # Save updated data back to file
            self._save_submissions_data()

            # Return True if any submissions were deleted
            return len(self.submissions_data) < original_count

        except Exception as e:
            print(f"Error deleting student submissions: {e}")
            return False

    def delete_submission(self, submission_id: str) -> bool:
        """Delete a specific submission by ID"""
        try:
            original_count = len(self.submissions_data)

            # Filter out the specific submission
            self.submissions_data = [
                submission
                for submission in self.submissions_data
                if submission.get("id", "") != submission_id
            ]

            # Save updated data back to file
            self._save_submissions_data()

            # Return True if submission was deleted
            return len(self.submissions_data) < original_count

        except Exception as e:
            print(f"Error deleting submission: {e}")
            return False

    def clear_all_submissions(self) -> bool:
        """Clear all submission data"""
        try:
            self.submissions_data = []
            self._save_submissions_data()
            return True
        except Exception as e:
            print(f"Error clearing all submissions: {e}")
            return False

    def _save_submissions_data(self) -> bool:
        """Save submissions data back to JSON file"""
        try:
            submissions_file = os.path.join(
                os.path.dirname(__file__), "..", "submissions_data.json"
            )
            with open(submissions_file, "w") as f:
                json.dump(self.submissions_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving submissions data: {e}")
            return False
