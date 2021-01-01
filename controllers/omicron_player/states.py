from fsm import RobotState, StateMachine, FSMState
from utils import move_to_point, kite_point, sign, log
from math import sqrt, copysign, atan2, pi

GOAL_DIST = 0.85

# TODO GIVE THESE LESS SHITTY NAMES
CHASE_TO_CIRCLE = 0.3
CIRCLE_TO_CHASE = 0.4
CIRCLE_OFFSET = 0.15
FORWARD_ANGLE_ENTER = 0.2
FORWARD_ANGLE_EXIT = 1
AIM_TO_CIRCLE = 0.5
YEET_TO_AIM = 0.3

class StateAttackChase(FSMState):
    def enter(self, fsm, rs):
        log("Entering attack chase", rs)
    def update(self, fsm, rs):
        rs.out = move_to_point(rs, rs.ball_pos[0], rs.ball_pos[1])
        distance = sqrt(pow(rs.ball_pos[0] - rs.agent_pos[0], 2) + pow(rs.ball_pos[1] - rs.agent_pos[1], 2))
        if distance <= CHASE_TO_CIRCLE:
            fsm.change_state(rs, StateAttackCircle())
    def exit(self, fsm, rs):
        log("Exiting attack chase", rs)

class StateAttackCircle(FSMState):
    def enter(self, fsm, rs):
        log("Entering attack circle", rs)
    def update(self, fsm, rs):
        distance = sqrt(pow(rs.ball_pos[0] - rs.agent_pos[0], 2) + pow(rs.ball_pos[1] - rs.agent_pos[1], 2))
        goal_angle = atan2(GOAL_DIST - rs.agent_pos[1], -rs.agent_pos[0])
        direction = atan2(rs.ball_pos[1] - rs.agent_pos[1], rs.ball_pos[0] - rs.agent_pos[0]) - goal_angle
        direction = (direction + pi) % (2*pi) - pi
        # Circle the ball based on which side the robot approaches it
        rs.out = kite_point(rs, rs.ball_pos[0], rs.ball_pos[1], CIRCLE_OFFSET, sign(direction) < 0)
        if (abs(direction) < FORWARD_ANGLE_ENTER):
            fsm.change_state(rs, StateAttackYeet())
            return
        if distance >= CIRCLE_TO_CHASE:
            fsm.change_state(rs, StateAttackChase())
            return
    def exit(self, fsm, rs):
        log("Exiting attack circle", rs)

class StateAttackYeet(FSMState):
    def enter(self, fsm, rs):
        log("Entering attack yeet", rs)
    def update(self, fsm, rs):
        distance = sqrt(pow(rs.ball_pos[0] - rs.agent_pos[0], 2) + pow(rs.ball_pos[1] - rs.agent_pos[1], 2))
        goal_angle = atan2(GOAL_DIST - rs.agent_pos[1], -rs.agent_pos[0])
        direction = atan2(rs.ball_pos[1] - rs.agent_pos[1], rs.ball_pos[0] - rs.agent_pos[0]) - goal_angle
        rs.out = move_to_point(rs, rs.ball_pos[0], rs.ball_pos[1])
        if distance >= CIRCLE_TO_CHASE or (abs(direction) > FORWARD_ANGLE_EXIT):
            fsm.change_state(rs, StateAttackCircle())
            return
    def exit(self, fsm, rs):
        log("Exiting attack yeet", rs)

attack_fsm = StateMachine()