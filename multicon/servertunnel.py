from gestioneclient import DictElaboration
import socket
import ssl
from threading import Thread
from clienttunnel import ClientTunnel

#classe che permette il funzionamento del tunnel gesteno la connessione del server e quella dei client
class ServerTunnel:
    CLIENTCONNECTIONLIST = []
    tokencounter = 0
    status = True

    def gettoken(self):
        self.tokencounter = self.tokencounter + 1
        print("token " + str(self.tokencounter) + " generato per il server " + str(self.servertoken))
        return self.tokencounter

    def __init__(self, serverconn, token: int):
        self.serverconn = serverconn
        self.servertoken = token
        print("tunnel creato con token " + str(self.servertoken))

    def AddClient(self, clientconn):
        x = ClientTunnel(self.gettoken(), self.serverconn, clientconn, self.servertoken)
        Thread(target=x.ReciveHandle).start()
        clientconn.send({'mode' : 'man', 'data' : 'notification.tunnel.start'})
        print("istanza del nuovo client " + socket.gethostbyname(socket.gethostname()) + " con token " + str(x.token))
        print("thread del client " + str(x.token) + " iniziato")
        self.CLIENTCONNECTIONLIST.append(x)

    def CloseClient(self, token: int):
        for client in self.CLIENTCONNECTIONLIST:
            if client.token == token:
                client.Stop()
                self.CLIENTCONNECTIONLIST.remove(client)
                print("client " + str(token) + " disconnesso")
                break

    def KillServer(self):
        print("chiusura server " + str(self.servertoken))
        for client in self.CLIENTCONNECTIONLIST:
            client.Stop()
            self.CLIENTCONNECTIONLIST.remove(client)
            self.status = False
            break
        self.serverconn.Close()
        self.status = False

    def CeckHandle(self):
        while True:
            for servertun in self.CLIENTCONNECTIONLIST:
                if servertun.status == False:
                    self.CLIENTCONNECTIONLIST.remove(servertun)
                    print("istanza di un client disconnesso rimossa dalla memoria")
                if len(servertun.SOCKETS) > 10:
                    servertun.Close()

    def ReciveHandle(self):
        try:
            while True:
                x = True
                packet = self.serverconn.recv()
                if type(packet) == dict:
                    if packet['mode'] == 'man':
                        DictElaboration(packet, True, self)
                    elif packet['mode'] == 'data':
                        for client in self.CLIENTCONNECTIONLIST:
                            for socket in client.SOCKETS:
                                if socket == packet["token"]:
                                    client.clientconn.send({"mode" : "data", "token" : packet["token"] - self.servertoken, "data" : packet["data"]})
                                    x = False
                                    break
                            if x == False:
                                break
        except ConnectionResetError or ssl.SSLEOFError:
            print("CONNESSIONE CON HOSTER DEL TUNNEL " + str(self.servertoken()) + " CRASHATA")
            self.KillServer()