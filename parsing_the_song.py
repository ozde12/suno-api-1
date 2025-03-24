import json
import time
from twisted.internet import reactor, defer
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.component import Component, run
from autobahn.twisted.util import sleep
from alpha_mini_rug import perform_movement  # Import movement function

# Define a time scaling factor
delta_t = 1500 

# Define dance moves with structured frames
dance_moves = {
    "intro_or_outro_moves": [
        {"time": 0.5 * delta_t, "data": {
            "body.head.yaw": 0.4,  
            "body.arms.right.upper.pitch": -0.5,
            "body.arms.left.upper.pitch": -0.5,
            "body.torso.yaw": 0.25,
            "body.legs.right.upper.pitch": 0.0,
            "body.legs.left.upper.pitch": 0.0,
            "body.head.roll": 0.0
        }},
        {"time": 1.0 * delta_t, "data": {
            "body.head.yaw": 0.0,  
            "body.arms.right.upper.pitch": 0.0,
            "body.arms.left.upper.pitch": 0.0,
            "body.torso.yaw": 0.0,
            "body.legs.right.upper.pitch": 0.0,
            "body.legs.left.upper.pitch": 0.0,
            "body.head.roll": 0.0
        }},
        {"time": 1.5 * delta_t, "data": {
            "body.head.yaw": -0.4,  
            "body.arms.right.upper.pitch": 0.5,
            "body.arms.left.upper.pitch": 0.5,
            "body.torso.yaw": -0.25,
            "body.legs.right.upper.pitch": 0.0,
            "body.legs.left.upper.pitch": 0.0,
            "body.head.roll": 0.0
        }},
        {"time": 2.0 * delta_t, "data": {
            "body.head.yaw": 0.0,  
            "body.arms.right.upper.pitch": 0.0,
            "body.arms.left.upper.pitch": 0.0,
            "body.torso.yaw": 0.0,
            "body.legs.right.upper.pitch": 0.0,
            "body.legs.left.upper.pitch": 0.0,
            "body.head.roll": 0.0
        }},
    ],
    "verse_moves": [
        {"time": 0.5 * delta_t, "data": {
            "body.arms.right.upper.pitch": -0.5,
            "body.arms.left.upper.pitch": 0.5,
            "body.legs.right.lower.pitch": 0.0,
            "body.legs.left.lower.pitch": 0.0,
            "body.head.yaw": 0.0,
            "body.torso.yaw": 0.0,
            "body.head.roll": 0.174
        }},
        {"time": 1 * delta_t, "data": {
            "body.arms.right.upper.pitch": 0.0,
            "body.arms.left.upper.pitch": 0.0,
            "body.legs.right.lower.pitch": 0.0,
            "body.legs.left.lower.pitch": 0.0,
            "body.head.yaw": 0.0,
            "body.torso.yaw": 0.0,
            "body.head.roll": -0.174
        }},
        {"time": 1.5 * delta_t, "data": {
            "body.arms.right.upper.pitch": 0.5,
            "body.arms.left.upper.pitch": -0.5,
            "body.legs.right.lower.pitch": 0.0,
            "body.legs.left.lower.pitch": 0.0,
            "body.head.yaw": 0.0,
            "body.torso.yaw": 0.0,
            "body.head.roll": 0.174
        }},
        {"time": 2.0 * delta_t, "data": {
            "body.arms.right.upper.pitch": 0.0,
            "body.arms.left.upper.pitch": 0.0,
            "body.legs.right.lower.pitch": 0.0,
            "body.legs.left.lower.pitch": 0.0,
            "body.head.yaw": 0.0,
            "body.torso.yaw": 0.0,
            "body.head.roll": -0.174
        }},
    ],
    "chorus_moves": [
        {"time": 1.0 * delta_t, "data": {
            "body.arms.right.upper.pitch": -1.5,
            "body.arms.left.upper.pitch": 1.5,
            "body.legs.right.upper.pitch": 0.1,
            "body.legs.left.upper.pitch": -0.1,
            "body.torso.yaw": 0.5,
            "body.head.yaw": 0.0,
            "body.head.roll": 0.0
        }},
        {"time": 2.0 * delta_t, "data": {
            "body.arms.right.upper.pitch": 0.0,
            "body.arms.left.upper.pitch": 0.0,
            "body.legs.right.upper.pitch": 0.0,
            "body.legs.left.upper.pitch": 0.0,
            "body.torso.yaw": 0.0,
            "body.head.yaw": 0.0,
            "body.head.roll": 0.0
        }},
        {"time": 3.0 * delta_t, "data": {
            "body.arms.right.upper.pitch": 1.5,
            "body.arms.left.upper.pitch": -1.5,
            "body.legs.right.upper.pitch": -0.1,
            "body.legs.left.upper.pitch": 0.1,
            "body.torso.yaw": -0.5,
            "body.head.yaw": 0.0,
            "body.head.roll": 0.0
        }},
        {"time": 4.0 * delta_t, "data": {
            "body.arms.right.upper.pitch": 0.0,
            "body.arms.left.upper.pitch": 0.0,
            "body.legs.right.upper.pitch": 0.0,
            "body.legs.left.upper.pitch": 0.0,
            "body.torso.yaw": 0.0,
            "body.head.yaw": 0.0,
            "body.head.roll": 0.0
        }},
    ],
    "bridge_moves": [
        {"time": 0.5 * delta_t, "data": {
            "body.torso.yaw": 0.7,
            "body.legs.right.upper.pitch": 0.2,
            "body.legs.left.upper.pitch": -0.2,
            "body.arms.right.upper.pitch": -0.3,
            "body.arms.left.upper.pitch": 0.6,
            "body.head.yaw": 0.0,
            "body.head.roll": 0.0
        }},
        {"time": 1 * delta_t, "data": {
            "body.torso.yaw": 0.0,
            "body.legs.right.upper.pitch": 0.0,
            "body.legs.left.upper.pitch": 0.0,
            "body.arms.right.upper.pitch": 0.0,
            "body.arms.left.upper.pitch": 0.0,
            "body.head.yaw": 0.0,
            "body.head.roll": 0.0
        }},
    ]
}

music_start_time = 0.0  

@inlineCallbacks
def play_music(session):
    """Plays music using the WAMP streaming API."""
    global music_start_time
    print(f"Music playback requested at {music_start_time:.2f} seconds (system time).")

    try:
        result = yield session.call(
            "rom.actuator.audio.stream",
            url="https://audio.jukehost.co.uk/V0nXb4jfEjrJ1rT8D1Z04dTNIneY74Al",
            sync=False
        )
        music_start_time = time.time()
        print(f"Music started successfully: {result}")
    except Exception as e:
        print(f"Error starting music: {e}")

@inlineCallbacks
def execute_move(session, move_name, expected_time):
    """Executes a move at the expected time using perform_movement."""
    actual_time = time.time() - music_start_time
    delay = actual_time - expected_time
    print(f"Executing move: {move_name} at {actual_time:.2f}s (Expected: {expected_time:.2f}, Delay: {delay:.2f})")

    try:
        yield perform_movement(session, frames=dance_moves[move_name])
    except Exception as e:
        print(f"Error executing {move_name}: {e}")

def schedule_moves(session, timestamps):
    """Schedules moves using a DeferredList."""
    deferreds = []
    start_time = time.time()

    MOVE_INTERVALS = {
        "verse": 4,
        "chorus": 4,
        "bridge": 6,
        "intro_or_outro": 4
    }

    for section, times in timestamps.items():
        move_name = section + "_moves"
        if move_name not in dance_moves:
            print(f"Warning: No move found for section '{section}'")
            continue

        interval = MOVE_INTERVALS.get(section, 4)
        filtered_times = times[::interval]

        for t in filtered_times:
            d = defer.Deferred()
            reactor.callLater(t, d.callback, (move_name, t))
            d.addCallback(lambda data: execute_move(session, *data))
            deferreds.append(d)

    return defer.DeferredList(deferreds)

@inlineCallbacks
def main(session, details):
    """Main execution function when session is connected."""
    print("Session connected!")

    yield session.call("rom.optional.behavior.play", name="BlocklyStand")

    with open("music_analysis.json", "r") as f:
        analysis = json.load(f)

    timestamps = analysis["movement_schedule"]

    valid_times = [times for times in timestamps.values() if times]
    if not valid_times:
        raise ValueError("Error: No valid timestamps found in movement_schedule.")

    song_duration = max(max(times) for times in valid_times)
    print(f"Extracted Song Duration: {song_duration} seconds")

    # Start music and schedule moves simultaneously
    deferreds = [play_music(session), schedule_moves(session, timestamps)]
    yield defer.DeferredList(deferreds)

    # Wait for song to finish
    yield sleep(song_duration)
    yield session.call("rom.actuator.audio.stop")
    session.leave()

# WAMP Component for streaming music
wamp = Component(
    transports=[{
        "url": "ws://wamp.robotsindeklas.nl",
        "serializers": ["msgpack"],
        "max_retries": 0
    }],
    realm="rie.67e12fe8540602623a34dfc1",
)
wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])
