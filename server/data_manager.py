import coloredlogs
import logging
from subscriber import Subscriber
import threading
import os

LOCK = threading.Lock()
SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
if os.getcwd() != SERVER_DIR:
    os.chdir(SERVER_DIR)

logging.basicConfig(
    level=logging.DEBUG,
)
coloredlogs.install(
    level='DEBUG', logger=logging.getLogger(__name__),
    fmt='%(levelname)s %(message)s')


def getSubscriber(client_id, subscribers: list):
    for s in subscribers:
        if s.id == client_id:
            return s
    return None


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


def getSubscriberFromCookie(cookie, subscribers: list):
    for client in subscribers:
        if client.cookie == cookie:
            return client
    logging.critical(("Could not find client with cookie {}".format(cookie)))
    return None


def appendCookie(id, cookie):
    file_lines = []
    with open("subscribers.data", "r") as f:
        for line in f.readlines():
            split_line = line.split(',')
            sub_id = split_line[0]
            if (sub_id == id):
                new_line = ','.join([line.strip(), cookie]) + '\n'
                file_lines += new_line
            else:
                file_lines += line

    with open("subscribers.data", "w") as f:
        f.writelines(file_lines)
