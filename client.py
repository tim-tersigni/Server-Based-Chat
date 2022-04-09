import logging
import socket
import uuid
import secrets


def udp():
    # Set to logging.WARNING to remove info / debug output
    logging.basicConfig(level=logging.INFO)

    # (c is for client, s is for socket in var names)
    c_id = int(input("Enter client ID:\n"))

    buffer_size = 1024
    s_udp_address_port = ("127.0.0.1", 12000)

    # Create client udp socket
    c_udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # Send hello message to server for authentication
    msg_string = "!HELLO {}".format(c_id)
    msg_bytes = str.encode(msg_string)

    c_udp_socket.sendto(msg_bytes, s_udp_address_port)

    # Wait for challenge
    while(True):
        # Bytes received by the socket are formatted in a length 2 tuple:
        # message, address
        bytes_recv = c_udp_socket.recvfrom(buffer_size)
        if bytes_recv == None:
            continue

        s_message = bytes_recv[0].decode("utf-8")
        s_address_port = bytes_recv[1]
        logging.info("Server message: {} ".format(s_message))
        logging.info("Server IP, port: {}".format(s_address_port))

        # Check for protocol identifier !
        if s_message[0] == '!':
            s_message = s_message[1:]
            protocol_split = s_message.split()
            protocol_type = protocol_split[0]
            protocol_args = protocol_split[1:]
            logging.info(
                "Protocol message detected, type = {}".format(protocol_type))

            if protocol_type == 'CHALLENGE':
                print('TODO, challenge received\n')
                break
            else:
                print('CHALLENGE expected, received {}'.format(protocol_type))
                break

def tcp():
    s_tcp_ip = "127.0.0.1"
    s_tcp_port = 1234
    s_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_tcp_socket.connect((s_tcp_ip,s_tcp_port))

if __name__ == '__main__':
    #udp()
    tcp()
