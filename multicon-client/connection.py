import socket

import json
import ssl

preambolo = b'&&$&$&&'
datasplitpattern = b'$&&$'

#classe che consente di manipolare il socket del server
class SSLSoket:
    def __init__(self, timeout: int, ip: str, port: int):
        self.ip = ip
        self.port = port
        socket.timeout(timeout)
        print("timeout impostato a " + str(timeout))
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        print("socket creato")
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.load_verify_locations("myCA.pem")
        self.wsocket = context.wrap_socket(self.socket, server_hostname=ip)
        print("socket wrapped con ssl")

    def Connect(self):
        try:
            self.wsocket.connect((self.ip,self.port))
            return True
        except:
            return False

    def Close(self):
        self.wsocket.close()

#gestisce la recezione e l'invio dei singoli pacchetti
class ConnClass:
    ERRORSTATUS = False
    recvbuffer = b''

    def __init__(self, conn):
        self.connection = conn

    def send(self, data):
        self.connection.send(data + preambolo)

    def recv(self):
        databuffer = b''
        while 1:
            databuffer = databuffer + self.connection.recv(4080)
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
                return {'mode': 'data', 'token': int(token.decode()), 'data': data}
            else:
                return data

    def send(self, data):
        if type(data) == bytes:
            self.conn.send('data' + datasplitpattern + data)
        if type(data) == dict:
            if len(data.keys()) == 3 and data["mode"] == "data":
                self.conn.send(b'data' + datasplitpattern + data["data"] + datasplitpattern + str(data["token"]).encode())
            else:
                self.conn.send(b'json' + datasplitpattern + json.dumps(data).encode())

    def Close(self):
        self.conn.Close()