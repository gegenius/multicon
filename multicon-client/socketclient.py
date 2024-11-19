from connection import *
from threading import Thread

class SocketClient:

    status = True

    def __init__(self, token: int, serversocket: ConnWrapp, sock: socket.socket):
        self.serversocket = serversocket
        self.token = token
        self.socket = sock
        Thread(target=self.ReciveHandle).start()

    def Close(self):
        print("socket crashato")
        try:
            self.serversocket.send({"mode":"man", "data":"notification.disconnect.client", "token":self.token})
        except:
            pass
        self.socket.close()
        self.status = False

    def ReciveHandle(self):
        try:
            while True:
                data = self.socket.recv(4080)
                if data == b'':
                    self.Close()
                    return
                self.serversocket.send({'mode' : 'data', 'token' : self.token, 'data' : data})
        except ConnectionResetError:
            self.Close()