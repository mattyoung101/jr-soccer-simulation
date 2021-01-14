# Inter-process communicaton between robots
# NOTE: THIS MAY BE ILLEGAL depending on how you interpret the rules (it can be easily disabled for this reason)
# We are waiting for confirmation: https://github.com/RoboCupJuniorTC/rcj-soccer-sim/issues/29#issuecomment-758640512
import time
import math
import socket
import sys

# CLIENT {"message": "connect", "agent_id": 0} -> SERVER {"message": "ok"}
# SERVER {"message": "switch", "role": "defender", "reason": "ball too close"} -> CLIENT {"message": "ok"}

class IPCClient():
    def __init__(self, port):
        self.port = port
        self.connected = False

class IPCServer():
    def __init__(self, port):
        self.port = port
        self.sock = None

    def launch(self):
        # TCP socket on IP (could also use AF_UNIX but can't find enough docs on that)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('', self.port))
        self.sock.listen(1)
        # TODO how do we await without slowing down to hell

    def terminate(self):
        self.sock.close()