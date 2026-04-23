# 🔧 Testing & Troubleshooting Guide

## How to Test the App

### Step 1: Open the Application
1. Browser should already show: `http://127.0.0.1:5000`
2. Look for the **mode indicator** at the top showing:
   - ✅ **Real Whisper AI** (if whisper installed) 
   - ⚠️ **Demo Mode** (if whisper not installed)

### Step 2: Upload a Test File
1. Click **"Or upload an audio/video file"** box
2. Select one of these files from the `uploads/` folder:
   - `test.mp4` (video file)
   - `test1.mp4` (video file)  
   - `Python in 2 Minutes!.mp4` (video file)
   - Or any MP3/WAV file you have

3. Click **"Transcribe Audio"** button

### Step 3: Monitor the Console (F12)
While file is processing, open browser console (F12 → Console tab) and you'll see:
```
Starting transcription for: test.mp4
Sending file to server...
Server response: {success: true, transcription: "...", filename: "test.mp4"}
Transcription successful. Topic: [extracted topic]
Transcription length: [number of characters]
Generating notes with: {topic: "...", level: "intermediate", transcriptionLength: [number]}
Notes response: {success: true, notes: {...}, message: "..."}
Notes generated successfully: {...}
```

## Debugging Information

### Check Backend Logs (Terminal)
The terminal where you ran `python app.py` will show:
```
📨 Received transcribe request
📋 Files received: ['audio']
📁 File: test.mp4
💾 Saving to: static/temp/media_20260418_...mp4
✅ File saved, size: 12345 bytes
🎤 Transcribing: test.mp4
✅ Transcription done: 456 chars
```

### If No Output Appears

**Problem**: "Nothing is happening" or "Blank screen"
- **Solution**: 
  1. Open browser console (F12 → Console tab)
  2. Click "Upload" again
  3. Look for error messages
  4. Share the console errors from "Client Error:" or "Fetch error:"

**Problem**: "File uploaded but no transcription"
- **Check**:
  1. Is the file actually being saved? Check terminal logs
  2. Does `static/temp/` folder exist and is writable?
  3. Check terminal for "File saved" message
  4. Look for any errors starting with ❌

**Problem**: "Notes not generating despite transcription"
- **Check**:
  1. Transcription shows in browser ✓
  2. Level selector is set (Beginner/Intermediate/Advanced) ✓
  3. Open console (F12) and look for "generateNotes" start message
  4. Check API endpoint response in console under "Notes response:"

## Required Directories

Make sure these folders exist in project root:
```bash
mkdir -p static/temp
mkdir -p uploads
mkdir -p outputs/pdf
mkdir -p outputs/docx
```

Or create a batch file to auto-create them:
```batch
@echo off
if not exist "static\temp" mkdir static\temp
if not exist "uploads" mkdir uploads
if not exist "outputs\pdf" mkdir outputs\pdf
if not exist "outputs\docx" mkdir outputs\docx
echo ✅ Directories ready
```

## API Endpoints (Manual Testing)

### Test Transcribe Endpoint
```powershell
$file = Get-Item "uploads/test.mp4"
$response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/transcribe-audio" `
  -Method POST -Form @{audio=$file}
$response.Content | ConvertFrom-Json | Format-List
```

**Expected Response**:
```json
{
  "success": true,
  "transcription": "Today we'll learn about Python programming...",
  "filename": "test.mp4",
  "message": "File transcribed successfully"
}
```

### Test Notes Generation Endpoint  
```powershell
$body = @{
    topic = "Python Programming"
    transcription = "Today we'll learn about Python programming. Python is a high-level language..."
    level = "intermediate"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/generate-notes" `
  -Method POST -Headers @{"Content-Type"="application/json"} -Body $body
$response.Content | ConvertFrom-Json | Select-Object success, message
```

### Test Health Endpoint
```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:5000/health" | Select-Object -ExpandProperty Content
```

**Expected Response**:
```json
{
  "status": "healthy",
  "whisper_available": false,
  "timestamp": "2026-04-18T13:36:50.568486"
}
```

## File System Checks

### Verify Files are Being Saved
In PowerShell:
```powershell
# Check if temp files created and cleaned up
Get-ChildItem static/temp/

# Check generated files
Get-ChildItem outputs/pdf/
Get-ChildItem outputs/docx/

# Check uploads
Get-ChildItem uploads/
```

## Common Issues & Solutions

### ❌ "OSError: [WinError 10038] An operation was attempted on something that is not a socket"
- **Cause**: Flask debug reloader issue on Windows
- **Fix**: Already applied (`use_reloader=False`)
- **Action**: Restart app with `python app.py`

### ❌ "FFmpeg not found" (for video files)
- **Cause**: FFmpeg not installed
- **Fix**: Download from https://ffmpeg.org/download.html
- **Workaround**: Use audio files (MP3, WAV) instead of video

### ❌ "'whisper_model' is not defined"
- **Cause**: Whisper import error
- **Fix**: App falls back to demo mode automatically
- **Note**: This is expected if `pip install openai-whisper` hasn't been run

### ❌ Notes section doesn't appear
- **Debug Steps**:
  1. Check browser console (F12 → Console)
  2. Look for "displayNotes" errors
  3. Verify `notesSection` div exists in HTML
  4. Check if `currentNotes` variable is set

### ❌ Export buttons don't work
- **Check**:
  1. Do `outputs/pdf` and `outputs/docx` folders exist?
  2. Are they writable?
  3. Check terminal for export errors
  4. Verify reportlab and python-docx are installed: `pip list | grep -E "reportlab|docx"`

## Enabling Real Whisper AI

Once you have this working, upgrade to real transcription:

```bash
# Install OpenAI Whisper
pip install openai-whisper

# Install FFmpeg (needed for audio extraction from video)
# Windows: Download from https://ffmpeg.org/download.html and add to PATH

# Restart the app
python app.py

# The app should now show "Real Whisper AI" in mode indicator
```

## Performance Tips

- **Large files (>100MB)**: Might take time. Be patient and check terminal logs
- **Video to audio**: Uses FFmpeg. Slower for long videos (normal, takes ~30 seconds per minute of video)
- **Real Whisper**: Much slower than demo but accurate (base model: ~1-2 seconds per minute of audio)

## Getting Real Help

If still having issues, share:
1. **Terminal output**: Copy from `python app.py` terminal
2. **Browser console errors**: F12 → Console → Copy errors
3. **File being uploaded**: What's the filename and size?
4. **Steps you took**: Exactly what buttons did you click?

---

**Status Check Commands**:
```bash
# Check if app is running
Invoke-WebRequest http://127.0.0.1:5000/

# Check Python packages
pip list | grep -E "Flask|whisper|reportlab|docx"

# Check file directory
Get-ChildItem static/temp/
```
