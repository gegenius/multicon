from gestioneclient import DictElaboration
import ssl

#gestisce la connessione del singolo client
class ClientTunnel():

    SOCKETS = []
    status = True

    def __init__(self, token: int, serverconn, clientconn, servertoken: int):
        self.token = token
        self.servertoken = servertoken
        self.serverconn = serverconn
        self.clientconn = clientconn

    def ReciveHandle(self):
        try:
            while True:
                packet = self.clientconn.recv()
                if type(packet) == dict:
                    try:
                        packet["token"] = packet["token"] + self.servertoken
                    except:
                        pass
                    if packet["mode"] == "man":
                        DictElaboration(packet, False, self)
                    elif packet["mode"] == "data":
                        self.serverconn.send(packet)
                        if self.IsSocket(packet["token"]) == False:
                            self.SOCKETS.append(packet["token"])
                            print("----------------\n")
                            for z in self.SOCKETS: print(str(z) + "\n")
                            print("----------------")

        except ConnectionResetError or ssl.SSLEOFError:
            print("crash connessione client")
            self.Stop

    def IsSocket(self, token):
        if token in self.SOCKETS:
            return True
        else:
            return False

    def CloseClient(self, token: int):
        self.SOCKETS.remove(token)
        self.serverconn.send({"mode":"man", "token": token, "data":"notification.disconnect.client"})
        print("chiusa la connessione " + str(token))

    def Stop(self):
        print("client " + str(self.token) + " disconnesso")
        for socket in self.SOCKETS:
            self.serverconn.send({'mode': 'man', 'data': 'notification.disconnect.client', 'token': socket})
            print("connessione " + str(socket) + " chiusa")
        try:
            self.clientconn.send({"mode" : 'man', 'data' : 'notification.disconnect'})
        except:
            pass
        self.clientconn.Close()
        self.status = False