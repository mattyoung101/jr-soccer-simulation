# Inter-process communicaton between robots by using IPC over a local TCP socket
# Legality: Should be OK, however I can only guarantee this for the Feb 2021 RoboCup Jr competition.
# You should verify legality for any future comps. We cannot be held liable if you use this code in future and do not
# disable IPC if it becomes illegal!
# For reference see my issue here: https://github.com/RoboCupJuniorTC/rcj-soccer-sim/issues/29

import time
import math
import socket
import sys
from multiprocessing import Process
from dataclasses import dataclass
import json
#import fcntl
from enum import Enum

# CLIENT {"message": "connect", "agent_id": 0} -> SERVER {"message": "ok"}
# SERVER {"message": "switch", "role": "defender", "reason": "ball too close"} -> CLIENT {"message": "ok"}

#####
# FIXME: HANDLE ERRORS PROPERLY!!!!
#####

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

class IPCClient():
    def __init__(self, port: int):
        self.port = port
        self.sock = None
        self.status = IPCStatus.DISCONNECTED
        self.connect_process = None
        #self.listen_process = None

    def __connect_async(self):
        print(f"Connecting to server on port {self.port}")
        try:
            self.sock.connect(('localhost', self.port))
            print("Successfully connected to server!")
        except ConnectionRefusedError as e:
            print(f"[ERROR] Failed to connect to IPCServer socket: {e}", file=sys.stderr)

        self.status = IPCStatus.CONNECTED

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
            print("IPCClient is already connected!")
            return
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(True)

        # connect in async too (just in case?)
        # technically we haven't connected yet, but if we don't set this to be true then omicron_player will keep
        # attempting to reconnect which we don't want
        self.status = IPCStatus.CONNECTING
        self.connect_process = Process(target=self.__connect_async, args=())
        self.connect_process.start()
    
    def disconnect(self):
        self.status = IPCStatus.DISCONNECTED
        self.sock.close()
        self.connect_process.kill()
        # self.listen_process.kill()

class IPCServer():
    def __init__(self, port: int):
        self.port = port
        self.sock = None
        self.clients = []
        self.join_process = None

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
        # https://docs.python.org/3/howto/sockets.html#ipc
        # apparently binding to localhost skips a few layers of netcode in the system
        try:
            self.sock.bind(('localhost', self.port))
            self.sock.listen(1)
        
            # accept clients in parallel
            self.join_process = Process(target=self.__accept, args=(2,)) # num_clients = 2
            self.join_process.start()
        except Exception as e:
            print(f"[ERROR] Failed to bind/listen server socket: {e} - IPC is now impossible!", file=sys.stderr)

    def transmit(self, message):
        msg_bytes = bytes(message, "US-ASCII")
        for client in self.clients:
            client.conn.sendall(msg_bytes)

    def terminate(self):
        self.sock.close()
        self.join_process.kill()