import coloredlogs, logging
import server_config, subscriber
import socket
import secrets
import hashlib
from collections import namedtuple
from Crypto.Cipher import AES
import base64

logging.basicConfig(
    level=logging.DEBUG,
)
coloredlogs.install(level='DEBUG', logger=logging.getLogger(__name__), fmt='%(levelname)s %(message)s')

def udp():
    # (c is for client, s is for socket in var names)
    buffer_size = 2048
    s_udp_ip = '127.0.0.1'
    s_udp_port = 12000

    # Bind UDP socket to address and ip
    server_config.S_UDP_SOCKET.bind((s_udp_ip, s_udp_port))

    # UDP Server Loop
    logging.info('UDP server listening...')
    while(True):
        # Bytes received by the socket are formatted in a length 2 tuple:
        # message, address
        bytes_recv = server_config.S_UDP_SOCKET.recvfrom(buffer_size)
        if bytes_recv == None:
            continue

        c_message = bytes_recv[0].decode("utf-8")
        server_config.C_UDP_ADDRESS = bytes_recv[1]
        print("Message received: {} ".format(c_message))
        logging.info("Client IP, port: {}".format(server_config.C_UDP_ADDRESS))

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
                challenge_rand = protocolHello(c_id)

            elif protocol_type == 'RESPONSE':
                c_id = protocol_args[0]
                res = protocol_args[1]
                protocolResponse(c_id, res, challenge_rand)

            # Not a recognized protocol
            else:
                logging.error("{} is not a recognized protocol".format(protocol_type))

        # TODO: non-protocol messages
        else:
            logging.debug("Client message is not a protocol message.\n")

def tcp():
    n=1 #n will be the number of users we have
    s_tcp_ip = "127.0.0.1"

    server_config.S_TCP_SOCKET=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server_config.S_TCP_SOCKET.bind((s_tcp_ip,server_config.S_TCP_PORT))
    server_config.S_TCP_SOCKET.listen(n)
    while(True):
        clientAddress=server_config.S_TCP_SOCKET.accept()
        print(f"Connection Established- {clientAddress[0]}:{clientAddress[1]}")

def protocolHello(client_id):
    if subscriber.getSubscriber(client_id) != None:
        print("Client {} is a subscriber".format(client_id))

        # retrieve client's key and concatenate a random uuid, then encrypt with MD5
        key = subscriber.getSubscriber(client_id).key
        rand = secrets.token_hex(16)
        key_rand = key + rand
        xres = hashlib.md5(str.encode(key_rand)).hexdigest()
        logging.debug("XRES: {}".format(xres))

        # store xres for future authentication
        xres_dict = {"id":client_id, "xres":xres}
        server_config.XRES_LIST.append(xres_dict)
        logging.info("XRES for {} stored".format(client_id))

        # challenge client with 
        send_message("!CHALLENGE {}".format(rand), client_id=client_id)
        return rand

    else:
        print("Client {} is not a subscriber\n".format(client_id))

def protocolResponse(client_id, res, challenge_rand):
    # fetch xres
    for item in server_config.XRES_LIST:
        if item['id'] == client_id:
            if item['xres'] == res:
                print("Client {} is authenticated".format(client_id))
                cookie = str(secrets.token_hex(16))
                text = cookie + ' ' + str(server_config.S_TCP_PORT)
                key = subscriber.getSubscriber(client_id).key
                send_message('!AUTH_SUCCESS {}'.format(encrypt(rand=challenge_rand, key=key, text=text)), client_id=client_id,)
            else:
                print("Client {} failed authentication. RES {} did not match XRES {}".format(client_id, res, item['xres']))
                send_message("!AUTH_FAIL", client_id=client_id)
            server_config.XRES_LIST.remove(item) # remove old XRES
            return

    logging.warning("Client {} not found in XRES_LIST".format(client_id))

def send_message(msg_string, client_id):
    print("Sent message to {}: {}".format(client_id, msg_string))
    msg_bytes = str.encode(msg_string)
    server_config.S_UDP_SOCKET.sendto(msg_bytes, server_config.C_UDP_ADDRESS)

def encrypt(rand, key, text):
    text = str(text)
    cipher_key = bytes.fromhex(str(rand) + str(key)) # create cypher key from rand and k_a
    cipher = AES.new(cipher_key, AES.MODE_CFB)
    cipher_text = cipher.encrypt(text.encode())
    cipher_iv_text = base64.b64encode(cipher.iv) + b'#' + base64.b64encode(cipher_text) # convert from raw bytes output to base64 (allows # deliminator) to str for clean output
    cipher_iv_text = cipher_iv_text.decode()
    logging.info("Decrypted text: {}".format(text))
    return cipher_iv_text

if __name__ == '__main__':
    #Run udp and tcp concurrently
    udp()
    #tcp()