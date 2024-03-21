FORMAT = 'utf-8'
HEADER = 256

class Rede():
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Rede, cls).__new__(cls)
            # Inicialize os atributos da instância aqui, se necessário
        return cls._instance

    def __init__(self): #Estrutura de lista duplamente ligada para representar a topologia em malha
        self.inicio = None
        self.ultimo = None
        self.cont = 0
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
        self.cont += 1

    def routing(self, emissor, remetente, msg):
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

