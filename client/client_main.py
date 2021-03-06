"""
client_main.py

- The main script for an individual client.

- udp() is used during authentication. After client receives authentication
udp() launches tcp() as udp is not used following authentication.

- protocol message functionality moved to client_messages for readibility.
client_main.udp() receives and parses the messages only.

"""

import logging
import coloredlogs
import client_config as cfg
import client_messaging
import threading
import os
import time

logging.basicConfig(
    level=logging.WARNING,
)
coloredlogs.install(level='WARNING', logger=logging.getLogger(__name__),
                    fmt='%(levelname)s %(message)s')


def udp():
    # get client ID from input and get key if subscriber
    cfg.initialize()

    buffer_size = 1024

    # Send hello message to server for authentication
    client_messaging.send_message_udp(
        "!HELLO {}".format(cfg.CLIENT_ID))

    # Authentication loop
    while(cfg.LOGGED_IN):
        # Bytes received by the socket are formatted in a length 2 tuple:
        # message, address
        bytes_recv = cfg.C_UDP_SOCKET.recvfrom(buffer_size)
        if bytes_recv is None:
            continue

        s_message = bytes_recv[0].decode("utf-8")
        s_address_port = bytes_recv[1]
        logging.info("Server message: {} ".format(s_message))
        logging.info("Server IP, port: {}".format(s_address_port))

        # Check for protocol identifier !
        if client_messaging.is_protocol(s_message):
            s_message = s_message[1:]   # remove !
            protocol_split = s_message.split()
            protocol_type = protocol_split[0]
            protocol_args = protocol_split[1:]
            logging.debug(
                "Protocol message detected, type = {}".format(protocol_type))

            if protocol_type == 'CHALLENGE':
                client_messaging.protocolChallenge(protocol_args)

            elif protocol_type == 'AUTH_SUCCESS':
                client_messaging.protocolAuthSuccess(protocol_args)
                break

            elif protocol_type == 'AUTH_FAIL':
                logging.critical("Authentication failed!")
                break

            else:
                print('{} is not a recognized protocol.'.format(protocol_type))
                break

    # Client is authenticated
    if(cfg.AUTHENTICATED):
        print("TCP PORT IS {}".format(cfg.S_TCP_PORT))
        tcp()


def tcp():
    buffer_size = 1024

    s_tcp_ip = cfg.S_TCP_IP
    s_tcp_port = cfg.S_TCP_PORT
    c_tcp_socket = cfg.C_TCP_SOCKET
    c_tcp_socket.connect((s_tcp_ip, s_tcp_port))
    print("TCP Connected: {} {}".format(s_tcp_ip, s_tcp_port))
    cfg.LOGGED_IN = True  # for logging off

    # send CONNECT cookie to server
    message = "!CONNECT {}".format(cfg.COOKIE)
    client_messaging.send_message_tcp(message)

    # connection loop
    while(cfg.LOGGED_IN is True):
        bytes_recv = c_tcp_socket.recv(buffer_size)
        if bytes_recv is None:
            continue

        s_message = bytes_recv.decode("utf-8")

        if len(s_message.strip()) < 1:
            continue

        if client_messaging.is_protocol(s_message):
            s_message = s_message[1:]   # remove !
            protocol_split = s_message.split()
            protocol_type = protocol_split[0]
            logging.debug(
                "Protocol message detected, type = {}".format(protocol_type))

            if protocol_type == "CONNECTED":
                client_messaging.protocolConnected()
                break

            else:
                print('{} is not a recognized protocol.'.format(protocol_type))
                break

    # threading event to signal log off
    log_off_event = threading.Event()

    # create receiving thread to allow for sending and receiving messages
    threading.Thread(target=recv, args=(log_off_event,)).start()

    # user input daemon so typing does not interrupt script
    threading.Thread(
        target=chat_input, args=(log_off_event,), daemon=True).start()

    log_off_event.wait()


# run as thread for recieving messages when connected
def recv(log_off_event: threading.Event):
    while(log_off_event.is_set() is False):
        buffer_size = 1024

        bytes_recv = cfg.C_TCP_SOCKET.recv(buffer_size)
        if bytes_recv is None:
            continue

        s_message = bytes_recv.decode("utf-8")
        logging.debug("Message received: {}".format(s_message))

        if client_messaging.is_protocol(s_message):
            s_message = s_message[1:]   # remove !
            protocol_split = s_message.split()
            protocol_type = protocol_split[0]
            protocol_args = protocol_split[1:]
            logging.debug(
                "Protocol message detected, type = {}".format(protocol_type))

            if protocol_type == "CHAT_STARTED":
                client_messaging.protocolChatStarted(protocol_args)

            elif protocol_type == "UNREACHABLE":
                client_messaging.protocolUnreachable(protocol_args)

            elif protocol_type == "END_NOTIF":
                client_messaging.protocolEndNotif(protocol_args)

            elif protocol_type == "CHAT":
                client_messaging.protocolChat(protocol_args)

            elif protocol_type == "HISTORY_RESP":
                client_messaging.protocolHistoryResp(protocol_args)

            elif protocol_type == "WARNING":
                logging.warning(' '.join(protocol_args))


def chat_input(log_off_event: threading.Event):
    while(log_off_event.is_set() is False):
        inactive = threading.Event()
        # start inactivity timer thread
        timer = threading.Timer(
            600, checkInactive, args=(inactive, log_off_event))
        timer.start()

        # get input, cancel timer
        chat_input = input()
        timer.cancel()

        # filter out blank messages, then send
        if chat_input.strip() is not None:
            client_messaging.send_message_tcp(chat_input)

        # log off
        if chat_input.lower().strip() == "log off":
            log_off_event.set()


# function ran when inactivity timer is up
def checkInactive(inactive, log_off_event):
    print("Logging out for inactivity.")
    log_off_event.set()


if __name__ == '__main__':
    udp()

    # Log off
    time.sleep(0.5)
    print("Logged out successfully.")
    time.sleep(1)
    os.system('cls' if os.name == 'nt' else 'clear')
