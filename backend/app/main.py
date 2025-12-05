from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import logging
from pydub import AudioSegment
from app.transcribe import transcribe_audio_path  # your transcription function

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="Speech Recognition API")

# CORS 
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# helper: convert audio to wav
def convert_to_wav(file_path: str) -> str:
    try:
        # Try to find ffmpeg in PATH first
        audio = AudioSegment.from_file(file_path)
    except (OSError, FileNotFoundError):
        # If that fails, try common ffmpeg locations
        ffmpeg_paths = [
            r"C:\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
            r"ffmpeg" 
        ]
        ffprobe_paths = [
            r"C:\ffmpeg\bin\ffprobe.exe",
            r"C:\Program Files\ffmpeg\bin\ffprobe.exe",
            r"ffprobe" 
        ]
        
        success = False
        for ffmpeg, ffprobe in zip(ffmpeg_paths, ffprobe_paths):
            try:
                AudioSegment.converter = ffmpeg
                AudioSegment.ffprobe = ffprobe
                audio = AudioSegment.from_file(file_path)
                success = True
                break
            except:
                continue
                
        if not success:
            raise FileNotFoundError("Could not find ffmpeg. Please install it and add it to PATH")

    wav_path = os.path.splitext(file_path)[0] + ".wav"
    audio.export(wav_path, format="wav")
    return wav_path

# REST endpoint
@app.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...), 
    model: str = "wav2vec2-base",  # default to fastest model
    lang: str = "en"
):
    """Transcribe uploaded audio file"""
    logger.info(f"Transcribing file: {file.filename} using model: {model}")
    
    tmp_path = None
    tmp_path_wav = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        tmp_path_wav = convert_to_wav(tmp_path)
        text = transcribe_audio_path(tmp_path_wav, model_name=model)
        
        return {
            "text": text,
            "model": model,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error transcribing file: {str(e)}")
        return {
            "error": str(e),
            "status": "error"
        }
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
        if tmp_path_wav and os.path.exists(tmp_path_wav):
            os.remove(tmp_path_wav)

# Add health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# WebSocket endpoint for streaming
@app.websocket("/ws/stream/")
async def websocket_stream(ws: WebSocket):
    await ws.accept()
    buffer = bytearray()
    full_audio_chunks = []
    CHUNK_THRESHOLD = 1600  # bytes
    try:
        while True:
            event = await ws.receive()
            # binary chunk
            if "bytes" in event and event["bytes"]:
                chunk = event["bytes"]
                buffer.extend(chunk)
                full_audio_chunks.append(chunk)

                if len(buffer) >= CHUNK_THRESHOLD:
                    # write temp file for small chunk
                    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".webm")
                    tmp_file.write(buffer)
                    tmp_file.close()
                    wav_file = convert_to_wav(tmp_file.name)

                    # transcribe small chunk (~1-2 sec)
                    partial_text = transcribe_audio_path(wav_file, chunk_size=2)
                    await ws.send_json({"text": partial_text})

                    # cleanup
                    buffer = bytearray()
                    os.remove(tmp_file.name)
                    os.remove(wav_file)

            # text commands
            elif "text" in event and event["text"]:
                if event["text"] == "FLUSH":
                    # save full recording
                    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".webm")
                    for c in full_audio_chunks:
                        tmp_file.write(c)
                    tmp_file.close()
                    wav_file = convert_to_wav(tmp_file.name)

                    full_text = transcribe_audio_path(wav_file, chunk_size=5)
                    await ws.send_json({"text": full_text, "final": True})

                    # cleanup
                    os.remove(tmp_file.name)
                    os.remove(wav_file)
                    full_audio_chunks = []
                    buffer = bytearray()

    except WebSocketDisconnect:
        pass
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected; final buffer size: %d", len(buffer))
        if buffer:
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".webm")
            wav_file = None
            try:
                tmp_file.write(buffer)
                tmp_file.close()

                wav_file = convert_to_wav(tmp_file.name)
                final_text = transcribe_audio_path(wav_file)
                logger.info(f"Final transcription result: {final_text[:200]}")
                # Can't send over closed websocket; log instead
                logger.info(f"Would have sent final transcription over WS: {final_text[:200]}")
            except Exception as e:
                logger.error(f"Error processing final websocket buffer: {e}")
            finally:
                if tmp_file and os.path.exists(tmp_file.name):
                    os.remove(tmp_file.name)
                if wav_file and os.path.exists(wav_file):
                    os.remove(wav_file)
    