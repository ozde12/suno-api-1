import os
import random
from typing import List, Dict
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.component import Component, run
from alpha_mini_rug import perform_movement  # Import movement function

# Define a time scaling factor
delta_t = 1500

# Define dance moves using the correct format
dance_moves: Dict[str, List[Dict]] = {
    "intro_moves": [
        {"time": 0.5 * delta_t, "data": {
            "body.head.yaw": 0.5,  
            "body.arms.right.upper.pitch": -1.0,
            "body.arms.left.upper.pitch": -1.0,
            "body.torso.yaw": 0.3,
            "body.legs.right.lower.pitch": 0.0,
            "body.legs.left.lower.pitch": 0.0,
        }},
        {"time": 1.0 * delta_t, "data": {
            "body.head.yaw": 0.0,  
            "body.arms.right.upper.pitch": 0.0,
            "body.arms.left.upper.pitch": 0.0,
            "body.torso.yaw": 0.0,
            "body.legs.right.lower.pitch": 0.0,
            "body.legs.left.lower.pitch": 0.0,
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
        }},
        {"time": 1 * delta_t, "data": {
            "body.arms.right.upper.pitch": 0.0,
            "body.arms.left.upper.pitch": 0.0,
            "body.legs.right.lower.pitch": 0.0,
            "body.legs.left.lower.pitch": 0.0,
            "body.head.yaw": 0.0,
            "body.torso.yaw": 0.0,
        }},
    ],
    "chorus_moves": [
        {"time": 0.5 * delta_t, "data": {
            "body.arms.right.upper.pitch": -1.5,
            "body.arms.left.upper.pitch": 1.5,
            "body.legs.right.lower.pitch": 0.1,
            "body.legs.left.lower.pitch": -0.1,
            "body.torso.yaw": 0.5,
            "body.head.yaw": 0.0,
        }},
        {"time": 1 * delta_t, "data": {
            "body.arms.right.upper.pitch": 0.0,
            "body.arms.left.upper.pitch": 0.0,
            "body.legs.right.lower.pitch": 0.0,
            "body.legs.left.lower.pitch": 0.0,
            "body.torso.yaw": 0.0,
            "body.head.yaw": 0.0,
        }},
    ],
    "bridge_moves": [
        {"time": 0.5 * delta_t, "data": {
            "body.torso.yaw": 0.7,
            "body.legs.right.lower.pitch": 0.2,
            "body.legs.left.lower.pitch": -0.2,
            "body.arms.right.upper.pitch": -0.3,
            "body.arms.left.upper.pitch": 0.6,
            "body.head.yaw": 0.0,
        }},
        {"time": 1 * delta_t, "data": {
            "body.torso.yaw": 0.0,
            "body.legs.right.lower.pitch": 0.0,
            "body.legs.left.lower.pitch": 0.0,
            "body.arms.right.upper.pitch": 0.0,
            "body.arms.left.upper.pitch": 0.0,
            "body.head.yaw": 0.0,
        }},
    ]
}

@inlineCallbacks
def execute_moves(session):
    """Executes predefined dance moves using the perform_movement function."""
    for move_name, frames in dance_moves.items():
        print(f"Executing {move_name}...")
        try:
            for frame in frames:
                print(f"Sending frame: {frame}")  # Debugging print
            yield perform_movement(session, frames=frames)
            print(f"{move_name} executed successfully!\n")
        except Exception as e:
            print(f"Error executing {move_name}: {e}\n")
            import traceback
            traceback.print_exc()  # Print full error details

@inlineCallbacks
def main(session, details):
    """Main function that runs when the WAMP session joins."""
    print("Connected to WAMP session!")
    
    # Play a default behavior
    yield session.call("rom.optional.behavior.play", name="BlocklyStand")

    # Execute the dance moves
    yield execute_moves(session)

# Define the WAMP component
wamp = Component(
    transports=[{
        "url": "ws://wamp.robotsindeklas.nl",
        "serializers": ["msgpack"],
        "max_retries": 0
    }],
    realm="rie.67e141ca540602623a34e03f",
)

# Register main function to execute when WAMP connects
wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])
