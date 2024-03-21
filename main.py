from rede import Rede
from cliente import Cliente

rede = Rede()
def main():
    cliente = Cliente(roteamento_esq=rede.inicio, roteamento_dir=rede.ultimo, id=rede.cont)
    cliente.create_socket()
    rede.insert(cliente)
    cliente.certificate()

    while True:      #Garante que todos os nos foram criados
        if rede.cont == 6:
            remetente = cliente.dir
            while cliente.id != remetente.id: #Comunica com todos os outros nos
                if not remetente.conexao[cliente.id]: #Caso nao exista conexao, eh criada como thread e eh mantido o registro da thread
                    print(f'Conexão entre cliente {cliente.id} e cliente {remetente.id} estabelecida')
                    remetente.conexao[cliente.id] = True
                    cliente.conexao[remetente.id] = True

                remetente = remetente.dir   #Itera sobre os proximos nos

            cliente.broadcast()

main()