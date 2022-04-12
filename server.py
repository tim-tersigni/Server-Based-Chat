import coloredlogs, logging
import socket
import secrets
import hashlib
from collections import namedtuple
import datetime
import random
from Crypto.Cipher import AES

logging.basicConfig(
    level=logging.DEBUG,
)
coloredlogs.install(level='DEBUG', logger=logging.getLogger(__name__), fmt='%(levelname)s %(message)s')

def udp():
    global C_UDP_ADDRESS

    # (c is for client, s is for socket in var names)
    buffer_size = 2048
    s_udp_ip = '127.0.0.1'
    s_udp_port = 12000

    # Bind UDP socket to address and ip
    S_UDP_SOCKET.bind((s_udp_ip, s_udp_port))

    # UDP Server Loop
    logging.info('UDP server listening...')
    while(True):
        # Bytes received by the socket are formatted in a length 2 tuple:
        # message, address
        bytes_recv = S_UDP_SOCKET.recvfrom(buffer_size)
        if bytes_recv == None:
            continue

        c_message = bytes_recv[0].decode("utf-8")
        C_UDP_ADDRESS = bytes_recv[1]
        print("Message received: {} ".format(c_message))
        logging.info("Client IP, port: {}".format(C_UDP_ADDRESS))

        # Is the message a protocol message? (a command for the server)
        # SYNTAX OF PROTOCOL MESSAGES: !PROTOCOL ARG1 ARG2 ARGn...
        if c_message[0] == '!':
            c_message = c_message[1:]
            protocol_split = c_message.split()
            protocol_type = protocol_split[0]
            protocol_args = protocol_split[1:]
            logging.debug(
                "Protocol message detected, type = {}".format(protocol_type))

            # !HELLO
            if protocol_type == 'HELLO':
                c_id = protocol_args[0]
                protocolHello(c_id)

            elif protocol_type == 'RESPONSE':
                c_id = protocol_args[0]
                res = protocol_args[1]
                protocolResponse(c_id, res)

            # Not a recognized protocol
            else:
                logging.error("{} is not a recognized protocol".format(protocol_type))

        # TODO: non-protocol messages
        else:
            logging.debug("Client message is not a protocol message.\n")

def tcp():
    n=1 #n will be the number of users we have
    s_tcp_ip = "127.0.0.1"

    S_TCP_SOCKET=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    S_TCP_SOCKET.bind((s_tcp_ip,S_TCP_PORT))
    S_TCP_SOCKET.listen(n)
    while(True):
        clientSocket,clientAddress=S_TCP_SOCKET.accept()
        print(f"Connection Established- {clientAddress[0]}:{clientAddress[1]}")

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

def getKey(client_id):
    try:
        return getSubscriber(client_id)[1]
    except:
        logging.CRITICAL("Could not find key for {}".format(client_id))
        return None

def send_message(msg_string, client_id):
    print("Sent message to {}: {}".format(client_id, msg_string))
    msg_bytes = str.encode(msg_string)
    S_UDP_SOCKET.sendto(msg_bytes, C_UDP_ADDRESS)

def encrypt(rand, key, text):
    cipher_key = bytes.fromhex(str(rand) + str(key)) # create cypher key from rand and k_a
    cipher = AES.new(cipher_key, AES.MODE_EAX)
    cipher_text = cipher.encrypt_and_digest(bytes(text, 'utf-8'))
    logging.debug("Encrypted text: {}".format(cipher_text))
    return cipher_text

def protocolHello(client_id):
    if getSubscriber(client_id) != None:
        print("Client {} is a subscriber".format(client_id))

        # retrieve client's key and concatenate a random uuid, then encrypt with MD5
        key = getKey(client_id)
        rand = secrets.token_hex(16)
        key_rand = key + rand
        xres = hashlib.md5(str.encode(key_rand)).hexdigest()
        logging.debug("XRES: {}".format(xres))

        # store xres for future authentication
        xres_dict = {"id":client_id, "xres":xres}
        XRES_LIST.append(xres_dict)
        logging.info("XRES for {} stored".format(client_id))

        # challenge client with 
        send_message("!CHALLENGE {}".format(rand), client_id=client_id)

    else:
        print("Client {} is not a subscriber\n".format(client_id))

def protocolResponse(client_id, res):
    # fetch xres
    for item in XRES_LIST:
        if item['id'] == client_id:
            if item['xres'] == res:
                print("Client {} is authenticated".format(client_id))
                cookie = str(random.seed(datetime.datetime.utcnow().timestamp()))
                rand = str(secrets.token_hex(16))
                send_message('!AUTH_SUCCESS {}'.format(encrypt(rand=rand, key=getKey(client_id), text=cookie + ' ' + str(S_TCP_PORT))), client_id=client_id,)
                return
            else:
                print("Client {} failed authentication. RES {} did not match XRES {}".format(client_id, res, item['xres']))
                send_message("!AUTH_FAIL", client_id=client_id)
                return

    logging.warning("Client {} not found in XRES_LIST".format(client_id))



SUBSCRIBERS = loadSubscribers('subscribers.data')
S_UDP_SOCKET = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
C_UDP_ADDRESS = None
S_TCP_SOCKET=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
S_TCP_PORT = 1234
XRES_LIST = []
if __name__ == '__main__':
    #Run udp and tcp concurrently
    udp()
    #tcp()