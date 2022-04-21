"""
server_config.py
author: Tim Tersigni

- A config file for the server.
"""

import socket
S_UDP_SOCKET = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
C_UDP_ADDRESS = None
S_TCP_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
S_TCP_IP = "127.0.0.1"
S_TCP_PORT = 1234
