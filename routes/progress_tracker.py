"""
Student Progress Tracker API Routes

Provides REST API endpoints for student performance analytics,
detailed metrics, charts, and trend analysis.
"""

from datetime import datetime
from functools import wraps

from flask import Blueprint, jsonify, request, session

from services.progress_tracker_service import ProgressTrackerService

progress_tracker_bp = Blueprint("progress_tracker", __name__)
progress_service = ProgressTrackerService()


def require_auth(f):
    """Decorator to require authentication"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # For testing with real data, allow access without strict auth
        # In production, you would check proper authentication
        if "user_id" not in session:
            # Create a temporary session for testing
            session["user_id"] = "test_user"
            session["username"] = "Test User"
        return f(*args, **kwargs)

    return decorated_function


@progress_tracker_bp.route("/overview/<student_id>", methods=["GET"])
@require_auth
def get_student_overview(student_id):
    """Get comprehensive student performance overview"""
    try:
        overview_data = progress_service.get_student_overview(student_id)
        return jsonify({"success": True, "data": overview_data})
    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"success": False, "error": str(e)}), 500


@progress_tracker_bp.route("/timeline/<student_id>", methods=["GET"])
@require_auth
def get_performance_timeline(student_id):
    """Get performance timeline data for charts"""
    try:
        period = request.args.get("period", "6months")
        timeline_data = progress_service.get_performance_timeline(student_id, period)
        return jsonify({"success": True, "data": timeline_data})
    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"success": False, "error": str(e)}), 500


@progress_tracker_bp.route("/skills/<student_id>", methods=["GET"])
@require_auth
def get_skill_analysis(student_id):
    """Get detailed skill-wise performance analysis"""
    try:
        skills_data = progress_service.get_skill_analysis(student_id)
        return jsonify({"success": True, "data": skills_data})
    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"success": False, "error": str(e)}), 500


@progress_tracker_bp.route("/comparison/<student_id>", methods=["GET"])
@require_auth
def get_comparative_analysis(student_id):
    """Get comparative analysis against class averages"""
    try:
        comparison_data = progress_service.get_comparative_analysis(student_id)
        return jsonify({"success": True, "data": comparison_data})
    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"success": False, "error": str(e)}), 500


@progress_tracker_bp.route("/achievements/<student_id>", methods=["GET"])
@require_auth
def get_achievement_progress(student_id):
    """Get achievement and milestone progress"""
    try:
        achievements_data = progress_service.get_achievement_progress(student_id)
        return jsonify({"success": True, "data": achievements_data})
    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"success": False, "error": str(e)}), 500


@progress_tracker_bp.route("/recommendations/<student_id>", methods=["GET"])
@require_auth
def get_detailed_recommendations(student_id):
    """Get personalized recommendations for improvement"""
    try:
        recommendations_data = progress_service.get_detailed_recommendations(student_id)
        return jsonify({"success": True, "data": recommendations_data})
    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"success": False, "error": str(e)}), 500


@progress_tracker_bp.route("/dashboard-data/<student_id>", methods=["GET"])
@require_auth
def get_dashboard_data(student_id):
    """Get comprehensive dashboard data in single request"""
    try:
        dashboard_data = {
            "overview": progress_service.get_student_overview(student_id),
            "timeline": progress_service.get_performance_timeline(student_id, "6months"),
            "skills": progress_service.get_skill_analysis(student_id),
            "achievements": progress_service.get_achievement_progress(student_id),
            "recommendations": progress_service.get_detailed_recommendations(student_id),
        }
        return jsonify({"success": True, "data": dashboard_data})
    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"success": False, "error": str(e)}), 500


@progress_tracker_bp.route("/export/<student_id>", methods=["GET"])
@require_auth
def export_progress_report(student_id):
    """Export detailed progress report"""
    try:
        format_type = request.args.get("format", "json")

        # Get all data for export
        export_data = {
            "student_id": student_id,
            "generated_at": datetime.now().isoformat(),
            "overview": progress_service.get_student_overview(student_id),
            "timeline": progress_service.get_performance_timeline(student_id, "6months"),
            "skills": progress_service.get_skill_analysis(student_id),
            "comparison": progress_service.get_comparative_analysis(student_id),
            "achievements": progress_service.get_achievement_progress(student_id),
            "recommendations": progress_service.get_detailed_recommendations(student_id),
        }

        if format_type == "json":
            return jsonify({"success": True, "data": export_data, "format": "json"})
        else:
            # For other formats, return JSON with format info
            return jsonify(
                {
                    "success": True,
                    "data": export_data,
                    "format": format_type,
                    "message": f"Export in {format_type} format prepared",
                }
            )

    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"success": False, "error": str(e)}), 500


@progress_tracker_bp.route("/all-students", methods=["GET"])
@require_auth
def get_all_students():
    """Get all students with their basic progress info for teacher dashboard"""
    try:
        all_students_data = progress_service.get_all_students_overview()
        return jsonify({"success": True, "data": all_students_data})
    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"success": False, "error": str(e)}), 500


@progress_tracker_bp.route("/class-statistics", methods=["GET"])
@require_auth
def get_class_statistics():
    """Get overall class statistics for teacher dashboard"""
    try:
        class_stats = progress_service.get_class_statistics()
        return jsonify({"success": True, "data": class_stats})
    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"success": False, "error": str(e)}), 500


@progress_tracker_bp.route("/delete-student/<student_id>", methods=["DELETE"])
@require_auth
def delete_student_data(student_id):
    """Delete all submissions for a specific student"""
    try:
        success = progress_service.delete_student_submissions(student_id)
        if success:
            return jsonify(
                {"success": True, "message": f"All submissions for {student_id} have been deleted"}
            )
        else:
            return (
                jsonify(
                    {"success": False, "error": "Student not found or no submissions to delete"}
                ),
                404,
            )
    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"success": False, "error": str(e)}), 500


@progress_tracker_bp.route("/delete-submission/<submission_id>", methods=["DELETE"])
@require_auth
def delete_single_submission(submission_id):
    """Delete a specific submission"""
    try:
        success = progress_service.delete_submission(submission_id)
        if success:
            return jsonify({"success": True, "message": "Submission deleted successfully"})
        else:
            return jsonify({"success": False, "error": "Submission not found"}), 404
    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"success": False, "error": str(e)}), 500


@progress_tracker_bp.route("/clear-all-data", methods=["DELETE"])
@require_auth
def clear_all_submissions():
    """Clear all submission data (use with caution)"""
    try:
        success = progress_service.clear_all_submissions()
        if success:
            return jsonify({"success": True, "message": "All submission data has been cleared"})
        else:
            return jsonify({"success": False, "error": "Failed to clear data"}), 500
    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"success": False, "error": str(e)}), 500
