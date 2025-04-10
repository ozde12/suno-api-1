import librosa
import json 
import time
from twisted.internet import reactor, defer
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
from alpha_mini_rug import perform_movement  # Import movement function
import logging
import os

# Define a time scaling factor
delta_t = 1500

# Define movement patterns
dance_moves = {
    "move_1": [
        {"time": 0.5 * delta_t, "data": {
            "body.head.yaw": 0.5,  
            "body.arms.right.upper.pitch": -1.0,
            "body.arms.left.upper.pitch": -1.0,
            "body.torso.yaw": 0.3,
            "body.legs.right.lower.pitch": 0.0,
            "body.legs.left.lower.pitch": 0.0,
            "body.head.roll": 0.0,
            "body.legs.left.upper.pitch":0.0,
            "body.legs.right.upper.pitch":0.0
        }},
        {"time": 1.0 * delta_t, "data": {
            "body.head.yaw": 0.0,  
            "body.arms.right.upper.pitch": 0.0,
            "body.arms.left.upper.pitch": 0.0,
            "body.torso.yaw": 0.0,
            "body.legs.right.lower.pitch": 0.0,
            "body.legs.left.lower.pitch": 0.0,
            "body.head.roll": 0.0,
            "body.legs.left.upper.pitch":0.0,
            "body.legs.right.upper.pitch":0.0
        }},
    ],
    "move_2": [
        {"time": 0.5 * delta_t, "data": {
            "body.arms.right.upper.pitch": -0.5,
            "body.arms.left.upper.pitch": 0.5,
            "body.legs.right.lower.pitch": 0.0,
            "body.legs.left.lower.pitch": 0.0,
            "body.head.yaw": 0.0,
            "body.torso.yaw": -0.3,
            "body.head.roll": 0.174,
            "body.legs.left.upper.pitch":0.0,
            "body.legs.right.upper.pitch":0.0
        }},
        {"time": 1 * delta_t, "data": {
            "body.arms.right.upper.pitch": 0.0,
            "body.arms.left.upper.pitch": 0.0,
            "body.legs.right.lower.pitch": 0.0,
            "body.legs.left.lower.pitch": 0.0,
            "body.head.yaw": 0.0,
            "body.torso.yaw": 0.0,
            "body.head.roll": -0.174,
            "body.legs.left.upper.pitch":0.0,
            "body.legs.right.upper.pitch":0.0
        }},
    ],
    "move_3": [
        {"time": 0.5 * delta_t, "data": {
            "body.arms.right.upper.pitch": -1.5,
            "body.arms.left.upper.pitch": 1.5,
            "body.legs.right.lower.pitch": 0.1,
            "body.legs.left.lower.pitch": -0.1,
            "body.torso.yaw": 0.5,
            "body.head.yaw": 0.0,
            "body.head.roll": 0.0,
            "body.legs.left.upper.pitch":0.0,
            "body.legs.right.upper.pitch":0.0
        }},
        {"time": 1 * delta_t, "data": {
            "body.arms.right.upper.pitch": 0.0,
            "body.arms.left.upper.pitch": 0.0,
            "body.legs.right.lower.pitch": 0.0,
            "body.legs.left.lower.pitch": 0.0,
            "body.torso.yaw": 0.0,
            "body.head.yaw": 0.0,
            "body.head.roll": 0.0,
            "body.legs.left.upper.pitch":0.0,
            "body.legs.right.upper.pitch":0.0
        }},
    ],
    "move_4": [
        {"time": 0.5* delta_t, "data": {
            "body.torso.yaw": -0.5,
            "body.legs.right.lower.pitch": 0.1,
            "body.legs.left.lower.pitch": -0.1,
            "body.arms.right.upper.pitch": -0.3,
            "body.arms.left.upper.pitch": 0.6,
            "body.head.yaw": -0.5,
            "body.head.roll": 0.174,
            "body.legs.left.upper.pitch":0.0,
            "body.legs.right.upper.pitch":0.0
        }},
        {"time": 1 * delta_t, "data": {
            "body.torso.yaw": 0.0,
            "body.legs.right.lower.pitch": 0.0,
            "body.legs.left.lower.pitch": 0.0,
            "body.arms.right.upper.pitch": 0.0,
            "body.arms.left.upper.pitch": 0.0,
            "body.head.yaw": 0.0,
            "body.head.roll": -0.174,
            "body.legs.left.upper.pitch":0.0,
            "body.legs.right.upper.pitch":0.0
        }},
    ]
}

music_start_time = 0.0  # Track when music starts

@inlineCallbacks
def play_music(session, language: str):
    """Plays music using the WAMP streaming API."""
    global music_start_time

    if language == "nl":
        url="https://audio.jukehost.co.uk/CB682YXgzhWzFbN6WMxQUAqmiRCuUsiY"
    else:
        url="https://audio.jukehost.co.uk/4tS0VmA72jU8YGPAYvmOQVBnih7bpEnB"

    try:
        result = yield session.call("rom.actuator.audio.stream", url=url, sync=False)
        music_start_time = time.time()
        print(f"Music started successfully: {result}")
    except Exception as e:
        print(f"Error starting music: {e}")

@inlineCallbacks
def execute_move(session, move_name, expected_time):
    """Executes a move at the expected time using perform_movement."""
    actual_time = time.time() - music_start_time
    delay = actual_time - expected_time
    print(f"Executing {move_name} at {actual_time:.2f}s (Expected: {expected_time:.2f}, Delay: {delay:.2f})")

    move = dance_moves.get(move_name, None)
    if move:
        try:
            yield perform_movement(session, frames=move)
        except Exception as e:
            logging.error(f"Error executing {move_name}: {e}", exc_info=True)
            print(f"Error executing {move_name}: {e}")

def schedule_moves(session, beat_times, song_duration):
    """Schedules moves based on beat timings in a loop, executing a move every 4 beats."""
    deferreds = []
    move_keys = list(dance_moves.keys())  # ["move_1", "move_2", "move_3", "move_4"]
    move_index = 0  

    for i in range(0, len(beat_times), 4):  # Every 4 beats
        if beat_times[i] > song_duration:  # Stop scheduling if song is over
            break

        move_name = move_keys[move_index % len(move_keys)]
        move_index += 1  

        d = defer.Deferred()
        reactor.callLater(beat_times[i], d.callback, (move_name, beat_times[i]))
        d.addCallback(lambda data: execute_move(session, *data))
        deferreds.append(d)

    return defer.DeferredList(deferreds)

@inlineCallbacks
def main(session, audio_path, language: str):
    """Main execution function when session is connected."""
    print("Getting beats and dance...")

    yield session.call("rom.optional.behavior.play", name="BlocklyStand")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, "..", "..", "beat_timestamps.json")

    print("opening json path")
    # Load the beat timestamps
    with open(json_path, "r") as f:
        beat_data = json.load(f)
    print("opened beat timestamps")

    beat_times = beat_data["beats"]

    global music_start_time
    music_start_time = time.time()

    # Load audio and calculate tempo
    y, sr = librosa.load(audio_path)
    print("load audio")
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    print("got tempo")
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    print("got beat times")

    # Save beat timestamps
    with open("beat_timestamps.json", "w") as f:
        json.dump({"beats": beat_times.tolist()}, f, indent=4)
    print("opened beat timestamps")

    print(f"Detected Tempo: {tempo} BPM")
    print(f"Saved {len(beat_times)} beats to beat_timestamps.json")

    # Get song duration (moved this earlier to ensure it's defined)
    song_duration = librosa.get_duration(y=y, sr=sr)
    print(f"Song Duration: {song_duration:.2f} seconds")

    # Run the music and schedule the moves
    deferreds = [play_music(session, language), schedule_moves(session, beat_times, song_duration)]
    print("deferred")
    yield defer.DeferredList(deferreds)

    yield sleep(song_duration)
    yield session.call("rom.actuator.audio.stop")
    yield session.call("rom.optional.behavior.play", name="BlocklyStand")
    print("done with song main")
