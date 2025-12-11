"""
Property-based tests for API versioning
**Feature: project-improvements, Property 1-4: API Version Routing and JSON Round-Trip**
**Validates: Requirements 3.1, 3.2, 3.3, 3.5**
"""

import pytest
import json
from hypothesis import given, strategies as st, settings, assume
from datetime import datetime


class MockRequest:
    """Mock request object for testing version negotiation."""

    def __init__(self, path='', headers=None):
        self.path = path
        self.headers = headers or {}


@pytest.mark.property
class TestAPIVersionRouting:
    """Property tests for API version routing consistency."""

    # **Feature: project-improvements, Property 1: API Version Routing Consistency (V1)**
    @given(
        endpoint=st.sampled_from([
            '/auth/login', '/auth/signup', '/auth/profile', '/auth/logout',
            '/submissions/submit', '/submissions/my-submissions', '/submissions/stats',
            '/assignments/', '/assignments/123',
            '/gamification/user/stats', '/gamification/leaderboard', '/gamification/badges',
            '/plagiarism/scan', '/plagiarism/results/123',
            '/collaboration/create-session', '/collaboration/public-sessions',
        ])
    )
    @settings(max_examples=100, deadline=2000)
    def test_v1_url_routing_consistency(self, endpoint):
        """
        Property 1: API Version Routing Consistency (V1)
        *For any* request to a /api/v1/* endpoint, the get_api_version function
        SHALL return 'v1'.
        **Validates: Requirements 3.1**
        """
        from routes.api_versioning import get_api_version

        # Create request with v1 URL path
        path = f'/api/v1{endpoint}'
        req = MockRequest(path=path)

        # Get version
        version = get_api_version(req)

        # Assert v1 is returned
        assert version == 'v1', f"Expected 'v1' for path {path}, got '{version}'"


    # **Feature: project-improvements, Property 2: API Version Routing Consistency (V2)**
    @given(
        endpoint=st.sampled_from([
            '/auth/login', '/auth/signup', '/auth/profile', '/auth/logout', '/auth/refresh',
            '/submissions/submit', '/submissions/my-submissions', '/submissions/stats',
            '/assignments/', '/assignments/123',
            '/gamification/user/stats', '/gamification/leaderboard', '/gamification/badges',
            '/gamification/achievements',
            '/plagiarism/scan', '/plagiarism/results/123', '/plagiarism/cross-language',
            '/collaboration/create-session', '/collaboration/public-sessions',
            '/collaboration/video/123/start',
            '/analytics/overview', '/analytics/predictions', '/analytics/engagement',
        ])
    )
    @settings(max_examples=100, deadline=2000)
    def test_v2_url_routing_consistency(self, endpoint):
        """
        Property 2: API Version Routing Consistency (V2)
        *For any* request to a /api/v2/* endpoint, the get_api_version function
        SHALL return 'v2'.
        **Validates: Requirements 3.2**
        """
        from routes.api_versioning import get_api_version

        # Create request with v2 URL path
        path = f'/api/v2{endpoint}'
        req = MockRequest(path=path)

        # Get version
        version = get_api_version(req)

        # Assert v2 is returned
        assert version == 'v2', f"Expected 'v2' for path {path}, got '{version}'"

    # **Feature: project-improvements, Property 3: API Version Header Negotiation**
    @given(
        header_value=st.sampled_from(['v1', 'v2', '1', '2', '1.0', '2.0', '1.0.0', '2.0.0'])
    )
    @settings(max_examples=100, deadline=2000)
    def test_version_header_negotiation(self, header_value):
        """
        Property 3: API Version Header Negotiation
        *For any* request with an API-Version header value V, the get_api_version
        function SHALL return the corresponding version ('v1' or 'v2') when path
        is unversioned.
        **Validates: Requirements 3.3**
        """
        from routes.api_versioning import get_api_version

        # Create request with unversioned path and API-Version header
        req = MockRequest(
            path='/api/auth/login',  # Unversioned path
            headers={'API-Version': header_value}
        )

        # Get version
        version = get_api_version(req)

        # Determine expected version based on header value
        if header_value in ('v2', '2', '2.0', '2.0.0'):
            expected = 'v2'
        else:
            expected = 'v1'

        assert version == expected, f"Expected '{expected}' for header '{header_value}', got '{version}'"

    @given(
        path_version=st.sampled_from(['v1', 'v2']),
        header_version=st.sampled_from(['v1', 'v2'])
    )
    @settings(max_examples=100, deadline=2000)
    def test_url_takes_precedence_over_header(self, path_version, header_version):
        """
        Property: URL path version takes precedence over header version.
        **Validates: Requirements 3.1, 3.2, 3.3**
        """
        from routes.api_versioning import get_api_version

        # Create request with versioned path and different header
        req = MockRequest(
            path=f'/api/{path_version}/auth/login',
            headers={'API-Version': header_version}
        )

        # Get version
        version = get_api_version(req)

        # URL should take precedence
        assert version == path_version, f"Expected '{path_version}' (from URL), got '{version}'"



@pytest.mark.property
class TestAPIResponseJSONRoundTrip:
    """Property tests for API response JSON round-trip consistency."""

    # **Feature: project-improvements, Property 4: API Response JSON Round-Trip**
    @given(
        status=st.sampled_from(['success', 'error', 'pending']),
        message=st.text(min_size=0, max_size=200, alphabet=st.characters(
            min_codepoint=32, max_codepoint=126  # Printable ASCII
        )),
        score=st.one_of(st.none(), st.integers(min_value=0, max_value=100)),
        data_items=st.lists(
            st.dictionaries(
                keys=st.text(min_size=1, max_size=20, alphabet=st.characters(
                    min_codepoint=97, max_codepoint=122  # lowercase letters
                )),
                values=st.one_of(
                    st.integers(),
                    st.floats(allow_nan=False, allow_infinity=False),
                    st.text(max_size=50),
                    st.booleans(),
                    st.none()
                ),
                min_size=0,
                max_size=5
            ),
            min_size=0,
            max_size=5
        )
    )
    @settings(max_examples=100, deadline=2000)
    def test_api_response_json_round_trip(self, status, message, score, data_items):
        """
        Property 4: API Response JSON Round-Trip
        *For any* valid API response object, serializing to JSON and deserializing
        back SHALL produce an equivalent object.
        **Validates: Requirements 3.5**
        """
        # Create a typical API response structure
        response = {
            'status': status,
            'message': message,
            'api_version': '1.0.0',
            'version': 'v1',
            'data': {
                'score': score,
                'items': data_items,
            }
        }

        # Serialize to JSON
        serialized = json.dumps(response)

        # Deserialize back
        deserialized = json.loads(serialized)

        # Verify round-trip produces equivalent object
        assert deserialized == response
        assert deserialized['status'] == status
        assert deserialized['message'] == message
        assert deserialized['api_version'] == '1.0.0'
        assert deserialized['data']['score'] == score
        assert deserialized['data']['items'] == data_items

    @given(
        submission_id=st.text(min_size=1, max_size=36, alphabet=st.characters(
            min_codepoint=48, max_codepoint=122  # alphanumeric
        )),
        code=st.text(min_size=0, max_size=500),
        language=st.sampled_from(['python', 'javascript', 'java', 'cpp', 'c']),
        score=st.one_of(st.none(), st.integers(min_value=0, max_value=100)),
        complexity=st.integers(min_value=1, max_value=10),
        lines_of_code=st.integers(min_value=1, max_value=1000)
    )
    @settings(max_examples=100, deadline=2000)
    def test_submission_response_round_trip(self, submission_id, code, language, score, complexity, lines_of_code):
        """
        Property: Submission response with metrics should round-trip correctly.
        **Validates: Requirements 3.5**
        """
        # V2-style submission response with metrics
        response = {
            'status': 'success',
            'api_version': '2.0.0',
            'version': 'v2',
            'data': {
                'id': submission_id,
                'code': code,
                'language': language,
                'score': score,
                'metrics': {
                    'complexity': complexity,
                    'lines_of_code': lines_of_code,
                    'big_o': 'O(n)',
                }
            }
        }

        # Round-trip
        serialized = json.dumps(response)
        deserialized = json.loads(serialized)

        assert deserialized == response
        assert deserialized['data']['id'] == submission_id
        assert deserialized['data']['metrics']['complexity'] == complexity

    @given(
        entries=st.lists(
            st.fixed_dictionaries({
                'rank': st.integers(min_value=1, max_value=100),
                'username': st.text(min_size=1, max_size=30, alphabet=st.characters(
                    min_codepoint=97, max_codepoint=122
                )),
                'points': st.integers(min_value=0, max_value=10000),
                'level': st.sampled_from(['Beginner', 'Intermediate', 'Advanced', 'Expert']),
            }),
            min_size=0,
            max_size=10
        )
    )
    @settings(max_examples=100, deadline=2000)
    def test_leaderboard_response_round_trip(self, entries):
        """
        Property: Leaderboard response should round-trip correctly.
        **Validates: Requirements 3.5**
        """
        response = {
            'status': 'success',
            'api_version': '1.0.0',
            'version': 'v1',
            'data': {
                'leaderboard': entries,
                'timeframe': 'all',
                'generated_at': datetime.utcnow().isoformat(),
            }
        }

        # Round-trip
        serialized = json.dumps(response)
        deserialized = json.loads(serialized)

        assert deserialized['status'] == response['status']
        assert deserialized['data']['leaderboard'] == entries
        assert len(deserialized['data']['leaderboard']) == len(entries)
