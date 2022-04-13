import logging, coloredlogs
import socket
import uuid
import secrets
import hashlib
import base64
from Crypto.Cipher import AES

from server import S_TCP_PORT
logging.basicConfig(
    level=logging.DEBUG,
)
coloredlogs.install(level='DEBUG', logger=logging.getLogger(__name__), fmt='%(levelname)s %(message)s')

def udp():
    buffer_size = 1024
    global COOKIE
    global AUTHENTICATED
    global S_TCP_PORT
    logging.basicConfig(level=logging.DEBUG) # Set to logging.WARNING to remove info / debug output

    # Send hello message to server for authentication
    send_message("!HELLO {}".format(CLIENT_ID))

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
            s_message = s_message[1:] # remove !
            protocol_split = s_message.split()
            protocol_type = protocol_split[0]
            protocol_args = protocol_split[1:]
            logging.debug(
                "Protocol message detected, type = {}".format(protocol_type))
            if protocol_type == 'CHALLENGE':
                rand = protocol_args[0]
                protocolChallenge(rand)

            elif protocol_type == 'AUTH_SUCCESS':
                print('Authentication succeeded\n')
                encrypted_message = ' '.join(protocol_args)
                logging.debug("Message to decrypt: {}".format(encrypted_message))
                decrypted_message = decrypt(encrypted_message)
                decrypted_args = decrypted_message.split(' ')
                COOKIE = decrypted_args[0]
                S_TCP_PORT = decrypted_args[1]
                AUTHENTICATED = True
                break
            
            elif protocol_type == 'AUTH_FAIL':
                logging.critical("Authentication failed!")
                break

            else:
                print('CHALLENGE expected, received {}'.format(protocol_type))
                break
    
    # Client is authenticated, connect to tcp
    # TODO
    print("TCP PORT IS {}".format(S_TCP_PORT))
    input("Press enter to exit...")

def tcp(tcp_port):
    s_tcp_ip = "127.0.0.1"
    s_tcp_port = tcp_port
    s_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_tcp_socket.connect((s_tcp_ip,s_tcp_port))

def protocolChallenge(rand):
    global RAND
    RAND = rand
    
    # find res
    key = get_key()
    key_rand = key + rand
    res = hashlib.md5(str.encode(key_rand)).hexdigest()     
    logging.debug("res = {}".format(res))         

    # send response message
    send_message("!RESPONSE {} {}".format(CLIENT_ID, res))

def send_message(msg_string):
    msg_bytes = str.encode(msg_string)
    C_UDP_SOCKET.sendto(msg_bytes, S_UDP_ADDRESS)

def get_key():
    subscriber_file = open('subscribers.data', 'r')
    for line in subscriber_file:
        split_line = line.split(',')
        sub_id = split_line[0]
        if sub_id == CLIENT_ID:
            sub_key = split_line[1]
            return sub_key
        
    logging.debug("Could not find client's secret key")
    return None

def decrypt(iv_text):
    iv_text_list = iv_text.split('#')
    iv = base64.b64decode(iv_text_list[0].encode()) # convert from str to base64 bytes to raw bytes
    cipher_text = iv_text_list[1]
    cipher_text = base64.b64decode(iv_text_list[1].encode())
    logging.debug("iv bytes: {}, ecnrypted text bytes: {}".format(iv, cipher_text))
    
    key = get_key()
    cipher_key = bytes.fromhex(str(RAND) + str(key))
    logging.debug("cipher_key: {}".format(cipher_key))
    logging.debug("rand: {} key: {}".format(str(RAND), str(key)))
    cipher = AES.new(cipher_key, AES.MODE_CFB, iv=iv)
    plaintext = cipher.decrypt(cipher_text).decode()
    logging.info("Decrypted text: {}".format(plaintext))
    return plaintext

# Create client udp socket
CLIENT_ID = input("Enter client ID:\n")
C_UDP_SOCKET = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
S_UDP_ADDRESS = ("127.0.0.1", 12000)
S_TCP_PORT = None
AUTHENTICATED = False
COOKIE = None
RAND = None
if __name__ == '__main__':
    udp()
    #tcp()
