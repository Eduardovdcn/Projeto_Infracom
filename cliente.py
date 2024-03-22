from socket import *
import rsa
from Crypto.Cipher import AES 
from Crypto.Random import get_random_bytes

HEADER = 256
FORMAT = 'utf-8'

class Cliente():    #Cada no eh um processo com socket e chaves unicas
    def __init__(self, roteamento_dir, roteamento_esq, id, rede_endereco, certificadora_endereco):
        self.rede_endereco = rede_endereco
        self.certificadora_endereco = certificadora_endereco
        self.id = id
        self.dir = roteamento_dir
        self.esq = roteamento_esq
        self.chave_priv = None 
        self.chave_sim = {}
        self.conexao = {0: False, 1: False, 2: False, 3: False, 4: False, 5:False}

    def create_socket(self):
        self.socket = socket(AF_INET, SOCK_DGRAM) 
        self.endereco = ('127.0.0.1', 8080+self.id)
        print(self.endereco)
        self.socket.bind(self.endereco)

    def certificate(self):      #Cria as chaves assimetricas de cada no (pub na certificadora e priv no cliente)
        chave_pub, chave_priv = rsa.newkeys(256)
        chave_pub_bytes = rsa.PublicKey.save_pkcs1(chave_pub)

        self.chave_priv = chave_priv
        self.socket.sendto(b'certificate '+chave_pub_bytes, self.certificadora_endereco)

    def send(self, dupla):
        self.ask_key(dupla)
        self.handle_key(dupla)

        for _  in range(5):
            self.send_msg(dupla)
            self.rcv_msg(dupla)

        self.conexao[dupla.id] = False 

    def rcv(self, dupla):
        self.send_key(dupla)

        for _ in range(5):      #Troca 5 mensagens
                self.rcv_msg(dupla)
                self.send_msg(dupla)

        self.conexao[dupla.id] = False        #Fecha a conexao

    def key_exchange(self, dupla):       #Cria e troca as chaves simetricas
        chave = get_random_bytes(16)
        self.chave_sim[dupla.id] = chave
        self.socket.sendto(('Qual é a chave pública do cliente ?', dupla.id).encode(FORMAT), self.certificadora_endereco)
        chave_pub = self.socket.recv(117).decode(FORMAT)
        chave_cript = rsa.encrypt(chave.encode(), chave_pub)
        # send_header(chave_cript, self.rede_endereco)
        self.socket.sendto(chave_cript.encode(FORMAT), self.rede_endereco)

    def send_key(self, dupla):
        tam_msg = self.socket.recv(HEADER).decode(FORMAT)
        if tam_msg:      #Caso a mensagem nao seja nula
            tam_msg = int(tam_msg)
            msg = self.socket.recv(tam_msg).decode(FORMAT)
            msg_descripto = rsa.decrypt(msg, self.chave_priv.decode())
            if msg_descripto == 'oi, vamos trocar chaves':
                self.key_exchange(dupla)

    def handle_key(self, dupla):       #Cria nova chave simetrica e envia criptografia assimetrica ou recebe a chave criptografada
        tam_msg = self.socket.recv(HEADER).decode(FORMAT)
        if tam_msg:      #Caso a mensagem nao seja nula
            tam_msg = int(tam_msg)
            msg = self.socket.recv(tam_msg).decode(FORMAT)
            msg_descripto = rsa.decrypt(msg, self.chave_priv.decode())
            self.chave_sim[dupla.id] = msg_descripto

    def ask_key(self, dupla):    #Mensagem especifica para iniciar o chat e trocar as chaves simetricas
        print('Por favor, digite "oi, vamos trocar chaves" para iniciar o chat')
        msg = input()
        while msg != 'oi, vamos trocar chaves':
            print('Por favor, digite "oi, vamos trocar chaves" para iniciar o chat')
            msg = input()

        self.socket.sendto(('Qual é a chave pública do cliente ?', dupla.id).encode(FORMAT), self.certificadora_endereco)
        chave_pub_bytes = self.socket.recv(117).decode(FORMAT)
        chave_pub = rsa.PublicKey.load_pkcs1(chave_pub_bytes)
        msg_cripto = rsa.encrypt(msg.encode(), chave_pub) 
        # send_header(msg_cripto.encode(FORMAT), self.rede_endereco)
        self.socket.sendto(msg_cripto.encode(FORMAT), self.rede_endereco)

    def rcv_msg(self, dupla):     #Recebe mensagens
        tam_msg = self.socket.recv(HEADER).decode(FORMAT)
        if tam_msg:      #Caso a mensagem nao seja nula
            tam_msg = int(tam_msg)
            ciphertext, nonce, tag = self.socket.recv(tam_msg).decode(FORMAT)    #Recebe a mensagem
            chave = self.chave_sim[dupla.id]

            cipher = AES.new(chave, AES.MODE_EAX, nonce=nonce)
            plaintext = cipher.decrypt(ciphertext)      #Descriptografa
            try:
                cipher.verify(tag)
                print("The message is authentic:", plaintext)
            except ValueError:
                print("Key incorrect or message corrupted")
        
    def send_msg(self, dupla):
        msg = input()
        cipher = AES.new(self.chave_sim[dupla.id], AES.MODE_EAX)        #Criptografa a mensagem
        ciphertext, tag = cipher.encrypt_and_digest(msg)
        nonce = cipher.nonce

        msg_cripto = (ciphertext, nonce, tag)
        # send_header(msg_cripto, dupla)
        self.socket.sendto((msg_cripto, dupla.id), self.rede_endereco)

    def broadcast(self):
        send_msg = f'mensage de broadcast enviada por cliente {self.id}: aviso'
        # send_header(send_msg)
        self.socket.sendto(send_msg.encode(FORMAT), ('255.255.255.255', 5005))

    def confirm_broadcast(self, dupla):
        tam_msg = self.socket.recv(HEADER).decode(FORMAT)
        if tam_msg:      #Caso a mensagem nao seja nula
            tam_msg = int(tam_msg)
            msg = self.socket.recv(tam_msg).decode(FORMAT)    #Recebe a mensagem
            print(msg)

            send_msg = f'mensage de broadcast recebida por cliente {self.id}: aviso'
            # send_header(send_msg, dupla)
            self.socket.sendto(send_msg.encode(FORMAT), self.endereco)

    def rcv_confirmation(self):
        tam_msg = self.socket.recv(HEADER).decode(FORMAT)
        if tam_msg:      #Caso a mensagem nao seja nula
            tam_msg = int(tam_msg)
            msg = self.socket.recv(tam_msg).decode(FORMAT)    #Recebe a mensagem
            print(msg)