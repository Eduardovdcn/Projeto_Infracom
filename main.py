from cliente import Cliente

FORMAT = 'utf-8'
HEADER = 256

def create_node():
    cliente = Cliente(rede_endereco=('localhost', 8050), certificadora_endereco=('localhost', 8090))
    cliente.insert(cliente)
    cliente.certificate()

    return cliente

def main():
    cliente = create_node()

    while True:
        if rede_cont == 6:
            id = int(input('Digite o ID do cliente que deseja se comunicar (200 para encerrar)'))
            if id == 200: break
            dupla_endereco = cliente.connect(id)

            cliente.ask_key(remetente)
            cliente.routing(dupla_endereco)
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

        else:
            cliente.socket.sendto('Esperando criar clientes... '.encode(FORMAT), cliente.rede_endereco)
            rede_cont = cliente.socket.recv(1024)
            rede_cont = int(rede_cont)

main()