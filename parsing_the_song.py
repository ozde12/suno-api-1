import json
from twisted.internet import reactor, defer
from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep

# Define Moves
MOVES = {
    "verse": "Stand/Emotions/Positive/Happy_1",
    "chorus": "Stand/Emotions/Positive/Winner_2",
    "bridge": "BlocklyTouchShoulders"
}

@inlineCallbacks
def play_music(session):
    """Plays music using the WAMP streaming API."""
    print("Starting music playback...")

    try:
        result = yield session.call("rom.actuator.audio.stream",
            url="https://audio.jukehost.co.uk/V0nXb4jfEjrJ1rT8D1Z04dTNIneY74Al",
            sync=False
        )
        print(f"Music started successfully: {result}")  # Debugging response from WAMP API
    except Exception as e:
        print(f"Error starting music: {e}")


@inlineCallbacks
def execute_move(session, move):
    """Simulate executing a move."""
    print(f"Executing move: {move}")  # Debugging
    yield session.call("rom.optional.behavior.play", name=move)

def schedule_moves(session, timestamps):
    """Schedule moves, reducing movement density."""
    deferreds = []

    MOVE_INTERVALS = {
        "verse": 4,
        "chorus": 2,
        "bridge": 6
    }

    for section, times in timestamps.items():
        move = MOVES.get(section)  # Get move based on section name

        if move is None:
            print(f"Warning: No move found for section '{section}'")
            continue  # Skip scheduling unknown moves

        interval = MOVE_INTERVALS.get(section, 4)
        filtered_times = times[::interval]

        print(f"Scheduling {len(filtered_times)} moves for {section} ({move})")

        for t in filtered_times:
            print(f"Scheduling move {move} at time {t:.2f}")

            d = defer.Deferred()
            reactor.callLater(t, d.callback, move)
            d.addCallback(lambda move_name: execute_move(session, move_name))
            deferreds.append(d)

    return defer.DeferredList(deferreds)

@inlineCallbacks
def main(session, details):
    print("Session connected!")

    with open("music_analysis.json", "r") as f:
        analysis = json.load(f)

    timestamps = analysis["movement_schedule"]

    valid_times = [times for times in timestamps.values() if times]
    if not valid_times:
        raise ValueError("Error: No valid timestamps found in movement_schedule.")

    song_duration = max(max(times) for times in valid_times)

    print(f"Extracted Song Duration: {song_duration} seconds")

    # Start music first
    yield play_music(session)
    
    # Schedule movements slightly after music starts
    yield sleep(1)  # Small delay to ensure music starts before moves
    yield schedule_moves(session, timestamps)

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
    realm="rie.67d7f8f37d4143cdaa8217c2",
)
wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])
