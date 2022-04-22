"""
server_config.py
author: Tim Tersigni

- A config file for the server.

- Contains initilization() to configure config on launch as some info
requires user input.
"""


import socket
from os import path

CLIENT_ID = None
KEY = None
C_UDP_SOCKET = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
C_TCP_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
S_UDP_ADDRESS = ("127.0.0.1", 12000)
S_TCP_IP = "127.0.0.1"
S_TCP_PORT = None
AUTHENTICATED = False
COOKIE = None
RAND = None
CONNECTED = False
LOGGED_IN = False


# get client ID from input and get key if subscriber
def initialize():
    global CLIENT_ID, KEY, LOGGED_IN
    CLIENT_ID = input("Enter client ID:\n")

    # set KEY from subscribers.data
    basepath = path.dirname(__file__)
    filepath = path.abspath(path.join(
        basepath, "..", "server", "subscribers.data"))
    subscriber_file = open(filepath, 'r')
    for line in subscriber_file:
        split_line = line.split(',')
        sub_id = split_line[0]
        if sub_id == CLIENT_ID:
            KEY = split_line[1]

    LOGGED_IN = True

    if KEY is None:
        print("YOU ARE NOT A SUBSCRIBER.")
        initialize()
