import os

import jwt
import openai
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

import constants.authTokens as auth
import constants.paths as paths
import service_utils.databaseUtils as databaseUtils
from service_utils import recordingutils
from service_utils.authUtils import require_token
import os

# DONT FORGET TO REMOVE BEFORE DEPLOYING

app = Flask(__name__)
CORS(app)


openai.api_key = auth.OPENAI_TOKEN


@app.route("/session_recording", methods=["POST"])
def process_data():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if file and recordingutils.allowed_file(file.filename):
        file_path = os.path.join(os.getcwd(), "resources/client_side_recordings", file.filename)
        file.save(file_path)

        # convert the webm file to a wav file
        wav_path = os.path.splitext(file_path)[0] + ".wav"
        recordingutils.convert_webm_to_wav(file_path, wav_path)
        # remove the webm file
        os.remove(file_path)

        result = {"message": "WAV file received", "file_path": file_path}
        return jsonify(result)
    else:
        return jsonify({"error": "Invalid file format"}), 400


@app.route("/interview_registration", methods=["POST"])
def interview_request():
    account_ready = databaseUtils.create_account(data=request.get_json())
    if account_ready:
        return jsonify({"get_auth_ready": True})
    else:
        return jsonify({"get_auth_ready": False})


@app.route("/authnticate_interview", methods=["GET"])
def authnticate_interview():
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
    auth_token = jwt.encode(payload, os.environ.get("SECRET_KEY"), algorithm="HS256")
    return {"auth_token": auth_token}


# Send Get
@app.route("/generate_response", methods=["GET"])
@require_token
def get_audio_response():
    First_user_message = recordingutils.speech_to_text()
    generated_text = recordingutils.generate_text(First_user_message)
    recordingutils.text_to_speech(generated_text)
    return send_file(paths.GENERATED_SPEECH_PATH, as_attachment=True)


if __name__ == "__main__":
    app.run()
