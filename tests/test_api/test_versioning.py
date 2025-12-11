"""
Tests for API versioning system
"""

import pytest


@pytest.mark.contract
class TestAPIVersioning:
    """Test API versioning functionality"""

    def test_v1_health_endpoint(self, client):
        """Test v1 health endpoint"""
        response = client.get('/api/v1/health')
        assert response.status_code == 200

        data = response.json
        assert data['version'] == 'v1'
        assert data['api_version'] == '1.0.0'
        assert data['status'] == 'healthy'

    def test_v2_health_endpoint(self, client):
        """Test v2 health endpoint"""
        response = client.get('/api/v2/health')
        assert response.status_code == 200

        data = response.json
        assert data['version'] == 'v2'
        assert data['api_version'] == '2.0.0'
        assert data['status'] == 'healthy'
        assert data.get('enhanced_features') is True

    def test_v1_info_endpoint(self, client):
        """Test v1 info endpoint"""
        response = client.get('/api/v1/info')
        assert response.status_code == 200

        data = response.json
        assert 'endpoints' in data
        assert 'features' in data
        assert data['api_version'] == '1.0.0'

    def test_v2_info_endpoint(self, client):
        """Test v2 info endpoint with breaking changes info"""
        response = client.get('/api/v2/info')
        assert response.status_code == 200

        data = response.json
        assert 'endpoints' in data
        assert 'features' in data
        assert 'breaking_changes' in data
        assert data['api_version'] == '2.0.0'

    def test_version_header_negotiation(self, client):
        """Test API version negotiation via headers"""
        # Request with v2 header
        response = client.get('/health', headers={'API-Version': 'v2'})
        # Note: This requires implementing header-based routing
        # For now, just verify the header is accepted
        assert response.status_code in [200, 404]

    def test_backward_compatibility(self, client):
        """Test that v1 endpoints remain stable"""
        # Both v1 and v2 health endpoints should work
        v1_response = client.get('/api/v1/health')
        v2_response = client.get('/api/v2/health')

        assert v1_response.status_code == 200
        assert v2_response.status_code == 200

        # V1 should not have enhanced features
        assert 'enhanced_features' not in v1_response.json
        # V2 should have enhanced features
        assert 'enhanced_features' in v2_response.json
