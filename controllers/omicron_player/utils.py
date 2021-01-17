from math import atan2, sqrt, pi, copysign, ceil
from fsm import RobotState
import time
import random

# true if logging should be enabled (probably disable in comp)
DEBUG = True
# true if inter-process communication between robots is allowed
IPC_ENABLED = True
IPC_PORT = 42708

# CONTANTS
WHEEL_RADIUS = 0.02
WHEEL_SPACING = 0.085
MOTOR_MAX_VEL = 10
DIAGONAL = 1.8 # field diagonal, calculated by hand :)

MOVE_SPEED = 0.2

HEADING_KP = 1.5
ARRIVE_THRESH = 0.05
STOP_THRESH = 0.01

KITE_RADIUS_KP = 10
KITE_HEADING_KP = 1.5
KITE_THRESH = 0.05

def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

def sign(val):
    return copysign(1, val)

def smallest_angle_between(angle1, angle2):
    return (angle1 - angle2 + pi) % (2*pi) - pi

def log(string, rs: RobotState):
    if DEBUG:
        print(f"{rs.agent_name}: {string}")

def predict_time_func(ball_dist):
    """Used for choosing how long to predict for in the goalie. ball_dist between 0 and 1.8, out between 0ms and 1024ms."""
    # https://www.desmos.com/calculator/o8cl5z537b
    return min(1500 * sqrt(ball_dist), 2048)

# https://stackoverflow.com/a/26454777/5007892
def round_nearest(x, to):
    return int(ceil(x / to)) * to

def ipc_generate_port():
    """Generates a unique port for IPC since, because we can't close the port (we don't know when the controller is quit),
    we could ger refused access to a static port. Note: this can fail if timing is unfortunate, but should be very rare."""
    curtime = round_nearest(time.time(), 5.0)
    return random.Random(curtime).randint(20_000, 45_000)

# Calculates the speed to run motors given a movement and rotation speed
# Returns motor values in the format [left, right]
def calc_motors(speed, rotation):
    centre_wheel = speed / WHEEL_RADIUS
    if not rotation:
        return [centre_wheel, centre_wheel]
    elif not speed:
        wheel_speed = constrain((WHEEL_SPACING * rotation) / WHEEL_RADIUS, -10, 10)
        return [wheel_speed, -wheel_speed]
    else:
        turning_radius = abs(speed/rotation)
        outer_wheel = abs(centre_wheel) * ((0.5 * turning_radius + WHEEL_SPACING) / (0.5 * turning_radius))
        inner_wheel = abs(centre_wheel) * ((0.5 * turning_radius - WHEEL_SPACING) / (0.5 * turning_radius))
        if abs(outer_wheel) > MOTOR_MAX_VEL:
            # print("MOTOR OUTPUT SATURATED")
            inner_wheel /= outer_wheel / MOTOR_MAX_VEL
            outer_wheel = MOTOR_MAX_VEL
        # print(f"turning: {turning_radius}, outer: {outer_wheel}, inner: {inner_wheel}")
        if sign(speed) == -1:
            return [-outer_wheel, -inner_wheel] if rotation > 0 else [-inner_wheel, -outer_wheel]
        else:
            return [outer_wheel, inner_wheel] if rotation < 0 else [inner_wheel, outer_wheel]

def move_to_point(rs: RobotState, end_x, end_y, reverse):
    direction = atan2(end_y - rs.agent_pos[1], end_x - rs.agent_pos[0])
    distance = sqrt(pow(end_x - rs.agent_pos[0], 2) + pow(end_y - rs.agent_pos[1], 2))
    if distance <= STOP_THRESH:
        return [calc_motors(0, 0), True]
    else:
        error = (rs.agent_heading - direction + (pi if reverse else 0)) % (2*pi)
        error = error - 2*pi if error > pi else error
        # print(f"Direction: {direction}, Heading: {rs.agent_heading}, Error: {error}")
        return [calc_motors(-MOVE_SPEED if reverse else MOVE_SPEED, HEADING_KP * error), True if distance <= ARRIVE_THRESH else False]

def kite_point(rs: RobotState, centre_x, centre_y, radius, reversed):
    reverse = 1 if reversed else -1

    direction = ((5*pi)/2 - atan2(centre_y - rs.agent_pos[1], centre_x - rs.agent_pos[0])) % (2*pi)
    direction = direction - 2*pi if direction > pi else direction

    bot_heading = ((5*pi)/2 - rs.agent_heading) % (2*pi)
    bot_heading = bot_heading - 2*pi if bot_heading > pi else bot_heading

    distance = sqrt(pow(centre_x - rs.agent_pos[0], 2) + pow(centre_y - rs.agent_pos[1], 2))

    heading_error = (direction + pi/2 * reverse) - bot_heading
    heading_error = heading_error - 2*reverse*pi if abs(heading_error) > pi else heading_error

    distance_error = distance - radius

    if abs(heading_error) > pi/2:
        return [calc_motors(MOVE_SPEED, HEADING_KP * heading_error), True if distance_error < KITE_THRESH else False]
    else:
        return [calc_motors(MOVE_SPEED, -reverse * KITE_RADIUS_KP * distance_error + KITE_HEADING_KP * heading_error), 
                True if distance_error < KITE_THRESH else False]


def predict_object(current_pos, velocity, millis):
    """Predicts the given object num_ticks into the future.

    Args:
        current_pos (list): current x,y position of object
        velocity (list): current velocity (x,y velocity) of object 
        millis (int): number of simulator milliseconds to predict into future (should be multiple of 32)

    Returns:
        list: predicted x,y position of object num_millis into the future
    """
    new_offset = [velocity[0] * millis, velocity[1] * millis]
    # dispatch new position
    return [current_pos[0] + new_offset[0], current_pos[1] + new_offset[1]]