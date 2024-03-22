from cliente import Cliente

FORMAT = 'utf-8'
HEADER = 256

def create_node():
    
    cliente = Cliente(roteamento_esq=rede.inicio, roteamento_dir=rede.ultimo, id=rede.cont, rede_endereco=('localhost', 8050), certificadora_endereco=('localhost', 8090))
    cliente.create_socket()
    rede.insert(cliente)
    cliente.certificate()

    return cliente

def send_header(self, msg, remetente):    #Define o tamanho da mensagem que sera mandada
        tamanho_msg = len(msg)
        tamanho_msg = str(tamanho_msg).encode(FORMAT)
        tamanho_msg = b' ' * (HEADER - len(tamanho_msg))

        self.socket.sendto(tamanho_msg, remetente.endereco)

def main():
    cliente = create_node()

    while True:
        if rede.cont == 6:
            id = input('Digite o ID do cliente que deseja se comunicar (200 para encerrar)')
            if id == 200: break
            remetente = rede.get_Client(id)

            cliente.ask_key(remetente)
            rede.routing(cliente, remetente)
            remetente.send_key(cliente)
            rede.routing(remetente, cliente)
            cliente.handle_key(remetente)

            for _  in range(5):
                cliente.send_msg(remetente)
                rede.routing(cliente, remetente)
                remetente.rcv_msg(cliente)
                rede.routing(remetente, cliente)
                remetente.send_msg(cliente)
                cliente.rcv_msg(remetente)

            cliente.conexao[remetente.id] = False
            remetente.conexao[cliente.id] = False

            cliente.broadcast()
            for _  in range(5):
                remetente.confirm_broadcast(cliente)
                rede.routing(remetente, cliente)
                cliente.rcv_confirmation()

                remetente = remetente.dir

main()