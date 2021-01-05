"""
Agent for RoboCup Jr 2021 Simulation project.
Copyright (c) 2020 Team Omicron (Ethan Lo, Matt Young, James Talkington).
"""
from controller import Robot
import struct
import math
import utils
import fsm
import states

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


rs = fsm.RobotState()
rs.agent_name = name

if rs.agent_name[1] == '1':
    states.attack_fsm.change_state(rs, states.StateAttackChase())
elif rs.agent_name[1] == '2':
    states.attack_fsm.change_state(rs, states.StateAttackHover())
elif rs.agent_name[1] == '3':
    states.defend_fsm.change_state(rs, states.StateDefendIdle())

while robot.step(TIME_STEP) != -1:
    # Supervisor comms stuff
    if receiver.getQueueLength() > 0:
        packet = receiver.getData()
        receiver.nextPacket()

        data = parse_supervisor_msg(packet)

        # if name.upper() != 'B3':
        #     continue

        # Update RobotState
        # Why are these coordinates so messed, it's cartesian coordinates from the underside of the field???
        rs.agent_pos = [-data[name.upper()]['y'], -data[name.upper()]['x']]
        rs.ball_pos = [-data['ball']['y'], -data['ball']['x']]
        rs.agent_heading = data[name.upper()]['orientation']

        # Update state machine
        if rs.agent_name[1] in ['1', '2']:
            states.attack_fsm.update(rs)
        elif rs.agent_name[1] == '3':
            states.defend_fsm.update(rs)
        
        # Update motors
        left_motor.setVelocity(rs.out[0][0])
        right_motor.setVelocity(rs.out[0][1])
