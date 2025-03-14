import json
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

# File path for aligned lyrics JSON
ALIGNED_LYRICS_PATH = r"C:\Users\ozdep\Documents\suno 1002\suno-api\suno-api\saved_songs\d07e0180-cd91-4467-99d1-5a579253a053_aligned_lyrics.json"

def load_lyrics(file_path):
    """Load aligned lyrics JSON and extract section timestamps."""
    with open(file_path, "r") as f:
        data = json.load(f)
    
    timestamps = {"verse": [], "chorus": [], "bridge": []}

    for entry in data:
        word = entry["word"].strip().lower()
        start_time = entry["start_s"]

        if "[verse]" in word:
            timestamps["verse"].append(start_time)
        elif "[chorus]" in word:
            timestamps["chorus"].append(start_time)
        elif "[bridge]" in word:
            timestamps["bridge"].append(start_time)

    return timestamps

def analyze_music(audio_path, output_file="music_analysis.json"):
    """Analyzes beats, time signature, and extracts section timestamps."""
    # Load audio file
    y, sr = librosa.load(audio_path, sr=None)
    
    # Beat detection
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    # Compute beat intervals
    beat_intervals = np.diff(beat_times)

    # Create a histogram of beat intervals
    plt.figure(figsize=(8, 5))
    plt.hist(beat_intervals, bins=30, alpha=0.7, color="blue")
    plt.xlabel("Beat Interval (seconds)")
    plt.ylabel("Frequency")
    plt.title("Histogram of Beat Intervals")
    plt.grid(True)
    plt.savefig("beat_histogram.png")  # Save histogram
    plt.show()

    # Detect time signature
    beat_counts = Counter(np.round(beat_intervals, 2))
    most_common_interval = beat_counts.most_common(1)[0][0]

    time_signature = "Unknown"
    if most_common_interval < 0.3:
        time_signature = "2/4 or faster"
    elif most_common_interval < 0.6:
        time_signature = "4/4"
    elif most_common_interval < 0.8:
        time_signature = "3/4 or 6/8"

    # Load section timestamps
    section_timestamps = load_lyrics(ALIGNED_LYRICS_PATH)

    # Save results
    analysis = {
        "tempo": tempo,
        "beat_times": beat_times.tolist(),
        "time_signature": time_signature,
        "section_timestamps": section_timestamps
    }

    with open(output_file, "w") as f:
        json.dump(analysis, f)

    print(f"Analysis saved to {output_file}")
    print(f"Detected Time Signature: {time_signature}")

if __name__ == "__main__":
    audio_file = r"C:\Users\ozdep\Documents\suno 1002\suno-api\suno-api\saved_songs\Purrfect Day.mp3" # Update with actual file
    analyze_music(audio_file)
