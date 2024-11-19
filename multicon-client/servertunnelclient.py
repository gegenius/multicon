from connection import *
from socketclient import *
from connectionmanager import *
from threading import Thread

class ServerTunnelClient:

    CLIENTS = []

    def __init__(self, conn: ConnWrapp, port: int, ip: str):
        self.conn = conn
        self.ip = ip
        self.port = port

    def KillTunnel(self):
        for client in self.CLIENTS:
            client.Close()
        self.conn.Close()

    def StartTunnel(self):
        self.conn.send({'mode' : 'man', 'data': 'conn.ser'})
        responce = self.conn.recv()
        if type(responce) == dict:
            if responce['mode'] == 'man' and responce['data'] == 'notification.tunnel.start':
                Thread(target=self.ReciveHandle).start()
                print("TunnelServer avviato")
                return True
        return False

    def AddSocket(self, token):
        try:
            s = socket.socket()
            s.connect((self.ip, self.port))
        except:
            self.KillTunnel()
        finally:
            self.CLIENTS.append(SocketClient(token, self.conn, s))
            print("nuova connessione con token " + str(token))
            print("----------------\n")
            for x in self.CLIENTS: print(str(x.token) + "\n")
            print("----------------")
            return s

    def ReciveHandle(self):
        try:
            while True:
                data = self.conn.recv()
                if type(data) == dict:
                    if "data" in data.keys() and "token" in data.keys() and "mode" in data.keys():
                        if data["mode"] == "data":
                            for client in self.CLIENTS:
                                if client.token == data["token"]:
                                    client.socket.send(data["data"])
                                    return
                            c = self.AddSocket(data["token"])
                            c.send(data["data"])

                        elif data["mode"] == "man":
                            ManElab(data, True, self)
        except ConnectionResetError or ssl.SSLEOFError:
            print("CONNESSIONE CON SERVER CRASHATA")
            self.KillTunnel()

    def CeckHandle(self):
        while True:
            for client in self.CLIENTS:
                if client.status == False:
                    self.CLIENTS.remove(client)

    def CloseSocket(self, token):
        for client in self.CLIENTS:
            if client.token == token:
                client.Close()
                self.CLIENTS.remove(client)
                return
        print("socket da chiudere non trovatro")