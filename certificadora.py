from socket import *
import rsa

FORMAT = 'utf-8'

class Certificadora():
    def __init__(self): #Cada chave publica corresponde ao id do no
        self.chaves_pub = {}
        self.endereco = ('127.0.0.1', 8090)
        self.socket = socket(AF_INET, SOCK_DGRAM) 
        self.socket.bind(self.endereco)

    def certificate(self):   #Recebe a chave pub na certificacao
        chave_pub_bytes, endereco = self.socket.recvfrom(117).decode(FORMAT)
        id = endereco[1] - 8080
        chave_pub = rsa.PublicKey.load_pkcs1(chave_pub_bytes)
        self.chaves_pub[id] = chave_pub
        print(self.chaves_pub[id])

    def send_pubkey(self):
        msg, endereco = self.socket.recvfrom(117).decode(FORMAT)
        msg, remetente_id = msg
        if msg == "Qual é a chave pública do cliente ?": 
            remetente_id = endereco[1] - 8080
            chave_pub_bytes = rsa.PublicKey.save_pkcs1(self.chaves_pub[remetente_id])
            self.socket.sendto((chave_pub_bytes).encode(FORMAT), endereco)

    def listen(self):
        print(self.endereco)
        while True:
            print('123')
            data, endereco = self.socket.recvfrom(1024)
            print(data)
            if data.startswith(b'certificate'):
                chave_pub_bytes = data.split(maxsplit=1)[1]
                print(chave_pub_bytes)
                id = endereco[1] - 8080
                chave_pub = rsa.PublicKey.load_pkcs1(chave_pub_bytes)
                self.chaves_pub[id] = chave_pub
                print(self.chaves_pub[id])

certificadora = Certificadora()
certificadora.listen()