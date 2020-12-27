# This code partially inspired by our FSM written in C, as used in 2019 and 2020
# on our RoboCup Jr Open/Lightweight robots.

class RobotState:
    def __init__(self):
        self.agent_pos = [0, 0]
        self.agent_heading = 0
        self.ball_pos = [0, 0]

class StateMachine:
    def __init__(self):
        self.current_state = None

    def update(self, state: RobotState):
        if current_state is not None:
            self.current_state.update(self, state)
        else:
            print("ERROR: Tried to update FSM with null state!")

    def change_state(self, new_state):
        self.current_state.exit(self, state)
        self.current_state = new_state
        self.current_state.enter(self, state)

class FSMState:
    def __init__(self, name: str):
        self.name = name

    def enter(self, fsm: StateMachine, state: RobotState):
        pass

    def update(self, fsm: StateMachine, state: RobotState):
        pass

    def exit(self, fsm: StateMachine, state: RobotState):
        pass

if __name__ == "__main__":
    # TODO add testing code
