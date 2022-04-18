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
S_UDP_ADDRESS = ("127.0.0.1", 12000)
S_TCP_PORT = None
AUTHENTICATED = False
COOKIE = None
RAND = None

# get client ID from input and get key if subscriber
def initialize():
    global CLIENT_ID, KEY
    CLIENT_ID = input("Enter client ID:\n")

    #get key
    basepath = path.dirname(__file__)
    filepath =path.abspath(path.join(basepath, "..", "server", "subscribers.data"))
    subscriber_file = open(filepath, 'r')
    for line in subscriber_file:
        split_line = line.split(',')
        sub_id = split_line[0]
        if sub_id == CLIENT_ID:
            KEY = split_line[1]
    
    if KEY == None:
        print("YOU ARE NOT A SUBSCRIBER.")