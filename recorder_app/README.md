# CaptureCloud — Screen Recorder

## Stack
- Frontend: React, Vite, Tailwind CSS, Lucide icons
- Backend: FastAPI, Python, SQLite
- Browser capture: getDisplayMedia + MediaRecorder + Canvas captureStream
- Storage: server-side local disk (`backend/storage`) and SQLite metadata (not a third-party cloud bucket yet)

## Run locally
### 1) Backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
### 2) Frontend (new terminal)
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173

## Demo login
- username: `admin`
- password: `ChangeMe123!`

**Change this demo credential and implement proper user administration, password hashing (bcrypt/Argon2), token expiry, HTTPS, and authorization before company production use.** This starter stores videos on the backend server disk, which acts as the app's server-side library; it is not a deployed cloud storage bucket. For persistent cloud storage in production, connect S3-compatible storage (AWS S3, Cloudflare R2, MinIO, etc.).

## Notes
- Browser permissions are required; recording works on localhost or HTTPS.
- The quality selector scales the captured video through a canvas and uses the selected bitrate preset at recorder start.
- Adaptive toggle is included in the interface, but true automatic bitrate renegotiation during an active MediaRecorder session is not implemented in this starter.
- Audio is included when the browser's screen-share dialog offers audio and the user selects it.
