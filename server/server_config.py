import subscriber
import socket
try:
    SUBSCRIBERS = subscriber.loadSubscribers("subscribers.data")
except:
    SUBSCRIBERS = subscriber.loadSubscribers("./server/subscribers.data")
S_UDP_SOCKET = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
C_UDP_ADDRESS = None
S_TCP_SOCKET=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
S_TCP_PORT = 1234
XRES_LIST = []