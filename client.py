import logging
import socket
import uuid
import secrets

# Set to logging.WARNING to remove info / debug output
logging.basicConfig(level=logging.INFO)

# (c is for client, s is for socket in var names)
c_id = int(input("Enter client ID:\n"))

buffer_size = 1024
s_udp_address_port = ("127.0.0.1", 12000)

# Create client udp socket
c_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Send hello message to server for authentication
msg_string = "HELLO {}".format(c_id)
msg_bytes = str.encode(msg_string)

c_socket.sendto(msg_bytes, s_udp_address_port)
