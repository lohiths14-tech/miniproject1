"""
API v1 Gamification Blueprint

Wraps existing gamification functionality with v1 versioned endpoints.
"""

from datetime import datetime
from flask import Blueprint, jsonify, request, session

gamification_v1_bp = Blueprint('gamification_v1', __name__, url_prefix='/api/v1/gamification')


def _add_version_metadata(response_data):
    """Add v1 version metadata to response."""
    response_data['api_version'] = '1.0.0'
    response_data['version'] = 'v1'
    return response_data


@gamification_v1_bp.route('/user/stats', methods=['GET'])
def get_user_stats_v1():
    """Get comprehensive user gamification stats - v1."""
    try:
        from services.gamification_service import gamification_service

        user_id = session.get('user_id', 'demo_user')
        achievements = gamification_service.get_user_achievements_summary(user_id)
        level_info = gamification_service.calculate_level_from_points(achievements['total_points'])

        return jsonify(_add_version_metadata({
            'status': 'success',
            'data': {**achievements, 'level_info': level_info}
        }))

    except Exception as e:
        return jsonify(_add_version_metadata({'status': 'error', 'message': str(e)})), 500


@gamification_v1_bp.route('/leaderboard', methods=['GET'])
def get_leaderboard_v1():
    """Get leaderboard with optional filters - v1."""
    try:
        from services.gamification_service import gamification_service

        course_id = request.args.get('course_id')
        timeframe = request.args.get('timeframe', 'all')

        leaderboard = gamification_service.get_leaderboard(course_id, timeframe)

        return jsonify(_add_version_metadata({
            'status': 'success',
            'data': {
                'leaderboard': leaderboard,
                'timeframe': timeframe,
                'generated_at': datetime.utcnow().isoformat(),
            },
        }))

    except Exception as e:
        return jsonify(_add_version_metadata({'status': 'error', 'message': str(e)})), 500


@gamification_v1_bp.route('/badges', methods=['GET'])
def get_all_badges_v1():
    """Get all available badges and achievements - v1."""
    try:
        from services.gamification_service import gamification_service

        badges = gamification_service.achievements_config['badges']
        challenges = gamification_service.achievements_config['challenges']

        return jsonify(_add_version_metadata({
            'status': 'success',
            'data': {'badges': badges, 'challenges': challenges}
        }))

    except Exception as e:
        return jsonify(_add_version_metadata({'status': 'error', 'message': str(e)})), 500


@gamification_v1_bp.route('/challenges/monthly', methods=['GET'])
def get_monthly_challenges_v1():
    """Get current monthly challenges - v1."""
    try:
        from services.gamification_service import gamification_service

        challenges = gamification_service.get_monthly_challenges()

        return jsonify(_add_version_metadata({
            'status': 'success',
            'data': {
                'challenges': challenges,
                'month': datetime.utcnow().strftime('%Y-%m')
            },
        }))

    except Exception as e:
        return jsonify(_add_version_metadata({'status': 'error', 'message': str(e)})), 500


@gamification_v1_bp.route('/award-points', methods=['POST'])
def award_points_v1():
    """Award points for a specific action - v1."""
    try:
        from services.gamification_service import gamification_service

        data = request.get_json()
        user_id = data.get('user_id')
        action = data.get('action')
        metadata = data.get('metadata', {})

        if not user_id or not action:
            return jsonify(_add_version_metadata({
                'status': 'error',
                'message': 'Missing required fields: user_id, action'
            })), 400

        result = gamification_service.award_points_and_badges(user_id, action, metadata)

        return jsonify(_add_version_metadata({'status': 'success', 'data': result}))

    except Exception as e:
        return jsonify(_add_version_metadata({'status': 'error', 'message': str(e)})), 500


@gamification_v1_bp.route('/check-achievements', methods=['POST'])
def check_achievements_v1():
    """Check for new achievements for a user - v1."""
    try:
        from services.gamification_service import gamification_service

        data = request.get_json()
        user_id = data.get('user_id')
        user_stats = data.get('user_stats', {})

        if not user_id:
            return jsonify(_add_version_metadata({
                'status': 'error',
                'message': 'Missing required field: user_id'
            })), 400

        new_badges = gamification_service.check_badge_eligibility(user_stats)

        return jsonify(_add_version_metadata({
            'status': 'success',
            'data': {'new_badges': new_badges, 'user_id': user_id}
        }))

    except Exception as e:
        return jsonify(_add_version_metadata({'status': 'error', 'message': str(e)})), 500


@gamification_v1_bp.route('/streak/update', methods=['POST'])
def update_streak_v1():
    """Update user's submission streak - v1."""
    try:
        from services.gamification_service import gamification_service

        data = request.get_json()
        user_id = data.get('user_id')
        last_submission = data.get('last_submission_date')

        if not user_id:
            return jsonify(_add_version_metadata({
                'status': 'error',
                'message': 'Missing required field: user_id'
            })), 400

        last_submission_date = None
        if last_submission:
            last_submission_date = datetime.fromisoformat(last_submission.replace('Z', '+00:00'))

        streak_info = gamification_service.update_streak(user_id, last_submission_date)

        return jsonify(_add_version_metadata({'status': 'success', 'data': streak_info}))

    except Exception as e:
        return jsonify(_add_version_metadata({'status': 'error', 'message': str(e)})), 500


@gamification_v1_bp.route('/level/calculate', methods=['POST'])
def calculate_level_v1():
    """Calculate user level from total points - v1."""
    try:
        from services.gamification_service import gamification_service

        data = request.get_json()
        total_points = data.get('total_points', 0)

        level_info = gamification_service.calculate_level_from_points(total_points)

        return jsonify(_add_version_metadata({'status': 'success', 'data': level_info}))

    except Exception as e:
        return jsonify(_add_version_metadata({'status': 'error', 'message': str(e)})), 500
