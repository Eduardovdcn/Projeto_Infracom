from rede import Rede
from socket import *
import rsa
from Crypto.Cipher import AES 
from Crypto.Random import get_random_bytes

HEADER = 256
FORMAT = 'utf-8'

class Cliente():    #Cada no eh um processo com socket e chaves unicas
    def __init__(self, roteamento_dir, roteamento_esq, id):
        self.id = id
        self.dir = roteamento_dir
        self.esq = roteamento_esq
        self.socket = socket(AF_INET, SOCK_DGRAM) 
        self.endereco = ('localhost', 5050+self.id)
        self.chave_priv = None 
        self.chave_sim = {}
        self.lista_threads = []
        self.conexao = {0: False, 1: False, 2: False, 3: False, 4: False, 5:False}

    def certificate(self, certificadora):      #Cria as chaves assimetricas de cada no (pub na certificadora e priv no cliente)
        chave_pub, chave_priv = rsa.newkeys(256)

        self.chave_priv = chave_priv
        self.socket.sendto(chave_pub.encode(FORMAT), certificadora.endereco)

        certificadora.rcv_pubkey(self.id)

    def key_exchange(self, certificadora, dupla):       #Cria e troca as chaves simetricas
        chave = get_random_bytes(16)
        self.chave_sim[dupla.id] = chave
        chave_cript = rsa.encrypt(chave.encode(), certificadora.chaves_pub[dupla.id])
        self.send_header(chave_cript, dupla)
        self.socket.sendto(chave_cript.encode(FORMAT), dupla.endereco)

    def handle_key(self, emissor, certificadora):       #Cria nova chave simetrica e envia criptografia assimetrica ou recebe a chave criptografada
        msg_length = self.socket.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = self.socket.recv(msg_length).decode(FORMAT)
            msg_descripto = rsa.decrypt(msg, self.chave_priv.decode())

            if msg_descripto == 'oi, vamos trocar chaves':
                self.key_exchange(certificadora, emissor)

            else:
                self.chave_sim[emissor.id] = msg_descripto

    def ask_key(self, remetente, certificadora):    #Mensagem especifica para iniciar o chat e trocar as chaves simetricas
        print('Por favor, digite "oi, vamos trocar chaves" para iniciar o chat')
        msg = input()
        while msg != 'oi, vamos trocar chaves':
            print('Por favor, digite "oi, vamos trocar chaves" para iniciar o chat')
            msg = input()

        msg_cripto = rsa.encrypt(msg.encode(), certificadora.chaves_pub[remetente.id]) 
        self.send_header(msg_cripto)
        self.socket.sendto((msg_cripto).encode(FORMAT), remetente.endereco)

    def rcv_msg(self, emissor):     #Recebe mensagens
        msg_length = self.socket.recv(HEADER).decode(FORMAT)
        if msg_length:      #Caso a mensagem nao seja nula
            msg_length = int(msg_length)
            ciphertext, nonce, tag = self.socket.recv(msg_length).decode(FORMAT)    #Recebe a mensagem
            chave = self.chave_sim[emissor.id]

            cipher = AES.new(chave, AES.MODE_EAX, nonce=nonce)
            plaintext = cipher.decrypt(ciphertext)      #Descriptografa
            try:
                cipher.verify(tag)
                print("The message is authentic:", plaintext)
            except ValueError:
                print("Key incorrect or message corrupted")
        
    def send_msg(self, remetente, rede):
        msg = input()
        cipher = AES.new(self.chave_sim[remetente.id], AES.MODE_EAX)        #Criptografa a mensagem
        ciphertext, tag = cipher.encrypt_and_digest(msg)
        nonce = cipher.nonce

        self.send_header(msg, remetente)        #Envia o tamanho da mensagem
        rede.routing(self, remetente, )   #Envia a mensagem

    def communicate(self, certificadora, cliente):     #Envia mensagens criptografadas
        while self.conexao[cliente.id]:
            self.ask_key(remetente=cliente, certificadora=certificadora)    #Troca as chaves simetricas por meio de chaves assimetricas
            cliente.handle_key(emissor=self, certificadora=certificadora)
            self.handle_key(cliente, certificadora)

            for _ in range(5):      #Troca 5 mensagens
                self.send_msg(remetente=cliente)
                cliente.rcv_msg(emissor=self)
                cliente.send_msg(remetente=self)
                self.rcv_msg(emissor=cliente)

            self.conexao[cliente.id] = False        #Fecha a conexao
            cliente.conexao[self.id] = False

    def broadcast(self):
        send_msg = f'mensage de broadcast enviada por cliente {self.id}: aviso'
        self.socket.sendto(send_msg.encode(FORMAT), ('255.255.255.255', 5005))

        cliente = self.dir
        while (cliente.id != self.id):
            rcv_msg = cliente.socket.rcv(len(send_msg)).decode(FORMAT)
            print(rcv_msg)
            send_msg = f'mensage de broadcast recebida por cliente {self.id}: aviso'
            cliente.socket.sendto(send_msg.encode(FORMAT), self.endereco)

            cliente = cliente.dir