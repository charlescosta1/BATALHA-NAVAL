import socket
import threading
import json

class Conexao:
    def __init__(self, servidor, nome, ip="localhost", porta=5000):
        self.servidor = servidor
        self.nome = nome
        self.ip = ip
        self.porta = porta
        self.conexao = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.nome_adversario = None

        if self.servidor:
            self.iniciar_servidor()
        else:
            self.conectar_ao_servidor()

    def iniciar_servidor(self):
        """Inicia o servidor e aguarda conexões"""
        self.socket.bind((self.ip, self.porta))
        self.socket.listen(1)
        print(f"[AGUARDANDO] Esperando conexão em {self.ip}:{self.porta}...")

        self.conexao, endereco = self.socket.accept()

        # Recebe o nome do adversário
        self.nome_adversario = self.conexao.recv(1024).decode()
        print(f"[CONECTADO] Jogador conectado: {self.nome_adversario}. IP: {endereco}")

        # Envia o próprio nome ao adversário
        self.conexao.send(self.nome.encode())

        threading.Thread(target=self.receber_mensagens, daemon=True).start()

    def conectar_ao_servidor(self):
        """Se conecta ao servidor do outro jogador"""
        try:
            self.socket.connect((self.ip, self.porta))
            self.conexao = self.socket

            # Envia o próprio nome ao servidor
            self.conexao.send(self.nome.encode())

            # Recebe o nome do servidor
            self.nome_adversario = self.conexao.recv(1024).decode()
            print(f"[CONECTADO] Conectado ao jogador {self.nome_adversario}. IP: {self.ip}:{self.porta}")

            threading.Thread(target=self.receber_mensagens, daemon=True).start()
        except Exception as erro:
            print(f"[ERRO] Falha ao conectar.")
            print(f"ERRO: {erro}")
            self.socket.close()

    def enviar_mensagem(self, texto):
        """Envia mensagens para o adversário"""
        if self.conexao:
            try:
                mensagem = {"nome": self.nome, "texto": texto}
                self.conexao.send(json.dumps(mensagem).encode())
            except Exception as erro:
                print(f"[ERRO] Falha ao enviar mensagem.")
                print(f"ERRO: {erro}")

    def receber_mensagens(self):
        """Recebe mensagens do adversário"""
        while True:
            try:
                dados = self.conexao.recv(1024).decode()
                if not dados:
                    break

                mensagem = json.loads(dados)
                print(f"{mensagem['nome']}: {mensagem['texto']}")

            except Exception as erro:
                print(f"[ERRO] Falha ao receber mensagem: {erro}")
                break

        # Quando a thread for interrompida, fechamos a conexão
        self.socket.close()
