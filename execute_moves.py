import os
import random
from typing import Dict, Generator, List, Tuple
import nltk
#import spacy
from twisted.internet.defer import DeferredList, inlineCallbacks
from openai import OpenAI
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from alpha_mini_rug import perform_movement
from typing import Generator
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.component import Component, run

Jingle_bells = [
    {'time': 0.0, 'data': {'body.head.pitch': 0, 'body.legs.right.foot.roll': 0.03161255787892264, 'body.legs.left.lower.pitch': 0, 'body.arms.right.lower.roll': -0.8726, 'body.legs.left.foot.roll': -0.03161255787892264, 'body.legs.left.upper.pitch': 0, 'body.torso.yaw': -0.017453292519943295, 'body.legs.right.lower.pitch': 0, 'body.head.roll': 0, 'body.head.yaw': 0, 'body.arms.left.upper.pitch': -0.5, 'body.legs.right.upper.pitch': 0, 'body.arms.left.lower.roll': -0.8726, 'body.arms.right.upper.pitch': -0.5}},

{'time': 1.5, 'data': {'body.legs.right.foot.roll': 0.03161255787892264, 'body.legs.left.upper.pitch': 0, 'body.arms.right.upper.pitch': -0.34292036732051034, 'body.legs.right.lower.pitch': 0, 'body.legs.right.upper.pitch': 0, 'body.head.pitch': -0.03490658503988659, 'body.legs.left.foot.roll': -0.03161255787892264, 'body.torso.yaw': -0.017453292519943295, 'body.legs.left.lower.pitch': 0, 'body.head.yaw': 0, 'body.arms.left.lower.roll': -0.8726, 'body.head.roll': 0, 'body.arms.right.lower.roll': -0.8726, 'body.arms.left.upper.pitch': -0.34292036732051034}, 'time': 1742300891715},

{'time': 3.6, 'data': {'body.legs.left.upper.pitch': 0, 'body.head.yaw': 0, 'body.torso.yaw': -0.017453292519943295, 'body.head.pitch': -0.08726646259971647, 'body.legs.right.foot.roll': 0.03161255787892264, 'body.arms.right.upper.pitch': -0.028761101961531033, 'body.legs.left.foot.roll': -0.03161255787892264, 'body.arms.left.upper.pitch': -0.011307809441587713, 'body.legs.right.lower.pitch': 0, 'body.legs.right.upper.pitch': 0, 'body.head.roll': 0, 'body.legs.left.lower.pitch': 0, 'body.arms.right.lower.roll': -0.8726, 'body.arms.left.lower.roll': -0.8726}},

{'time': 5.4, 'data': {'body.arms.right.upper.pitch': 0.23303828583761843, 'body.legs.left.foot.roll': -0.03161255787892264, 'body.arms.left.upper.pitch': 0.26794487087750496, 'body.torso.yaw': -0.017453292519943295, 'body.legs.right.lower.pitch': 0, 'body.legs.left.lower.pitch': 0, 'body.legs.left.upper.pitch': 0, 'body.legs.right.foot.roll': 0.03161255787892264, 'body.arms.right.lower.roll': -0.8726, 'body.head.yaw': 0, 'body.arms.left.lower.roll': -0.8551467074800567, 'body.head.roll': 0, 'body.legs.right.upper.pitch': 0, 'body.head.pitch': -0.15707963267948966}},

{'time': 7.6, 'data': {'body.legs.left.lower.pitch': 0, 'body.legs.left.upper.pitch': 0, 'body.arms.left.upper.pitch': 0.35521133347722134, 'body.head.pitch': -0.17453292519943295, 'body.legs.right.foot.roll': 0.03161255787892264, 'body.arms.right.lower.roll': -0.8726, 'body.torso.yaw': -0.017453292519943295, 'body.legs.left.foot.roll': -0.03161255787892264, 'body.legs.right.lower.pitch': 0, 'body.legs.right.upper.pitch': 0, 'body.head.roll': 0, 'body.head.yaw': 0, 'body.arms.left.lower.roll': -0.8376934149601134, 'body.arms.right.upper.pitch': 0.3377580409572781}},

{'time': 9.2, 'data': {'body.legs.left.upper.pitch': 0, 'body.legs.right.upper.pitch': 0, 'body.legs.left.lower.pitch': 0, 'body.arms.right.lower.roll': -0.8726, 'body.head.roll': 0, 'body.head.yaw': 0, 'body.legs.left.foot.roll': -0.03161255787892264, 'body.arms.left.upper.pitch': 0.35521133347722134, 'body.torso.yaw': -0.017453292519943295, 'body.head.pitch': 0.15707963267948966, 'body.arms.right.upper.pitch': 0.3203047484373349, 'body.legs.right.lower.pitch': 0, 'body.arms.left.lower.roll': -0.8376934149601134, 'body.legs.right.foot.roll': 0.03161255787892264}},

{'time': 11.9, 'data': {'body.head.roll': 0, 'body.legs.left.upper.pitch': 0, 'body.legs.right.upper.pitch': 0, 'body.head.pitch': 0.15707963267948966, 'body.legs.right.foot.roll': 0.03161255787892264, 'body.legs.left.foot.roll': -0.03161255787892264, 'body.torso.yaw': -0.017453292519943295, 'body.arms.right.upper.pitch': 0.3377580409572781, 'body.arms.left.upper.pitch': 0.35521133347722134, 'body.arms.right.lower.roll': -0.8726, 'body.head.yaw': 0, 'body.legs.right.lower.pitch': 0, 'body.arms.left.lower.roll': -0.8376934149601134, 'body.legs.left.lower.pitch': 0}},

{'time': 13.3, 'data': {'body.arms.right.upper.pitch': 0.35521133347722134, 'body.arms.right.lower.roll': -0.8726, 'body.legs.right.upper.pitch': 0, 'body.head.pitch': -0.017453292519943295, 'body.head.roll': -0.06981317007977318, 'body.head.yaw': 0.15707963267948966, 'body.legs.left.foot.roll': -0.03161255787892264, 'body.legs.left.upper.pitch': 0, 'body.arms.left.lower.roll': -0.38390780944158776, 'body.arms.left.upper.pitch': -0.34292036732051034, 'body.legs.right.lower.pitch': 0, 'body.legs.left.lower.pitch': 0, 'body.torso.yaw': -0.06981317007977318, 'body.legs.right.foot.roll': 0.03161255787892264}},

{'time': 16.2, 'data': {'body.legs.right.lower.pitch': 0, 'body.arms.left.lower.roll': -0.2268281767620981, 'body.legs.left.upper.pitch': 0, 'body.head.yaw': 0.22689280275926282, 'body.legs.left.foot.roll': -0.03161255787892264, 'body.legs.right.upper.pitch': 0, 'body.head.pitch': -0.10471975511965977, 'body.legs.right.foot.roll': 0.03161255787892264, 'body.arms.right.lower.roll': -0.8726, 'body.arms.left.upper.pitch': -1.337758040957278, 'body.torso.yaw': -0.15707963267948966, 'body.head.roll': -0.06981317007977318, 'body.arms.right.upper.pitch': 0.37266462599716477, 'body.legs.left.lower.pitch': 0}},

{'time': 19.1, 'data': {'body.legs.left.foot.roll': -0.03161255787892264, 'body.arms.left.lower.roll': -0.5060808570811908, 'body.legs.right.foot.roll': 0.03161255787892264, 'body.head.yaw': 0.12217304763960307, 'body.legs.right.upper.pitch': 0, 'body.head.pitch': -0.017453292519943295, 'body.arms.right.upper.pitch': 0.35521133347722134, 'body.legs.left.lower.pitch': 0, 'body.arms.left.upper.pitch': -2.0009831567151233, 'body.torso.yaw': -0.15707963267948966, 'body.head.roll': -0.017453292519943295, 'body.arms.right.lower.roll': -0.8726, 'body.legs.left.upper.pitch': 0, 'body.legs.right.lower.pitch': 0}},

{'time': 21.9, 'data': {'body.legs.left.foot.roll': -0.03161255787892264, 'body.arms.left.upper.pitch': -1.5821041362364843, 'body.arms.right.upper.pitch': -0.011307809441587713, 'body.legs.right.foot.roll': 0.03161255787892264, 'body.head.yaw': -0.05235987755982988, 'body.legs.right.lower.pitch': 0, 'body.arms.left.lower.roll': -0.6457071972407372, 'body.arms.right.lower.roll': -0.6108006122008507, 'body.legs.right.upper.pitch': 0, 'body.head.roll': 0, 'body.torso.yaw': -0.15707963267948966, 'body.legs.left.upper.pitch': 0, 'body.head.pitch': -0.03490658503988659, 'body.legs.left.lower.pitch': 0}},
]

@inlineCallbacks
def main(session, details):
    movements = perform_movement(session, frames = Jingle_bells, mode="linear", sync=False, force=False)
    yield movements
    yield session.call("rom.optional.behavior.play", name="BlocklyStand")
    session.leave()

wamp = Component(
    transports=[{"url": "ws://wamp.robotsindeklas.nl", "serializers": ["msgpack"], "max_retries": 0}],
    realm="rie.67dbf737540602623a34c5ba",
)

wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])