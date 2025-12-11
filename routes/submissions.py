import json
import os
from datetime import datetime
from functools import wraps
import uuid

from flask import Blueprint, jsonify, request, session

submissions_bp = Blueprint("submissions", __name__)


def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated_function


def load_submissions():
    """Load submissions from JSON file"""
    submissions_file = "submissions_data.json"
    if os.path.exists(submissions_file):
        with open(submissions_file, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def save_submissions(submissions):
    """Save submissions to JSON file"""
    submissions_file = "submissions_data.json"
    with open(submissions_file, "w") as f:
        json.dump(submissions, f, indent=2)


@submissions_bp.route("/submit", methods=["POST"])
@require_auth
def submit_code():
    """Submit code for grading"""
    try:
        data = request.get_json(silent=True)

        # Validate required fields
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        assignment_id = data.get("assignment_id")
        code = data.get("code")
        language = data.get("language", "python")

        if not assignment_id:
            return jsonify({"error": "assignment_id is required"}), 400

        if not code or not code.strip():
            return jsonify({"error": "code is required and cannot be empty"}), 400

        # Get user from session
        user_id = session.get("user_id")
        user_email = session.get("user_email", f"user_{user_id}@example.com")

        # Create submission
        submission_id = str(uuid.uuid4())
        submission = {
            "id": submission_id,
            "submission_id": submission_id,
            "user_id": user_id,
            "student_email": user_email,
            "assignment_id": assignment_id,
            "code": code,
            "language": language,
            "submitted_at": datetime.utcnow().isoformat(),
            "status": "pending",
            "score": None
        }

        # Load existing submissions and add new one
        submissions = load_submissions()
        submissions.append(submission)
        save_submissions(submissions)

        return jsonify({
            "status": "success",
            "message": "Code submitted successfully",
            "id": submission_id,
            "submission_id": submission_id,
            "submitted_at": submission["submitted_at"]
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@submissions_bp.route("/my-submissions", methods=["GET"])
@require_auth
def get_my_submissions():
    """Get submissions for the authenticated user"""
    try:
        user_id = session.get("user_id")
        user_email = session.get("user_email")

        submissions = load_submissions()

        # Filter submissions for this user
        user_submissions = [
            sub for sub in submissions
            if sub.get("user_id") == user_id or sub.get("student_email") == user_email
        ]

        # Handle pagination
        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 10, type=int)

        # Apply pagination
        start = (page - 1) * limit
        end = start + limit
        paginated_submissions = user_submissions[start:end]

        return jsonify({
            "status": "success",
            "data": paginated_submissions,
            "total": len(user_submissions),
            "page": page,
            "limit": limit
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@submissions_bp.route("/<submission_id>", methods=["GET"])
@require_auth
def get_submission_details(submission_id):
    """Get details of a specific submission"""
    try:
        user_id = session.get("user_id")
        user_email = session.get("user_email")

        submissions = load_submissions()

        # Find the submission
        submission = next(
            (sub for sub in submissions if sub.get("id") == submission_id or sub.get("submission_id") == submission_id),
            None
        )

        if not submission:
            return jsonify({"error": "Submission not found"}), 404

        # Check if user owns this submission
        if submission.get("user_id") != user_id and submission.get("student_email") != user_email:
            return jsonify({"error": "Unauthorized access to this submission"}), 403

        return jsonify({
            "status": "success",
            "data": submission
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@submissions_bp.route("/<submission_id>/results", methods=["GET"])
@require_auth
def get_submission_results(submission_id):
    """Get grading results for a specific submission"""
    try:
        user_id = session.get("user_id")
        user_email = session.get("user_email")

        submissions = load_submissions()

        # Find the submission
        submission = next(
            (sub for sub in submissions if sub.get("id") == submission_id or sub.get("submission_id") == submission_id),
            None
        )

        if not submission:
            return jsonify({"error": "Submission not found"}), 404

        # Check if user owns this submission
        if submission.get("user_id") != user_id and submission.get("student_email") != user_email:
            return jsonify({"error": "Unauthorized access to this submission"}), 403

        # Return results
        results = {
            "submission_id": submission_id,
            "score": submission.get("score"),
            "status": submission.get("status", "pending"),
            "feedback": submission.get("feedback"),
            "graded_at": submission.get("graded_at")
        }

        return jsonify({
            "status": "success",
            "data": results
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@submissions_bp.route("/stats", methods=["GET"])
def get_submission_stats():
    """Get submission statistics"""
    try:
        submissions = load_submissions()

        # Calculate statistics
        total = len(submissions)
        graded = len([s for s in submissions if s.get("score") is not None])
        pending = total - graded

        # Calculate average score
        scores = [s["score"] for s in submissions if s["score"] is not None]
        avg_score = sum(scores) / len(scores) if scores else 0

        return jsonify(
            {
                "status": "success",
                "data": {
                    "total_submissions": total,
                    "graded_submissions": graded,
                    "pending_submissions": pending,
                    "average_score": round(avg_score, 1),
                },
            }
        )

    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@submissions_bp.route("/student/<student_email>", methods=["GET"])
def get_student_submissions(student_email):
    """Get submissions for a specific student"""
    try:
        submissions = load_submissions()

        # Filter submissions for this student
        student_submissions = [sub for sub in submissions if sub["student_email"] == student_email]

        return jsonify({"status": "success", "data": student_submissions})

    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"status": "error", "message": str(e)}), 500


def _time_ago(timestamp_str):
    """Convert timestamp to 'time ago' format"""
    try:
        timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        now = datetime.now()
        diff = now - timestamp

        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"
    except (ValueError, TypeError, AttributeError):
        return "Recently"



@submissions_bp.route("/recent", methods=["GET"])
@require_auth
def get_recent_submissions():
    """Get recent submissions for lecturer dashboard"""
    try:
        submissions = load_submissions()

        # Get limit from query params (default 10)
        limit = request.args.get('limit', 10, type=int)

        # Sort by timestamp (most recent first)
        sorted_submissions = sorted(
            submissions,
            key=lambda x: x.get('timestamp', ''),
            reverse=True
        )

        # Get recent submissions
        recent = sorted_submissions[:limit]

        # Format for frontend
        formatted = []
        for sub in recent:
            formatted.append({
                'id': sub.get('id', ''),
                'student_name': sub.get('student_name', 'Unknown'),
                'student_email': sub.get('student_email', ''),
                'assignment_title': sub.get('assignment_title', 'Untitled'),
                'score': sub.get('score', 0),
                'status': sub.get('status', 'pending'),
                'timestamp': sub.get('timestamp', ''),
                'language': sub.get('language', 'python')
            })

        return jsonify({
            'success': True,
            'submissions': formatted,
            'count': len(formatted)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
