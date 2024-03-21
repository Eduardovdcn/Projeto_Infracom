from socket import *
import rsa

FORMAT = 'utf-8'

class Certificadora():
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Certificadora, cls).__new__(cls)
            cls.chaves_pub = {}
            cls.endereco = ('localhost', 8090)
            cls.socket = socket(AF_INET, SOCK_DGRAM) 
            cls.socket.bind(cls.endereco)
        return cls._instance

    def __init__(self): #Cada chave publica corresponde ao id do no
        self.chaves_pub = {}
        self.endereco = ('localhost', 8090)
        self.socket = socket(AF_INET, SOCK_DGRAM) 
        self.socket.bind(self.endereco)

    def rcv_pubkey(self, id):   #Recebe a chave pub na certificacao
        chave_pub_bytes = self.socket.recv(117).decode(FORMAT)
        chave_pub = rsa.PublicKey.load_pkcs1(chave_pub_bytes)
        self.chaves_pub[id] = chave_pub
        print(self.chaves_pub[id])

