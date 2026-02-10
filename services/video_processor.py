import subprocess
import os
import shutil
from pathlib import Path

def extract_audio_from_video(video_path: str) -> str:
    audio_path = f"temp_audio_{Path(video_path).stem}.wav"
    
    # 🔍 SYSTEM SEARCH:
    # 1. Check common Linux path first (Streamlit Cloud)
    # 2. Check system PATH
    # 3. Check local folder (Windows)
    if os.path.exists("/usr/bin/ffmpeg"):
        ffmpeg_bin = "/usr/bin/ffmpeg"
    else:
        ffmpeg_bin = shutil.which("ffmpeg") or os.path.join(os.getcwd(), "ffmpeg.exe")

    if not ffmpeg_bin or not (os.path.exists(ffmpeg_bin) or shutil.which(ffmpeg_bin)):
         raise Exception("FFmpeg not found! Please ensure 'packages.txt' exists in root with 'ffmpeg' written inside.")

    try:
        command = [
            ffmpeg_bin, "-i", video_path,
            "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le",
            "-y", audio_path
        ]
        # Using text=True and capture_output to catch specific errors
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return audio_path
    except subprocess.CalledProcessError as e:
        raise Exception(f"FFmpeg process failed: {e.stderr}")
    except Exception as e:
        raise Exception(f"Error extracting audio: {str(e)}")