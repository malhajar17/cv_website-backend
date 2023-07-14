import os

import openai
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

import constants.authTokens as auth
import constants.paths as paths
import service_utils.databaseUtils as databaseUtils
from models.user_session_info import UserSessionInfo
import service_utils.authUtils as auth
from service_utils import recordingUtils
from service_utils.authUtils import require_token
import os
import whisper

app = Flask(__name__)
CORS(app)
model = None

@app.route('/warmup-model', methods=['GET'])
@require_token
def warmup_model():

    model = whisper.load_model(os.environ.get("WHISPER_MODEL"))
    file_path = os.path.join(os.getcwd(), "resources/client_side_recordings", "silence.wav")
    whisper.transcribe(model, file_path)
    return jsonify({"status": "Whisper model warmed up"})

@app.route("/session_recording", methods=["POST"])
def process_data():
    user_info = UserSessionInfo.get_instance()
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if file and recordingUtils.allowed_file(file.filename):
        file_name = "recording"
        file_path = os.path.join(os.getcwd(), "resources/client_side_recordings", file.filename)
        file.save(file_path)

        # convert the webm file to a wav file
        wav_path = os.path.splitext(file_path)[0] + ".wav"
        recordingUtils.convert_webm_to_wav(file_path, wav_path)
        # remove the webm file
        os.remove(file_path)

        result = {"message": "WAV file received", "file_path": file_path}
        return jsonify(result)
    else:
        return jsonify({"error": "Invalid file format"}), 400


@app.route("/interview_registration", methods=["POST"])
def interview_request():
    try:
        user_data = request.get_json()

        account_id = databaseUtils.create_account(user_data)
        if account_id is not None:
            session_id = databaseUtils.create_session(account_id)
            print(f"Created new session with ID {session_id} for account {account_id}")

        response = jsonify({"get_auth_ready": True})
        return response, 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"get_auth_ready": False}), 500
    

@app.route("/authenticate_interview", methods=["GET"])
@require_token
def authenticate_interview():
    return auth.authenticate_interview(request)

# Send Get
@app.route("/generate_response", methods=["GET"])
@require_token
def get_audio_response():
    openai.api_key = os.environ.get("OPENAI_TOKEN")
    First_user_message = recordingUtils.speech_to_text()
    generated_text = recordingUtils.generate_text(First_user_message)
    recordingUtils.text_to_speech(generated_text)
    return send_file(paths.GENERATED_SPEECH_PATH + "gs_.wav", as_attachment=True)


if __name__ == "__main__":
    app.run()
