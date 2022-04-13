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

# Actions taken when server receives !RESPONSE
def protocolResponse(client_id, res, challenge_rand):
    # fetch xres
    for item in server_config.XRES_LIST:
        if item['id'] == client_id:
            if item['xres'] == res:
                print("Client {} is authenticated".format(client_id))
                cookie = str(secrets.token_hex(16))
                text = cookie + ' ' + str(server_config.S_TCP_PORT)
                key = subscriber.getSubscriber(client_id).key
                send_message('!AUTH_SUCCESS {}'.format(encryption.encrypt(rand=challenge_rand, key=key, text=text)), client_id=client_id,)
            else:
                print("Client {} failed authentication. RES {} did not match XRES {}".format(client_id, res, item['xres']))
                send_message("!AUTH_FAIL", client_id=client_id)
            server_config.XRES_LIST.remove(item) # remove old XRES
            return

    logging.warning("Client {} not found in XRES_LIST".format(client_id))