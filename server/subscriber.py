"""
subscriber.py
author: Tim Tersigni

- Defines Subscriber object for simple user info storage

- Initialize subscriber list from subscribers.data with loadSubscribers(). This
function is used on startup in server_config.py

- Return Subscriber object from client_id if the client is saved as a 
subscriber in server_config.SUBSCRIBERS
"""


import coloredlogs, logging
import server_config

logging.basicConfig(
    level=logging.DEBUG,
)
coloredlogs.install(level='DEBUG', logger=logging.getLogger(__name__), fmt='%(levelname)s %(message)s')

class Subscriber(object):
    xres = None # for use in authentication
    cookie = None # user cookie
    authenticated = False
    def __init__(self, id, key):
        self.id = id
        self.key = key

def loadSubscribers(file_path):
    # return list of Subscribers
    subscriber_file = open(file_path, 'r')
    subscribers = []
    for line in subscriber_file:
        split_line = line.split(',')
        sub_id = split_line[0]
        sub_key = split_line[1]
        s = Subscriber(id=sub_id, key=sub_key)
        subscribers.append(s)
    return subscribers

def getSubscriber(client_id):
    for s in server_config.SUBSCRIBERS:
        if s.id == client_id:
            return s
    return None