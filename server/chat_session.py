"""
chat_session.py
author: Tim Tersigni

- Chat session object that tracks participating subscribers and session id
"""

import coloredlogs
import logging
from subscriber import Subscriber
import os

logging.basicConfig(
    level=logging.DEBUG,
)
coloredlogs.install(
    level='DEBUG', logger=logging.getLogger(__name__),
    fmt='%(levelname)s %(message)s')


class Chat_Session(object):
    def __init__(self, client_a: Subscriber, client_b: Subscriber, id):
        self.client_a = client_a
        self.client_b = client_b
        self.id = id
        self.clients = [client_a, client_b]
        self.log_file_path = self.createLog()

    def __eq__(self, other):
        if self.id == other.id:
            for c in self.clients():
                if not other.containsClient():
                    return False
            return True
        return False

    def createLog(self) -> str:
        try:
            log_name = f"{self.id}.log"
            log_file_path = os.path.join(os.getcwd(), "chat_logs", log_name)
            f = open(log_file_path, "w")
            f.close()
            return log_file_path
        except Exception:
            logging.critical(f"Could not create log file for {self.id}")

    def addToLog(self, id, message: str):
        new_line = f"{id} {message}"

        with open(self.log_file_path, 'a') as f:
            f.write(f"{new_line}\n")
            f.close()

    def deleteLog(self) -> str:
        try:
            os.remove(self.log_file_path)

        except Exception:
            logging.critical(f"Could not delete {self.log_file_path}")

    def getLogContents(self) -> list:
        with open(self.log_file_path, 'r') as f:
            lines = f.readlines()
            f.close()
            return lines

    # Return a clients chat partner
    def getPartner(self, client) -> Subscriber:
        for c in self.clients:
            if c != client:
                return c

    # Check if client is in chat session
    def containsClient(self, client: Subscriber) -> bool:
        for c in self.clients:
            c: Subscriber
            if c.id == client.id:
                return True
        return False

    # End the chat session
    def end(self):
        try:
            for c in self.clients:
                if c.chat_session is not None:
                    c.chat_session = None
            return True
        except Exception:
            return False
