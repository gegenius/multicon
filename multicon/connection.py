import socket, json, ssl

preambolo = b'&&$&$&&'
datasplitpattern = b'$&&$'

#classe che consente di manipolare il socket del server
class SSLSoket:
    def __init__(self, timeout: int, ip: str, port: int):
        socket.timeout(timeout)
        print("timeout impostato a " + str(timeout))
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        print("socket creato")
        self.socket.bind((ip, port))
        print("bind server " + ip + ":" + str(port))
        self.socket.listen(10)
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.load_verify_locations("myCA.pem", 'myCA.key')
        self.wsocket = context.wrap_socket(self.socket, server_side=True)
        print("socket wrapped con ssl")

    def Accept(self):
        conn, addr = self.wsocket.accept()
        print("connessione accettata da " + str(addr))
        return conn, addr

    def Close(self):
        self.wsocket.close()

#gestisce la recezione e l'invio dei singoli pacchetti
class ConnClass:
    ERRORSTATUS = False

    def __init__(self, conn):
        self.connection = conn
        self.recvbuffer = b''

    def send(self, data):
        self.connection.send(data + preambolo)

    def recv(self):
        databuffer = b''
        while 1:
            databuffer = databuffer + self.connection.recv()
            if preambolo in databuffer:
                break
        databuffer = databuffer.split(preambolo)
        packet = self.recvbuffer + databuffer[0]
        self.recvbuffer = databuffer[1]
        return packet

    def Close(self):
        self.connection.close()

#classe che elabora eventuali json
class ConnWrapp:

    def __init__(self, ConnClassIstance: ConnClass):
        self.conn = ConnClassIstance

    def recv(self):
        packet = self.conn.recv()
        packet = packet.split(datasplitpattern)
        if len(packet) >= 2:
            packettype = packet[0]
            data = packet[1]
        else:
            return
        if packettype == b'json':
            return json.loads(data.decode())
        elif packettype == b'data':
            if len(packet) == 3:
                token = packet[2]
                return {'mode' : 'data', 'token' : int(token.decode()), 'data' : data}
            else:
                return data

    def send(self, data):
        if type(data) == bytes:
            self.conn.send(b'data' + datasplitpattern + data)
        if type(data) == dict:
            if len(data.keys()) == 3 and data["mode"] == "data":
                self.conn.send(b'data' + datasplitpattern + data["data"] + datasplitpattern + str(data["token"]).encode())
            else:
                self.conn.send(b'json' + datasplitpattern + json.dumps(data).encode())

    def Close(self):
        self.conn.Close()