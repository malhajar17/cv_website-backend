import os
import azure.cognitiveservices.speech as speechsdk
import openai
import whisper
from pydub import AudioSegment

import constants.authTokens as auth
import constants.paths as paths
import constants.prompts as prompts


def convert_webm_to_wav(webm_path, wav_path):
    try:
        audio = AudioSegment.from_file(webm_path, "mp3")
    except:
        audio = AudioSegment.from_file(webm_path, format="mp4")

    audio.export(wav_path, format="wav")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() == "mp3"


def generate_text(First_user_message, model=os.environ.get("OPEN_AI_MODULE"), temperature=0.3):
    prompt = prompts.MOHAMAD_PERSONA_PROMPT

    messages = [{"role": "system", "content": prompt}, {"role": "assistant", "content": First_user_message}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=1000,
    )
    return response.choices[0].message["content"]


def text_to_speech(text):
    # Creates an instance of a speech config with specified subscription key and service region.
    speech_key = os.environ.get("AZURE_COGNITIVE_TOKEN")
    service_region = "eastus"
    path = os.path.join(os.getcwd(), paths.GENERATED_SPEECH_PATH)

    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=False, filename=path)
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    # Note: the voice setting will not overwrite the voice element in input SSML.
    speech_config.speech_synthesis_voice_name = "en-US-DavisNeural"
    speech_config.speech_synthesis_language = "en-US"
    # use the default speaker as audio output.
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    speech_synthesizer.speak_text(text)


def speech_to_text():
    model = whisper.load_model(os.environ.get("WHISPER_MODEL"))
    path = os.path.join(os.getcwd(), paths.RECORDED_SPEECH_PATH)

    transcription = whisper.transcribe(model, path)
    return transcription["text"]
