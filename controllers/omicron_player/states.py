# Contains implementation of FSM code
from fsm import RobotState, StateMachine, FSMState
from utils import move_to_point, kite_point, sign, log, calc_motors, smallest_angle_between, predict_object, predict_time_func
from math import sqrt, copysign, atan2, pi

# === PARAMETERS === #

# Global
GOAL_DIST = 0.85

# Striker (Attack) FSM
HOVER_DIST = 0.75
HOVER_TO_PUSH = 1
BALL_TOO_FAR = 1.2
PUSHER_THRESH = 0.1
BEHIND_THRESH = 0.6
SIDE_THRESH = 0.5

CHASE_TO_CIRCLE = 0.25 # TODO GIVE THESE LESS SHITTY NAMES
CIRCLE_TO_CHASE = 0.3
CIRCLE_OFFSET = 0.1
FORWARD_ANGLE_ENTER = 0.4
FORWARD_ANGLE_EXIT = 0.8
AIM_TO_CIRCLE = 0.5
YEET_TO_AIM = 0.3

# Midfielder (Mid) specific
MID_ANGLE_ENTER = 0.4
MID_ANGLE_EXIT = 1
BALL_VEL_THRESH = 0.002

# Goalie (Defend) FSM
IDLE_DIST = 0.3
SURGE_THRESH = 0.45
SURGE_DIST = 0.5
BALL_SAFE_DIST = 0.5


# === ATTACK FSM === #

class StateAttackKickoff(FSMState):
    def enter(self, fsm, rs):
        log("Entering attack kickoff", rs)
    
    def update(self, fsm, rs):
        rs.out = move_to_point(rs, rs.ball_pos[0], rs.ball_pos[1], False)
        if rs.simulation_time > 3008:
            fsm.change_state(rs, StateAttackChase())
            return
    
    def exit(self, rsm, rs):
        log("Exiting attack kickoff", rs)


class StateAttackChase(FSMState):
    def enter(self, fsm, rs):
        log("Entering attack chase", rs)

    def update(self, fsm, rs):
        ball_vel = rs.ball_predictor.push_measurement(rs.ball_pos, rs.simulation_time)
        ball_dist = sqrt(pow(rs.agent_pos[0] - rs.ball_pos[0], 2) + pow(rs.agent_pos[1] - rs.ball_pos[1], 2))
        predict_time = predict_time_func(ball_dist)
        predicted_ball = predict_object(rs.ball_pos, ball_vel, predict_time)

        rs.out = move_to_point(rs, rs.ball_pos[0], rs.ball_pos[1], False)
        if ball_dist <= CHASE_TO_CIRCLE:
            fsm.change_state(rs, StateAttackCircle())
            return

    def exit(self, fsm, rs):
        log("Exiting attack chase", rs)

class StateAttackCircle(FSMState):
    def enter(self, fsm, rs):
        log("Entering attack circle", rs)

    def update(self, fsm, rs):
        ball_vel = rs.ball_predictor.push_measurement(rs.ball_pos, rs.simulation_time)
        ball_dist = sqrt(pow(rs.agent_pos[0] - rs.ball_pos[0], 2) + pow(rs.agent_pos[1] - rs.ball_pos[1], 2))
        predict_time = predict_time_func(ball_dist)
        predicted_ball = predict_object(rs.ball_pos, ball_vel, predict_time)

        goal_angle = atan2(GOAL_DIST - rs.agent_pos[1], -rs.agent_pos[0])
        direction = atan2(rs.ball_pos[1] - rs.agent_pos[1], rs.ball_pos[0] - rs.agent_pos[0]) - goal_angle
        direction = (direction + pi) % (2*pi) - pi
        # Circle the ball based on which side the robot approaches it
        rs.out = kite_point(rs, predicted_ball[0], predicted_ball[1], CIRCLE_OFFSET, sign(direction) < 0) 
        if (abs(direction) < FORWARD_ANGLE_ENTER):
            fsm.change_state(rs, StateAttackYeet())
            return
        if ball_dist >= CIRCLE_TO_CHASE:
            fsm.change_state(rs, StateAttackChase())
            return

    def exit(self, fsm, rs):
        log("Exiting attack circle", rs)

class StateAttackYeet(FSMState):
    def enter(self, fsm, rs):
        log("Entering attack yeet", rs)

    def update(self, fsm, rs):
        ball_vel = rs.ball_predictor.push_measurement(rs.ball_pos, rs.simulation_time)
        ball_dist = sqrt(pow(rs.agent_pos[0] - rs.ball_pos[0], 2) + pow(rs.agent_pos[1] - rs.ball_pos[1], 2))
        predict_time = predict_time_func(ball_dist)
        predicted_ball = predict_object(rs.ball_pos, ball_vel, predict_time)

        goal_angle = atan2(GOAL_DIST - rs.agent_pos[1], -rs.agent_pos[0])
        direction = atan2(rs.ball_pos[1] - rs.agent_pos[1], rs.ball_pos[0] - rs.agent_pos[0]) - goal_angle
        rs.out = move_to_point(rs, predicted_ball[0], predicted_ball[1], False)
        if ball_dist >= CIRCLE_TO_CHASE or (abs(direction) > FORWARD_ANGLE_EXIT):
            fsm.change_state(rs, StateAttackCircle())
            return

    def exit(self, fsm, rs):
        log("Exiting attack yeet", rs)


# === MID FSM === #
class StateMidIdle(FSMState):
    def enter(self, fsm, rs):
        log("Entering mid idle", rs)

    def update(self, fsm, rs):
        ball_vel = rs.ball_predictor.push_measurement(rs.ball_pos, rs.simulation_time)
        ball_dist = sqrt(pow(rs.agent_pos[0] - rs.ball_pos[0], 2) + pow(rs.agent_pos[1] - rs.ball_pos[1], 2))
        predict_time = predict_time_func(ball_dist)
        predicted_ball = predict_object(rs.ball_pos, ball_vel, predict_time)

        mag = sqrt(pow(rs.ball_pos[0], 2) + pow(rs.ball_pos[1], 2))
        rs.out = move_to_point(rs, 0.2*(predicted_ball[0]/mag), 0.2*(predicted_ball[1]/mag), False)
        if abs(rs.ball_pos[0]) < SIDE_THRESH and rs.ball_pos[1] > BEHIND_THRESH - GOAL_DIST:
            fsm.change_state(rs, StateMidHover())
            return

    def exit(self, fsm, rs):
        log("Exiting mid idle", rs)

class StateMidHover(FSMState):
    def enter(self, fsm, rs):
        log("Entering mid hover", rs)

    def update(self, fsm, rs):
        # update ball predictions
        ball_vel = rs.ball_predictor.push_measurement(rs.ball_pos, rs.simulation_time)
        ball_dist = sqrt(pow(rs.agent_pos[0] - rs.ball_pos[0], 2) + pow(rs.agent_pos[1] - rs.ball_pos[1], 2))
        predict_time = predict_time_func(ball_dist)
        predicted_ball = predict_object(rs.ball_pos, ball_vel, predict_time)
        # print(f"Ball prediction for {predict_time} ticks: {predicted_ball}")

        ball_speed = sqrt(pow(ball_vel[0], 2) + pow(ball_vel[1], 2))
        rs.out = move_to_point(rs, HOVER_DIST * (rs.ball_pos[0] / (rs.ball_pos[1] + GOAL_DIST)), HOVER_DIST - GOAL_DIST, False)
        distance = predicted_ball[1] + GOAL_DIST
        if abs(rs.ball_pos[0]) > SIDE_THRESH or rs.ball_pos[1] < BEHIND_THRESH - GOAL_DIST:
            fsm.change_state(rs, StateMidIdle())
            return
        if distance < HOVER_TO_PUSH or distance < BEHIND_THRESH:
            if ball_speed < BALL_VEL_THRESH:
                fsm.change_state(rs, StateMidChase())
            else:
                fsm.change_state(rs, StateMidPush())
            return

    def exit(self, fsm, rs):
        log("Exiting mid hover", rs)

class StateMidPush(FSMState):
    def enter(self, fsm, rs):
        log("Entering mid push", rs)
    
    def update(self, fsm, rs):
        ball_vel = rs.ball_predictor.push_measurement(rs.ball_pos, rs.simulation_time)
        ball_dist = sqrt(pow(rs.agent_pos[0] - rs.ball_pos[0], 2) + pow(rs.agent_pos[1] - rs.ball_pos[1], 2))
        predict_time = predict_time_func(ball_dist)
        predicted_ball = predict_object(rs.ball_pos, ball_vel, predict_time)

        rs.out = move_to_point(rs, predicted_ball[0], predicted_ball[1], False)
        if abs(rs.ball_pos[0]) > SIDE_THRESH or rs.ball_pos[1] < BEHIND_THRESH - GOAL_DIST:
            fsm.change_state(rs, StateMidIdle())
            return
        if rs.ball_pos[1] < BEHIND_THRESH - GOAL_DIST:
            fsm.change_state(rs, StateMidHover())
            return
    
    def exit(self, fsm, rs):
        log("Exiting mid push", rs)

class StateMidChase(FSMState):
    def enter(self, fsm, rs):
        log("Entering mid chase", rs)

    def update(self, fsm, rs):
        # update ball predictions
        ball_vel = rs.ball_predictor.push_measurement(rs.ball_pos, rs.simulation_time)
        ball_dist = sqrt(pow(rs.agent_pos[0] - rs.ball_pos[0], 2) + pow(rs.agent_pos[1] - rs.ball_pos[1], 2))
        predict_time = predict_time_func(ball_dist)
        predicted_ball = predict_object(rs.ball_pos, ball_vel, predict_time)
        # print(f"Ball prediction for {predict_time} ticks: {predicted_ball}")

        rs.out = move_to_point(rs, predicted_ball[0], predicted_ball[1], False)
        distance = sqrt(pow(rs.ball_pos[0] - rs.agent_pos[0], 2) + pow(rs.ball_pos[1] - rs.agent_pos[1], 2))
        if abs(rs.ball_pos[0]) > SIDE_THRESH or rs.ball_pos[1] < BEHIND_THRESH - GOAL_DIST:
            fsm.change_state(rs, StateMidIdle())
            return
        if distance <= CHASE_TO_CIRCLE:
            fsm.change_state(rs, StateMidCircle())
            return
        if rs.ball_pos[1] < BEHIND_THRESH - GOAL_DIST:
            fsm.change_state(rs, StateMidHover())
            return

    def exit(self, fsm, rs):
        log("Exiting mid chase", rs)

class StateMidCircle(FSMState):
    def enter(self, fsm, rs):
        log("Entering mid circle", rs)

    def update(self, fsm, rs):
        distance = sqrt(pow(rs.ball_pos[0] - rs.agent_pos[0], 2) + pow(rs.ball_pos[1] - rs.agent_pos[1], 2))
        direction = atan2(rs.ball_pos[1] - rs.agent_pos[1], rs.ball_pos[0] - rs.agent_pos[0]) - pi/2
        direction = (direction + pi) % (2*pi) - pi
        # Circle the ball based on which side the robot approaches it
        rs.out = kite_point(rs, rs.ball_pos[0], rs.ball_pos[1], CIRCLE_OFFSET, sign(direction) < 0) 
        if abs(rs.ball_pos[0]) > SIDE_THRESH or rs.ball_pos[1] < BEHIND_THRESH - GOAL_DIST:
            fsm.change_state(rs, StateMidIdle())
            return
        if (abs(direction) < MID_ANGLE_ENTER):
            fsm.change_state(rs, StateMidYeet())
            return
        if distance >= CIRCLE_TO_CHASE:
            fsm.change_state(rs, StateMidChase())
            return
        
        if rs.ball_pos[1] > BALL_TOO_FAR - GOAL_DIST:
            fsm.change_state(rs, StateMidHover())
            return

    def exit(self, fsm, rs):
        log("Exiting mid circle", rs)

class StateMidYeet(FSMState):
    def enter(self, fsm, rs):
        log("Entering mid yeet", rs)

    def update(self, fsm, rs):
        distance = sqrt(pow(rs.ball_pos[0] - rs.agent_pos[0], 2) + pow(rs.ball_pos[1] - rs.agent_pos[1], 2))
        direction = atan2(rs.ball_pos[1] - rs.agent_pos[1], rs.ball_pos[0] - rs.agent_pos[0]) - pi/2
        rs.out = move_to_point(rs, rs.ball_pos[0], rs.ball_pos[1], False)
        if abs(rs.ball_pos[0]) > SIDE_THRESH or rs.ball_pos[1] < BEHIND_THRESH - GOAL_DIST:
            fsm.change_state(rs, StateMidIdle())
            return
        if distance >= CIRCLE_TO_CHASE or (abs(direction) > MID_ANGLE_EXIT):
            fsm.change_state(rs, StateMidCircle())
            return

    def exit(self, fsm, rs):
        log("Exiting mid yeet", rs)


# === DEFEND FSM === #

class StateDefendHover(FSMState):
    def enter(self, fsm, rs):
        log("Entering defend hover", rs)

    def update(self, fsm, rs):
        # update ball predictions
        ball_vel = rs.ball_predictor.push_measurement(rs.ball_pos, rs.simulation_time)
        ball_dist = sqrt(pow(rs.agent_pos[0] - rs.ball_pos[0], 2) + pow(rs.agent_pos[1] - rs.ball_pos[1], 2))
        predict_time = predict_time_func(ball_dist)
        predicted_ball = predict_object(rs.ball_pos, ball_vel, predict_time)
        #print(f"Ball prediction for {predict_time} ticks: {predicted_ball}")
        
        # direction = atan2(predicted_ball[1] - rs.agent_pos[1], predicted_ball[0] - rs.agent_pos[0])
        rs.out = move_to_point(rs, IDLE_DIST * (rs.ball_pos[0] / (rs.ball_pos[1] + GOAL_DIST)), IDLE_DIST - GOAL_DIST, False)
        distance = predicted_ball[1] + GOAL_DIST
        if distance < SURGE_THRESH:
            fsm.change_state(rs, StateDefendSurge())
            return

    def exit(self, fsm, rs):
        log("Exiting defend hover", rs)

class StateDefendSurge(FSMState):
    def enter(self, fsm, rs):
        log("Entering defend surge", rs)

    def update(self, fsm, rs):
        # update ball predictions
        ball_vel = rs.ball_predictor.push_measurement(rs.ball_pos, rs.simulation_time)
        actual_ball_dist = sqrt(pow(rs.agent_pos[0] - rs.ball_pos[0], 2) + pow(rs.agent_pos[1] - rs.ball_pos[1], 2))
        predict_time = predict_time_func(actual_ball_dist)
        predicted_ball = predict_object(rs.ball_pos, ball_vel, predict_time)
        #print(f"Ball prediction for {predict_time} ticks: {predicted_ball}")

        rs.out = move_to_point(rs, predicted_ball[0], predicted_ball[1], False)
        ball_dist = rs.ball_pos[1] + GOAL_DIST
        robot_dist = rs.agent_pos[1] + GOAL_DIST
        if ball_dist >= BALL_SAFE_DIST or robot_dist >= SURGE_DIST:
            fsm.change_state(rs, StateDefendHover())
            return

    def exit(self, fsm, rs):
        log("Exiting defend surge", rs)
