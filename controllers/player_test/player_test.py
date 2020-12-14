"""rcj_soccer_player controller."""
from controller import Robot
import struct
import math
import utils

TIME_STEP = 64
ROBOT_NAMES = ["B1", "B2", "B3", "Y1", "Y2", "Y3"]
N_ROBOTS = len(ROBOT_NAMES)


def parse_supervisor_msg(packet: str) -> dict:
    # X, Z and rotation for each robot
    # plus X and Z for ball
    struct_fmt = 'ddd' * 6 + 'dd'

    unpacked = struct.unpack(struct_fmt, packet)

    data = {}
    for i, r in enumerate(ROBOT_NAMES):
        data[r] = {
            "x": unpacked[3 * i],
            "y": unpacked[3 * i + 1],
            "orientation": unpacked[3 * i + 2]
        }
    data["ball"] = {
        "x": unpacked[3 * N_ROBOTS],
        "y": unpacked[3 * N_ROBOTS + 1]
    }
    return data

# Create robot instance
robot = Robot()

name = robot.getName()
team = name[0]
player_id = int(name[1])


receiver = robot.getReceiver("receiver")
receiver.enable(TIME_STEP)

left_motor = robot.getMotor("left wheel motor")
right_motor = robot.getMotor("right wheel motor")

left_motor.setPosition(float('+inf'))
right_motor.setPosition(float('+inf'))

left_motor.setVelocity(0.0)
right_motor.setVelocity(0.0)


prev_angle = 0

while robot.step(TIME_STEP) != -1:
    if receiver.getQueueLength() > 0:
        packet = receiver.getData()
        receiver.nextPacket()

        data = parse_supervisor_msg(packet)

        # Move only the B1 robot -- everyone else stay still
        # if name.upper() != 'B1':
        #     continue

        # Get the position of our robot
        robot_pos = data[name.upper()]
        # Get the position of the ball
        ball_pos = data['ball']

        robot_angle = robot_pos['orientation']

        speeds = utils.move_to_point(robot_pos['x'], robot_pos['y'], ball_pos['x'], ball_pos['y'], robot_angle)
        
        left_motor.setVelocity(speeds[0])
        right_motor.setVelocity(speeds[1])