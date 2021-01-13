# This file is part of Team Omicron's RoboCup Jr simulation league agent.
# Copyright (c) 2020 Team Omicron (Ethan Lo, Matt Young, James Talkington).
# 
# Based on the rcj_soccer_player controller that ships with the simulator.

import math

from rcj_soccer_robot import RCJSoccerRobot, TIME_STEP
import fsm
import states
import utils
from fsm import RobotState, StateMachine

class OmicronAgent(RCJSoccerRobot):
    def setup(self):
        # TODO consider moving this to an __init__ constructor? will it work?
        self.rs = RobotState()
        self.rs.agent_name = self.name
        self.rs.agent_id = self.player_id
        self.attack_fsm = StateMachine()
        self.mid_fsm = StateMachine()
        self.defend_fsm = StateMachine()

        # setup our state machines
        if self.player_id == 3:
            # self.attack_fsm.change_state(self.rs, states.StateAttackChase())
            print(None)
        elif self.player_id == 2:
            self.mid_fsm.change_state(self.rs, states.StateMidHover())
        elif self.player_id == 1:
            # self.defend_fsm.change_state(self.rs, states.StateDefendHover())
            print(None)

    def run(self):
        while self.robot.step(TIME_STEP) != -1:
            if self.is_new_data():
                data = self.get_new_data()

                # Update RobotState
                # Why are these coordinates so messed, it's cartesian coordinates from the underside of the field???
                self.rs.agent_pos = [-data[self.name.upper()]['y'], -data[self.name.upper()]['x']]
                self.rs.ball_pos = [-data['ball']['y'], -data['ball']['x']]
                self.rs.agent_heading = data[self.name.upper()]['orientation']
                # NOTE: according to my reading of the docs, on all our controllers, the synchronization field is set
                # to TRUE, which means that robot.step(TIME_STEP) always returns zero (not delta time), so I assume
                # that means it always elapses by that time (although I am not sure!)
                # docs ref: https://cyberbotics.com/doc/reference/robot#wb_robot_step
                self.rs.simulation_time += TIME_STEP
                # note that this will only be called if the initial position has not yet been set in the predictor
                self.rs.ball_predictor.set_initial_pos(self.rs.agent_pos)

                # Update state machine
                if self.rs.agent_id == 3:
                    # self.attack_fsm.update(self.rs)
                    print(None)
                elif self.rs.agent_id == 2:
                    self.mid_fsm.update(self.rs)
                elif self.rs.agent_id == 1:
                    # self.defend_fsm.update(self.rs)
                    print(None)
                
                # Update motors
                self.left_motor.setVelocity(self.rs.out[0][0])
                self.right_motor.setVelocity(self.rs.out[0][1])

omicron_agent = OmicronAgent()
omicron_agent.setup()
omicron_agent.run()
