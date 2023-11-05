from fastapi import HTTPException
from google.cloud import texttospeech
import requests
import struct
import json

def text_to_wav_by_google(message: str) -> bytes:
    # TTSクライアントの初期化
    client = texttospeech.TextToSpeechClient()

    # リクエストの構築
    request = texttospeech.SynthesizeSpeechRequest(
        input=texttospeech.SynthesisInput(text=message),
        voice=texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Neural2-F",
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        ),
        audio_config=texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16
        )
    )

    # TTSリクエストの実行
    response = client.synthesize_speech(request=request)
    return response.audio_content

def create_wav_header(data_length):
    # WAVヘッダーの作成
    header = bytearray()
    # RIFF header
    header.extend(struct.pack('4sI4s', b'RIFF', 36 + data_length, b'WAVE'))
    # fmt chunk
    header.extend(struct.pack('4sIHHIIHH', b'fmt ', 16, 1, 1, 16000, 16000 * 2, 2, 16))
    # data chunk
    header.extend(struct.pack('4sI', b'data', data_length))

    return header

def text_to_wav_by_elevenlabs(message):
    apiKey = "f2ee636e217e2e73357190864e947b17"

    # APIエンドポイントとヘッダーの設定
    url = "https://api.elevenlabs.io/v1/text-to-speech/zrHiDhphv9ZnVXBqCLjz?output_format=pcm_16000"
    headers = {
        "Content-Type": "application/json",
        "xi-api-key": apiKey,
        "accept": "audio/mpeg"
    }

    # リクエストのbodyの設定
    body = {
        "text": message,
        'model_id': 'eleven_monolingual_v1',
        'voice_settings': {
            'stability': 0.5,
            'similarity_boost': 0.5
        }
    }

    # APIリクエストの実行
    response = requests.post(url, headers=headers, json=body)

    pcm_data = response.content
    wav_header = create_wav_header(len(pcm_data))

    return wav_header + pcm_data

# voicevoxの場合
def text_to_wav_by_voicevox(message: str) -> bytes:
    VOICE_VOX_API_URL = "http://host.docker.internal:50021"
    speaker_id = 46

    tts_query_response = requests.post(
        f"{VOICE_VOX_API_URL}/audio_query?speaker={speaker_id}&text={message}",
        headers={'Content-Type': 'application/json'},
    )
    
    if tts_query_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch TTS query.")

    tts_query_json = tts_query_response.json()
    tts_query_json['speedScale'] = 1.16
    tts_query_json['pitchScale'] = -0.02
    tts_query_json['intonationScale'] = 1.26

    synthesis_response = requests.post(
        f"{VOICE_VOX_API_URL}/synthesis?speaker={speaker_id}&speedScale=1",
        headers={'Content-Type': 'application/json'},
        data=json.dumps(tts_query_json),
    )

    if synthesis_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch TTS synthesis result.")

    return synthesis_response.content
