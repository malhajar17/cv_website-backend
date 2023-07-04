import os
from functools import wraps

import jwt
from flask import jsonify, request

import constants.authTokens as auth
from service_utils import databaseUtils


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
        if "Authorization" not in request.headers:
            return jsonify({"error": "Authorization required"}), 401

        # Get the token from the 'Authorization' header
        token = request.headers["Authorization"]

        # Validate the token (you can implement your own validation logic)
        valid_token = _validate_token(token)
        if not valid_token:
            return jsonify({"error": "Invalid token"}), 401

        # If the token is valid, proceed with the decorated function
        return f(*args, **kwargs)

    return decorated


def authenticate_interview(request):
    # Extract the required fields from the JSON data
    first_name = request.args.get("first_name")
    last_name = request.args.get("last_name")

    # Concatenate the first name and last name
    name = f"{first_name} {last_name}"
    # Check if the user is restricted
    is_restricted = databaseUtils.is_prohibited_user(first_name, last_name)
    if is_restricted:
        # User is restricted, return a specific token or value indicating the restriction
        return {"restriction_token": "RESTRICTED"}
    # Generate the payload with the name or any additional data you want to include
    payload = {"name": name}

    # Sign the token with the secret key
    auth_token = jwt.encode(payload, os.environ.get("INTERVIEW_START_SECRET_KEY"), algorithm="HS256")
    return {"auth_token": auth_token}
