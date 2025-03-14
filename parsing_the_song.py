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

# WAMP Component for streaming music
wamp = Component(
    transports=[{
        "url": "ws://wamp.robotsindeklas.nl",
        "serializers": ["msgpack"],
        "max_retries": 0
    }],
    realm="rie.67d401c799b259cf43b059e6",
)

@inlineCallbacks
def play_music(session):
    """Plays music using the WAMP streaming API."""
    print("Starting music...")
    yield session.call("rom.actuator.audio.stream",
        url="https://audio.jukehost.co.uk/V0nXb4jfEjrJ1rT8D1Z04dTNIneY74Al",
        sync=False
    )
    print("Music started.")

@inlineCallbacks
def execute_move(session, move):
    """Simulate executing a move."""
    yield session.call("rom.optional.behavior.play", name=move)

def schedule_moves(session, timestamps):
    """Schedule moves and music playback together."""
    deferreds = []

    # Schedule Music Start
    d_music = defer.Deferred()
    reactor.callLater(0, d_music.callback, session)
    d_music.addCallback(play_music)
    deferreds.append(d_music)

    # Schedule Moves
    for section, times in timestamps.items():
        move = MOVES.get(section, "Unknown Move")

        for t in times:
            d = defer.Deferred()
            reactor.callLater(t, d.callback, move)
            d.addCallback(execute_move(session, move))
            deferreds.append(d)

    return defer.DeferredList(deferreds)

@inlineCallbacks
def main(session, details):
    """Main function to start music and execute moves in sync."""
    with open("music_analysis.json", "r") as f:
        analysis = json.load(f)

    timestamps = analysis["section_timestamps"]

    # Schedule music and moves at the same time
    yield schedule_moves(session, timestamps)

    # Wait for the song to finish
    yield sleep(30)  # Adjust to actual song duration
    yield session.call("rom.actuator.audio.stop")
    session.leave()

wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])
