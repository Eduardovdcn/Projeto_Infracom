FORMAT = 'utf-8'

class Rede():
    def __init__(self): #Estrutura de lista duplamente ligada para representar a topologia em malha
        self.inicio = None
        self.ultimo = None
        self.roteamento = [
        [0, 'dir', 'dir', 'dir', 'esq', 'esq'],
        ['esq', 0, 'dir', 'dir', 'dir', 'esq'],
        ['esq', 'esq', 0, 'dir', 'esq', 'esq'],
        ['dir', 'esq', 'esq', 0, 'dir', 'dir'],
        ['dir', 'dir', 'esq', 'esq', 0, 'dir'],
        ['dir', 'dir', 'dir', 'esq', 'esq', 0]
        ]

    def insert(self, cliente):
        if self.inicio == None: self.inicio = cliente
        
        if self.ultimo != None:
            cliente.esq = self.ultimo
            self.ultimo.dir = cliente
            cliente.dir = self.inicio
            self.inicio.esq = cliente

        self.ultimo = cliente

    def routing(self, emissor, remetente, msg, tam_msg):
        dir = self.roteamento[emissor.id][remetente.id]

        if dir == 'esq': 
            prox_emissor = emissor.esq
        else:
            prox_emissor = emissor.dir

        emissor.socket.sendto(msg.encode(FORMAT), prox_emissor.endereco)
        msg_rcv = prox_emissor.socket.rcv(tam_msg)

        if prox_emissor != remetente:
            return self.routing(self, prox_emissor, remetente, msg_rcv, tam_msg)
        else:
            return msg_rcv