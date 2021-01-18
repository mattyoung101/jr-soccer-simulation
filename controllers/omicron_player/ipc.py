# Inter-process communicaton between robots by using IPC over a local TCP socket
# Legality: Should be OK, however I can only guarantee this for the Feb 2021 RoboCup Jr competition.
# You should verify legality for any future comps. We cannot be held liable if you use this code in future and do not
# disable IPC if it becomes illegal!
# For reference see my issue here: https://github.com/RoboCupJuniorTC/rcj-soccer-sim/issues/29

import time
import math
import socket
import sys
from threading import Thread
from dataclasses import dataclass
import json
from enum import Enum

# CLIENT {"message": "connect", "agent_id": 0} -> SERVER {"message": "ok"}
# SERVER {"message": "switch", "role": "defender", "reason": "ball too close"} -> CLIENT {"message": "ok"}

## TODO: Switch to UDP instead of TCP?

@dataclass
class IPCConnection:
    # we do actually have types for these, but idk what they are (docs for socket don't say!)
    conn: any
    addr: any

class IPCStatus(Enum):
    DISCONNECTED = 0
    CONNECTING = 1
    CONNECTED = 2
    FAILED = 3

class IPCClient():
    def __init__(self, port: int):
        self.port = port
        self.sock = None
        self.status = IPCStatus.DISCONNECTED
        self.connect_thread = None
        #self.listen_process = None

    def __connect_async(self):
        print(f"Connecting to server on port {self.port}")
        try:
            self.sock.connect(('localhost', self.port))
            print("Successfully connected to server!")
            self.status = IPCStatus.CONNECTED
        except ConnectionRefusedError as e:
            print(f"[ERROR] Failed to connect to IPCServer socket: {e}", file=sys.stderr)
            self.status = IPCStatus.FAILED

        # once we're connected, start our receive function
        # self.listen_process = Process(target=self.__listen_async, args=())
        # self.listen_process.start()

    # def check_messages(self):
    #     availableBytes = fcntl.ioctl(self.sock, fcntl.FIONREAD)

    # def __listen_async(self):
    #     print("IPCClient listening started")

    #     while self.alive:
    #         data = self.sock.recv(1024)
    #         if not data:
    #             print("Data was null!")
    #             break
    #         datastr = data.decode("US-ASCII")
    #         print(f"Received message: {datastr}")

    def connect(self):
        if self.status != IPCStatus.DISCONNECTED:
            print("IPCClient is already connected (or connecting)!")
            return
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(True)

        # connect in async too (just in case?)
        self.status = IPCStatus.CONNECTING
        self.connect_thread = Thread(target=self.__connect_async, args=())
        self.connect_thread.daemon = True
        self.connect_thread.start()
    
    def disconnect(self):
        self.status = IPCStatus.DISCONNECTED
        self.sock.close()
        # cannot stop threads in Python, and cannot be bothered to program an exit condition given that
        # the thread is a daemon and disconnect() is likely never called

class IPCServer():
    def __init__(self, port: int):
        self.port = port
        self.sock = None
        self.clients = []
        self.join_thread = None

    def __accept(self, num_clients: int):
        print("IPCServer is now accepting clients")

        for i in range(num_clients):
            print(f"Waiting for client {i}")
            conn, addr = self.sock.accept()
            print(f"Client id {i} on {addr} connected!")
            self.clients.append(IPCConnection(conn, addr))

        print("======== All clients have connected to IPCServer successfully! ========")

    def launch(self):
        # TCP socket over IP (could also use AF_UNIX but can't find enough docs on that)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # https://docs.python.org/3/howto/sockets.html#ipc
            # apparently binding to localhost skips a few layers of netcode in the system
            self.sock.bind(('localhost', self.port))
            self.sock.listen(1)
        
            # accept clients in parallel
            self.join_thread = Thread(target=self.__accept, args=(2,)) # num_clients = 2
            self.join_thread.daemon = True
            self.join_thread.start()
        except Exception as e:
            # TODO catch a more narrow exception above!
            print(f"[ERROR] Failed to bind/listen server socket: {e} - IPC is now impossible!", file=sys.stderr)

    def transmit(self, message):
        msg_bytes = bytes(message, "US-ASCII")
        for client in self.clients:
            client.conn.sendall(msg_bytes)

    def terminate(self):
        self.sock.close()
        # cannot terminate threads in Python, see IPCClient disconnect()