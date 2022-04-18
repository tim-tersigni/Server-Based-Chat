import coloredlogs, logging
import server_config, subscriber
import encryption
import secrets
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

# Send message to client client-id
def send_message(message: str, client_id):
    print("Sent message to {}: {}".format(str(client_id), message))
    msg_bytes = str.encode(message)
    server_config.S_UDP_SOCKET.sendto(msg_bytes, server_config.C_UDP_ADDRESS)

# Actions taken when server receives !HELLO
def protocolHello(client_id):
    client = subscriber.getSubscriber(client_id)
    if client != None:
        print("Client {} is a subscriber".format(client_id))
        # retrieve client's key and concatenate a random uuid, then encrypt with MD5
        key = client.key
        rand = secrets.token_hex(16)
        key_rand = key + rand
        xres = hashlib.md5(str.encode(key_rand)).hexdigest()
        logging.debug("XRES: {}".format(xres))

        # store xres for future authentication
        client.xres = xres
        logging.info("XRES for {} set".format(client_id))

        # challenge client with 
        send_message("!CHALLENGE {}".format(rand), client_id=client_id)
        return rand

    else:
        print("Client {} is not a subscriber\n".format(client_id))

# Actions taken when server receives !RESPONSE
# returns True if authenticated, False otherwise
def protocolResponse(client_id, res, challenge_rand) -> bool:
    # fetch xres
    for client in server_config.SUBSCRIBERS:
        if client.id == client_id:
            if client.xres == res:
                print("Client {} is authenticated".format(client_id))
                client.cookie = str(secrets.token_hex(16))
                text = client.cookie + ' ' + str(server_config.S_TCP_PORT)
                key = subscriber.getSubscriber(client_id).key
                send_message('!AUTH_SUCCESS {}'.format(encryption.encrypt(rand=challenge_rand, key=key, text=text)), client_id=client_id,)
                
                # return cookie
                return True
            else:
                print("Client {} failed authentication. RES {} did not match XRES {}".format(client_id, res, client.xres))
                send_message("!AUTH_FAIL", client_id=client_id)
            client.xres = None # remove old XRES
            return False
            