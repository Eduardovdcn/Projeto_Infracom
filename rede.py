from socket import *
import json
FORMAT = 'utf-8'
HEADER = 256

class Rede():
    def __init__(self): #Cada chave publica corresponde ao id do no
        self.inicio = None
        self.ultimo = None
        self.cont = 0 
        self.clientes = [
            ('127.0.0.1', 8080),
            ('127.0.0.1', 8081),
            ('127.0.0.1', 8082),
            ('127.0.0.1', 8083),
            ('127.0.0.1', 8084),
            ('127.0.0.1', 8085)
        ]
        self.endereco = ('localhost', 8050)
        self.socket = socket(AF_INET, SOCK_DGRAM) 
        self.socket.bind(self.endereco)
        self.roteamento = [
        [0, 'prox', 'prox', 'prox', 'ant', 'ant'],
        ['ant', 0, 'prox', 'prox', 'prox', 'ant'],
        ['ant', 'ant', 0, 'prox', 'ant', 'ant'],
        ['prox', 'ant', 'ant', 0, 'prox', 'prox'],
        ['prox', 'prox', 'ant', 'ant', 0, 'prox'],
        ['prox', 'prox', 'prox', 'ant', 'ant', 0]
        ]

    def insert(self, id, endereco):
        if id == 5:
            self.socket.sendto(f'{self.clientes[id-1]}+{self.clientes[0]}'.encode(FORMAT), endereco)
        else:
            self.socket.sendto(f'{self.clientes[id-1]}+{self.clientes[id+1]}'.encode(FORMAT), endereco)

    def routing(self, emissor, remetente):
            msg = self.socket.recv(tam_msg).decode(FORMAT)
            prox = self.roteamento[emissor.id][remetente.id]

            if prox == 'ant': 
                prox_emissor = emissor.ant
            else:
                prox_emissor = emissor.prox

            emissor.send_header(remetente)
            emissor.socket.sendto(msg.encode(FORMAT), prox_emissor.endereco)

            if prox_emissor != remetente:
                tam_msg = prox_emissor.socket.rcv(HEADER).decode(FORMAT)
                msg_rcv = prox_emissor.socket.rcv(tam_msg).decode(FORMAT)
                return self.routing(self, prox_emissor, remetente, msg_rcv, tam_msg)
            else:
                return msg_rcv

    def getClient(self, id_cliente):
        return self.clientes[id_cliente]
        
    def listen(self):
        while True:
            print('123')
            msg, endereco = self.socket.recvfrom(1024)
            print(msg)

            if msg.startswith(b'Qual eh o meu id'):
                self.socket.sendto(str(self.cont).encode(FORMAT), ('localhost', 8097))
                self.cont += 1

            elif msg.startswith(b'Insira-me'):
                id = msg.split(maxsplit=1)[1].decode(FORMAT)
                id = int(id)
                self.insert(id, endereco)

            elif msg.startswith(b'Esperando criar clientes... '):
                self.socket.sendto(str(self.cont).encode(FORMAT), endereco)

            elif msg.startswith(b'Quero_me_conectar_com'):
                id = msg.split(maxsplit=1)[1]
                id = int(id)
                cliente = self.getClient(id)
                self.socket.sendto(str(self.clientes[id]).encode(FORMAT), cliente)

            elif msg.startswith(b'O endereco do remetente eh'):
                self.routing()


rede = Rede()
rede.listen()        