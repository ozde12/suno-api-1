import librosa
import json
import time
from twisted.internet import reactor, defer
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.component import Component, run
from autobahn.twisted.util import sleep
from alpha_mini_rug import perform_movement  # Import movement function
import logging

# Load the audio file and detect beats
audio_path = r"C:\Users\ozdep\Documents\suno 1002\suno-api\suno-api\saved_songs\song_in_dutch.mp3"
y, sr = librosa.load(audio_path)
tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
beat_times = librosa.frames_to_time(beat_frames, sr=sr)

# Save beat timestamps
with open("beat_timestamps.json", "w") as f:
    json.dump({"beats": beat_times.tolist()}, f, indent=4)

print(f"Detected Tempo: {tempo:.2f} BPM")
print(f"Saved {len(beat_times)} beats to beat_timestamps.json")

# Get song duration
song_duration = librosa.get_duration(y=y, sr=sr)

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
    ],
    "move_5": [
    {
        "time": 1.0 * delta_t,
        "data": {
            "body.torso.yaw": -0.15,                         # Lean torso slightly for balance
            "body.legs.right.upper.pitch": 1.2,              # Raise right leg
            "body.legs.right.lower.pitch": 0.1,              # Slight bend
            "body.legs.left.upper.pitch": 0.0,
            "body.legs.left.lower.pitch": 0.25,              # Supporting leg slightly bent
            "body.arms.right.upper.pitch": -0.3,             # Counter arm
            "body.arms.left.upper.pitch": 0.4,               # Balance arm
            "body.head.yaw": 0.0,
            "body.head.roll": 0.1                            # Subtle head tilt
        }
    },
    {
        "time": 3.0 * delta_t,
        "data": {
            "body.torso.yaw": 0.15,                          # Shift torso the other way
            "body.legs.left.upper.pitch": 1.2,               # Raise left leg
            "body.legs.left.lower.pitch": 0.1,
            "body.legs.right.upper.pitch": 0.0,
            "body.legs.right.lower.pitch": 0.25,
            "body.arms.left.upper.pitch": -0.3,
            "body.arms.right.upper.pitch": 0.4,
            "body.head.yaw": 0.0,
            "body.head.roll": -0.1
        }
    },
    {
        "time": 5.5 * delta_t,
        "data": {
            "body.torso.yaw": 0.0,
            "body.legs.right.upper.pitch": 0.0,
            "body.legs.right.lower.pitch": 0.0,
            "body.legs.left.upper.pitch": 0.0,
            "body.legs.left.lower.pitch": 0.0,
            "body.arms.right.upper.pitch": 0.0,
            "body.arms.left.upper.pitch": 0.0,
            "body.head.yaw": 0.0,
            "body.head.roll": 0.0
        }
    }
    ]

}
# WAMP Component
wamp = Component(
    transports=[{"url": "ws://wamp.robotsindeklas.nl", "serializers": ["msgpack"], "max_retries": 0}],
    realm="rie.67e28066540602623a34e87d",
)

music_start_time = 0.0  # Track when music starts

@inlineCallbacks
def play_music(session):
    """Plays music using the WAMP streaming API."""
    global music_start_time
    try:
        result = yield session.call("rom.actuator.audio.stream", url="https://audio.jukehost.co.uk/CB682YXgzhWzFbN6WMxQUAqmiRCuUsiY ", sync=False)
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

def schedule_moves(session, beat_times):
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
def main(session, details):
    """Main execution function when session is connected."""
    print("Session connected!")

    yield session.call("rom.optional.behavior.play", name="BlocklyStand")

    with open("beat_timestamps.json", "r") as f:
        beat_data = json.load(f)

    beat_times = beat_data["beats"]

    global music_start_time  
    music_start_time = time.time()  

    deferreds = [play_music(session), schedule_moves(session, beat_times)]
    yield defer.DeferredList(deferreds)

    yield sleep(song_duration)
    yield session.call("rom.actuator.audio.stop")
    session.leave()

wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])
