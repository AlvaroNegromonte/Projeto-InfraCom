# reliable.py
import random
import threading
import queue
from socket import error as sock_error

class RDTEndpoint:
    def __init__(self, sock, loss_prob=0.0, timeout_s=0.5, bufsize=1024, debug=False):
        self.sock = sock
        self.loss_prob = loss_prob
        self.timeout_s = timeout_s
        self.bufsize = bufsize
        self.debug = debug

        self.state = {}
        self.send_lock = threading.Lock()

        # Filas de controle
        self.ack_queue = queue.Queue()
        self.data_queue = queue.Queue()

        # Controle da thread de recepção
        self.running = True
        self.listener = threading.Thread(target=self._recv_loop, daemon=True)
        self.listener.start()

    def _ensure_state(self, addr):
        if addr not in self.state:
            self.state[addr] = {
                "send_seq": 0,
                "recv_expected": 0
            }

    def _recv_loop(self):
        """Loop dedicado para receber pacotes e separar ACKs e dados."""
        while self.running:
            try:
                pacote, addr = self.sock.recvfrom(self.bufsize + 1)
            except sock_error:
                break
            except Exception:
                continue

            if not pacote:
                continue

            # Simula perda de pacote na recepção
            if random.random() < self.loss_prob:
                if self.debug:
                    print(f"[RDT] *** PACOTE PERDIDO (simulado) de {addr}")
                continue

            if len(pacote) == 1:
                # ACK
                seq = pacote[0]
                self.ack_queue.put((seq, addr))
                if self.debug:
                    print(f"[RDT] ACK {seq} recebido de {addr}")
            else:
                # Dados
                seq = pacote[0]
                dados = pacote[1:]
                self._ensure_state(addr)
                expected = self.state[addr]["recv_expected"]

                if seq == expected:
                    # ACK correto
                    try:
                        self.sock.sendto(bytes([seq]), addr)
                    except sock_error:
                        continue
                    self.state[addr]["recv_expected"] = 1 - expected
                    self.data_queue.put((dados, addr))
                else:
                    # Duplicado → reenviar último ACK
                    dup_ack = bytes([1 - expected])
                    try:
                        self.sock.sendto(dup_ack, addr)
                    except sock_error:
                        continue

    def sendto(self, data: bytes, addr):
        """Envia dados de forma confiável usando Stop-and-Wait."""
        self._ensure_state(addr)
        seq = self.state[addr]["send_seq"]
        pacote = bytes([seq]) + data
        ack_recebido = False

        with self.send_lock:
            while not ack_recebido:
                # Simula perda no envio
                if random.random() > self.loss_prob:
                    try:
                        self.sock.sendto(pacote, addr)
                        if self.debug:
                            print(f"[RDT] Enviado seq={seq} para {addr}")
                    except sock_error:
                        return
                else:
                    if self.debug:
                        print(f"[RDT] *** PACOTE PERDIDO (simulado) seq={seq}")

                try:
                    ack_seq, ack_addr = self.ack_queue.get(timeout=self.timeout_s)
                    if ack_addr == addr and ack_seq == seq:
                        ack_recebido = True
                        self.state[addr]["send_seq"] = 1 - seq
                except queue.Empty:
                    if self.debug:
                        print(f"[RDT] Timeout esperando ACK seq={seq}. Reenviando...")

    def recvfrom(self):
        """Bloqueia até ter um dado válido para entregar."""
        try:
            dados, addr = self.data_queue.get()
            return dados, addr
        except Exception:
            return b"", None

    def close(self):
        self.running = False
        try:
            self.sock.close()
        except:
            pass