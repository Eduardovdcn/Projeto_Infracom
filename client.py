from socket import *
import threading
import rsa
from Crypto.Cipher import AES as aes

class Certificadora():
    def __init__(self): #Cada chave publica corresponde ao id do no
        self.chaves_pub = {}

class Rede():
    def __init__(self): #Estrutura de lista duplamente ligada para representar a topologia em malha
        self.inicio = None
        self.ultimo = None

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
        self.id = #GERAR ID
        self.dir = roteamento_dir
        self.esq = roteamento_esq
        self.socket = None
        self.endereco = [] 
        self.chave_priv = None 
        self.chave_sim = {}
        self.thread = None

    def certificate(self, certificadora):      #Cria as chaves assimetricas de cada no (pub na certificadora e priv no cliente)
        chave_pub, chave_priv = rsa.newkeys(512)

        self.chave_priv = chave_priv
        certificadora.chaves_pub[self.id] = chave_pub

    def connect(self):      #Inicia a thread do socket para enviar mensagens
        self.socket = socket(AF_INET, SOCK_DGRAM) 
        self.endereco = #PENSAR EM COMO CRIAR ENDEREÇO

        self.thread = threading.Thread(target=self.communicate).start()
                
    def disconnect(self):
        self.socket.close()
        self.thread.join()

    def communicate(self, certificadora, posicao):      #Envia mensagens criptografadas
        ...

    def key_exchange(self, certificadora, dupla):       #Cria e troca as chaves simetricas
        chave = #GERAR COM AES
        self.chave_sim[dupla.id] = chave
        chave_cript = rsa.encrypt(chave.encode(), certificadora.chaves_pub[dupla.id])
        self.socket.sendto(chave_cript, dupla.endereco)

    def rcv(self, emissor, msg, certificadora):
        msg_descripto = rsa.decrypt(msg, self.chave_priv.decode())
        if msg_descripto == 'oi, vamos trocar chaves':
            self.key_exchange(certificadora, emissor)

    def send(self, remetente, certificadora):
        msg = input()
        msg_cripto = rsa.encrypt(msg.encode(), certificadora.chaves_pub[remetente.id]) 
        self.socket.sendto(msg_cripto, remetente.endereco)


def main():
    rede = Rede()
    certificadora = Certificadora()
    for i in range(6): #Criacao dos nos
        cliente = Cliente()
        rede.insert(cliente)
        cliente.certificate(certificadora)
        cliente.connect()

main()
