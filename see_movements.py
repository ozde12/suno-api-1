from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks


@inlineCallbacks
def main(session, details):
    #moves = yield session.call("rom.optional.behavior.info")
	#yield session.call("rom.optional.behavior.play", name="standbysquat_002")
    #print(moves)
	yield session.call("rom.optional.behavior.play", name="BlocklyTouchShoulders")
	yield session.call("rom.optional.behavior.play", name="BlocklySneeze")
	yield session.call("rom.optional.behavior.play", name="dance_00011en")
	
	#yield session.call("rom.optional.behavior.play", name="BlocklyLeftArmUp")
	#yield session.call("rom.optional.behavior.play", name="BlocklyRightArmUp")


wamp = Component(
	transports=[{
		"url": "ws://wamp.robotsindeklas.nl",
		"serializers": ["msgpack"],
		"max_retries": 0
	}],
	realm="rie.67d942577d4143cdaa821da2",
)

wamp.on_join(main)

if __name__ == "__main__":
	run([wamp])