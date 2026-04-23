from __future__ import annotations

from html import escape
from pathlib import Path
import os
import traceback

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_file, send_from_directory
from flask_cors import CORS
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv('env')

from backend.config import (
    CORS_ORIGINS,
    DOCX_DIR,
    FRONTEND_DIR,
    MAX_CONTENT_LENGTH,
    MONGODB_DB,
    MONGODB_URI,
    PDF_DIR,
    PORT,
    SECRET_KEY,
)
from backend.services.note_service import generate_diagrams, generate_notes, generate_quiz
from backend.services.storage_service import MongoRepository
from backend.services.transcription_service import (
    WHISPER_AVAILABLE,
    detect_topic,
    get_whisper_status,
    save_upload,
    transcribe_media,
)
from backend.utils.exporters import create_docx, create_pdf

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path='')
app.config['SECRET_KEY'] = SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
CORS(app, resources={r'/api/*': {'origins': CORS_ORIGINS}})

repository = MongoRepository(MONGODB_URI, MONGODB_DB)
PDF_DIR.mkdir(parents=True, exist_ok=True)
DOCX_DIR.mkdir(parents=True, exist_ok=True)

serializer = URLSafeTimedSerializer(SECRET_KEY, salt='adaptive-notes-auth')
APP_BUILD_MARKER = 'transcribe-diagnostics-v1'


@app.errorhandler(Exception)
def handle_exception(error):
    if request.path.startswith('/api/') or request.path == '/health':
        return jsonify({'success': False, 'error': str(error), 'trace': traceback.format_exc(limit=3)}), 500
    raise error


@app.get('/')
def serve_frontend():
    return send_from_directory(FRONTEND_DIR, 'index.html')


@app.get('/login')
@app.get('/dashboard')
def serve_app_page():
    return send_from_directory(FRONTEND_DIR, 'index.html')


@app.get('/assets/<path:filename>')
def serve_assets(filename: str):
    return send_from_directory(FRONTEND_DIR / 'assets', filename)


@app.get('/favicon.ico')
def favicon():
    return ('', 204)


@app.get('/health')
def health():
    whisper_ready, whisper_error = get_whisper_status()
    return jsonify(
        {
            'build': APP_BUILD_MARKER,
            'status': 'healthy',
            'whisper_available': whisper_ready,
            'whisper_imported': WHISPER_AVAILABLE,
            'whisper_error': whisper_error,
            'mongodb_connected': repository.is_connected,
            'mongodb_error': repository.error,
        }
    )


@app.post('/api/auth/login')
def login_endpoint():
    if not repository.is_connected:
        return jsonify({'success': False, 'error': 'Database is not connected.'}), 503

    payload = request.get_json(force=True, silent=True) or {}
    email = str(payload.get('email') or '').strip().lower()
    password = str(payload.get('password') or '')

    if not email:
        return jsonify({'success': False, 'error': 'Email is required.'}), 400
    if not password:
        return jsonify({'success': False, 'error': 'Password is required.'}), 400

    user = repository.find_user_by_email(email)
    if not user:
        return jsonify({'success': False, 'error': 'Invalid email or password.'}), 401

    password_hash = user.get('password_hash') or ''
    if not password_hash or not check_password_hash(password_hash, password):
        return jsonify({'success': False, 'error': 'Invalid email or password.'}), 401

    token = serializer.dumps({'sub': user['id'], 'email': user['email']})
    return jsonify({'success': True, 'token': token, 'token_type': 'bearer', 'user': {'email': user['email'], 'name': user.get('name')}})


@app.post('/api/auth/register')
def register_endpoint():
    if not repository.is_connected:
        return jsonify({'success': False, 'error': 'Database is not connected.'}), 503

    payload = request.get_json(force=True, silent=True) or {}
    name = str(payload.get('name') or '').strip()
    email = str(payload.get('email') or '').strip().lower()
    password = str(payload.get('password') or '')

    if not email:
        return jsonify({'success': False, 'error': 'Email is required.'}), 400
    if '@' not in email or '.' not in email.split('@')[-1]:
        return jsonify({'success': False, 'error': 'Enter a valid email address.'}), 400
    if not password:
        return jsonify({'success': False, 'error': 'Password is required.'}), 400

    password_hash = generate_password_hash(password)
    user_id = repository.create_user({'name': name or None, 'email': email, 'password_hash': password_hash})
    if not user_id:
        return jsonify({'success': False, 'error': 'Account already exists for this email.'}), 409

    token = serializer.dumps({'sub': user_id, 'email': email})
    return jsonify({'success': True, 'token': token, 'token_type': 'bearer', 'user': {'email': email, 'name': name}})


@app.post('/api/transcribe-audio')
def transcribe_audio_endpoint():
    file = request.files.get('audio') or request.files.get('file') or request.files.get('video')
    if file is None or not file.filename:
        return jsonify({'success': False, 'error': 'No audio or video file provided.'}), 400
    temp_path: Path | None = None
    try:
        try:
            temp_path = save_upload(file)
        except Exception as exc:
            errno = getattr(exc, 'errno', None)
            filename = getattr(exc, 'filename', None)
            return (
                jsonify(
                    {
                        'success': False,
                        'error': f'Upload save failed: {type(exc).__name__}: {exc}',
                        'build': APP_BUILD_MARKER,
                        'diagnostics': {
                            'stage': 'save_upload',
                            'errno': errno,
                            'os_filename': str(filename) if filename else None,
                            'incoming_filename': file.filename,
                            'content_type': file.content_type,
                            'content_length': request.content_length,
                        },
                    }
                ),
                500,
            )
        try:
            transcription_result = transcribe_media(temp_path)
        except OSError as exc:
            raise RuntimeError(f'Unable to process uploaded media file: {temp_path}') from exc
        transcription = transcription_result['text']
        topic = detect_topic(transcription, Path(file.filename).stem)
        return jsonify(
            {
                'success': True,
                'filename': file.filename,
                'topic': topic,
                'transcription': transcription,
                'raw_transcription': transcription_result.get('raw_text', transcription),
                'language': transcription_result.get('language', 'unknown'),
                'transcription_quality': transcription_result.get('quality', 'unknown'),
                'warnings': transcription_result.get('warnings', []),
                'message': 'Transcription completed successfully.',
            }
        )
    finally:
        if temp_path and temp_path.exists():
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass


@app.post('/api/generate-notes')
def generate_notes_endpoint():
    data = request.get_json(force=True)
    topic = data.get('topic') or 'Learning Notes'
    transcription = data.get('transcription', '')
    level = data.get('level', 'intermediate')
    notes = generate_notes(topic, transcription, level)
    diagrams = generate_diagrams(topic, transcription, level)
    quiz = generate_quiz(topic, transcription, level)
    session_id = repository.create_session(
        {
            'topic': topic,
            'level': level,
            'transcription': transcription,
            'notes': notes,
            'diagrams': diagrams,
            'quiz': quiz,
            'source_filename': data.get('filename', ''),
        }
    )
    return jsonify(
        {
            'success': True,
            'session_id': session_id,
            'notes': notes,
            'diagrams': diagrams,
            'quiz': quiz,
            'mongodb_connected': repository.is_connected,
            'message': 'Notes generated successfully.',
        }
    )


@app.post('/api/export-pdf')
def export_pdf_endpoint():
    data = request.get_json(force=True)
    notes = data.get('notes', {})
    topic = notes.get('topic') or data.get('topic') or 'Learning Notes'
    file_path = create_pdf(topic, notes, data.get('level', notes.get('level', 'intermediate')))
    export_data = {
        'type': 'PDF',
        'filename': file_path.name,
        'download_url': f'/api/download/pdf/{file_path.name}',
        'created_at': file_path.stat().st_mtime,
    }
    session_id = data.get('session_id')
    if session_id:
        repository.attach_export(session_id, export_data)
    return jsonify({'success': True, 'filename': file_path.name, 'download_url': export_data['download_url']})


@app.post('/api/export-docx')
def export_docx_endpoint():
    data = request.get_json(force=True)
    notes = data.get('notes', {})
    topic = notes.get('topic') or data.get('topic') or 'Learning Notes'
    file_path = create_docx(topic, notes, data.get('level', notes.get('level', 'intermediate')))
    export_data = {
        'type': 'DOCX',
        'filename': file_path.name,
        'download_url': f'/api/download/docx/{file_path.name}',
        'created_at': file_path.stat().st_mtime,
    }
    session_id = data.get('session_id')
    if session_id:
        repository.attach_export(session_id, export_data)
    return jsonify({'success': True, 'filename': file_path.name, 'download_url': export_data['download_url']})


@app.post('/api/preview-notes')
def preview_notes_endpoint():
    data = request.get_json(force=True)
    notes = data.get('notes', {})
    topic = escape(notes.get('topic', 'Learning Notes'))
    introduction = escape(notes.get('introduction', ''))
    summary = escape(notes.get('summary', ''))
    highlights = ''.join(f'<li>{escape(str(item))}</li>' for item in notes.get('highlights', []))
    structure = ''.join(f'<li>{escape(str(item))}</li>' for item in notes.get('structure', []))
    html = f"""
    <article style='font-family: Segoe UI, sans-serif; line-height: 1.7;'>
      <h1>{topic}</h1>
      <h2>Introduction</h2>
      <p>{introduction}</p>
      <h2>Key Highlights</h2>
      <ul>{highlights}</ul>
      <h2>Learning Structure</h2>
      <ol>{structure}</ol>
      <h2>Summary</h2>
      <p>{summary}</p>
    </article>
    """
    return jsonify({'success': True, 'html': html})


@app.get('/api/history')
def history_endpoint():
    return jsonify({'success': True, 'items': repository.list_history(), 'mongodb_connected': repository.is_connected})


@app.delete('/api/history/<session_id>')
def delete_history_item(session_id: str):
    deleted = repository.delete_session(session_id)
    if not deleted:
        return jsonify({'success': False, 'error': 'History item not found.'}), 404
    return jsonify({'success': True, 'message': 'History item cleared successfully.'})


@app.get('/api/download/pdf/<path:filename>')
def download_pdf(filename: str):
    return send_file(PDF_DIR / filename, as_attachment=True, download_name=filename)


@app.get('/api/download/docx/<path:filename>')
def download_docx(filename: str):
    return send_file(DOCX_DIR / filename, as_attachment=True, download_name=filename)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=PORT, debug=True)
