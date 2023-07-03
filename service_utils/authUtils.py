from functools import wraps
from flask import request, jsonify
import constants.authTokens as auth

def _validate_token(token):
    VALID_TOKENS = [auth.API_ACCESS_TOKEN] 
    # Check if the provided token exists in the dictionary
    if token in VALID_TOKENS:
        return True
    return False

def require_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Check if the 'Authorization' header is present
        if 'Authorization' not in request.headers:
            return jsonify({'error': 'Authorization required'}), 401

        # Get the token from the 'Authorization' header
        token = request.headers['Authorization']

        # Validate the token (you can implement your own validation logic)
        valid_token = _validate_token(token)
        if not valid_token:
            return jsonify({'error': 'Invalid token'}), 401

        # If the token is valid, proceed with the decorated function
        return f(*args, **kwargs)

    return decorated