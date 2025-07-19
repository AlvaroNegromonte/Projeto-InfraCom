
# Segunda Etapa: Transmissão Confiável com RDT 3.0 (implementada sobre UDP)

## 📄 Descrição do Projeto

Este projeto implementa uma **comunicação Cliente-Servidor confiável** utilizando o protocolo UDP com a biblioteca `socket` em Python, seguindo os princípios do **RDT 3.0**, conforme apresentado na disciplina e no livro do Kurose.

O sistema é capaz de:

- Enviar arquivos do cliente para o servidor (ex: `.txt`, `.jpg`, etc.) com confiabilidade;
- Tratar perdas de pacotes simuladas, com retransmissões automáticas;
- Garantir entrega correta, sem duplicação, usando sequência de pacotes e ACKs;
- Armazenar o arquivo recebido no servidor com nome modificado;
- Devolver o arquivo ao cliente, também com nome alterado.

> Obs.: A transmissão ocorre em **segmentos de até 1024 bytes**, com controle de sequência (`seq = 0 ou 1`) e tempo de retransmissão.

---

## 👥 Integrantes do grupo

- Álvaro Cavalcante Negromonte  
- Felipe Torres de Macedo  
- Luiz Felipe Silva Lustosa  
- Julio Cesar Barbosa da Silva  
- Vinícius de Sousa Rodrigues  
- Manoel Carvalho de Lira  

---

## 📁 Estrutura da Pasta

```
entrega02/
├── client_rdt.py          # Cliente UDP com RDT 3.0
├── server_rdt.py          # Servidor UDP com RDT 3.0
├── mensagem.txt           # Arquivo .txt para testes
├── wallpaper.jpg          # Arquivo .jpg para testes
```

---

## ▶️ Instruções de Execução

### 1. Abrir dois terminais

#### ➤ Terminal 1 – Servidor

```bash
python3 server_rdt.py
```

O servidor ficará escutando na porta **5001**, aguardando o recebimento de um arquivo.

---

#### ➤ Terminal 2 – Cliente

```bash
python3 client_rdt.py
```

Será solicitado ao usuário digitar o **caminho do arquivo a ser enviado**, como por exemplo:

```
mensagem.txt
wallpaper.jpg
```

---

### 2. O que acontece durante a execução

- O cliente divide o arquivo em blocos de 1024 bytes, com um byte de controle (`seq`) na frente;
- Cada pacote é enviado via UDP e aguarda confirmação (ACK) do servidor;
- Em caso de perda simulada (20% dos pacotes), o cliente retransmite após `timeout`;
- O servidor verifica o número de sequência e envia ACKs adequados;
- O arquivo é salvo no servidor com o prefixo `recebido_`;
- Ao final, o servidor devolve o arquivo ao cliente com o prefixo `retornado_`.

---

## 🧪 Simulação de perdas e confiabilidade

- A simulação de perdas é feita com a variável:
```python
LOSS_PROB = 0.1
```
- Um `timeout` de retransmissão também é definido com:
```python
TIMEOUT = 0.5  # segundos
```

- Toda a lógica de confiabilidade é feita **em nível de aplicação**, como ensinado na disciplina, implementando o comportamento do RDT 3.0 (envio com parada e espera, verificação de duplicatas, ACKs explícitos).
