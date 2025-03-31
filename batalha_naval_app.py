import tkinter as tk
from tkinter import simpledialog, messagebox
import socket
import threading

class BatalhaNavalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Batalha Naval Distribuída")
        self.root.geometry("300x300")

        self.socket = None
        self.nome = None
        self.ip = "localhost"  # IP local para testar na própria máquina
        self.porta = 5000
        self.conexao = None  # Adicionando a variável para a conexão real

        # Menu inicial
        tk.Label(root, text="Batalha Naval Distribuída", font=("Arial", 16, "bold")).pack(pady=20)

        tk.Button(root, text="Criar Partida", font=("Arial", 12), command=self.criar_partida).pack(pady=5)
        tk.Button(root, text="Entrar em uma Partida", font=("Arial", 12), command=self.entrar_partida).pack(pady=5)
        tk.Button(root, text="Sair", font=("Arial", 12), command=root.quit).pack(pady=20)

    def pedir_nome(self):
        # Pede o nome do jogador
        self.nome = simpledialog.askstring("Nome do Jogador", "Digite seu nome:")
        if not self.nome:
            messagebox.showerror("Erro", "Você precisa fornecer um nome!")
            return False
        return True

    def criar_partida(self):
        # Cria o servidor e aguarda conexão de um jogador
        if not self.pedir_nome():
            return
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.bind((self.ip, self.porta))
            self.socket.listen(1)
            print(f"[AGUARDANDO] Esperando conexão em {self.ip}:{self.porta}...")
            messagebox.showinfo("Criando Partida", f"Partida criada! Aguarde outro jogador se conectar.")
            threading.Thread(target=self.iniciar_servidor, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível criar a partida: {e}")

    def iniciar_servidor(self):
        # Inicia o servidor e aguarda conexão de um adversário
        try:
            self.conexao, endereco = self.socket.accept()
            print(f"[CONECTADO] Jogador conectado: {endereco}")
            self.conexao.send(self.nome.encode())
            self.nome_adversario = self.conexao.recv(1024).decode()
            print(f"[CONECTADO] Adversário: {self.nome_adversario}")
            messagebox.showinfo("Jogador Conectado", f"{self.nome_adversario} se conectou à partida.")
            self.jogar()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro na conexão com o adversário: {e}")

    def entrar_partida(self):
        # Conecta-se ao servidor
        if not self.pedir_nome():
            return
        
        self.ip = simpledialog.askstring("Conectar a Partida", "Digite o IP do servidor:")
        if not self.ip:
            messagebox.showerror("Erro", "Você precisa fornecer o IP do servidor!")
            return

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.ip, self.porta))
            print(f"[CONECTADO] Conectado ao servidor {self.ip}:{self.porta}")
            self.socket.send(self.nome.encode())
            self.nome_adversario = self.socket.recv(1024).decode()
            print(f"[CONECTADO] Adversário: {self.nome_adversario}")
            messagebox.showinfo("Conectado", f"Você está conectado ao jogador {self.nome_adversario}.")
            self.jogar()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao conectar-se à partida: {e}")

    def jogar(self):
        # Inicia a partida após a conexão
        print(f"Iniciando partida com {self.nome_adversario}")
        messagebox.showinfo("Iniciar Jogo", f"A partida com {self.nome_adversario} está começando!")

# Inicializa a interface gráfica
root = tk.Tk()
app = BatalhaNavalApp(root)
root.mainloop()
