import functools
import coloredlogs, logging
import server_config, server_messaging
import socket
from multiprocessing import Pool
import functools

logging.basicConfig(
    level=logging.DEBUG,
)
coloredlogs.install(level='WARNING', logger=logging.getLogger(__name__), fmt='%(levelname)s %(message)s')

def udp():
    buffer_size = 2048
    s_udp_ip = '127.0.0.1'
    s_udp_port = 12000

    # Bind UDP socket to address and ip
    server_config.S_UDP_SOCKET.bind((s_udp_ip, s_udp_port))

    # UDP Server Loop
    print('UDP server listening...')
    while(True):
        # Bytes received by the socket are formatted in a length 2 tuple:
        # message, address
        bytes_recv = server_config.S_UDP_SOCKET.recvfrom(buffer_size)
        if bytes_recv == None:
            continue

        c_message = bytes_recv[0].decode("utf-8")
        server_config.C_UDP_ADDRESS = bytes_recv[1]
        print("Message received: {} ".format(c_message))
        logging.info("Client IP, port: {}".format(server_config.C_UDP_ADDRESS))

        # Is the message a protocol message? (a command for the server)
        # SYNTAX OF PROTOCOL MESSAGES: !PROTOCOL ARG1 ARG2 ARGn...
        if server_messaging.is_protocol(c_message):
            c_message = c_message[1:]
            protocol_split = c_message.split()
            protocol_type = protocol_split[0]
            protocol_args = protocol_split[1:]
            logging.debug(
                "Protocol message detected, type = {}".format(protocol_type))

            # !HELLO
            if protocol_type == 'HELLO':
                c_id = protocol_args[0]
                challenge_rand = server_messaging.protocolHello(c_id)

            # !RESPONSE
            elif protocol_type == 'RESPONSE':
                c_id = protocol_args[0]
                res = protocol_args[1]

                # response protocol function returns the user's cookie, or None if auth failed
                cookie = server_messaging.protocolResponse(c_id, res, challenge_rand)
                if cookie != None:
                    # TODO store cookie
                    print("TODO store cookie")


            # Not a recognized protocol
            else:
                logging.error("{} is not a recognized protocol".format(protocol_type))

        # TODO: non-protocol messages
        else:
            logging.debug("Client message is not a protocol message.\n")

def tcp():
    n=1 #n will be the number of users we have
    s_tcp_ip = "127.0.0.1"

    server_config.S_TCP_SOCKET=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server_config.S_TCP_SOCKET.bind((s_tcp_ip,server_config.S_TCP_PORT))
    server_config.S_TCP_SOCKET.listen(n)
    print("TCP server is listening...")
    while(True):
        clientAddress=server_config.S_TCP_SOCKET.accept()
        print(f"TCP Connection Established: {clientAddress[0]}:{clientAddress[1]}")

# for multiprocessing
def smap(f):
    return f()

if __name__ == '__main__':
    #Run udp and tcp concurrently
    f_udp = functools.partial(udp, 1)
    f_tcp = functools.partial(tcp, 1)

    with Pool() as pool:
        res = pool.map(smap, [udp, tcp] )