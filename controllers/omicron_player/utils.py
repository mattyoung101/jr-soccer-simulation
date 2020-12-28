from math import atan2, sqrt, pi

# CONTANTS
WHEEL_RADIUS = 0.02
WHEEL_SPACING = 0.085
MOTOR_MAX_VEL = 10

HEADING_KP = 1.5
ARRIVE_THRESH = 0.05
STOP_THRESH = 0.01

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

def move_to_point(start_x, start_y, end_x, end_y, heading):
    direction = atan2(end_y - start_y, end_x - start_x)
    distance = sqrt(pow(end_x - start_x, 2) + pow(end_y - start_y, 2))
    if distance <= STOP_THRESH:
        return [calc_motors(0, 0), True]
    else:
        error = (heading + direction + pi/2) % (2*pi)
        error = error - 2*pi if error > pi else error
        return [calc_motors(0.2, HEADING_KP * error), True if distance <= ARRIVE_THRESH else False]

