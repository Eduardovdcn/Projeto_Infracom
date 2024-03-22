from socket import *
FORMAT = 'utf-8'
HEADER = 256

class Rede():
    def __init__(self): #Cada chave publica corresponde ao id do no
        self.inicio = None
        self.ultimo = None
        self.cont = 0 
        self.clientes = []
        self.endereco = ('localhost', 8050)
        self.socket = socket(AF_INET, SOCK_DGRAM) 
        self.socket.bind(self.endereco)

    def insert(self, cliente):
        if self.inicio == None: self.inicio = cliente
        
        if self.ultimo != None:
            cliente.esq = self.ultimo
            self.ultimo.dir = cliente
            cliente.dir = self.inicio
            self.inicio.esq = cliente

        self.ultimo = cliente
        self.clientes.append(cliente)
        self.cont += 1

    def routing(self, emissor, remetente):
        tam_msg = self.socket.recv(HEADER).decode(FORMAT)
        if tam_msg:      #Caso a mensagem nao seja nula
            tam_msg = int(tam_msg)
            msg = self.socket.recv(tam_msg).decode(FORMAT)
            msg = self.socket.recv(tam_msg)
            dir = self.roteamento[emissor.id][remetente.id]

            if dir == 'esq': 
                prox_emissor = emissor.esq
            else:
                prox_emissor = emissor.dir

            emissor.send_header(remetente)
            emissor.socket.sendto(msg.encode(FORMAT), prox_emissor.endereco)

            if prox_emissor != remetente:
                tam_msg = prox_emissor.socket.rcv(HEADER).decode(FORMAT)
                msg_rcv = prox_emissor.socket.rcv(tam_msg).decode(FORMAT)
                return self.routing(self, prox_emissor, remetente, msg_rcv, tam_msg)
            else:
                return msg_rcv

    def get_Client(self, id_cliente):
        return self.clientes[id_cliente]
