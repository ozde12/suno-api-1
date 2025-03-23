import librosa
import json
import time
from twisted.internet import reactor, defer
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.component import Component, run
from autobahn.twisted.util import sleep
from alpha_mini_rug import perform_movement  # Import movement function

# Load the audio file
audio_path = r"C:\Users\ozdep\Documents\suno 1002\suno-api\suno-api\saved_songs\Purrfect_Day.mp3"
y, sr = librosa.load(audio_path)

# Detect beats
tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
beat_times = librosa.frames_to_time(beat_frames, sr=sr)

# Save beat timestamps
with open("beat_timestamps.json", "w") as f:
    json.dump({"beats": beat_times.tolist()}, f, indent=4)

print(f"Detected Tempo: {tempo:.2f} BPM")
print(f"Saved {len(beat_times)} beats to beat_timestamps.json")

# Define renamed dance moves in sequence
dance_moves = [
    {"name": "Move 1", "data": {
        "body.head.yaw": 0.4, "body.arms.right.upper.pitch": -0.5,
        "body.arms.left.upper.pitch": -0.5, "body.torso.yaw": 0.25
    }},
    {"name": "Move 2", "data": {
        "body.head.yaw": -0.4, "body.arms.right.upper.pitch": 0.5,
        "body.arms.left.upper.pitch": 0.5, "body.torso.yaw": -0.25
    }},
    {"name": "Move 3", "data": {
        "body.arms.right.upper.pitch": -0.5, "body.arms.left.upper.pitch": 0.5,
        "body.head.roll": 0.174
    }},
    {"name": "Move 4", "data": {
        "body.arms.right.upper.pitch": 0.5, "body.arms.left.upper.pitch": -0.5,
        "body.head.roll": -0.174
    }},
    {"name": "Move 5", "data": {
        "body.arms.right.upper.pitch": -1.5, "body.arms.left.upper.pitch": 1.5,
        "body.torso.yaw": 0.5
    }},
    {"name": "Move 6", "data": {
        "body.arms.right.upper.pitch": 1.5, "body.arms.left.upper.pitch": -1.5,
        "body.torso.yaw": -0.5
    }},
    {"name": "Move 7", "data": {
        "body.torso.yaw": 0.7, "body.legs.right.upper.pitch": 0.2,
        "body.legs.left.upper.pitch": -0.2
    }},
]

# WAMP Component for robot communication
wamp = Component(
    transports=[{"url": "ws://wamp.robotsindeklas.nl", "serializers": ["msgpack"], "max_retries": 0}],
    realm="rie.67dbce6b540602623a34c4a8",
)

music_start_time = 0.0  # Track when music starts

@inlineCallbacks
def play_music(session):
    """Plays music using the WAMP streaming API."""
    global music_start_time
    try:
        result = yield session.call("rom.actuator.audio.stream", url="https://audio.jukehost.co.uk/V0nXb4jfEjrJ1rT8D1Z04dTNIneY74Al", sync=False)
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

    move = next((m for m in dance_moves if m["name"] == move_name), None)
    if move:
        try:
            yield perform_movement(session, frames=[{"time": 0.5, "data": move["data"]}])
        except Exception as e:
            print(f"Error executing {move_name}: {e}")

def schedule_moves(session, beat_times):
    """Schedules moves based on beat timings."""
    deferreds = []
    move_index = 0  # Track which move to use next

    for i, beat_time in enumerate(beat_times):
        move_name = dance_moves[move_index]["name"]  # Get move name in order
        move_index = (move_index + 1) % len(dance_moves)  # Loop through moves

        d = defer.Deferred()
        reactor.callLater(beat_time, d.callback, (move_name, beat_time))
        d.addCallback(lambda data: execute_move(session, *data))
        deferreds.append(d)

    return defer.DeferredList(deferreds)

@inlineCallbacks
def main(session, details):
    """Main execution function when session is connected."""
    print("Session connected!")

    yield session.call("rom.optional.behavior.play", name="BlocklyStand")

    # Load beat timestamps
    with open("beat_timestamps.json", "r") as f:
        beat_data = json.load(f)

    beat_times = beat_data["beats"]

    # Start music and schedule moves
    deferreds = [play_music(session), schedule_moves(session, beat_times)]
    yield defer.DeferredList(deferreds)

    # Wait for song to finish
    yield sleep(beat_times[-1])
    yield session.call("rom.actuator.audio.stop")
    session.leave()

wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])
