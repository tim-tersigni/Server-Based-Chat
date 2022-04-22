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

    def logOff(self, subscribers):
        print("TODO Log off")
