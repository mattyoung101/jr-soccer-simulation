"""
Agent for RoboCup Jr 2021 Simulation project.
Copyright (c) 2020 Team Omicron (Ethan Lo, Matt Young, James Talkington).
Based on the rcj_soccer_player controller that ships with the simulator.
"""
import math

from rcj_soccer_robot import RCJSoccerRobot, TIME_STEP
import fsm
import states
import utils
from fsm import RobotState, StateMachine

class OmicronAgent(RCJSoccerRobot):
    def setup(self):
        # TODO consider moving this to an __init__ constructor?
        self.rs = RobotState()
        self.rs.agent_name = self.name
        self.rs.agent_id = self.player_id
        self.attack_fsm = StateMachine()
        self.defend_fsm = StateMachine()

        # setup our state machines
        if self.player_id == 1:
            self.attack_fsm.change_state(self.rs, states.StateAttackChase())
        elif self.player_id == 2:
            self.attack_fsm.change_state(self.rs, states.StateAttackHover())
        elif self.player_id == 3:
            self.defend_fsm.change_state(self.rs, states.StateDefendIdle())

    def run(self):
        while self.robot.step(TIME_STEP) != -1:
            if self.is_new_data():
                data = self.get_new_data()

                # Update RobotState
                # Why are these coordinates so messed, it's cartesian coordinates from the underside of the field???
                self.rs.agent_pos = [-data[self.name.upper()]['y'], -data[self.name.upper()]['x']]
                self.rs.ball_pos = [-data['ball']['y'], -data['ball']['x']]
                self.rs.agent_heading = data[self.name.upper()]['orientation']

                # Update state machine
                if self.rs.agent_id in [1, 2]:
                    self.attack_fsm.update(self.rs)
                elif self.rs.agent_id == 3:
                    self.defend_fsm.update(self.rs)
                
                # Update motors
                self.left_motor.setVelocity(self.rs.out[0][0])
                self.right_motor.setVelocity(self.rs.out[0][1])


omicron_agent = OmicronAgent()
omicron_agent.setup()
omicron_agent.run()
