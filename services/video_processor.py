import subprocess
import os
from pathlib import Path

def extract_audio_from_video(video_path: str) -> str:
    """Extract audio from video file optimized for Whisper AI"""
    
    # 1. Create a clean output name
    audio_path = f"temp_audio_{Path(video_path).stem}.wav"
    
    # 2. Point to the ffmpeg.exe in YOUR folder
    # We use 'ffmpeg.exe' for Windows. If it's in the same folder as app.py, this works.
    ffmpeg_exe = os.path.join(os.getcwd(), "ffmpeg.exe")

    try:
        command = [
            ffmpeg_exe,        # Use the absolute path to your .exe
            "-i", video_path,
            "-ar", "16000",    # Whisper prefers 16kHz
            "-ac", "1",        # Whisper prefers Mono
            "-c:a", "pcm_s16le", # PCM 16-bit encoding (best for AI)
            "-y",              # Overwrite existing files without asking
            audio_path
        ]
        
        # We use stderr=subprocess.STDOUT to see errors if it fails
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return audio_path
    
    except FileNotFoundError:
        raise Exception(f"ffmpeg.exe not found at {ffmpeg_exe}. Please copy ffmpeg.exe into this folder.")
    except subprocess.CalledProcessError as e:
        raise Exception(f"FFmpeg Error: {e.stderr}")
    except Exception as e:
        raise Exception(f"Error extracting audio: {str(e)}")