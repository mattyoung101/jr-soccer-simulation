from fsm import RobotState, StateMachine, FSMState
from utils import move_to_point
from math import sqrt

ORBIT_DIST_MIN = 0.3
ORBIT_DIST_MAX = 0.5

class StateAttackChase(FSMState):
    def enter(self, fsm, rs):
        print("Entering attack chase")
    def update(self, fsm, rs):
        rs.out = move_to_point(rs.agent_pos[0], rs.agent_pos[1], rs.ball_pos[0], rs.ball_pos[1], rs.agent_heading)
        distance = sqrt(pow(rs.ball_pos[0] - rs.agent_pos[0], 2) + pow(rs.ball_pos[1] - rs.agent_pos[1], 2))
    def exit(self, fsm, rs):
        print("Exiting attack chase")

class StateAttackCircle(FSMState):
    def enter(self, fsm, rs):
        print("Entering attack circle")
    def update(self, fsm, rs):
        delta_x = rs.ball_pos[0] - rs.agent_pos[0]
        delta_y = rs.ball_pos[1] - rs.agent_pos[1]
        # my brain ded imma come back to this
    def exit(self, fsm, rs):
        print("Exiting attack circle")

attack_fsm = StateMachine()