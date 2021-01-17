# This code partially inspired by our FSM written in C, as used in 2019 and 2020
# on our RoboCup Jr Open/Lightweight robots.

from predictor import Predictor

# TODO consider moving to states.py?
class RobotState:
    """The state of the robot in the world (simplified). Includes "output" such as motor values."""
    def __init__(self):
        # inputs
        self.agent_name = ""
        self.agent_id = -1
        self.agent_pos = [0, 0]
        self.agent_heading = 0
        self.simulation_time = 0 # in simulation milliseconds
        self.ball_pos = [0, 0]
        self.ball_predictor = Predictor() # per agent ball predictor
        self.ipc_server = None
        self.ipc_client = None
        self.ipc_port = None

        # outputs
        self.out = [[0, 0], False] # Left, Right, Flag

class StateMachine:
    """A very simple finite state machine."""
    def __init__(self):
        """Initialises the FSM. The state is initially set to null."""
        self.current_state = None

    def update(self, rs: RobotState):
        """Ticks the FSM. Make sure that current_state is not None first."""
        if self.current_state is not None:
            self.current_state.update(self, rs)
        else:
            import utils
            utils.log("ERROR: Tried to update FSM with null state!", rs)

    def change_state(self, rs: RobotState, new_state):
        """Changes from one state to another.

        Args:
            rs (RobotState): current robot state
            new_state ([FSMState]): new FSM state to enter into
        """
        if self.current_state is not None:
            self.current_state.exit(self, rs)
        self.current_state = new_state
        self.current_state.enter(self, rs)

class FSMState:
    """State in a state machine."""
    def enter(self, fsm: StateMachine, rs: RobotState):
        """Called when entering into this state."""
        pass

    def update(self, fsm: StateMachine, rs: RobotState):
        """Called each tick this state is active in."""
        pass

    def exit(self, fsm: StateMachine, rs: RobotState):
        """Called when changing out of this state."""
        pass

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
