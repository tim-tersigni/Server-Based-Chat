import logging
import socket
import uuid
import hashlib
import select
import secrets
from collections import namedtuple


def udp():
    # Set to logging.WARNING to remove info / debug output
    logging.basicConfig(level=logging.INFO)

    # (c is for client, s is for socket in var names)
    buffer_size = 2048
    server_udp_ip = '127.0.0.1'
    server_udp_port = 12000

    # Bind UDP socket to address and ip
    server_udp_socket.bind((server_udp_ip, server_udp_port))

    # UDP Server Loop
    logging.info('UDP server listening...')
    server_instruction = ""
    while(True):
        #server_instruction = input("Enter Instruction: ")
        # Bytes received by the socket are formatted in a length 2 tuple:
        # message, address
        bytes_recv = server_udp_socket.recvfrom(buffer_size)
        if bytes_recv == None:
            continue

        client_message = bytes_recv[0].decode("utf-8")
        client_address_port = bytes_recv[1]
        logging.info("Client message: {} ".format(client_message))
        logging.info("Client IP, port: {}".format(client_address_port))

        # Is the message a protocol message? (a command for the server)
        # SYNTAX OF PROTOCOL MESSAGES: !PROTOCOL ARG1 ARG2 ARGn...
        if client_message[0] == '!':
            client_message = client_message[1:]
            protocol_split = client_message.split()
            protocol_type = protocol_split[0]
            protocol_args = protocol_split[1:]
            logging.info(
                "Protocol message detected, type = {}".format(protocol_type))

            # !HELLO
            if protocol_type == 'HELLO':
                client_id = protocol_args[0]
                protocolHello(client_id, client_address_port)


            #Not a recognized protocol
            else:
                print("ERROR, {} is not a protocol.\n".format(protocol_type))

        # TODO: non-protocol messages
        else:
            logging.info("Client message is not a protocol message.\n")

def tcp():
<<<<<<< Updated upstream
    tcp_ip = "127.0.0.1"
    port = 1234

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind((tcp_ip, port))
    server_socket.listen()

    sockets_list = [server_socket]
    clients = {}

def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
    except:
        pass
=======
    n=1 #n will be the number of users we have
    s_tcp_ip = "127.0.0.1"
    s_tcp_port = 1234

    S_TCP_SOCKET=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    S_TCP_SOCKET.bind((s_tcp_ip,s_tcp_port))
    S_TCP_SOCKET.listen(n)
    while(True):
        clientSocket,clientAddress=S_TCP_SOCKET.accept()
        print(f"Connection Established- {clientAddress[0]}:{clientAddress[1]}")
>>>>>>> Stashed changes

def loadSubscribers(file_path):
    # return list of namedtuples for subscribers in format (id, key)
    subscriber_file = open(file_path, 'r')
    subscribers = []
    Sub = namedtuple('Sub', ['id', 'key'])
    for line in subscriber_file:
        split_line = line.split(',')
        sub_id = split_line[0]
        sub_key = split_line[1]
        s = Sub(sub_id, sub_key)
        subscribers.append(s)
    return subscribers


def getSubscriber(client_id):
    for s in SUBSCRIBERS:
        if s.id == client_id:
            return s
    return None


def protocolHello(client_id, client_address_port):
    if getSubscriber(client_id) is not None:
        print("Client {} is a subscriber\n".format(client_id))

        # retrieve client's key and concatenate a random uuid, then encrypt with MD5
        key = getSubscriber(client_id)[1]
        key_rand = key + str(uuid.uuid4())
        key_rand_hash = hashlib.md5(str.encode(key_rand))

        # challenge client with hash
        msg = "!CHALLENGE {}".format(key_rand_hash)
        server_udp_socket.sendto(str.encode(msg), client_address_port)

    else:
        print("Client {} is not a subscriber\n".format(client_id))


SUBSCRIBERS = loadSubscribers('subscribers.data')
<<<<<<< Updated upstream
server_udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

if __name__ == '__main__':
    tcp()
=======
S_UDP_SOCKET = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
S_TCP_SOCKET=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
if __name__ == '__main__':
    #Run udp and tcp concurrently
    #udp()
    tcp()
>>>>>>> Stashed changes
