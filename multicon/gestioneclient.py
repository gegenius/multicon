def NewConnectionManager(packet: dict, conn, TUNMAN):
    if packet["mode"] == 'man':
        if packet["data"] == 'conn.cli':
            return TUNMAN.AddClientToTunnelServer(packet["token"], conn)
        elif packet["data"] == 'conn.ser':
            TUNMAN.StartTunnelServer(conn)
            conn.send({"mode" : "man", "data" : "notification.tunnel.start"})
            return True
    return False

def DictElaboration(packet: dict, servertunnelmode: bool, istance):
    if packet["mode"] == 'man':
        if packet["data"] == 'notification.disconnect':
            if servertunnelmode == True:
                istance.KillServer()
            else:
                istance.Stop()
        if packet["data"] == 'notification.disconnect.client':
            istance.CloseClient(packet["token"])

def ConnectionManager(conn, addr, TUNMAN):
    for x in range(10):
        packet = conn.recv()
        if type(packet) == dict:
            feedback = NewConnectionManager(packet, conn, TUNMAN)
            if feedback == True:
                return
    print("il client " + addr + " ha impiegato tropppo tempo a cannettersi")
    conn.Close()