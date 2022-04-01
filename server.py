import logging
import socket
import uuid

# Set to logging.WARNING to remove info / debug output
logging.basicConfig(level=logging.INFO)

# (c is for client, s is for socket in var names)
buffer_size = 2048
s_udp_ip = '127.0.0.1'
s_udp_port = 12000

# Create UDP datagram socket
s_udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind UDP socket to address and ip
s_udp_socket.bind((s_udp_ip, s_udp_port))

# UDP Server Loop
logging.info('UDP server listening...')
while(True):
    # Bytes received by the socket are formatted in a length 2 tuple:
    # message, address
    bytes_recv = s_udp_socket.recvfrom(buffer_size)

    c_message = bytes_recv[0].decode("utf-8")
    c_ip = bytes_recv[1]
    logging.info("Client message: \"{} \"".format(c_message))
    logging.info("Client IP, port: {}".format(c_ip))
