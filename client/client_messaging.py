"""
client_messaging.py
author: Tim Tersigni

- Protocol functions contain all actions the server performs in response to the
respective protocol, helping shrink the main script.

- is_protocol() detects if a message is a protocol

- send message using send_message()
"""

import coloredlogs
import logging
import client_config
import decryption
import hashlib

logging.basicConfig(
    level=logging.DEBUG,
)
coloredlogs.install(level='DEBUG', logger=logging.getLogger(__name__),
                    fmt='%(levelname)s %(message)s')


def send_message_udp(message: str):
    msg_bytes = str.encode(message)
    client_config.C_UDP_SOCKET.sendto(msg_bytes, client_config.S_UDP_ADDRESS)


def send_message_tcp(message: str):
    msg_bytes = str.encode(message)
    client_config.C_TCP_SOCKET.sendall(msg_bytes)


# Returns if message received is a protocol message
def is_protocol(message: str) -> bool:
    if message[0] == '!':
        return True
    return False


def protocolChallenge(args):
    rand = args[0]
    client_config.RAND = rand

    # find res
    key = client_config.KEY
    key_rand = key + rand
    res = hashlib.md5(str.encode(key_rand)).hexdigest()
    logging.debug("res = {}".format(res))

    # send response message
    send_message_udp("!RESPONSE {} {}".format(client_config.CLIENT_ID, res))


def protocolAuthSuccess(args):
    print('Authentication succeeded')
    encrypted_message = ' '.join(args)
    logging.debug("Message to decrypt: {}".format(encrypted_message))
    decrypted_message = decryption.decrypt(
        client_config.CLIENT_ID, client_config.KEY, encrypted_message)
    decrypted_args = decrypted_message.split(' ')
    client_config.COOKIE = decrypted_args[0]
    client_config.S_TCP_PORT = int(decrypted_args[1])
    client_config.AUTHENTICATED = True


def protocolConnected():
    client_config.CONNECTED = True
    print('You are connected!')

