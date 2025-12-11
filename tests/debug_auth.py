
import pytest
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

def test_debug_token_generation(app, auth_headers):
    """Debug token generation and validation"""
    with app.app_context():
        # Verify secret key
        print(f"DEBUG: JWT_SECRET_KEY = {app.config.get('JWT_SECRET_KEY')}")

        # Decode token manually to check
        token = auth_headers['Authorization'].split(' ')[1]
        print(f"DEBUG: Generated Token = {token}")

        from flask_jwt_extended import decode_token
        try:
            decoded = decode_token(token)
            print(f"DEBUG: Decoded Token = {decoded}")
        except Exception as e:
            print(f"DEBUG: Token Decode Error = {e}")

def test_debug_endpoint_response(client, auth_headers):
    """Hit a protected endpoint and print response"""
    response = client.get('/api/gamification/achievements', headers=auth_headers)
    print(f"DEBUG: Status Code = {response.status_code}")
    print(f"DEBUG: Response Body = {response.get_data(as_text=True)}")
    assert response.status_code == 200
