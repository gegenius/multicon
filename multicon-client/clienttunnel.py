from connection import *
from connectionmanager import *

from socketclient import SocketClient
from threading import Thread

class ClientTunnel:

    CONNECTIONS = []
    token = 0

    def gettoken(self):
        self.token = self.token + 1
        return self.token

    def __init__(self, conn: ConnWrapp, port: int, ip: str, tokenserver: int):
        self.serverconn = conn
        self.ip = ip
        self.port = port
        self.tokenserver = tokenserver
        self.s = socket.socket()

    def StartTunnel(self):
        self.serverconn.send({"mode" : "man", "data": "conn.cli", "token" : self.tokenserver})
        print("pacchetto di inizializzazione inviato")
        responce = self.serverconn.recv()
        print("pacchetto di inizializzazione ricevuto")
        if type(responce) == dict:
            if "data" in responce.keys() and "mode" in responce.keys():
                if responce['mode'] == 'man' and responce['data'] == 'notification.tunnel.start':
                    self.s.bind((self.ip, self.port))
                    self.s.listen()
                    Thread(target=self.ReciveHandle).start()
                    Thread(target=self.AcceptHandle).start()
                    print("TUNNEL AVVIATO")
                    return True
        return False

    def Close(self):
        for conn in self.CONNECTIONS:
            conn.close()
        try:
            self.serverconn.send({"mode" : "man", "data" : "notification.disconnect"})
        except:
            pass
        self.serverconn.Close()



    def AddSocket(self, token, socket):
        try:
            s = SocketClient(token, self.serverconn, socket)
        except:
            print("impossibile avviare il thread del socket")
            self.Close()
        finally:
            self.CONNECTIONS.append(s)
            return s.socket

    def CloseSocket(self, token):
        pass

    def ReciveHandle(self):
        try:
            while True:
                x = False
                data = self.serverconn.recv()
                if type(data) == dict:
                    if "data" in data.keys() and "token" in data.keys() and "mode" in data.keys():
                        if data["mode"] == "data":
                            for connection in self.CONNECTIONS:
                                if connection.token == data["token"]:
                                    connection.socket.send(data["data"])
                                    x = True
                                    break
                            if x == False:
                                print("token errati")
                        elif data["mode"] == "man":
                            ManElab(data, False, self)
        except ConnectionResetError or ssl.SSLEOFError:
            print("CONNESSIONE CON SERVER CRASHATA")
            self.Close()

    def AcceptHandle(self):
        while True:
            try:
                conn, addr = self.s.accept()
            except:
                print("errore nell'accettazione della connessione")
            finally:
                self.AddSocket(self.gettoken(), conn)
                print("nuovo socket creato " + str(addr))

    def CeckHandle(self):
        while True:
            for client in self.CONNECTIONS:
                if client.status == False:
                    self.CONNECTIONS.remove(client)