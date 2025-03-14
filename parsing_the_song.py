import librosa
import numpy as np
import json
import time
import matplotlib.pyplot as plt
from scipy.stats import mode
from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks

# Load the audio file and analyze beats
def analyze_beats(audio_path):
    y, sr = librosa.load(audio_path, sr=None)  
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, trim=False)  
    beat_times = librosa.frames_to_time(beats, sr=sr)  
    return tempo, beat_times

# Estimate the time signature
def estimate_time_signature(beat_times):
    if len(beat_times) < 4:
        return "Unknown (Not enough beats detected)"
    
    beat_intervals = np.diff(beat_times)  
    avg_interval = np.median(beat_intervals)  

    estimated_beats_per_measure = [2, 3, 4, 6]
    beat_groups = [round(1 / avg_interval * b) for b in estimated_beats_per_measure]
    
    signature = mode(beat_groups, keepdims=False)[0]

    if signature == 2:
        return "2/2 or 2/4"
    elif signature == 3:
        return "3/4"
    elif signature == 4:
        return "4/4"
    elif signature == 6:
        return "6/8"
    else:
        return "Unknown"

# Retrieve lyric timestamps from JSON file
def load_lyric_timestamps(json_path):
    with open(json_path, "r", encoding="utf-8") as file:
        lyrics_data = json.load(file)
    return [(entry["word"], entry["start_s"]) for entry in lyrics_data if entry["success"]]

# Define dance moves
MOVES = {
    "verse": "Stand/Emotions/Positive/Happy_1",  
    "chorus": "Stand/Emotions/Positive/Winner_2",   
    "bridge": "BlocklyTouchShoulders"
}

# Assign moves based on beats and lyrics
def assign_moves(beat_times, lyric_timestamps):
    dance_sequence = []
    beat_index = 0  

    for word, lyric_time in lyric_timestamps:
        move_type = "verse" if "verse" in word.lower() else "chorus" if "chorus" in word.lower() else "bridge"
        move = MOVES.get(move_type, "SMALL_STEP")
        
        while beat_index < len(beat_times) and beat_times[beat_index] < lyric_time:
            beat_index += 1

        if beat_index < len(beat_times):
            movement_time = beat_times[beat_index]  
            dance_sequence.append({"time": movement_time, "word": word, "move": move})

    return dance_sequence

# Play the song on the robot
@inlineCallbacks
def play_song_on_robot(session, audio_url):
    try:
        print("Streaming music to the robot...")
        yield session.call("rom.actuator.audio.stream", url=audio_url, sync=False)
        print("Music started successfully.")
    except Exception as e:
        print(f"Error while streaming music: {e}")

# Execute dance moves in sync with the song
@inlineCallbacks
def execute_dance(session, dance_sequence, song_start_time):
    for step in dance_sequence:
        wait_time = step["time"] - (time.time() - song_start_time)
        if wait_time > 0:
            yield sleep(wait_time)  # **Use non-blocking sleep**
        
        print(f"Executing move: {step['move']} at {step['time']}s for word '{step['word']}'")
        try:
            yield session.call("rom.optional.behavior.play", name=step['move'])
        except Exception as e:
            print(f"Error executing move: {e}")

# Main execution function
@inlineCallbacks
def main(session, details):
    audio_url = r"C:\Users\ozdep\Documents\suno 1002\suno-api\suno-api\saved_songs\Purrfect Day.mp3"  # Replace with actual song URL
    json_path = r"C:\Users\ozdep\Documents\suno 1002\suno-api\suno-api\saved_songs\d07e0180-cd91-4467-99d1-5a579253a053_aligned_lyrics.json"
    
    print("Analyzing song...")
    tempo, beat_times = analyze_beats(audio_url)  
    lyric_timestamps = load_lyric_timestamps(json_path)
    
    print(f"Detected tempo: {tempo} BPM")
    
    time_signature = estimate_time_signature(beat_times)
    print(f"Estimated Time Signature: {time_signature}")

    dance_sequence = assign_moves(beat_times, lyric_timestamps)

    print("Starting song and dance...")
    song_start_time = time.time()  # Sync start time
    
    yield play_song_on_robot(session, audio_url)  # Start playing the song

    yield execute_dance(session, dance_sequence, song_start_time)  # Start the dance moves

    print("Stopping music...")
    try:
        yield session.call("rom.actuator.audio.stop")
    except Exception as e:
        print(f"Error stopping music: {e}")

    session.leave()  # Close connection with the robot

# Setup WAMP connection for robot control
wamp = Component(
    transports=[{
        "url": "wss://wamp.robotsindeklas.nl",
        "serializers": ["msgpack"]
    }],
    realm="rie.67d401c799b259cf43b059e6",
)

wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])
