"""lecturer module.

This module provides functionality for the AI Grading System.
"""

import statistics
from datetime import datetime

from bson.objectid import ObjectId
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from models import Assignment, Submission, User
from services.email_service import send_assignment_notification

lecturer_bp = Blueprint("lecturer", __name__)


@lecturer_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def get_lecturer_dashboard():
    """get_lecturer_dashboard function.

    Returns:
        Response data
    """

    try:
        current_user_id = get_jwt_identity()
        user = User.find_by_id(current_user_id)

        if not user or user.role != "lecturer":
            return jsonify({"error": "Access denied"}), 403

        # Get assignments created by this lecturer
        assignments_data = list(
            current_app.mongo.db.assignments.find({"created_by": current_user_id})
        )

        # Get all submissions for these assignments
        assignment_ids = [str(a["_id"]) for a in assignments_data]
        submissions_data = list(
            current_app.mongo.db.submissions.find({"assignment_id": {"$in": assignment_ids}})
        )

        # Get all students
        students_data = list(current_app.mongo.db.users.find({"role": "student"}))

        # Prepare dashboard data
        dashboard_data = {
            "user": user.to_dict(),
            "assignments": assignments_data,
            "recent_submissions": [],
            "students": students_data,
            "statistics": {
                "total_assignments": len(assignments_data),
                "total_submissions": len(submissions_data),
                "pending_grades": 0,
                "average_score": 0,
                "plagiarism_violations": 0,
            },
        }

        # Process submissions for statistics
        total_score = 0
        graded_count = 0
        plagiarism_violations = 0

        for submission in submissions_data:
            if submission.get("status") == "submitted":
                dashboard_data["statistics"]["pending_grades"] += 1
            elif submission.get("status") == "graded":
                total_score += submission.get("score", 0)
                graded_count += 1

            if not submission.get("plagiarism_passed", True):
                plagiarism_violations += 1

            # Add to recent submissions
            dashboard_data["recent_submissions"].append(
                {
                    "assignment_id": submission.get("assignment_id"),
                    "student_id": submission.get("student_id"),
                    "score": submission.get("score", 0),
                    "submitted_at": submission.get("submitted_at"),
                    "plagiarism_passed": submission.get("plagiarism_passed", True),
                    "status": submission.get("status", "submitted"),
                }
            )

        dashboard_data["statistics"]["average_score"] = (
            total_score / graded_count if graded_count > 0 else 0
        )
        dashboard_data["statistics"]["plagiarism_violations"] = plagiarism_violations

        # Sort recent submissions by date
        dashboard_data["recent_submissions"].sort(
            key=lambda x: x.get("submitted_at", datetime.min), reverse=True
        )
        dashboard_data["recent_submissions"] = dashboard_data["recent_submissions"][
            :10
        ]  # Last 10 submissions

        return jsonify(dashboard_data), 200

    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"error": f"Failed to get dashboard data: {str(e)}"}), 500


@lecturer_bp.route("/assignments", methods=["GET"])
@jwt_required()
def get_lecturer_assignments():
    """get_lecturer_assignments function.

    Returns:
        Response data
    """

    try:
        current_user_id = get_jwt_identity()
        user = User.find_by_id(current_user_id)

        if not user or user.role != "lecturer":
            return jsonify({"error": "Access denied"}), 403

        assignments_data = list(
            current_app.mongo.db.assignments.find({"created_by": current_user_id})
        )

        # Add submission statistics for each assignment
        for assignment in assignments_data:
            assignment_id = str(assignment["_id"])
            submissions_count = current_app.mongo.db.submissions.count_documents(
                {"assignment_id": assignment_id}
            )
            assignment["submissions_count"] = submissions_count

        return jsonify({"assignments": assignments_data}), 200

    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"error": f"Failed to get assignments: {str(e)}"}), 500


@lecturer_bp.route("/students", methods=["GET"])
@jwt_required()
def get_students():
    """get_students function.

    Returns:
        Response data
    """

    try:
        current_user_id = get_jwt_identity()
        user = User.find_by_id(current_user_id)

        if not user or user.role != "lecturer":
            return jsonify({"error": "Access denied"}), 403

        students_data = list(
            current_app.mongo.db.users.find(
                {"role": "student"}, {"password_hash": 0}  # Exclude password hash
            )
        )

        # Add submission statistics for each student
        for student in students_data:
            student_id = str(student["_id"])
            submissions_data = list(
                current_app.mongo.db.submissions.find({"student_id": student_id})
            )

            student["statistics"] = {
                "total_submissions": len(submissions_data),
                "average_score": sum(s.get("score", 0) for s in submissions_data)
                / len(submissions_data)
                if submissions_data
                else 0,
                "plagiarism_violations": sum(
                    1 for s in submissions_data if not s.get("plagiarism_passed", True)
                ),
            }

        return jsonify({"students": students_data}), 200

    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"error": f"Failed to get students: {str(e)}"}), 500


@lecturer_bp.route("/analytics", methods=["GET"])
@jwt_required()
def get_analytics():
    """get_analytics function.

    Returns:
        Response data
    """

    try:
        current_user_id = get_jwt_identity()
        user = User.find_by_id(current_user_id)

        if not user or user.role != "lecturer":
            return jsonify({"error": "Access denied"}), 403

        # Get assignments created by this lecturer
        assignment_ids = [
            str(a["_id"])
            for a in current_app.mongo.db.assignments.find({"created_by": current_user_id})
        ]

        # Get all submissions for these assignments
        submissions_data = list(
            current_app.mongo.db.submissions.find({"assignment_id": {"$in": assignment_ids}})
        )

        # Calculate analytics
        analytics = {
            "score_distribution": {"90-100": 0, "80-89": 0, "70-79": 0, "60-69": 0, "below-60": 0},
            "submission_trends": {},
            "plagiarism_statistics": {
                "total_submissions": len(submissions_data),
                "violations": 0,
                "violation_rate": 0,
            },
            "performance_metrics": {
                "average_score": 0,
                "highest_score": 0,
                "lowest_score": 100,
                "standard_deviation": 0,
            },
        }

        scores = []
        for submission in submissions_data:
            score = submission.get("score", 0)
            scores.append(score)

            # Score distribution
            if score >= 90:
                analytics["score_distribution"]["90-100"] += 1
            elif score >= 80:
                analytics["score_distribution"]["80-89"] += 1
            elif score >= 70:
                analytics["score_distribution"]["70-79"] += 1
            elif score >= 60:
                analytics["score_distribution"]["60-69"] += 1
            else:
                analytics["score_distribution"]["below-60"] += 1

            # Plagiarism statistics
            if not submission.get("plagiarism_passed", True):
                analytics["plagiarism_statistics"]["violations"] += 1

            # Submission trends (by date)
            submitted_at = submission.get("submitted_at")
            if submitted_at:
                date_key = submitted_at.strftime("%Y-%m-%d")
                analytics["submission_trends"][date_key] = (
                    analytics["submission_trends"].get(date_key, 0) + 1
                )

        # Performance metrics
        if scores:
            import statistics

            analytics["performance_metrics"]["average_score"] = statistics.mean(scores)
            analytics["performance_metrics"]["highest_score"] = max(scores)
            analytics["performance_metrics"]["lowest_score"] = min(scores)
            analytics["performance_metrics"]["standard_deviation"] = (
                statistics.stdev(scores) if len(scores) > 1 else 0
            )

        # Plagiarism violation rate
        if analytics["plagiarism_statistics"]["total_submissions"] > 0:
            analytics["plagiarism_statistics"]["violation_rate"] = (
                analytics["plagiarism_statistics"]["violations"]
                / analytics["plagiarism_statistics"]["total_submissions"]
            ) * 100

        return jsonify(analytics), 200

    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"error": f"Failed to get analytics: {str(e)}"}), 500


@lecturer_bp.route("/leaderboard", methods=["GET"])
@jwt_required()
def get_leaderboard():
    """get_leaderboard function.

    Returns:
        Response data
    """

    try:
        current_user_id = get_jwt_identity()
        user = User.find_by_id(current_user_id)

        if not user or user.role != "lecturer":
            return jsonify({"error": "Access denied"}), 403

        # Get all students with their submission statistics
        students_data = list(
            current_app.mongo.db.users.find({"role": "student"}, {"password_hash": 0})
        )

        leaderboard = []
        for student in students_data:
            student_id = str(student["_id"])
            submissions_data = list(
                current_app.mongo.db.submissions.find({"student_id": student_id})
            )

            if submissions_data:
                average_score = sum(s.get("score", 0) for s in submissions_data) / len(
                    submissions_data
                )
                total_score = sum(s.get("score", 0) for s in submissions_data)
                plagiarism_violations = sum(
                    1 for s in submissions_data if not s.get("plagiarism_passed", True)
                )

                leaderboard.append(
                    {
                        "student_id": student_id,
                        "username": student.get("username", ""),
                        "usn": student.get("usn", ""),
                        "average_score": round(average_score, 2),
                        "total_score": total_score,
                        "total_submissions": len(submissions_data),
                        "plagiarism_violations": plagiarism_violations,
                    }
                )

        # Sort by average score (descending)
        leaderboard.sort(key=lambda x: x["average_score"], reverse=True)

        # Add rank
        for i, entry in enumerate(leaderboard):
            entry["rank"] = i + 1

        return jsonify({"leaderboard": leaderboard}), 200

    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"error": f"Failed to get leaderboard: {str(e)}"}), 500
