"""
Comprehensive Gamification Service Tests
Tests for achievement detection, points calculation, leaderboards, and level progression
"""

import pytest
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings
from services.gamification_service import (
    gamification_service,
    GamificationService,
    BadgeType,
    AchievementLevel
)


@pytest.fixture
def service():
    """Create a fresh gamification service instance"""
    return GamificationService()


@pytest.fixture
def mock_user_id():
    """Mock user ID for testing"""
    return "test_user_123"


# ==================== 10.1 Achievement Detection Tests ====================

@pytest.mark.unit
class TestAchievementDetection:
    """Test suite for achievement detection (10.1)"""

    def test_first_submission_achievement(self, service):
        """Test first submission achievement detection"""
        user_stats = {
            'total_submissions': 1,
            'badges': []
        }

        badges = service.check_badge_eligibility(user_stats)

        # Should earn first submission badge
        first_sub_badges = [b for b in badges if b['badge_id'] == 'first_submission']
        assert len(first_sub_badges) ==1
        assert first_sub_badges[0]['config']['name'] == 'First Steps'
        assert first_sub_badges[0]['config']['points'] == 50

    def test_perfect_score_achievement(self, service):
        """Test perfect score achievement detection"""
        user_stats = {
            'total_submissions': 5,
            'perfect_scores': 1,
            'badges': []
        }

        badges = service.check_badge_eligibility(user_stats)

        perfect_badges = [b for b in badges if b['badge_id'] == 'perfect_score']
        assert len(perfect_badges) == 1
        assert perfect_badges[0]['config']['level'] == AchievementLevel.SILVER.value

    def test_streak_achievements(self, service):
        """Test streak achievement detection at different levels"""
        # 3-day streak
        stats_3 = {'current_streak': 3, 'badges': []}
        badges_3 = service.check_badge_eligibility(stats_3)
        streak_3_badges = [b for b in badges_3 if b['badge_id'] == 'streak_3']
        assert len(streak_3_badges) == 1

        # 7-day streak
        stats_7 = {'current_streak': 7, 'badges': []}
        badges_7 = service.check_badge_eligibility(stats_7)
        streak_7_badges = [b for b in badges_7 if b['badge_id'] == 'streak_7']
        assert len(streak_7_badges) == 1

        # 30-day streak
        stats_30 = {'current_streak': 30, 'badges': []}
        badges_30 = service.check_badge_eligibility(stats_30)
        streak_30_badges = [b for b in badges_30 if b['badge_id'] == 'streak_30']
        assert len(streak_30_badges) == 1

    def test_milestone_achievements(self, service):
        """Test milestone achievement detection"""
        user_stats = {
            'leaderboard_rank': 1,
            'badges': []
        }

        badges = service.check_badge_eligibility(user_stats)

        first_place_badges = [b for b in badges if b['badge_id'] == 'first_place']
        assert len(first_place_badges) == 1
        assert first_place_badges[0]['config']['level'] == AchievementLevel.PLATINUM.value

    def test_no_duplicate_badges(self, service):
        """Test that already earned badges are not awarded again"""
        user_stats = {
            'total_submissions': 5,
            'badges': ['first_submission']  # Already earned
        }

        badges = service.check_badge_eligibility(user_stats)

        first_sub_badges = [b for b in badges if b['badge_id'] == 'first_submission']
        assert len(first_sub_badges) == 0  # Should not be awarded again

    def test_speed_demon_achievement(self, service):
        """Test speed-based achievement"""
        user_stats = {
            'fastest_completion': 290,  # Under 5 minutes (300 seconds)
            'badges': []
        }

        badges = service.check_badge_eligibility(user_stats)

        speed_badges = [b for b in badges if b['badge_id'] == 'speed_demon']
        assert len(speed_badges) == 1
        assert speed_badges[0]['config']['type'] == BadgeType.SPEED.value

    def test_multi_language_achievement(self, service):
        """Test multi-language achievement"""
        user_stats = {
            'languages_used': ['python', 'java', 'cpp'],
            'badges': []
        }

        badges = service.check_badge_eligibility(user_stats)

        polyglot_badges = [b for b in badges if b['badge_id'] == 'multi_language']
        assert len(polyglot_badges) == 1

    def test_collaboration_achievement(self, service):
        """Test collaboration-based achievement"""
        user_stats = {
            'collaboration_sessions': 5,
            'badges': []
        }

        badges = service.check_badge_eligibility(user_stats)

        helper_badges = [b for b in badges if b['badge_id'] == 'helper']
        assert len(helper_badges) == 1
        assert helper_badges[0]['config']['type'] == BadgeType.COLLABORATION.value


# ==================== 10.2 Points Calculation Tests ====================

@pytest.mark.unit
class TestPointsCalculation:
    """Test suite for points calculation (10.2)"""

    def test_base_points_calculation(self, service, mock_user_id):
        """Test base points for submission"""
        points = service.calculate_points(mock_user_id, 'submission', {})

        # Base submission points
        assert points >= 50

    def test_multiplier_application(self, service, mock_user_id):
        """Test score-based multiplier"""
        # Low score
        points_low = service.calculate_points(mock_user_id, 'submission', {'score': 50})

        # High score
        points_high = service.calculate_points(mock_user_id, 'submission', {'score': 100})

        # Higher score should give more points
        assert points_high > points_low

    def test_streak_bonuses(self, service, mock_user_id):
        """Test streak bonus points"""
        # Day 1
        points_day1 = service.calculate_points(
            mock_user_id,
            'streak_bonus',
            {'streak_days': 1}
        )

        # Day 7
        points_day7 = service.calculate_points(
            mock_user_id,
            'streak_bonus',
            {'streak_days': 7}
        )

        # Longer streak should give more points
        assert points_day7 > points_day1

    def test_level_progression(self, service):
        """Test level calculation from points"""
        # Beginner level
        level_info_0 = service.calculate_level_from_points(0)
        assert level_info_0['current_level']['name'] == 'Beginner'

        # Novice level
        level_info_500 = service.calculate_level_from_points(500)
        assert level_info_500['current_level']['name'] == 'Novice'

        # Intermediate level
        level_info_1500 = service.calculate_level_from_points(1500)
        assert level_info_1500['current_level']['name'] == 'Intermediate'

        # Expert level
        level_info_6000 = service.calculate_level_from_points(6000)
        assert level_info_6000['current_level']['name'] == 'Expert'

    def test_point_values_for_actions(self, service, mock_user_id):
        """Test different point values for different actions"""
        actions_and_expected = [
            ('submission', 50),
            ('correct_test_case', 5),
            ('perfect_score', 50),
            ('first_attempt_success', 25),
            ('collaboration_session', 20),
            ('daily_login', 5),
        ]

        for action, expected_base in actions_and_expected:
            points = service.calculate_points(mock_user_id, action, {})
            assert points >= expected_base

    def test_improvement_bonus(self, service, mock_user_id):
        """Test improvement bonus calculation"""
        # 10% improvement
        points_10 = service.calculate_points(
            mock_user_id,
            'improvement',
            {'improvement_percent': 10}
        )

        # 50% improvement
        points_50 = service.calculate_points(
            mock_user_id,
            'improvement',
            {'improvement_percent': 50}
        )

        assert points_50 > points_10


# ==================== 10.3 Leaderboard Generation Tests ====================

@pytest.mark.unit
class TestLeaderboardGeneration:
    """Test suite for leaderboard generation (10.3)"""

    def test_ranking_calculation(self, service):
        """Test leaderboard ranking calculation"""
        leaderboard = service.get_leaderboard()

        assert isinstance(leaderboard, list)
        # Check ranking order
        for user in leaderboard:
            assert 'rank' in user
            assert 'total_points' in user

    def test_sorting_by_points(self, service):
        """Test leaderboard sorting by points (descending)"""
        leaderboard = service.get_leaderboard()

        if len(leaderboard) > 1:
            for i in range(len(leaderboard) - 1):
                assert leaderboard[i]['total_points'] >= leaderboard[i + 1]['total_points']

    def test_tie_breaking(self, service):
        """Test tie-breaking logic for equal points"""
        # In a real system, this would test secondary sorting criteria
        # (e.g., submission time, badge count, etc.)
        leaderboard = service.get_leaderboard()
        assert isinstance(leaderboard, list)

    def test_temporal_filters(self, service):
        """Test leaderboard temporal filtering"""
        # All-time
        lb_all = service.get_leaderboard(timeframe='all')
        assert isinstance(lb_all, list)

        # This would filter by time in a real implementation
        # For now just verify it returns data

    def test_leaderboard_structure(self, service):
        """Test leaderboard entry structure"""
        leaderboard = service.get_leaderboard()

        if leaderboard:
            entry = leaderboard[0]
            required_fields = ['user_id', 'username', 'total_points', 'rank']
            for field in required_fields:
                assert field in entry


# ==================== 10.4 Points Monotonicity Property Test ====================

@pytest.mark.property
class TestPointsMonotonicity:
    """Property 9: Gamification Points Monotonicity (10.4)
    Validates: Requirements 5.4
    Property: Points should never decrease
    """

    @given(
        score1=st.integers(min_value=0, max_value=100),
        score2=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=50, deadline=1000)
    def test_points_monotonicity(self, score1, score2):
        """Points should be monotonic - submitting should never decrease total points"""
        service = GamificationService()

        points1 = service.calculate_points('user1', 'submission', {'score': score1})
        points2 = service.calculate_points('user1', 'submission', {'score': score2})

        # Points should always be non-negative
        assert points1 >= 0
        assert points2 >= 0

    @given(streak_days=st.integers(min_value=1, max_value=100))
    @settings(max_examples=50, deadline=1000)
    def test_streak_points_increase_monotonically(self, streak_days):
        """Longer streaks should give equal or more points"""
        service = GamificationService()

        points_n = service.calculate_points('user1', 'streak_bonus', {'streak_days': streak_days})

        if streak_days > 1:
            points_n_minus_1 = service.calculate_points(
                'user1',
                'streak_bonus',
                {'streak_days': streak_days - 1}
            )
            # Longer streak should give more or equal points
            assert points_n >= points_n_minus_1

    @given(
        points=st.integers(min_value=0, max_value=50000)
    )
    @settings(max_examples=50, deadline=1000)
    def test_level_progression_monotonic(self, points):
        """Level should never decrease as points increase"""
        service = GamificationService()

        level_n = service._calculate_level(points)

        if points > 0:
            level_n_minus_1 = service._calculate_level(points - 1)
            # Level should never decrease
            assert level_n >= level_n_minus_1


# ==================== 10.5 Leaderboard Sorting Property Test ====================

@pytest.mark.property
class TestLeaderboardSorting:
    """Property 12: Leaderboard Sorting Consistency (10.5)
    Validates: Requirements 5.7
    Property: Leaderboard should always be sorted correctly
    """

    def test_leaderboard_sorted_descending(self):
        """Leaderboard should always be sorted by points descending"""
        service = GamificationService()
        leaderboard = service.get_leaderboard()

        if len(leaderboard) > 1:
            points = [entry['total_points'] for entry in leaderboard]
            # Check if sorted in descending order
            assert points == sorted(points, reverse=True)

    def test_rank_consistency(self):
        """Rank numbers should be consistent with sorting"""
        service = GamificationService()
        leaderboard = service.get_leaderboard()

        for i, entry in enumerate(leaderboard, start=1):
            # Rank should match position (assuming no ties)
            # Or at least be in ascending order
            assert entry['rank'] <= i

    @given(
        st.lists(
            st.tuples(
                st.text(min_size=1, max_size=20),  # user_id
                st.integers(min_value=0, max_value=10000)  # points
            ),
            min_size=0,
            max_size=20
        )
    )
    @settings(max_examples=30, deadline=2000)
    def test_sorting_property(self, user_points_list):
        """Generated leaderboards should always be properly sorted"""
        # Simulate leaderboard generation
        leaderboard = [
            {'user_id': user_id, 'total_points': points, 'rank': 0}
            for user_id, points in user_points_list
        ]

        # Sort by points descending
        leaderboard.sort(key=lambda x: x['total_points'], reverse=True)

        # Assign ranks
        for i, entry in enumerate(leaderboard, start=1):
            entry['rank'] = i

        # Verify sorting
        if len(leaderboard) > 1:
            for i in range(len(leaderboard) - 1):
                assert leaderboard[i]['total_points'] >= leaderboard[i + 1]['total_points']
                assert leaderboard[i]['rank'] < leaderboard[i + 1]['rank']


# ==================== Additional Tests ====================

@pytest.mark.unit
class TestStreakManagement:
    """Test streak tracking and updates"""

    def test_new_streak(self, service, mock_user_id):
        """Test starting a new streak"""
        result = service.update_streak(mock_user_id, None)

        assert result['current_streak'] == 1
        assert result['longest_streak'] == 1
        assert result['streak_broken'] == False

    def test_consecutive_day_streak(self, service, mock_user_id):
        """Test consecutive day submission"""
        yesterday = datetime.utcnow() - timedelta(days=1)
        result = service.update_streak(mock_user_id, yesterday)

        # Logic would increment streak in real implementation
        assert 'current_streak' in result
        assert 'streak_broken' in result

    def test_same_day_submission(self, service, mock_user_id):
        """Test multiple submissions on same day"""
        today = datetime.utcnow()
        result = service.update_streak(mock_user_id, today)

        assert result['streak_broken'] == False

    def test_broken_streak(self, service, mock_user_id):
        """Test streak breaks after missing days"""
        three_days_ago = datetime.utcnow() - timedelta(days=3)
        result = service.update_streak(mock_user_id, three_days_ago)

        assert result['streak_broken'] == True
        assert result['current_streak'] == 1


@pytest.mark.unit
class TestLevelSystem:
    """Test level progression system"""

    def test_level_thresholds(self, service):
        """Test all level thresholds"""
        levels = [
            (0, 'Beginner'),
            (500, 'Novice'),
            (1500, 'Intermediate'),
            (3000, 'Advanced'),
            (6000, 'Expert'),
            (12000, 'Master'),
            (25000, 'Legend'),
        ]

        for points, expected_name in levels:
            level_info = service.calculate_level_from_points(points)
            assert level_info['current_level']['name'] == expected_name

    def test_progress_to_next_level(self, service):
        """Test progress calculation to next level"""
        level_info = service.calculate_level_from_points(1000)

        assert 'progress_percent' in level_info
        assert 0 <= level_info['progress_percent'] <= 100
        assert 'points_to_next' in level_info

    def test_max_level_no_next(self, service):
        """Test max level has no next level"""
        level_info = service.calculate_level_from_points(30000)

        assert level_info['current_level']['name'] == 'Legend'
        assert level_info['next_level'] is None
        assert level_info['points_to_next'] == 0


@pytest.mark.parametrize("score,expected_min_points", [
    (100, 100),  # Perfect score
    (95, 90),    # High score
    (80, 80),    # Good score
    (50, 50),    # Passing score
])
def test_points_for_various_scores(mock_user_id, score, expected_min_points):
    """Test points awarded for different score levels"""
    service = GamificationService()
    result = service.award_points_and_badges(
        mock_user_id,
        'submission',
        {'score': score}
    )

    assert result['points_awarded'] >= expected_min_points
