"""
server_messaging.py
author: Tim Tersigni

- Protocol functions contain all actions the server performs in response to the
respective protocol, helping shrink the main script.

- is_protocol() detects if a message is a protocol

"""

import coloredlogs
import logging
import server_config
import subscriber
import encryption
import secrets
import hashlib

logging.basicConfig(
    level=logging.DEBUG,
)
coloredlogs.install(level='INFO', logger=logging.getLogger(__name__),
                    fmt='%(levelname)s %(message)s')


# Returns if message received is a protocol message
def is_protocol(message: str) -> bool:
    if message[0] == '!':
        return True
    return False


# Send message to client client-id
def send_message_udp(message: str, client_id):
    print("Sent message to {}: {}".format(str(client_id), message))
    msg_bytes = str.encode(message)
    server_config.S_UDP_SOCKET.sendto(msg_bytes, server_config.C_UDP_ADDRESS)


# Send tcp message to client client-id
def send_message_tcp(message: str, client_id, c_tcp_conn):
    print("Sent message to {}: {}".format(str(client_id), message))
    msg_bytes = str.encode(message)
    c_tcp_conn.sendall(msg_bytes)


# Actions taken when server receives !HELLO
def protocolHello(client_id):
    client = subscriber.getSubscriber(client_id)
    if client is not None:
        print("Client {} is a subscriber".format(client_id))

        # retrieve client's key and concatenate a random uuid
        # then encrypt with MD5
        key = client.key
        rand = secrets.token_hex(16)
        key_rand = key + rand
        xres = hashlib.md5(str.encode(key_rand)).hexdigest()
        logging.debug("XRES: {}".format(xres))

        # store xres for future authentication
        client.xres = xres
        logging.info("XRES for {} set".format(client_id))

        # challenge client
        send_message_udp("!CHALLENGE {}".format(rand), client_id=client_id)
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
                # save cookie to subscriber in subscriber.data
                client.write_cookie()
                text = client.cookie + ' ' + str(server_config.S_TCP_PORT)
                key = subscriber.getSubscriber(client_id).key
                send_message_udp('!AUTH_SUCCESS {}'.format(encryption.encrypt(
                    rand=challenge_rand, key=key, text=text)),
                    client_id=client_id,)
                return True
            else:
                print((
                    "Client {} failed authentication. RES {} is not {}"
                      ).format(client_id, res, client.xres))
                send_message_udp("!AUTH_FAIL", client_id=client_id)
            client.xres is None  # remove old XRES
            return False


# Actions taken when server thread receives !CHAT_REQUEST
def protocolChatRequest(protocol_args, conn):
    client_b_id = protocol_args[0]
    client_b = subscriber.getSubscriber(client_b_id)

    # check if client b is connected and not in a chat session
    if client_b.tcp_connected and not client_b.chatting:
        print("TODO")


def protocolConnect(cookie, c_tcp_ip, c_tcp_port, c_tcp_conn):
    client = subscriber.getSubscriberFromCookie(cookie)
    client.tcp_connected = True

    # Send client !CONNECTED message
    message = "!CONNECTED"
    client = "{} {}".format(c_tcp_ip, c_tcp_port)
    send_message_tcp(message, client, c_tcp_conn)
