import logging
import socket
import uuid
import secrets

# Set to logging.WARNING to remove info / debug output
logging.basicConfig(level=logging.INFO)

# Load list of subscribers from subscribers.data
subscriber_file = open('subscribers.data', 'r')
subscribers = []
for line in subscriber_file:
    split_line = line.split(',')
    sub_id = split_line[0]
    subscribers.append(sub_id)

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

    # Is the message a protocol message? (a command for the server)
    # SYNTAX OF PROTOCOL MESSAGES: !PROTOCOL ARG1 ARG2 ARGn...
    if c_message[0] == '!':
        c_message = c_message[1:]
        protocol_split = c_message.split()
        protocol_type = protocol_split[0]
        c_id = c_message.split()[1]
        logging.info(
            "Protocol message detected, type = {}".format(protocol_type))

        # HELLO message
        if protocol_type == 'HELLO':
            # Verify client id is on list of subscribers
            if c_id in subscribers:
                print("Client {} is a subscriber\n".format(c_id))

                # TODO Send challenge message to client with random key

            else:
                print("Client {} is not a subscriber\n".format(c_id))
        # Not a recognized protocol
        else:
            print("ERROR, {} is not a protocol.\n".format(protocol_type))

    # TODO: non-protocol messages
    else:
        logging.info("Client message is not a protocol message.\n")
