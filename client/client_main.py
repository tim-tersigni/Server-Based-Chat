import logging, coloredlogs
import client_config, client_messaging
import socket
from multiprocessing import Pool
import functools


logging.basicConfig(
    level=logging.DEBUG,
)
coloredlogs.install(level='INFO', logger=logging.getLogger(__name__), fmt='%(levelname)s %(message)s')


def udp_init():
    # get client ID from input and get key if subscriber
    client_config.initialize()

    buffer_size = 1024

    # Send hello message to server for authentication
    client_messaging.send_message("!HELLO {}".format(client_config.CLIENT_ID))

    # Authentication loop
    authenticated = False
    while(True):
        # Bytes received by the socket are formatted in a length 2 tuple:
        # message, address
        bytes_recv = client_config.C_UDP_SOCKET.recvfrom(buffer_size)
        if bytes_recv == None:
            continue

        s_message = bytes_recv[0].decode("utf-8")
        s_address_port = bytes_recv[1]
        logging.info("Server message: {} ".format(s_message))
        logging.info("Server IP, port: {}".format(s_address_port))

        # Check for protocol identifier !
        if client_messaging.is_protocol(s_message):
            s_message = s_message[1:] # remove !
            protocol_split = s_message.split()
            protocol_type = protocol_split[0]
            protocol_args = protocol_split[1:]
            logging.debug(
                "Protocol message detected, type = {}".format(protocol_type))
            
            if protocol_type == 'CHALLENGE':
                client_messaging.protocolChallenge(protocol_args)

            elif protocol_type == 'AUTH_SUCCESS':
                client_messaging.protocolAuthSuccess(protocol_args)
                break
            
            elif protocol_type == 'AUTH_FAIL':
                logging.critical("Authentication failed!")
                break

            else:
                print('CHALLENGE expected, received {}'.format(protocol_type))
                break
    
    # Client is authenticated
    print("TCP PORT IS {}".format(client_config.S_TCP_PORT))
    return

def udp():
    buffer_size = 1024

    client_config.C_UDP_SOCKET.bind(('', 12000))

    # Message loop
    while(True):
        # Bytes received by the socket are formatted in a length 2 tuple:
        # message, address
        bytes_recv = client_config.C_UDP_SOCKET.recvfrom(1024)
        if bytes_recv == None:
            continue

        s_message = bytes_recv[0].decode("utf-8")
        s_address_port = bytes_recv[1]
        logging.info("Server message: {} ".format(s_message))
        logging.info("Server IP, port: {}".format(s_address_port))

        # Check for protocol identifier !
        if client_messaging.is_protocol(s_message):
            s_message = s_message[1:] # remove !
            protocol_split = s_message.split()
            protocol_type = protocol_split[0]
            protocol_args = protocol_split[1:]
            logging.debug(
                "Protocol message detected, type = {}".format(protocol_type))

def tcp():
    print("tcp")
    s_tcp_ip = "127.0.0.1"
    s_tcp_port = client_config.S_TCP_PORT
    s_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_tcp_socket.connect((s_tcp_ip,s_tcp_port))
    print("TCP Connected: {} {}".format(s_tcp_ip, s_tcp_port))

def send_message(msg_string):
    msg_bytes = str.encode(msg_string)
    client_config.C_UDP_SOCKET.sendto(msg_bytes, client_config.S_UDP_ADDRESS)

# for multiprocessing
def smap(f):
    return f()

if __name__ == '__main__':
    udp_init()

    #Run udp and tcp concurrently
    f_udp = functools.partial(udp, 1)
    f_tcp = functools.partial(tcp, 1)

    with Pool() as pool:
        res = pool.map(smap, [udp, tcp] )
