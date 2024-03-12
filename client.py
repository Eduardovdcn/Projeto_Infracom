from socket import *
import threading
import rsa

server_address = (4080, 'localhost')

class Certificadora():
    def __init__(self): #Cada chave publica corresponde a posicao de criação do no
        self.lista_chaves = []

class Rede():
    def __init__(self, roteamento_dir, roteamento_esq): #Estrutura de lista duplamente ligada para representar a topologia em malha
        self.inicio = None
        self.ultimo = None
        self.dir = roteamento_dir
        self.esq = roteamento_esq

    def insert(self, cliente):
        if self.inicio == None: self.inicio = cliente
        
        if self.ultimo != None:
            cliente.esq = self.ultimo
            self.ultimo.dir = cliente
            cliente.dir = self.inicio
            self.inicio.esq = cliente

        self.ultimo = cliente

class Cliente():    #Cada no eh um processo com socket e chaves unicas
    def __init__(self, roteamento_dir, roteamento_esq):
        self.dir = roteamento_dir
        self.esq = roteamento_esq
        self.socket = None
        self.chave_priv = None 

    def certificate(self, certificadora, posicao):      #Cria as chaves e deixa salvas
        chave_pub, chave_priv = rsa.newkeys(512)

        self.chave_priv = chave_priv
        certificadora.lista_chaves[posicao] = chave_pub

    def connect(self):      #Inicia a thread do socket para enviar mensagens
        self.socket = socket(AF_INET, SOCK_DGRAM) 

        threading.Thread(target=self.communicate).start()

    def communicate(self, certificadora, posicao):      #Envia mensagens criptografadas
        while True:
            mensagem = input('')
            enc_mensagem = rsa.encrypt(mensagem.encode(), self.chave_priv)
            dec_mensagem = rsa.decrypt((enc_mensagem, certificadora.lista_chaves[posicao]).decode())

    def disconnect(self):
        self.socket.close()

def rcv():
    ...

def snd():
    ...

def main():
    rede = Rede()
    certificadora = Certificadora()
    for i in range(6): #Criacao dos nos
        cliente = Cliente()
        cliente.certificate(certificadora, i)
        cliente.connect()
