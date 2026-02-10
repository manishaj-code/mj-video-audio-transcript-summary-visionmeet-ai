import subprocess
import os
import shutil # New import to find FFmpeg automatically
from pathlib import Path

def extract_audio_from_video(video_path: str) -> str:
    audio_path = f"temp_audio_{Path(video_path).stem}.wav"
    
    # SMART CHECK: 
    # 1. Look for 'ffmpeg' in the system PATH (works for Cloud/Linux)
    # 2. If not found, look for our local 'ffmpeg.exe' (works for Windows)
    ffmpeg_path = shutil.which("ffmpeg") 
    
    if not ffmpeg_path:
        # Fallback to local exe for Windows development
        local_exe = os.path.join(os.getcwd(), "ffmpeg.exe")
        if os.path.exists(local_exe):
            ffmpeg_path = local_exe
        else:
            raise Exception("FFmpeg not found! On Cloud, ensure packages.txt has 'ffmpeg'. On Windows, ensure ffmpeg.exe is in the folder.")

    try:
        command = [
            ffmpeg_path,
            "-i", video_path,
            "-ar", "16000",
            "-ac", "1",
            "-c:a", "pcm_s16le",
            "-y",
            audio_path
        ]
        
        subprocess.run(command, capture_output=True, check=True, text=True)
        return audio_path
    
    except subprocess.CalledProcessError as e:
        raise Exception(f"FFmpeg Error: {e.stderr}")