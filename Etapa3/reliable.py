# reliable.py
import random
from socket import timeout, error as sock_error
import threading

class RDTEndpoint:
    def __init__(self, sock, loss_prob=0.0, timeout_s=0.5, bufsize=1024, debug=False):
        self.sock = sock
        self.loss_prob = loss_prob
        self.timeout_s = timeout_s
        self.bufsize = bufsize
        self.debug = debug

        # Estado por endereço remoto
        self.state = {}

        # Evita condições de corrida entre sendto() e outras recvfrom() em threads diferentes
        self.send_lock = threading.Lock()

    def _ensure_state(self, addr):
        if addr not in self.state:
            self.state[addr] = {
                "send_seq": 0,
                "recv_expected": 0,
                "last_good_ack": 1
            }

    # -------------------------
    # ENVIO CONFIÁVEL (Stop-and-wait)
    # -------------------------
    def sendto(self, data: bytes, addr):
        self._ensure_state(addr)
        seq = self.state[addr]["send_seq"]
        pacote = bytes([seq]) + data
        ack_recebido = False

        # Lock só no envio/espera de ACK para não conflitar com outras threads
        with self.send_lock:
            while not ack_recebido:
                # simula perda do pacote (somente se quiser testar na etapa 2)
                if random.random() > self.loss_prob:
                    try:
                        self.sock.sendto(pacote, addr)
                        if self.debug:
                            print(f"[RDT] Enviado seq={seq} para {addr}")
                    except sock_error:
                        # socket pode estar fechado
                        if self.debug:
                            print("[RDT] Erro ao enviar (socket fechado?)")
                        return
                else:
                    if self.debug:
                        print(f"[RDT] *** PACOTE PERDIDO (simulado) seq={seq} ***")

                old_timeout = self.sock.gettimeout()  # salva timeout antigo ANTES de alterar
                self.sock.settimeout(self.timeout_s)
                try:
                    ack, src = self.sock.recvfrom(1)
                    if src != addr:
                        # ACK de outro endpoint – ignora e continua esperando o correto
                        continue
                    if ack and ack[0] == seq:
                        if self.debug:
                            print(f"[RDT] ACK {ack[0]} recebido de {addr}")
                        ack_recebido = True
                        self.state[addr]["send_seq"] = 1 - seq
                    else:
                        if self.debug:
                            print(f"[RDT] ACK incorreto {ack[0]} (esperado {seq})")
                except timeout:
                    if self.debug:
                        print(f"[RDT] Timeout esperando ACK seq={seq}. Reenviando...")
                except sock_error:
                    # socket fechado durante a espera
                    if self.debug:
                        print("[RDT] Erro ao receber ACK (socket fechado?)")
                    return
                finally:
                    # restaura o timeout antigo (None = bloqueante)
                    self.sock.settimeout(old_timeout)

    # -------------------------
    # RECEPÇÃO CONFIÁVEL
    # -------------------------
    def recvfrom(self):
        """Bloqueia até receber um pacote de dados válido. Retorna (data, addr)."""
        # Garante bloqueante aqui
        self.sock.settimeout(None)

        while True:
            try:
                pacote, addr = self.sock.recvfrom(self.bufsize + 1)
            except timeout:
                # não deveria acontecer pois setamos bloqueante, mas por segurança…
                continue
            except sock_error:
                # socket fechado
                return b"", None

            if not pacote:
                continue

            if pacote == b"Acabou":
                return pacote, addr

            self._ensure_state(addr)

            # simula perda do lado recebedor (somente se quiser testar na etapa 2)
            if random.random() < self.loss_prob:
                if self.debug:
                    print(f"[RDT] *** PACOTE PERDIDO AO RECEBER (simulado) de {addr}")
                # não envia ACK => força retransmissão do remetente
                continue

            seq = pacote[0]
            dados = pacote[1:]
            expected = self.state[addr]["recv_expected"]

            if self.debug:
                print(f"[RDT] Recebido seq={seq} de {addr}, esperado={expected}")

            if seq == expected:
                # envia ACK correto
                try:
                    self.sock.sendto(bytes([seq]), addr)
                except sock_error:
                    if self.debug:
                        print("[RDT] Erro ao enviar ACK (socket fechado?)")
                    return b"", None

                self.state[addr]["recv_expected"] = 1 - expected
                return dados, addr
            else:
                # Duplicado: reenvia último ACK (inverso do esperado)
                dup_ack = bytes([1 - expected])
                if self.debug:
                    print(f"[RDT] Duplicado de {addr}. Reenviando ACK {dup_ack[0]}")
                try:
                    self.sock.sendto(dup_ack, addr)
                except sock_error:
                    if self.debug:
                        print("[RDT] Erro ao reenviar ACK duplicado (socket fechado?)")
                    return b"", None
                # e segue aguardando o pacote correto
