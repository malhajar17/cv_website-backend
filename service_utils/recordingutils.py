import os
import azure.cognitiveservices.speech as speechsdk
import openai
import whisper
from pydub import AudioSegment
import ffmpeg

import constants.authTokens as auth
import constants.paths as paths
import constants.prompts as prompts

def _mime_to_format(mime_type):
    mime_to_format_map = {
        "audio/mp3": "mp3",
        "audio/mp4": "mp4",
        "audio/webm": "webm",
        "application/octet-stream": "mp3",  # Assuming mp3 as default for octet-stream
    }

    return mime_to_format_map.get(mime_type, "mp3")  # "mp3" as default for unknown mime types

def convert_webm_to_wav(input_path, wav_path):
    # Check if output file already exists, if so, delete it
    if os.path.exists(wav_path):
        os.remove(wav_path)
    ffmpeg.input(input_path).output(wav_path, format='wav').run()


def allowed_file(filename):
    return True



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

def speech_to_text_warmup(path):
        model = whisper.load_model(os.environ.get("WHISPER_MODEL"))
        transcription = whisper.transcribe(model, path)
        return model