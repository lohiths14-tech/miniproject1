"""
API v2 Gamification Blueprint

Enhanced gamification with achievements and advanced features.
"""

from datetime import datetime
from flask import Blueprint, jsonify, request, session

gamification_v2_bp = Blueprint('gamification_v2', __name__, url_prefix='/api/v2/gamification')


def _add_version_metadata(response_data):
    """Add v2 version metadata to response."""
    response_data['api_version'] = '2.0.0'
    response_data['version'] = 'v2'
    return response_data


@gamification_v2_bp.route('/user/stats', methods=['GET'])
def get_user_stats_v2():
    """Get comprehensive user gamification stats - v2 with achievements."""
    try:
        from services.gamification_service import gamification_service

        user_id = session.get('user_id', 'demo_user')
        achievements = gamification_service.get_user_achievements_summary(user_id)
        level_info = gamification_service.calculate_level_from_points(achievements['total_points'])

        # V2: Add achievement progress
        achievement_progress = {
            'badges_earned': len(achievements.get('badges', [])),
            'total_badges': 15,
            'completion_percentage': round(len(achievements.get('badges', [])) / 15 * 100, 1),
        }

        return jsonify(_add_version_metadata({
            'status': 'success',
            'data': {
                **achievements,
                'level_info': level_info,
                'achievement_progress': achievement_progress,
            }
        }))

    except Exception as e:
        return jsonify(_add_version_metadata({'status': 'error', 'message': str(e)})), 500


@gamification_v2_bp.route('/leaderboard', methods=['GET'])
def get_leaderboard_v2():
    """Get leaderboard with optional filters - v2 with enhanced data."""
    try:
        from services.gamification_service import gamification_service

        course_id = request.args.get('course_id')
        timeframe = request.args.get('timeframe', 'all')
        include_badges = request.args.get('include_badges', 'true').lower() == 'true'

        leaderboard = gamification_service.get_leaderboard(course_id, timeframe)

        # V2: Add rank change indicators
        for i, entry in enumerate(leaderboard):
            entry['rank'] = i + 1
            entry['rank_change'] = 0  # Would be calculated from historical data

        return jsonify(_add_version_metadata({
            'status': 'success',
            'data': {
                'leaderboard': leaderboard,
                'timeframe': timeframe,
                'generated_at': datetime.utcnow().isoformat(),
                'total_participants': len(leaderboard),
            },
        }))

    except Exception as e:
        return jsonify(_add_version_metadata({'status': 'error', 'message': str(e)})), 500


@gamification_v2_bp.route('/badges', methods=['GET'])
def get_all_badges_v2():
    """Get all available badges and achievements - v2 with categories."""
    try:
        from services.gamification_service import gamification_service

        badges = gamification_service.achievements_config['badges']
        challenges = gamification_service.achievements_config['challenges']

        # V2: Categorize badges
        categorized_badges = {
            'streak': {},
            'submission': {},
            'achievement': {},
            'special': {},
        }

        for badge_id, badge in badges.items():
            if 'streak' in badge_id:
                categorized_badges['streak'][badge_id] = badge
            elif 'submission' in badge_id or 'first' in badge_id:
                categorized_badges['submission'][badge_id] = badge
            elif 'perfect' in badge_id or 'master' in badge_id:
                categorized_badges['achievement'][badge_id] = badge
            else:
                categorized_badges['special'][badge_id] = badge

        return jsonify(_add_version_metadata({
            'status': 'success',
            'data': {
                'badges': badges,
                'categorized_badges': categorized_badges,
                'challenges': challenges,
                'total_badges': len(badges),
            }
        }))

    except Exception as e:
        return jsonify(_add_version_metadata({'status': 'error', 'message': str(e)})), 500


@gamification_v2_bp.route('/challenges/monthly', methods=['GET'])
def get_monthly_challenges_v2():
    """Get current monthly challenges - v2 with progress tracking."""
    try:
        from services.gamification_service import gamification_service

        challenges = gamification_service.get_monthly_challenges()
        user_id = session.get('user_id', 'demo_user')

        # V2: Add user progress for each challenge
        for challenge in challenges:
            challenge['user_progress'] = {
                'current': 0,
                'target': challenge.get('target', 10),
                'completed': False,
            }

        return jsonify(_add_version_metadata({
            'status': 'success',
            'data': {
                'challenges': challenges,
                'month': datetime.utcnow().strftime('%Y-%m'),
                'days_remaining': 30 - datetime.utcnow().day,
            },
        }))

    except Exception as e:
        return jsonify(_add_version_metadata({'status': 'error', 'message': str(e)})), 500


@gamification_v2_bp.route('/award-points', methods=['POST'])
def award_points_v2():
    """Award points for a specific action - v2 with bonus multipliers."""
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

        # V2: Add bonus information
        result['bonus_applied'] = False
        result['bonus_multiplier'] = 1.0

        return jsonify(_add_version_metadata({'status': 'success', 'data': result}))

    except Exception as e:
        return jsonify(_add_version_metadata({'status': 'error', 'message': str(e)})), 500


@gamification_v2_bp.route('/achievements', methods=['GET'])
def get_achievements_v2():
    """Get user achievements - v2 only endpoint."""
    try:
        from services.gamification_service import gamification_service

        user_id = session.get('user_id', 'demo_user')
        achievements = gamification_service.get_user_achievements_summary(user_id)

        # V2: Add achievement details
        achievement_details = {
            'earned': achievements.get('badges', []),
            'in_progress': [],
            'locked': [],
            'recent': [],
        }

        return jsonify(_add_version_metadata({
            'status': 'success',
            'data': achievement_details
        }))

    except Exception as e:
        return jsonify(_add_version_metadata({'status': 'error', 'message': str(e)})), 500


@gamification_v2_bp.route('/streak/update', methods=['POST'])
def update_streak_v2():
    """Update user's submission streak - v2."""
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

        # V2: Add streak milestones
        streak_info['next_milestone'] = ((streak_info.get('current_streak', 0) // 7) + 1) * 7
        streak_info['milestone_progress'] = streak_info.get('current_streak', 0) % 7

        return jsonify(_add_version_metadata({'status': 'success', 'data': streak_info}))

    except Exception as e:
        return jsonify(_add_version_metadata({'status': 'error', 'message': str(e)})), 500
