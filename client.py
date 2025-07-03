from socket import *
import os

BUFFER_SIZE = 1024
SERVER_NAME = "localhost"
SERVER_PORT = 5001
destino = (SERVER_NAME, SERVER_PORT)

# criação do socket Cliente UDP
clientSocket = socket(AF_INET, SOCK_DGRAM) 

# link do arquivo que vai ser enviado
mensagem = input("Caminho do arquivo a ser enviado: ").strip()

# envia o nome do arquivo
clientSocket.sendto(os.path.basename(mensagem).encode(), destino)

# envia o conteudo do arquivo em pacotes
with open(mensagem, 'rb') as f:
    while True:
        chunk = f.read(BUFFER_SIZE)
        if not chunk:   # encerra leitura quando o conteudo estiver vazio    
            break
        clientSocket.sendto(chunk, destino)
clientSocket.sendto(b"Acabou", destino)     # mensagem de encerramento enviada para indicar ao server que o conteudo foi finalizado

print("Cliente enviou arquivo e espera a devolução.")

# recebe o arquivo de volta com nome modificado
mensagem_recebida = "retornado_" + os.path.basename(mensagem)
with open(mensagem_recebida, 'wb') as f:
    while True:
        dados, _ = clientSocket.recvfrom(BUFFER_SIZE)   # nao precisaremos do endereco do cliente nesse momento, por isso "_" 
        if dados == b"Acabou":  # mensagem de encerramento do arquivo enviada pelo server, indicando que o conteúdo foi finalizado
            break
        f.write(dados)

print(f"Cliente recebeu o arquivo de volta como: {mensagem_recebida}")

# fecha o socket
clientSocket.close()
