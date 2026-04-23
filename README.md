# Adaptive Notes Studio

Adaptive Notes Studio is a Flask web app that turns uploaded audio or video into study notes.

It transcribes the uploaded file with local Whisper, detects the topic from the actual transcript, generates level-based notes, creates quiz and diagram ideas, and exports the result as PDF or DOCX.

Recent updates:

- stronger transcript cleanup (spelling/grammar normalization + duplicate sentence removal)
- topic-consistency filtering to reduce mixed-topic outputs
- per-upload quiz signatures and question IDs to prevent stale quiz reuse
- Python topic handling improved so Python lectures are not incorrectly forced to ML

## Important Note About AI APIs

This project does not use any external AI API such as OpenAI API, Gemini API, Claude API, or other cloud LLM APIs.

It uses:

- `openai-whisper` as a local Python package for speech-to-text
- custom Python logic for topic detection, notes, quiz, and diagram generation

Whisper may download its model file the first time it runs, but after that the speech transcription runs locally.

## What The App Does

1. User uploads an audio or video file.
2. Flask receives the file.
3. Whisper converts speech into text.
4. The app extracts the topic from the transcript.
5. The app generates notes based on the selected level.
6. The browser shows the transcript, topic, summary, highlights, learning structure, diagrams, and quiz.
7. The user can preview the notes.
8. The user can export PDF or DOCX.
9. MongoDB stores history if MongoDB is running.
10. Users can create an account and log in (stored in MongoDB).

## Dynamic Topic And Notes Generation

The app now generates content from the uploaded file transcript.

It does not keep manual Python notes in the code and does not force every upload into the same topic.

For each uploaded file, the app now:

- extracts repeated and important words from the transcript
- builds a topic title from the transcript
- selects evidence sentences from the uploaded file
- creates highlights from real transcript lines
- builds a learning structure from detected concepts
- creates quiz options from the same transcript
- uses the final generated topic in preview, PDF, and DOCX export

If the audio content is different, the topic and notes should also be different.

## Project Structure

```text
Sanchula Siva Jyothi/
|-- app.py
|-- env
|-- requirements.txt
|-- START.bat
|-- README.md
|
|-- backend/
|   |-- app.py
|   |-- config.py
|   |-- services/
|   |   |-- transcription_service.py
|   |   |-- note_service.py
|   |   `-- storage_service.py
|   `-- utils/
|       `-- exporters.py
|
|-- frontend/
|   |-- index.html
|   `-- assets/
|       |-- app.js
|       `-- styles.css
|
|-- outputs/
|   |-- pdf/
|   `-- docx/
|
|-- static/
|   `-- temp/
|       |-- whisper-cache/
|       `-- ffmpeg-bin/
|
|-- uploads/
|-- generated/
|-- templates/
|-- models/
`-- database/
```

## Main Files

`app.py`  
Local entry point. Run this file to start the app.

`backend/app.py`  
Main Flask server. Contains routes for upload, transcription, notes generation, preview, export, downloads, and history.

`backend/config.py`  
Loads paths and settings such as port, MongoDB URI, output folders, temp folder, and Whisper model name.

`backend/services/transcription_service.py`  
Handles uploaded media, local Whisper transcription, ffmpeg setup, transcript cleanup, quality warnings, and transcript-based topic detection.

`backend/services/note_service.py`  
Creates dynamic notes from transcript content. This is where topic, highlights, structure, summary, diagrams, and quiz are generated.

`backend/services/storage_service.py`  
Connects to MongoDB and stores generated sessions and export history.

`backend/utils/exporters.py`  
Creates PDF and DOCX files from the generated notes.

`frontend/index.html`  
Main browser page.

`frontend/assets/app.js`  
Handles upload, API calls, rendering notes, preview, export, quiz, health checks, and history.

`frontend/assets/styles.css`  
Controls the UI design and layout.

## Requirements

Install dependencies from:

```text
requirements.txt
```

Main dependencies:

- `Flask`: backend web server
- `Flask-CORS`: API CORS support
- `python-dotenv`: reads the `env` file
- `pymongo`: MongoDB history
- `reportlab`: PDF export
- `python-docx`: DOCX export
- `openai-whisper`: local speech-to-text
- `imageio-ffmpeg`: bundled ffmpeg helper

## Configuration

The app reads settings from the root `env` file.

Example:

```env
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=adaptive_notes
SESSION_SECRET=change_this_to_a_long_random_string
PORT=4000
CLIENT_ORIGIN=*
WHISPER_MODEL=base
MAX_CONTENT_LENGTH=524288000
```

Important values:

- `PORT`: local Flask port
- `MONGODB_URI` (or `MONGO_URI`): MongoDB connection string
- `MONGODB_DB`: MongoDB database name
- `SESSION_SECRET`: Flask secret key
- `CLIENT_ORIGIN`: allowed frontend origin
- `WHISPER_MODEL`: Whisper model name, usually `base`
- `MAX_CONTENT_LENGTH`: max upload size in bytes

### Authentication (MongoDB required)

Login + registration use MongoDB (`users` collection). If MongoDB is not running, auth endpoints return `503`.

## Installation

Open PowerShell in the project folder:

```powershell
cd "C:\Users\nikhi\Downloads\my_fin_pro\Sanchula Siva Jyothi"
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Or use the Windows starter:

```powershell
.\START.bat
```

`START.bat` checks Python, prepares the virtual environment, installs dependencies if needed, creates output folders, and starts the app.

## Run The App

```powershell
python app.py
```

Open:

```text
http://127.0.0.1:4000
```

If your `env` file uses another port, open that port instead.

## User Workflow

1. Start the Flask server.
2. Open the app in the browser.
3. Select `Beginner`, `Intermediate`, or `Advanced`.
4. Upload an audio or video file.
5. Click `Transcribe and Generate Notes`.
6. Review the detected topic and transcript.
7. Review generated notes, diagrams, and quiz.
8. Click `Preview` to view notes in the browser.
9. Click `Export PDF` or `Export DOCX`.
10. Check history if MongoDB is connected.

## API Endpoints

```text
GET    /
GET    /health
POST   /api/auth/register
POST   /api/auth/login
POST   /api/transcribe-audio
POST   /api/generate-notes
POST   /api/preview-notes
POST   /api/export-pdf
POST   /api/export-docx
GET    /api/history
DELETE /api/history/<session_id>
GET    /api/download/pdf/<filename>
GET    /api/download/docx/<filename>
```

## Output Folders

PDF files:

```text
outputs/pdf/
```

DOCX files:

```text
outputs/docx/
```

Temporary media, ffmpeg, and Whisper cache:

```text
By default the app now uses:

```text
%LOCALAPPDATA%/Temp/adaptive-notes/temp/
```

You can override with:

```text
APP_TEMP_DIR
```

## Troubleshooting

### Topic still looks old, repeated, or mixed

Hard refresh the browser:

```text
Ctrl + Shift + R
```

If it still happens, restart Flask:

```powershell
python app.py
```

Also verify `/health` returns the latest build marker and that you are not running an old Python process.

### Quiz looks reused across uploads

The backend now attaches:

- `quiz_signature` (derived from topic + difficulty + transcript)
- `id` per question

Two different transcript uploads should produce different `quiz_signature` values.

If signatures are identical, check that the frontend is sending different transcription text to `/api/generate-notes`.

### Notes do not match the expected file name

The app uses the audio transcript, not the file name. For example, a file named `harvard.wav` may contain the Harvard sentence audio:

```text
The stale smell of old beer lingers...
```

In that case, the generated topic will be based on those spoken words, not the file name.

### Whisper is not ready

Check that dependencies are installed:

```powershell
pip install -r requirements.txt
```

The first Whisper run may need internet access to download the model.

### MongoDB is not connected

Make sure MongoDB is running and `MONGO_URI` is correct in `env`.

The app can still generate notes without MongoDB, but history will not be saved.

### PDF or DOCX export fails

Check:

- notes were generated first
- `outputs/pdf/` and `outputs/docx/` exist
- dependencies are installed
- the Flask server is still running

## Current Core Flow

```text
frontend/index.html
  ↓
frontend/assets/app.js
  ↓
backend/app.py
  ↓
backend/services/transcription_service.py
  ↓
backend/services/note_service.py
  ↓
backend/services/storage_service.py
  ↓
backend/utils/exporters.py
```

In one line:

```text
Upload file -> transcribe speech -> detect transcript topic -> generate notes -> preview/export -> save history
```
