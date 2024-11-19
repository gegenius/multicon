def ManElab(packet: dict, tunnelserver: bool, istance):
    if packet["data"] == "notification.disconnect":
        istance.KillTunnel()
    if packet["data"] == "notification.disconnect.client":
        istance.CloseSocket(packet["token"])