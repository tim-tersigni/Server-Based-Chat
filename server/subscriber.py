"""
subscriber.py
author: Tim Tersigni

- Defines Subscriber object for simple user info storage

- Initialize subscriber list from subscribers.data with loadSubscribers(). This
function is used on startup in server_config.py

- Return Subscriber object from client_id if the client is saved as a
 subscriber in server_config.SUBSCRIBERS
"""


import coloredlogs
import logging

logging.basicConfig(
    level=logging.DEBUG,
)
coloredlogs.install(
    level='DEBUG', logger=logging.getLogger(__name__),
    fmt='%(levelname)s %(message)s')


class Subscriber(object):
    xres = None  # for use in authentication
    cookie = None  # user cookie
    authenticated = False
    tcp_connected = False
    tcp_conn = None
    chat_session = None

    def __init__(self, id, key):
        self.id = id
        self.key = key

    def __eq__(self, other):
        return self.id == other.id

    def logOff(self, chat_sessions, connected_clients):
        # if in chat session, end it
        if self.chat_session is not None:
            # remove chat session from list and end it
            chat_sessions.remove(self.chat_session)
            self.chat_session.end()

        # Log off
        try:
            # remove self from connected clients
            connected_clients.remove(self)

            # delete subscriber object
            del self

            return True

        except Exception:
            return False
