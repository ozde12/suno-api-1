import json
from twisted.internet import reactor, defer
from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
import time 

# Define Moves
MOVES = {
    "verse": "Stand/Emotions/Positive/Happy_1",
    "chorus": "Stand/Emotions/Positive/Winner_2",
    "bridge": "BlocklyTouchShoulders",
    "intro_or_outro": "Stand/Emotions/Positive/Winner_2"
}

music_start_time = 0.0

@inlineCallbacks
def play_music(session):
    """Plays music using the WAMP streaming API."""

    global music_start_time
    
    #print("Starting music playback...")
    print(f"Music playback requested at {music_start_time:.2f} seconds (system time).")

    try:
        result = yield session.call("rom.actuator.audio.stream",
            url="https://audio.jukehost.co.uk/V0nXb4jfEjrJ1rT8D1Z04dTNIneY74Al",
            sync=False
        )
        music_start_time = time.time()
        print(f"Music started successfully: {result}")  # Debugging response from WAMP API
    except Exception as e:
        print(f"Error starting music: {e}")


@inlineCallbacks
def execute_move(session, start_time, data):
    """Simulate executing a move."""
    move, expected_time, section = data
    actual_time = time.time() - start_time
    delay = actual_time - expected_time
    print(f"Executing move: {move} at {actual_time:.2f}s for the section {section} Expected: {expected_time}, Delay: {delay:.2f}")  # Debugging
    yield session.call("rom.optional.behavior.play", name=move)

def schedule_moves(session, timestamps):
    """Schedule moves, reducing movement density."""
    deferreds = []

    MOVE_INTERVALS = {
        "verse": 4,
        "chorus": 4,
        "bridge": 6,
        "intro_or_outro": 4
    }
    start_time = time.time()

    for section, times in timestamps.items():
        move = MOVES.get(section)  # Get move based on section name

        if move is None:
            print(f"Warning: No move found for section '{section}'")
            print("NAME OF SECTION:", section)
            continue  # Skip scheduling unknown moves

        interval = MOVE_INTERVALS.get(section, 4)
        filtered_times = times[::interval]

        print(f"Scheduling {len(filtered_times)} moves for {section} ({move})")

        for t in filtered_times:
            d = defer.Deferred()
            expected_exec_time = t
            reactor.callLater(t, d.callback, (move, expected_exec_time, section))  # Pass expected execution time
            d.addCallback(lambda data: execute_move(session, start_time, data))
            deferreds.append(d)

    return defer.DeferredList(deferreds)

@inlineCallbacks
def main(session, details):
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
    realm="rie.67dbf737540602623a34c5ba",
)
wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])