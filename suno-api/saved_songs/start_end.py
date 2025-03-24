import json
import os
import time
from twisted.internet import reactor, defer
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.component import Component, run
from autobahn.twisted.util import sleep
from alpha_mini_rug import perform_movement  # Import movement function

# Define movement patterns
dance_moves = {
    "lyrical_moves": [
        {"time": 0.5, "data": {"body.arms.right.upper.pitch": -0.5, "body.arms.left.upper.pitch": 0.5}},
        {"time": 1.0, "data": {"body.arms.right.upper.pitch": 0.0, "body.arms.left.upper.pitch": 0.0}},
        {"time": 1.5, "data": {"body.arms.right.upper.pitch": 0.5, "body.arms.left.upper.pitch": -0.5}}
    ],
    "non_lyrical_moves": [
        {"time": 0.5, "data": {"body.head.yaw": 0.0, "body.torso.yaw": 0.0}},
        {"time": 1.0, "data": {"body.head.yaw": -0.2, "body.torso.yaw": 0.2}}
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
json_file = r"C:\Users\ozdep\Documents\suno 1002\suno-api\suno-api\saved_songs\cat_Song_english.mp3"
word_timestamps = extract_word_timestamps(json_file)

# Group words into lyrical & non-lyrical sections
sections = {"lyrical": [], "non_lyrical": []}
previous_end = 0

for word in word_timestamps:
    word_start, word_end = word["start"], word["end"]

    # If there's a gap, mark it as non-lyrical
    if word_start > previous_end + 1.0:  # Allow short gaps within lyrics
        sections["non_lyrical"].append((previous_end, word_start))

    sections["lyrical"].append((word_start, word_end))
    previous_end = word_end

# If there's an instrumental section at the end
if previous_end < word_timestamps[-1]["end"]:
    sections["non_lyrical"].append((previous_end, word_timestamps[-1]["end"]))

# Save to JSON for debugging
with open("movement_schedule.json", "w") as f:
    json.dump({"movement_schedule": sections}, f, indent=4)

print("Saved movement schedule to movement_schedule.json.")

# Twisted reactor function to execute moves
@inlineCallbacks
def execute_move(session, move_name, expected_time):
    actual_time = time.time()
    delay = actual_time - expected_time
    print(f"Executing {move_name} at {actual_time:.2f}s (Expected: {expected_time:.2f}, Delay: {delay:.2f})")

    try:
        yield perform_movement(session, frames=dance_moves[move_name])
    except Exception as e:
        print(f"Error executing {move_name}: {e}")

# Function to schedule moves dynamically
def schedule_moves(session):
    deferreds = []
    for section, times in sections.items():
        move_name = "lyrical_moves" if section == "lyrical" else "non_lyrical_moves"

        for t in times:
            d = defer.Deferred()
            reactor.callLater(t[0], d.callback, (move_name, t[0]))  # Use start time
            d.addCallback(lambda data: execute_move(session, *data))
            deferreds.append(d)

    return defer.DeferredList(deferreds)

@inlineCallbacks
def main(session, details):
    """Main function for executing robot dance moves."""
    print("Session connected!")

    # Start music playback
    yield session.call("rom.optional.behavior.play", name="BlocklyStand")
    yield sleep(1)  # Short delay before moves

    # Schedule moves dynamically
    yield schedule_moves(session)

    # Wait for the song to finish
    yield sleep(max(t[-1] for t in sections["lyrical"] + sections["non_lyrical"]))
    yield session.call("rom.actuator.audio.stop")
    session.leave()

# WAMP Component for controlling the robot
wamp = Component(
    transports=[{"url": "ws://wamp.robotsindeklas.nl", "serializers": ["msgpack"], "max_retries": 0}],
    realm="rie.67dbce6b540602623a34c4a8",
)
wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])
