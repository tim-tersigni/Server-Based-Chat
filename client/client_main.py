import logging, coloredlogs
import client_config, client_messaging
import socket
from Crypto.Cipher import AES


logging.basicConfig(
    level=logging.DEBUG,
)
coloredlogs.install(level='DEBUG', logger=logging.getLogger(__name__), fmt='%(levelname)s %(message)s')

# get client ID from input and get key if subscriber
client_config.initialize()

def udp():
    buffer_size = 1024
    logging.basicConfig(level=logging.DEBUG) # Set to logging.WARNING to remove info / debug output

    # Send hello message to server for authentication
    send_message("!HELLO {}".format(client_config.CLIENT_ID))

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
    
    # Client is authenticated, connect to tcp
    # TODO
    print("TCP PORT IS {}".format(client_config.S_TCP_PORT))
    input("Press enter to exit...")

def tcp(tcp_port):
    s_tcp_ip = "127.0.0.1"
    s_tcp_port = tcp_port
    s_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_tcp_socket.connect((s_tcp_ip,s_tcp_port))

def send_message(msg_string):
    msg_bytes = str.encode(msg_string)
    client_config.C_UDP_SOCKET.sendto(msg_bytes, client_config.S_UDP_ADDRESS)
        
    logging.debug("Could not find client's secret key")
    return None

if __name__ == '__main__':
    udp()
    #tcp()
