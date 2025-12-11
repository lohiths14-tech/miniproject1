from datetime import datetime

# from bson.objectid import ObjectId  # Unused
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from models import Assignment, User
from services.email_service import send_assignment_notification

assignments_bp = Blueprint("assignments", __name__)


@assignments_bp.route("/", methods=["GET"], strict_slashes=False)
@jwt_required()
def get_assignments():
    """get_assignments function.

    Returns:
        Response data
    """

    try:
        current_user_email = get_jwt_identity()
        user = User.find_by_email(current_user_email)

        if not user:
            return jsonify({"error": "User not found"}), 404

        assignments = Assignment.find_all_active()
        assignments_data = [assignment.to_dict() for assignment in assignments]

        return jsonify({"assignments": assignments_data}), 200

    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"error": f"Failed to get assignments: {str(e)}"}), 500


@assignments_bp.route("/<assignment_id>", methods=["GET"])
@jwt_required()
def get_assignment(assignment_id):
    """get_assignment function.

    Returns:
        Response data
    """

    try:
        assignment = Assignment.find_by_id(assignment_id)
        if not assignment:
            return jsonify({"error": "Assignment not found"}), 404

        return jsonify(assignment.to_dict()), 200

    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"error": f"Failed to get assignment: {str(e)}"}), 500


@assignments_bp.route("/", methods=["POST"], strict_slashes=False)
@jwt_required()
def create_assignment():
    """create_assignment function.

    Returns:
        Response data
    """

    try:
        current_user_email = get_jwt_identity()
        user = User.find_by_email(current_user_email)

        if not user or user.role != "lecturer":
            return jsonify({"error": "Access denied. Only lecturers can create assignments"}), 403

        current_user_id = str(user._id)
        data = request.get_json()

        # Validate required fields
        required_fields = ["title", "description", "deadline"]
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"{field} is required"}), 400

        # Parse deadline
        try:
            deadline = datetime.fromisoformat(data["deadline"].replace("Z", "+00:00"))
        except ValueError:
            return jsonify({"error": "Invalid deadline format. Use ISO format"}), 400

        # Validate test cases
        test_cases = data.get("test_cases", [])
        if not isinstance(test_cases, list):
            return jsonify({"error": "test_cases must be a list"}), 400

        for i, test_case in enumerate(test_cases):
            if (
                not isinstance(test_case, dict)
                or "input" not in test_case
                or "expected_output" not in test_case
            ):
                return (
                    jsonify({"error": f"Test case {i+1} must have input and expected_output"}),
                    400,
                )

        # Create assignment
        assignment = Assignment(
            title=data["title"].strip(),
            description=data["description"].strip(),
            created_by=current_user_id,
            deadline=deadline,
            test_cases=test_cases,
            programming_language=data.get("programming_language", "python"),
            max_score=data.get("max_score", 100),
            starter_code=data.get("starter_code", ""),
            difficulty=data.get("difficulty", "medium"),
        )

        assignment.save()

        # Send notification emails to all students
        try:
            students = current_app.mongo.db.users.find({"role": "student", "is_active": True})
            for student in students:
                send_assignment_notification(
                    student["email"], student["username"], assignment.title, assignment.deadline
                )
        except (ValueError, KeyError, AttributeError) as e:
            print(f"Failed to send notification emails: {str(e)}")

        return (
            jsonify(
                {"message": "Assignment created successfully", "assignment": assignment.to_dict()}
            ),
            201,
        )

    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"error": f"Failed to create assignment: {str(e)}"}), 500


@assignments_bp.route("/<assignment_id>", methods=["PUT"])
@jwt_required()
def update_assignment(assignment_id):
    """update_assignment function.

    Returns:
        Response data
    """

    try:
        current_user_email = get_jwt_identity()
        user = User.find_by_email(current_user_email)

        if not user or user.role != "lecturer":
            return jsonify({"error": "Access denied"}), 403

        current_user_id = str(user._id)
        assignment = Assignment.find_by_id(assignment_id)
        if not assignment:
            return jsonify({"error": "Assignment not found"}), 404

        # Check if lecturer owns this assignment
        if assignment.created_by != current_user_id:
            return jsonify({"error": "You can only update your own assignments"}), 403

        data = request.get_json()

        # Update fields if provided
        if "title" in data:
            assignment.title = data["title"].strip()
        if "description" in data:
            assignment.description = data["description"].strip()
        if "deadline" in data:
            try:
                assignment.deadline = datetime.fromisoformat(
                    data["deadline"].replace("Z", "+00:00")
                )
            except ValueError:
                return jsonify({"error": "Invalid deadline format"}), 400
        if "test_cases" in data:
            assignment.test_cases = data["test_cases"]
        if "programming_language" in data:
            assignment.programming_language = data["programming_language"]
        if "max_score" in data:
            assignment.max_score = data["max_score"]
        if "starter_code" in data:
            assignment.starter_code = data["starter_code"]
        if "difficulty" in data:
            assignment.difficulty = data["difficulty"]
        if "is_active" in data:
            assignment.is_active = data["is_active"]

        assignment.save()

        return (
            jsonify(
                {"message": "Assignment updated successfully", "assignment": assignment.to_dict()}
            ),
            200,
        )

    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"error": f"Failed to update assignment: {str(e)}"}), 500


@assignments_bp.route("/<assignment_id>", methods=["DELETE"])
@jwt_required()
def delete_assignment(assignment_id):
    """delete_assignment function.

    Returns:
        Response data
    """

    try:
        current_user_email = get_jwt_identity()
        user = User.find_by_email(current_user_email)

        if not user or user.role != "lecturer":
            return jsonify({"error": "Access denied"}), 403

        current_user_id = str(user._id)
        assignment = Assignment.find_by_id(assignment_id)
        if not assignment:
            return jsonify({"error": "Assignment not found"}), 404

        # Check if lecturer owns this assignment
        if assignment.created_by != current_user_id:
            return jsonify({"error": "You can only delete your own assignments"}), 403

        # Soft delete - mark as inactive
        assignment.is_active = False
        assignment.save()

        return jsonify({"message": "Assignment deleted successfully"}), 200

    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"error": f"Failed to delete assignment: {str(e)}"}), 500


@assignments_bp.route("/<assignment_id>/submissions", methods=["GET"])
@jwt_required()
def get_assignment_submissions(assignment_id):
    """get_assignment_submissions function.

    Returns:
        Response data
    """

    try:
        current_user_email = get_jwt_identity()
        user = User.find_by_email(current_user_email)

        if not user or user.role != "lecturer":
            return jsonify({"error": "Access denied"}), 403

        current_user_id = str(user._id)
        assignment = Assignment.find_by_id(assignment_id)
        if not assignment:
            return jsonify({"error": "Assignment not found"}), 404

        # Check if lecturer owns this assignment
        if assignment.created_by != current_user_id:
            return jsonify({"error": "You can only view submissions for your own assignments"}), 403

        # Get all submissions for this assignment
        submissions_data = list(
            current_app.mongo.db.submissions.find({"assignment_id": assignment_id})
        )

        # Get student details for each submission
        for submission in submissions_data:
            student = User.find_by_id(submission["student_id"])
            if student:
                submission["student_info"] = {
                    "username": student.username,
                    "email": student.email,
                    "usn": getattr(student, "usn", ""),
                }
            else:
                submission["student_info"] = {"username": "Unknown", "email": "", "usn": ""}

        return jsonify({"assignment": assignment.to_dict(), "submissions": submissions_data}), 200

    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"error": f"Failed to get submissions: {str(e)}"}), 500
