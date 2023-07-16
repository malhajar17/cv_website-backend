import logging
import os

import openai
import whisper
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

import constants.authTokens as auth
import constants.paths as paths
import service_utils.authUtils as auth
import service_utils.databaseUtils as databaseUtils
import service_utils.sessionEndUtils as sessionEndUtils
from service_utils import recordingUtils
from service_utils.authUtils import require_token

app = Flask(__name__)
CORS(app)
model = None
logging.basicConfig(level=logging.DEBUG)

@app.route('/warmup-model', methods=['GET'])
@require_token
def warmup_model():

    model = whisper.load_model(os.environ.get("WHISPER_MODEL"))
    file_path = os.path.join(os.getcwd(), "resources/client_side_recordings", "silence.wav")
    whisper.transcribe(model, file_path)
    return jsonify({"status": "Whisper model warmed up"})

@app.route("/session_recording", methods=["POST"])
def process_data():
    print(request.args.get("accountID"))
    if "file" not in request.files:
         return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if file and recordingUtils.allowed_file(file.filename):
        # Recieve the account info
        accountid = request.args.get("accountID")
        sessionID = request.args.get("sessionID")
        sequence = request.args.get("sequence")

        file_path = os.path.join(os.getcwd(), "resources/client_side_recordings", file.filename)
        print(f'Saving file to: {file_path}')

        try:
            file.save(file_path)
        except Exception as e:
            print(f'Error saving file: {e}')
            raise e

        wav_path = "re_"+ accountid+"_"+sessionID+"_" + sequence + ".wav"
        wav_path_full = os.path.join(os.getcwd(), "resources/client_side_recordings", wav_path)
        print(f'Converting webm to wav: {wav_path_full}')
        try:
            recordingUtils.convert_webm_to_wav(file_path, wav_path_full)
        except Exception as e:
            print(f'Error converting webm to wav: {e}')
            raise e
        # remove the webm file
        os.remove(file_path)
        directory = os.path.join(os.getcwd(), "resources/client_side_recordings")

        files_in_directory = os.listdir(directory)
        print(files_in_directory)

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

        response = jsonify({"get_auth_ready": True,"session_id":session_id,"account_id":account_id})
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
    accountid = request.args.get("accountID")
    sessionID = request.args.get("sessionID")
    sequence = request.args.get("sequence")
    path = accountid+"_"+sessionID+"_" + sequence

    openai.api_key = os.environ.get("OPENAI_TOKEN")
    First_user_message = recordingUtils.speech_to_text(path,accountid,sessionID,sequence)
    generated_text = recordingUtils.generate_text(First_user_message,accountid=accountid,sessionID=sessionID,sequence=sequence)
    recordingUtils.text_to_speech(generated_text,path)
    return send_file(paths.GENERATED_SPEECH_PATH + "gs_"+path+".wav", as_attachment=True)

@app.route('/end_interview', methods=['POST'])
@require_token
def end_interview():
    session_id = request.args.get('sessionID')
    review = request.args.get('review')

    recordings_path = os.path.join(os.getcwd(), "resources/client_side_recordings")
    gs_urls, re_urls = sessionEndUtils.upload_recordings_and_get_urls(recordings_path)

    UserRecordingsInfoToBeInserted = sessionEndUtils.extract_info_from_links(re_urls)
    databaseUtils.create_recording_entries(UserRecordingsInfoToBeInserted)
    
    generatedRecordingsInfoToBeInserted =  sessionEndUtils.extract_info_from_links(gs_urls)
    databaseUtils.create_ttsrecording_entries(generatedRecordingsInfoToBeInserted)
    databaseUtils.create_review(session_id=session_id,review=review)
    databaseUtils.update_session_end_time(session_id)

    return jsonify({'End': True}), 200

if __name__ == "__main__":
    app.run()
