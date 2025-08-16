import sys
import threading
from socket import *
from reliable import RDTEndpoint

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5001
BUFFER_SIZE = 1024
LOSS_PROB = 0.0    # para etapa 3, deixe 0
TIMEOUT = 0.5

class ChatClient:
    def __init__(self, server_ip, server_port):
        self.server_addr = (server_ip, server_port)
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.rdt = RDTEndpoint(self.sock, loss_prob=LOSS_PROB, timeout_s=TIMEOUT,
                               bufsize=BUFFER_SIZE, debug=False)
        self.running = True
        self.username = None

        self.friends = set()

        self.listener = threading.Thread(target=self._listen_loop, daemon=True)
        self.listener.start()

    def _listen_loop(self):
        while self.running:
            try:
                data, addr = self.rdt.recvfrom()
                if not data or data == b"Acabou":
                    continue

                try:
                    msg = data.decode(errors='ignore').strip()
                    if not msg:
                        continue
                except Exception:
                    continue
                
               # Resposta do servidor para a lista online
                if msg.startswith("[ONLINE_LIST]"):
                    lista = msg.split("\n", 1)[1] if "\n" in msg else ""
                    print("Quem tá no chat:")
                    if lista.strip():
                        print(lista)
                    else:
                        print("(nenhum)")
                    print("> ", end="", flush=True)   # reimprime o prompt
                    continue

                # Mensagens diretas do servidor
                if msg == "OK":
                    print("[SERVIDOR] Conectado com sucesso.")
                    continue
                if msg == "bye":
                    print("[SERVIDOR] Desconectado.")
                    self.running = False
                    break
                if msg == "Voce foi banido.":
                    print("[SERVIDOR] Você foi banido. Encerrando cliente.")
                    self.running = False
                    break

                # Mantém a mensagem original do servidor
                out = msg
                if "/~" in msg:
                    try:
                        _, after = msg.split("/~", 1)
                        user_part = after.split(":", 1)[0].strip()
                        if user_part in self.friends:
                            out = f"[ amigo ] {msg}"
                    except Exception:
                        out = msg
                # Quando o servidor avisa que agora são amigos:
                if msg.startswith("[SERVIDOR] Voce agora é amigo de "):
                    nome = msg.split("de ")[1].strip(".")
                    self.friends.add(nome)

                # Quando o outro usuário aceita nosso pedido de amizade
                if msg.startswith("[SERVIDOR] ") and "aceitou seu pedido de amizade" in msg:
                    nome = msg.split("[SERVIDOR] ")[1].split(" aceitou")[0].strip()
                    self.friends.add(nome)

                # Quando outro usuário remove você da lista de amigos
                if msg.startswith("[SERVIDOR] ") and "removeu você da lista de amigos" in msg:
                    nome = msg.split("[SERVIDOR] ")[1].split(" removeu")[0].strip()
                    if nome in self.friends:
                        self.friends.remove(nome)
                    print(msg)

                # Quando removemos alguém da nossa lista e o servidor confirma
                if msg.startswith("[SERVIDOR] ") and "removido da sua lista de amigos" in msg:
                    nome = msg.split("[SERVIDOR] ")[1].split(" removido")[0].strip()
                    if nome in self.friends:
                        self.friends.remove(nome)
                    print(msg)

                print(out)


            except Exception as e:
                print(f"[ERRO NO LISTENER] {e}")

    def send(self, text: str):
        self.rdt.sendto(text.encode(), self.server_addr)


    def run(self):
        print("Comandos:")
        print("hi, meu nome eh <nome>")
        print("bye")
        print("list")
        print("ban <nome>")
        print("mylist | addtomylist <nome> | rmvfrommylist <nome>")
        print("==== Envie qualquer outra linha para o chat público ====")

        self.send("online_list")

        try:
            while self.running:
                try:
                    line = input("> ").strip()
                except EOFError:
                    break

                if not line:
                    continue

                # Comandos locais
                if line == "mylist":
                    if self.friends:
                        print("Amigos:", ", ".join(sorted(self.friends)))
                    else:
                        print("Amigos: (vazio)")
                    continue

                if line.startswith("addtomylist "):
                    nome = line.split(" ", 1)[1].strip()
                    if nome:
                        self.send(f"addtomylist {nome}")
                    continue

                if line.startswith("rmvfrommylist "):
                    nome = line.split(" ", 1)[1].strip()
                    if nome:
                        self.send(f"rmvfrommylist {nome}")
                    continue


                if line.startswith("aceitar "):
                    nome = line.split(" ", 1)[1].strip()
                    if nome:
                        self.send(f"aceitar {nome}")
                    continue

                if line.startswith("rejeitar "):
                    nome = line.split(" ", 1)[1].strip()
                    if nome:
                        self.send(f"rejeitar {nome}")
                    continue

                # Envia ao servidor
                self.send(line)

        finally:
            self.sock.close()
            print("Cliente encerrado.")



if __name__ == "__main__":
    ip = SERVER_IP
    port = SERVER_PORT
    if len(sys.argv) >= 2:
        ip = sys.argv[1]
    if len(sys.argv) >= 3:
        port = int(sys.argv[2])

    client = ChatClient(ip, port)
    client.run()