from socket import *
import rsa

FORMAT = 'utf-8'

class Certificadora():
    def __init__(self): #Cada chave publica corresponde ao id do no
        self.chaves_pub = {}
        self.endereco = ('127.0.0.1', 8090)
        self.socket = socket(AF_INET, SOCK_DGRAM) 
        self.socket.bind(self.endereco)

    def listen(self):       #Recebe mensagens enquanto roda
        while True:
            msg, endereco = self.socket.recvfrom(1024)
            if msg.startswith(b'certificate'):      #Certifica o no (recebe a chave pub e salva)
                chave_pub_bytes = self.socket.recv(1024)
                id = endereco[1] - 8080
                chave_pub = rsa.PublicKey.load_pkcs1(chave_pub_bytes)
                self.chaves_pub[id] = chave_pub

            elif msg.startswith(b'Qual'):       #Envia a chave pub do no pelo id
                text, id = msg.split()
                remetente_id = int(id)
                print(self.chaves_pub[remetente_id])
                chave_pub_bytes = rsa.PublicKey.save_pkcs1(self.chaves_pub[remetente_id])
                self.socket.sendto(chave_pub_bytes, endereco)

certificadora = Certificadora()
certificadora.listen()