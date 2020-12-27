# This code partially inspired by our FSM written in C, as used in 2019 and 2020
# on our RoboCup Jr Open/Lightweight robots.

class RobotState:
    def __init__(self):
        self.agent_pos = [0, 0]
        self.agent_heading = 0
        self.ball_pos = [0, 0]

class StateMachine:
    def __init__(self, initial_state):
        self.current_state = initial_state

<<<<<<< HEAD
    def update(self, state: RobotState):
        if self.current_state is not None:
            self.current_state.update(self, state)
=======
    def update(self, rs: RobotState):
        if self.current_state is not None:
            self.current_state.update(self, rs)
>>>>>>> f4de33c8af40572af966228d95498cafc79b15cb
        else:
            print("ERROR: Tried to update FSM with null state!")

    def change_state(self, rs: RobotState, new_state):
        self.current_state.exit(self, rs)
        self.current_state = new_state
        self.current_state.enter(self, rs)

class FSMState:
    def enter(self, fsm: StateMachine, rs: RobotState):
        pass

    def update(self, fsm: StateMachine, rs: RobotState):
        pass

    def exit(self, fsm: StateMachine, rs: RobotState):
        pass

<<<<<<< HEAD
# if __name__ == "__main__":
#     # TODO add testing code
=======
if __name__ == "__main__":
    class TestState2(FSMState):
        def update(self, fsm, rs):
            print("Updating TestState2 WOOOO")

    class TestState(FSMState):
        def update(self, fsm, rs):
            print("In TestState update()")
            print(fsm, rs)
            fsm.change_state(rs, TestState2())

    myTestState = TestState()
    world = RobotState()
    fsm = StateMachine(myTestState)
    fsm.update(world)
    fsm.update(world)
    fsm.update(world)
>>>>>>> f4de33c8af40572af966228d95498cafc79b15cb
