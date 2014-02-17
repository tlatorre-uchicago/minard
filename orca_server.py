import socket
from threading import Thread
from functools import partial
import time

def orca_server(clientsocket, filename):
    while True:
        with open(filename,'rb') as f:
            for msg in iter(partial(f.read,256),''):
                clientsocket.sendall(msg)
                time.sleep(2e-3)

if __name__ == '__main__':
    import sys

    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind(('localhost',44666))
    serversocket.listen(1)

    while True:
        clientsocket, address = serversocket.accept()
        try:
            orca_server(clientsocket,sys.argv[1])
        except socket.error:
            continue
