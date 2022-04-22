"""
server_main.py

- The main script for the server. Establishes udp and tcp connections and
 listens for messages.

- protocol message functionality moved to server_messages for readability.
 The main script parses messages and detects protocols only.

- Tcp and udp servers are run concurrently in a mulitprocessing pool to allow
 for new client connections and inter-client messaging.
"""

import coloredlogs
import logging
import server_config as cfg
import server_messaging
import subscriber
import socket
import data_manager
import threading
import time

logging.basicConfig(
    level=logging.DEBUG,
)
coloredlogs.install(
    level='DEBUG', logger=logging.getLogger(__name__),
    fmt='%(levelname)s %(message)s')


def udp(subscribers):
    buffer_size = 2048
    s_udp_ip = '127.0.0.1'
    s_udp_port = 12000

    # Bind UDP socket to address and ip
    cfg.S_UDP_SOCKET.bind((s_udp_ip, s_udp_port))

    # UDP Server Loop
    print('UDP server listening...')
    while(True):
        # Bytes received by the socket are formatted in a length 2 tuple:
        # message, address
        bytes_recv = cfg.S_UDP_SOCKET.recvfrom(buffer_size)
        if bytes_recv is None:
            continue

        c_message = bytes_recv[0].decode("utf-8")

        if len(c_message) < 1:
            continue
        cfg.C_UDP_ADDRESS = bytes_recv[1]
        print("Message received: {} ".format(c_message))
        logging.info("Client IP, port: {}".format(cfg.C_UDP_ADDRESS))

        # Is the message a protocol message? (a command for the server)
        # SYNTAX OF PROTOCOL MESSAGES: !PROTOCOL ARG1 ARG2 ARGn...
        if server_messaging.is_protocol(c_message):
            c_message = c_message[1:]
            protocol_split = c_message.split()
            protocol_type = protocol_split[0]
            protocol_args = protocol_split[1:]
            logging.debug(
                "Protocol message detected, type = {}".format(protocol_type))

            # !HELLO
            if protocol_type == 'HELLO':
                c_id = protocol_args[0]
                challenge_rand = server_messaging.protocolHello(
                    c_id, subscribers)

            # !RESPONSE
            elif protocol_type == 'RESPONSE':
                c_id = protocol_args[0]
                res = protocol_args[1]
                # if protocolResponse returns true, client is authenticated
                if (
                    server_messaging.protocolResponse(
                        c_id, res, challenge_rand, subscribers)
                   ):
                    client = data_manager.getSubscriber(
                        client_id=c_id, subscribers=subscribers)
                    client.authenticated = True

            # Not a recognized protocol
            else:
                logging.error(
                    "{} is not a recognized protocol".format(protocol_type))

        # non-protocol messages
        else:
            logging.debug("Client message is not a protocol message.\n")


def tcp(subscribers):
    # store sessions
    chat_sessions = []
    # store connected clients to avoid iterating through all subs
    connected_clients = []

    n = 10  # n will be the number of users we have
    cfg.S_TCP_SOCKET = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM)
    cfg.S_TCP_SOCKET.bind(
        (cfg.S_TCP_IP, cfg.S_TCP_PORT))
    cfg.S_TCP_SOCKET.listen(n)
    print("TCP server is listening...")

    while(True):
        c_tcp_conn, c_tcp_ip_port = cfg.S_TCP_SOCKET.accept()
        print("TCP connection established, launching thread...")
        threading.Thread(
            target=tcp_connection,
            args=(
                c_tcp_conn, c_tcp_ip_port, chat_sessions,
                connected_clients)).start()


def tcp_connection(c_tcp_conn, c_tcp_ip_port,
                   chat_sessions, connected_clients):
    buffer_size = 1024

    client: subscriber.Subscriber = None
    c_tcp_ip = c_tcp_ip_port[0]
    c_tcp_port = c_tcp_ip_port[1]

    print("TCP connection thread created!: {} {}".format(
        c_tcp_ip, c_tcp_port), flush=True)

    # Receive CONNECT from client to attach client to connection
    while True:
        bytes_recv = c_tcp_conn.recv(buffer_size)
        if bytes_recv is None:
            continue

        s_message = bytes_recv.decode("utf-8")

        if len(s_message) < 1:
            continue

        if server_messaging.is_protocol(s_message):
            s_message = s_message[1:]  # remove !
            protocol_split = s_message.split()
            protocol_type = protocol_split[0]
            protocol_args = protocol_split[1:]

            if protocol_type != "CONNECT":
                logging.error(
                    "Expected CONNECT, received {}".format(protocol_type))
                continue

            elif protocol_type == "CONNECT":
                cookie = protocol_args[0]

                # attach client to connection thread, give client connection
                # object for messaging
                client = server_messaging.protocolConnect(
                    cookie, c_tcp_ip, c_tcp_port, c_tcp_conn, subscribers)
                client.tcp_conn = c_tcp_conn
                connected_clients.append(client)
                break

    print(
        "TCP event loop started: {} {}".format(c_tcp_ip, c_tcp_port),
        flush=True)

    # TCP event loop
    logged_in = True
    while logged_in:
        bytes_recv = c_tcp_conn.recv(buffer_size)
        if bytes_recv is None:
            continue

        s_message = bytes_recv.decode("utf-8")

        if len(s_message) < 1:
            continue

        print(
            "TCP message from {}: {}".format(client.id, s_message), flush=True)

        if server_messaging.is_protocol(s_message):
            s_message = s_message[1:]   # remove !
            protocol_split = s_message.split()
            protocol_type = protocol_split[0]
            protocol_args = protocol_split[1:]
            logging.debug(
                "Protocol message detected, type = {}".format(protocol_type))

            # !CHAT_REQUEST Client requests chat session
            if protocol_type == "CHAT_REQUEST":
                new_session = server_messaging.protocolChatRequest(
                    protocol_args=protocol_args, client_a=client,
                    connected_clients=connected_clients)

                # If session created, add to chat_sessions list
                if new_session is not None:
                    chat_sessions.append(new_session)

            # !END_REQUEST Client requests to end chat session.
            # End chat session and remove from chat_sessions.
            if protocol_type == "END_REQUEST":
                server_messaging.protocolEndRequest(client, chat_sessions)

        # non-protocol messages
        else:
            # log off
            if s_message.strip().lower() == "log off":
                logged_in = False

            # client is chatting, send message to partner
            elif client.chat_session is not None:
                partner: subscriber.Subscriber = (
                    client.chat_session.getPartner(client))
                message = f"[{client.id}]: {s_message}"
                server_messaging.send_message_tcp(
                    message=message, client_id=partner.id,
                    c_tcp_conn=partner.tcp_conn
                )

            else:
                logging.warn(
                    "TCP {} {}: {} is not a protocol message.\n".format(
                        s_message, c_tcp_ip, c_tcp_port))

    # log off client
    server_messaging.logOff(
        client=client, chat_sessions=chat_sessions,
        connected_clients=connected_clients)


if __name__ == '__main__':
    # load subscriber list from data file. pass to udp and tcp as shared
    # list
    try:
        subscribers = data_manager.loadSubscribers("subscribers.data")
    except Exception:
        subscribers = data_manager.loadSubscribers("./server/subscribers.data")

    threading.Thread(
        target=udp, args=(subscribers,)).start()
    threading.Thread(
        target=tcp, args=(subscribers,)).start()
