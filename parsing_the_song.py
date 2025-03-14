import librosa
import librosa.display
import numpy as np
import json
import time
import matplotlib.pyplot as plt

# Load the audio file and analyze beats
def analyze_beats(audio_path):
    y, sr = librosa.load(audio_path, sr=None)  # Load audio
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, trim=False)  # Detect beats
    beat_times = librosa.frames_to_time(beats, sr=sr)  # Convert beats to time
    return tempo, beat_times

# Plot histogram of beat intervals
def plot_beat_histogram(beat_times):
    if len(beat_times) < 2:
        print("Not enough beats detected to plot a histogram.")
        return
    
    beat_intervals = np.diff(beat_times)  # Time differences between consecutive beats
    
    plt.figure(figsize=(8, 5))
    plt.hist(beat_intervals, bins=25, alpha=0.75, color='b', edgecolor='black')
    plt.xlabel("Time Between Beats (s)")
    plt.ylabel("Frequency")
    plt.title("Beat Interval Distribution (Rhythm Pattern)")
    plt.grid(True)
    plt.show()

# Retrieve lyric timestamps from JSON file
def load_lyric_timestamps(json_path):
    with open(json_path, "r", encoding="utf-8") as file:
        lyrics_data = json.load(file)
    return [(entry["word"], entry["start_s"]) for entry in lyrics_data if entry["success"]]

# Define dance moves (Placeholder actions)
MOVES = {
    "verse": "SMALL_STEP",  
    "chorus": "BIG_JUMP",   
    "bridge": "LOOK_AROUND"
}

# Assign moves based on beats and lyrics
def assign_moves(beat_times, lyric_timestamps):
    dance_sequence = []
    beat_index = 0  # Track the beats

    for word, lyric_time in lyric_timestamps:
        move_type = "verse" if "verse" in word.lower() else "chorus" if "chorus" in word.lower() else "bridge"
        move = MOVES.get(move_type, "SMALL_STEP")
        
        while beat_index < len(beat_times) and beat_times[beat_index] < lyric_time:
            beat_index += 1

        if beat_index < len(beat_times):
            movement_time = beat_times[beat_index]  # Place move at the next beat
            dance_sequence.append({"time": movement_time, "word": word, "move": move})

    return dance_sequence

# Execute moves in sync with the song
def execute_dance(dance_sequence):
    start_time = time.time()
    
    for step in dance_sequence:
        wait_time = step["time"] - (time.time() - start_time)
        if wait_time > 0:
            time.sleep(wait_time)  # Syncs to song timing
        
        print(f"Executing move: {step['move']} at {step['time']}s for word '{step['word']}'")

# Main execution
if __name__ == "__main__":
    audio_path = r"C:\Users\ozdep\Documents\suno 1002\suno-api\suno-api\saved_songs\Purrfect Day.mp3"  # Change this to the actual path of your song
    json_path = r"C:\Users\ozdep\Documents\suno 1002\suno-api\suno-api\saved_songs\d07e0180-cd91-4467-99d1-5a579253a053_aligned_lyrics.json"
    
    tempo, beat_times = analyze_beats(audio_path)
    lyric_timestamps = load_lyric_timestamps(json_path)
    
    print(f"Detected tempo: {tempo} BPM")
    
    # Plot the beat histogram
    plot_beat_histogram(beat_times)
    
    dance_sequence = assign_moves(beat_times, lyric_timestamps)
    
    print("Starting dance execution...")
    execute_dance(dance_sequence)