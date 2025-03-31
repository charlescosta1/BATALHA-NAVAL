import tkinter as tk
from tkinter import simpledialog, messagebox
import socket
import threading
import random

class BatalhaNavalApp:
    def __init__(self, root):
        # Inicializa a interface gráfica
        self.root = root
        self.root.title("Batalha Naval Distribuída")
        self.root.geometry("400x400")
        self.socket, self.nome, self.conexao = None, None, None
        self.eh_servidor, self.turno = False, False
        self.tabuleiro_proprio = [[0] * 7 for _ in range(7)]  # Tabuleiro do jogador
        self.tabuleiro_adversario = [[0] * 7 for _ in range(7)]  # Tabuleiro do adversário
        self.navios_restantes, self.botoes_adversario = 0, []
        self.criar_menu_inicial()  # Chama a função para exibir o menu inicial

    def criar_menu_inicial(self):
        # Função que cria o menu inicial do jogo
        for widget in self.root.winfo_children():
            widget.destroy()  # Limpa a interface
        tk.Label(self.root, text="Batalha Naval Distribuída", font=("Arial", 16, "bold")).pack(pady=20)
        tk.Button(self.root, text="Criar Partida", font=("Arial", 12), command=self.criar_partida).pack(pady=5)
        tk.Button(self.root, text="Entrar em uma Partida", font=("Arial", 12), command=self.entrar_partida).pack(pady=5)
        tk.Button(self.root, text="Sair", font=("Arial", 12), command=self.root.quit).pack(pady=20)

    def pedir_nome(self):
        # Função que pede o nome do jogador
        self.nome = simpledialog.askstring("Nome do Jogador", "Digite seu nome:")
        if not self.nome:
            messagebox.showerror("Erro", "Você precisa fornecer um nome!")  # Caso o jogador não forneça nome
            return False
        return True

    def criar_partida(self):
        # Função que cria uma nova partida (servidor)
        if not self.pedir_nome(): return
        self.eh_servidor = True
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind(("localhost", 5000))  # O servidor escuta na porta 5000
            self.socket.listen(1)  # Aguarda um jogador
            messagebox.showinfo("Criar Partida", "Partida criada! Aguarde outro jogador...")
            threading.Thread(target=self.iniciar_servidor, daemon=True).start()  # Inicia a thread do servidor
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar partida: {e}")

    def iniciar_servidor(self):
        # Função que aguarda a conexão de outro jogador
        self.conexao, _ = self.socket.accept()  # Aceita a conexão do adversário
        self.conexao.send(self.nome.encode())  # Envia o nome do jogador
        self.nome_adversario = self.conexao.recv(1024).decode()  # Recebe o nome do adversário
        self.root.after(0, lambda: messagebox.showinfo("Conectado", f"{self.nome_adversario} conectou!"))
        self.root.after(0, self.jogar)  # Chama a função para iniciar o jogo
        self.turno = True  # O servidor começa jogando

    def entrar_partida(self):
        # Função que permite o jogador entrar em uma partida existente (cliente)
        if not self.pedir_nome(): return
        self.ip = simpledialog.askstring("IP do Servidor", "Digite o IP do servidor:")
        if not self.ip:
            messagebox.showerror("Erro", "IP é obrigatório!")  # Caso o IP não seja fornecido
            return
        self.eh_servidor = False
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.ip, 5000))  # Conecta ao servidor
            self.socket.send(self.nome.encode())  # Envia o nome do jogador
            self.nome_adversario = self.socket.recv(1024).decode()  # Recebe o nome do adversário
            self.conexao = self.socket
            messagebox.showinfo("Conectado", f"Conectado a {self.nome_adversario}!")
            self.jogar()  # Chama a função para iniciar o jogo
            self.turno = False  # O cliente começa esperando
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao conectar: {e}")

    def jogar(self):
        # Função principal do jogo
        for widget in self.root.winfo_children():
            widget.destroy()  # Limpa a tela
        self.colocar_navios()  # Coloca os navios no tabuleiro
        tk.Label(self.root, text="Seu Tabuleiro", font=("Arial", 14)).pack()
        frame_meu = tk.Frame(self.root)
        frame_meu.pack()
        self.criar_tabuleiro(frame_meu, self.tabuleiro_proprio)  # Exibe o tabuleiro do jogador
        tk.Label(self.root, text=f"Tabuleiro de {self.nome_adversario}", font=("Arial", 14)).pack()
        frame_adversario = tk.Frame(self.root)
        frame_adversario.pack()
        self.criar_tabuleiro_adversario(frame_adversario)  # Exibe o tabuleiro do adversário
        threading.Thread(target=self.receber_mensagens, daemon=True).start()  # Inicia a thread para receber mensagens
        self.atualizar_estado_botoes()  # Atualiza o estado dos botões

    def colocar_navios(self):
        # Função que coloca 3 navios no tabuleiro do jogador
        self.navios_restantes = 0
        for _ in range(3):  # Coloca 3 navios
            while True:
                x, y = random.randint(0, 6), random.randint(0, 6)
                if self.tabuleiro_proprio[x][y] == 0:
                    self.tabuleiro_proprio[x][y] = 1  # Marca a posição do navio
                    self.navios_restantes += 1
                    break

    def criar_tabuleiro(self, frame, tabuleiro):
        # Função que cria o tabuleiro do jogador
        for linha in range(7):
            for coluna in range(7):
                celula = tabuleiro[linha][coluna]
                bg = "white"
                if celula == 1: bg = "gray"  # Navio
                elif celula == 2: bg = "red"  # Navio atingido
                elif celula == 3: bg = "blue"  # Água
                lbl = tk.Label(frame, text=" ", width=3, height=1, bg=bg, relief="ridge")
                lbl.grid(row=linha, column=coluna)

    def criar_tabuleiro_adversario(self, frame):
        # Função que cria o tabuleiro do adversário com botões para atacar
        self.botoes_adversario = []
        for linha in range(7):
            linha_botoes = []
            for coluna in range(7):
                btn = tk.Button(frame, text=" ", width=3, height=1,
                               command=lambda l=linha, c=coluna: self.atacar(l, c))
                btn.grid(row=linha, column=coluna)
                linha_botoes.append(btn)
            self.botoes_adversario.append(linha_botoes)

    def atualizar_estado_botoes(self):
        # Função que atualiza o estado dos botões (habilita ou desabilita)
        estado = tk.NORMAL if self.turno else tk.DISABLED
        for linha in self.botoes_adversario:
            for btn in linha:
                btn.config(state=estado)

    def atacar(self, x, y):
        # Função chamada quando o jogador ataca
        if self.turno and self.tabuleiro_adversario[x][y] == 0:
            self.tabuleiro_adversario[x][y] = 1  # Marca o ataque
            self.botoes_adversario[x][y].config(state=tk.DISABLED)
            self.ultimo_ataque = (x, y)
            self.conexao.send(f"ATTACK {x} {y}".encode())  # Envia o ataque para o adversário
            self.turno = False
            self.atualizar_estado_botoes()

    def receber_mensagens(self):
        # Função que recebe mensagens do adversário
        while True:
            try:
                mensagem = self.conexao.recv(1024).decode()
                if not mensagem: break
                if mensagem.startswith("ATTACK"):
                    # Recebe um ataque do adversário
                    _, x, y = mensagem.split()
                    x, y = int(x), int(y)
                    resultado = "RESULT " + ("hit" if self.tabuleiro_proprio[x][y] == 1 else "miss")
                    if self.tabuleiro_proprio[x][y] == 1:
                        self.tabuleiro_proprio[x][y] = 2
                        self.navios_restantes -= 1
                        if self.navios_restantes == 0:
                            self.conexao.send("GAME_OVER win".encode())  # Envia fim de jogo se o jogador perdeu
                            self.root.after(0, lambda: messagebox.showinfo("Fim", "Você perdeu!"))
                            self.root.after(0, self.root.quit)
                    else: self.tabuleiro_proprio[x][y] = 3
                    self.conexao.send(resultado.encode())
                    self.root.after(0, self.atualizar_celula_propria, x, y, resultado.split()[1])
                    self.turno = True
                    self.root.after(0, self.atualizar_estado_botoes)
                elif mensagem.startswith("RESULT"):
                    # Recebe o resultado do ataque do adversário
                    _, res = mensagem.split()
                    x, y = self.ultimo_ataque
                    self.tabuleiro_adversario[x][y] = 2 if res == "hit" else 3
                    self.root.after(0, lambda: self.botoes_adversario[x][y].config(
                        bg="red" if res == "hit" else "blue",
                        text="X" if res == "hit" else "O"))
                elif mensagem.startswith("GAME_OVER"):
                    # Recebe a mensagem de fim de jogo
                    _, res = mensagem.split()
                    self.root.after(0, lambda: messagebox.showinfo("Fim", f"Você {res}!"))
                    self.root.after(0, self.root.quit)
            except Exception as e:
                print(f"Erro: {e}")
                break

    def atualizar_celula_propria(self, x, y, resultado):
        # Função para atualizar a célula do tabuleiro do jogador
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    info = child.grid_info()
                    if info['row'] == str(x) and info['column'] == str(y):
                        child.config(bg="red" if resultado == "hit" else "blue", 
                                    text="X" if resultado == "hit" else "O")

if __name__ == "__main__":
    root = tk.Tk()
    app = BatalhaNavalApp(root)
    root.mainloop()
