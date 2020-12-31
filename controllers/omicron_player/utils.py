from math import atan2, sqrt, pi
from fsm import RobotState

# CONTANTS
WHEEL_RADIUS = 0.02
WHEEL_SPACING = 0.085
MOTOR_MAX_VEL = 10

MOVE_SPEED = 0.2

HEADING_KP = 1.5
ARRIVE_THRESH = 0.05
STOP_THRESH = 0.01

KITE_RADIUS_KP = 5
KITE_HEADING_KP = 2

def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

# Calculates the speed to run motors given a movement and rotation speed
# Returns motor values in the format [left, right]
def calc_motors(speed, rotation):
    centre_wheel = speed / WHEEL_RADIUS
    if not rotation:
        return [centre_wheel, centre_wheel]
    elif not speed:
        wheel_speed = (WHEEL_SPACING * rotation) / WHEEL_RADIUS
        return [-wheel_speed, wheel_speed] if rotation > 0 else [wheel_speed, -wheel_speed]
    else:
        turning_radius = speed / abs(rotation)
        outer_wheel = centre_wheel * ((0.5 * turning_radius + WHEEL_SPACING) / (0.5 * turning_radius))
        inner_wheel = centre_wheel * ((0.5 * turning_radius - WHEEL_SPACING) / (0.5 * turning_radius))
        if outer_wheel > MOTOR_MAX_VEL:
            # print("MOTOR OUTPUT SATURATED")
            inner_wheel /= outer_wheel / MOTOR_MAX_VEL
            outer_wheel = MOTOR_MAX_VEL
        # print(f"turning: {turning_radius}, outer: {outer_wheel}, inner: {inner_wheel}")
        return [outer_wheel, inner_wheel] if rotation < 0 else [inner_wheel, outer_wheel]

def move_to_point(rs: RobotState, end_x, end_y):
    direction = atan2(end_y - rs.agent_pos[1], end_x - rs.agent_pos[0])
    distance = sqrt(pow(end_x - rs.agent_pos[0], 2) + pow(end_y - rs.agent_pos[1], 2))
    if distance <= STOP_THRESH:
        return [calc_motors(0, 0), True]
    else:
        error = (rs.agent_heading - direction) % (2*pi)
        error = error - 2*pi if error > pi else error
        # print(f"Direction: {direction}, Heading: {heading}, Error: {error}")
        return [calc_motors(MOVE_SPEED, HEADING_KP * error), True if distance <= ARRIVE_THRESH else False]

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

    # print(direction, bot_heading, heading_error)
    print(heading_error, distance_error)

    if abs(heading_error) > pi/2:
        print("pog1")
        return [calc_motors(MOVE_SPEED, HEADING_KP * heading_error), False]
    else:
        print("pog2")
        return [calc_motors(MOVE_SPEED, -reverse * KITE_RADIUS_KP * distance_error + KITE_HEADING_KP * heading_error), False]


