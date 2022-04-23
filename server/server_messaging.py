"""
server_messaging.py
author: Tim Tersigni

- Protocol functions contain all actions the server performs in response to the
respective protocol, helping shrink the main script.

- is_protocol() detects if a message is a protocol

- send messages over udp or tcp
"""

import coloredlogs
import logging
from subscriber import Subscriber
import server_config
import encryption
import secrets
import hashlib
import data_manager
from chat_session import Chat_Session
import threading
import time
lock = threading.Lock()

logging.basicConfig(
    level=logging.DEBUG,
)
coloredlogs.install(level='INFO', logger=logging.getLogger(__name__),
                    fmt='%(levelname)s %(message)s')


# Returns if message received is a protocol message
def is_protocol(message: str) -> bool:
    if len(message) < 1:
        return False

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
    lock.acquire()
    print("Sent message to {}: {}".format(str(client_id), message))
    msg_bytes = str.encode(message)
    c_tcp_conn.sendall(msg_bytes)
    lock.release()


# Actions taken when server receives !HELLO
def protocolHello(client_id, subscribers):
    client = data_manager.getSubscriber(client_id, subscribers)
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
def protocolResponse(client_id, res, challenge_rand, subscribers) -> bool:
    # find client in subscriber list
    client = data_manager.getSubscriber(client_id, subscribers)

    # the client's response matches stored xres, authenticate
    if client.xres == res:
        print("Client {} is authenticated".format(client_id))
        # generate client cookie and store in it's subscriber object
        client.cookie = str(secrets.token_hex(16))
        # create encrypted cookie and port message
        # send AUTH_SUCCESS to client
        text = client.cookie + ' ' + str(server_config.S_TCP_PORT)
        key = data_manager.getSubscriber(client_id, subscribers).key
        send_message_udp('!AUTH_SUCCESS {}'.format(encryption.encrypt(
            rand=challenge_rand, key=key, text=text)),
            client_id=client_id,)
        return True

    # the client's response did not match, fail authentication
    else:
        print((
            "Client {} failed authentication. RES {} is not {}"
                ).format(client_id, res, client.xres))
        send_message_udp("!AUTH_FAIL", client_id=client_id)
    client.xres is None  # remove old XRES
    return False


def protocolConnect(cookie, c_tcp_ip, c_tcp_port, c_tcp_conn, subscribers):
    client = data_manager.getSubscriberFromCookie(cookie, subscribers)
    client.tcp_connected = True

    # Send client !CONNECTED message
    message = "!CONNECTED"
    client_addr = "{} {}".format(c_tcp_ip, c_tcp_port)
    send_message_tcp(message, client_addr, c_tcp_conn)

    return client


# Actions taken when server thread receives !CHAT_REQUEST
def protocolChatRequest(protocol_args, client_a: Subscriber,
                        connected_clients):
    try:
        client_b_id = protocol_args[0]
        client_b: Subscriber = data_manager.getSubscriber(
            client_b_id, connected_clients)
    except Exception:
        logging.error("Insufficient args.")

    # client b is not connected
    if client_b is None:
        logging.error(f"CHAT_REQUEST: {client_b_id} is not CONNECTED")

    # prevent chatting with self
    elif client_b_id == client_a.id:
        message = "!WARNING You can't chat with yourself."
        send_message_tcp(
            message=message, client_id=client_a.id,
            c_tcp_conn=client_a.tcp_conn
        )

    # check if client b is connected and not in a chat session
    elif client_b.tcp_connected and client_b.chat_session is None:
        print(f"Connecting client {client_a.id} to {client_b_id}")

        # create chat session and assign to subscriber objects
        session_id = str(secrets.token_hex(16))
        chat_session = Chat_Session(
            client_a=client_a, client_b=client_b, id=session_id)
        client_a.chat_session = chat_session
        client_b.chat_session = chat_session

        # send chat started messages to both clients
        message = f"!CHAT_STARTED {session_id} {client_b_id}"
        send_message_tcp(
            message=message, client_id=client_a.id,
            c_tcp_conn=client_a.tcp_conn)
        message = f"!CHAT_STARTED {session_id} {client_a.id}"
        send_message_tcp(
            message=message, client_id=client_b_id,
            c_tcp_conn=client_b.tcp_conn)

        # return new chat session object for server
        return chat_session

    # client b is busy, can not start session
    elif client_b.tcp_connected:
        logging.error(f"CHAT_REQUEST: {client_b_id} is busy")

    # Tell client_a that client_b is UNREACHABLE
    message = f"!UNREACHABLE {client_b_id}"
    send_message_tcp(
        message=message, client_id=client_a.id, c_tcp_conn=client_a.tcp_conn
    )

    # return no new chat session as it was not started
    return None


# Actions taken when the server receives !END_REQUEST
def protocolEndRequest(client, chat_sessions: Chat_Session):
    # the client is in a chat session
    if client.chat_session is not None:
        # save chat partner and session id before ending session
        client_b = client.chat_session.getPartner(client)
        session_id = client.chat_session.id
        # try to end chat session
        if client.chat_session.end():
            # inform both clients chat session has ended
            message = f"!END_NOTIF {session_id}"

            send_message_tcp(
                message=message, client_id=client.id,
                c_tcp_conn=client.tcp_conn)
            send_message_tcp(
                message=message, client_id=client_b.id,
                c_tcp_conn=client_b.tcp_conn)

            # try to remove session from chat_sessions list
            for s in chat_sessions:
                s: Chat_Session
                # remove session
                if s.containsClient(client=client):
                    chat_sessions.remove(s)
                # failed to remove session
                else:
                    logging.error(
                        f"Could not remove {client.chat_session.id}")

        # ending the chat session failed
        else:
            logging.critical(
                "Could not end chat session {}".format(client.chat_session.id))
            message = "ERROR could not end chat session"
            send_message_tcp(message, client.id, client.tcp_conn)

    # the client is not in a chat session, can't end session
    else:
        logging.error(
            f"Client {client.id} is not chatting. Can not end session.")


def protocolHistoryReq(client, client_b_id, subscribers: list):
    for s in subscribers:
        s: Subscriber
        if s.id == client_b_id:
            client_b = s
    chat_session = client_b.chat_session
    log_lines = chat_session.getLogContents()

    for line in log_lines:
        message = f"!HISTORY_RESP {line.strip()}"
        logging.debug(f"message: {message}")

        send_message_tcp(message=message, client_id=client.id,
                         c_tcp_conn=client.tcp_conn)
        time.sleep(0.01)


def logOff(client, chat_sessions, connected_clients):
    # try to log off client
    if client.logOff(chat_sessions, connected_clients):

        # Notify client that session is ended successfully
        send_message_tcp(
            f"!END_NOTIF {client.chat_session.id}",
            client.id, client.tcp_conn)

    # failed to log off
    else:
        logging.critical(f"Could not log off client {client.id}")
        send_message_tcp(
            "ERROR could not log off", client.id, client.tcp_conn
        )
