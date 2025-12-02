# Speech Recognition Project

This project implements real-time speech recognition using Wav2Vec 2.0 with FastAPI backend and React frontend.

## Prerequisites

1. Python 3.10 or higher
2. Node.js and npm
3. FFmpeg (for audio processing)

## Setup

1. Install FFmpeg:
   - Download FFmpeg from https://www.gyan.dev/ffmpeg/builds/
   - Extract to C:\ffmpeg
   - Add C:\ffmpeg\bin to your system PATH

2. Set up the project:
   - Run `setup.ps1` in PowerShell
   OR
   - Manual setup:
     ```powershell
     # Backend setup
     cd backend
     python -m venv mlstateofartenv
     .\mlstateofartenv\Scripts\Activate.ps1
     pip install -r requirements.txt

     # Frontend setup
     cd ../frontend
     npm install
     ```

## Running the Project

1. Start the backend:
   ```powershell
   cd backend
   .\mlstateofartenv\Scripts\Activate.ps1
   python -m uvicorn app.main:app --reload
   ```

2. Start the frontend (in a new terminal):
   ```powershell
   cd frontend
   npm run dev
   ```

3. Open http://localhost:5173 in your browser

## Troubleshooting

1. WebSocket Connection Issues:
   - Ensure backend is running on http://localhost:8000
   - Check browser console for connection errors
   - Verify CORS settings in backend

2. Audio Processing Issues:
   - Verify FFmpeg is installed and in PATH
   - Check audio input permissions in browser
   - Try different audio input devices

3. Model Loading Issues:
   - Ensure enough RAM is available (at least 4GB free)
   - Check internet connection for model download
   - Try clearing the model cache

## Testing

1. Basic API Test:
   ```powershell
   curl http://localhost:8000/health
   ```

2. Audio File Test:
   ```powershell
   curl -F "file=@test.wav" http://localhost:8000/transcribe
   ```