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

    def getPartner(self, client):
        for c in self.clients:
            if c != client:
                return c
