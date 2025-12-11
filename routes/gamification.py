"""
Gamification API Routes
Handles all gamification-related endpoints for points, badges, leaderboards, and achievements
"""

import json
from datetime import datetime

from flask import Blueprint, jsonify, request, session

from services.gamification_service import gamification_service

from models import User
from flask_jwt_extended import jwt_required, get_jwt_identity

# Create blueprint
gamification_bp = Blueprint("gamification", __name__)


@gamification_bp.route("/user/stats", methods=["GET"])
@jwt_required()
def get_user_stats():
    """Get comprehensive user gamification stats"""
    try:
        current_user_email = get_jwt_identity()
        user = User.find_by_email(current_user_email)
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404

        user_id = str(user._id)

        # Get user achievement summary
        achievements = gamification_service.get_user_achievements_summary(user_id)

        # Calculate level information
        level_info = gamification_service.calculate_level_from_points(achievements["total_points"])

        return jsonify({"status": "success", "data": {**achievements, "level_info": level_info}})

    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@gamification_bp.route("/points", methods=["GET"])
@jwt_required()
def get_points():
    """Get user total points"""
    try:
        current_user_email = get_jwt_identity()
        user = User.find_by_email(current_user_email)
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404

        user_id = str(user._id)
        achievements = gamification_service.get_user_achievements_summary(user_id)

        return jsonify({"status": "success", "total_points": achievements.get("total_points", 0)})

    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@gamification_bp.route("/leaderboard", methods=["GET"])
@jwt_required()
def get_leaderboard():
    """Get leaderboard with optional filters"""
    try:
        course_id = request.args.get("course_id")
        timeframe = request.args.get("timeframe", "all")  # all, weekly, monthly

        leaderboard = gamification_service.get_leaderboard(course_id, timeframe)

        return jsonify(
            {
                "status": "success",
                "data": {
                    "leaderboard": leaderboard,
                    "timeframe": timeframe,
                    "generated_at": datetime.utcnow().isoformat(),
                },
            }
        )

    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@gamification_bp.route("/badges", methods=["GET"])
@gamification_bp.route("/achievements", methods=["GET"])
@jwt_required()
def get_all_badges():
    """Get all available badges and achievements"""
    try:
        badges = gamification_service.achievements_config["badges"]
        challenges = gamification_service.achievements_config["challenges"]

        return jsonify({"status": "success", "data": {"badges": badges, "challenges": challenges}})

    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@gamification_bp.route("/challenges/monthly", methods=["GET"])
def get_monthly_challenges():
    """Get current monthly challenges"""
    try:
        challenges = gamification_service.get_monthly_challenges()

        return jsonify(
            {
                "status": "success",
                "data": {"challenges": challenges, "month": datetime.utcnow().strftime("%Y-%m")},
            }
        )

    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@gamification_bp.route("/award-points", methods=["POST"])
@jwt_required()
def award_points():
    """Award points for a specific action (admin only)"""
    try:
        current_user_email = get_jwt_identity()
        user = User.find_by_email(current_user_email)
        if not user or user.role != "admin":
            return jsonify({"status": "error", "message": "Access denied. Admin privileges required."}), 403

        data = request.get_json()
        user_id = data.get("user_id")
        action = data.get("action")
        points = data.get("points")
        metadata = data.get("metadata", {})

        # Support manual point awarding
        if not action and points is not None:
            action = "manual_adjustment"
            metadata["points"] = points

        if not user_id or not action:
            return (
                jsonify({"status": "error", "message": "Missing required fields: user_id, action (or points)"}),
                400,
            )

        result = gamification_service.award_points_and_badges(user_id, action, metadata)

        return jsonify({"status": "success", "data": result})

    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@gamification_bp.route("/check-achievements", methods=["POST"])
def check_achievements():
    """Check for new achievements for a user"""
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        user_stats = data.get("user_stats", {})

        if not user_id:
            return jsonify({"status": "error", "message": "Missing required field: user_id"}), 400

        new_badges = gamification_service.check_badge_eligibility(user_stats)

        return jsonify(
            {"status": "success", "data": {"new_badges": new_badges, "user_id": user_id}}
        )

    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@gamification_bp.route("/streak/update", methods=["POST"])
def update_streak():
    """Update user's submission streak"""
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        last_submission = data.get("last_submission_date")

        if not user_id:
            return jsonify({"status": "error", "message": "Missing required field: user_id"}), 400

        # Parse datetime if provided
        last_submission_date = None
        if last_submission:
            last_submission_date = datetime.fromisoformat(last_submission.replace("Z", "+00:00"))

        streak_info = gamification_service.update_streak(user_id, last_submission_date)

        return jsonify({"status": "success", "data": streak_info})

    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@gamification_bp.route("/level/calculate", methods=["POST"])
def calculate_level():
    """Calculate user level from total points"""
    try:
        data = request.get_json()
        total_points = data.get("total_points", 0)

        level_info = gamification_service.calculate_level_from_points(total_points)

        return jsonify({"status": "success", "data": level_info})

    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@gamification_bp.route("/demo/student-profile", methods=["GET"])
def demo_student_profile():
    """Demo endpoint showing a complete student gamification profile"""
    try:
        # Simulate a student's gamification data
        demo_data = {
            "user_info": {"user_id": "demo_student", "username": "alice_coder", "avatar": "👩‍💻"},
            "stats": gamification_service.get_user_achievements_summary("demo_student"),
            "level": gamification_service.calculate_level_from_points(1850),
            "recent_achievements": [
                {
                    "type": "badge",
                    "badge": gamification_service.achievements_config["badges"]["streak_7"],
                    "earned_at": "2025-09-22T14:15:00Z",
                },
                {
                    "type": "points",
                    "amount": 85,
                    "reason": "Perfect score on Array Algorithms",
                    "earned_at": "2025-09-27T09:00:00Z",
                },
            ],
            "leaderboard_position": 3,
            "monthly_challenges": gamification_service.get_monthly_challenges(),
        }

        return jsonify({"status": "success", "data": demo_data})

    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@gamification_bp.route("/demo/award-submission", methods=["POST"])
def demo_award_submission():
    """Demo endpoint for awarding points after submission"""
    try:
        data = request.get_json()
        score = data.get("score", 85)
        time_taken = data.get("time_taken", 600)  # seconds

        # Simulate awarding points for submission
        submission_result = gamification_service.award_points_and_badges(
            "demo_student", "submission", {"score": score, "time_taken": time_taken}
        )

        # Check for speed bonus
        speed_result = None
        if time_taken <= 300:  # 5 minutes
            speed_result = gamification_service.award_points_and_badges(
                "demo_student", "speed_demon", {"time_taken": time_taken}
            )

        return jsonify(
            {
                "status": "success",
                "data": {
                    "submission_award": submission_result,
                    "speed_bonus": speed_result,
                    "total_points_earned": submission_result["points_earned"]
                    + (speed_result["points_earned"] if speed_result else 0),
                },
            }
        )

    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"status": "error", "message": str(e)}), 500
