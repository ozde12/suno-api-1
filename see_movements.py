from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks


@inlineCallbacks
def main(session, details):
    #moves = yield session.call("rom.optional.behavior.info")
    #print(moves)
	yield session.call("rom.optional.behavior.play", name="dance_00011en'")


wamp = Component(
	transports=[{
		"url": "ws://wamp.robotsindeklas.nl",
		"serializers": ["msgpack"],
		"max_retries": 0
	}],
	realm="rie.67d401c799b259cf43b059e6",
)

wamp.on_join(main)

if __name__ == "__main__":
	run([wamp])