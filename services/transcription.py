#import whisper
from faster_whisper import WhisperModel
import os

def transcribe_audio(audio_path: str):
    """Transcribe audio using faster-whisper (free, local)"""
    
    try:
        # Use faster-whisper for speed
        model = WhisperModel("base", device="cpu", compute_type="int8")
        segments, info = model.transcribe(audio_path, language="en")
        
        transcript = []
        for segment in segments:
            transcript.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text,
                "timestamp": f"[{int(segment.start//60):02d}:{int(segment.start%60):02d}]"
            })
        
        return transcript
    
    except Exception as e:
        raise Exception(f"Transcription error: {str(e)}")