from pyannote.audio import Pipeline
import torch

def detect_speakers(audio_path: str, transcript: list) -> list:
    """Detect speakers in audio (simplified version)"""
    
    try:
        # Initialize speaker diarization pipeline
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.0",
            use_auth_token="hf_token_here"  # Get free token from huggingface.co
        )
        
        if torch.cuda.is_available():
            pipeline.to(torch.device("cuda"))
        
        diarization = pipeline(audio_path)
        
        speakers = {}
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            if speaker not in speakers:
                speakers[speaker] = {
                    "name": f"Speaker {len(speakers) + 1}",
                    "duration": 0,
                    "segments": 0,
                    "sample_text": ""
                }
            
            speakers[speaker]["duration"] += int(turn.end - turn.start)
            speakers[speaker]["segments"] += 1
        
        # Add transcript samples
        for i, speaker_data in enumerate(speakers.values(), 1):
            for chunk in transcript[:3]:
                if speaker_data["sample_text"] == "":
                    speaker_data["sample_text"] = chunk.get("text", "")
        
        return list(speakers.values())
    
    except Exception as e:
        # Fallback: simple speaker detection
        return [
            {
                "name": "Speaker 1",
                "duration": "Unknown",
                "segments": "Unknown",
                "sample_text": transcript[0].get("text", "") if transcript else ""
            }
        ]