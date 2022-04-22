"""
chat_session.py
author: Tim Tersigni

- Chat session object that tracks participating subscribers and session id
"""

from subscriber import Subscriber


class Chat_Session(object):
    def __init__(self, client_a: Subscriber, client_b: Subscriber, id):
        self.client_a = client_a
        self.client_b = client_b
        self.id = id
        self.clients = [client_a, client_b]

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
                c.chat_session = None
                return True
        except Exception:
            return False
