# This file is part of Team Omicron in RoboCup Jr 2021 Soccer Simulation.
# Copyright (c) 2021 Ethan Lo & Matt Young. All rights reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from math import atan2, sqrt, pi

class Predictor:
    """
    The predictor records velocities of a simulation object to extrapolate its position in the future.
    """
    def __init__(self):
        self.last_pos = [0, 0] # x,y
        self.last_delta = [0, 0] # delta x, delta y
        self.last_time = 0 # scalar
        self.last_velocity = [0, 0] # not currently used but recorded anyway
        self.has_set_initial = False # for setting the initial position so we don't get weird values on first call

    def set_initial_pos(self, current_pos):
        if not self.has_set_initial:
            print("Predictor is setting initial robot position")
            self.last_pos = current_pos
            self.has_set_initial = True

    def push_measurement(self, current_pos, current_time):
        """Push position data to the predictor. In exchange, you get velocity measurements back.

        Args:
            current_pos (list): x,y position of robot
            current_time (int): current game tick

        Returns:
            list: x velocity and y velocity of object
        """
        delta_pos = [current_pos[0] - self.last_pos[0], current_pos[1] - self.last_pos[1]]
        delta_t = current_time - self.last_time
        velocity = [delta_pos[0] / delta_t, delta_pos[1] / delta_t]
        # update our internal state for the next call
        self.last_pos = current_pos
        self.last_time = current_time
        self.last_delta = delta_pos
        self.last_velocity = velocity
        return velocity