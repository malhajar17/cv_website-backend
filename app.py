import os

import openai
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

import constants.authTokens as auth
import constants.paths as paths
from service_utils import recordingutils
from service_utils.authUtils import require_token
app = Flask(__name__)
CORS(app)


openai.api_key = auth.OPENAI_TOKEN

@app.route('/session_recording', methods=['POST'])
def process_data():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and recordingutils.allowed_file(file.filename):
        file_path =  os.path.join(os.getcwd(),"resources/client_side_recordings",file.filename)
        file.save(file_path)

        # convert the webm file to a wav file
        wav_path = os.path.splitext(file_path)[0] + '.wav'
        print(wav_path)
        recordingutils.convert_webm_to_wav(file_path, wav_path)
        # remove the webm file
        os.remove(file_path)
        
        result = {'message': 'WAV file received', 'file_path': file_path}
        return jsonify(result)
    else:
        return jsonify({'error': 'Invalid file format'}), 400

 # Send Get
@app.route('/generate_response', methods=['GET'])
@require_token
def get_audio_response():
    First_user_message = recordingutils.speech_to_text()
    generated_text = recordingutils.generate_text(First_user_message)
    recordingutils.text_to_speech(generated_text)
    return send_file(paths.GENERATED_SPEECH_PATH, as_attachment=True)

if __name__ == '__main__':
    app.run()
