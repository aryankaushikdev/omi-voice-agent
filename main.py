from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydub import AudioSegment
import tempfile
import openai
import requests
from io import BytesIO
import os

app = FastAPI()

# ✅ Load API keys from environment variables (set these in Railway)
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

@app.get("/")
def health():
    return {"status": "ok"}

@app.get("/debug")
def debug():
    return {
        "openai_key_present": bool(OPENAI_API_KEY),
        "elevenlabs_key_present": bool(ELEVEN_API_KEY)
    }

@app.post("/audio")
async def receive_audio(request: Request):
    try:
        print("📩 Request received")
        sample_rate = int(request.query_params.get("sample_rate", 16000))
        uid = request.query_params.get("uid", "unknown")

        audio_bytes = await request.body()
        print(f"🧩 Received {len(audio_bytes)} bytes from UID: {uid}")

        # Save audio to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            audio = AudioSegment(
                data=audio_bytes,
                sample_width=2,
                frame_rate=sample_rate,
                channels=1
            )
            audio.export(temp_audio.name, format="wav")
            print(f"✅ Audio saved to: {temp_audio.name}")

            audio_file = open(temp_audio.name, "rb")
            transcript = openai.Audio.transcribe("whisper-1", audio_file)["text"]
            print(f"📝 Transcript: {transcript}")

        # Contextual reply
        response_text = query_rag(transcript)
        print(f"🤖 RAG response: {response_text}")

        # ElevenLabs TTS
        audio_response = eleven_labs_tts(response_text)
        return StreamingResponse(BytesIO(audio_response), media_type="audio/mpeg")

    except Exception as e:
        print("❌ CRITICAL ERROR:", str(e))
        return {"error": str(e)}

def query_rag(text):
    return f"In Gravesend’s fertile alluvial soil, the best course of action is: {text.lower()}. Consider legumes like beans or peas for nitrogen recovery."

def eleven_labs_tts(text):
    voice_id = "Rachel"
    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        headers={
            "xi-api-key": ELEVEN_API_KEY,
            "Content-Type": "application/json"
        },
        json={
            "text": text,
            "voice_settings": {
                "stability": 0.7,
                "similarity_boost": 0.8
            }
        }
    )
    if response.status_code != 200:
        raise Exception(f"TTS failed: {response.text}")
    return response.content
