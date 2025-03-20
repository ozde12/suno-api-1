import json
import librosa
import numpy as np
from collections import Counter

ALIGNED_LYRICS_PATH = r"C:\Users\ozdep\Documents\suno 1002\suno-api\suno-api\saved_songs\d07e0180-cd91-4467-99d1-5a579253a053_aligned_lyrics.json"

def load_lyrics(file_path):
    """Load aligned lyrics JSON and extract section start and end timestamps."""
    with open(file_path, "r") as f:
        data = json.load(f)

    section_boundaries = {}
    current_section = None

    for entry in data:
        word = entry["word"].strip().lower()
        start_time = entry["start_s"]
        end_time = entry["end_s"]

        # Detect section headers and store their start and end times
        if "[verse" in word:
            current_section = "verse"
        elif "[chorus" in word:
            current_section = "chorus"
        elif "[bridge" in word:
            current_section = "bridge"
        elif "intro_or_outro" in word:
            current_section = "intro_or_outro"

        if current_section:
            if current_section not in section_boundaries:
                section_boundaries[current_section] = {"start": start_time, "end": end_time}
            else:
                section_boundaries[current_section]["end"] = max(section_boundaries[current_section]["end"], end_time)

    return section_boundaries

def analyze_music(audio_path):
    """Analyzes beats, extracts tempo, and aligns movements to lyrics sections."""
    y, sr = librosa.load(audio_path, sr=None)

    # Beat detection
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr).tolist()

    if not beat_times:
        print("Warning: No beats detected, using default spacing.")
        beat_times = np.linspace(0, librosa.get_duration(y=y, sr=sr), num=100).tolist()

    # Compute average beat duration
    beat_intervals = np.diff(beat_times)
    avg_beat_duration = np.mean(beat_intervals) if len(beat_intervals) > 0 else 0.5  # Default fallback

    # Load lyrics timestamps
    section_boundaries = load_lyrics(ALIGNED_LYRICS_PATH)

    # Assign each beat to a section
    movement_schedule = {"verse": [], "chorus": [], "bridge": [], "intro_or_outro": []}
    
    for beat in beat_times:
        assigned = False
        for section, times in section_boundaries.items():
            if times["start"] <= beat <= times["end"]:
                movement_schedule[section].append(beat)
                assigned = True
                break
        
        # If no section found, place in a fallback category (e.g., intro or outro)
        if not assigned:
            movement_schedule.setdefault("intro_or_outro", []).append(beat)

    return {
        "tempo": tempo,
        "beat_times": beat_times,
        "time_signature": "4/4",
        "movement_schedule": movement_schedule
    }

if __name__ == "__main__":
    audio_file = r"C:\Users\ozdep\Documents\suno 1002\suno-api\suno-api\saved_songs\Purrfect Day.mp3"
    results = analyze_music(audio_file)
    print(json.dumps(results, indent=4))

    with open("music_analysis.json", "w") as f:
        json.dump(results, f, indent=4)
