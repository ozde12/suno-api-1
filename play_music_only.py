from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
@inlineCallbacks
def main(session, details):
	yield session.call("rom.actuator.audio.stream",
		url="https://audio.jukehost.co.uk/V0nXb4jfEjrJ1rT8D1Z04dTNIneY74Al",
		sync=False
	)
	yield sleep(30)
	yield session.call("rom.actuator.audio.stop")
	session.leave() # Close the connection with the robot
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
