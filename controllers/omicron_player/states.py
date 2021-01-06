from fsm import RobotState, StateMachine, FSMState
from utils import move_to_point, kite_point, sign, log, calc_motors, smallest_angle_between
from math import sqrt, copysign, atan2, pi

# === PARAMETERS === #

# Global
GOAL_DIST = 0.85

# Striker (Attack) FSM
HOVER_DIST = 0.5
HOVER_TO_PUSH = 0.35
BALL_TOO_FAR = 0.3
PUSHER_THRESH = 0.1
BEHIND_THRESH = pi * 5/6

CHASE_TO_CIRCLE = 0.3 # TODO GIVE THESE LESS SHITTY NAMES
CIRCLE_TO_CHASE = 0.4
CIRCLE_OFFSET = 0.15
FORWARD_ANGLE_ENTER = 0.2
FORWARD_ANGLE_EXIT = 1
AIM_TO_CIRCLE = 0.5
YEET_TO_AIM = 0.3

# Goalie (Defend) FSM
IDLE_DIST = 0.2
IDLE_KP = 1.5
SURGE_DIST = 0.25
BALL_TOO_CLOSE = 0.3
BALL_SAFE_DIST = 0.31


# === ATTACK FSM === #

class StateAttackHover(FSMState):
    def enter(self, fsm, rs):
        log("Entering attack hover", rs)
    def update(self, fsm, rs):
        rs.out = move_to_point(rs, HOVER_DIST * (rs.ball_pos[0] / (rs.ball_pos[1] + GOAL_DIST)), HOVER_DIST - GOAL_DIST, True if rs.agent_pos[1] > HOVER_DIST - GOAL_DIST else False)
        distance = sqrt(pow(rs.ball_pos[0] - rs.agent_pos[0], 2) + pow(rs.ball_pos[1] - rs.agent_pos[1], 2))
        if rs.out[1] and distance < HOVER_TO_PUSH:
            fsm.change_state(rs, StateAttackPush())
    def exit(self, fsm, rs):
        log("Exiting attack hover", rs)

class StateAttackPush(FSMState):
    def enter(self, fsm, rs):
        log("Entering attack push", rs)
    def update(self, fsm, rs):
        distance = sqrt(pow(rs.ball_pos[0] - rs.agent_pos[0], 2) + pow(rs.ball_pos[1] - rs.agent_pos[1], 2))
        direction = atan2(rs.ball_pos[1] - rs.agent_pos[1], rs.ball_pos[0] - rs.agent_pos[0])
        rs.out = move_to_point(rs, rs.ball_pos[0], rs.ball_pos[1], False)
        if rs.ball_pos[1] > PUSHER_THRESH or distance > BALL_TOO_FAR:
            fsm.change_state(rs, StateAttackHover())
        if (-BEHIND_THRESH - pi/2) >= direction >= (BEHIND_THRESH - pi/2):
            print("pog")
            fsm.change_state(rs, StateAttackChase())
    def exit(self, fsm, rs):
        log("Exiting attack push", rs)

class StateAttackChase(FSMState):
    def enter(self, fsm, rs):
        log("Entering attack chase", rs)
    def update(self, fsm, rs):
        rs.out = move_to_point(rs, rs.ball_pos[0], rs.ball_pos[1], False)
        distance = sqrt(pow(rs.ball_pos[0] - rs.agent_pos[0], 2) + pow(rs.ball_pos[1] - rs.agent_pos[1], 2))
        if distance <= CHASE_TO_CIRCLE:
            fsm.change_state(rs, StateAttackCircle())
        
        if rs.agent_name[1] == '2' and rs.ball_pos[1] > rs.agent_pos[1]:
            print("pog")
            fsm.change_state(rs, StateAttackPush())
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
        rs.out = move_to_point(rs, rs.ball_pos[0], rs.ball_pos[1], False)
        if distance >= CIRCLE_TO_CHASE or (abs(direction) > FORWARD_ANGLE_EXIT):
            fsm.change_state(rs, StateAttackCircle())
            return
    def exit(self, fsm, rs):
        log("Exiting attack yeet", rs)

attack_fsm = StateMachine()


# === DEFEND FSM === #

class StateDefendIdle(FSMState):
    def enter(self, fsm, rs):
        log("Entering defend idle", rs)
    def update(self, fsm, rs):
        rs.out = move_to_point(rs, 0, IDLE_DIST - GOAL_DIST, False)
        distance = sqrt(pow(rs.ball_pos[0], 2) + pow(rs.ball_pos[1] + (GOAL_DIST - IDLE_DIST), 2))
        if rs.out[1]:
            direction = atan2(rs.ball_pos[1] - rs.agent_pos[1], rs.ball_pos[0] - rs.agent_pos[0])
            error = smallest_angle_between(direction, rs.agent_heading)
            rs.out = [calc_motors(0, IDLE_KP * error), True]
        if distance <= BALL_TOO_CLOSE:
            fsm.change_state(rs, StateDefendSurge())
    def exit(self, fsm, rs):
        log("Exiting defend idle", rs)

class StateDefendSurge(FSMState):
    def enter(self, fsm, rs):
        log("Entering defend surge", rs)
    def update(self, fsm, rs):
        rs.out = move_to_point(rs, rs.ball_pos[0], rs.ball_pos[1], False)
        ball_dist = sqrt(pow(rs.ball_pos[0], 2) + pow(rs.ball_pos[1] + (GOAL_DIST - IDLE_DIST), 2))
        robot_dist = sqrt(pow(rs.agent_pos[0], 2) + pow(rs.agent_pos[1] + (GOAL_DIST - IDLE_DIST), 2))
        if ball_dist >= BALL_SAFE_DIST or robot_dist >= SURGE_DIST:
            fsm.change_state(rs, StateDefendIdle())
    def exit(self, fsm, rs):
        log("Exiting defend surge", rs)

defend_fsm = StateMachine()