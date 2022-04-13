import coloredlogs, logging
import client_config, decryption
import hashlib

logging.basicConfig(
    level=logging.DEBUG,
)
coloredlogs.install(level='DEBUG', logger=logging.getLogger(__name__), fmt='%(levelname)s %(message)s')

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
    send_message("!RESPONSE {} {}".format(client_config.CLIENT_ID, res))

def protocolAuthSuccess(args):
    print('Authentication succeeded\n')
    encrypted_message = ' '.join(args)
    logging.debug("Message to decrypt: {}".format(encrypted_message))
    decrypted_message = decryption.decrypt(client_config.CLIENT_ID, client_config.KEY, encrypted_message)
    decrypted_args = decrypted_message.split(' ')
    client_config.COOKIE = decrypted_args[0]
    client_config.S_TCP_PORT = int(decrypted_args[1])
    client_config.AUTHENTICATED = True

def send_message(msg_string):
    msg_bytes = str.encode(msg_string)
    client_config.C_UDP_SOCKET.sendto(msg_bytes, client_config.S_UDP_ADDRESS)

