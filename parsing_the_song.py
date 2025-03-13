import librosa
import librosa.display
import numpy as np
import json
import time

# Load the audio file and analyze beats
def analyze_beats(audio_path):
    y, sr = librosa.load(audio_path, sr=None)  # Load audio
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, trim=False)  # Detect beats
    beat_times = librosa.frames_to_time(beats, sr=sr)  # Convert beats to time
    return tempo, beat_times

# RETRIEVE THE LYRIC TIME STAMPS
# Example timestamps for each lyric line (Replace with actual lyric alignment)
LYRIC_TIMESTAMPS = {
    "verse_1": [0.0, 3.0, 6.0],
    "chorus": [9.0, 12.0, 15.0],
    "verse_2": [18.0, 21.0, 24.0],
    "bridge": [27.0, 30.0],
    "final_chorus": [33.0, 36.0, 39.0]
}

#WILL DEFINE IN THE TUTORIAL
# Define dance moves (Placeholder actions)
MOVES = {
    "verse": "SMALL_STEP",  
    "chorus": "BIG_JUMP",   
    "bridge": "LOOK_AROUND"
}

# Assign moves based on beats and lyrics
def assign_moves(beat_times):
    dance_sequence = []
    beat_index = 0  # Track the beats

    for section, times in LYRIC_TIMESTAMPS.items():
        move_type = "verse" if "verse" in section else "chorus" if "chorus" in section else "bridge"

        for lyric_time in times:
            # Find the closest beat after the lyric start time
            while beat_index < len(beat_times) and beat_times[beat_index] < lyric_time:
                beat_index += 1

            if beat_index < len(beat_times):
                movement_time = beat_times[beat_index]  # Place move at the next beat
                dance_sequence.append({"time": movement_time, "move": MOVES[move_type]})

    return dance_sequence

# USE THE CODE FROM ASSIGNMENT 2 TO REPLACE HERE
# Execute moves in sync with the song
def execute_dance(dance_sequence):
    start_time = time.time()
    
    for step in dance_sequence:
        wait_time = step["time"] - (time.time() - start_time)
        if wait_time > 0:
            time.sleep(wait_time)  # Syncs to song timing
        
        move = step["move"]
        print(f"Executing move: {move}")  # Replace with actual robot command

#CHANGE TO INCLUDE THE 
# Main execution
if __name__ == "__main__":
    audio_path = "your_song.wav"  # Change this to the actual path of your song
    tempo, beat_times = analyze_beats(audio_path)
    
    print(f"Detected tempo: {tempo} BPM")
    
    dance_sequence = assign_moves(beat_times)
    
    print("Starting dance execution...")
    execute_dance(dance_sequence)
