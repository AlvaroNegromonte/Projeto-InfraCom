import sys
from socket import *
from datetime import datetime
from reliable import RDTEndpoint
import threading

SERVER_IP = "0.0.0.0"
SERVER_PORT = 5001
BUFFER_SIZE = 1024
LOSS_PROB = 0.0
TIMEOUT = 0.5

class ChatServer:
    def __init__(self, ip, port):
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.bind((ip, port))
        print(f"[SERVIDOR] Escutando em {ip}:{port}")

        self.rdt = RDTEndpoint(self.sock, loss_prob=LOSS_PROB, timeout_s=TIMEOUT,
                               bufsize=BUFFER_SIZE, debug=False)

        self.clients = {}        # username -> addr
        self.addr_to_user = {}   # addr -> username
        self.ban_votes = {}
        self.banned = set()      # conjunto de endereços banidos
        self.lock = threading.Lock()

    def _broadcast(self, payload: bytes):
        """Envia para todos os clientes logados."""
        with self.lock:
            for user, addr in self.clients.items():
                try:
                    self.rdt.sendto(payload, addr)
                except Exception as e:
                    print(f"[SERVIDOR] Erro ao enviar para {user} ({addr}): {e}")

    def _format_msg(self, addr, username, msg_text):
        """Formata a mensagem no padrão <IP>:<PORTA>/~<username>: msg data-hora"""
        ip, port = addr
        now = datetime.now()
        stamp = now.strftime("%H:%M:%S %d/%m/%Y")
        return f"{ip}:{port}/~{username}: {msg_text} {stamp}"

    def _handle_hi(self, addr, text):
        parts = text.split()
        if len(parts) < 5:
            self.rdt.sendto(b"Formato invalido. Use: hi, meu nome eh <nome>", addr)
            return

        username = parts[-1].strip()
        with self.lock:
            if username in self.clients:
                self.rdt.sendto(b"Nome ja utilizado. Tente outro.", addr)
                return
            self.clients[username] = addr
            self.addr_to_user[addr] = username
            if addr in self.banned:
                self.banned.remove(addr)

        self.rdt.sendto(b"OK", addr)
        join_msg = f"*** {username} entrou na sala ***"
        self._broadcast(join_msg.encode())

    def _handle_bye(self, addr):
        with self.lock:
            if addr not in self.addr_to_user:
                self.rdt.sendto(b"Voce nao esta conectado.", addr)
                return
            username = self.addr_to_user.pop(addr)
            self.clients.pop(username, None)

        self.rdt.sendto(b"bye", addr)
        left_msg = f"*** {username} saiu da sala ***"
        self._broadcast(left_msg.encode())

    def _handle_list(self, addr):
        with self.lock:
            users = "\n".join(self.clients.keys())
        self.rdt.sendto(users.encode(), addr)

    def _handle_ban(self, addr, text):
        parts = text.split()
        if len(parts) != 2:
            self.rdt.sendto(b"Formato: ban <nome_do_usuario>", addr)
            return

        target = parts[1]
        with self.lock:
            if addr not in self.addr_to_user:
                self.rdt.sendto(b"Voce nao esta conectado.", addr)
                return
            voter = self.addr_to_user[addr]
            if target not in self.clients:
                self.rdt.sendto(b"Usuario nao encontrado.", addr)
                return

            voters = self.ban_votes.setdefault(target, set())
            if voter in voters:
                self.rdt.sendto(b"Voce ja votou para banir esse usuario.", addr)
                return

            voters.add(voter)
            total = len(self.clients)
            need = total // 2 + 1
            x = len(voters)
            y = need

        self._broadcast(f"[ {target} ] ban {x}/{y}".encode())

        # Caso atingiu a maioria, banir
        if x >= y:
            with self.lock:
                taddr = self.clients.pop(target)
                self.addr_to_user.pop(taddr, None)
                self.ban_votes.pop(target, None)
                self.banned.add(taddr)  # marca como banido

            # Mensagem final para o banido (sem RDT, apenas um aviso)
            self.sock.sendto(b"Voce foi banido.", taddr)
            self._broadcast(f"*** {target} foi banido ***".encode())

    def _handle_message(self, addr, username, text):
        form = self._format_msg(addr, username, text)
        self._broadcast(form.encode())

    def serve_forever(self):
        while True:
            data, addr = self.rdt.recvfrom()
            if data == b"Acabou":
                continue

            # Ignora clientes banidos
            if addr in self.banned:
                continue

            text = data.decode(errors='ignore').strip()

            with self.lock:
                username = self.addr_to_user.get(addr)

            if text.startswith("hi, meu nome eh"):
                self._handle_hi(addr, text)
            elif text == "bye":
                self._handle_bye(addr)
            elif text == "list":
                self._handle_list(addr)
            elif text.startswith("ban "):
                self._handle_ban(addr, text)
            else:
                if username is None:
                    # Cliente não conectado -> ignora (não manda loop infinito)
                    continue
                else:
                    self._handle_message(addr, username, text)

if __name__ == "__main__":
    ip = SERVER_IP
    port = SERVER_PORT
    if len(sys.argv) >= 2:
        ip = sys.argv[1]
    if len(sys.argv) >= 3:
        port = int(sys.argv[2])
    server = ChatServer(ip, port)
    server.serve_forever()
