from connection import *
from servertunnelclient import *
from clienttunnel import ClientTunnel

import argparse

parser = argparse.ArgumentParser()

parser.add_argument("-Sa", "--server_address", type=str, nargs=1, help="ip address del server [host:port]")
parser.add_argument("-Ta", "--tunnel_address", type=str, nargs=1, help="ip address dell'interfaccia dove avviare il tunnel [host:port]")
parser.add_argument("-sa", "--service_address", type=str, nargs=1, help="ip del servizio a cui reindirizzare le connessioni [host:port]")
parser.add_argument("-t", "--token", type=int, nargs=1, help="token del server")

args = parser.parse_args()

def main():
    if args.server_address and ((args.tunnel_address and args.token) or args.service_address):
        args.server_address = args.server_address[0].split(":")
        if len(args.server_address) == 2:
            serip = args.server_address[0]
            serport = args.server_address[1]
            try:
                serport = int(serport)
            except:
                return False
        else:
            return False

        if args.tunnel_address:
            args.tunnel_address = args.tunnel_address[0].split(":")
            if len(args.tunnel_address) == 2:
                tip = args.tunnel_address[0]
                tport = args.tunnel_address[1]
                try:
                    tport = int(tport)
                except:
                    return False
            else:
                return False
            Client(tip, tport, serip, serport, args.token[0])

        if args.service_address:
            args.service_address = args.service_address[0].split(":")
            if len(args.service_address) == 2:
                sip = args.service_address[0]
                sport = args.service_address[1]
                try:
                    sport = int(sport)
                except:
                    return False
                Server(sip, sport, serip, serport)
            else:
                return False
    else:
        return False


def Client(tip, tport, serip, serport, token):
    try:
        x = SSLSoket(10, serip, serport)
        x.Connect()
        y = ClientTunnel(ConnWrapp(ConnClass(x.wsocket)), tport, tip, token)
        y.StartTunnel()
    except:
        print("ERRORE DI CONNESSIONE")
        exit()

def Server(sip, sport, serip, serport):
    try:
        x = SSLSoket(10, serip, serport )
        x.Connect()
        y = ServerTunnelClient(ConnWrapp(ConnClass(x.wsocket)), sport, sip)
        y.StartTunnel()
    except:
        print("ERRORE DI CONNESSIONE")
        exit()

x = main()
if x == False:
    print("PARAMETRI ERRATI")