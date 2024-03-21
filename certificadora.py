from socket import *

FORMAT = 'utf-8'

class Certificadora():
    def __init__(self): #Cada chave publica corresponde ao id do no
        self.chaves_pub = {}
        self.endereco = ('localhost', 6060)
        self.socket = socket(AF_INET, SOCK_DGRAM)

    def rcv_pubkey(self, id):   #Recebe a chave pub na certificacao
        pubkey = self.socket.rcv(256).decode(FORMAT)
        self.chaves_pub[id] = pubkey
