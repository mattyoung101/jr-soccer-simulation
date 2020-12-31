from fsm import RobotState, StateMachine, FSMState
from utils import move_to_point
from math import sqrt, copysign

CHASE_TO_CIRCLE = 0.4
CIRCLE_TO_CHASE = 0.5
CIRCLE_OFFSET = 0.2
AIM_TO_CIRCLE = 0.5
YEET_TO_AIM = 0.5

class StateAttackChase(FSMState):
    def enter(self, fsm, rs):
        print("Entering attack chase")
    def update(self, fsm, rs):
        rs.out = move_to_point(rs, rs.ball_pos[0], rs.ball_pos[1])
        distance = sqrt(pow(rs.ball_pos[0] - rs.agent_pos[0], 2) + pow(rs.ball_pos[1] - rs.agent_pos[1], 2))
        if distance <= CHASE_TO_CIRCLE:
            fsm.change_state(rs, StateAttackCircle())
    def exit(self, fsm, rs):
        print("Exiting attack chase")

class StateAttackCircle(FSMState):
    def enter(self, fsm, rs):
        print("Entering attack circle")
    def update(self, fsm, rs):
        delta_x = rs.ball_pos[0] - rs.agent_pos[0]
        distance = sqrt(pow(rs.ball_pos[0] - rs.agent_pos[0], 2) + pow(rs.ball_pos[1] - rs.agent_pos[1], 2))
        # Move next to the ball (on the side of the robot) based on which team it is on
        target_x = CIRCLE_OFFSET * copysign(1, delta_x) + rs.ball_pos[0]
        rs.out = move_to_point(rs, target_x, rs.ball_pos[1])
        if rs.out[1] or rs.agent_pos[0] < rs.ball_pos[0]: # need to check if behind ball
            fsm.change_state(rs, StateAttackAim())
            return
        if distance >= CIRCLE_TO_CHASE:
            fsm.change_state(rs, StateAttackChase())
            return
    def exit(self, fsm, rs):
        print("Exiting attack circle")

class StateAttackAim(FSMState):
    def enter(self, fsm, rs):
        print("Entering attack aim")
    def update(self, fsm, rs):
        distance = sqrt(pow(rs.ball_pos[0] - rs.agent_pos[0], 2) + pow(rs.ball_pos[1] - rs.agent_pos[1], 2))
        target_y = rs.ball_pos[1] - CIRCLE_OFFSET
        rs.out = move_to_point(rs, rs.ball_pos[0], target_y)
        if rs.out[1]:
            fsm.change_state(rs, StateAttackYeet())
            return
        if distance >= CIRCLE_TO_CHASE:
            fsm.change_state(rs, StateAttackChase())
            return
    def exit(self, fsm, rs):
        print("Exiting attack aim")

class StateAttackYeet(FSMState):
    def enter(self, fsm, rs):
        print("Entering attack yeet")
    def update(self, fsm, rs):
        distance = sqrt(pow(rs.ball_pos[0] - rs.agent_pos[0], 2) + pow(rs.ball_pos[1] - rs.agent_pos[1], 2))
        rs.out = move_to_point(rs, rs.ball_pos[0], rs.ball_pos[1])
        if distance >= CIRCLE_TO_CHASE or rs.agent_pos[1] > rs.ball_pos[1]:
            fsm.change_state(rs, StateAttackAim())
            return

attack_fsm = StateMachine()