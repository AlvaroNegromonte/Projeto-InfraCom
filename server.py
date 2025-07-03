from socket import *

BUFFER_SIZE = 1024
SERVER_NAME = "localhost"
SERVER_PORT = 5001

# criação do socket Server UDP
server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind((SERVER_NAME, SERVER_PORT))

print(f"Servidor espera receber o arquivo em {SERVER_NAME}:{SERVER_PORT}.")

# recebe o arquivo e o endereco do cliente
mensagem, client_addr = server_socket.recvfrom(BUFFER_SIZE)

# recebe o nome do arquivo
nomeArquivo = mensagem.decode()
print(f"Servidor recebe o arquivo: {nomeArquivo}")

# cria o arquivo recebido para armazenar os dados, mudando o nome do arquivo 
with open("recebido_" + nomeArquivo, 'wb') as f:
    while True:
        mensagem, _ = server_socket.recvfrom(BUFFER_SIZE) # nao precisaremos do endereco do cliente nesse momento, por isso o "_"
        if mensagem == b"Acabou":   # mensagem de encerramento do arquivo enviada pelo cliente, indicando que o conteúdo foi finalizado
            break
        f.write(mensagem)

print(f"Servidor recebe arquivo {nomeArquivo} e salva como recebido:{nomeArquivo}")

# envia de volta ao cliente com nome modificado
with open("recebido_" + nomeArquivo, 'rb') as f:
    while True:
        chunk = f.read(BUFFER_SIZE)
        if not chunk:
            break
        server_socket.sendto(chunk, client_addr)
    server_socket.sendto(b"Acabou", client_addr)

print("Servidor devolve o arquivo ao cliente.")
server_socket.close()
