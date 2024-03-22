from socket import *
import rsa

FORMAT = 'utf-8'

class Certificadora():
    def __init__(self): #Cada chave publica corresponde ao id do no
        self.chaves_pub = {}
        self.endereco = ('127.0.0.1', 8090)
        self.socket = socket(AF_INET, SOCK_DGRAM) 
        self.socket.bind(self.endereco)

    def listen(self):
        print(self.endereco)
        while True:
            print('123')
            msg, endereco = self.socket.recvfrom(1024)
            print(msg)
            if msg.startswith(b'certificate'):
                chave_pub_bytes = msg.split(maxsplit=1)[1]
                print(chave_pub_bytes)
                id = endereco[1] - 8080
                chave_pub = rsa.PublicKey.load_pkcs1(chave_pub_bytes)
                self.chaves_pub[id] = chave_pub
                print(self.chaves_pub[id])

            elif msg.startswith(b'Qual'):
                remetente_id = endereco[1] - 8080
                chave_pub_bytes = rsa.PublicKey.save_pkcs1(self.chaves_pub[remetente_id])
                self.socket.sendto((chave_pub_bytes).encode(FORMAT), endereco)

certificadora = Certificadora()
certificadora.listen()