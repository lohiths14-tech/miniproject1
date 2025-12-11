"""
Integration tests for achievement award workflow
Tests end-to-end flow: trigger → detection → award → points → leaderboard → notification
**Validates: Requirements 4.5**
"""

import pytest
import json
from unittest.mock import patch, Mock, MagicMock
from datetime import datetime
from services.gamification_service import gamification_service


@pytest.mark.integration
class TestAchievementWorkflow:
    """Test complete achievement award workflow"""

    def test_complete_achievement_award_workflow(self, client, test_db, test_user, test_assignment):
        """
        Test complete achievement award workflow:
        1. Trigger condition is met (e.g., submission)
        2. Achievement is detected
        3. Achievement is awarded
        4. Points are calculated
        5. Leaderboard is updated
        6. User is notified (with mock)
        7. Verify end-to-end data flow
        """
        # Mock email notification service
        with patch('services.email_service.send_email') as mock_email:
            mock_email.return_value = True

            # Step 1: Trigger condition - First submission
            # Simulate user stats for first submission
            user_stats = {
                'total_submissions': 1,
                'perfect_scores': 0,
                'current_streak': 1,
                'languages_used': ['python'],
                'badges': []
            }

            # Step 2: Achievement detection
            new_badges = gamification_service.check_badge_eligibility(user_stats)

            # Verify achievement detected
            assert len(new_badges) > 0, "Should detect at least one achievement"
            first_submission_badge = next(
                (b for b in new_badges if b['badge_id'] == 'first_submission'),
                None
            )
            assert first_submission_badge is not None, "Should detect first submission achievement"

            # Step 3: Achievement is awarded
            badge_config = first_submission_badge['config']
            assert badge_config['name'] == 'First Steps'
            assert badge_config['points'] == 50
            assert badge_config['icon'] == '🎯'

            # Step 4: Points are calculated
            result = gamification_service.award_points_and_badges(
                user_id=str(test_user['_id']),
                action='submission',
                metadata={'score': 85, 'language': 'python'}
            )

            # Verify points awarded
            assert result['points_earned'] > 0, "Should earn points for submission"
            assert result['total_points'] > 0, "Should have total points"
            assert 'new_badges' in result
            assert len(result['new_badges']) > 0, "Should have new badges"

            # Step 5: Verify leaderboard can be generated
            leaderboard = gamification_service.get_leaderboard()
            assert isinstance(leaderboard, list), "Leaderboard should be a list"

            # Step 6: Verify notification would be sent (in real system)
            # In the currenttation, notification is handled by the caller
            # We verify the data is available for notification
            assert 'badges_earned' in result
            assert len(result['badges_earned']) > 0

            # Step 7: Verify end-to-end data flow
            assert result['action'] == 'submission'
            assert 'timestamp' in result
            assert result['current_level'] is not None
            assert result['level_title'] is not None

    def test_achievement_workflow_perfect_score(self, client, test_db, test_user):
        """Test achievement workflow for perfect score"""
        # Simulate user stats with perfect score
        user_stats = {
            'total_submissions': 5,
            'perfect_scores': 1,
            'current_streak': 3,
            'languages_used': ['python'],
            'badges': ['first_submission']
        }

        # Check for perfect score achievement
        new_badges = gamification_service.check_badge_eligibility(user_stats)

        # Verify perfect score badge detected
        perfect_badge = next(
            (b for b in new_badges if b['badge_id'] == 'perfect_score'),
            None
        )
        assert perfect_badge is not None, "Should detect perfect score achievement"
        assert perfect_badge['config']['name'] == 'Perfectionist'
        assert perfect_badge['config']['points'] == 200

    def test_achievement_workflow_streak_badges(self, client, test_db, test_user):
        """Test achievement workflow for streak badges"""
        # Test 3-day streak
        user_stats_3 = {
            'total_submissions': 3,
            'current_streak': 3,
            'badges': ['first_submission']
        }

        badges_3 = gamification_service.check_badge_eligibility(user_stats_3)
        streak_3_badge = next(
            (b for b in badges_3 if b['badge_id'] == 'streak_3'),
            None
        )
        assert streak_3_badge is not None, "Should detect 3-day streak"
        assert streak_3_badge['config']['name'] == 'On Fire'
        assert streak_3_badge['config']['icon'] == '🔥'

        # Test 7-day streak
        user_stats_7 = {
            'total_submissions': 7,
            'current_streak': 7,
            'badges': ['first_submission', 'streak_3']
        }

        badges_7 = gamification_service.check_badge_eligibility(user_stats_7)
        streak_7_badge = next(
            (b for b in badges_7 if b['badge_id'] == 'streak_7'),
            None
        )
        assert streak_7_badge is not None, "Should detect 7-day streak"
        assert streak_7_badge['config']['name'] == 'Week Warrior'
        assert streak_7_badge['config']['icon'] == '🏆'

    def test_achievement_workflow_multi_language(self, client, test_db, test_user):
        """Test achievement workflow for multi-language badge"""
        user_stats = {
            'total_submissions': 10,
            'languages_used': ['python', 'java', 'javascript'],
            'badges': ['first_submission']
        }

        new_badges = gamification_service.check_badge_eligibility(user_stats)

        multi_lang_badge = next(
            (b for b in new_badges if b['badge_id'] == 'multi_language'),
            None
        )
        assert multi_lang_badge is not None, "Should detect multi-language achievement"
        assert multi_lang_badge['config']['name'] == 'Polyglot'
        assert multi_lang_badge['config']['points'] == 400
        assert multi_lang_badge['config']['icon'] == '🌍'

    def test_achievement_workflow_collaboration(self, client, test_db, test_user):
        """Test achievement workflow for collaboration badge"""
        user_stats = {
            'total_submissions': 10,
            'collaboration_sessions': 5,
            'badges': ['first_submission']
        }

        new_badges = gamification_service.check_badge_eligibility(user_stats)

        collab_badge = next(
            (b for b in new_badges if b['badge_id'] == 'helper'),
            None
        )
        assert collab_badge is not None, "Should detect collaboration achievement"
        assert collab_badge['config']['name'] == 'Team Player'
        assert collab_badge['config']['points'] == 250
        assert collab_badge['config']['icon'] == '🤝'

    def test_achievement_workflow_no_duplicate_awards(self, client, test_db, test_user):
        """Test that achievements are not awarded twice"""
        # User already has first_submission badge
        user_stats = {
            'total_submissions': 5,
            'badges': ['first_submission', 'streak_3']
        }

        new_badges = gamification_service.check_badge_eligibility(user_stats)

        # Should not include already earned badges
        badge_ids = [b['badge_id'] for b in new_badges]
        assert 'first_submission' not in badge_ids, "Should not award first_submission again"
        assert 'streak_3' not in badge_ids, "Should not award streak_3 again"

    def test_achievement_workflow_points_calculation(self, client, test_db, test_user):
        """Test points calculation in achievement workflow"""
        # Test submission points with score multiplier
        result = gamification_service.award_points_and_badges(
            user_id=str(test_user['_id']),
            action='submission',
            metadata={'score': 100}
        )

        # Base submission points (50) * multiplier (1 + 100/100 = 2.0) = 100
        assert result['points_earned'] == 100, "Should calculate points with score multiplier"

        # Test streak bonus
        result_streak = gamification_service.award_points_and_badges(
            user_id=str(test_user['_id']),
            action='streak_bonus',
            metadata={'streak_days': 5}
        )

        # Streak bonus should apply multiplier
        assert result_streak['points_earned'] > 0, "Should earn streak bonus points"

    def test_achievement_workflow_level_progression(self, client, test_db, test_user):
        """Test level progression in achievement workflow"""
        # Test different point levels
        test_cases = [
            (0, 'Beginner', '🌱'),
            (500, 'Novice', '🌿'),
            (1500, 'Intermediate', '🌳'),
            (3000, 'Advanced', '🚀'),
            (6000, 'Expert', '⭐'),
            (12000, 'Master', '💎'),
            (25000, 'Legend', '👑')
        ]

        for points, expected_name, expected_icon in test_cases:
            level_info = gamification_service.calculate_level_from_points(points)
            assert level_info['current_level']['name'] == expected_name, \
                f"Points {points} should be {expected_name}"
            assert level_info['current_level']['icon'] == expected_icon, \
                f"Points {points} should have icon {expected_icon}"

    def test_achievement_workflow_leaderboard_update(self, client, test_db):
        """Test leaderboard update in achievement workflow"""
        # Get leaderboard
        leaderboard = gamification_service.get_leaderboard()

        # Verify leaderboard structure
        assert isinstance(leaderboard, list), "Leaderboard should be a list"

        if len(leaderboard) > 0:
            # Verify leaderboard entry structure
            entry = leaderboard[0]
            assert 'user_id' in entry
            assert 'username' in entry
            assert 'total_points' in entry
            assert 'badges_count' in entry
            assert 'rank' in entry

            # Verify leaderboard is sorted by points
            if len(leaderboard) > 1:
                for i in range(len(leaderboard) - 1):
                    assert leaderboard[i]['total_points'] >= leaderboard[i + 1]['total_points'], \
                        "Leaderboard should be sorted by points descending"

    def test_achievement_workflow_user_summary(self, client, test_db, test_user):
        """Test user achievement summary in workflow"""
        summary = gamification_service.get_user_achievements_summary(str(test_user['_id']))

        # Verify summary structure
        assert 'total_points' in summary
        assert 'rank' in summary
        assert 'badges' in summary
        assert 'current_streak' in summary
        assert 'longest_streak' in summary
        assert 'next_badges' in summary
        assert 'recent_activities' in summary

        # Verify badges structure
        if len(summary['badges']) > 0:
            badge = summary['badges'][0]
            assert 'badge_id' in badge
            assert 'earned_at' in badge
            assert 'config' in badge

        # Verify next badges structure
        if len(summary['next_badges']) > 0:
            next_badge = summary['next_badges'][0]
            assert 'badge_id' in next_badge
            assert 'progress' in next_badge
            assert 'required' in next_badge
            assert 'config' in next_badge

    def test_achievement_workflow_monthly_challenges(self, client, test_db):
        """Test monthly challenges in achievement workflow"""
        challenges = gamification_service.get_monthly_challenges()

        # Verify challenges structure
        assert isinstance(challenges, list), "Challenges should be a list"

        if len(challenges) > 0:
            challenge = challenges[0]
            assert 'challenge_id' in challenge
            assert 'config' in challenge
            assert 'deadline' in challenge
            assert 'participation_count' in challenge

            # Verify challenge config
            config = challenge['config']
            assert 'name' in config
            assert 'description' in config
            assert 'points' in config
            assert 'icon' in config

    def test_achievement_workflow_improvement_badge(self, client, test_db, test_user):
        """Test improvement badge in achievement workflow"""
        user_stats = {
            'total_submissions': 10,
            'max_improvement': 35,
            'badges': ['first_submission']
        }

        new_badges = gamification_service.check_badge_eligibility(user_stats)

        improvement_badge = next(
            (b for b in new_badges if b['badge_id'] == 'improver'),
            None
        )
        assert improvement_badge is not None, "Should detect improvement achievement"
        assert improvement_badge['config']['name'] == 'Rising Star'
        assert improvement_badge['config']['points'] == 150
        assert improvement_badge['config']['icon'] == '📈'

    def test_achievement_workflow_first_place_badge(self, client, test_db, test_user):
        """Test first place badge in achievement workflow"""
        user_stats = {
            'total_submissions': 20,
            'leaderboard_rank': 1,
            'badges': ['first_submission']
        }

        new_badges = gamification_service.check_badge_eligibility(user_stats)

        first_place_badge = next(
            (b for b in new_badges if b['badge_id'] == 'first_place'),
            None
        )
        assert first_place_badge is not None, "Should detect first place achievement"
        assert first_place_badge['config']['name'] == 'Champion'
        assert first_place_badge['config']['points'] == 500
        assert first_place_badge['config']['icon'] == '🥇'

    def test_achievement_workflow_speed_demon_badge(self, client, test_db, test_user):
        """Test speed demon badge in achievement workflow"""
        user_stats = {
            'total_submissions': 10,
            'fastest_completion': 250,  # 250 seconds = 4 minutes 10 seconds
            'badges': ['first_submission']
        }

        new_badges = gamification_service.check_badge_eligibility(user_stats)

        speed_badge = next(
            (b for b in new_badges if b['badge_id'] == 'speed_demon'),
            None
        )
        assert speed_badge is not None, "Should detect speed demon achievement"
        assert speed_badge['config']['name'] == 'Speed Demon'
        assert speed_badge['config']['points'] == 300
        assert speed_badge['config']['icon'] == '⚡'

    def test_achievement_workflow_multiple_badges_at_once(self, client, test_db, test_user):
        """Test awarding multiple badges in one workflow"""
        # User meets criteria for multiple badges
        user_stats = {
            'total_submissions': 1,  # First submission
            'perfect_scores': 1,     # Perfect score
            'current_streak': 3,     # 3-day streak
            'badges': []
        }

        new_badges = gamification_service.check_badge_eligibility(user_stats)

        # Should detect multiple achievements
        badge_ids = [b['badge_id'] for b in new_badges]
        assert 'first_submission' in badge_ids, "Should detect first submission"
        assert 'perfect_score' in badge_ids, "Should detect perfect score"
        assert 'streak_3' in badge_ids, "Should detect 3-day streak"

        # Verify total points from all badges
        total_badge_points = sum(b['config']['points'] for b in new_badges)
        assert total_badge_points > 0, "Should have total points from all badges"

    def test_achievement_workflow_with_notification_mock(self, client, test_db, test_user):
        """Test achievement workflow with notification mocking"""
        with patch('services.email_service.send_achievement_notification') as mock_notify:
            mock_notify.return_value = True

            # Award points and badges
            result = gamification_service.award_points_and_badges(
                user_id=str(test_user['_id']),
                action='submission',
                metadata={'score': 100, 'perfect_score': True}
            )

            # Verify result contains notification data
            assert 'new_badges' in result
            assert 'points_earned' in result
            assert 'total_points' in result

            # In a real system, notification would be called here
            # We verify the data is available for notification
            if len(result['new_badges']) > 0:
                badge = result['new_badges'][0]
                assert 'badge_id' in badge
                assert 'config' in badge
                assert 'earned_at' in badge

    def test_achievement_workflow_edge_case_no_achievements(self, client, test_db, test_user):
        """Test achievement workflow when no achievements are earned"""
        # User has already earned all possible badges for their stats
        user_stats = {
            'total_submissions': 1,
            'badges': ['first_submission']  # Already has the only badge they qualify for
        }

        new_badges = gamification_service.check_badge_eligibility(user_stats)

        # Should not award any new badges
        assert len(new_badges) == 0, "Should not award badges already earned"

    def test_achievement_workflow_streak_progression(self, client, test_db, test_user):
        """Test achievement workflow for streak progression"""
        # Test progression through streak badges
        streak_levels = [
            (3, 'streak_3', 'On Fire', 100),
            (7, 'streak_7', 'Week Warrior', 250),
            (30, 'streak_30', 'Coding Legend', 1000)
        ]

        for streak_days, badge_id, badge_name, points in streak_levels:
            user_stats = {
                'total_submissions': streak_days,
                'current_streak': streak_days,
                'badges': []
            }

            new_badges = gamification_service.check_badge_eligibility(user_stats)
            streak_badge = next(
                (b for b in new_badges if b['badge_id'] == badge_id),
                None
            )

            assert streak_badge is not None, f"Should detect {badge_name}"
            assert streak_badge['config']['name'] == badge_name
            assert streak_badge['config']['points'] == points

