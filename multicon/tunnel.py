from threading import Thread
from servertunnel import ServerTunnel

#classe che gestisce le istanze dei tunnel
class TunnelManager:

    SERVERTUNNEL = []
    token = 0

    def gettoken(self):
        self.token = self.token + 1
        return self.token

    def __init__(self):
        pass

    def StartTunnelServer(self, serverconn):
        x = ServerTunnel(serverconn, self.gettoken())
        Thread(target=x.ReciveHandle).start()
        self.SERVERTUNNEL.append(x)

    def AddClientToTunnelServer(self, servertoken: int, clientconn):
        for servertun in self.SERVERTUNNEL:
            if servertun.servertoken == servertoken:
                servertun.AddClient(clientconn)
                return True
        return False

    def CeckHandle(self):
        while True:
            for servertun in self.SERVERTUNNEL:
                if servertun.status == False:
                    self.SERVERTUNNEL.remove(servertun)

    def StopTunnelServer(self, token: int):
        for servertun in self.SERVERTUNNEL:
            if servertun.servertoken == token:
                servertun.KillServer()
                break