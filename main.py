from rede import Rede
from certificadora import Certificadora
from cliente import Cliente
import threading

def main():
    rede = Rede()
    certificadora = Certificadora()

    for id in range(6): #Criacao dos nos com certificado e sockets
        cliente = Cliente(roteamento_esq=rede.inicio, roteamento_dir=rede.ultimo, id=id)
        rede.insert(cliente)
        cliente.certificate(certificadora)

    for _ in range(6): #Para cada no
        no_atual = rede.inicio
        
        cliente = rede.inicio.dir
        while cliente.id != no_atual.id: #Comunica com todos os outros nos
            if not no_atual.conexao[cliente.id]: #Caso nao exista conexao, eh criada como thread e eh mantido o registro da thread
                thread_comunicacao = threading.Thread(target=no_atual.communicate(), args=(certificadora, cliente))
                no_atual.lista_threads.append(thread_comunicacao)
                no_atual.conexao[cliente.id] = True
                cliente.conexao[no_atual.id] = True
                thread_comunicacao.start()

            cliente = cliente.dir   #Itera sobre os proximos nos

        for thread in no_atual.lista_threads: #Espera todas as threads terminarem para comecar o broadcast
            thread.join()

        thread_broadcast = threading.Thread(target=no_atual.broadcast(), args=(certificadora))
        thread_broadcast.start()

        no_atual = no_atual.dir   #Itera sobre os proximos nos

main()