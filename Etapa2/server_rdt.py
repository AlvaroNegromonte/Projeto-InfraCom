from socket import *
import random

BUFFER_SIZE = 1024 #tamanho dos segmentos
SERVER_NAME = "localhost" #nome do server criado
SERVER_PORT = 5001 #porta que o servidor está associado
LOSS_PROB = 0.1 #probabilidade simulada de perdas

#Criação do socket UDP, associacao a porta 5001 e print para indicar server 'ready'
server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind((SERVER_NAME, SERVER_PORT))
print(f"[SERVIDOR] Esperando em {SERVER_NAME}:{SERVER_PORT}...")

#Recebe arquivo e endereco do cliente
mensagem, client_addr = server_socket.recvfrom(BUFFER_SIZE)

try:
    nomeArquivo = mensagem.decode() #Recebe nome do arquivo
except UnicodeDecodeError: #exception caso haja erro no nome do arquivo
    print("[SERVIDOR] Erro ao decodificar o nome do arquivo. Encerrando.")
    exit(1)

print(f"[SERVIDOR] Vai salvar como: recebido_{nomeArquivo}") #arquivo que sera criado

expected_seq = 0 #controle de duplicatas, primeiro pacote tem expected_seq = 0
#o numero de seq serve justamente para detectar duplicatas, garantir ordem correta de entrega e controlar fluxo

#Abre o arquivo para armazenar os dados, mudando o nome do arquivo
with open("recebido_" + nomeArquivo, 'wb') as f:
    while True:         #BUFFER_SIZE + 1 é para incluir o 'seq'
        pacote, _ = server_socket.recvfrom(BUFFER_SIZE + 1)# nao precisaremos do endereco do cliente nesse momento, por isso o "_"

        if pacote == b"Acabou": #finaliza envio
            break

        if random.random() < LOSS_PROB: #simula perda de pacote com probabilidade LOSS_PROB
            print(f"[SERVIDOR] *** PACOTE PERDIDO seq={pacote[0]} (simulado) ***")
            continue #simplemente ignora o pacote

        #extrai dados do pacote
        seq = pacote[0]
        dados = pacote[1:]
        print(f"[SERVIDOR] Recebido seq={seq}")

        #verifica se o pacote é o esperado, se seq está correto ou naõ
        if seq == expected_seq:
            f.write(dados)
            print(f"[SERVIDOR] Dados salvos. Enviando ACK {seq}")
            server_socket.sendto(bytes([seq]), client_addr)
            expected_seq = 1 - expected_seq
        else: #Reenvia o ultimo ACK (cliente pode ter perdido o ultimo ACK)
            print(f"[SERVIDOR] Duplicado! Reenviando ACK {1 - expected_seq}")
            server_socket.sendto(bytes([1 - expected_seq]), client_addr)

# Envia de volta o arquivo recebido ao cliente
with open("recebido_" + nomeArquivo, 'rb') as f:
    while True:
        chunk = f.read(BUFFER_SIZE)
        if not chunk:
            break
        server_socket.sendto(chunk, client_addr)
    server_socket.sendto(b"Acabou", client_addr)

print("[SERVIDOR] Arquivo devolvido ao cliente.")
server_socket.close()
