from math import atan2, sqrt, pi

class Predictor:
    """
    The predictor records velocities of simulation objects to extrapolate their positions in the future.
    """

    def __init__(self, initial_pos):
        self.last_pos = initial_pos # x,y
        self.last_displacement = [0, 0] # delta x, delta y
        self.last_time = 0 # scalar
        pass

    def add_measurement(self, current_pos, current_time):
        #dist = sqrt((current_pos[0] - self.last_pos[0]) ** 2 + (current_pos[1] - self.last_pos[1]) ** 2)
        
        pass