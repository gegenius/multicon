from gestioneclient import ConnectionManager
from tunnel import TunnelManager
from threading import Thread
from connection import SSLSoket, ConnClass, ConnWrapp

try:
    SOCKET = SSLSoket(5, "0.0.0.0", 5555)
    TUNNELMANAGER = TunnelManager()
except:
    print("IMPOSSIBILE CREARE IL SOCKET")
    exit()

def main():
    while True:
        try:
            conn, addr = SOCKET.Accept()
        except:
            print("porcodio non funziona un cazzo")
        finally:
            conn = ConnWrapp(ConnClass(conn))
            Thread(target=ConnectionManager, args=(conn, addr, TUNNELMANAGER)).start()

main()