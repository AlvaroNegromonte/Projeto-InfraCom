from socket import *
import os
import time
import random

BUFFER_SIZE = 1024 #tam dos segmentos
SERVER_NAME = "localhost" #nome do server
SERVER_PORT = 5001 #porta do servidor
LOSS_PROB = 0.1 #probabilidade de perda de pacotes (simulada)
TIMEOUT = 0.5 #timeout para retransmitir o dado

#declara o destino e o socket do cliente
destino = (SERVER_NAME, SERVER_PORT)
clientSocket = socket(AF_INET, SOCK_DGRAM)

#faz garantia que o usuario digitou um caminho valido
mensagem = input("Caminho do arquivo a ser enviado: ").strip()
while not mensagem or not os.path.isfile(mensagem):
    print("Arquivo inválido. Tente novamente.")
    mensagem = input("Caminho do arquivo a ser enviado: ").strip()

#envia o nome do arquivo como texto (
#servidor usa para salvar como recebido_...
clientSocket.sendto(os.path.basename(mensagem).encode(), destino)

seq = 0 #num inicial de sequencia (alterna entre 0 e 1)
with open(mensagem, 'rb') as f:
    while True:
        chunk = f.read(BUFFER_SIZE) #le o arquivo em pedaços de BUFFER_SIZE bytes
        if not chunk: #fim do arquivo
            break

        pacote = bytes([seq]) + chunk #pacote criado com primeiro byte sendo seq
        ack_recebido = False

        while not ack_recebido:
            #simula perda e só envia o pacote caso ele não seja "perdido"
            if random.random() > LOSS_PROB:
                clientSocket.sendto(pacote, destino)
                print(f"[CLIENTE] Enviado seq={seq}")
            else:
                print(f"[CLIENTE] *** PACOTE seq={seq} PERDIDO (simulado) ***")

            clientSocket.settimeout(TIMEOUT)

            #aguarda o ACK correto por até 0.3s (timeout)
            #reenvia mesmo pacote caso não tenha recebido o ACK no tempo esperado
            try:
                ack, _ = clientSocket.recvfrom(1)
                if ack[0] == seq:
                    print(f"[CLIENTE] Recebido ACK {ack[0]}")
                    ack_recebido = True
                    seq = 1 - seq
                else:
                    print(f"[CLIENTE] ACK errado: {ack[0]}. Esperado: {seq}")
            except timeout:
                print(f"[CLIENTE] Timeout - reenviando seq={seq}")

#envia sinal para servidor indicando fim da transmissao
clientSocket.sendto(b"Acabou", destino)
print("[CLIENTE] Arquivo enviado. Aguardando devolução.")

# Recebe arquivo de volta
mensagem_recebida = "retornado_" + os.path.basename(mensagem)
with open(mensagem_recebida, 'wb') as f:
    while True:
        dados, _ = clientSocket.recvfrom(BUFFER_SIZE)
        if dados == b"Acabou":
            break
        f.write(dados)

print(f"[CLIENTE] Arquivo retornado como: {mensagem_recebida}")
clientSocket.close()
