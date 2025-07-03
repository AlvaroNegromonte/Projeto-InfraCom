*Primeira Etapa: Transmissão de arquivos com UDP*

**Descrição do projeto**

-> Esse projeto implementa a comunicação Cliente-Servidor via protocolo UDP utilizando a biblioteca "socket" em Python. O sistema consegue:

- Enviar arquivos do cliente para o servidor (ex: .txt, .jpg);
- Armazenar o arquivo no servidor com nome modificado;
- Retornar o arquivo para o cliente, também com nome alterado.

Obs: A transferência ocorre em pacotes de até 1024 bytes.

--------------------------------------------------------------

**Integrantes do grupo**

- Álvaro Cavalcante Negromonte
- Felipe Torres de Macedo
- Luiz Felipe Silva Lustosa
- Julio Cesar Barbosa da Silva
- Vinícius de Sousa Rodrigues
- Manoel Carvalho de lira

--------------------------------------------------------------

**Estrutura da pasta**

- client.py
- server.py
- mensagem.txt (arquivo .txt para teste)
- wallpaper.jpg (arquivo .jpg para teste)

--------------------------------------------------------------

**Instruções de execução**

1. Abra dois terminais 

- Terminal 1: Servidor

-> Comando: python3 server.py
-> O servidor ficará aguardando o envio de um arquivo na porta "5001"

---

- Terminal 2: Cliente

-> Comando: python3 client.py
-> Será solicitado digitar o nome do arquivo a ser enviado (ex: mensagem ou wallpaper.jpg)

---

2. O que vai acontecer:

- O cliente envia o arquivo ao servidor;
- O servidor salva com prefixo "recebido_";
- O servidor devolve o arquivo ao cliente com prefixo "retornado_".