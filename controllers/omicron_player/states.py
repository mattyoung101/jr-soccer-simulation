from fsm import RobotState, StateMachine, FSMState
from utils import move_to_point
from math import sqrt, copysign

CHASE_TO_CIRCLE = 0.3
CIRCLE_TO_CHASE = 0.5
CIRCLE_OFFSET = 0.3
AIM_TO_CIRCLE = 0.5
YEET_TO_AIM = 0.5

class StateAttackChase(FSMState):
    def enter(self, fsm, rs):
        print("Entering attack chase")
    def update(self, fsm, rs):
        rs.out = move_to_point(rs.agent_pos[0], rs.agent_pos[1], rs.ball_pos[0], rs.ball_pos[1], rs.agent_heading)
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
        target_x = CIRCLE_OFFSET * copysign(1, delta_x) * (1 if rs.agent_name[0] == 'Y' else -1) + rs.ball_pos[0]
        rs.out = move_to_point(rs.agent_pos[0], rs.agent_pos[1], target_x, rs.ball_pos[1], rs.agent_heading)
        if rs.out[1]: # need to check if behind ball
            fsm.change_state(rs, StateAttackAim())
        if distance >= CIRCLE_TO_CHASE:
            fsm.change_state(rs, StateAttackChase())
    def exit(self, fsm, rs):
        print("Exiting attack circle")

class StateAttackAim(FSMState):
    def enter(self, fsm, rs):
        print("Entering attack aim")
    def update(self, fsm, rs):
        distance = sqrt(pow(rs.ball_pos[0] - rs.agent_pos[0], 2) + pow(rs.ball_pos[1] - rs.agent_pos[1], 2))
        target_y = CIRCLE_OFFSET * (1 if rs.agent_name[0] == 'B' else -1) + rs.ball_pos[1]
        rs.out = move_to_point(rs.agent_pos[0], rs.agent_pos[1], rs.ball_pos[0], target_y, rs.agent_heading)
        if rs.out[1]:
            fsm.change_state()
        if distance >= CIRCLE_TO_CHASE:
            fsm.change_state(rs, StateAttackChase())
    def exit(self, fsm, rs):
        print("Exiting attack aim")

class StateAttackYeet(FSMState):
    def enter(self, fsm, rs):
        print("Entering attack yeet")
    def update(self, fsm, rs):
        rs.out = move_to_point(rs.agent_pos[0], rs.agent_pos[1], rs.ball_pos[0], rs.ball_pos[1], rs.agent_heading)
        if 

attack_fsm = StateMachine()