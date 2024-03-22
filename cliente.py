from socket import *
import threading
import rsa
from Crypto.Cipher import AES 
from Crypto.Random import get_random_bytes

HEADER = 256
FORMAT = 'utf-8'

class Cliente():    #Cada no eh um processo com socketves unicas
    def __init__(self, rede_endereco, certificadora_endereco):
        self.rede_endereco = rede_endereco
        self.certificadora_endereco = certificadora_endereco
        self.socket = None
        self.socket_id = socket(AF_INET, SOCK_DGRAM)
        self.id = None
        self.endereco = None
        self.prox = None
        self.ant = None
        self.chave_priv = None 
        self.chave_sim = {}
        self.conexao = {0: False, 1: False, 2: False, 3: False, 4: False, 5: False}

    def create_socket(self):
        self.socket_id.bind(('localhost', 8097))
        self.socket_id.sendto(b'Qual eh o meu id', self.rede_endereco)
        id = self.socket_id.recv(1024).decode(FORMAT)
        self.id = int(id)
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.endereco = ('127.0.0.1', 8080+self.id)
        self.socket.bind(self.endereco)
        self.socket_id.close()

    def insert(self):
        self.socket.sendto('Insira-me '.encode(FORMAT)+str(self.id).encode(FORMAT), self.rede_endereco)
        msg = self.socket.recv(1024).decode(FORMAT)
        print(msg)
        self.ant, self.prox = msg.split('+')

    def certificate(self):      #Cria as chaves assimetricas de cada no (pub na certificadora e priv no cliente)
        chave_pub, chave_priv = rsa.newkeys(256)
        chave_pub_bytes = rsa.PublicKey.save_pkcs1(chave_pub)

        self.chave_priv = chave_priv
        self.socket.sendto(b'certificate '+chave_pub_bytes, self.certificadora_endereco)

    def connect(self, id):
        self.socket.sendto('Quero_me_conectar_com '.encode(FORMAT)+id.encode(FORMAT), self.rede_endereco)
        dupla_endereco = self.socket.recv(1024)

        return dupla_endereco

    def routing(self, endereco):
        self.socket.sendto('O endereco do remetente eh '.encode(FORMAT)+endereco.encode(FORMAT))

    def send(self, dupla_id, dupla_endereco):
        self.ask_key(dupla_id)
        self.handle_key(dupla_id)

        for _  in range(5):
            self.send_msg(dupla_id, dupla_endereco)
            self.rcv_msg(dupla_id)

        self.conexao[dupla_id] = False 
        return 'sair'

    def rcv(self, dupla_id, dupla_endereco):
        self.send_key(dupla_id)

        for _ in range(5):      #Troca 5 mensagens
                self.rcv_msg(dupla_id)
                self.send_msg(dupla_id, dupla_endereco)

        self.conexao[dupla_id] = False        #Fecha a conexao

    def key_exchange(self, dupla_id):       #Cria e troca as chaves simetricas
        chave = get_random_bytes(16)
        self.chave_sim[dupla_id] = chave
        self.socket.sendto(('Qual é a chave pública do cliente ?', dupla_id).encode(FORMAT), self.certificadora_endereco)
        chave_pub = self.socket.recv(1024).decode(FORMAT)
        chave_cript = rsa.encrypt(chave.encode(), chave_pub)
        # send_header(chave_cript, self.rede_endereco)
        self.socket.sendto(chave_cript.encode(FORMAT), self.rede_endereco)

    def send_key(self, dupla_id):    
        msg = self.socket.recv(1024).decode(FORMAT)
        msg_descripto = rsa.decrypt(msg, self.chave_priv.decode())
        if msg_descripto == 'oi, vamos trocar chaves':
            self.key_exchange(dupla_id)

    def handle_key(self, dupla_id):       #Cria nova chave simetrica e envia criptografia assimetrica ou recebe a chave criptografada
        msg = self.socket.recv(1024).decode(FORMAT)
        msg_descripto = rsa.decrypt(msg, self.chave_priv.decode())
        self.chave_sim[dupla_id] = msg_descripto

    def ask_key(self, dupla_id):    #Mensagem especifica para iniciar o chat e trocar as chaves simetricas
        print('Por favor, digite "oi, vamos trocar chaves" para iniciar o chat')
        msg = input()
        while msg != 'oi, vamos trocar chaves':
            print('Por favor, digite "oi, vamos trocar chaves" para iniciar o chat')
            msg = input()

        self.socket.sendto(('Qual é a chave pública do cliente ?', dupla_id).encode(FORMAT), self.certificadora_endereco)
        chave_pub_bytes = self.socket.recv(1024).decode(FORMAT)
        chave_pub = rsa.PublicKey.load_pkcs1(chave_pub_bytes)
        msg_cripto = rsa.encrypt(msg.encode(), chave_pub) 
        # send_header(msg_cripto.encode(FORMAT), self.rede_endereco)
        self.socket.sendto(msg_cripto.encode(FORMAT), self.rede_endereco)

    def rcv_msg(self, dupla_id):     #Recebe mensagens
        ciphertext, nonce, tag = self.socket.recv(1024).decode(FORMAT)    #Recebe a mensagem
        chave = self.chave_sim[dupla_id]

        cipher = AES.new(chave, AES.MODE_EAX, nonce=nonce)
        plaintext = cipher.decrypt(ciphertext)      #Descriptografa
        try:
            cipher.verify(tag)
            print("The message is authentic:", plaintext)
        except ValueError:
            print("Key incorrect or message corrupted")
        
    def send_msg(self, dupla_id, dupla_endereco):
        msg = input()
        cipher = AES.new(self.chave_sim[dupla_id], AES.MODE_EAX)        #Criptografa a mensagem
        ciphertext, tag = cipher.encrypt_and_digest(msg)
        nonce = cipher.nonce

        msg_cripto = (ciphertext, nonce, tag)
        self.socket.sendto(b'O endereco do remetente eh'+dupla_endereco.encode(FORMAT)+msg_cripto, self.rede_endereco)

    def broadcast(self):
        send_msg = f'mensage de broadcast enviada por cliente {self.id}: aviso'
        self.socket.sendto(send_msg.encode(FORMAT), ('255.255.255.255', 5005))

    def confirm_broadcast(self):
        msg = self.socket.recv(1024).decode(FORMAT)    #Recebe a mensagem
        print(msg)

        send_msg = f'mensage de broadcast recebida por cliente {self.id}: aviso'
        # send_header(send_msg, dupla)
        self.socket.sendto(send_msg.encode(FORMAT), self.endereco)

    def rcv_confirmation(self):
        msg = self.socket.recv(1024).decode(FORMAT)    #Recebe a mensagem
        print(msg)

    def create_node(self):
        self.create_socket()
        self.insert()
        self.certificate()

        return cliente

    def main(self):
        self.create_node()

        rede_cont = 0
        while True:
            if rede_cont == 6:
                for _ in range()
                dupla_endereco = self.connect(dupla_id)

                rcv_thread = threading.Thread(target=self.rcv, args=(dupla_id, dupla_endereco))
                rcv_thread.start()

                while True:
                    if self.send(dupla_id, dupla_endereco) == 'sair':
                        break
                
                self.conexao[dupla_id] = False

                # cliente.broadcast()
                # for _  in range(5):
                #     remetente.confirm_broadcast(cliente)
                #     cliente.rcv_confirmation()

                #     remetente = remetente.dir

            else:
                self.socket.sendto('Esperando criar clientes... '.encode(FORMAT), cliente.rede_endereco)
                rede_cont = self.socket.recv(1024)
                rede_cont = int(rede_cont)


cliente = Cliente(rede_endereco=('localhost', 8050), certificadora_endereco=('localhost', 8090))
cliente.main()