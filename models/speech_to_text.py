import whisper
import ffmpeg
import os

class SpeechToText:
    def __init__(self, model_size='base'):
        print(f"Loading Whisper model: {model_size}")
        self.model = whisper.load_model(model_size)
    
    def transcribe(self, audio_path):
        """Convert audio/video to text using Whisper"""
        print(f"Transcribing: {audio_path}")
        
        # If video file, extract audio first
        if audio_path.lower().endswith(('.mp4', '.avi', '.mkv')):
            audio_path = self._extract_audio(audio_path)
        
        # Transcribe
        result = self.model.transcribe(audio_path)
        
        # Clean up temporary audio file
        if audio_path != audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
        
        return result['text']
    
    def _extract_audio(self, video_path):
        """Extract audio from video file"""
        audio_path = video_path.replace('.mp4', '.wav').replace('.avi', '.wav').replace('.mkv', '.wav')
        
        ffmpeg.input(video_path).output(
            audio_path, 
            acodec='pcm_s16le', 
            ac=1, 
            ar='16k'
        ).run(overwrite_output=True, quiet=True)
        
        return audio_path
    
    def transcribe_with_timestamps(self, audio_path):
        """Transcribe with word-level timestamps"""
        result = self.model.transcribe(audio_path, word_timestamps=True)
        return result