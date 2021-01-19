# Inter-process communicaton between robots by using IPC over a local TCP socket
# Legality: Should be OK, however I can only guarantee this for the Feb 2021 RoboCup Jr competition.
# You should verify legality for any future comps. We cannot be held liable if you use this code in future and do not
# disable IPC if it becomes illegal!
# For reference see my issue here: https://github.com/RoboCupJuniorTC/rcj-soccer-sim/issues/29

import sys
from threading import Thread
from multiprocessing.connection import Listener, Client
from enum import Enum

# CLIENT {"message": "connect", "agent_id": 0} -> SERVER {"message": "ok"}
# SERVER {"message": "switch", "role": "defender", "reason": "ball too close"} -> CLIENT {"message": "ok"}

class IPCStatus(Enum):
    DISCONNECTED = 0
    CONNECTING = 1
    CONNECTED = 2
    FAILED = 3

class IPCClient():
    def __init__(self, port: int):
        self.port = port
        self.status = IPCStatus.DISCONNECTED

    def __connect_async(self):
        print(f"Connecting to server on port {self.port}")
        self.client = Client(("localhost", self.port), "AF_INET")
        print("Successfully connected to server!")

        # once we're connected, start our receive function
        self.recv_thread = Thread(target=self.__listen_async, args=())
        self.recv_thread.daemon = True
        self.recv_thread.start()
        self.status = IPCStatus.CONNECTED

    def __listen_async(self):
        print("IPCClient listening started")
        
        while self.status == IPCStatus.CONNECTED:
            msg = self.client.recv()
            print(f"New message: {msg}")

    def connect(self):
        if self.status != IPCStatus.DISCONNECTED:
            print("IPCClient is already connected (or connecting)!")
            return

        # connect in async too, in case that blocks for a little bit
        self.status = IPCStatus.CONNECTING
        self.connect_thread = Thread(target=self.__connect_async, args=())
        self.connect_thread.daemon = True
        self.connect_thread.start()
    
    def disconnect(self):
        self.status = IPCStatus.DISCONNECTED
        self.client.close()
        # cannot stop threads in Python, and cannot be bothered to program an exit condition given that
        # the thread is a daemon and disconnect() is likely never called

class IPCServer():
    def __init__(self, port: int):
        self.port = port
        self.clients = []

    def __accept(self, num_clients: int):
        print("IPCServer is now accepting clients")

        # NOTE: client IDs don't necessarily correspond to robot IDs! Client ID 0 is probably NOT robot ID 1!
        for i in range(num_clients):
            print(f"Waiting for client {i}")
            conn = self.listener.accept()
            print(f"Client id {i} on {conn} connected!")
            self.clients.append(conn)

        print("======== All clients have connected to IPCServer successfully! ========")

    def launch(self):
        self.listener = Listener(("localhost", self.port), "AF_INET")
        self.join_thread = Thread(target=self.__accept, args=(2,)) # num_clients = 2
        self.join_thread.daemon = True
        self.join_thread.start()

    def transmit(self, message):
        for client in self.clients:
            client.send(message)

    def terminate(self):
        self.listener.close()
        # cannot terminate threads in Python, see IPCClient disconnect()