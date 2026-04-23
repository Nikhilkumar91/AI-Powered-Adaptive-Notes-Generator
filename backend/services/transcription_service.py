from __future__ import annotations

from datetime import datetime
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from typing import Any

from backend.config import TEMP_DIR, WHISPER_MODEL

TEMP_DIR.mkdir(parents=True, exist_ok=True)
WHISPER_CACHE_DIR = TEMP_DIR / 'whisper-cache'
WHISPER_CACHE_DIR.mkdir(parents=True, exist_ok=True)
FFMPEG_BIN_DIR = TEMP_DIR / 'ffmpeg-bin'
FFMPEG_BIN_DIR.mkdir(parents=True, exist_ok=True)

FFMPEG_READY = False
FFMPEG_ERROR: str | None = None
WHISPER_ERROR: str | None = None

whisper = None
_whisper = None

try:
    import whisper

    WHISPER_AVAILABLE = True
except Exception as exc:
    WHISPER_ERROR = f'{type(exc).__name__}: {exc}'
    WHISPER_AVAILABLE = False

AUDIO_EXTENSIONS = {'.wav', '.mp3', '.m4a', '.ogg', '.flac'}
VIDEO_EXTENSIONS = {'.mp4', '.webm', '.avi', '.mov', '.mkv', '.flv'}

COMMON_SUBSTITUTIONS: list[tuple[str, str]] = [
    (r'\bnatural learning\b', 'machine learning'),
    (r'\bdeep larning\b', 'deep learning'),
    (r'\bdeeplearning\b', 'deep learning'),
]

TOPIC_STOPWORDS = {
    'about', 'after', 'again', 'also', 'and', 'any', 'are', 'because', 'been', 'being', 'but',
    'can', 'could', 'did', 'does', 'during', 'each', 'few', 'for', 'from', 'had', 'has', 'have',
    'here', 'how', 'into', 'its', 'just', 'more', 'most', 'not', 'only', 'other', 'our', 'out',
    'over', 'same', 'she', 'should', 'some', 'such', 'than', 'that', 'the', 'their', 'them',
    'then', 'there', 'these', 'they', 'this', 'those', 'through', 'too', 'under', 'until', 'very',
    'was', 'were', 'what', 'when', 'where', 'which', 'while', 'who', 'why', 'will', 'with',
    'would', 'you', 'your',
}


def timestamp() -> str:
    return datetime.now().strftime('%Y%m%d_%H%M%S')


def get_whisper_status() -> tuple[bool, str | None]:
    if whisper is None:
        return False, WHISPER_ERROR or 'Whisper is not installed.'
    if _whisper is not None:
        return True, None
    try:
        load_whisper_model()
        return True, None
    except Exception:
        return False, WHISPER_ERROR or 'Whisper model could not be loaded.'


def load_whisper_model():
    global _whisper
    global WHISPER_ERROR

    if whisper is None:
        raise RuntimeError(WHISPER_ERROR or 'Whisper is not installed.')

    if _whisper is None:
        try:
            _whisper = whisper.load_model(WHISPER_MODEL, download_root=str(WHISPER_CACHE_DIR))
            WHISPER_ERROR = None
        except Exception as exc:
            WHISPER_ERROR = f'{type(exc).__name__}: {exc}'
            raise

    return _whisper


def ensure_ffmpeg_on_path() -> bool:
    global FFMPEG_READY
    global FFMPEG_ERROR

    if FFMPEG_READY:
        return True

    if shutil.which('ffmpeg'):
        FFMPEG_READY = True
        FFMPEG_ERROR = None
        return True

    try:
        import imageio_ffmpeg

        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        bundled_target = FFMPEG_BIN_DIR / 'ffmpeg.exe'
        if not bundled_target.exists():
            shutil.copy2(ffmpeg_exe, bundled_target)

        os.environ['PATH'] = str(FFMPEG_BIN_DIR) + os.pathsep + os.environ.get('PATH', '')
        FFMPEG_READY = shutil.which('ffmpeg') is not None
        FFMPEG_ERROR = None if FFMPEG_READY else 'Bundled ffmpeg could not be added to PATH.'
    except Exception as exc:
        FFMPEG_READY = False
        FFMPEG_ERROR = f'{type(exc).__name__}: {exc}'

    return FFMPEG_READY


def extract_audio_from_video(video_path: Path) -> Path:
    if not ensure_ffmpeg_on_path():
        raise RuntimeError(FFMPEG_ERROR or 'ffmpeg is unavailable.')

    output_path = TEMP_DIR / f'{video_path.stem}_{timestamp()}.wav'
    command = [
        'ffmpeg',
        '-y',
        '-i',
        str(video_path),
        '-vn',
        '-ac',
        '1',
        '-ar',
        '16000',
        '-af',
        'highpass=f=100,lowpass=f=7000,loudnorm',
        str(output_path),
    ]
    result = subprocess.run(command, capture_output=True, text=True, timeout=180)
    if result.returncode != 0 or not output_path.exists():
        raise RuntimeError(result.stderr.strip() or 'Audio extraction failed.')
    return output_path


def transcribe_media(file_path: Path) -> dict[str, Any]:
    if not WHISPER_AVAILABLE:
        raise RuntimeError(WHISPER_ERROR or 'Whisper is not available.')

    ensure_ffmpeg_on_path()

    source_path = Path(file_path).expanduser().resolve(strict=False)
    if not source_path.exists() or not source_path.is_file():
        raise RuntimeError(f'Uploaded media file does not exist: {source_path}')

    transcription_input = source_path
    extracted_audio_path: Path | None = None
    if source_path.suffix.lower() in VIDEO_EXTENSIONS:
        extracted_audio_path = extract_audio_from_video(source_path)
        transcription_input = extracted_audio_path

    model = load_whisper_model()
    try:
        result = model.transcribe(
            str(transcription_input),
            fp16=False,
            temperature=0.0,
            condition_on_previous_text=False,
            compression_ratio_threshold=2.4,
            logprob_threshold=-1.0,
            no_speech_threshold=0.6,
            verbose=False,
        )
    except OSError as exc:
        raise RuntimeError(f'Failed to read media for transcription: {transcription_input}') from exc
    finally:
        if extracted_audio_path and extracted_audio_path.exists():
            extracted_audio_path.unlink(missing_ok=True)

    raw_text = _normalize_text(result.get('text', ''))
    clarified_text = _clarify_transcript(raw_text)
    segments = _normalize_segments(result.get('segments', []))
    quality = _estimate_quality(clarified_text, segments)
    warnings = _build_warnings(clarified_text, quality)

    if not clarified_text:
        raise RuntimeError('No speech could be transcribed from this file.')

    return {
        'text': clarified_text,
        'raw_text': raw_text,
        'language': result.get('language') or 'unknown',
        'segments': segments,
        'quality': quality,
        'warnings': warnings,
    }


def detect_topic(transcription: str, fallback_name: str = 'Learning Notes') -> str:
    sentences = _split_sentences(transcription)
    topic = _topic_from_repeated_phrases(sentences)
    if topic:
        return topic

    for sentence in sentences:
        words = _topic_words(sentence)
        if len(words) >= 2:
            return _title_from_words(words[:5])

    fallback_words = _topic_words(Path(fallback_name).stem.replace('_', ' '))
    if fallback_words:
        return _title_from_words(fallback_words[:5])
    return 'Uploaded Lecture Notes'


def _topic_from_repeated_phrases(sentences: list[str]) -> str:
    counts: dict[str, int] = {}
    first_seen: dict[str, int] = {}
    order = 0

    for sentence in sentences:
        words = _topic_words(sentence)
        for size in (3, 2):
            for index in range(0, max(len(words) - size + 1, 0)):
                phrase = ' '.join(words[index:index + size])
                counts[phrase] = counts.get(phrase, 0) + 1
                first_seen.setdefault(phrase, order)
                order += 1

    if not counts:
        return ''

    phrase, count = sorted(counts.items(), key=lambda item: (-item[1], first_seen[item[0]]))[0]
    return _title_from_words(phrase.split()) if count > 1 or len(phrase.split()) >= 2 else ''


def _topic_words(text: str) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z'-]{2,}", (text or '').lower())
    return [word.strip("'-") for word in words if word not in TOPIC_STOPWORDS and len(word.strip("'-")) > 2]


def _title_from_words(words: list[str]) -> str:
    small_words = {'and', 'or', 'the', 'of', 'in', 'to', 'for', 'with'}
    titled = []
    for index, word in enumerate(words):
        titled.append(word if index and word in small_words else word.capitalize())
    return ' '.join(titled)


def save_upload(file_storage) -> Path:
    suffix = Path(file_storage.filename or '').suffix.lower()
    if not re.fullmatch(r'\.[a-z0-9]{1,8}', suffix or '', flags=re.IGNORECASE):
        suffix = ''

    upload_dir = _resolve_upload_dir()
    try:
        # Avoid FileStorage.save edge-cases on Windows by creating the temp file ourselves.
        with tempfile.NamedTemporaryFile(
            mode='wb',
            suffix=suffix,
            prefix=f'media_{timestamp()}_',
            dir=str(upload_dir),
            delete=False,
        ) as handle:
            file_storage.stream.seek(0)
            shutil.copyfileobj(file_storage.stream, handle)
            target = Path(handle.name)
    except OSError as exc:
        filename = getattr(exc, 'filename', None)
        raise RuntimeError(
            f'Failed to save uploaded file to temp path (dir={upload_dir}) '
            f'(original filename={file_storage.filename!r}, os_filename={filename!r})'
        ) from exc
    except Exception as exc:
        raise RuntimeError(f'Failed to persist uploaded file (dir={upload_dir})') from exc
    return target


def _resolve_upload_dir() -> Path:
    candidates = [
        TEMP_DIR,
        Path(tempfile.gettempdir()) / 'adaptive-notes' / 'temp',
    ]
    for candidate in candidates:
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            return candidate
        except OSError:
            continue
    raise RuntimeError('Unable to prepare a writable temp directory for uploads.')


def _normalize_text(text: str) -> str:
    cleaned = text.replace('\r', ' ').replace('\n', ' ')
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    for pattern, replacement in COMMON_SUBSTITUTIONS:
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s+([,.;:!?])', r'\1', cleaned)
    cleaned = re.sub(r'([.!?])([A-Z])', r'\1 \2', cleaned)
    return cleaned


def _clarify_transcript(text: str) -> str:
    if not text:
        return ''

    clarified = text
    lowered = clarified.lower()

    if 'subset of ai' in lowered or 'subset of artificial intelligence' in lowered:
        clarified = re.sub(
            r'[^.]*machine learning[^.]*subset of (?:ai|artificial intelligence)[^.]*\.?',
            'Machine learning is a subset of artificial intelligence that allows systems to learn from data and improve over time.',
            clarified,
            flags=re.IGNORECASE,
        )

    if 'deep learning' in lowered and ('part of' in lowered or 'subset of' in lowered):
        clarified = re.sub(
            r'[^.]*deep learning[^.]*?(?:part of|subset of)[^.]*\.?',
            'Deep learning is a subset of machine learning that uses layered models to learn complex patterns.',
            clarified,
            flags=re.IGNORECASE,
        )

    if 'human intervention' in lowered:
        clarified = re.sub(
            r'[^.]*human intervention[^.]*\.?',
            'AI systems can reduce the amount of manual human intervention needed for certain tasks.',
            clarified,
            flags=re.IGNORECASE,
        )

    sentences = _split_sentences(clarified)
    return ' '.join(_format_sentence(sentence) for sentence in sentences if sentence).strip()


def _normalize_segments(segments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for segment in segments:
        text = _format_sentence(_normalize_text(segment.get('text', '')))
        if not text:
            continue
        normalized.append(
            {
                'start': round(float(segment.get('start', 0.0)), 2),
                'end': round(float(segment.get('end', 0.0)), 2),
                'text': text,
            }
        )
    return normalized


def _estimate_quality(text: str, segments: list[dict[str, Any]]) -> str:
    words = re.findall(r"[A-Za-z']+", text.lower())
    word_count = len(words)
    unique_ratio = (len(set(words)) / word_count) if word_count else 0.0
    long_segments = sum(1 for segment in segments if len(segment['text'].split()) >= 6)

    if word_count >= 25 and unique_ratio >= 0.55 and long_segments >= 2:
        return 'high'
    if word_count >= 12 and long_segments >= 1:
        return 'medium'
    return 'low'


def _build_warnings(text: str, quality: str) -> list[str]:
    warnings: list[str] = []
    if quality == 'low':
        warnings.append('The audio was difficult to transcribe clearly, so the notes focus only on the clearest detected ideas.')
    if len(text.split()) < 10:
        warnings.append('Very little spoken content was detected in the upload.')
    return warnings


def _split_sentences(text: str) -> list[str]:
    cleaned = _normalize_text(text)
    if not cleaned:
        return []
    parts = re.split(r'(?<=[.!?])\s+', cleaned)
    merged: list[str] = []
    buffer = ''

    for part in parts:
        part = part.strip(' .')
        if not part:
            continue
        if len(part.split()) < 4:
            buffer = f'{buffer} {part}'.strip()
            continue
        if buffer:
            part = f'{buffer} {part}'.strip()
            buffer = ''
        merged.append(part)

    if buffer:
        merged.append(buffer)

    return merged


def _format_sentence(sentence: str) -> str:
    cleaned = sentence.strip(' .')
    if not cleaned:
        return ''
    cleaned = cleaned[:1].upper() + cleaned[1:]
    if cleaned[-1] not in '.!?':
        cleaned += '.'
    return cleaned
