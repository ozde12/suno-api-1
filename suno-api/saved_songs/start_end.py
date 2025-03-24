import json
import os
import time
from twisted.internet import reactor, defer
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.component import Component, run
from autobahn.twisted.util import sleep
from alpha_mini_rug import perform_movement  # Import movement function

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
        }},
        {"time": 1.0 * delta_t, "data": {
            "body.head.yaw": 0.0,  
            "body.arms.right.upper.pitch": 0.0,
            "body.arms.left.upper.pitch": 0.0,
            "body.torso.yaw": 0.0,
            "body.legs.right.lower.pitch": 0.0,
            "body.legs.left.lower.pitch": 0.0,
            "body.head.roll": 0.0,
        }},
    ],
    "move_2": [
        {"time": 0.5 * delta_t, "data": {
            "body.arms.right.upper.pitch": -0.5,
            "body.arms.left.upper.pitch": 0.5,
            "body.legs.right.lower.pitch": 0.0,
            "body.legs.left.lower.pitch": 0.0,
            "body.head.yaw": 0.0,
            "body.torso.yaw": 0.0,
            "body.head.roll": 0.174,
        }},
        {"time": 1 * delta_t, "data": {
            "body.arms.right.upper.pitch": 0.0,
            "body.arms.left.upper.pitch": 0.0,
            "body.legs.right.lower.pitch": 0.0,
            "body.legs.left.lower.pitch": 0.0,
            "body.head.yaw": 0.0,
            "body.torso.yaw": 0.0,
            "body.head.roll": -0.174,
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
        }},
        {"time": 1 * delta_t, "data": {
            "body.arms.right.upper.pitch": 0.0,
            "body.arms.left.upper.pitch": 0.0,
            "body.legs.right.lower.pitch": 0.0,
            "body.legs.left.lower.pitch": 0.0,
            "body.torso.yaw": 0.0,
            "body.head.yaw": 0.0,
            "body.head.roll": 0.0,
        }},
    ],
    "move_4": [
        {"time": 0.5 * delta_t, "data": {
            "body.torso.yaw": 0.7,
            "body.legs.right.lower.pitch": 0.1,
            "body.legs.left.lower.pitch": -0.1,
            "body.arms.right.upper.pitch": -0.3,
            "body.arms.left.upper.pitch": 0.6,
            "body.head.yaw": -0.5,
            "body.head.roll": 0.174,
        }},
        {"time": 1 * delta_t, "data": {
            "body.torso.yaw": 0.0,
            "body.legs.right.lower.pitch": 0.0,
            "body.legs.left.lower.pitch": 0.0,
            "body.arms.right.upper.pitch": 0.0,
            "body.arms.left.upper.pitch": 0.0,
            "body.head.yaw": 0.0,
            "body.head.roll": -0.174
        }},
    ]
}

# Load word timestamps from JSON file
def extract_word_timestamps(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if not content:
            raise ValueError(f"JSON file is empty: {file_path}")

        data = json.loads(content)

    word_timestamps = []
    for segment in data.get("segments", []):
        for word in segment.get("words", []):
            word_timestamps.append({
                "word": word["word"],
                "start": word["start"],
                "end": word["end"]
            })

    return word_timestamps

# Define song file location
json_file = r"C:\Users\ozdep\Documents\suno 1002\suno-api\suno-api\word_timestamps.json"
word_timestamps = extract_word_timestamps(json_file)

# Directly schedule moves based on start and end times
def schedule_moves(session):
    deferreds = []
    for i, word in enumerate(word_timestamps):
        move_name = f"move_{(i % len(dance_moves)) + 1}"  # Cycle through moves like move_1, move_2, etc.

        # Schedule movement based on the start time of the word
        d = defer.Deferred()
        reactor.callLater(word["start"], d.callback, (move_name, word["start"]))  # Use word start time for movement
        d.addCallback(lambda data: execute_move(session, *data))
        deferreds.append(d)

    return defer.DeferredList(deferreds)

@inlineCallbacks
def execute_move(session, move_name, expected_time):
    actual_time = time.time()
    delay = actual_time - expected_time
    print(f"Executing {move_name} at {actual_time:.2f}s (Expected: {expected_time:.2f}, Delay: {delay:.2f})")

    try:
        yield perform_movement(session, frames=dance_moves[move_name])
    except Exception as e:
        print(f"Error executing {move_name}: {e}")

@inlineCallbacks
def main(session, details):
    """Main function for executing robot dance moves."""
    print("Session connected!")

    # Start music playback
    yield session.call("rom.optional.behavior.play", name="BlocklyStand")
    yield sleep(1)  # Short delay before moves

    # Schedule moves dynamically based on word timestamps
    yield schedule_moves(session)

    # Wait for the song to finish
    yield sleep(max(word["end"] for word in word_timestamps))  # Wait until the last word's end time
    yield session.call("rom.actuator.audio.stop")
    session.leave()

# WAMP Component for controlling the robot
wamp = Component(
    transports=[{"url": "ws://wamp.robotsindeklas.nl", "serializers": ["msgpack"], "max_retries": 0}],
    realm="rie.67e141ca540602623a34e03f",
)
wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])
