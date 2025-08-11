# Terceira Etapa: Transmissão Confiável com RDT 3.0 (implementada sobre UDP)

## 📄 Descrição do Projeto

Este projeto implementa uma comunicação Cliente-Servidor confiável de mensagens de chat utilizando o protocolo UDP com a biblioteca socket em Python, seguindo os princípios do RDT 3.0 descritos no livro Computer Networking: A Top-Down Approach (Kurose e Ross).

Nesta terceira etapa, o sistema permite:

- Trocar mensagens de texto de forma confiável entre cliente e servidor;
- Tratar perdas e duplicações de pacotes;
- Implementar retransmissões automáticas baseadas em timeout;
- Simular perdas de pacotes para testes;
- Garantir que cada mensagem seja entregue corretamente e na ordem correta;
- Suportar comandos de chat, como autenticação de usuário, listagem de usuários, votação para banimento e gerenciamento de lista de amigos.

> A transmissão é feita em segmentos de até 1024 bytes (mais 1 byte de número de sequência), com numeração alternada (0 e 1) e confirmações (ACKs) explícitas para cada pacote.

---

## 👥 Integrantes do grupo

- Álvaro Cavalcante Negromonte
- Felipe Torres de Macedo
- Luiz Felipe Silva Lustosa
- Julio Cesar Barbosa da Silva
- Vinícius de Sousa Rodrigues
- Manoel lira de Carvalho

---

## 📁 Estrutura da Pasta

```
Etapa3/
├── server.py             # Servidor UDP com RDT 3.0
├── client.py             # Cliente UDP com RDT 3.0
├── reliable.py           # Implementação das funções de envio/recebimento confiável
├── __pycache__.py        # Cache compilado do Python
├── README.md             # Documento de descrição do projeto
```

---

## ▶️ Instruções de Execução

### 1. Abrir dois terminais

#### ➤ Terminal 1 – Servidor
```bash
python3 server.py 
ou 
python server.py 0.0.0.0 5001
```
O servidor ficará escutando na porta **5001**, aguardando arquivos.

---

#### ➤ Terminal 2 – Cliente
```bash
python3 client.py 
ou 
python client.py 127.0.0.1 5001
```
O cliente entrará no servidor que abriga o chat tendo que se identificar, primariamente, para então entrar no chat propriamente dito.
```
O cliente pode realizar os seguintes comandos:
- hi, meu nome eh <nome>    # Conectar à sala
- bye                       # Sair da sala
- list                      # Exibir lista de usuários do chat
- ban <nome>                # Banir usuário da sala            
- mylist                    # Exibir lista de amigos
- addtomylist <nome>        # Adicionar usuário à lista de amigos
- rmvfrommylist <nome>      # Remover usuário da lista de amigos

Para haver mais de um cliente dentro do mesmo chat, basta rodar o comando python em um outro terminal.
---

### 2. Durante a execução
- O cliente envia mensagens de texto ao servidor usando o protocolo confiável implementado em RDTEndpoint (Stop-and-Wait);
- Cada mensagem é precedida por 1 byte de número de sequência (0 ou 1) e aguarda o ACK correspondente;
- Em caso de perda simulada ou ausência de ACK dentro do timeout, o pacote é retransmitido;
- O servidor valida o número de sequência esperado; se receber duplicatas, reenvia o último ACK sem processar a mensagem novamente;
- Mensagens válidas são formatadas com o padrão <IP>:<PORTA>/~<username>: mensagem data-hora e enviadas a todos os usuários conectados (broadcast);
- Não há transferência de arquivos nesta etapa — apenas troca de mensagens de chat com confiabilidade.
---

## 🧪 Simulação de perdas
As perdas de pacotes podem ser simuladas ajustando a variável LOSS_PROB no client.py e no server.py:
```python
LOSS_PROB = 0.0  # valor padrão: nenhuma perda simulada
```
Para simular perdas, defina um valor maior que 0.0, por exemplo:
```python
LOSS_PROB = 0.1  # 10% de probabilidade de perda
```
O tempo de retransmissão (timeout) é configurado pela variável:
```python
TIMEOUT = 0.5  # segundos
```

Esse valor define quanto tempo o sistema aguarda um ACK antes de retransmitir o pacote.
---

## 📚 Referências
- KUROSE, James F.; ROSS, Keith W. *Computer Networking: A Top-Down Approach*. 8ª ed. Pearson, 2021.
- Documentação oficial do Python: [socket](https://docs.python.org/3/library/socket.html)