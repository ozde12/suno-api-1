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
    {'time': 1742300891323, 'data': {'body.head.pitch': 0, 'body.legs.right.foot.roll': 0.03161255787892264, 'body.legs.left.lower.pitch': 0, 'body.arms.right.lower.roll': -0.8726, 'body.legs.left.foot.roll': -0.03161255787892264, 'body.legs.left.upper.pitch': 0, 'body.torso.yaw': -0.017453292519943295, 'body.legs.right.lower.pitch': 0, 'body.head.roll': 0, 'body.head.yaw': 0, 'body.arms.left.upper.pitch': -0.5, 'body.legs.right.upper.pitch': 0, 'body.arms.left.lower.roll': -0.8726, 'body.arms.right.upper.pitch': -0.5}},

{'data': {'body.legs.right.foot.roll': 0.03161255787892264, 'body.legs.left.upper.pitch': 0, 'body.arms.right.upper.pitch': -0.34292036732051034, 'body.legs.right.lower.pitch': 0, 'body.legs.right.upper.pitch': 0, 'body.head.pitch': -0.03490658503988659, 'body.legs.left.foot.roll': -0.03161255787892264, 'body.torso.yaw': -0.017453292519943295, 'body.legs.left.lower.pitch': 0, 'body.head.yaw': 0, 'body.arms.left.lower.roll': -0.8726, 'body.head.roll': 0, 'body.arms.right.lower.roll': -0.8726, 'body.arms.left.upper.pitch': -0.34292036732051034}, 'time': 1742300891715},

{'time': 1742300891818, 'data': {'body.legs.left.upper.pitch': 0, 'body.head.yaw': 0, 'body.torso.yaw': -0.017453292519943295, 'body.head.pitch': -0.08726646259971647, 'body.legs.right.foot.roll': 0.03161255787892264, 'body.arms.right.upper.pitch': -0.028761101961531033, 'body.legs.left.foot.roll': -0.03161255787892264, 'body.arms.left.upper.pitch': -0.011307809441587713, 'body.legs.right.lower.pitch': 0, 'body.legs.right.upper.pitch': 0, 'body.head.roll': 0, 'body.legs.left.lower.pitch': 0, 'body.arms.right.lower.roll': -0.8726, 'body.arms.left.lower.roll': -0.8726}},

{'time': 1742300891904, 'data': {'body.arms.right.upper.pitch': 0.23303828583761843, 'body.legs.left.foot.roll': -0.03161255787892264, 'body.arms.left.upper.pitch': 0.26794487087750496, 'body.torso.yaw': -0.017453292519943295, 'body.legs.right.lower.pitch': 0, 'body.legs.left.lower.pitch': 0, 'body.legs.left.upper.pitch': 0, 'body.legs.right.foot.roll': 0.03161255787892264, 'body.arms.right.lower.roll': -0.8726, 'body.head.yaw': 0, 'body.arms.left.lower.roll': -0.8551467074800567, 'body.head.roll': 0, 'body.legs.right.upper.pitch': 0, 'body.head.pitch': -0.15707963267948966}},

{'time': 1742300892009, 'data': {'body.legs.left.lower.pitch': 0, 'body.legs.left.upper.pitch': 0, 'body.arms.left.upper.pitch': 0.35521133347722134, 'body.head.pitch': -0.17453292519943295, 'body.legs.right.foot.roll': 0.03161255787892264, 'body.arms.right.lower.roll': -0.8726, 'body.torso.yaw': -0.017453292519943295, 'body.legs.left.foot.roll': -0.03161255787892264, 'body.legs.right.lower.pitch': 0, 'body.legs.right.upper.pitch': 0, 'body.head.roll': 0, 'body.head.yaw': 0, 'body.arms.left.lower.roll': -0.8376934149601134, 'body.arms.right.upper.pitch': 0.3377580409572781}},

{'time': 1742300892404, 'data': {'body.legs.left.upper.pitch': 0, 'body.legs.right.upper.pitch': 0, 'body.legs.left.lower.pitch': 0, 'body.arms.right.lower.roll': -0.8726, 'body.head.roll': 0, 'body.head.yaw': 0, 'body.legs.left.foot.roll': -0.03161255787892264, 'body.arms.left.upper.pitch': 0.35521133347722134, 'body.torso.yaw': -0.017453292519943295, 'body.head.pitch': 0.15707963267948966, 'body.arms.right.upper.pitch': 0.3203047484373349, 'body.legs.right.lower.pitch': 0, 'body.arms.left.lower.roll': -0.8376934149601134, 'body.legs.right.foot.roll': 0.03161255787892264}},

{'time': 1742300892525, 'data': {'body.head.roll': 0, 'body.legs.left.upper.pitch': 0, 'body.legs.right.upper.pitch': 0, 'body.head.pitch': 0.15707963267948966, 'body.legs.right.foot.roll': 0.03161255787892264, 'body.legs.left.foot.roll': -0.03161255787892264, 'body.torso.yaw': -0.017453292519943295, 'body.arms.right.upper.pitch': 0.3377580409572781, 'body.arms.left.upper.pitch': 0.35521133347722134, 'body.arms.right.lower.roll': -0.8726, 'body.head.yaw': 0, 'body.legs.right.lower.pitch': 0, 'body.arms.left.lower.roll': -0.8376934149601134, 'body.legs.left.lower.pitch': 0}},

{'time': 1742300897010, 'data': {'body.arms.right.upper.pitch': 0.35521133347722134, 'body.arms.right.lower.roll': -0.8726, 'body.legs.right.upper.pitch': 0, 'body.head.pitch': -0.017453292519943295, 'body.head.roll': -0.06981317007977318, 'body.head.yaw': 0.15707963267948966, 'body.legs.left.foot.roll': -0.03161255787892264, 'body.legs.left.upper.pitch': 0, 'body.arms.left.lower.roll': -0.38390780944158776, 'body.arms.left.upper.pitch': -0.34292036732051034, 'body.legs.right.lower.pitch': 0, 'body.legs.left.lower.pitch': 0, 'body.torso.yaw': -0.06981317007977318, 'body.legs.right.foot.roll': 0.03161255787892264}},

{'time': 1742300897217, 'data': {'body.legs.right.lower.pitch': 0, 'body.arms.left.lower.roll': -0.2268281767620981, 'body.legs.left.upper.pitch': 0, 'body.head.yaw': 0.22689280275926282, 'body.legs.left.foot.roll': -0.03161255787892264, 'body.legs.right.upper.pitch': 0, 'body.head.pitch': -0.10471975511965977, 'body.legs.right.foot.roll': 0.03161255787892264, 'body.arms.right.lower.roll': -0.8726, 'body.arms.left.upper.pitch': -1.337758040957278, 'body.torso.yaw': -0.15707963267948966, 'body.head.roll': -0.06981317007977318, 'body.arms.right.upper.pitch': 0.37266462599716477, 'body.legs.left.lower.pitch': 0}},

{'time': 1742300897906, 'data': {'body.legs.left.foot.roll': -0.03161255787892264, 'body.arms.left.lower.roll': -0.5060808570811908, 'body.legs.right.foot.roll': 0.03161255787892264, 'body.head.yaw': 0.12217304763960307, 'body.legs.right.upper.pitch': 0, 'body.head.pitch': -0.017453292519943295, 'body.arms.right.upper.pitch': 0.35521133347722134, 'body.legs.left.lower.pitch': 0, 'body.arms.left.upper.pitch': -2.0009831567151233, 'body.torso.yaw': -0.15707963267948966, 'body.head.roll': -0.017453292519943295, 'body.arms.right.lower.roll': -0.8726, 'body.legs.left.upper.pitch': 0, 'body.legs.right.lower.pitch': 0}},

{'time': 1742300898009, 'data': {'body.legs.left.foot.roll': -0.03161255787892264, 'body.arms.left.upper.pitch': -1.5821041362364843, 'body.arms.right.upper.pitch': -0.011307809441587713, 'body.legs.right.foot.roll': 0.03161255787892264, 'body.head.yaw': -0.05235987755982988, 'body.legs.right.lower.pitch': 0, 'body.arms.left.lower.roll': -0.6457071972407372, 'body.arms.right.lower.roll': -0.6108006122008507, 'body.legs.right.upper.pitch': 0, 'body.head.roll': 0, 'body.torso.yaw': -0.15707963267948966, 'body.legs.left.upper.pitch': 0, 'body.head.pitch': -0.03490658503988659, 'body.legs.left.lower.pitch': 0}},

{'time': 1742300898112, 'data': {'body.legs.left.foot.roll': -0.03161255787892264, 'body.arms.left.upper.pitch': -1.1806784082777886, 'body.head.pitch': -0.10471975511965977, 'body.legs.right.lower.pitch': 0, 'body.arms.right.upper.pitch': -0.4825467074800567, 'body.arms.right.lower.roll': -0.27918805432192806, 'body.head.yaw': -0.296705972839036, 'body.legs.left.upper.pitch': 0, 'body.arms.left.lower.roll': -0.7678802448803402, 'body.head.roll': 0.017453292519943295, 'body.legs.right.foot.roll': 0.03161255787892264, 'body.legs.left.lower.pitch': 0, 'body.torso.yaw': -0.17453292519943295, 'body.legs.right.upper.pitch': 0}},

{'data': {'body.legs.left.foot.roll': -0.03161255787892264, 'body.torso.yaw': -0.17453292519943295, 'body.arms.left.lower.roll': -0.8551467074800567, 'body.head.roll': 0.017453292519943295, 'body.head.pitch': -0.13962634015954636, 'body.arms.right.upper.pitch': -0.918879020478639, 'body.legs.right.foot.roll': 0.03161255787892264, 'body.arms.right.lower.roll': -0.10465512912249508, 'body.head.yaw': -0.4363323129985824, 'body.legs.left.upper.pitch': 0, 'body.legs.right.lower.pitch': 0, 'body.legs.left.lower.pitch': 0, 'body.arms.left.upper.pitch': -0.7268928027592628, 'body.legs.right.upper.pitch': 0}, 'time': 1742300898217},

{'time': 1742300898319, 'data': {'body.legs.left.lower.pitch': 0, 'body.legs.left.upper.pitch': 0, 'body.head.roll': 0.017453292519943295, 'body.legs.right.upper.pitch': 0, 'body.legs.right.foot.roll': 0.03161255787892264, 'body.legs.right.lower.pitch': 0, 'body.head.pitch': -0.10471975511965977, 'body.arms.left.lower.roll': -0.8551467074800567, 'body.arms.right.lower.roll': -0.24428146928204142, 'body.head.yaw': -0.24434609527920614, 'body.arms.left.upper.pitch': -0.2905604897606805, 'body.legs.left.foot.roll': -0.03161255787892264, 'body.torso.yaw': -0.17453292519943295, 'body.arms.right.upper.pitch': -1.337758040957278}},

{'time': 1742300898405, 'data': {'body.legs.right.foot.roll': 0.03161255787892264, 'body.legs.left.foot.roll': -0.03161255787892264, 'body.arms.left.upper.pitch': 0.12831853071795862, 'body.torso.yaw': -0.17453292519943295, 'body.legs.right.upper.pitch': 0, 'body.head.yaw': -0.017453292519943295, 'body.legs.left.upper.pitch': 0, 'body.legs.right.lower.pitch': 0, 'body.arms.right.upper.pitch': -1.7042771838760875, 'body.legs.left.lower.pitch': 0, 'body.arms.right.lower.roll': -0.453720979521361, 'body.head.pitch': -0.03490658503988659, 'body.arms.left.lower.roll': -0.8551467074800567, 'body.head.roll': 0.017453292519943295}},

{'time': 1742300898510, 'data': {'body.head.yaw': -0.03490658503988659, 'body.legs.left.upper.pitch': 0, 'body.legs.right.foot.roll': 0.03161255787892264, 'body.arms.left.upper.pitch': 0.3203047484373349, 'body.legs.left.lower.pitch': 0, 'body.head.roll': 0, 'body.arms.right.lower.roll': -0.453720979521361, 'body.legs.left.foot.roll': -0.03161255787892264, 'body.torso.yaw': -0.17453292519943295, 'body.legs.right.lower.pitch': 0, 'body.legs.right.upper.pitch': 0, 'body.head.pitch': -0.03490658503988659, 'body.arms.left.lower.roll': -0.8551467074800567, 'body.arms.right.upper.pitch': -2.0009831567151233}},

{'time': 1742300898612, 'data': {'body.arms.left.upper.pitch': 0.35521133347722134, 'body.torso.yaw': -0.17453292519943295, 'body.legs.right.foot.roll': 0.03161255787892264, 'body.head.yaw': -0.24434609527920614, 'body.legs.left.foot.roll': -0.03161255787892264, 'body.legs.right.upper.pitch': 0, 'body.head.roll': 0.017453292519943295, 'body.arms.right.lower.roll': -0.26173476180198474, 'body.head.pitch': -0.08726646259971647, 'body.arms.left.lower.roll': -0.8551467074800567, 'body.legs.left.lower.pitch': 0, 'body.legs.left.upper.pitch': 0, 'body.legs.right.lower.pitch': 0, 'body.arms.right.upper.pitch': -2.1231562043547267}},

{'time': 1742300898716, 'data': {'body.arms.right.lower.roll': -0.08720183660255176, 'body.legs.right.lower.pitch': 0, 'body.arms.right.upper.pitch': -2.1929693744344996, 'body.legs.right.foot.roll': 0.03161255787892264, 'body.legs.left.foot.roll': -0.03161255787892264, 'body.arms.left.upper.pitch': 0.37266462599716477, 'body.head.pitch': -0.13962634015954636, 'body.arms.left.lower.roll': -0.8551467074800567, 'body.legs.left.lower.pitch': 0, 'body.torso.yaw': -0.17453292519943295, 'body.head.yaw': -0.4363323129985824, 'body.legs.left.upper.pitch': 0, 'body.legs.right.upper.pitch': 0, 'body.head.roll': 0.017453292519943295}},

{'time': 1742300898820, 'data': {'body.torso.yaw': -0.17453292519943295, 'body.legs.right.lower.pitch': 0, 'body.legs.right.upper.pitch': 0, 'body.arms.left.lower.roll': -0.8551467074800567, 'body.head.yaw': -0.2792526803190927, 'body.legs.left.foot.roll': -0.03161255787892264, 'body.legs.left.lower.pitch': 0, 'body.arms.right.lower.roll': -0.20937488424215478, 'body.legs.left.upper.pitch': 0, 'body.arms.left.upper.pitch': 0.37266462599716477, 'body.head.pitch': -0.12217304763960307, 'body.head.roll': 0.017453292519943295, 'body.arms.right.upper.pitch': -2.14060949687467, 'body.legs.right.foot.roll': 0.03161255787892264}},

{'time': 1742300898905, 'data': {'body.arms.left.lower.roll': -0.8551467074800567, 'body.legs.left.lower.pitch': 0, 'body.arms.left.upper.pitch': 0.37266462599716477, 'body.torso.yaw': -0.17453292519943295, 'body.head.roll': 0.017453292519943295, 'body.arms.right.upper.pitch': -2.0707963267948966, 'body.legs.right.foot.roll': 0.03161255787892264, 'body.arms.right.lower.roll': -0.38390780944158776, 'body.head.yaw': -0.08726646259971647, 'body.legs.right.upper.pitch': 0, 'body.head.pitch': -0.05235987755982988, 'body.legs.left.foot.roll': -0.03161255787892264, 'body.legs.left.upper.pitch': 0, 'body.legs.right.lower.pitch': 0}},

{'time': 1742300899010, 'data': {'body.legs.left.lower.pitch': 0.08726646259971647, 'body.legs.left.foot.roll': -0.03161255787892264, 'body.torso.yaw': -0.15707963267948966, 'body.head.pitch': 0, 'body.head.yaw': 0.06981317007977318, 'body.legs.left.upper.pitch': -0.12217304763960307, 'body.arms.right.lower.roll': -0.6631604897606805, 'body.arms.left.upper.pitch': 0.25049157835756175, 'body.legs.right.lower.pitch': 0.06981317007977318, 'body.arms.right.upper.pitch': -1.913716694115407, 'body.legs.right.upper.pitch': -0.10471975511965977, 'body.arms.left.lower.roll': -0.9424131700797732, 'body.head.roll': 0, 'body.legs.right.foot.roll': 0.03161255787892264}},
]

@inlineCallbacks
def main(session, details):
    movements = perform_movement(session, frames = Jingle_bells, mode="linear", sync=False, force=False)
    yield movements
    yield session.call("rom.optional.behavior.play", name="BlocklyStand")
    session.leave()

wamp = Component(
    transports=[{"url": "ws://wamp.robotsindeklas.nl", "serializers": ["msgpack"], "max_retries": 0}],
    realm="rie.67d942577d4143cdaa821da2",
)

wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])