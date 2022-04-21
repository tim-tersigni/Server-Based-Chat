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
import server_config

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
    chatting = False

    def __init__(self, id, key):
        self.id = id
        self.key = key

    def write_cookie(self):
        file_lines = ""
        try:
            f = open("subscribers.data", 'r')
        except Exception:
            f = open("./server/subscribers.data", 'r')

        for line in f.readlines():
            split_line = line.split(',')
            sub_id = split_line[0]
            if (sub_id == self.id):
                new_line = ','.join([line.strip(), self.cookie]) + '\n'
                file_lines += new_line
            else:
                file_lines += line
        try:
            with open("subscribers.data", 'w') as f:
                f.writelines(file_lines)

        except Exception:
            with open("./server/subscribers.data", 'w') as f:
                f.writelines(file_lines)

        print("Wrote cookie {} to client {}".format(self.cookie, self.id))


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


def getSubscriber(client_id) -> Subscriber:
    for s in server_config.SUBSCRIBERS:
        if s.id == client_id:
            return s
    return None


def getSubscriberFromCookie(cookie) -> Subscriber:
    with open("./subscribers.data", 'r') as f:
        for line in f:
            split_line = line.split(',')
            if len(split_line) < 3:
                logging.CRITICAL(
                    "{} had no cookie".format(split_line[0]))
                return None
            sub_cookie = split_line[2]

            if cookie == sub_cookie:
                sub_id = split_line[0]
                return getSubscriber(sub_id)

            logging.CRITICAL(
                "No subscriber found with cookie {}".format(cookie))
            return None
