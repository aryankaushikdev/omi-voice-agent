from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydub import AudioSegment
import tempfile
import openai
import requests
from io import BytesIO

app = FastAPI()

# Replace these with your actual API keys
ELEVEN_API_KEY = "your_elevenlabs_api_key"
OPENAI_API_KEY = "your_openai_api_key"
openai.api_key = OPENAI_API_KEY

@app.post("/audio")
async def receive_audio(request: Request):
    sample_rate = request.query_params.get("sample_rate", 16000)
    uid = request.query_params.get("uid", "unknown")

    audio_bytes = await request.body()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        audio = AudioSegment(
            data=audio_bytes,
            sample_width=2,
            frame_rate=int(sample_rate),
            channels=1
        )
        audio.export(temp_audio.name, format="wav")

        # Transcribe with Whisper
        audio_file = open(temp_audio.name, "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio_file)["text"]

    print(f"User ({uid}) said: {transcript}")

    # Query the RAG agent (static context for Gravesend)
    response_text = query_rag(transcript)

    # Convert response to speech using ElevenLabs
    audio_response = eleven_labs_tts(response_text)

    return StreamingResponse(BytesIO(audio_response), media_type="audio/mpeg")

def query_rag(text):
    return f"In Gravesend’s alluvial soil, the best approach would be: {text.lower()} with legumes like beans."

def eleven_labs_tts(text):
    response = requests.post(
        "https://api.elevenlabs.io/v1/text-to-speech/Rachel",
        headers={
            "xi-api-key": ELEVEN_API_KEY,
            "Content-Type": "application/json"
        },
        json={
            "text": text,
            "voice_settings": {"stability": 0.7, "similarity_boost": 0.8}
        }
    )
    return response.content
