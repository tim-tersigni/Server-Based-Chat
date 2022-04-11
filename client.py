import logging
import socket
import uuid
import secrets
import hashlib


def udp():
    c_id = input("Enter client ID:\n")
    buffer_size = 1024
    cookie = None
    s_tcp_port = None
    logging.basicConfig(level=logging.DEBUG) # Set to logging.WARNING to remove info / debug output

    # Send hello message to server for authentication
    send_message("!HELLO {}".format(c_id))

    # Authentication loop
    authenticated = False
    while(True):
        # Bytes received by the socket are formatted in a length 2 tuple:
        # message, address
        bytes_recv = C_UDP_SOCKET.recvfrom(buffer_size)
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
            logging.debug(
                "Protocol message detected, type = {}".format(protocol_type))
            if protocol_type == 'CHALLENGE':
                rand = protocol_args[0]
                protocolChallenge(rand, c_id)

            elif protocol_type == 'AUTH_SUCCESS':
                print('Authentication succeeded\n')
                cookie = protocol_args[0]
                authenticated = True
                break
            
            elif protocol_type == 'AUTH_FAIL':
                logging.critical("Authentication failed!")
                break

            else:
                print('CHALLENGE expected, received {}'.format(protocol_type))
                break
    
    # Client is authenticated, connect to tcp
    # TODO

def tcp(tcp_port):
    s_tcp_ip = "127.0.0.1"
    s_tcp_port = tcp_port
    s_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_tcp_socket.connect((s_tcp_ip,s_tcp_port))

def protocolChallenge(rand, c_id):
    # find res
    key = get_key(c_id)
    key_rand = key + rand
    res = hashlib.md5(str.encode(key_rand)).hexdigest()     
    logging.debug("res = {}".format(res))         

    # send response message
    send_message("!RESPONSE {} {}".format(c_id, res))

def send_message(msg_string):
    msg_bytes = str.encode(msg_string)
    C_UDP_SOCKET.sendto(msg_bytes, S_UDP_ADDRESS)

def get_key(id):
    subscriber_file = open('subscribers.data', 'r')
    for line in subscriber_file:
        split_line = line.split(',')
        sub_id = split_line[0]
        if sub_id == id:
            sub_key = split_line[1]
            return sub_key
        
    logging.debug("Could not find client's secret key")
    return None

# Create client udp socket
C_UDP_SOCKET = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
S_UDP_ADDRESS = ("127.0.0.1", 12000)
if __name__ == '__main__':
    udp()
    #tcp()
